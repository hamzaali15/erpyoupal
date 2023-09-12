// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Clockify Detailed Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "Clockify User"
		},
		{
			"fieldname": "workspace_id",
			"label": __("Workspace ID"),
			"fieldtype": "Link",
			"options": "Clockify Workspace"
		},
		{
			"fieldname": "project_id",
			"label": __("Project ID"),
			"fieldtype": "Link",
			"options": "Clockify Projects"
		},
		{
			"fieldname": "task_id",
			"label": __("Task ID"),
			"fieldtype": "Link",
			"options": "Clockify Task"
		}
	]
};
