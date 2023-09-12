# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import fmt_money, flt, getdate
from erpyoupal.clockify_project.clockify_utils import timelogs_per_project
from erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog import format_seconds_to_hhmmss

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			'label': _('User'),
			'fieldtype': 'Data',
			'fieldname': 'user',
			'width': 200
		},
		{
			'label': _('Workspace Name'),
			'fieldtype': 'Data',
			'fieldname': 'workspace_name',
			'width': 150
		},
		{
			'label': _('Project Name'),
			'fieldtype': 'Data',
			'fieldname': 'project_name',
			'width': 150
		},
		{
			'label': _('Task'),
			'fieldtype': 'Data',
			'fieldname': 'task',
			'width': 150
		},
		{
			'label': _('Total'),
			'fieldtype': 'Data',
			'fieldname': 'total',
			'width': 150
		},
		{
			'label': _('Billable'),
			'fieldtype': 'Data',
			'fieldname': 'billable',
			'width': 150
		}
	]
	return columns

def get_data(filters):
	data = []
	user_data = {}

	ct_filters = {}
	if filters.workspace_id:
		ct_filters["workspace"] = filters.workspace_id
	if filters.task_id:
		ct_filters["task"] = filters.task_id
	if filters.project_id:
		ct_filters["project"] = filters.project_id
	if filters.user:
		ct_filters["clockify_user"] = filters.user

	timelogs = frappe.get_all("Clockify Timelog", filters=ct_filters, fields=["*"])
	for timelog in timelogs:
		if (getdate(filters.from_date) <= getdate(timelog.time_in) <= getdate(filters.to_date)) or (getdate(filters.from_date) <= getdate(timelog.time_out) <= getdate(filters.to_date)):
			if timelog.clockify_user not in user_data:
				user_data[timelog.clockify_user] = {
					"workspace_name": frappe.db.get_value("Clockify Workspace", timelog.workspace, "workspace_name"),
					"project_name": frappe.db.get_value("Clockify Projects", timelog.project, "project_name"),
					"task": frappe.db.get_value("Clockify Task", timelog.task, "task_name"),
					"user": timelog.clockify_user,
					"total_seconds": 0,
					"total_seconds_billable": 0
				}
			user_data[timelog.clockify_user]['total_seconds'] += flt(timelog.total_seconds)
			if timelog.billable:
				user_data[timelog.clockify_user]['total_seconds_billable'] += flt(timelog.total_seconds)

	if user_data:
		for userd in user_data:
			total_seconds = flt(user_data[userd]["total_seconds"])
			total_seconds_billable = flt(user_data[userd]["total_seconds_billable"])
			data_row = {
				"workspace_name": user_data[userd]["workspace_name"],
				"project_name": user_data[userd]["project_name"],
				"task": user_data[userd]["task"],
				"user": userd,
				"total": format_seconds_to_hhmmss(total_seconds),
				"billable": format_seconds_to_hhmmss(total_seconds_billable)
			}
			data.append(data_row)

	return data
