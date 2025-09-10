# Copyright (c) 2025, JF and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
    category = filters.get("category")
    product_name = filters.get("product_name")
    batch_no = filters.get("batch_no")
    supplier = filters.get("supplier")
    po = filters.get("po")
    so = filters.get("so")
    
    # Build filter conditions
    conditions = {}
    if category:
        conditions["custom_category"] = category
    if product_name:
        conditions["custom_item"] = product_name
    if batch_no:
        conditions["custom_batch_no"] = batch_no
    if supplier:
        conditions["custom_supplier"] = supplier
    if po:
        conditions["custom_po_number"] = po
    if so:
        conditions["custom_so_number"] = so

    # Ambil data Sample Request
    raw_data = frappe.db.get_all(
        "Sample Request",
        fields=[
            "name",
            "project_request",
            "sample_code",
            "sample_group",
            "sample_tipe",
            "default_uom",
            "qty",
            "excepted_start_date",
            "excepted_end_date",
            "company_type"
        ],
        filters=conditions
    )

    data = []
    for row in raw_data:
        project_id = ""
        customer_name = ""
        latest_status = ""

        # Kalau ada project_request, ambil data project
        if row.project_request:
            project = frappe.db.get_value(
                "Project Request",
                row.project_request,
                ["name", "customer"],
                as_dict=True
            )
            if project:
                project_id = project.name
                customer_name = project.customer

        # Ambil status terakhir dari child table Sample Request Actual Time
        latest_child = frappe.db.get_all(
            "Sample Request Actual Time",
            fields=["state", "time"],
            filters={"parent": row.name},
            order_by="time desc",
            limit=1
        )
        if latest_child:
            latest_status = latest_child[0].state

        data.append({
            "name": row.name,
            "project_request": row.project_request,
            "project_id": project_id,
            "customer_name": customer_name,
            "sample_code": row.sample_code,
            "sample_group": row.sample_group,
            "sample_tipe": row.sample_tipe,
            "default_uom": row.default_uom,
            "qty": row.qty,
            "excepted_start_date": row.excepted_start_date,
            "excepted_end_date": row.excepted_end_date,
            "company_type": row.company_type,
            "status": latest_status
        })

    # Definisikan kolom
    columns = [
        {"label": "Name", "fieldname": "name", "fieldtype": "Data"},
        {"label": "Project ID", "fieldname": "project_id", "fieldtype": "Data"},
        {"label": "Sample Code", "fieldname": "sample_code", "fieldtype": "Data"},
        {"label": "Sample Group", "fieldname": "sample_group", "fieldtype": "Data"},
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data"},
        {"label": "Start Date", "fieldname": "excepted_start_date", "fieldtype": "Date"},
        {"label": "End Date", "fieldname": "excepted_end_date", "fieldtype": "Date"},
        {"label": "Company Type", "fieldname": "company_type", "fieldtype": "Data"},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data"},
    ]

    return columns, data
