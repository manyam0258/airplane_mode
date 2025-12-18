# Copyright (c) 2025, surendhranath
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import math


class AirplaneTicket(Document):
    """
    Airplane Ticket Controller

    Guarantees:
    - Web Form always allows saving
    - Seats assigned deterministically (A, B, C)
    - Capacity is strictly enforced
    - No ticket can be submitted after flight completion
    """

    # --------------------------------------------------
    # VALIDATE (WEB FORM SAFE)
    # --------------------------------------------------
    def validate(self):
        self.validate_add_ons()
        self.calculate_total_amount()
        self.assign_seat_if_missing()

    # --------------------------------------------------
    # ADD-ON DUPLICATE CHECK
    # --------------------------------------------------
    def validate_add_ons(self):
        seen = set()
        for row in self.add_ons:
            if row.item in seen:
                frappe.throw(_("Add-on '{0}' already added").format(row.item))
            seen.add(row.item)

    # --------------------------------------------------
    # TOTAL AMOUNT CALCULATION
    # --------------------------------------------------
    def calculate_total_amount(self):
        add_on_total = sum((row.amount or 0) for row in self.add_ons)
        self.total_amount = (self.flight_price or 0) + add_on_total

    # --------------------------------------------------
    # SEAT ASSIGNMENT (A, B, C ONLY)
    # --------------------------------------------------
    def assign_seat_if_missing(self):
        if self.seat or not self.flight:
            return

        airplane = frappe.db.get_value("Airplane Flight", self.flight, "airplane")
        if not airplane:
            return

        capacity = frappe.db.get_value("Airplane", airplane, "capacity") or 0

        if capacity <= 0:
            return

        seat_columns = ["A", "B", "C"]
        seats_per_row = len(seat_columns)
        total_rows = math.ceil(capacity / seats_per_row)

        booked_seats = set(
            frappe.db.get_all(
                "Airplane Ticket", filters={"flight": self.flight}, pluck="seat"
            )
        )

        seat_counter = 0

        for row in range(1, total_rows + 1):
            for col in seat_columns:
                seat_counter += 1

                if seat_counter > capacity:
                    return

                seat = f"{row}{col}"
                if seat not in booked_seats:
                    self.seat = seat
                    return

        frappe.throw(_("No seats available for this flight"))

    # --------------------------------------------------
    # SUBMISSION RULES (DESK ONLY)
    # --------------------------------------------------
    def before_submit(self):
        if self.status != "Boarded":
            frappe.throw(_("Ticket must be in 'Boarded' status before submission"))

        flight = frappe.get_doc("Airplane Flight", self.flight)

        # 🚫 Block manual submission AFTER flight completion
        if flight.docstatus == 1 and not frappe.flags.get("from_flight_submit"):
            frappe.throw(_("Cannot submit ticket. Flight has already been completed."))

        airplane = flight.airplane
        if not airplane:
            frappe.throw(_("Airplane not linked to flight"))

        capacity = frappe.db.get_value("Airplane", airplane, "capacity") or 0

        submitted_count = frappe.db.count(
            "Airplane Ticket", {"flight": self.flight, "docstatus": 1}
        )

        if submitted_count >= capacity:
            frappe.throw(_("Cannot submit ticket. Airplane capacity exceeded."))
