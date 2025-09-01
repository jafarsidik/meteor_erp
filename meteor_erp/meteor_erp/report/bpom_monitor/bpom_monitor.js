// Copyright (c) 2025, JF and contributors
// For license information, please see license.txt

frappe.query_reports["BPOM Monitor"] = {
	"filters": [
		{
			fieldname: "product_name",
			label: "Product Name",
			fieldtype: "Link",
			options: "Item"
		},
		{
            fieldname: "product_type",
            label: "Product Type",
            fieldtype: "Link",
			options:"Product Type"
        },
		{
            fieldname: "bpom_number",
            label: "BPOM Number",
            fieldtype: "Data"
        },
	]
};
