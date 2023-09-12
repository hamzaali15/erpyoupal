# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class PartnerPortalActivityLog(Document):
	def validate(self):
		self.full_name = frappe.db.get_value('User', {'name': self.user}, 'full_name')
		self.operation_date = now()
		if not self.status:
			self.status = 'Success'
		if self.operation in ['Login']:
			self.subject = str(self.full_name)+" logged in"
			frappe.db.set_value('People', {'email_address': self.user}, 'talent_portal_log_status', 'Logged In')
			frappe.db.set_value('People', {'email_address': self.user}, 'talent_portal_last_login', self.operation_date)
		if self.operation in ['Logout']:
			self.subject = str(self.full_name)+" logged out"
			frappe.db.set_value('People', {'email_address': self.user}, 'talent_portal_log_status', 'Logged Out')