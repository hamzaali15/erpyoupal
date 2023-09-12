# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
from typing import List
import frappe
import datetime
from datetime import timedelta
import time
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, get_timespan_date_range, time_diff_in_hours, get_datetime, get_time, now

from erpyoupal.clockify_project.clockify_api import add_timelog_to_clockify, format_normal_to_iso_datetime, validate_clockify_user, delete_clockify_timelog, update_timelog_to_clockify
from erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects import get_project_totals

class ClockifyTimelog(Document):
	def validate(self):
		if not self.status:
			self.status = 'Pending'
		self.get_user_fullname()
		self.vlaidate_locked_timelog()
		self.validate_time_in_out()
		self.get_totaltime()
		if not self.get("skip_restriction"):
			validate_timelog_restriction_result = validate_timelog_restriction(self.workspace, self.time_in, self.time_out)
			if str(validate_timelog_restriction_result) in ["Failed. Timelog Restricted"]:
				frappe.throw(_("Failed. Timelog Restricted"))
		if self.is_new() and not self.workspace:
			frappe.throw(_("Workspace is required"))
		if not self.is_new():
			self.update_clockify_timelog()
		self.get_total_cost()
		#save project
		if self.project:
			clockify_project = frappe.get_doc('Clockify Projects', self.project)
			clockify_project.flags.ignore_permissions = True
			clockify_project.save()

	def get_user_fullname(self):
		self.full_name = frappe.db.get_value('Clockify User', self.clockify_user, 'full_name')

	def vlaidate_locked_timelog(self):
		if not self.is_new() and frappe.db.get_value('Clockify Timelog', self.name, 'locked') and self.locked:
			frappe.throw(_("Failed, Timelog is locked."))

	def get_total_cost(self):
		hourly_rate = frappe.db.get_value('Clockify User', self.clockify_user, 'rate')
		if self.project:
			clockify_project = frappe.get_doc('Clockify Projects', self.project)
			if clockify_project and clockify_project.erp_members:
				for mem in clockify_project.erp_members:
					if self.clockify_user == mem.clockify_user:
						if self.hourly_rate:
							hourly_rate = self.hourly_rate
							break
		if not self.hourly_rate:
			self.hourly_rate = hourly_rate
		if not self.total_cost:
			self.total_cost = hourly_rate * self.total_hours

	def update_clockify_timelog(self):
		if not self.get('pulled_from_clockify') and self.clockify_timelog_id and self.sync_with_clockify:
			if validate_clockify_user(self.clockify_user):
				timelog_data = {
					"start": format_normal_to_iso_datetime(self.time_in),
					"billable": self.billable,
					"description": self.description,
					"projectId": frappe.db.get_value('Clockify Projects', {'name': self.project}, 'clockify_project_id'),
					"taskId": self.task_id,
					"end": format_normal_to_iso_datetime(self.time_out)
				}
				if self.tags:
					timelog_data["tagIds"] = []
					for tag in self.tags:
						tag_id = frappe.db.get_value('Clockify Tag', {'name': tag.tag_name}, 'clockify_id')
						timelog_data["tagIds"].append(tag_id)
						update_timelog_to_clockify_result = update_timelog_to_clockify(email=self.clockify_user, workspace_id=frappe.db.get_value('Clockify Workspace', self.workspace, 'clockify_workspace_id'), timelog_id=self.clockify_timelog_id, data=timelog_data)
						if update_timelog_to_clockify_result and type(update_timelog_to_clockify_result) in [dict]:
							pass
						else:
							self.db_set('sync_with_clockify', 0)

	def after_insert(self):
		if not self.get('pulled_from_clockify'):
			if validate_clockify_user(self.clockify_user) and self.sync_with_clockify:
				timelog_data = {
					"start": format_normal_to_iso_datetime(self.time_in),
					"billable": self.billable,
					"description": self.description,
					"projectId": frappe.db.get_value('Clockify Projects', {'name': self.project}, 'project_id'),
					"taskId": frappe.db.get_value('Clockify Task', {'name': self.task}, 'clockify_task_id'),
					"end": format_normal_to_iso_datetime(self.time_out)
				}
				if self.tags:
					timelog_data["tagIds"] = []
					for tag in self.tags:
						tag_id = frappe.db.get_value('Clockify Tag', {'name': tag.tag_name}, 'clockify_id')
						timelog_data["tagIds"].append(tag_id)

				add_timelog_to_clockify_result = add_timelog_to_clockify(email=self.clockify_user, workspace_id=frappe.db.get_value('Clockify Workspace', self.workspace, 'clockify_workspace_id'), data=timelog_data)
				if add_timelog_to_clockify_result and type(add_timelog_to_clockify_result) in [dict]:
					self.db_set('clockify_timelog_id', add_timelog_to_clockify_result.get('id'))
				else:
					self.db_set('sync_with_clockify', 0)

	def on_trash(self):
		if validate_clockify_user(self.clockify_user) and self.workspace and self.clockify_timelog_id:
			delete_clockify_timelog_result = delete_clockify_timelog(email=self.clockify_user, workspace_id=frappe.db.get_value('Clockify Workspace', self.workspace, 'clockify_workspace_id'), timelog_id=self.clockify_timelog_id)
			if delete_clockify_timelog_result:
				if delete_clockify_timelog_result.status_code in [204, '204', 200, '200']:
					frappe.msgprint(_("Clockify Timelog Deleted"))

	def validate_time_in_out(self):
		if self.time_in > self.time_out:
			frappe.throw(_("Time In cannot be greater than Time Out"))
		#if flt((get_datetime(self.time_out)-get_datetime(self.time_in)).days) >= 2:
		#	frappe.throw(_("Time Out Invalid"))

	def get_task_details(self):
		pass
		#doc = frappe.get_all("Clockify Task", filters={"name": self.clockify_task}, fields=["name", "task", "task_id"])
		#if doc:
		#	self.task = doc[0].task
		#	self.task_id = doc[0].task_id

	def get_totaltime(self):
		time_diff = (get_datetime(self.time_out) - get_datetime(self.time_in))
		total_seconds = time_diff.total_seconds()
		self.total_seconds = total_seconds
		self.total_hours = total_seconds/3600
		self.total_time = format_seconds_to_hhmmss(seconds=total_seconds)
		self.week_number = get_datetime(self.time_in).strftime("%V")
		week_number_now = get_datetime(now()).strftime("%V")
		if int(self.week_number) != int(week_number_now):
			self.locked = 1
			#validate_timelog_restriction(workspace_id, time_in, time_out)

