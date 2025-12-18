# Copyright (c) 2025, surendhranath
# For license information, please see license.txt

from frappe.website.website_generator import WebsiteGenerator
import frappe
from frappe import _


class AirplaneFlight(WebsiteGenerator):
    """
    Airplane Flight Controller

    Responsibilities:
    - Acts as WebsiteGenerator (portal page)
    - On submit:
        - Enforce capacity
        - Submit all boarded tickets
        - Mark flight as Completed
    """

    def on_submit(self):
        # ------------------------------------
        # 1. Validate airplane & capacity
        # ------------------------------------
        airplane = self.airplane
        if not airplane:
            frappe.throw(_("No airplane linked to this flight"))

        capacity = frappe.db.get_value("Airplane", airplane, "capacity") or 0

        # ------------------------------------
        # 2. Fetch boarded draft tickets
        # ------------------------------------
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

        # ------------------------------------
        # 3. Submit boarded tickets (FLAGGED)
        # ------------------------------------
        frappe.flags.from_flight_submit = True

        for t in boarded_tickets:
            ticket = frappe.get_doc("Airplane Ticket", t.name)
            ticket.submit()

        # ------------------------------------
        # 4. Mark flight as completed
        # ------------------------------------
        self.status = "Completed"
