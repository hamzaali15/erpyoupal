# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import fmt_money, flt
from erpyoupal.clockify_project.clockify_utils import timelogs_per_project

def execute(filters=None):
	columns = get_columns(filters)
	data,data_summary = get_data(filters)
	chart_data = get_chart_data(data,data_summary)
	report_summary = get_report_summary(data,data_summary)
	return columns, data, None, chart_data, report_summary

def get_report_summary(data,data_summary):
	if not data:
		return None
	else:
		row = []
		for d in data_summary:
			if d["profit"] < 1:
				row.append({"value":fmt_money(d["profit"],currency="$"),
					"indicator":"Red",
					"label":_(d["project"]),
					"datatype":"Data"})
			else:
				row.append({"value":fmt_money(d["profit"],currency="$"),
					"indicator":"Green",
					"label":_(d["project"]),
					"datatype":"Data"})
	return row

def get_data(filters):
	data = []
	data_summary = []
	total_hours=0
	total_payment=0
	timelogs_dict = timelogs_per_project(filters.from_date, filters.to_date)
	for project in timelogs_dict:
		project_hours = 0
		project_payment = 0
		budget = frappe.db.get_value("Clockify Projects",project,'project_billable_rate')
		if not budget:
			budget = 0
		project_name = frappe.db.get_value("Clockify Projects",project,"project_name")
		if project == "No Project":
			project_name = "No Project"
		#if not project_name or not budget:
		#	raise Exception( project_name, budget )
		data.append({"project":"<b>"+str(project_name)+"</b>","payment":"<b>Budget: "+fmt_money(budget,currency="$")+"</b>"})
		for c_user in timelogs_dict[project]:
			rate = frappe.db.get_value("Clockify User",c_user,"rate")
			hours = timelogs_dict[project][c_user]["total"]
			data.append({"c_user":c_user,"rate":fmt_money(rate,currency="$"),"hours":"{:.2f}".format(hours),"payment":fmt_money(rate*hours,currency="$")})
			project_hours += hours
			project_payment += rate*hours
			total_hours += hours
			total_payment += rate*hours
		data.append({"hours":"<b>"+"{:.2f}".format(project_hours)+"</b>","payment":"<b>"+fmt_money(project_payment,currency="$")+"</b>"})
		data.append({})
		data_summary.append({"project":project_name,"budget":budget,"payment":project_payment,"profit":budget - project_payment})
	data.append({"project":"<b>Grand Total</b>","hours":"<b>"+"{:.2f}".format(total_hours)+"</b>","payment":"<b>"+fmt_money(total_payment,currency="$")+"</b>"})

	return data,data_summary

def get_columns(filters):
	return [{
		'label': _('Project'),
		'fieldtype': 'Data',
		'fieldname': 'project',
		'options': 'Clockify Projects',
		'width': 300
	},{
		'label': _('User'),
		'fieldtype': 'Link',
		'fieldname': 'c_user',
		'options': 'Clockify User',
		'width': 300
	},{
		'label': _('Rate'),
		'fieldtype': 'Data',
		'fieldname': 'rate',
		'width': 200
	},{
		'label': _('Hours'),
		'fieldtype': 'Data',
		'fieldname': 'hours',
		'width': 200
	},{
		'label': _('Payment'),
		'fieldtype': 'Data',
		'fieldname': 'payment',
		'width': 200
	}]

def get_chart_data(data,data_summary):
	labels = []
	payment = []
	budget = []
	# completed = []
	# overdue = []

	for d in data_summary:
		labels.append(d["project"])
		payment.append(d["payment"])
		budget.append(d["budget"])
		
	# 	total.append(project.total_tasks)
	# 	completed.append(project.completed_tasks)
	# 	overdue.append(project.overdue_tasks)

	return {
		"data": {
			'labels': labels,
			'datasets': [
				{
					"name": "budget",
					"values": budget
				},
				{
					"name": "payment",
					"values": payment
				},
			]
		},
		"type": "bar",
		"colors": ["#00c906",'red'],
		"barOptions": {
			"stacked": False
		}
	}