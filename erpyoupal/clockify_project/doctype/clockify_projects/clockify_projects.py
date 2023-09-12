# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
import datetime
from datetime import timedelta
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, now, time_diff_in_hours, get_datetime
from erpyoupal.clockify_project.clockify_api import add_project_to_clockify, validate_clockify_user, update_clockify_project, delete_clockify_project
from erpyoupal.clockify_project.doctype.clockify_user.clockify_user import create_clockify_user_from_people

class ClockifyProjects(Document):
	def autoname(self):
		self.get_project_name()

	def get_project_name(self):
		projectname = None
		name_ext = "App"			
		if self.erp_project_name:
			projectname = self.erp_project_name
		if self.clockify_project_id:
			name_ext = "Clockify"
		if self.clockify_project_name:
			projectname = self.clockify_project_name

		if not projectname:
			frappe.throw(_("App/Clockify Project Name is required"))

		self.project_name = projectname
		self.name_extension = name_ext
		self.project_fullname = projectname #+" - "+name_ext
		self.erp_project_id = self.project_fullname

	def validate(self):
		if self.workspace and not self.organization:
			if frappe.get_all('Clockify Workspace', filters={'name': self.workspace}, fields=['name']):
				self.organization = frappe.db.get_value('Clockify Workspace', self.workspace, 'organization')
		self.remove_duplicate_members()
		self.archived_project()
		self.calculate_amounts()
		self.add_erpmembers_to_workspace()
	
	def remove_duplicate_members(self):
		final_members = []
		included_members = []
		if self.erp_members:
			for row_erp_members in self.erp_members:
				if not row_erp_members.clockify_user in included_members:
					included_members.append( row_erp_members.clockify_user )
					final_members.append(row_erp_members)
		if final_members:
			self.erp_members = final_members
	
	def add_erpmembers_to_workspace(self):
		if self.erp_members:
			doc = frappe.get_doc("Clockify Workspace", self.workspace)
			erp_members = str(doc.erp_members)
			erp_members.replace(" ", "")
			new_erp_members = []
			if erp_members:
				new_erp_members = erp_members.split(",")
			for row in self.erp_members:
				if row.clockify_user and not row.clockify_user in erp_members:
					new_erp_members.append(row.clockify_user)
			if new_erp_members:
				doc.erp_members = ', '.join(new_erp_members)
			doc.flags.ignore_permissions = True
			doc.save()

	def on_trash(self):
		if self.archive:
			if self.sync_with_clockify:
				clockify_user = None
				workspaces = frappe.get_all("Clockify Workspace", filters={'name': self.workspace}, fields=['name', 'default_owner', 'clockify_workspace_id'])
				if workspaces:
					clockify_user = workspaces[0].default_owner
					delete_clockify_project_result = delete_clockify_project(email=clockify_user, workspace_id=workspaces[0].clockify_workspace_id, project_id=self.clockify_project_id)
					if delete_clockify_project_result:
						if delete_clockify_project_result.status_code in [204, '204', 200, '200']:
							frappe.msgprint(_("Clockify Project Deleted"))
		else:
			pass
			#frappe.throw(_("You cant delete unarchived projects"))

	def archived_project(self):
		if self.sync_with_clockify:
			clockify_user = None
			workspaces = frappe.get_all("Clockify Workspace", filters={'name': self.workspace}, fields=['name', 'default_owner', 'clockify_workspace_id'])
			if workspaces:
				clockify_user = workspaces[0].default_owner
				data = {'archived': self.archive}
				update_clockify_project(email=clockify_user, workspace_id=workspaces[0].clockify_workspace_id, project_id=self.clockify_project_id, data=data)

	def after_insert(self):
		if not self.get('pulled_from_clockify'):
			if self.sync_with_clockify:
				clockify_user = None
				workspaces = frappe.get_all("Clockify Workspace", filters={'name': self.workspace}, fields=['name', 'default_owner', 'clockify_workspace_id'])
				if workspaces:
					clockify_user = workspaces[0].default_owner

				if clockify_user and validate_clockify_user(clockify_user):
					isPublic = False
					if self.visibility == "Public":
						isPublic = True

					add_project_to_clockify_result = add_project_to_clockify(email=clockify_user, workspace_id=workspaces[0].clockify_workspace_id, data={
						"name": self.clockify_project_name,
						"clientId": self.client,
						"workspaceId": workspaces[0].clockify_workspace_id,
						"isPublic": isPublic,
						"color": self.color,
						"note": self.note,
						"billable": self.billable,
						"public": isPublic
					})
					if add_project_to_clockify_result and type(add_project_to_clockify_result) in [dict]:
						self.db_set('clockify_project_id', add_project_to_clockify_result.get('id'))

	def calculate_amounts(self):
		#TOTAL COST
		total_cost = 0
		total_cost_to_pay = 0
		total_hours_consumed = 0
		cost_per_user = {}
		if self.erp_members:
			for pmem in self.erp_members:
				if not pmem.clockify_user in cost_per_user:
					cost_per_user[pmem.clockify_user] = pmem.hourly_rate if pmem.hourly_rate else 0

		#Task Hours
		task_per_project = {}
		if self.erp_tasks:
			for ptask in self.erp_tasks:
				if ptask.task and not ptask.task in task_per_project:
					task_per_project[ptask.task] = {
						"assignees": ptask.assignees,
						"total_hours_spent": 0,
					}

		#Timelogs counting
		timelogs = frappe.get_all("Clockify Timelog", filters={"project": self.name}, fields=["name", "total_seconds", "billable", "clockify_user", "task"])
		for timelog in timelogs:
			if timelog.clockify_user in cost_per_user:
				total_hours_consumed += flt(timelog.total_seconds)/3600
				total_cost += (flt(timelog.total_seconds)/3600)*flt(cost_per_user[timelog.clockify_user])
				if timelog.billable:
					total_cost_to_pay += (flt(timelog.total_seconds)/3600)*flt(cost_per_user[timelog.clockify_user])
			if timelog.task and timelog.task in task_per_project:
				if not task_per_project[timelog.task]["assignees"]:
					task_per_project[timelog.task]["total_hours_spent"] += flt(timelog.total_seconds)/3600
				if task_per_project[timelog.task]["assignees"] and (timelog.clockify_user in task_per_project[timelog.task]["assignees"]) or (task_per_project[timelog.task]["assignees"] in ['Anyone', None]):
					task_per_project[timelog.task]["total_hours_spent"] += flt(timelog.total_seconds)/3600
					

		#assign new
		if self.erp_tasks:
			for newtask in self.erp_tasks:
				if newtask.task:
					newtask.total_hours_spent = task_per_project[newtask.task]["total_hours_spent"]
		self.total_cost = total_cost_to_pay
		self.total_hours_consumed = total_hours_consumed


