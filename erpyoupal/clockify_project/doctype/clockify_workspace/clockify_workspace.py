# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, time_diff_in_hours, get_datetime, get_time, now
from erpyoupal.clockify_project.doctype.clockify_timelog.clockify_timelog import validate_timelog_restriction

class ClockifyWorkspace(Document):
	def autoname(self):
		self.get_final_workspacename()

	def validate(self):
		self.get_final_workspacename()

	def get_final_workspacename(self):
		workspacename = None
		name_ext = "App"			
		if self.erp_workspace_name:
			workspacename = self.erp_workspace_name
		if self.clockify_workspace_id:
			name_ext = "Clockify"
		if self.clockify_workspace_name:
			workspacename = self.clockify_workspace_name

		if not workspacename:
			frappe.throw(_("App/Clockify Workspace Name is required"))

		self.workspace_name = workspacename
		self.name_extension = name_ext
		self.workspace_fullname = workspacename #+" - "+name_ext
		self.erp_workspace_id = self.name


#erpyoupal.clockify_project.doctype.clockify_workspace.clockify_workspace.get_clockify_workspace
@frappe.whitelist()
def get_clockify_workspace(filters={}):
	result = []
	docs = frappe.get_all("Clockify Workspace", filters=filters, fields=["name"])
	if docs:
		for dos in docs:
			doc = frappe.get_doc("Clockify Workspace", dos.name)
			result.append(doc)

	return result

#erpyoupal.clockify_project.doctype.clockify_workspace.clockify_workspace.get_user_clockify_workspace
@frappe.whitelist()
def get_user_clockify_workspace(user):
	result = []
	docs = frappe.get_all("Clockify Workspace", fields=["name"])
	if docs:
		for dos in docs:
			is_member = 0
			doc = frappe.get_doc("Clockify Workspace", dos.name)
			if doc.erp_members and str(user) in doc.erp_members:
				is_member = 1
			if doc.clockify_members:
				user_doc = frappe.get_doc("Clockify User", user)
				if str(user_doc.user_id) in doc.clockify_members:
					is_member = 1
			doc.user_can_add_time = 0
			validate_timelog_restriction_result = validate_timelog_restriction(workspace_id=dos.name, time_in=now(), time_out=now())
			if str(validate_timelog_restriction_result) == "Timelog not restricted":
				doc.user_can_add_time = 1
			
			if is_member:
				result.append(doc)

	return result

#erpyoupal.clockify_project.doctype.clockify_workspace.clockify_workspace.add_workspace
@frappe.whitelist()
def add_workspace(data={}):
	pass

#erpyoupal.clockify_project.doctype.clockify_workspace.clockify_workspace.delete_workspace
@frappe.whitelist()
def delete_workspace(workspace):
	if frappe.get_all("Clockify Workspace", filters={"name": workspace}, fields=["name"]):
		doc = frappe.get_doc("Clockify Workspace", workspace)
		doc.flags.ignore_permissions = True
		return doc.delete()
	else:
		return "Workspace not found"


#erpyoupal.clockify_project.doctype.clockify_workspace.clockify_workspace.create_clockify_workspace_from_organizations
@frappe.whitelist()
def create_clockify_workspace_from_organizations(organization, organization_name):
	is_primary_contact_person = None
	organization_members = []
	people_list = frappe.get_all('People', filters={'organization_name': organization}, fields=['name', 'is_primary_contact_person', 'email_address'])
	if people_list:
		for row_people_list in people_list:
			if row_people_list.email_address:
				if not row_people_list.email_address in organization_members:
					organization_members.append(row_people_list.email_address)
				if row_people_list.is_primary_contact_person:
					is_primary_contact_person = row_people_list.email_address
	
	organization_members_final = None
	if organization_members:
		organization_members_final = ', '.join(organization_members)		

	new_doc = frappe.new_doc("Clockify Workspace")
	new_doc.organization = organization
	new_doc.default_owner = is_primary_contact_person
	new_doc.erp_workspace_name = organization_name
	new_doc.erp_members = organization_members_final
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	new_doc.insert()

#erpyoupal.clockify_project.doctype.clockify_workspace.clockify_workspace.patch_create_clockify_workspace_from_organizations
@frappe.whitelist()
def patch_create_clockify_workspace_from_organizations():
	organizations_list = frappe.get_all('Organizations', fields=['name', 'organization_name'])
	if organizations_list:
		for row_organizations_list in organizations_list:
			if not frappe.get_all('Clockify Workspace', filters={'erp_workspace_name': row_organizations_list.organization_name}, fields=['name']):
				if frappe.get_all('Organizations', filters={'name': row_organizations_list.name}, fields=['name']):
					create_clockify_workspace_from_organizations(organization=row_organizations_list.name, organization_name=row_organizations_list.organization_name)