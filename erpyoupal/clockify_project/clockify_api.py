from __future__ import unicode_literals
from hashlib import new
import frappe
from frappe import _
from frappe.utils import get_datetime, get_time, nowtime, today, flt
import json
import shutil
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime

#https://clockify.me/developers-api

def get_user_access(email):
	result = None
	users = frappe.get_all("Clockify User", filters={'email': email}, fields=['name'])
	if users:
		user = frappe.get_doc("Clockify User", users[0].name)
		result = user.api_key
	return result

def get_admin_user_access():
	admin_user = frappe.db.get_single_value('Clockify Settings', 'admin_user')
	if not admin_user:
		frappe.throw("No Admin Use found")
	admin_user_id = frappe.db.get_single_value('Clockify Settings', 'admin_user_id')
	if not admin_user_id:
		frappe.throw("No Admin User ID found")
	api_key = frappe.db.get_single_value('Clockify Settings', 'api_key')
	if not api_key:
		frappe.throw("No Admin API Key found")
	return api_key

#erpyoupal.clockify_project.clockify_api.get_workspaces
@frappe.whitelist()
def get_workspaces(email=None):
	#GET /workspaces
	result = "No response"
	http_request = None
	user_api_key = None
	if email:
		user_api_key = get_user_access(email)
	else:
		user_api_key = get_admin_user_access()
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		http_request = requests.get(url, headers=headers)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result

#erpyoupal.clockify_project.clockify_api.pull_workspaces
@frappe.whitelist()
def pull_workspaces(email=None):
	get_workspaces_result = get_workspaces(email=None)
	if get_workspaces_result and type(get_workspaces_result) in [list]:
		for row in get_workspaces_result:
			#Init data
			workspace_data = {
				#"workspace_name": None,
				#"erp_workspace_id": None,
				#"erp_workspace_name": None,
				#"erp_tags": None,
				#"erp_members": None,
				"clockify_workspace_id": None,
				"clockify_workspace_name": None,
				#"clockify_tags": None,
				"clockify_members": None,
				"pulled_from_clockify": None,
				#"sync_with_clockify": None,
				#"enable_weekly_restriction": None,
				#"defined_restrictions": None
			}

			#validate, insert data
			if row.get("id"):
				workspace_data["clockify_workspace_id"] = row.get("id")
				workspace_data["pulled_from_clockify"] = 1
			if row.get("name"):
				workspace_data["clockify_workspace_name"] = row.get("name")

			clockify_members = []
			if row.get("memberships"):
				for mem in row.get("memberships"):
					clockify_members.append(mem.get("userId"))
			if clockify_members:
				workspace_data["clockify_members"] = ', '.join(clockify_members)

			is_existing = frappe.get_all("Clockify Workspace", filters={"clockify_workspace_id": row.get("id")}, fields=["name"])
			if is_existing:
				cur_doc = frappe.get_doc("Clockify Workspace", is_existing[0].name)
				cur_doc.update(workspace_data)
				cur_doc.flags.ignore_permissions = True
				cur_doc.save()
			else:
				new_doc = frappe.new_doc("Clockify Workspace")
				new_doc.update(workspace_data)		
				new_doc.flags.ignore_permissions = True
				new_doc.insert()

def get_projects(email, workspace_id, params={}):
	#GET /workspaces/{workspaceId}/projects
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		http_request = requests.get(url, headers=headers, params=params)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result