#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.get_clockify_project
@frappe.whitelist()
def get_clockify_project(filters={}):
	result = []
	docs = frappe.get_all("Clockify Projects", filters=filters, fields=["name"])
	if docs:
		for dos in docs:
			doc = frappe.get_doc("Clockify Projects", dos.name)
			result.append(doc)

	return result


#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.get_workspace_projects
@frappe.whitelist()
def get_workspace_projects(workspace):
	result = []
	docs = frappe.get_all("Clockify Projects", filters={"workspace": workspace}, fields=["name"])
	if docs:
		for dos in docs:
			doc = frappe.get_doc("Clockify Projects", dos.name)
			result.append(doc)

	return result


#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.add_last_feedback_submission_date
@frappe.whitelist()
def add_last_feedback_submission_date(user, submission_time=None):
	if frappe.db.exists("Clockify User", {"user_id": user}):
		if submission_time:
			doc = frappe.get_doc("Clockify User", {"user_id": user})
			doc.last_feedback_submission_date = get_datetime(now())
			doc.flags.ignore_permissions = True
			frappe.db.commit()
			return doc.save()
		else:
			return "SUBMISSION TIME IS NOT DEFINED"
	else:
		return "USER NOT FOUND"

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.get_last_feedback_submission_date
@frappe.whitelist()
def get_last_feedback_submission_date(user):
	if frappe.db.exists("Clockify User", {"user_id": user}):
		return frappe.db.sql("""SELECT last_feedback_submission_date FROM `tabClockify User` WHERE user_id = '{0}'""".format(user), as_dict=True)
	else:
		return "USER NOT FOUND"

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.get_projects_feedback_questions
@frappe.whitelist()
def get_projects_feedback_questions(workspace, project):
	questions = []
	default_questions = frappe.get_single("Feedback Default Questions")
	doc = frappe.get_doc("Clockify Projects", {"workspace": workspace, "project_name": project})
	if default_questions:
		for default_question in default_questions.consultant_feedback_default_questions:
			questions.append(default_question)
	if doc:
		for question in doc.consultant_feedback_questions:
			questions.append(question)

	return questions


