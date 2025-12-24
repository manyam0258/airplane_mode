import frappe
from frappe.utils import nowdate, getdate
from datetime import date


def send_monthly_rent_reminders():
    """
    Monthly scheduler job to send rent due reminders to tenants
    """

    # --------------------------------------------------
    # 1. CHECK GLOBAL SETTING
    # --------------------------------------------------
    settings = frappe.get_single("Shop Settings")

    if not settings.enable_rent_reminder:
        return

    today = getdate(nowdate())
    current_year = today.year
    current_month = today.month

    # --------------------------------------------------
    # 2. GET ACTIVE CONTRACTS
    # --------------------------------------------------
    contracts = frappe.get_all(
        "Contract",
        filters={
            "docstatus": 1,
            "status": "Active",
        },
        fields=[
            "name",
            "tenant",
            "shop",
            "rent_amount",
            "start_date",
            "end_date",
        ],
    )

    # --------------------------------------------------
    # 3. CHECK RENT PAYMENT FOR CURRENT MONTH
    # --------------------------------------------------
    for contract in contracts:
        payment_exists = frappe.db.sql(
            """
            SELECT name
            FROM `tabShop Rent Payment`
            WHERE contract = %s
              AND YEAR(payment_date) = %s
              AND MONTH(payment_date) = %s
            """,
            (contract.name, current_year, current_month),
        )

        if payment_exists:
            continue  # Rent already paid for this month

        send_rent_reminder_email(contract)

    def send_rent_reminder_email(contract):
        """
        Send rent reminder email to tenant
        """

        tenant = frappe.get_doc("Tenant", contract.tenant)

        if not tenant.email:
            return

        subject = "Monthly Rent Reminder"

        message = f"""
        Dear {tenant.tenant_name},

        This is a friendly reminder that the rent for the current month is due.

        Shop       : {contract.shop}
        Amount Due : ₹{contract.rent_amount}

        Kindly make the payment at the earliest.

        Regards,
        Airport Shop Management Team
        """

        frappe.sendmail(
            recipients=[tenant.email],
            subject=subject,
            message=message,
        )
