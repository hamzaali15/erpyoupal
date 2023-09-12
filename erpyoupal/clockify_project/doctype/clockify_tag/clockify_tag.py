# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_datetime, get_time, nowtime, today, flt
from frappe.model.document import Document
from erpyoupal.clockify_project.clockify_api import add_new_tag

class ClockifyTag(Document):
	def autoname(self):
		self.get_tag_name()

	def get_tag_name(self):
		tagname = None
		name_ext = "App"			
		if self.erp_tag_name:
			tagname = self.erp_tag_name
		if self.clockify_tag_id:
			name_ext = "Clockify"
		if self.clockify_tag_name:
			tagname = self.clockify_tag_name

		if not tagname:
			frappe.throw(_("App/Clockify Project Name is required"))

		self.tag_name = tagname
		self.name_extension = name_ext
		self.tag_fullname = tagname+" - "+name_ext
		self.erp_tag_id = self.tag_fullname

	def validate(self):
		if self.is_new() and not self.get("created_from_clockify"):
			add_new_tag_result = add_new_tag(email=frappe.session.user, workspace_id=self.workspace, data={"name", self.tag_name})
			if add_new_tag_result:
				if "id" in add_new_tag_result:
					self.clockify_id = add_new_tag_result.get("id")
					frappe.msgprint("Clockify Tag added")
				else:
					pass
					#frappe.msgprint(str(add_new_tag_result))

#erpyoupal.clockify_project.doctype.clockify_tag.clockify_tag.get_workspace_tags
@frappe.whitelist()
def get_workspace_tags(workspace):
	result = []
	workspaces = frappe.get_all("Clockify Workspace", filters={"name": workspace}, fields=["name"])
	if workspaces:
		for workspace in workspaces:
			doc = frappe.get_doc("Clockify Workspace", workspace.name)
			if doc.erp_tags:
				for erp_tag in doc.erp_tags:
					tag_doc = frappe.get_doc("Clockify Tag", erp_tag.tag_name)
					result.append(tag_doc)
	return result