#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.create_consultant_feedback
@frappe.whitelist()
def create_consultant_feedback(workspace, project, user, feedback_list=[]):
	feedback_list = json.loads(feedback_list)
	doc = frappe.new_doc("Consultant Feedback")
	doc.consultant = user
	doc.feedback_date = getdate()
	doc.workspace = workspace
	doc.project = project
	for feedback in feedback_list:
		doc.append("consultant_feedback_questions_and_answers", {
			"question": feedback["question"],
			"answer": feedback["answer"]
		})
	doc.flags.ignore_permissions = True
	doc.flags.ignore_links = True
	return doc.insert()


#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.get_user_workspace_projects
@frappe.whitelist()
def get_user_workspace_projects(workspace, user):
	now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	first_date = now - timedelta(days=now.weekday())
	result = []
	docs = frappe.get_all("Clockify Projects", filters={"workspace": workspace}, fields=["name"])
	if docs:
		for dos in docs:
			doc = frappe.get_doc("Clockify Projects", dos.name)
			is_member = 0
			if doc.erp_members:
				for erp_row in doc.erp_members:
					if str(user) == str(erp_row.clockify_user):
						is_member = 1
						break
			if doc.clockify_members:
				for clo_row in doc.clockify_members:
					if str(user) == str(clo_row.clockify_user):
						is_member = 1
						break
			if is_member:
				is_feedback_submitted = frappe.db.sql("""SELECT name FROM `tabConsultant Feedback` WHERE feedback_date >= '{0}' AND feedback_date <= '{1}' AND consultant = '{2}' AND project = '{3}'""".format(first_date, now, user, dos.name), as_dict=True)
				if is_feedback_submitted:
					doc.is_feedback_submitted = 1
				else:
					doc.is_feedback_submitted = 0
				result.append(doc)

	return result

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.get_project_tasks
@frappe.whitelist(allow_guest = True)
def get_project_tasks(project_id, assignee=None):
	result = []
	docs = frappe.get_all("Clockify Projects", filters={"name": project_id}, fields=["name"])
	if docs:
		doc = frappe.get_doc("Clockify Projects", project_id)
		if doc.erp_tasks:
			for row in doc.erp_tasks:
				is_valid = 0
				rowdata = {
					"task": row.get("task"),
					"task_name": row.get("task_name"),
					"status": row.get("status"),
					"assignees": row.get("assignees"),
					"estimated_hours": row.get("estimated_hours"),
					"total_hours_spent": row.get("total_hours_spent")
				}
				if assignee:
					if (assignee in row.get("assignees")) or ("Anyone" in row.get("assignees")):
						is_valid = 1
				else:
					is_valid = 1
				if is_valid:
					result.append(rowdata)

		if doc.clockify_tasks:
			for row in doc.clockify_tasks:
				is_valid = 0
				rowdata = {
					"task": row.get("task"),
					"task_name": row.get("task_name"),
					"status": row.get("status"),
					"assignees": row.get("assignees"),
					"estimated_hours": row.get("estimated_hours"),
					"total_hours_spent": row.get("total_hours_spent")
				}
				if assignee:
					assignee_id = frappe.db.get_value("Clockify User", assignee, "user_id")
					if (assignee_id in row.get("assignees")) or ("Anyone" in row.get("assignees")):
						is_valid = 1
				else:
					is_valid = 1
				if is_valid:
					result.append(rowdata)
	return result

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.get_project_totals
@frappe.whitelist()
def get_project_totals(project_name=None, additional_hours=0):
	cp_filters = {}
	if project_name:
		cp_filters = {"name": project_name}
	projects = frappe.get_all("Clockify Projects", filters=cp_filters, fields=["name"])
	if projects:
		for project in projects:
			project_doc = frappe.get_doc("Clockify Projects", project.name)

			#TOTAL COST
			total_cost = 0
			total_cost_to_pay = 0
			cost_per_user = {}
			if project_doc.project_members:
				for pmem in project_doc.project_members:
					if not pmem.clockify_user in cost_per_user:					
						cost_per_user[pmem.clockify_user] = pmem.hourly_rate

			#Task Hours
			task_per_project = {}
			if project_doc.tasks:
				for ptask in project_doc.tasks:
					if ptask.task_id and not ptask.task_id in task_per_project:
						task_per_project[ptask.task_id] = {
							"assignees": ptask.assignees,
							"total_hours_spent": 0,
						}

			#Timelogs counting
			timelogs = frappe.get_all("Clockify Timelog", filters={"project": project.name}, fields=["name", "total_seconds", "billable", "clockify_user", "clockify_task"])
			for timelog in timelogs:
				if timelog.clockify_user in cost_per_user:
					total_cost += (flt(timelog.total_seconds)/3600)*flt(cost_per_user[timelog.clockify_user])
					if timelog.billable:
						total_cost_to_pay += (flt(timelog.total_seconds)/3600)*flt(cost_per_user[timelog.clockify_user])
				if timelog.clockify_task and timelog.clockify_task in task_per_project:
					if (timelog.clockify_user in task_per_project[timelog.clockify_task]["assignees"]) or (task_per_project[timelog.clockify_task]["assignees"] in ['Anyone']):
						task_per_project[timelog.clockify_task]["total_hours_spent"] += flt(timelog.total_seconds)/3600

			#assign new
			if project_doc.tasks:
				for newtask in project_doc.tasks:
					if newtask.task_id:
						newtask.total_hours_spent = task_per_project[newtask.task_id]["total_hours_spent"]
			project_doc.total_cost = total_cost_to_pay
			project_doc.flags.ignore_permissions = True
			project_doc.save()