@frappe.whitelist()
def format_seconds_to_hhmmss(seconds):
	hours = seconds // (60*60)
	seconds %= (60*60)
	minutes = seconds // 60
	seconds %= 60
	return "%02i:%02i:%02i" % (hours, minutes, seconds)

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.validate_timelog_restriction
@frappe.whitelist(allow_guest=True)
def validate_timelog_restriction(workspace_id, time_in, time_out):
	result = "Timelog not restricted"
	clockify_project = None
	clockify_projects = frappe.get_all("Clockify Workspace", filters={'name': workspace_id}, fields=['name', 'enable_weekly_restriction'])
	if clockify_projects:
		clockify_project = clockify_projects[0]

	if clockify_project and clockify_project.get('enable_weekly_restriction'):
		doc = frappe.get_doc("Clockify Workspace", clockify_project.name)
		if doc.defined_restrictions:
			for restr in doc.defined_restrictions:
				log_time_in = get_datetime(time_in)
				log_time_in_time = get_time(log_time_in)
				log_time_in_weekday = log_time_in.weekday()
				log_time_out = get_datetime(time_out)
				log_time_out_time = get_time(log_time_out)
				log_time_out_weekday = log_time_out.weekday()
				day_dict = {
					'Monday': 0,
					'Tuesday': 1,
					'Wednesday': 2,
					'Thursday': 3,
					'Friday': 4,
					'Saturday': 5,
					'Sunday': 6
				}
				to_be_restricted = 0

				included_weekdays = []
				restr_from_day = int(day_dict[restr.from_day])
				restr_to_day = int(day_dict[restr.to_day])
				if int(restr_from_day) > int(restr_to_day):
					restr_from_day = (-restr_from_day)
				if int(restr_from_day) <= int(log_time_in_weekday) <= int(restr_to_day):
					to_be_restricted = 1
				if to_be_restricted:
					restriction_fromtime = get_time(restr.from_time)
					restriction_totime = get_time(restr.to_time)
					to_be_restricted = 0
					if int(restr_from_day) == int(log_time_in_weekday):
						if restriction_fromtime <= log_time_in_time <= restriction_totime:
							to_be_restricted = 1
					else:
						if get_time('00:00:00') <= log_time_out_time <= restriction_totime:
							to_be_restricted = 1
				if to_be_restricted:
					result = "Failed. Timelog Restricted"

	return result

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.create_clockify_timelog
@frappe.whitelist()
def create_clockify_timelog(clockify_user, workspace_id, project, description=None, time_in=None, time_out=None, sync_to_clockify=0, billable=0, tags_included=[], clockify_task=None, task=None, task_id=None, linktext=None, attachments=[]):
	if time_in and time_out:
		doc = frappe.new_doc("Clockify Timelog")
		doc.workspace = workspace_id
		doc.clockify_user = clockify_user
		doc.project = project
		doc.task = clockify_task
		doc.description = description
		if time_in:
			doc.time_in = get_datetime(time_in)
		if time_out:
			doc.time_out = get_datetime(time_out)
		doc.billable = billable
		doc.sync_with_clockify = sync_to_clockify
		if tags_included:
			for tag in tags_included["tags"]:
				doc.append("tags", {"tag_name": tag["tag_name"]})
		if linktext:
			doc.external_link = linktext
		doc.flags.ignore_permissions = True
		return doc.insert()
	else:
		return "Time In and Out required"

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.duplicate_clockify_timelog
@frappe.whitelist()
def duplicate_clockify_timelog(timelog_id):
	if frappe.db.exists("Clockify Timelog", {"name": timelog_id}):
		doc = frappe.get_doc("Clockify Timelog", {"name": timelog_id})
		new_doc = frappe.new_doc("Clockify Timelog")
		new_doc.workspace = doc.workspace
		new_doc.clockify_user = doc.clockify_user
		new_doc.project = doc.project
		new_doc.task = doc.task
		new_doc.description = doc.description
		new_doc.time_in = doc.time_in
		new_doc.time_out = doc.time_out
		new_doc.billable = doc.billable
		new_doc.sync_with_clockify = doc.sync_with_clockify
		for tag in doc.tags:
			new_doc.append("tags", {"tag_name": tag["tag_name"]})
		new_doc.external_link = doc.external_link
		for att in doc.screenshots:
			new_doc.append("screenshots", {'screenshots': att["screenshots"]})
		doc.flags.ignore_permissions = True
		return doc.insert()

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.add_timelog_screenshots
@frappe.whitelist()
def add_timelog_screenshots(data):
	result = None
	if not data["timelog_id"]:
		frappe.throw("screenshots is required")
	if not data["screenshots"]:
		frappe.throw("screenshots is required")
	if frappe.get_all("Clockify Timelog", filters={"name": data["timelog_id"]}, fields=["name"]):
		doc = frappe.get_doc("Clockify Timelog", data["timelog_id"])
		for row in data["screenshots"]:
			doc.append("screenshots", {"screenshots": row})
		doc.flags.ignore_permissions = True
		doc.flags.ignore_links = True
		result = doc.save()

	return "ok"

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.create_clockify_timelog_using_manual_time
@frappe.whitelist()
def create_clockify_timelog_using_manual_time(clockify_user, workspace_id, project, description=None, time_in=None, sync_to_clockify=0, billable=0, tags_included=[], clockify_task=None, task=None, task_id=None):
	if time_in:
		doc = frappe.new_doc("Clockify Timelog")
		doc.workspace = workspace_id
		doc.clockify_user = clockify_user
		doc.project = project
		doc.task = clockify_task
		doc.description = description
		if time_in:
			doc.time_in = get_datetime(time_in)
			doc.time_out = get_datetime(time_in)
		doc.billable = billable
		doc.sync_with_clockify = sync_to_clockify
		if tags_included:
			for tag in tags_included["tags"]:
				doc.append("tags", {"tag_name": tag["tag_name"]})
		doc.flags.ignore_permissions = True
		return doc.insert()
	else:
		return "Time In required"


