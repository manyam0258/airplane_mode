# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data, total_revenue = get_data()
    chart = get_chart(data)
    summary = get_summary(total_revenue)

    return columns, data, None, chart, summary


# --------------------------------------------------
# Columns
# --------------------------------------------------
def get_columns():
    return [
        {
            "label": _("Airline"),
            "fieldname": "airline",
            "fieldtype": "Link",
            "options": "Airline",
            "width": 200,
        },
        {
            "label": _("Revenue"),
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 150,
        },
    ]


# --------------------------------------------------
# Data Logic (NO SQL, NO get_doc)
# --------------------------------------------------
def get_data():
    # 1. Fetch all airlines (including 0 revenue ones)
    airlines = frappe.get_all("Airline", fields=["name"])

    revenue_map = {a.name: 0 for a in airlines}

    # 2. Fetch submitted tickets only
    tickets = frappe.get_all(
        "Airplane Ticket", filters={"docstatus": 1}, fields=["total_amount", "flight"]
    )

    # 3. Resolve flight -> airplane -> airline (DB ONLY)
    for ticket in tickets:
        airplane = frappe.db.get_value("Airplane Flight", ticket.flight, "airplane")

        if not airplane:
            continue

        airline = frappe.db.get_value("Airplane", airplane, "airline")

        if airline:
            revenue_map[airline] += flt(ticket.total_amount)

    # 4. Build rows + total
    data = []
    total_revenue = 0

    for airline, revenue in revenue_map.items():
        data.append({"airline": airline, "revenue": revenue})
        total_revenue += revenue

    # 5. Total row
    data.append({"airline": _("Total"), "revenue": total_revenue})

    return data, total_revenue


# --------------------------------------------------
# Donut Chart
# --------------------------------------------------
def get_chart(data):
    labels = []
    values = []

    for row in data:
        if row["airline"] != _("Total") and row["revenue"] > 0:
            labels.append(row["airline"])
            values.append(row["revenue"])

    return {
        "data": {
            "labels": labels,
            "datasets": [{"values": values}],
        },
        "type": "donut",
    }


# --------------------------------------------------
# Summary
# --------------------------------------------------
def get_summary(total_revenue):
    return [
        {
            "label": _("Total Revenue"),
            "value": total_revenue,
            "datatype": "Currency",
        }
    ]
