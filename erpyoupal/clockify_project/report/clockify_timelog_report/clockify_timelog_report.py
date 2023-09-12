# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import fmt_money, flt, getdate
from erpyoupal.clockify_project.clockify_utils import timelogs_per_project

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart_data = get_chart_data(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart_data, report_summary

def get_columns(filters):
	columns = [
		{
			'label': _('View'),
			'fieldtype': 'Link',
			'fieldname': 'view',
			'options': 'Clockify Timelog',
			'width': 100
		},
		{
			'label': _('Full name'),
			'fieldtype': 'Data',
			'fieldname': 'full_name',
			'width': 150
		},
		{
			'label': _('User'),
			'fieldtype': 'Data',
			'fieldname': 'user',
			'width': 150
		},
		{
			'label': _('Project'),
			'fieldtype': 'Data',
			'fieldname': 'project',
			'width': 200
		},
		{
			'label': _('Client'),
			'fieldtype': 'Data',
			'fieldname': 'client',
			'width': 150
		},
		{
			'label': _('Total Hours'),
			'fieldtype': 'Data',
			'fieldname': 'total_hours',
			'width': 100
		},
		{
			'label': _('Billable/Non Billable'),
			'fieldtype': 'Data',
			'fieldname': 'billable_non_billable',
			'width': 100
		},
		{
			'label': _('Manager'),
			'fieldtype': 'Data',
			'fieldname': 'manager',
			'width': 150
		},
		{
			'label': _('Condition'),
			'fieldtype': 'Data',
			'fieldname': 'condition',
			'width': 100
		},
		{
			'label': _('Status'),
			'fieldtype': 'Select',
			'fieldname': 'status',
			'options': 'Pending\nApproved\nDeclined',
			'width': 100
		},
#		{
#			'label': _('Update Status'),
#			'fieldtype': 'Data',
#			'fieldname': 'action_status',
#			'width': 100
#		},
		{
			'label': _('Comment'),
			'fieldtype': 'Data',
			'fieldname': 'comment',
			'width': 100
		},
		{
			'label': _('Time In'),
			'fieldtype': 'Data',
			'fieldname': 'time_in',
			'width': 150
		},
		{
			'label': _('Time Out'),
			'fieldtype': 'Data',
			'fieldname': 'time_out',
			'width': 150
		}
#		{
#			'label': _('Hourly Rate'),
#			'fieldtype': 'Data',
#			'fieldname': 'hourly_rate',
#			'width': 150
#		},
#		{
#			'label': _('Amount'),
#			'fieldtype': 'Data',
#			'fieldname': 'amount',
#			'width': 150
#		}
	]
	return columns

def get_data(filters):
	data = []

	ct_filters = []
	if filters.workspace_id:
		ct_filters.append(['workspace', '=', filters.workspace_id])
	if filters.task_id:
		ct_filters.append(['task', '=', filters.task_id])
	if filters.project_id:
		ct_filters.append(['project', '=', filters.project_id])
	if filters.user:
		ct_filters.append(['clockify_user', '=', filters.user])
	if filters.full_name:
		ct_filters.append(['full_name', 'like', '%'+filters.full_name+'%'])

	timelogs = frappe.get_all("Clockify Timelog", filters=ct_filters, fields=["*"], order_by="time_in asc")
	for timelog in timelogs:
		if (getdate(filters.from_date) <= getdate(timelog.time_in) <= getdate(filters.to_date)) or (getdate(filters.from_date) <= getdate(timelog.time_out) <= getdate(filters.to_date)):
			rate = 0
			if timelog.project and timelog.clockify_user:
				rate = get_user_rate_from_project(project=timelog.project, user=timelog.clockify_user)
			comments = frappe.get_all('Comment', filters={'reference_doctype': 'Clockify Timelog', 'comment_type': 'comment', 'reference_name': timelog.name}, fields=['name'])
			data_row = {
				'view': timelog.name,
				'full_name': timelog.full_name,
				'user': timelog.clockify_user,
				'project': timelog.project,
				'client': timelog.client,
				'total_hours': flt(timelog.total_hours, 2),
				'billable_non_billable': "<b>Billable</b>" if timelog.billable else "Non Billable",
				'manager': timelog.manager,
				'condition': "Locked" if timelog.locked else "Unlocked",
				'status': timelog.status,
				#'action_status': '<button type="button" data="'+timelog.status+'" onClick="console.log("'+timelog.status+'")">'+timelog.status+'</button>',
				'comment': len(comments),
				'time_in': timelog.time_in,
				'time_out': timelog.time_out,
				'is_billable': timelog.billable,
				'hourly_rate': flt(rate, 2),
				'amount': flt(flt(rate) * flt(timelog.total_hours), 2),
			}
			data.append(data_row)

	return data

def get_report_summary(data):
	report_summary = []

	total_hours = 0
	total_billable = 0
	total_nonbillable = 0
	total_pending_hours = 0
	total_pending_billable = 0
	total_pending_nonbillable = 0
	total_approved_hours = 0
	total_approved_billable = 0
	total_approved_nonbillable = 0
	total_declined_hours = 0
	total_declined_billable = 0
	total_declined_nonbillable = 0
	total_billable_amount = 0
	total_nonbillable_amount = 0

	if data:
		row = []
		for d in data:
			if d['status'] in ['Pending']:
				total_pending_hours += flt(d['total_hours'])
			if d['status'] in ['Approved']:
				total_approved_hours += flt(d['total_hours'])
			if d['status'] in ['Declined']:
				total_declined_hours += flt(d['total_hours'])

			if d['is_billable']:
				total_billable += flt(d['total_hours'])
				total_billable_amount += flt(d['amount'])
				if d['status'] in ['Pending']:
					total_pending_billable += flt(d['total_hours'])
				if d['status'] in ['Approved']:
					total_approved_billable += flt(d['total_hours'])
				if d['status'] in ['Declined']:
					total_declined_billable += flt(d['total_hours'])
			else:
				total_nonbillable += flt(d['total_hours'])
				total_nonbillable_amount += flt(d['amount'])
				if d['status'] in ['Pending']:
					total_pending_nonbillable += flt(d['total_hours'])
				if d['status'] in ['Approved']:
					total_approved_nonbillable += flt(d['total_hours'])
				if d['status'] in ['Declined']:
					total_declined_nonbillable += flt(d['total_hours'])

			total_hours += flt(d['total_hours'])

	report_summary.append({
		"value": flt(total_hours, 2),
		"indicator": "blue",
		"label": _('Total Hours'),
		"datatype": "Data"
		})
	
	report_summary.append({
		"value": flt(total_pending_hours, 2),
		"indicator": "black",
		"label": _('Total Pending Hours'),
		"datatype": "Data"
		})
	
#	report_summary.append({
#		"value": total_pending_billable,
#		"indicator": "Green",
#		"label": _('Total Pending Billable Hours'),
#		"datatype": "Data"
#		})
	
#	report_summary.append({
#		"value": total_pending_nonbillable,
#		"indicator": "Red",
#		"label": _('Total Pending Non Billable Hours'),
#		"datatype": "Data"
#		})
	
	report_summary.append({
		"value": flt(total_approved_hours, 2),
		"indicator": "green",
		"label": _('Total Approved Hours'),
		"datatype": "Data"
		})
	
#	report_summary.append({
#		"value": total_approved_billable,
#		"indicator": "Green",
#		"label": _('Total Approved Billable Hours'),
#		"datatype": "Data"
#		})
	
#	report_summary.append({
#		"value": total_approved_nonbillable,
#		"indicator": "Red",
#		"label": _('Total Approved Non Billable Hours'),
#		"datatype": "Data"
#		})
	
	report_summary.append({
		"value": flt(total_declined_hours, 2),
		"indicator": "red",
		"label": _('Total Declined Hours'),
		"datatype": "Data"
		})
	
#	report_summary.append({
#		"value": total_declined_billable,
#		"indicator": "Green",
#		"label": _('Total Declined Billable Hours'),
#		"datatype": "Data"
#		})
	
#	report_summary.append({
#		"value": total_declined_nonbillable,
#		"indicator": "Red",
#		"label": _('Total Declined Non Billable Hours'),
#		"datatype": "Data"
#		})

	report_summary.append({
		"value": flt(total_billable, 2),
		"indicator": "green",
		"label": _('Total Billable Hours'),
		"datatype": "Data"
		})

	report_summary.append({
		"value": flt(total_nonbillable, 2),
		"indicator": "red",
		"label": _('Total Non Billable Hours'),
		"datatype": "Data"
		})
	
	report_summary.append({
		"value": flt(total_billable_amount, 2),
		"indicator": "green",
		"label": _('Total Billable Amount'),
		"datatype": "Data"
		})

	report_summary.append({
		"value": flt(total_nonbillable_amount, 2),
		"indicator": "red",
		"label": _('Total Non Billable Amount'),
		"datatype": "Data"
		})

	return report_summary


def get_chart_data(data):
	labels = []
	billable = []
	non_billable = []
	report_dict = {}

	for d in data:
		target_date = getdate(d["time_in"])
		if not target_date in report_dict:
			report_dict[target_date] = {
				'target_date': target_date,
				'total_billable': 0,
				'total_nonbillable': 0, 
			}
		if d['is_billable']:
			report_dict[target_date]['total_billable'] += flt(d['total_hours'])
		else:
			report_dict[target_date]['total_nonbillable'] += flt(d['total_hours'])

	for row_report_dict in report_dict:
		labels.append(row_report_dict)
		billable.append(flt(report_dict[row_report_dict]['total_billable'], 2))
		non_billable.append(flt(report_dict[row_report_dict]['total_nonbillable'], 2))

	return {
		"data": {
			'labels': labels,
			'datasets': [
				{
					"name": "Billable Hours",
					"values": billable
				},
				{
					"name": "Non Billable Hours",
					"values": non_billable
				},
			]
		},
		"type": "bar",
		"colors": ["#00c906",'red'],
		"barOptions": {
			"stacked": False
		}
	}


def get_user_rate_from_project(project, user):
	rate = 0
	if frappe.get_all('Clockify Projects', filters={'name': project}):
		timelog_doc = frappe.get_doc('Clockify Projects', project)
		if timelog_doc.erp_members:
			for row in timelog_doc.erp_members:
				if str(row.clockify_user) == str(user):
					rate = flt(row.hourly_rate)

	return rate