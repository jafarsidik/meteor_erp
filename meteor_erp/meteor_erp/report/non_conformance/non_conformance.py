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
		"Non Conformance",
		fields=["*"],
		filters=conditions
		#order_by="tanggal_pelaporan asc"
	)
	 # Definisikan kolom
	columns = [
		{"label": "No", "fieldname": "name", "fieldtype": "Data"},
  		{"label": "Category", "fieldname": "custom_category", "fieldtype": "Data"},
    	{"label": "Item Code (Product Name)", "fieldname": "custom_item", "fieldtype": "Data"},
     	{"label": "Batch No", "fieldname": "custom_batch_no", "fieldtype": "Data"},
		{"label": "Supplier", "fieldname": "custom_supplier", "fieldtype": "Data"},
		{"label": "Qty", "fieldname": "custom_qty", "fieldtype": "Data"},
		{"label": "UOM", "fieldname": "custom_uom", "fieldtype": "Data"},
		{"label": "PO Number", "fieldname": "custom_po_number", "fieldtype": "Data"},
		{"label": "SO Number", "fieldname": "custom_so_number", "fieldtype": "Data"},
		{"label": "Corrective Action", "fieldname": "corrective_action", "fieldtype": "Data"},
		{"label": "Preventive Action", "fieldname": "preventive_action", "fieldtype": "Data"},
  
		{"label": "Subject", "fieldname": "subject", "fieldtype": "Data"},
		{"label": "Procedure", "fieldname": "procedure", "fieldtype": "Data"},
		{"label": "Status", "fieldname": "status", "fieldtype": "Data"},
		
		
		
	]
	data =  raw_data
	return columns,data