#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.edit_clockify_timelog_using_manual_time
@frappe.whitelist()
def edit_clockify_timelog_using_manual_time(timelog_id, time_out=None):
	if time_out:
		doc = frappe.get_doc("Clockify Timelog", {"name": timelog_id})
		doc.time_out = get_datetime(time_out)
		doc.flags.ignore_permissions = True
		frappe.db.commit()
		return doc.save()
	else:
		return "Time Out required"


#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.edit_clockify_timelog
@frappe.whitelist()
def edit_clockify_timelog(erp_timelog_id, project=None, description=None, time_in=None, time_out=None, sync_to_clockify=0, billable=0, tags_included=[], clockify_task=None, task=None, task_id=None, edit_data={}, linktext=None, screenshot_url=None):
	if erp_timelog_id:
		doc = frappe.get_doc("Clockify Timelog", erp_timelog_id)
		if doc.locked:
			return "Failed, Timelog is locked"
		else:
			if edit_data:
				if time_in in edit_data:
					edit_data["time_in"] = get_datetime(edit_data["time_in"])
				if time_out in edit_data:
					edit_data["time_out"] = get_datetime(edit_data["time_out"])
				doc.update(edit_data)
			else:
				if project:
					doc.project = project
				if project in ["TO_REMOVE"]:
					doc.project = None
				if billable:
					doc.billable = billable
				if description:
					doc.description = description
				if description in ["TO_REMOVE"]:
					doc.description = None
				if sync_to_clockify:
					doc.sync_with_clockify = sync_to_clockify
				if time_in:
					doc.time_in = get_datetime(time_in)
				if time_out:
					doc.time_out = get_datetime(time_out)
				if tags_included:
					for tag in tags_included["tags"]:
						doc.append("tags", {"tag_name": tag["tag_name"]})
				if tags_included in ["TO_REMOVE"]:
					doc.tags = None
				if task:
					doc.task = task
				if task in ["TO_REMOVE"]:
					doc.task = None
				if linktext:
					doc.external_link = linktext
