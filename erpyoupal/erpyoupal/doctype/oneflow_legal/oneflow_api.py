from __future__ import unicode_literals
import frappe
from frappe import _
import json
import shutil
import os
import glob
import hashlib
import requests
from requests.structures import CaseInsensitiveDict
from frappe.utils import get_url

@frappe.whitelist()
def get_oneflow_token():
	#taimur@youpal.se
	result = "b3c6e2da471c1648ad6b089b5a953e5302a874f7"
	if str("app.youpal.se") in str(get_url()):
		#cid.z@youpalgroup.com
		#result = "0eec270d93e57340787ad215cfd706d69706daf8"
		#Relativesanityorinsanity@gmail.com
		result = "faf740398b6bb3d255a92539441cb1fa586b1367"
	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.get_contracts
@frappe.whitelist(allow_guest=True)
def get_contracts():
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = "https://api.oneflow.com/v1/contracts"
		headers = {
			'Accept': 'application/json',
			'content-type': 'application/json',
			'x-oneflow-api-token': authentication_token
		}
		response = requests.get(url, headers=headers)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.get_contract
@frappe.whitelist(allow_guest=True)
def get_contract(contract_id, user_email):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = f"https://api.oneflow.com/v1/contracts/{contract_id}"
		headers = {
			'Accept': 'application/json',
			'content-type': 'application/json',
			'x-oneflow-api-token': authentication_token,
			'x-oneflow-user-email': user_email
		}
		response = requests.get(url, headers=headers)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.delete_contract
@frappe.whitelist(allow_guest=True)
def delete_contract(contract_id, user_email):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = f"https://api.oneflow.com/v1/contracts/{contract_id}"
		headers = {
			'Accept': 'application/json',
			'content-type': 'application/json',
			'x-oneflow-api-token': authentication_token,
			'x-oneflow-user-email': user_email
		}
		response = requests.delete(url, headers=headers)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.create_contract_party
@frappe.whitelist(allow_guest=True)
def create_contract_party(contract_id, user_email, data):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = f"https://api.oneflow.com/v1/contracts/{contract_id}/parties"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"x-oneflow-api-token": authentication_token,
			"x-oneflow-user-email": user_email
		}
		data = json.dumps(data)
		response = requests.post(url, headers=headers, data=data)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.create_contrect_from_teplate
@frappe.whitelist(allow_guest=True)
def create_contrect_from_teplate(document_title, workspace_id, template_id, user_email, data_fields=None):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = "https://api.oneflow.com/v1/contracts/create"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"x-oneflow-api-token": str(authentication_token),
			"x-oneflow-user-email": str(user_email)
		}
		#"data_fields": [{"custom_id": "address", "value": "this is my address"}]
		data = '{"workspace_id": '+workspace_id+',"template_id": '+template_id+',"name": "'+document_title+'"}'
		if data_fields:
			#data_json = {"workspace_id": workspace_id,"template_id": template_id,"name": document_title, "data_fields": data_fields}
			data_fields_str = '['
			for row in data_fields:
				if data_fields_str != '[':
					data_fields_str += ','
				data_fields_str += '{"custom_id": "'+row.get("custom_id")+'","value": "'+row.get("value")+'"}'
			data_fields_str += ']'
			data = '{"workspace_id": '+workspace_id+',"template_id": '+template_id+',"name": "'+document_title+'","data_fields":'+data_fields_str+'}'
		response = requests.post(url, headers=headers, data=data)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.create_contract_access_link
@frappe.whitelist(allow_guest=True)
def create_contract_access_link(contract_id, participant_id, user_email):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = f"https://api.oneflow.com/v1/contracts/{contract_id}/participants/{participant_id}/access_link"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"x-oneflow-api-token": authentication_token,
		}
		response = requests.post(url, headers=headers)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.publish_contract
@frappe.whitelist(allow_guest=True)
def publish_contract(contract_id, user_email, data):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = f"https://api.oneflow.com/v1/contracts/{contract_id}/publish"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"x-oneflow-api-token": authentication_token,
			"x-oneflow-user-email": user_email
		}
		data = json.dumps(data)
		response = requests.post(url, headers=headers, data=data)
		result = response.json()
		response.close()
	else: 
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.get_templates
@frappe.whitelist(allow_guest=True)
def get_templates():
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = "https://api.oneflow.com/v1/templates"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"x-oneflow-api-token": authentication_token
		}
		response = requests.get(url, headers=headers)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.get_workspaces
@frappe.whitelist(allow_guest=True)
def get_workspaces():
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = "https://api.oneflow.com/v1/workspaces"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"x-oneflow-api-token": authentication_token
		}
		response = requests.get(url, headers=headers)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.populate_oneflow_templates
