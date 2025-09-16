import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
         {"label": _("Tanggal "), "fieldname": "transaction_date", "fieldtype": "Date", "width": 100},
        {"label": _("Material Request ID"), "fieldname": "name", "fieldtype": "Link", "options": "Material Request", "width": 150},
        {"label": _("Request Type"), "fieldname": "material_request_type", "fieldtype": "Data", "width": 140},
        {"label": _("Material Request Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Material Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 90},
	 {"label": _("Material Qty in Stock"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 120},  # 👈 tambahan
        {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 90},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        #{"label": _("Project"), "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 140},
       # {"label": _("Created By"), "fieldname": "owner", "fieldtype": "Data", "width": 150},
    ]


def get_conditions(filters):
    conditions = []

    if filters.get("status"):
        conditions.append("mr.status = %(status)s")
    if filters.get("material_request_type"):
        conditions.append("mr.material_request_type = %(material_request_type)s")
    if filters.get("company"):
        conditions.append("mr.company = %(company)s")
    if filters.get("from_date"):
        conditions.append("mr.transaction_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("mr.transaction_date <= %(to_date)s")

    return " AND ".join(conditions)

def get_data(filters):
    conditions = get_conditions(filters)
    if conditions:
        conditions = "WHERE " + conditions

    query = f"""
        SELECT
            mr.name,
            mr.transaction_date,
            mr.material_request_type,
            mr.status,
            mr.company,
            mri.item_code,
            mri.item_name,
            mri.qty,
            COALESCE(
                (SELECT SUM(bin.actual_qty)
                 FROM `tabBin` bin
                 WHERE bin.item_code = mri.item_code
                   AND bin.warehouse = mri.warehouse), 0
            ) AS actual_qty,
            mri.stock_uom,
            mri.warehouse,
            mri.project,
            mr.owner
        FROM
            `tabMaterial Request` mr
        INNER JOIN
            `tabMaterial Request Item` mri ON mr.name = mri.parent
        {conditions}
        ORDER BY mr.transaction_date DESC, mr.name
    """
    return frappe.db.sql(query, filters, as_dict=True)
