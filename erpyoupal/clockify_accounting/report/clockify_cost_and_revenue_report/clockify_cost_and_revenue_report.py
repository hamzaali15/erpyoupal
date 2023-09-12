# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import fmt_money, flt, getdate

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart_data = get_chart_data(filters, data)
	report_summary = get_report_summary(filters, data)
	return columns, data, None, chart_data, report_summary

def get_columns(filters):
	columns = [
		{
			'label': _('Workspace'),
			'fieldtype': 'Data',
			'fieldname': 'worksapce',
			'width': 200
		}
	]
	if filters.report_by in ['Per User', 'Per Project & User']:
		columns.append({
			'label': _('Full name'),
			'fieldtype': 'Data',
			'fieldname': 'full_name',
			'width': 200
		})
		columns.append({
			'label': _('User'),
			'fieldtype': 'Data',
			'fieldname': 'user',
			'width': 200
		})
	if filters.report_by in ['Per Project', 'Per Project & User']:
		columns.append({
			'label': _('Project'),
			'fieldtype': 'Data',
			'fieldname': 'project',
			'width': 200
		})
	columns.append({
		'label': _('Cost Amount'),
		'fieldtype': 'Data',
		'fieldname': 'cost',
		'width': 200
	})
	columns.append({
			'label': _('Revenue Amount'),
			'fieldtype': 'Data',
			'fieldname': 'revenue',
			'width': 200
	})
	columns.append({
			'label': _('Gross Margin'),
			'fieldtype': 'Data',
			'fieldname': 'gross_margin',
			'width': 200
	})
	columns.append({
			'label': _('Payment Status'),
			'fieldtype': 'Data',
			'fieldname': 'payment_status',
			'width': 200
	})

	return columns

def get_data(filters):
	data = []

	per_project = {}
	per_user = {}
	per_project_user = {}

	ct_filters = []
	if filters.workspace_id:
		ct_filters.append(['workspace', '=', filters.workspace_id])
	if filters.project_id:
		ct_filters.append(['project', '=', filters.project_id])
	if filters.user:
		ct_filters.append(['clockify_user', '=', filters.user])

	timelogs = frappe.get_all("Clockify Timelog", filters=ct_filters, fields=["*"], order_by="time_in asc")
	for timelog in timelogs:
		if (getdate(filters.from_date) <= getdate(timelog.time_in) <= getdate(filters.to_date)) or (getdate(filters.from_date) <= getdate(timelog.time_out) <= getdate(filters.to_date)):
			if timelog.project and timelog.clockify_user:
				cost_hours = 0
				cost_amount = 0
				revenue_hours = 0
				revenue_amount = 0
				total_gross_margin = 0

				if not timelog.project in per_project:
					per_project[timelog.project] = {
						'worksapce': timelog.workspace,
						'full_name': None,
						'user': None,
						'project': timelog.project,
						'cost': 0,
						'revenue': 0,
						'gross_margin': 0,
						'payment_status': 'Unreleased'
					}
				if not timelog.clockify_user in per_user:
					per_user[timelog.clockify_user] = {
						'worksapce': timelog.workspace,
						'full_name': timelog.full_name,
						'user': timelog.clockify_user,
						'project': timelog.project,
						'cost': 0,
						'revenue': 0,
						'gross_margin': 0,
						'payment_status': 'Unreleased'
					}
				projuser = str(timelog.project)+str(timelog.clockify_user)
				if not projuser in per_project_user:
					per_project_user[projuser] = {
						'worksapce': timelog.workspace,
						'full_name': timelog.full_name,
						'user': timelog.clockify_user,
						'project': timelog.project,
						'cost': 0,
						'revenue': 0,
						'gross_margin': 0,
						'payment_status': 'Unreleased',
						'project_user': str(timelog.project)+' | '+str(timelog.clockify_user)
					}

				rate, client_rate, gross_margin = get_candidate_rates(user=timelog.clockify_user, project=timelog.project)

				if timelog.billable:
					cost_hours += timelog.total_hours
					cost_amount += timelog.total_hours * flt(rate)
				else:
					revenue_hours += timelog.total_hours
					revenue_amount += timelog.total_hours * flt(rate)
				
				per_project[timelog.project]['cost'] += cost_amount
				per_project[timelog.project]['revenue'] += revenue_amount
				per_project_user[projuser]['gross_margin'] = gross_margin

				per_user[timelog.clockify_user]['cost'] += cost_amount
				per_user[timelog.clockify_user]['revenue'] += revenue_amount
				per_user[timelog.clockify_user]['gross_margin'] = gross_margin

				per_project_user[projuser]['cost'] += cost_amount
				per_project_user[projuser]['revenue'] += revenue_amount
				per_project_user[projuser]['gross_margin'] = gross_margin
	
	if filters.report_by in ['Per Project']:
		for row_proj in per_project:
			data.append(per_project[row_proj])
	if filters.report_by in ['Per User']:
		for row_per_user in per_user:
			data.append(per_user[row_per_user])
	if filters.report_by in ['Per Project & User']:
		for row_per_project_user in per_project_user:
			data.append(per_project_user[row_per_project_user])

	return data

