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
	],
	formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
		if (column.fieldname === "status" && data) {
			let color = "";
			if (data.status === "Danger") {
				color = "red";
			} else if (data.status === "Warning") {
				color = "orange";
			} else if (data.status === "Safe") {
				color = "blue";
			}else if(data.status === "OK"){
				color = "green";
			}
			value = `<div style="background-color:${color}; color:white; font-weight:bold; text-align:center;">${value}</div>`;
		}
        
        return value;
    }
};