@frappe.whitelist()
def pull_projects(email, workspace_id):
	get_projects_result = get_projects(email, workspace_id)
	if get_projects_result and type(get_projects_result) in [list]:
		for row in get_projects_result:
			workspace_list = frappe.get_all("Clockify Workspace", filters={"clockify_workspace_id": row.get('workspaceId')}, fields=["name"])
			if workspace_list:
				doc_data = {
					"workspace": workspace_list[0].name,
					#"project_fullname": None,
					#"project_name": None,
					#"name_extension": None,
					#"erp_project_id": None,
					#"erp_project_name": None,
					#"archive": None,
					"clockify_project_id": row.get('id'),
					"clockify_project_name": row.get('name'),
					"pulled_from_clockify": 1,
					#"sync_with_clockify": None,
					"visibility": 'Public' if row.get('public') else 'Private',
					"color": row.get('color'),
					"note": row.get('note'),
					"billable": row.get('billable'),
					#"project_billable_rate": None,
					#"total_cost": None,
					#"project_estimate": None,
					#"client": None,
					#"erp_tasks": None,
					#"erp_members": None,
					"clockify_tasks": [],
					"clockify_members": []
				}			

				if row.get('memberships'):
					for membership in row.get('memberships'):
						user_email = frappe.get_all("Clockify User", filters={'user_id': membership.get('userId')}, fields=['name'])
						if user_email:
							hourly_rate = 0
							if membership.get('hourlyRate') and membership['hourlyRate'].get('amount'):
								hourly_rate = flt(membership['hourlyRate'].get('amount')) * .01
							currency = None
							if membership.get('hourlyRate') and membership['hourlyRate'].get('currency'):
								currency = membership['hourlyRate'].get('currency')

							doc_data['clockify_members'].append({
								'clockify_user': str(user_email[0].name),
								'membership_type': membership.get('membershipType'),
								'membership_status': membership.get('membershipStatus'),
								'hourly_rate': hourly_rate,
								'currency': currency
							})

				get_project_tasks_result = get_project_tasks(email=email, workspace_id=workspace_id, project_id=row.get('id'))
				if get_project_tasks_result and type(get_project_tasks_result) in [list]:
					for gptr in get_project_tasks_result:
						clockify_assignees = ', '.join(eval(str(gptr.get("assigneeIds")))) if gptr.get("assigneeIds") else "Anyone"
						gptr_data = {
							#"task_name": None,
							#"task_fullname": None,
							#"name_extension": None,
							#"workspace": doc_data["workspace"],
							#"project": None,
							#"erp_task_id": None,
							#"erp_task_name": None,
							"clockify_task_id": gptr.get("id"),
							"clockify_task_name": gptr.get("name"),
							"clockify_status": gptr.get("status"),
							"clockify_workspace_id": doc_data["workspace"],
							"clockify_project_id": row.get('id'),
							"clockify_assignees": clockify_assignees
						}

						validate_clockify_tasks_result = validate_clockify_tasks(task_id=gptr.get("id"), data=dict(gptr_data), created_from_clockify=1)
						if validate_clockify_tasks_result:
							doc_data['clockify_tasks'].append({
								"task": validate_clockify_tasks_result,
								"task_name": gptr.get("name"),
								"status": gptr.get("status"),
								"assignees": clockify_assignees,
								"estimated_hours": 0,
								"total_hours_spent": 0
							})

				projects = frappe.get_all("Clockify Projects", filters={'clockify_project_id': row.get('id')}, fields=['name'])
				if not projects:
					new_doc = frappe.new_doc("Clockify Projects")
					new_doc.update(doc_data)
					new_doc.flags.ignore_permissions = True
					new_doc.insert()
				else:
					cur_doc = frappe.get_doc("Clockify Projects", projects[0].name)
					cur_doc.update(doc_data)
					cur_doc.flags.ignore_permissions = True
					cur_doc.save()


def validate_clockify_tasks(task_id, data,  created_from_clockify=0):
	existing_doc = frappe.get_all("Clockify Task", filters={"clockify_task_id": task_id}, fields=['name'])
	if existing_doc:
		cur_doc = frappe.get_doc("Clockify Task", existing_doc[0].name)
		cur_doc.update(data)
		cur_doc.flags.ignore_permissions = True
		cur_doc.save()
		return cur_doc.name
	else:
		new_doc = frappe.new_doc("Clockify Task")
		new_doc.created_from_clockify = created_from_clockify
		new_doc.update(data)
		new_doc.flags.ignore_permissions = True
		new_doc.insert()
		return new_doc.name

