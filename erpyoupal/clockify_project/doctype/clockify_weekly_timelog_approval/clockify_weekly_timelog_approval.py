# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe, calendar
from datetime import datetime, timedelta
from frappe.model.document import Document
from frappe.utils import flt, getdate, time_diff_in_hours, get_datetime, get_time, now
from erpyoupal.clockify_project.doctype.clockify_timelog_processing.clockify_timelog_processing import process_timelog

class ClockifyWeeklyTimelogApproval(Document):
	def validate(self):
		self.do_process_timelog()
	
	def after_insert(self):
		self.send_email_weekly_timelog_report()

	def do_process_timelog(self):
		if not self.is_new():
			if not self.processed and self.status == "Approved" and (frappe.db.get_value("Clockify Weekly Timelog Approval", self.name, "status") != "Approved"):
				process_timelog(entry={
					"workspace": self.workspace,
					"clockify_user": self.clockify_user,
					"project": None,
					"task": None,
					"period_from": self.period_from,
					"period_to": self.period_to
					})
				self.processed = 1
	
	def get_email_weekly_timelog_report_data(self):
		result = {
			'client_name': 'Cid Zaragoza',
			'consultant_name': 'John Matthew',
			'project_name': 'ERP Youpal',
			'active_hours_sunday': 0,
			'active_hours_monday': 8,
			'active_hours_tuesday': 7,
			'active_hours_wednesday': 6,
			'active_hours_thursday': 8,
			'active_hours_friday': 8,
			'active_hours_saturday': 0,
			'total_hours_this_month': 37,
			'total_hours_last_month': 40,
			'total_hours': 77,
			'total_budget_this_month': 1000,
			'total_budget_last_month': 1200,
			'total_budget': 2200
		}
		return result

	def send_email_weekly_timelog_report(self):
		frappe.sendmail(recipients=['cid@youpal.se'], subject="Weekly Report", reply_to="cid@youpal.se", with_container=True, template='weekly_timelog_report', args=self.get_email_weekly_timelog_report_data())

#erpyoupal.clockify_project.doctype.clockify_weekly_timelog_approval.clockify_weekly_timelog_approval.run_weekly_timelog_payment
@frappe.whitelist()
def run_weekly_timelog_payment(target_date=None):
	if not target_date:
		target_date = now()
	cur_date = get_datetime(target_date)
	cur_weeknumber = cur_date.strftime("%V")
	cur_weekday = cur_date.weekday()
	weekday_dict = {
		"Monday": 0,
		"Tuesday": 1,
		"Wednesay": 2,
		"Thursday": 3,
		"Friday": 4,
		"Saturday": 5,
		"Sunday": 6,
	}
	workspaces = frappe.get_all("Clockify Workspace", fields=["name"])
	for workspace in workspaces:
		setup_weekday = 6
		workspace_doc = frappe.get_doc("Clockify Workspace", workspace.name)
		if workspace_doc.enable_weekly_restriction:
			if workspace_doc.defined_restrictions:
				setup_weekday = weekday_dict[workspace_doc.defined_restrictions[0].from_day]

		if cur_weekday in [setup_weekday, str(setup_weekday)]:
			users_to_process = {}
			period_from = cur_date-timedelta(days=7)
			period_to = cur_date-timedelta(days=1)
			#periods = [cur_date-timedelta(days=1), cur_date-timedelta(days=2), cur_date-timedelta(days=3), cur_date-timedelta(days=4), cur_date-timedelta(days=5), cur_date-timedelta(days=6), cur_date-timedelta(days=7)]
			
			timelogs = frappe.get_all("Clockify Timelog", filters={"workspace": workspace.name, "locked": 1, "billable": 1}, 
				fields=["name", "clockify_user", "time_in", "total_cost", "total_hours", "project"])
			for timelog in timelogs:
				if getdate(period_from) <=  getdate(timelog.time_in) <= getdate(period_to):
					if not timelog.clockify_user in users_to_process:
						users_to_process[timelog.clockify_user] = {
							"total_amount": 0,
							"total_hours": 0,
							"included_timelogs": []
							}
					users_to_process[timelog.clockify_user]["total_amount"] += timelog.total_cost
					users_to_process[timelog.clockify_user]["total_hours"] += timelog.total_hours
					users_to_process[timelog.clockify_user]["included_timelogs"].append({
						"clockify_timelog": timelog.name,
						"project": timelog.project,
						"time_in": timelog.time_in,
						"time_out": timelog.time_out,
						"total_hours": timelog.total_hours,
						"total_cost": timelog.total_cost,
						"status": "Pending"
						})

			if users_to_process:
				for user in users_to_process:
					new_doc = frappe.new_doc("Clockify Weekly Timelog Approval")
					new_doc.workspace = workspace.name
					new_doc.clockify_user = user
					new_doc.status = "Pending"
					new_doc.period_from = getdate(period_from)
					new_doc.period_to = getdate(period_to)
					new_doc.auto_approve_on = get_datetime(cur_date+timedelta(days=1))
					new_doc.week_number = cur_weeknumber
					new_doc.processed = 0
					new_doc.total_amount = users_to_process[user]["total_amount"]
					new_doc.total_hours = users_to_process[user]["total_hours"]
					for row in users_to_process[user]["included_timelogs"]:
						new_doc.append("weekly_timelog_table", row)
					new_doc.flags.ignore_permissions = True
					new_doc.save()


