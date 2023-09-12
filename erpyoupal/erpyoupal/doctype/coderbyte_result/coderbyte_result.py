# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CoderbyteResult(Document):
	def validate(self):
		self.save_it_consultant()

	def save_it_consultant(self):
		pass
		#Trigger Save it consultant
		# it_consultant = frappe.db.get_value("Job Applicant", self.job_applicant, "it_consultant")
		# if it_consultant:
		# 	frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=it_consultant, queue='long', timeout=300, now=False)
