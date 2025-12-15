import frappe
import random
import string

def execute():
    # 1. Fetch all tickets
    tickets = frappe.db.get_all("Airplane Ticket", pluck="name")

    for ticket_name in tickets:
        doc = frappe.get_doc("Airplane Ticket", ticket_name)
        
        # 2. Check if seat is empty
        if not doc.seat:
            # 3. Generate Random Seat (Logic repeated from controller)
            random_int = random.randint(1, 99)
            random_char = random.choice(string.ascii_uppercase[:5])
            
            # 4. Update the database directly
            seat_number = f"{random_int}{random_char}"
            frappe.db.set_value("Airplane Ticket", doc.name, "seat", seat_number)
            
    frappe.db.commit()