#				if screenshot_url:
#					doc.append("attachments", {
#						'screenshots': screenshot_url
#					})
			doc.skip_restriction = 1
			doc.flags.ignore_permissions = True
			return doc.save()
	else:
		return "Invalid Data"

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.get_clockify_timelog
@frappe.whitelist()
def get_clockify_timelog(filters={}):
	result = []
	result_data = {}
	docs = frappe.get_all("Clockify Timelog", filters=filters, fields=["name"], order_by='time_in desc')
	if docs:
		for dos in docs:
			doc = frappe.get_doc("Clockify Timelog", dos.name)
			doc_data = {
				"name": doc.name,
				"workspace": doc.workspace,
				"clockify_user": doc.clockify_user,
				"project": doc.project,
				"task": doc.task,
				"tags": doc.tags,
				"description": doc.description,
				"erp_timelog_id": doc.erp_timelog_id,
				"clockify_timelog_id": doc.clockify_timelog_id,
				"time_in": doc.time_in,
				"time_out": doc.time_out,
				"total_time": doc.total_time,
				"total_hours": doc.total_hours,
				"total_seconds": doc.total_seconds,
				"billable": doc.billable,
				"locked": doc.locked,
				"sync_with_clockify": doc.sync_with_clockify,
				"external_link": doc.external_link,
				"screenshots": doc.screenshots,
				"time_in_time_only": str(doc.time_in)[11:] if doc.time_in else None,
				"time_out_time_only": str(doc.time_out)[11:] if doc.time_out else None
			}
			# for att in doc.attachments:
			# 	doc_data.append("attachments", {
			# 		'screenshots': att["screenshots"]
			# 	})
			target_date = None
			if doc.time_in:
				target_date = getdate(doc.time_in)
			if not doc.time_in and doc.time_out:
				target_date = getdate(doc.time_out)
			if target_date:
				target_date = str(getdate(target_date))
				if target_date not in result_data:
					result_data[target_date] = {
						'date': target_date,
						'logs': [],
						'total_time': "00:00:00",
						'total_hours': 0,
						'total_seconds': 0
					}
				result_data[target_date]['logs'].append(doc_data)
				result_data[target_date]['total_hours'] += flt(doc.total_hours)
				result_data[target_date]['total_seconds'] += flt(doc.total_seconds)
				result_data[target_date]['total_time'] = format_seconds_to_hhmmss(seconds=result_data[target_date]['total_seconds'])
	
	for res_d in result_data:
		result.append(result_data[res_d])

	return result


#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.get_project_timelog
@frappe.whitelist()
def get_project_timelog(project,date):
	now = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
	if date == "This Week":
		now = now - timedelta(days=now.weekday())
	elif date == "This Month":
		now = now.replace(day=1)
	elif date == "This Year":
		now = now.replace(day=1,month=1)
	return frappe.db.sql("""SELECT * FROM `tabClockify Timelog` WHERE project = %s AND time_out >= %s""",(project,now),as_dict=True)


