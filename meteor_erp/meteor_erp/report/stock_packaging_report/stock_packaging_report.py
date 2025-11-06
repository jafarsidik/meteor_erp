# Copyright (c) 2025, JF and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_to_date, cint, flt, get_datetime, getdate
from frappe.utils.deprecations import deprecated
from pypika import functions as fn
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter

SLE_COUNT_LIMIT = 100_000


def execute(filters=None):
    if not filters:
        filters = {}

    sle_count = frappe.db.estimate_count("Stock Ledger Entry")

    if (
        sle_count > SLE_COUNT_LIMIT
        and not filters.get("item_code")
        and not filters.get("warehouse")
        and not filters.get("warehouse_type")
    ):
        frappe.throw(
            _("Please select either the Item or Warehouse or Warehouse Type filter to generate the report.")
        )

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date must be before To Date"))

    float_precision = cint(frappe.db.get_default("float_precision")) or 3

    columns = get_columns(filters)
    item_map = get_item_details(filters)
    batch_map = get_batch_details()  # 🆕 ambil data batch
    iwb_map = get_item_warehouse_batch_map(filters, float_precision)

    data = []
    for item in sorted(iwb_map):
        if not filters.get("item") or filters.get("item") == item:
            for wh in sorted(iwb_map[item]):
                for batch in sorted(iwb_map[item][wh]):
                    qty_dict = iwb_map[item][wh][batch]
                    if qty_dict.opening_qty or qty_dict.in_qty or qty_dict.out_qty or qty_dict.bal_qty:
                        batch_detail = batch_map.get(batch)
                        batch_expiry_date = batch_detail.expiry_date if batch_detail else None

                        data.append({
                            "item_code": item,
                            "item_name": item_map[item]["item_name"],
                            "warehouse": wh,
                            "batch_no": batch,
                            "opening_qty": flt(qty_dict.opening_qty, float_precision),
                            "in_qty": flt(qty_dict.in_qty, float_precision),
                            "out_qty": flt(qty_dict.out_qty, float_precision),
                            "bal_qty": flt(qty_dict.bal_qty, float_precision),
                            "stock_uom": item_map[item]["stock_uom"],
                            "batch_expiry_date": batch_expiry_date,  # 🆕
                            "custom_bpom_number_expiration_date": item_map[item]["custom_bpom_number_expiration_date"],
                            "custom_bpom_number": item_map[item]["custom_bpom_number"],
                            "custom_halal_registry_number": item_map[item]["custom_halal_registry_number"],
                            "custom_is_halal": "Halal" if item_map[item].get("custom_is_halal") else "Non Halal",
                            "custom_is_allergen": "Allergen" if item_map[item].get("custom_is_allergen") else "Non Allergen",
                        })

    return columns, data


def get_columns(filters):
    """return columns based on filters"""

    columns = [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 140},
        {"label": _("Batch"), "fieldname": "batch_no", "fieldtype": "Link", "options": "Batch", "width": 120},
        #{"label": _("Opening Qty"), "fieldname": "opening_qty", "fieldtype": "Float", "width": 100},
        #{"label": _("In Qty"), "fieldname": "in_qty", "fieldtype": "Float", "width": 100},
        #{"label": _("Out Qty"), "fieldname": "out_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Sisa Qty"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 100},
        {"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 80},
        # 🔽 FIELD TAMBAHAN
        #{"label": _("BPOM Expiry"), "fieldname": "custom_bpom_number_expiration_date", "fieldtype": "Data", "width": 120},
        {"label": _("Expired Date Batch"), "fieldname": "batch_expiry_date", "fieldtype": "Data", "width": 120},
        {"label": _("BPOM TR"), "fieldname": "custom_bpom_number", "fieldtype": "Data", "width": 120},
        {"label": _("Halal Registry Number"), "fieldname": "custom_halal_registry_number", "fieldtype": "Data", "width": 160},
        {"label": _("Halal / Non Halal"), "fieldname": "custom_is_halal", "fieldtype": "Data", "width": 140},
        {"label": _("Allergen / Non Allergen"), "fieldname": "custom_is_allergen", "fieldtype": "Data", "width": 160},
    ]
    return columns


def get_stock_ledger_entries(filters):
    entries = get_stock_ledger_entries_for_batch_no(filters)
    entries += get_stock_ledger_entries_for_batch_bundle(filters)
    return entries


