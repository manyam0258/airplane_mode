import frappe


def get_context(context):
    context.shops = frappe.get_all(
        "Shop",
        filters={"status": "Available"},
        fields=["name", "shop_no", "area", "location", "photo", "status"],
    )
