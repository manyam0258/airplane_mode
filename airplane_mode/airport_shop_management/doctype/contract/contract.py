# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class Contract(Document):
    """
    Contract – Day 4 Final Logic

    Status lifecycle:
    - Scheduled : today < start_date
    - Active    : start_date <= today <= end_date
    - Expired   : today > end_date

    Shop availability is derived from ACTIVE contracts only.
    """

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------
    def validate(self):
        self._validate_dates()
        self._set_rent_amount_if_missing()

    def _validate_dates(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            frappe.throw(_("End Date must be after Start Date"))

    # --------------------------------------------------
    # SUBMIT
    # --------------------------------------------------
    def on_submit(self):
        self._validate_no_overlap()
        self._set_status_and_shop()

    # --------------------------------------------------
    # CANCEL
    # --------------------------------------------------
    def on_cancel(self):
        frappe.db.set_value("Contract", self.name, "status", "Expired")
        self._update_shop_if_required()

    # --------------------------------------------------
    # CORE LOGIC
    # --------------------------------------------------
    def _validate_no_overlap(self):
        overlapping = frappe.db.sql(
            """
            SELECT name
            FROM `tabContract`
            WHERE shop = %s
              AND docstatus = 1
              AND name != %s
              AND start_date <= %s
              AND end_date >= %s
            """,
            (self.shop, self.name, self.end_date, self.start_date),
        )

        if overlapping:
            frappe.throw(
                _("Another contract exists for this shop in the selected period")
            )

    def _set_status_and_shop(self):
        today = nowdate()

        if today < self.start_date:
            status = "Scheduled"
            shop_status = "Available"
        elif self.start_date <= today <= self.end_date:
            status = "Active"
            shop_status = "Occupied"
        else:
            status = "Expired"
            shop_status = "Available"

        frappe.db.set_value("Contract", self.name, "status", status)
        frappe.db.set_value("Shop", self.shop, "status", shop_status)

    def _update_shop_if_required(self):
        active_exists = frappe.db.exists(
            "Contract",
            {
                "shop": self.shop,
                "docstatus": 1,
                "status": "Active",
            },
        )

        if not active_exists:
            frappe.db.set_value("Shop", self.shop, "status", "Available")

    def _set_rent_amount_if_missing(self):
        if self.rent_amount:
            return

        if not self.shop:
            return

        shop = frappe.get_doc("Shop", self.shop)
        settings = frappe.get_single("Shop Settings")

        if shop.area and settings.default_rent_amount:
            self.rent_amount = shop.area * settings.default_rent_amount
