# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe import _
import frappe
from frappe.utils import fmt_money, flt, getdate

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart_data = get_chart_data(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart_data, report_summary

def get_columns(filters):
	columns = [
		{
			'label': _('Full name'),
			'fieldtype': 'Data',
			'fieldname': 'full_name',
			'width': 200
		},
		{
			'label': _('User'),
			'fieldtype': 'Data',
			'fieldname': 'user',
			'width': 200
		},
		{
			'label': _('Project'),
			'fieldtype': 'Data',
			'fieldname': 'project',
			'width': 200
		},
		{
			'label': _('Cost'),
			'fieldtype': 'Data',
			'fieldname': 'cost',
			'width': 200
		},
		{
			'label': _('Revenue'),
			'fieldtype': 'Data',
			'fieldname': 'revenue',
			'width': 200
		}
	]
	return columns

def get_data(filters):
	data = []

	return data

def get_chart_data(filters):
	chart_data = []

	return chart_data

def get_report_summary(filters):
	report_summary = []

	return report_summary
