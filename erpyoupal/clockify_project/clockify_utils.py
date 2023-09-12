from frappe import _, throw
import frappe
from frappe.utils import flt

def timelogs_per_project(from_date,to_date):
	timelogs_dict = {}
	for pro in frappe.db.get_list("Clockify Projects", pluck='name'):
		timelogs_dict.update({pro:{}})

	time_logs = frappe.db.sql("""SELECT total_cost,total_hours,clockify_user,project,billable FROM `tabClockify Timelog` WHERE time_in >= %s AND time_out <= %s""",(from_date,to_date),as_dict=True)
	for time in time_logs:
		dict_project = "No Project"
		if time.project:
			dict_project = time.project
		if dict_project not in timelogs_dict:
			timelogs_dict[dict_project] = {}
		if time.clockify_user not in timelogs_dict[dict_project]:
			timelogs_dict[dict_project].update({time.clockify_user:{"billable":0,"not_billable":0,"total":0}})
		if time.billable == 1:
			timelogs_dict[dict_project][time.clockify_user]["billable"] += flt(time.total_hours,2)
		else:
			timelogs_dict[dict_project][time.clockify_user]["not_billable"] += flt(time.total_hours,2)
		timelogs_dict[dict_project][time.clockify_user]["total"] += flt(time.total_hours,2)

	return timelogs_dict

@frappe.whitelist(allow_guest=True)
def create_timelog(time_in,time_out,project):
	time_in = time_in.replace("T", " ")
	time_out = time_out.replace("T", " ")
	new_doc = frappe.new_doc('Clockify Timelog')
	new_doc.workspace_id = "629033c6cde16468282427a4"
	new_doc.clockify_user = "john.d@youpalgroup.com"
	new_doc.project = project
	new_doc.time_in = time_in
	new_doc.time_out = time_out
	new_doc.billable = 1
	new_doc.flags.ignore_permissions = True
	new_doc.save()

@frappe.whitelist(allow_guest=True)
def get_project():
	projects = frappe.db.sql("""SELECT * FROM `tabClockify Projects`""",as_dict=True)

	return projects

#erpyoupal.clockify_project.clockify_utils.rename_name_extension
@frappe.whitelist()
def rename_name_extension():
	workspaces = frappe.get_all("Clockify Workspace", filters={"name_extension": "ERP"}, fields=["name","workspace_name"])
	for workspace in workspaces:
		frappe.db.set_value("Clockify Workspace", workspace.name, "name_extension", "App")
		frappe.db.set_value("Clockify Workspace", workspace.name, "workspace_fullname", str(workspace.workspace_name)+" - App")
		frappe.db.set_value("Clockify Workspace", workspace.name, "erp_workspace_id", str(workspace.workspace_name)+" - App")

	projects = frappe.get_all("Clockify Projects", filters={"name_extension": "ERP"}, fields=["name","project_name"])
	for project in projects:
		frappe.db.set_value("Clockify Projects", project.name, "name_extension", "App")
		frappe.db.set_value("Clockify Projects", project.name, "project_fullname", str(project.project_name)+" - App")
		frappe.db.set_value("Clockify Projects", project.name, "erp_project_id", str(project.project_name)+" - App")

	tags = frappe.get_all("Clockify Tag", filters={"name_extension": "ERP"}, fields=["name","tag_name"])
	for tag in tags:
		frappe.db.set_value("Clockify Tag", tag.name, "name_extension", "App")
		frappe.db.set_value("Clockify Tag", tag.name, "tag_fullname", str(tag.tag_name)+" - App")
		frappe.db.set_value("Clockify Tag", tag.name, "erp_tag_id", str(tag.tag_name)+" - App")

	tasks = frappe.get_all("Clockify Task", filters={"name_extension": "ERP"}, fields=["name","task_name"])
	for task in tasks:
		frappe.db.set_value("Clockify Task", task.name, "name_extension", "App")
		frappe.db.set_value("Clockify Task", task.name, "task_fullname", str(task.task_name)+" - App")
		frappe.db.set_value("Clockify Task", task.name, "erp_task_id", str(task.task_name)+" - App")