@frappe.whitelist(allow_guest=True)
def populate_oneflow_templates():
	templates = get_templates()
	if templates and templates.get("data"):
		for row in templates['data']:
			if row.get("id") and not frappe.get_all("OneFlow Template", filters={"template_id": row.get("id")}):
				new_doc = frappe.new_doc("OneFlow Template")
				new_doc.template_id = row.get("id")
				new_doc.template_title = row.get("name")
				if row.get("template_type"):
					new_doc.template_type = row["template_type"].get("name")
				new_doc.template_created_time = row.get("created_time")
				new_doc.template_updated_time = row.get("updated_time")
				new_doc.flags.ignore_permissions = True
				new_doc.insert()

#erpnext.crm.doctype.oneflow_legal.oneflow_api.populate_oneflow_workspaces
@frappe.whitelist(allow_guest=True)
def populate_oneflow_workspaces():
	templates = get_workspaces()
	if templates and templates.get("data"):
		for row in templates['data']:
			if row.get("id") and not frappe.get_all("OneFlow Workspace", filters={"workspace_id": row.get("id")}):
				new_doc = frappe.new_doc("OneFlow Workspace")
				new_doc.workspace_id = row.get("id")
				new_doc.workspace_name = row.get("name")
				new_doc.flags.ignore_permissions = True
				new_doc.insert()

#erpnext.crm.doctype.oneflow_legal.oneflow_api.get_contract_files
@frappe.whitelist(allow_guest=True)
def get_contract_files(contract_id="3392743"):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token:
		url = f"https://api.oneflow.com/v1/contracts/{contract_id}/files/1"
		headers = {
			"Accept": "application/json",
			"Content-Type": "application/json",
			"x-oneflow-api-token": authentication_token
		}
		response = requests.get(url, headers=headers)
		result = response.json()
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.download_contract_file
@frappe.whitelist(allow_guest=True)
def download_contract_file(contract_id, document_name):
	result = "No response"
	authentication_token = get_oneflow_token()
	if authentication_token and not frappe.db.get_value("OneFlow Legal", document_name, 'contract_pdf'):
		url = f"https://api.oneflow.com/v1/contracts/{contract_id}/files/1?download=true"
		headers = {
			"x-oneflow-api-token": authentication_token
		}
		querystring = {"download":"true"}
		response = requests.request("GET", url, headers=headers, params=querystring)
		result = "Failed to download file"
		if response.content:
			file_name = f"contract_{contract_id}.pdf"
			file_path = frappe.utils.get_site_path("public", "files", file_name)
			content = response.content

			with open(file_path, 'wb') as f:
				f.write(response.content)
			
			new_file = frappe.new_doc('File')
			new_file.content = response.content
			new_file.file_url = "/files/"+file_name
			new_file.file_size = os.path.getsize(file_path)
			new_file.file_name = file_name
			#if content:
			#    new_content_hash = content.encode()
			#    new_content_hash = hashlib.md5(new_content_hash).hexdigest()
			#    new_file.content_hash = new_content_hash
			new_file.folder = "Home"
			new_file.is_private = 0
			new_file.attached_to_doctype = 'OneFlow Legal'
			new_file.attached_to_name = document_name
			new_file.attached_to_field = 'contract_pdf'
			new_file.flags.ignore_existing_file_check=True
			new_file.flags.ignore_permissions = True
			new_file.save()
			#frappe.db.set_value("OneFlow Legal", document_name, 'contract_pdf', "/files/"+str(file_name))
			result = "/files/"+str(file_name)
		response.close()
	else:
		result = "Insufficient Access"

	return result

#erpnext.crm.doctype.oneflow_legal.oneflow_api.webhook_update_oneflow_legals
@frappe.whitelist(allow_guest=True)
def webhook_update_oneflow_legals(*args, **kwargs):
	result = None
	saved_args = locals()
	response_data = saved_args['kwargs']
	new_doc = frappe.new_doc("Oneflow Webhook Log")
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	new_doc.data = str(response_data)
	result = new_doc.insert()
	frappe.enqueue("erpnext.crm.doctype.oneflow_legal.oneflow_legal.update_oneflow_legals", queue='long', timeout=300, now=False)
	return True

#erpnext.crm.doctype.oneflow_legal.oneflow_api.test_webhook
@frappe.whitelist(allow_guest=True)
def test_webhook(*args, **kwargs):
	result = None
	saved_args = locals()
	response_data = saved_args['kwargs']
	new_doc = frappe.new_doc("Oneflow Webhook Log")
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	new_doc.data = str(response_data)
	result = new_doc.insert()
	frappe.enqueue("erpnext.crm.doctype.oneflow_legal.oneflow_legal.update_oneflow_legals", queue='long', timeout=300, now=False)
	return True