#erpyoupal.clockify_project.doctype.clockify_weekly_timelog_approval.clockify_weekly_timelog_approval.patch_fill_field_auto_approve_on
@frappe.whitelist()
def patch_fill_field_auto_approve_on(is_overwrite=1):
	cur_date = get_datetime(getdate(now()))
	clockify_weekly_timelog_approval_list = frappe.get_all('Clockify Weekly Timelog Approval', filters={'status': 'Pending'}, fields=['name', 'auto_approve_on', 'period_to'])
	for row in clockify_weekly_timelog_approval_list:
		if is_overwrite:
			frappe.db.set_value('Clockify Weekly Timelog Approval', row.name, 'auto_approve_on', get_datetime(getdate(row.period_to)+timedelta(days=1)), update_modified=False)
		else:
			if not row.auto_approve_on:
				frappe.db.set_value('Clockify Weekly Timelog Approval', row.name, 'auto_approve_on', get_datetime(getdate(row.period_to)+timedelta(days=1)), update_modified=False)


#erpyoupal.clockify_project.doctype.clockify_weekly_timelog_approval.clockify_weekly_timelog_approval.send_all_email_weekly_timelog_report
@frappe.whitelist()
def send_all_email_weekly_timelog_report():
	clockify_weekly_timelog_approval_list = frappe.get_all('Clockify Weekly Timelog Approval', filters={'status': 'Pending'}, fields=['name', 'auto_approve_on', 'period_to'])
	clockify_weekly_timelog_approval_list = [{'name': 'edcefca192'}]
	for row_cwtal in clockify_weekly_timelog_approval_list:
		cur_doc = frappe.get_doc('Clockify Weekly Timelog Approval', row_cwtal.get('name'))
		cur_doc.run_method("send_email_weekly_timelog_report")


#erpyoupal.clockify_project.doctype.clockify_weekly_timelog_approval.clockify_weekly_timelog_approval.get_weekly_report_data
@frappe.whitelist()
def get_weekly_report_data(user='hello@jamesdunkley.co.uk', target_date='2023-03-05', document_name=None):
	result = {
		'name': None,
		'user': None,
		'full_name': None,
		'position_title': None,
		'weekly_report_date': None,
		'period_from': None,
		'period_to': None,
		'workspace': None,
		'deliverables': [
			{
				'description': None,
				'screenshot': None,
				'duration': None,
				'date': None,
				'url_link': None,
				'tags': None
			}
		],
		'timesheet': [
			{
				'project': None,
				'time_in': None,
				'time_out': None,
				'total_hours': None,
				'is_billable': None
			}
		],
		'worked': {
			'hours': None,
			'date': None,
			'days_off': None,
		},
		'forecast': {
			'hours': None,
			'date': None,
			'days_off': None,
			'days_off_list': []
		},
		'to_approve': None,
		'to_file_dispute': None,
		'auto_approve_on': None
	}
	filtered_document = frappe.get_all('Clockify Weekly Timelog Approval', filters=[['clockify_user', '=', user], ['period_from', '<=', target_date], ['period_to', '>=', target_date]], fields=['name'])
	if filtered_document and not document_name:
		document_name = filtered_document[0].name
	if document_name:
		cur_doc = frappe.get_doc('Clockify Weekly Timelog Approval', document_name)
		result['name'] = cur_doc.get('name')
		result['user'] = cur_doc.get('clockify_user')
		result['full_name'] = frappe.db.get_value('Clockify User', cur_doc.get('clockify_user'), 'full_name')
		result['position_title'] = frappe.db.get_value('People', {'created_user': cur_doc.get('clockify_user')}, 'designation')
		result['period_from'] = cur_doc.period_from
		result['period_to']	= cur_doc.period_to
		result['workspace']	= cur_doc.workspace
		result['auto_approve_on'] = cur_doc.auto_approve_on
		# get weekly_report_date
		calendar_year_date = str(getdate(cur_doc.period_to))[:7]
		calendar_year_date = calendar_year_date.replace('-', '/')
		calendar_month_number = str(getdate(cur_doc.period_to))[8:]
		if calendar_month_number[:1] in [0, '0']:
			calendar_month_number = calendar_month_number[1:2]
		calendar_month_name = calendar.month_name[int(calendar_month_number)]
		result['weekly_report_date'] =  str(calendar_month_name)+" - "+str(calendar_year_date)
		#get deliverables
		result['deliverables'] = []
		result['timesheet'] = []
		for row_wtt in cur_doc.weekly_timelog_table:
			if frappe.get_all('Clockify Timelog', filters={'name': row_wtt.clockify_timelog}, fields=['name']):
				cur_doc_timelog = frappe.get_doc('Clockify Timelog', row_wtt.clockify_timelog)
				screenshot = None
				if cur_doc_timelog.screenshots:
					screenshot = cur_doc_timelog.screenshots[0].screenshot

				tags = None
				if cur_doc_timelog.tags:
					for row_cdtt in cur_doc_timelog.tags:
						if tags == None:
							tags = ""
						tags += "#"+str(row_cdtt.tag_name)+" "

				result['deliverables'].append({
					'description': cur_doc_timelog.description,
					'screenshot': screenshot,
					'duration': str(cur_doc_timelog.total_hours)+"hr",
					'date': str(getdate(cur_doc_timelog.time_in)),
					'url_link': "http://localhost:8081/app/clockify-timelog/"+str(cur_doc_timelog.name),
					'tags': tags
				})
			result['timesheet'].append(
				{
					'project': row_wtt.project,
					'time_in': row_wtt.time_in,
					'time_out': row_wtt.time_out,
					'total_hours': row_wtt.total_hours,
					'is_billable': "Billable" if cur_doc_timelog.billable else "Non Billable"
				}
			)
		
			result['worked']['hours'] = row_wtt.total_hours
			result['worked']['date'] = getdate(cur_doc.period_to)
			result['worked']['days_off'] = 0
			result['worked']['forecast'] = row_wtt.total_hours
			result['worked']['date'] = getdate(cur_doc.period_to)
			result['worked']['days_off'] = 0

	return result