#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.create_project_from_lead_custom
@frappe.whitelist()
def create_project_from_lead_custom(organization):
	organization_name = frappe.db.get_value('Organizations', organization, 'organization_name')
	workspace_list = frappe.get_all('Clockify Workspace', filters={'organization': organization}, fields=['name', 'default_owner'])
	if workspace_list:
		new_doc = frappe.new_doc('Clockify Projects')
		new_doc.workspace = workspace_list[0].name
		new_doc.erp_project_name = str(organization_name)
		if workspace_list[0].default_owner:
			if frappe.get_all('Clockify User', filters={'name': workspace_list[0].default_owner}, fields=['name']):
				new_doc.append('erp_members', {
					'clockify_user': workspace_list[0].default_owner,
					'hourly_rate': frappe.db.get_value('Clockify User', workspace_list[0].default_owner, 'rate')
				})
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.insert()

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.patch_create_project_from_lead_custom
@frappe.whitelist()
def patch_create_project_from_lead_custom():
	lead_custom_list = frappe.get_all('Lead Custom', fields=['name', 'organization', 'request_type', 'talent_title', 'project_title'])
	if lead_custom_list:
		for row_lead_custom_list in lead_custom_list:
			organization = row_lead_custom_list.organization
			if organization:
				workspace_list = frappe.get_all('Clockify Workspace', filters={'organization': organization}, fields=['name', 'default_owner'])
				if workspace_list:
					organization_name = frappe.db.get_value('Organizations', organization, 'organization_name')
					if not frappe.get_all('Clockify Projects', filters={'workspace': workspace_list[0].name}, fields=['name']):
						create_project_from_lead_custom(organization=organization)

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.assign_user_to_erp_members
@frappe.whitelist()
def assign_user_to_erp_members(user, organization, rate=0):
	if frappe.get_all('Clockify User', filters={'name': user}, fields=['name']):
		projects = frappe.get_all('Clockify Projects', filters={'organization': organization}, fields=['name'])
		if projects:
			for row_projects in projects:
				if (rate and rate <= 0) or (not rate):
					rate = frappe.db.get_value('Clockify User', user, 'rate') if frappe.db.get_value('Clockify User', user, 'rate') else 0

				cur_doc = frappe.get_doc('Clockify Projects', row_projects.name)
				cur_doc.append('erp_members', {
					'clockify_user': user,
					'hourly_rate': rate,
					'full_name': frappe.db.get_value('Clockify User', user, 'full_name')
				})
				cur_doc.flags.ignore_permissions = True
				cur_doc.flags.ignore_links = True
				cur_doc.save()
		else:
			pass
			#frappe.throw('Project not found')	
	else:
		pass
		#frappe.throw('User not found')


