// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

var firstday = getDateWeekFirstday(frappe.datetime.get_today());
var lastday = getDateWeekLastday(frappe.datetime.get_today());

function getDateWeekFirstday(curdate) {
    var curr = new Date(curdate);
	var firstday = new Date(curr.setDate(curr.getDate() - curr.getDay()));
    return firstday;
}

function getDateWeekLastday(curdate) {
    var curr = new Date(curdate);
	var lastday = new Date(curr.setDate(curr.getDate() - curr.getDay()+6));
    return lastday;
}

function getDatMonthFirstday(curdate) {
    var curr = new Date(curdate);
	//var firstDay = new Date(curr.getFullYear(), curr.getMonth(), 1);
	var firstday = [curr.getFullYear(), curr.getMonth()+1, '01'].join('-');
    return firstday;
}

function getDatMonthLastday(curdate) {
    var curr = new Date(curdate);
	var lastDay = new Date(curr.getFullYear(), curr.getMonth() + 1, 0);
    return lastDay;
}

function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}

frappe.query_reports["Clockify Timelog Report"] = {
	"filters": [
		{
			"fieldname": "quick_date_range",
			"label": __("Quick Date Range"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": [
				{ "value": "This Week", "label": __("This Week") },
				{ "value": "Last Week", "label": __("Last Week") },
				{ "value": "This Month", "label": __("This Month") },
				{ "value": "Last Month", "label": __("Last Month") },
			],
			"default": "This Week",
			"on_change": function(query_report) {
				var quick_date_range = frappe.query_report.get_filter_value('quick_date_range');
				if (quick_date_range=='This Week') {
					var curdate = new Date(frappe.datetime.get_today());
					var firstday = getDateWeekFirstday(curdate);
					var lastday = getDateWeekLastday(curdate)
					frappe.query_report.set_filter_value('from_date', firstday);
					frappe.query_report.set_filter_value('to_date', lastday);
					query_report.refresh();
				}
				if (quick_date_range=='Last Week') {
					var curdate = new Date(frappe.datetime.get_today());
					curdate.setDate(curdate.getDate()-7);
					var firstday = getDateWeekFirstday(curdate);
					var lastday = getDateWeekLastday(curdate)
					frappe.query_report.set_filter_value('from_date', firstday);
					frappe.query_report.set_filter_value('to_date', lastday);
					query_report.refresh();
				}
				if (quick_date_range=='This Month') {
					var curdate = new Date(frappe.datetime.get_today());
					got_month = ('0' + (curdate.getMonth() + 1)).slice(-2)
					var firstday = [curdate.getFullYear(), got_month, '01'].join('-');
					var lastday = getDatMonthLastday(curdate);
					frappe.query_report.set_filter_value('from_date', firstday);
					frappe.query_report.set_filter_value('to_date', lastday);
					query_report.refresh();
				}
				if (quick_date_range=='Last Month') {
					var curdate = new Date(frappe.datetime.get_today());
					curdate.setMonth(curdate.getMonth() - 1);
					got_month = ('0' + (curdate.getMonth() + 1)).slice(-2)
					var firstday = [curdate.getFullYear(), got_month, '01'].join('-');
					var lastday = getDatMonthLastday(curdate);
					frappe.query_report.set_filter_value('from_date', firstday);
					frappe.query_report.set_filter_value('to_date', lastday);
					query_report.refresh();
				}
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": formatDate(firstday)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": formatDate(lastday)
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
		{
			"fieldname": "full_name",
			"label": __("Full name"),
			"fieldtype": "Data"
		},
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "Clockify User"
		},
		{
			"fieldname": "task_id",
			"label": __("Task ID"),
			"fieldtype": "Link",
			"options": "Clockify Task"
		}
	]
};
