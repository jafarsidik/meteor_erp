# Copyright (c) 2025, JF and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 250},
        {"label": "Omzet", "fieldname": "omzet", "fieldtype": "Currency", "width": 150}
    ]

def get_data(filters):
    conditions = {"docstatus": 1}

    if filters.get("start_date"):
        conditions["transaction_date"] = [">=", filters.get("start_date")]
    if filters.get("end_date"):
        if "transaction_date" in conditions:
            conditions["transaction_date"] = ["between", [filters.get("start_date"), filters.get("end_date")]]
        else:
            conditions["transaction_date"] = ["<=", filters.get("end_date")]

    if filters.get("customer"):
        conditions["customer"] = filters.get("customer")

    # Ambil data Sales Order
    sales_orders = frappe.get_all(
        "Sales Order",
        filters=conditions,
        fields=["customer_name", "grand_total"]
    )

    # Group by customer
    customer_totals = {}
    for so in sales_orders:
        customer_totals[so.customer_name] = customer_totals.get(so.customer_name, 0) + so.grand_total

    # Format data untuk report
    data = [{"customer_name": c, "omzet": t} for c, t in customer_totals.items()]
    data.sort(key=lambda x: x["omzet"], reverse=True)
    return data
