import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    meta = frappe.get_meta("Delivery Note")
    columns = []
    for field in meta.fields:
        columns.append({
            "label": _(field.label),
            "fieldname": field.fieldname,
            "fieldtype": field.fieldtype,
            "options": field.options,
            "width": 150
        })
    return columns


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("customer"):
        conditions.append("customer = %(customer)s")
        values["customer"] = filters["customer"]

    if filters.get("company"):
        conditions.append("company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    where_clause = " and ".join(conditions)
    if where_clause:
        where_clause = " where " + where_clause

    query = f"""
        select *
        from `tabDelivery Note`
        {where_clause}
        order by posting_date desc
    """

    return frappe.db.sql(query, values, as_dict=True)
