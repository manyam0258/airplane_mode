# Copyright (c) 2025, surendhranath
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator


class AirplaneFlight(WebsiteGenerator):
    """
    Airplane Flight Controller
    """

    # --------------------------------------------------
    # SUBMIT LOGIC (UNCHANGED)
    # --------------------------------------------------
    def on_submit(self):
        airplane = self.airplane
        if not airplane:
            frappe.throw(_("No airplane linked to this flight"))

        capacity = frappe.db.get_value("Airplane", airplane, "capacity") or 0

        boarded_tickets = frappe.get_all(
            "Airplane Ticket",
            filters={"flight": self.name, "status": "Boarded", "docstatus": 0},
        )

        if len(boarded_tickets) > capacity:
            frappe.throw(
                _(
                    "Cannot submit flight. {0} boarded tickets exceed airplane capacity of {1}."
                ).format(len(boarded_tickets), capacity)
            )

        frappe.flags.from_flight_submit = True

        for t in boarded_tickets:
            ticket = frappe.get_doc("Airplane Ticket", t.name)
            ticket.submit()

        self.status = "Completed"

    # --------------------------------------------------
    # GATE CHANGE → BACKGROUND JOB (FIXED)
    # --------------------------------------------------
    def on_update(self):
        """
        Trigger background job ONLY when gate number changes
        """
        if not self.gate_no:
            return

        # Get document state BEFORE save
        old_doc = self.get_doc_before_save()

        # Skip first save (no previous state)
        if not old_doc:
            return

        # Trigger job only if gate number actually changed
        if old_doc.gate_no != self.gate_no:
            frappe.enqueue(
                method="airplane_mode.airplane_mode.doctype.airplane_flight.airplane_flight.update_ticket_gate_numbers",
                queue="default",
                flight=self.name,
                new_gate_no=self.gate_no,
            )


# --------------------------------------------------
# BACKGROUND JOB FUNCTION
# --------------------------------------------------
def update_ticket_gate_numbers(flight, new_gate_no):
    """
    Background Job:
    Update gate number in all tickets of a flight
    """
    tickets = frappe.get_all(
        "Airplane Ticket",
        filters={"flight": flight},
        pluck="name",
    )

    for ticket in tickets:
        frappe.db.set_value(
            "Airplane Ticket",
            ticket,
            "gate_no",
            new_gate_no,
        )

    frappe.db.commit()
