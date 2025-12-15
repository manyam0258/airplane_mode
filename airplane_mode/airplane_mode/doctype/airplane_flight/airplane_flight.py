# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

#import frappe
from frappe.website.website_generator import WebsiteGenerator


class AirplaneFlight(WebsiteGenerator):
	def on_submit(self):
		#To change status to Completed after submitting
		self.status = f"Completed"


