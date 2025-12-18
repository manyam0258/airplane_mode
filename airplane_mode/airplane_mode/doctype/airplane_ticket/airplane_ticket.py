# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

# Copyright (c) 2025
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
import random


class AirplaneTicket(Document):

    # -------------------------
    # VALIDATE (WEB FORM SAFE)
    # -------------------------
    def validate(self):
        self.validate_add_ons()
        self.calculate_total_amount()
        self.assign_seat_if_missing()

    # -------------------------
    # ADD-ON DUPLICATE CHECK
    # -------------------------
    def validate_add_ons(self):
        seen = set()
        for row in self.add_ons:
            if row.item in seen:
                frappe.throw(
                    _("The '{0}' Add-on has already been added").format(row.item)
                )
            seen.add(row.item)

    # -------------------------
    # TOTAL AMOUNT CALCULATION
    # -------------------------
    def calculate_total_amount(self):
        add_on_total = sum((row.amount or 0) for row in self.add_ons)
        self.total_amount = (self.flight_price or 0) + add_on_total

    # -------------------------
    # SEAT ASSIGNMENT (SAFE)
    # -------------------------
    def assign_seat_if_missing(self):
        if self.seat or not self.flight:
            return

        airplane = frappe.db.get_value("Airplane Flight", self.flight, "airplane")

        if not airplane:
            return

        capacity = frappe.db.get_value("Airplane", airplane, "capacity")

        if not capacity:
            return

        # Simple safe seat assignment
        self.seat = (
            f"{random.randint(1, capacity)}{random.choice(['A','B','C','D','E'])}"
        )

    # -------------------------
    # DESK-ONLY SUBMIT RULES
    # -------------------------
    def before_submit(self):
        if self.status != "Boarded":
            frappe.throw(_("You cannot submit this document until you are Boarded"))

        airplane = frappe.db.get_value("Airplane Flight", self.flight, "airplane")

        capacity = frappe.db.get_value("Airplane", airplane, "capacity") or 0

        booked = frappe.db.count(
            "Airplane Ticket", {"flight": self.flight, "docstatus": 1}
        )

        # exclude self if resubmitting
        if self.docstatus == 1:
            booked -= 1

        if booked >= capacity:
            frappe.throw(_("Flight capacity reached. Cannot submit more tickets."))
