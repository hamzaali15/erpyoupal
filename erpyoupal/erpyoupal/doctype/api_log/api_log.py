# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class APILog(Document):
	pass

#frappe.core.doctype.api_log.api_log.create_api_log
@frappe.whitelist(allow_guest=True)
def create_api_log(data):
	new_doc = frappe.new_doc("API Log")
	new_doc.title = data.get('title')
	new_doc.endpoint = data.get('endpoint')
	new_doc.log_type = data.get('log_type')
	new_doc.description = data.get('description')
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	result = new_doc.insert()
	frappe.local.response.update({"data": result})