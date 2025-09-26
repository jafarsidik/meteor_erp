# Copyright (c) 2025, JF and contributors
# For license information, please see license.txt
from typing import Any, TypedDict

import frappe
from frappe import _
from frappe.query_builder.functions import Sum


class StockBalanceFilter(TypedDict):
    company: str | None
    warehouse: str | None
    show_disabled_warehouses: int | None


SLEntry = dict[str, Any]


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data


def get_warehouse_wise_balance(filters: StockBalanceFilter) -> dict[str, Any]:
    sle = frappe.qb.DocType("Stock Ledger Entry")

    query = (
        frappe.qb.from_(sle)
        .select(
            sle.warehouse,
            Sum(sle.stock_value_difference).as_("stock_balance"),
        )
        .where((sle.docstatus < 2) & (sle.is_cancelled == 0))
        .groupby(sle.warehouse)
    )

    if filters.get("company"):
        query = query.where(sle.company == filters.get("company"))

    data = query.run(as_dict=True)
    return {d["warehouse"]: d for d in data} if data else {}


def get_packaging_info(warehouse_name: str) -> tuple[int, float, list[dict]]:
    """Ambil jumlah distinct packaging, total qty packaging, dan detail packaging per warehouse."""
    bin = frappe.qb.DocType("Bin")
    item = frappe.qb.DocType("Item")

    query = (
        frappe.qb.from_(bin)
        .join(item).on(bin.item_code == item.name)
        .select(
            item.item_name,
            Sum(bin.actual_qty).as_("qty"),
        )
        .where((bin.warehouse == warehouse_name) & (item.item_group == "Packaging"))
        .groupby(item.item_name)
    )

    result = query.run(as_list=True)

    # Jumlah distinct packaging
    list_packaging = len(result) if result else 0
    # Total qty packaging
    stock_packaging = sum([r[1] for r in result]) if result else 0.0
    # Detail list
    detail = [{"item_name": r[0], "qty": r[1]} for r in result] if result else []

    return list_packaging, stock_packaging, detail


def get_warehouses(report_filters: StockBalanceFilter):
    filters = {"company": report_filters.company, "disabled": 0}
    if report_filters.get("show_disabled_warehouses"):
        filters["disabled"] = ("in", [0, report_filters.show_disabled_warehouses])

    return frappe.get_all(
        "Warehouse",
        fields=["name", "parent_warehouse", "is_group", "disabled"],
        filters=filters,
        order_by="lft",
    )


def get_data(filters: StockBalanceFilter):
    warehouse_balance = get_warehouse_wise_balance(filters)
    warehouses = get_warehouses(filters)

    rows = []

    for warehouse in warehouses:
        wh_balance = warehouse_balance.get(warehouse.name, {})
        stock_balance = wh_balance.get("stock_balance", 0) or 0.0

        # Ambil List Packaging & Stock Packaging
        list_packaging, stock_packaging, packaging_detail = get_packaging_info(warehouse.name)

        row = {
            "name": warehouse.name,
            "warehouse_name": frappe.db.get_value("Warehouse", warehouse.name, "warehouse_name"),
            "detail_warehouse": "Group" if warehouse.is_group else "Leaf",
            "lokasi": frappe.db.get_value("Warehouse", warehouse.name, "city"),
            "stock_balance": stock_balance,
            "list_packaging": list_packaging,
            "stock_packaging": stock_packaging,
            "disabled": warehouse.disabled,
            "indent": 0,  # root level
        }
        rows.append(row)

        # Tambahkan child row packaging
        for pkg in packaging_detail:
            rows.append({
                "name": pkg["item_name"],
                "warehouse_name": "",
                "detail_warehouse": "Packaging",
                "lokasi": "",
                "stock_balance": 0,
                "list_packaging": "",
                "stock_packaging": pkg["qty"],
                "disabled": 0,
                "indent": 1,  # child of warehouse
            })

    # Hitung saldo & indentasi warehouse (kalau ada parent-child antar warehouse)
    update_indent(rows)
    set_balance_in_parent(rows)

    return rows


def update_indent(warehouses):
    for warehouse in warehouses:

        def add_indent(warehouse, indent):
            warehouse["indent"] = indent
            for child in warehouses:
                if child.get("parent_warehouse") == warehouse["name"]:
                    add_indent(child, indent + 1)

        if warehouse.get("is_group"):
            add_indent(warehouse, warehouse.get("indent", 0))

def set_balance_in_parent(rows):
    # urutkan dari child ke parent (indent besar -> kecil)
    rows = sorted(rows, key=lambda x: x.get("indent", 0), reverse=True)

    for row in rows:
        balance = row.get("stock_balance", 0)
        parent_name = row.get("parent_warehouse")

        if parent_name:
            for parent in rows:
                if parent.get("name") == parent_name:
                    parent["stock_balance"] = parent.get("stock_balance", 0) + balance


def get_columns(filters: StockBalanceFilter) -> list[dict]:
    columns = [
        {"label": _("ID Warehouse"), "fieldname": "name", "fieldtype": "Data", "width": 200},
        {"label": _("Name Warehouse"), "fieldname": "warehouse_name", "fieldtype": "Data", "width": 200},
        {"label": _("Detail Warehouse"), "fieldname": "detail_warehouse", "fieldtype": "Data", "width": 150},
        {"label": _("Lokasi"), "fieldname": "lokasi", "fieldtype": "Data", "width": 150},
        #{"label": _("Stock Balance"), "fieldname": "stock_balance", "fieldtype": "Float", "width": 150},
        {"label": _("List Packaging"), "fieldname": "list_packaging", "fieldtype": "Int", "width": 150},
        {"label": _("Stock Packaging"), "fieldname": "stock_packaging", "fieldtype": "Float", "width": 150},
    ]
    if filters.get("show_disabled_warehouses"):
        columns.append({"label": _("Warehouse Disabled?"), "fieldname": "disabled", "fieldtype": "Check", "width": 200})
    return columns
