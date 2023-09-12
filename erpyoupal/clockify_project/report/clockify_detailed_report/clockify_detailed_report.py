# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import fmt_money, flt, getdate
from erpyoupal.clockify_project.clockify_utils import timelogs_per_project

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
			'label': _('Time In'),
			'fieldtype': 'Data',
			'fieldname': 'time_in',
			'width': 200
		},
		{
			'label': _('Time Out'),
			'fieldtype': 'Data',
			'fieldname': 'time_out',
			'width': 200
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
			data_row = {
				"workspace_name": frappe.db.get_value("Clockify Workspace", timelog.workspace, "workspace_name"),
				"project_name": frappe.db.get_value("Clockify Projects", timelog.project, "project_name"),
				"task": frappe.db.get_value("Clockify Task", timelog.task, "task_name"),
				"user": timelog.clockify_user,
				"total": timelog.total_time,
				"billable": timelog.total_time if timelog.billable else "00:00:00",
				"time_in": timelog.time_in,
				"time_out": timelog.time_out
			}
			data.append(data_row)

	return data