def get_user_timelogs(email, workspace_id, user_id, params={}):
	#GET /workspaces/{workspaceId}/user/{userId}/time-entries
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{user_id}/time-entries"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		http_request = requests.get(url, headers=headers, params=params)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result


@frappe.whitelist()
def pull_workspace_timelogs(workspace_id):
	users = frappe.get_all("Clockify User", filters={'workspace_id': workspace_id}, fields=['*'])
	if users:
		for user in users:
			get_user_timelogs_result = get_user_timelogs(user.email, workspace_id, user.user_id)
			if get_user_timelogs_result and type(get_user_timelogs_result) in [list]:
				for row in get_user_timelogs_result:
					from_time = format_iso_datetime_to_normal(row['timeInterval'].get('start'))
					to_time = format_iso_datetime_to_normal(row['timeInterval'].get('end'))
					hours = (to_time - from_time).seconds/3600

					doc_data = {
						"workspace_id": row.get('workspaceId'),
						"clockify_user": frappe.db.get_value('Clockify User', {'user_id': row.get('userId')}, 'name'),
						"project": frappe.db.get_value('Clockify Projects', {'project_id': row.get('projectId')}, 'name'),
						"time_in": from_time, #row['timeInterval'].get('start')
						"time_out": to_time, #row['timeInterval'].get('end')
						"hours": hours, #row['timeInterval'].get('duration')
						"billable": row.get('billable'),
						"description": row.get('description'),
						"sync_to_clockify": True,
						"pulled_from_clockify": True
					}

					existing_timelog = frappe.get_all("Clockify Timelog", filters={'timelog_id': row.get('id')}, fields=['name'])
					if not existing_timelog:
						new_doc = frappe.new_doc("Clockify Timelog")
						new_doc.timelog_id = row.get('id')
						new_doc.update(doc_data)
						new_doc.flags.ignore_permissions = True
						new_doc.insert()
					else:
						cur_doc = frappe.get_doc("Clockify Timelog", existing_timelog[0].name)
						cur_doc.update(doc_data)
						cur_doc.flags.ignore_permissions = True
						cur_doc.save()


def get_workspace_users(email, workspace_id, params={}):
	#GET /workspaces/{workspaceId}/users
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/users"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		http_request = requests.get(url, headers=headers, params=params)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result


@frappe.whitelist()
def pull_workspace_users(workspace_id):
	workspaces = frappe.get_all("Clockify Workspace", filters={'workspace_id': workspace_id}, fields=['name', 'owner_user'])
	if workspaces and workspaces[0].owner_user:
		get_workspace_users_result = get_workspace_users(workspaces[0].owner_user, workspace_id, params={})
		if get_workspace_users_result and type(get_workspace_users_result) in [list]:
			for row in get_workspace_users_result:
				existing_users = frappe.get_all("Clockify User", filters={'user_id': row.get('id')}, fields=['name'])
				if not existing_users:
					existing_users = frappe.get_all("Clockify User", filters={'name': row.get('email')}, fields=['name'])
				if not existing_users:
					new_doc = frappe.new_doc("Clockify User")
					new_doc.first_name = None
					new_doc.last_name = None
					new_doc.full_name = row.get('name')
					new_doc.status = row.get('status')
					new_doc.rate = None
					new_doc.workspace_id = workspace_id
					new_doc.user_id = row.get('id')
					new_doc.email = row.get('email')
					new_doc.password = None
					new_doc.api_key = None
					new_doc.flags.ignore_permissions = True
					new_doc.insert()


#erpyoupal.clockify_project.clockify_api.add_new_tag
@frappe.whitelist()
def add_new_tag(email, workspace_id, data):
	#POST /workspaces/{workspaceId}/time-entries
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/tags"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		headers["content-type"] = 'application/json'
		if type(data) in [dict]:
			data = json.dumps(data)
		http_request = requests.post(url, headers=headers, data=data)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result


