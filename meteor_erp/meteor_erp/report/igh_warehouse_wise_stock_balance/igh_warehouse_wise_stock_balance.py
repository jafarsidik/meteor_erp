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


def get_packaging_info(warehouse_name: str) -> tuple[str, float]:
    """Ambil daftar item packaging dan total qty packaging per warehouse."""
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

    list_packaging = ", ".join([r[0] for r in result]) if result else ""
    stock_packaging = sum([r[1] for r in result]) if result else 0.0

    return list_packaging, stock_packaging


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

    for warehouse in warehouses:
        wh_balance = warehouse_balance.get(warehouse.name, {})
        warehouse.stock_balance = wh_balance.get("stock_balance", 0) or 0.0

        # Ambil List Packaging & Stock Packaging
        list_packaging, stock_packaging = get_packaging_info(warehouse.name)
        warehouse.list_packaging = list_packaging
        warehouse.stock_packaging = stock_packaging

    update_indent(warehouses)
    set_balance_in_parent(warehouses)

    return warehouses


def update_indent(warehouses):
    for warehouse in warehouses:

        def add_indent(warehouse, indent):
            warehouse.indent = indent
            for child in warehouses:
                if child.parent_warehouse == warehouse.name:
                    add_indent(child, indent + 1)

        if warehouse.is_group:
            add_indent(warehouse, warehouse.indent or 0)


def set_balance_in_parent(warehouses):
    warehouses = sorted(warehouses, key=lambda x: x.get("indent", 0), reverse=1)

    for warehouse in warehouses:

        def update_balance(warehouse, balance):
            for parent in warehouses:
                if warehouse.parent_warehouse == parent.name:
                    parent.stock_balance += balance

        update_balance(warehouse, warehouse.stock_balance)


def get_columns(filters: StockBalanceFilter) -> list[dict]:
    columns = [
        {
            "label": _("Warehouse"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        },
        {"label": _("Stock Balance"), "fieldname": "stock_balance", "fieldtype": "Float", "width": 150},
        {"label": _("List Packaging"), "fieldname": "list_packaging", "fieldtype": "Data", "width": 200},
        {"label": _("Stock Packaging"), "fieldname": "stock_packaging", "fieldtype": "Float", "width": 150},
    ]

    if filters.get("show_disabled_warehouses"):
        columns.append(
            {
                "label": _("Warehouse Disabled?"),
                "fieldname": "disabled",
                "fieldtype": "Check",
                "width": 200,
            }
        )

    return columns
