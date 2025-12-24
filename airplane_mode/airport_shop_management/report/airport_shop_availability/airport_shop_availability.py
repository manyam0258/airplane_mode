# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data


def get_columns():
    return [
        {
            "label": "Airport",
            "fieldname": "airport",
            "fieldtype": "Link",
            "options": "Airport",
            "width": 200,
        },
        {
            "label": "Total Shops",
            "fieldname": "total_shops",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": "Available Shops",
            "fieldname": "available_shops",
            "fieldtype": "Int",
            "width": 140,
        },
        {
            "label": "Occupied Shops",
            "fieldname": "occupied_shops",
            "fieldtype": "Int",
            "width": 140,
        },
    ]


def get_data():
    """
    Aggregates shop counts per airport
    """
    results = frappe.db.sql(
        """
        SELECT
            airport,
            COUNT(name) AS total_shops,
            SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS available_shops,
            SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_shops
        FROM `tabShop`
        GROUP BY airport
        ORDER BY airport
        """,
        as_dict=True,
    )

    return results