def get_chart_data(filters, data):
	labels = []
	cost_amount = []
	revenue_amount = []
	report_dict = {}

	for row in data:
		if filters.report_by in ['Per Project']:
			labels.append(row.get('project'))
		if filters.report_by in ['Per User']:
			labels.append(row.get('user'))
		if filters.report_by in ['Per Project & User']:
			labels.append(row.get('project_user'))
		
		cost_amount.append(flt(row.get('cost'), 2))
		revenue_amount.append(flt(row.get('revenue'), 2))

	return {
		"data": {
			'labels': labels,
			'datasets': [
				{
					"name": "Cost Amount",
					"values": cost_amount
				},
				{
					"name": "Revenue Amount",
					"values": revenue_amount
				},
			]
		},
		"type": "bar",
		"colors": ['red',"#00c906"],
		"barOptions": {
			"stacked": False
		}
	}

def get_report_summary(filters, data):
	report_summary = []

	total_cost_amount = 0
	total_revenue_amount = 0

	for row in data:
		total_cost_amount += row.get('cost')
		total_revenue_amount += row.get('revenue')

	report_summary.append({
		"value": flt(total_cost_amount, 2),
		"indicator": "red",
		"label": _('Total Cost Amount'),
		"datatype": "Data"
		})

	report_summary.append({
		"value": flt(total_revenue_amount, 2),
		"indicator": "green",
		"label": _('Total Revenue Amount'),
		"datatype": "Data"
		})

	return report_summary

def get_candidate_rates(user, project):
	rate = 0
	client_rate = 0
	gross_margin = 0
	members = frappe.db.sql("SELECT * FROM `tabClockify Project Members` WHERE `clockify_user`=%s AND `parent`=%s AND `parentfield`='erp_members' AND `parenttype`='Clockify Projects' ",(user, project), as_dict=1)
	if members:
		people = frappe.db.get_value('People', {'email_address': user}, 'name')
		organization = frappe.db.get_value('Clockify Projects', project, 'organization')
		leads = frappe.get_all('Lead Candidate', filters={'generated_by': organization, 'people': people}, fields=['name'])
		if leads:
			lead_doc = frappe.get_doc('Lead Candidate', leads[0].name)
			if lead_doc.candidate:
				rate = lead_doc.candidate[0].rate
				client_rate = lead_doc.candidate[0].client_rate
				if lead_doc.candidate[0].gross_margin:
					gross_margin = lead_doc.candidate[0].gross_margin
		
		if rate <= 0 and members[0].hourly_rate:
			rate = members[0].hourly_rate

	return rate, client_rate, gross_margin