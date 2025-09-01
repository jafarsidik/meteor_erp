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
	conditions = {
		#"item_group":"Products",
		#"tanggal_pelaporan": ["between", [f"{start_year}-01-01", f"{end_year}-12-31"]]
	}
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
 	# Ambil data
	raw_data = frappe.db.get_all(
		"Sample Request",
		fields=["*"],
		#filters=conditions
		#order_by="tanggal_pelaporan asc"
	)
	data = []
	for row in raw_data:
		project_id = ""
		customer_name = ""

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
			"company_type": row.company_type
		})

	# Definisikan kolom
	columns = [
		{"label": "Name", "fieldname": "name", "fieldtype": "Data"},
		{"label": "Project Request", "fieldname": "project_request", "fieldtype": "Data"},
		{"label": "Project ID", "fieldname": "project_id", "fieldtype": "Data"},
		{"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data"},
		{"label": "Simple Code", "fieldname": "sample_code", "fieldtype": "Data"},
		{"label": "Simple Group", "fieldname": "sample_group", "fieldtype": "Data"},
		{"label": "Simple Tipe", "fieldname": "sample_tipe", "fieldtype": "Data"},
		{"label": "Default UOM", "fieldname": "default_uom", "fieldtype": "Data"},
		{"label": "Qty", "fieldname": "qty", "fieldtype": "Data"},
		{"label": "Excepted Start Date", "fieldname": "excepted_start_date", "fieldtype": "Date"},
		{"label": "Excepted End Date", "fieldname": "excepted_end_date", "fieldtype": "Date"},
		{"label": "Company Type", "fieldname": "company_type", "fieldtype": "Data"}
	]

	return columns, data