#erpyoupal.clockify_project.clockify_api.validate_clockify_tags
@frappe.whitelist()
def validate_clockify_tags(tag_name, clockify_id=None, workspace_id=None, created_from_clockify=0):
	existing_tag = frappe.get_all("Clockify Tag", filters={"tag_name": tag_name}, fields=['name', 'tag_name', 'clockify_id', 'workspace_id'])
	if existing_tag:
		with_diff = 0
		if workspace_id != existing_tag[0].workspace_id:
			with_diff = 1
		if clockify_id != existing_tag[0].clockify_id:
			with_diff = 1
		if with_diff:
			cur_doc = frappe.get_doc("Clockify Tag", existing_tag[0].name)
			cur_doc.created_from_clockify = created_from_clockify
			cur_doc.clockify_id = clockify_id
			cur_doc.workspace_id = workspace_id
			cur_doc.flags.ignore_permissions = True
			cur_doc.save()
	else:
		new_tag = frappe.new_doc("Clockify Tag")
		new_tag.tag_name = tag_name
		new_tag.created_from_clockify = created_from_clockify
		new_tag.clockify_id = clockify_id
		new_tag.workspace_id = workspace_id
		new_tag.flags.ignore_permissions = True
		new_tag.insert()


#erpyoupal.clockify_project.clockify_api.add_timelog_to_clockify
@frappe.whitelist()
def add_timelog_to_clockify(email, workspace_id, data):
	#POST /workspaces/{workspaceId}/time-entries
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/time-entries"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		headers["content-type"] = 'application/json'
		if type(data) in [dict]:
			data = json.dumps(data)
		http_request = requests.post(url, headers=headers, data=data)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result

#erpyoupal.clockify_project.clockify_api.update_timelog_to_clockify
@frappe.whitelist()
def update_timelog_to_clockify(email, workspace_id, timelog_id, data):
	#PUT /workspaces/{workspaceId}/time-entries/{id}
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/time-entries/{timelog_id}"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		headers["content-type"] = 'application/json'
		if type(data) in [dict]:
			data = json.dumps(data)
		http_request = requests.put(url, headers=headers, data=data)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result


def get_project_tasks(email, workspace_id, project_id):
	#GET /workspaces/{workspaceId}/projects/{projectId}/tasks
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects/{project_id}/tasks"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		http_request = requests.get(url, headers=headers)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result


#erpyoupal.clockify_project.clockify_api.get_current_clockify_user
@frappe.whitelist()
def get_current_clockify_user():
	result = None
	user_email = frappe.db.get_value('User', frappe.session.user, 'email')
	clockify_user = frappe.get_all("Clockify User", filters={'name': user_email}, fields=['name'])
	if clockify_user:
		result = clockify_user[0].name

	return result


#erpyoupal.clockify_project.clockify_api.validate_clockify_user
@frappe.whitelist()
def validate_clockify_user(email):
	result = None
	clockify_user = frappe.get_all("Clockify User", filters={'name': email}, fields=['name'])
	if clockify_user:
		result = clockify_user[0].name

	return result

#erpyoupal.clockify_project.clockify_api.get_clockify_user_from_id
@frappe.whitelist()
def get_clockify_user_from_id(user_id):
	result = None
	clockify_user = frappe.get_all("Clockify User", filters={'user_id': user_id}, fields=['name'])
	if clockify_user:
		result = clockify_user[0].name

	return result


#erpyoupal.clockify_project.clockify_api.add_project_to_clockify
@frappe.whitelist()
def add_project_to_clockify(email, workspace_id, data):
	#POST /workspaces/{workspaceId}/projects
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		headers["content-type"] = 'application/json'
		if type(data) in [dict]:
			data = json.dumps(data)
		http_request = requests.post(url, headers=headers, data=data)
		result = http_request.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result

