// Copyright (c) 2025, JF and contributors
// For license information, please see license.txt

frappe.query_reports["Non Conformance"] = {
	"filters": [
		{
			fieldname: "category",
			label: "Category",
			fieldtype: "Select",
			options: ["Raw Material","Finished Goods","Packaging"]
		},
		{
			fieldname: "product_name",
			label: "Product Name",
			fieldtype: "Link",
			options: "Item"
		},
		{
			fieldname: "batch_no",
			label: "Batch No",
			fieldtype: "Link",
			options: "Batch"
		},
		{
			fieldname: "supplier",
			label: "Supplier",
			fieldtype: "Link",
			options: "Supplier"
		},
		{
			fieldname: "po",
			label: "Purchase Order",
			fieldtype: "Link",
			options: "Purchase Order"
		},
		{
			fieldname: "so",
			label: "Sales Order",
			fieldtype: "Link",
			options: "Sales Order"
		},
	]
};
