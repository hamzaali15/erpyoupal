// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Clockify Cost Report"] = {
	"filters": [
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": [
				{ "value": "January", "label": __("January") },
				{ "value": "February", "label": __("February") },
				{ "value": "March", "label": __("March") },
				{ "value": "April", "label": __("April") },
				{ "value": "May", "label": __("May") },
				{ "value": "June", "label": __("June") },
				{ "value": "July", "label": __("July") },
				{ "value": "August", "label": __("August") },
				{ "value": "September", "label": __("September") },
				{ "value": "October", "label": __("October") },
				{ "value": "November", "label": __("November") },
				{ "value": "December", "label": __("December") }
			],
			"default": "November",
		},
		{
			"fieldname": "workspace_id",
			"label": __("Workspace ID"),
			"fieldtype": "Link",
			"options": "Clockify Workspace",
			"default": "Youpal Group"
		},
		{
			"fieldname": "project_id",
			"label": __("Project ID"),
			"fieldtype": "Link",
			"options": "Clockify Projects",
			"get_query": function() {
				var workspace_id = frappe.query_report.get_filter_value('workspace_id');
				return{
					filters: {
						'workspace': workspace_id
					}
				};
			}
		},
	]
};
