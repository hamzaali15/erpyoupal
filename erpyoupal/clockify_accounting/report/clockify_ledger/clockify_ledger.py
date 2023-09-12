# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, time_diff_in_hours, get_datetime, get_time, now

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	total_debit = 0
	total_credit = 0

	#TL Entry
	tl_entries, tl_entries_total_debit, tl_entries_total_credit = get_tl_entries(filters)
	total_debit += tl_entries_total_debit
	total_credit += tl_entries_total_credit
	data.extend(tl_entries)
	
	#Get totals
	data.append({
		"target_date": None,
		"particulars": "Total",
		"account_number": None,
		"debit": total_debit,
		"credit": total_credit
		})

	return data

def get_tl_entries(filters):
	result = []
	total_debit = 0
	total_credit = 0

	tl_filters = {"workspace": filters.workspace, "hold_payment": 0}
	tl_entries = frappe.get_all("Clockify TL Entry", filters=tl_filters, fields=["*"])
	if tl_entries:
		for tl_entry in tl_entries:
			if getdate(filters.from_date) <= getdate(tl_entry.posting_date) <= getdate(filters.to_date):
				result.append({
					"target_date": tl_entry.posting_date,
					"particulars": "Timelog Payment Entry",
					"account_number": tl_entry.name,
					"debit": 0,
					"credit": flt(tl_entry.total_amount)
					})
				total_credit += flt(tl_entry.total_amount)
	return result, total_debit, total_credit

def get_columns(filters):
	columns = [
		{
			"label": _("Date"),
			"fieldname": "target_date",
			"fieldtype": "Date",
			"width": 200
		},
		{
			"label": _("Particulars"),
			"fieldname": "particulars",
			"fieldtype": "Data",
			"width": 300
		},
		{
			"label": _("Account No."),
			"fieldname": "account_number",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": _("Debit"),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 200
		},
		{
			"label": _("Credit"),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 200
		}
	]
	return columns