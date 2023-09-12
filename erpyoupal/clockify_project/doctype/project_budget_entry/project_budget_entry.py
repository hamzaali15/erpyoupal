# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ProjectBudgetEntry(Document):
	pass


#erpyoupal.clockify_project.doctype.project_budget_entry.project_budget_entry.create_budget_entry
@frappe.whitelist()
def create_budget_entry(project, budget_type, amount, currency, duration):
	result = None
	new_doc = frappe.new_doc("Project Budget Entry")
	new_doc.project = None
	new_doc.budget_type = None
	new_doc.amount = None
	new_doc.currency = None
	new_doc.duration = None
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	result = new_doc.insert()
	return result


#erpyoupal.clockify_project.doctype.project_budget_entry.project_budget_entry.get_projects_budget
@frappe.whitelist()
def get_projects_budget(project=None, organization=None):
	result = {
		"total_budget": 0,
		"total_budget_duration": 0
	}
	project_budget_data = {}

	if project:
		projects_list = frappe.get_all("Clockify Projects", filters={"name": project}, fields=["name"])
	if organization:
		projects_list = frappe.get_all("Clockify Projects", filters={"organization": organization}, fields=["name"])

	if projects_list:
		for row_pl in projects_list:
			if not row_pl.name in project_budget_data:
				project_budget_data[row_pl.name] = {
					"total_budget": 0,
					"total_budget_duration": 0
				}
			budgets = frappe.get_all("Project Budget Entry", filters={"project": row_pl.name}, fields=["*"])
			for row in budgets:
				if row.budget_type in ["Cost + Hours"]:
					project_budget_data[row_pl.name]["total_budget"] += flt(row.amount)
					project_budget_data[row_pl.name]["total_budget_duration"] += flt(row.amount)

				if row.budget_type in ["Monthly Hours"]:
					project_budget_data[row_pl.name]["total_budget_duration"] += flt(row.amount)
					
				if row.budget_type in ["Full Project Cost"]:
					project_budget_data[row_pl.name]["total_budget"] += flt(row.amount)
					break
	
	for row_pbd in project_budget_data:
		result["total_budget"] += project_budget_data[row_pbd]["total_budget"]
		result["total_budget_duration"] += project_budget_data[row_pbd]["total_budget_duration"]

	return result