#erpyoupal.clockify_project.clockify_api.delete_clockify_timelog
@frappe.whitelist()
def delete_clockify_timelog(email, workspace_id, timelog_id):
	#DELETE /workspaces/{workspaceId}/time-entries/{id}
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/time-entries/{timelog_id}"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		headers["content-type"] = 'application/json'
		http_request = requests.delete(url, headers=headers)
		result = http_request
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result

#erpyoupal.clockify_project.clockify_api.update_clockify_project
@frappe.whitelist()
def update_clockify_project(email, workspace_id, project_id, data):
	#PUT /workspaces/{workspaceId}/projects/{projectId}
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects/{project_id}"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		headers["content-type"] = 'application/json'
		if type(data) in [dict]:
			data = json.dumps(data)
		json_response = requests.put(url, headers=headers, data=data)
		result = json_response.json()
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result

#erpyoupal.clockify_project.clockify_api.delete_clockify_project
@frappe.whitelist()
def delete_clockify_project(email, workspace_id, project_id):
	#DELETE /workspaces/{workspaceId}/projects/{id}
	result = "No response"
	http_request = None
	user_api_key = get_user_access(email)
	if user_api_key:
		url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/projects/{project_id}"
		headers = CaseInsensitiveDict()
		headers["X-Api-Key"] = user_api_key
		headers["content-type"] = 'application/json'
		json_response = requests.delete(url, headers=headers)
		result = json_response
	else:
		result = "Insufficient user access"

	if http_request:
		http_request.connection.close()

	return result

#erpyoupal.clockify_project.clockify_api.time_created_manually_from_clockify
@frappe.whitelist(allow_guest=True)
def time_created_manually_from_clockify(*args, **kwargs):
	saved_args = locals()
	row = saved_args['kwargs']
	if row:
		existing_timelog = frappe.get_all("Clockify Timelog", filters={'timelog_id': row.get('id')}, fields=['name'])
		if not existing_timelog:
			from_time = format_iso_datetime_to_normal(row['timeInterval'].get('start'))
			to_time = format_iso_datetime_to_normal(row['timeInterval'].get('end'))
			hours = (to_time - from_time).seconds/3600
			new_doc = frappe.new_doc("Clockify Timelog")
			new_doc.timelog_id = row.get('id')
			doc_data = {
				"workspace_id": row.get('workspaceId'),
				"clockify_user": frappe.db.get_value('Clockify User', {'user_id': row.get('userId')}, 'name'),
				"project": frappe.db.get_value('Clockify Projects', {'project_id': row.get('projectId')}, 'name'),
				"time_in": from_time,
				"time_out": to_time,
				"hours": hours,
				"billable": row.get('billable'),
				"description": row.get('description'),
				"sync_to_clockify": True,
				"pulled_from_clockify": True
			}
			if row.get('task'):
				if 'name' in row['task']:
					doc_data['task'] = row['task']['name']
				if 'id' in row['task']:
					doc_data['task_id'] = row['task']['id']
			if row.get('tags'):
				for tag in row['tags']:
					validate_clockify_tags(tag_name=tag['name'], clockify_id=tag['id'], workspace_id=tag['workspaceId'], created_from_clockify=1)
					new_doc.append('tags', {
							'tag_name': tag['name']
						})
			new_doc.update(doc_data)
			new_doc.flags.ignore_permissions = True
			new_doc.insert()

	return 'success', 200

def format_iso_datetime_to_normal(my_datetime):
	formatted_my_datetime = datetime.strptime(my_datetime, "%Y-%m-%dT%H:%M:%SZ")
	formatted_my_datetime = get_datetime(formatted_my_datetime)
	return formatted_my_datetime

def format_normal_to_iso_datetime(my_datetime):
	formatted_my_datetime = get_datetime(my_datetime)
	formatted_my_datetime = datetime.strftime(formatted_my_datetime, "%Y-%m-%dT%H:%M:%SZ")
	return formatted_my_datetime