#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.get_clockify_timelog_summary
@frappe.whitelist()
def get_clockify_timelog_summary(user):
	weekly_summary = []
	now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	first_date = now - timedelta(days=now.weekday())
	last_date = first_date + timedelta(days=6)
	weekly_log = frappe.db.sql("""SELECT sum(total_hours) as total_hours, WEEKDAY(time_in) as date
	FROM `tabClockify Timelog` WHERE time_in >= '{0}' AND time_in <= '{1}' AND clockify_user = '{2}'
	GROUP BY CAST(time_in AS DATE) order by time_in""".format(first_date, last_date, user), as_dict=True)

	for log in weekly_log:
		if log.date == 0:
			weekly_summary.append({"Monday": log.total_hours})
		elif log.date == 1:
			weekly_summary.append({"Tuesday": log.total_hours})
		elif log.date == 2:
			weekly_summary.append({"Wednesday": log.total_hours})
		elif log.date == 3:
			weekly_summary.append({"Thursday": log.total_hours})
		elif log.date == 4:
			weekly_summary.append({"Friday": log.total_hours})
		elif log.date == 5:
			weekly_summary.append({"Saturday": log.total_hours})
		elif log.date == 6:
			weekly_summary.append({"Sunday": log.total_hours})
	return weekly_summary


#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.validate_timelog_lock
@frappe.whitelist()
def validate_timelog_lock():
	timelogs = frappe.get_all("Clockify Timelog", filters={"locked": 0}, fields=["name"])
	if timelogs:
		for timelog in timelogs:
			doc = frappe.get_doc("Clockify Timelog", timelog.name)
			doc.flags.ignore_permissions = True
			try:
				doc.save()
			except Exception as e:
				pass
			else:
				pass
			finally:
				pass

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.resave_timelog
@frappe.whitelist()
def resave_timelog():
	timelogs = frappe.get_all("Clockify Timelog", fields=["name"])
	for timelog in timelogs:
		doc = frappe.get_doc("Clockify Timelog", timelog.name)
		doc.flags.ignore_permissions = True
		try:
			doc.save()
		except Exception as e:
			pass
		else:
			pass
		finally:
			pass

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.delete_timelog
@frappe.whitelist()
def delete_timelog(timelog_id):
	result = "Failed to deleted Timelog"
	if frappe.db.exists("Clockify Timelog", {"name": timelog_id}):
		doc = frappe.get_doc("Clockify Timelog", timelog_id)
		if not doc.locked:
			doc.flags.ignore_permissions = True
			frappe.db.delete("Clockify Timelog", {"name": timelog_id})
			frappe.db.commit()
			result = "Timelog deleted"
		else:
			result = "Failed, Timelog is locked"
	else:
		result = "Timelog not found"
	return result

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.get_clockify_timelog_hours
@frappe.whitelist()
def get_clockify_timelog_hours(timespan, user):
	now = datetime.datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
	if timespan == "This Week":
		first_date = now - timedelta(days=now.weekday())
	elif timespan == "This Month":
		first_date = now.replace(day=1)
	elif timespan == "This Year":
		first_date = now.replace(day=1, month=1)
	total_hours = frappe.db.sql("""SELECT sum(total_hours) as total_hours FROM `tabClockify Timelog` WHERE time_in >= '{0}' AND time_in <= '{1}' AND clockify_user = '{2}'""".format(first_date, now, user), as_dict=True)
	return total_hours

#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.run_patch_get_fullname
@frappe.whitelist()
def run_patch_get_fullname():
	timelogs = frappe.get_all('Clockify Timelog', fields=['name', 'clockify_user'])
	for row_timelogs in timelogs:
		full_name = frappe.db.get_value('Clockify User', row_timelogs.clockify_user, 'full_name')
		frappe.db.set_value('Clockify Timelog', row_timelogs.name, 'full_name', full_name, update_modified=False)
		frappe.db.set_value('Clockify Timelog', row_timelogs.name, 'status', 'Pending', update_modified=False)


#erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog.run_patch_get_fullname_user
@frappe.whitelist()
def run_patch_get_fullname_user():
	users = frappe.get_all('Clockify User', fields=['name'])
	for row_users in users:
		doc = frappe.get_doc('Clockify User', row_users.name)
		doc.flags.ignore_permissions = True
		doc.flags.ignore_links = True
		doc.save()
		
