# custom_app/utils/naming.py
import frappe

def material_request_autoname(doc, method=None):
    prefix_map = {
        "Purchase": "MAT-Purchase-.YYYY.-",
        "Material Transfer": "MAT-Material Transfer-.YYYY.-",
        "Material Issue": "MAT-Material Issue-.YYYY.-",
        "Manufacture": "MAT-Material Manufacture-.YYYY.-",
        "Customer Provided": "MAT-Customer Provided-.YYYY.-"
    }
    prefix = prefix_map.get(doc.material_request_type, "MAT-Purchase-.YYYY.-")
    doc.name = frappe.model.naming.make_autoname(prefix + ".####")

