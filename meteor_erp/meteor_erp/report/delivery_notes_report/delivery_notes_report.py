import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Nomor SO"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 150},
        {"label": _("Pelanggan"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Qty sesuai SO"), "fieldname": "so_qty", "fieldtype": "Float", "width": 120},
        {"label": _("UoM"), "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 80},
        {"label": _("Delivery Note ID"), "fieldname": "delivery_note", "fieldtype": "Link", "options": "Delivery Note", "width": 150},
        {"label": _("Tanggal Pengiriman"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": _("Qty Dikirim"), "fieldname": "delivered_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Qty Sisa SO"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Tipe Pengiriman"), "fieldname": "custom_delivery_type", "fieldtype": "Data", "width": 150},
        {"label": _("Ekspedisi"), "fieldname": "custom_expedition_name", "fieldtype": "Data", "width": 150},
    ]


def get_data(filters):
    conditions = []
    values = {}

    if filters.get("customer"):
        conditions.append("dn.customer = %(customer)s")
        values["customer"] = filters["customer"]

    if filters.get("company"):
        conditions.append("dn.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("from_date"):
        conditions.append("dn.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("dn.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    where_clause = " and ".join(conditions)
    if where_clause:
        where_clause = " where " + where_clause

    query = f"""
        select
            so.name as sales_order,
            dn.customer,
            dni.item_name,
            so_item.qty as so_qty,
            dni.uom,
            dn.name as delivery_note,
            dn.posting_date,
            dni.qty as delivered_qty,
            (so_item.qty - ifnull(dn_so.delivered_qty, 0)) as pending_qty,
            dn.custom_delivery_type as custom_delivery_type,
            dn.custom_expedition_name as custom_expedition_name
        from `tabDelivery Note` dn
        inner join `tabDelivery Note Item` dni on dn.name = dni.parent
        left join `tabSales Order Item` so_item on dni.so_detail = so_item.name
        left join `tabSales Order` so on so_item.parent = so.name
        left join (
            select so_detail, sum(qty) as delivered_qty
            from `tabDelivery Note Item`
            group by so_detail
        ) dn_so on dn_so.so_detail = dni.so_detail
        {where_clause}
        order by dn.posting_date desc
    """

    return frappe.db.sql(query, values, as_dict=True)
