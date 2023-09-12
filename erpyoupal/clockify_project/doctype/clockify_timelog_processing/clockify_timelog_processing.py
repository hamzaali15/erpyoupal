# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from frappe.model.document import Document
from frappe.utils import flt, getdate, time_diff_in_hours, get_datetime, get_time, now

class ClockifyTimelogProcessing(Document):
	def validate(self):
		process_timelog(entry={
			"workspace": self.workspace,
			"clockify_user": self.clockify_user,
			"project": self.project,
			"task": self.task,
			"period_from": self.period_from,
			"period_to": self.period_to
		})

#erpyoupal.clockify_project.doctype.clockify_timelog_processing.clockify_timelog_processing.process_timelog
@frappe.whitelist()
def process_timelog(entry):
	calculate_timelogs(entry)

@frappe.whitelist()
def calculate_timelogs(entry):
	total_amount = 0

	tl_filters = {"workspace": entry.get("workspace"), "locked": 1, "billable": 1}
	if entry.get("clockify_user"):
		tl_filters["clockify_user"] = entry.get("clockify_user")
	if entry.get("project"):
		tl_filters["project"] = entry.get("project")
	if entry.get("task"):
		tl_filters["task"] = entry.get("task")
	timelogs = frappe.get_all("Clockify Timelog", filters=tl_filters, fields=["name", "total_cost", "billable", "hourly_rate", "workspace", "project", "total_hours", "time_in", "clockify_user", "task", "time_out"])

	for timelog in timelogs:
		if getdate(entry.get("period_from")) <= getdate(timelog.time_in) <= getdate(entry.get("period_to")):
			total_amount += flt(timelog.total_cost)
			create_tl_entry(tl_entry={
				"clockify_user": timelog.clockify_user,
				"workspace": timelog.workspace,
				"project": timelog.project,
				"task": timelog.task,
				"user_rate": timelog.hourly_rate,
				"time_in": timelog.time_in,
				"time_out": timelog.time_out,
				"total_hours": flt(timelog.total_hours),
				"total_amount": flt(timelog.total_cost),
				"hold_payment": 0
				})

@frappe.whitelist()
def create_tl_entry(tl_entry):
	tl_entries = frappe.get_all("Clockify TL Entry", filters={"workspace": tl_entry.get("workspace"), "clockify_user": tl_entry.get("clockify_user"), "time_in": tl_entry.get("time_in")}, fields=["name"])
	if tl_entries:
		tl_entry_doc = frappe.get_doc("Clockify TL Entry", tl_entries[0].name)
		tl_entry_doc.flags.ignore_permissions = True
		tl_entry_doc.delete()

	new_entry_doc = frappe.new_doc("Clockify TL Entry")
	new_entry_doc.clockify_user = tl_entry.get("clockify_user")
	new_entry_doc.workspace = tl_entry.get("workspace")
	new_entry_doc.project = tl_entry.get("project")
	new_entry_doc.task = tl_entry.get("task")
	new_entry_doc.user_rate = tl_entry.get("user_rate")
	new_entry_doc.time_in = tl_entry.get("time_in")
	new_entry_doc.time_out = tl_entry.get("time_out")
	new_entry_doc.total_hours = tl_entry.get("total_hours")
	new_entry_doc.total_amount = tl_entry.get("total_amount")
	new_entry_doc.hold_payment = tl_entry.get("hold_payment")
	new_entry_doc.flags.ignore_permissions = True
	new_entry_doc.save()
