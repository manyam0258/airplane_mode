# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import random

class AirplaneTicket(Document):
    def validate(self):

        #To eliminate Duplicates Add-on's
        item_set = set()
        total_add_ons = 0
        for value in self.add_ons:
            if value.item in item_set:
                frappe.throw(f"The '{value.item}' Add-on has already been added in your Ticket. Please pick another Add-on.")
                
            item_set.add(value.item)
            
			#Add-on amount calculation
            total_add_ons += value.amount

        if total_add_ons:
            #Total Amount  calculation
            self.total_amount = self.flight_price + total_add_ons
        elif not total_add_ons:
            #Total Amount  calculation when no Add_on
            self.total_amount = self.flight_price
        
        #Random Seat generator when empty
        if self.seat:
            return
        elif not self.seat:
            random_number = random.randint(1, 99)
            random_alphabet = random.choice(["A", "B", "C", "D", "E"])

            self.seat = f"{random_number}{random_alphabet}"

    def before_submit(self):
        #To check before submitting the form if the status is not 'Boarded'
        if self.status != "Boarded":
            frappe.throw("You cannot submit this document until you are 'Boarded'.")
            