@deprecated
def get_stock_ledger_entries_for_batch_no(filters):
    if not filters.get("from_date"):
        frappe.throw(_("'From Date' is required"))
    if not filters.get("to_date"):
        frappe.throw(_("'To Date' is required"))

    posting_datetime = get_datetime(add_to_date(filters["to_date"], days=1))

    sle = frappe.qb.DocType("Stock Ledger Entry")
    item = frappe.qb.DocType("Item")
    query = (
        frappe.qb.from_(sle)
        .inner_join(item).on(item.name == sle.item_code)
        .select(
            sle.item_code,
            sle.warehouse,
            sle.batch_no,
            sle.posting_date,
            fn.Sum(sle.actual_qty).as_("actual_qty"),
        )
        .where(
            (sle.docstatus < 2)
            & (sle.is_cancelled == 0)
            & (sle.batch_no != "")
            & (sle.posting_datetime < posting_datetime)
            & (item.item_group == "Packaging")
        )
        .groupby(sle.voucher_no, sle.batch_no, sle.item_code, sle.warehouse)
        .orderby(sle.item_code, sle.warehouse)
    )

    query = apply_warehouse_filter(query, sle, filters)
    if filters.warehouse_type and not filters.warehouse:
        warehouses = frappe.get_all(
            "Warehouse",
            filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
            pluck="name",
        )
        if warehouses:
            query = query.where(sle.warehouse.isin(warehouses))

    for field in ["item_code", "batch_no", "company"]:
        if filters.get(field):
            query = query.where(sle[field] == filters.get(field))

    return query.run(as_dict=True) or []


def get_stock_ledger_entries_for_batch_bundle(filters):
    sle = frappe.qb.DocType("Stock Ledger Entry")
    batch_package = frappe.qb.DocType("Serial and Batch Entry")
    item = frappe.qb.DocType("Item")

    to_date = get_datetime(filters.to_date + " 23:59:59")

    query = (
        frappe.qb.from_(sle)
        .inner_join(batch_package).on(batch_package.parent == sle.serial_and_batch_bundle)
        .inner_join(item).on(item.name == sle.item_code)
        .select(
            sle.item_code,
            sle.warehouse,
            batch_package.batch_no,
            sle.posting_date,
            fn.Sum(batch_package.qty).as_("actual_qty"),
        )
        .where(
            (sle.docstatus < 2)
            & (sle.is_cancelled == 0)
            & (sle.has_batch_no == 1)
            & (sle.posting_datetime <= to_date)
            & (item.item_group == "Packaging")
        )
        .groupby(sle.voucher_no, batch_package.batch_no, batch_package.warehouse)
        .orderby(sle.item_code, sle.warehouse)
    )

    query = apply_warehouse_filter(query, sle, filters)
    if filters.warehouse_type and not filters.warehouse:
        warehouses = frappe.get_all(
            "Warehouse",
            filters={"warehouse_type": filters.warehouse_type, "is_group": 0},
            pluck="name",
        )
        if warehouses:
            query = query.where(sle.warehouse.isin(warehouses))

    for field in ["item_code", "batch_no", "company"]:
        if filters.get(field):
            if field == "batch_no":
                query = query.where(batch_package[field] == filters.get(field))
            else:
                query = query.where(sle[field] == filters.get(field))

    return query.run(as_dict=True) or []


def get_item_warehouse_batch_map(filters, float_precision):
    sle = get_stock_ledger_entries(filters)
    iwb_map = {}

    from_date = getdate(filters["from_date"])
    to_date = getdate(filters["to_date"])

    for d in sle:
        iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {}).setdefault(
            d.batch_no, frappe._dict({"opening_qty": 0.0, "in_qty": 0.0, "out_qty": 0.0, "bal_qty": 0.0})
        )
        qty_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]

        if d.posting_date < from_date:
            qty_dict.opening_qty += flt(d.actual_qty, float_precision)
        elif from_date <= d.posting_date <= to_date:
            if flt(d.actual_qty) > 0:
                qty_dict.in_qty += flt(d.actual_qty, float_precision)
            else:
                qty_dict.out_qty += abs(flt(d.actual_qty, float_precision))

        qty_dict.bal_qty += flt(d.actual_qty, float_precision)

    return iwb_map


def get_item_details(filters):
    item_map = {}
    fields = [
        "name",
        "item_name",
        "description",
        "stock_uom",
        "custom_bpom_number_expiration_date",
        "custom_bpom_number",
        "custom_halal_registry_number",
        "custom_is_halal",
        "custom_is_allergen",
    ]
    for d in (frappe.qb.from_("Item").select(*fields).run(as_dict=1)):
        item_map.setdefault(d.name, d)

    return item_map


def get_batch_details():
    """Ambil expiry_date dari Doctype Batch"""
    batch_map = {}
    for d in frappe.get_all("Batch", fields=["name", "expiry_date"]):
        batch_map[d.name] = d
    return batch_map