#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.patch_assign_lead_candidate_to_erp_members
@frappe.whitelist()
def patch_assign_lead_candidate_to_erp_members():
	lead_candidates = frappe.get_all('Lead Candidate', fields=['*'])
	if lead_candidates:
		for row_lead_candidates in lead_candidates:
			organization = None
			organization_name = None
			email_primary = None

			if row_lead_candidates.generated_from_lead:
				organization = frappe.db.get_value('Lead Custom', row_lead_candidates.generated_from_lead, 'organization')
			if row_lead_candidates.it_consultant:
				email_primary = frappe.db.get_value('IT Consultant', row_lead_candidates.it_consultant, 'email_primary')
			
			if organization and email_primary:
				clockify_projects = frappe.get_all('Clockify Projects', filters={'organization': organization}, fields=['name'])
				if clockify_projects:
					assign_user_to_erp_members(user=email_primary, organization=organization)

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.create_project_from_organization
@frappe.whitelist()
def create_project_from_organization(organization):
	if frappe.get_all('Organizations', filters={'name': organization}):
		organization_name = frappe.db.get_value('Organizations', organization, 'organization_name')
		if not frappe.get_all('Clockify Projects', filters={'organization': organization, 'erp_project_name': organization_name}):
			new_doc = frappe.new_doc('Clockify Projects')
			new_doc.workspace = 'Youpal Group'
			new_doc.organization = organization
			new_doc.erp_project_name = organization_name
			new_doc.flags.ignore_permissions = True
			new_doc.flags.ignore_links = True
			new_doc.insert()

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.patch_create_project_from_organizations
@frappe.whitelist()
def patch_create_project_from_organizations():
	organizations = frappe.get_all('Organizations', fields=['name'])
	if organizations:
		for row_organizations in organizations:
			create_project_from_organization(organization=row_organizations.name)

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.patch_rename_clockify_projects
@frappe.whitelist()
def patch_rename_clockify_projects():
	pass

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.patch_archive_clockify_projects
@frappe.whitelist()
def patch_archive_clockify_projects():
	projs = frappe.get_all('Clockify Projects', fields=['name'])
	for row in projs:
		frappe.db.set_value('Clockify Projects', row.name, 'archive', 1)
		frappe.db.commit()

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.restore_deleted_projects
@frappe.whitelist()
def restore_deleted_projects():
	non_existing = []
	deleteds = frappe.get_all('Deleted Document', filters={'deleted_doctype': 'Clockify Projects'}, fields=['*'])
	for row_deleteds in deleteds:
		proj_name = row_deleteds.deleted_name
		proj_name = proj_name[:-6]
		if not frappe.get_all('Clockify Projects', filters={'erp_project_name': proj_name}, fields=['name']):
			new_doc = frappe.new_doc('Clockify Projects')
			new_doc.workspace = 'Youpal Group'
			new_doc.erp_project_name = proj_name
			new_doc.flags.ignore_permissions = True
			new_doc.flags.ignore_links = True
			new_doc.insert()

		sd_data = str(row_deleteds.data)
		sd_data = sd_data.replace("null", "None")
		d_data = eval(sd_data)
		doc = frappe.get_doc('Clockify Projects', proj_name)
		for row_em in d_data['erp_members']:
			doc.append('erp_members', {
				'clockify_user': row_em['clockify_user'],
				'hourly_rate': row_em['hourly_rate']
			})
		doc.flags.ignore_links = True
		doc.flags.ignore_permissions = True
		doc.save()

#erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects.patch_project_clockify_timelog
@frappe.whitelist()
def patch_project_clockify_timelog():
	timelogs = frappe.get_all('Clockify Timelog' , fields=['name', 'project'])
	for row in timelogs:
		#if row.workspace:
		#	new_workspace_name = row.workspace
		#	new_workspace_name = new_workspace_name[:-6]
		frappe.db.set_value('Clockify Timelog', row.name, 'workspace', 'Youpal Group', update_modified=False)
		frappe.db.commit()
