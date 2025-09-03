// Copyright (c) 2025, JF and contributors
// For license information, please see license.txt

frappe.query_reports["IGH Material Request"] = {
	"filters": [
		{
		"fieldname": "status",
		"label": "Status",
		"fieldtype": "Select",
		"options": "\nDraft\nSubmitted\nStopped\nCancelled\nPending\nPartially Ordered\nOrdered"
		},
		{
		"fieldname": "material_request_type",
		"label": "Request Type",
		"fieldtype": "Select",
		"options": "\nPurchase\nMaterial Transfer\nMaterial Issue\nManufacture\nCustomer Provided"
		},
		{
		"fieldname": "company",
		"label": "Company",
		"fieldtype": "Link",
		"options": "Company"
		},
		{
		"fieldname": "from_date",
		"label": "From Date",
		"fieldtype": "Date"
		},
		{
		"fieldname": "to_date",
		"label": "To Date",
		"fieldtype": "Date"
		}
	]
};
