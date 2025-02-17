import frappe
#from frappe.model.naming import get_default_naming_series
#from frappe.model.mapper import get_mapped_doc
#from frappe.utils import cint, cstr, flt, getdate, get_time
from frappe import _
#from frappe.model.document import Document
#from frappe.model import defaultfields


@frappe.whitelist(True)
def make_stock_entry(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def set_missing_values(source, target):
        target.purpose = "Material Receipt"  # Pastikan tujuan sesuai
        target.from_purchase_order = source.name

    doclist = get_mapped_doc(
        "Purchase Order",
        source_name,
        {
            "Purchase Order": {
                "doctype": "Stock Entry",
                "field_map": {
                    "supplier": "supplier",
                }
            },
            "Purchase Order Item": {
                "doctype": "Stock Entry Detail",
                "field_map": {
                    "item_code": "item_code",
                    "qty": "qty",
                    "uom": "uom",
                    "rate": "rate",
                    "warehouse": "t_warehouse"
                },
            },
        },
        target_doc,
        set_missing_values
    )

    return doclist
