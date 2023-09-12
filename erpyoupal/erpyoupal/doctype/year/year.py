# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Year(Document):
	pass

#erpyoupal.erpyoupal.doctype.year.year.populate_years
@frappe.whitelist()
def populate_years():
	start_year = 2025
	end_year = 1980

	while start_year != end_year:
		validate_year(year=start_year)
		start_year -= 1

#erpyoupal.erpyoupal.doctype.year.year.validate_year
@frappe.whitelist()
def validate_year(year):
	if not frappe.get_all("Year", filters={"name": year}):
		new_doc = frappe.new_doc("Year")
		new_doc.year = year
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.insert()
