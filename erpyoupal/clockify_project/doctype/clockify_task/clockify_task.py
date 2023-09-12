# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, time_diff_in_hours, get_datetime, get_time

class ClockifyTask(Document):
	def autoname(self):
		self.get_task_name()

	def get_task_name(self):
		taskname = None
		name_ext = "App"
		if self.erp_task_name:
			taskname = self.erp_task_name
		if self.clockify_task_id:
			name_ext = "Clockify"
		if self.clockify_task_name:
			taskname = self.clockify_task_name

		if not taskname:
			frappe.throw(_("App/Clockify Task Name is required"))

		self.task_name = taskname
		self.name_extension = name_ext
		self.task_fullname = taskname+" - "+name_ext


#erpyoupal.clockify_project.doctype.clockify_task.clockify_task.get_clockify_task
@frappe.whitelist()
def get_clockify_task(filters={}):
	result = frappe.get_all("Clockify Timelog", filters=filters, fields=[
		"name",
		"task",
		"task_id",
		"workspace_id",
		"project_id",
		"assignees",
		"assignees_id",
		"status",
		"done",
		"hours",
		"total_hours_spent"
	])
	return result