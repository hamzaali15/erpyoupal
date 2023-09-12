// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

const month = ["January","February","March","April","May","June","July","August","September","October","November","December"];

const date_today = new Date(frappe.datetime.get_today());
let today_monthname = month[date_today.getMonth()];
var firstday = getDatMonthFirstday(frappe.datetime.get_today());
var lastday = getDatMonthLastday(frappe.datetime.get_today());

function getDatMonthFirstday(curdate) {
    var curr = new Date(curdate);
	//var firstDay = new Date(curr.getFullYear(), curr.getMonth(), 1);
	var currmonth = curr.getMonth()+1
	if (currmonth.length == 1 || currmonth.length == '1'){
		var currmonth = '0'+currmonth.toString();
	}
	var firstday = [curr.getFullYear(), currmonth, '01'].join('-');
	var firstday = new Date(firstday);
    return firstday;
}

function getDatMonthLastday(curdate) {
    var curr = new Date(curdate);
	var currmonth = curr.getMonth()+1
	if (currmonth.length == 1 || currmonth.length == '1'){
		var currmonth = '0'+currmonth.toString();
	}
	var lastDay = new Date(curr.getFullYear(), currmonth, 0);
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

const month_dict = {
	'January': '01',
	'February': '02',
	'March': '03',
	'April': '04',
	'May': '05',
	'June': '06',
	'July': '07',
	'August': '08',
	'September': '09',
	'October': '10',
	'November': '11',
	'December': '12',
  }

frappe.query_reports["Clockify Cost and Revenue Report"] = {
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
			"default": today_monthname,
			"on_change": function(query_report) {
				var month = frappe.query_report.get_filter_value('month');
				var monthdate = [date_today.getFullYear(), month_dict[month], '01'].join('-');
				var curdate = new Date(monthdate);
				var firstday = getDatMonthFirstday(curdate);
				var lastday = getDatMonthLastday(curdate)
				console.log(firstday);
				console.log(lastday);
				frappe.query_report.set_filter_value('from_date', firstday);
				frappe.query_report.set_filter_value('to_date', lastday);
				query_report.refresh();
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
			"default": "Youpal Group - App"
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
			"fieldname": "report_by",
			"label": __("Report By"),
			"fieldtype": "Select",
			"options": [
				{ "value": "Per Project", "label": __("Per Project") },
				{ "value": "Per User", "label": __("Per User") },
				{ "value": "Per Project & User", "label": __("Per Project & User") }
			],
			"default": "Per Project"
		},
	]
};
