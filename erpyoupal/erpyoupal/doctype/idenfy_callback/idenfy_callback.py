# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpyoupal.erpyoupal.doctype.background_check.idenfy_api import update_background_check_document

class IdenfyCallback(Document):
	def after_insert(self):
		if self.response:
			#try:
			data = eval(self.response)
			update_background_check_document(data)
			#except:
			#	pass
