# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PartnerPortalFeedback(Document):
	pass

@frappe.whitelist()
def get_feedback_types():
	result = ["Other", "Error", "Bug", "Suggestion", "Enhancement"]
	#feedbacks = frappe.get_all('Talent Portal Feedback', fields=['*'])
	#for fb in feedbacks:
	#	if not fb.type in result:
	#		result.append(fb.type)
	frappe.local.response.update({"data": result})

@frappe.whitelist()
def add_feedback_type():
	pass

#erpyoupal.erpyoupal.doctype.partner_portal_feedback.partner_portal_feedback.submit_feedback
@frappe.whitelist()
def submit_feedback(data):
	new_doc = frappe.new_doc('Partner Portal Feedback')
	new_doc.title = data.get('title')
	new_doc.type = data.get('type')
	new_doc.feedback = data.get('feedback')
	new_doc.page_name = data.get('page_name')
	new_doc.attachment = data.get('attachment')
	new_doc.flags.ignore_links = True
	new_doc.flags.ignore_permissions = True
	frappe.local.response.update({"data": new_doc.insert()})
