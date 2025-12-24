# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class ShopRentPayment(Document):
    """
    Shop Rent Payment – Day 4 Final

    Rules:
    - Contract must be submitted
    - Payment date must fall within contract period
    - One payment per contract per calendar month
    - Advance payments allowed
    """

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------
    def validate(self):
        self._validate_contract()
        self._validate_payment_date()
        self._prevent_duplicate_monthly_payment()

    # --------------------------------------------------
    # CORE VALIDATIONS
    # --------------------------------------------------
    def _validate_contract(self):
        if not self.contract:
            return

        contract = frappe.get_doc("Contract", self.contract)

        if contract.docstatus != 1:
            frappe.throw(_("Rent payment is allowed only for submitted contracts"))

    def _validate_payment_date(self):
        if not self.payment_date:
            return

        contract = frappe.get_doc("Contract", self.contract)
        payment_date = getdate(self.payment_date)

        if payment_date < contract.start_date or payment_date > contract.end_date:
            frappe.throw(_("Payment date must fall within the contract period"))

    def _prevent_duplicate_monthly_payment(self):
        if not self.payment_date:
            return

        payment_date = getdate(self.payment_date)

        exists = frappe.db.sql(
            """
            SELECT name
            FROM `tabShop Rent Payment`
            WHERE contract = %s
              AND name != %s
              AND YEAR(payment_date) = %s
              AND MONTH(payment_date) = %s
            """,
            (
                self.contract,
                self.name,
                payment_date.year,
                payment_date.month,
            ),
        )

        if exists:
            frappe.throw(
                _(
                    "A rent payment already exists for this contract for the selected month"
                )
            )

    # --------------------------------------------------
    # SUBMIT
    # --------------------------------------------------
    def on_submit(self):
        frappe.db.set_value(
            self.doctype,
            self.name,
            {
                "status": "Paid",
                "payment_date": self.payment_date or nowdate(),
            },
        )
