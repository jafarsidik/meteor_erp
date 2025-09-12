# Copyright (c) 2025, JF and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, nowdate, date_diff

def execute(filters=None):
	product_name = filters.get("product_name")
	product_type = filters.get("product_type")
	bpom_number = filters.get("bpom_number")
	
	# Build filter conditions
	conditions = {
		"item_group":"Products",
		#"tanggal_pelaporan": ["between", [f"{start_year}-01-01", f"{end_year}-12-31"]]
	}

	if product_name:
		conditions["name"] = product_name
	if product_type:
		conditions["custom_product_group"] = product_type
	if bpom_number:
		conditions["custom_bpom_number"] = bpom_number
	
	# Ambil data
	raw_data = frappe.db.get_all(
		"Item",
		fields=["*"],
		filters=conditions
		#order_by="tanggal_pelaporan asc"
	)
	
	today = getdate(nowdate())
	data = []

	for row in raw_data:
		expiry = row.get("custom_bpom_number_expiration_date")
		status = "OK"
		if expiry:
			expiry_date = getdate(expiry)
			diff_days = date_diff(expiry_date, today)
			diff_months = diff_days / 30  # Approx in months

			if diff_months <= 3:
				status = "Danger"
			elif diff_months <= 6:
				status = "Warning"
			else:
				status = "OK"

		row["status"] = status
		data.append(row)
	 # Definisikan kolom
	columns = [
		{"label": "Product Name", "fieldname": "item_name", "fieldtype": "Data", "width": 300},
		{"label": "Registration Category", "fieldname": "custom_product_group", "fieldtype": "Data", "width": 120},
		{"label": "Product Classification", "fieldname": "custom_product_group", "fieldtype": "Data", "width": 120},
		{"label": "BPOM Registration Number", "fieldname": "custom_bpom_number", "fieldtype": "Data", "width":120},
		{"label": "BPOM Expiry", "fieldname": "custom_bpom_number_expiration_date", "fieldtype": "Data", "width": 120},
		
		{"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
  		{"label": "Halal Registration Number", "fieldname": "custom_halal_registry_number", "fieldtype": "Data", "width": 120},
		
	]
	return columns,data