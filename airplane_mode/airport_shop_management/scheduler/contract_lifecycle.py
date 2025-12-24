import frappe
from frappe.utils import nowdate


def update_contract_lifecycle():
    """
    Daily scheduler job:
    - Activate contracts whose start_date is today
    - Expire contracts whose end_date has passed
    - Update shop status accordingly
    """

    today = nowdate()

    # --------------------------------------------------
    # 1. ACTIVATE CONTRACTS
    # --------------------------------------------------
    contracts_to_activate = frappe.get_all(
        "Contract",
        filters={
            "docstatus": 1,
            "status": ["!=", "Active"],
            "start_date": ["<=", today],
            "end_date": [">=", today],
        },
        fields=["name", "shop"],
    )

    for contract in contracts_to_activate:
        frappe.db.set_value("Contract", contract.name, "status", "Active")
        frappe.db.set_value("Shop", contract.shop, "status", "Occupied")

    # --------------------------------------------------
    # 2. EXPIRE CONTRACTS
    # --------------------------------------------------
    contracts_to_expire = frappe.get_all(
        "Contract",
        filters={
            "docstatus": 1,
            "status": "Active",
            "end_date": ["<", today],
        },
        fields=["name", "shop"],
    )

    for contract in contracts_to_expire:
        frappe.db.set_value("Contract", contract.name, "status", "Expired")

        # Check if any other active contract exists for this shop
        active_exists = frappe.db.exists(
            "Contract",
            {
                "shop": contract.shop,
                "docstatus": 1,
                "status": "Active",
            },
        )

        if not active_exists:
            frappe.db.set_value("Shop", contract.shop, "status", "Available")

    frappe.db.commit()
