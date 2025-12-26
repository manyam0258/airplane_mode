import frappe


def get_context(context):
    shop_name = frappe.form_dict.get("name")

    if not shop_name:
        frappe.throw("Shop not specified")

    shop = frappe.get_doc("Shop", shop_name)

    context.shop = shop
