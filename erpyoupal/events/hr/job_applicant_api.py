from __future__ import unicode_literals
from typing import final

import frappe
from frappe import _

import requests
import json
import copy
from requests.structures import CaseInsensitiveDict
from frappe.utils import now

def parse_resume(attachment_path, is_private_attachment=0):
	request_result = None
	url = "https://cvapi.youpal.es/parse"
	headers = CaseInsensitiveDict()
	headers["X-Api-Key"] = "3a0490fbcfa2c4d5215d54abe54034a6543bd315f8566d4e71c0b54f0cf7f8ba"
	if True: #attachment_path.lower().endswith(('.pdf')):
		local_filename = attachment_path.split('/')[-1]
		if is_private_attachment:
			local_filename = frappe.utils.get_site_path("private", "files", local_filename)
		else:
			local_filename = frappe.utils.get_site_path("public", "files", local_filename)
		with open(local_filename, 'rb') as opened_file:
			files = {"file": opened_file}
			try:
				requests_api = requests.post(url, headers=headers, files=files)
				json_response = requests_api.json()
				request_result = json.dumps(json_response)
				requests_api.close()
			except Exception as e:
				request_result = {'message': str(e)}
				request_result = json.dumps(request_result)
	else:
		request_result = {'message': 'Only PDF Files are supported.'}
		request_result = json.dumps(request_result) 

	return request_result

#erpyoupal.events.hr.job_applicant_api.run_all_job_applicant_parse_resume
@frappe.whitelist()
def run_all_job_applicant_parse_resume():
	job_applicant_lists = frappe.get_all("Job Applicant", fields=['name'])
	for ja in job_applicant_lists:
		ja_doc = frappe.get_doc("Job Applicant", ja.name)
		if not ja_doc.last_date_parsed and ja_doc.resume_attachment:
			ja_doc.to_parse_resume = 1
			ja_doc.flags.ignore_permissions = True
			try:
				ja_doc.save()
			except:
				pass

#erpyoupal.events.hr.job_applicant_api.run_all_job_applicant_agency_parse_cvs
@frappe.whitelist()
def run_all_job_applicant_agency_parse_cvs():
	job_applicant_agencies = frappe.get_all("Job Applicant Agency", fields=['name'])
	for ja in job_applicant_agencies:
		ja_doc = frappe.get_doc("Job Applicant Agency", ja.name)
		if ja_doc.attach_cvs:
			with_parsing = 0
			for cvs in ja_doc.attach_cvs:
				if not cvs.last_date_parsed:
					cvs.to_parse_cv = 1
					with_parsing = 1

			if with_parsing:
				ja_doc.flags.ignore_permissions = True
				try:
					ja_doc.save()
				except:
					pass

#erpyoupal.events.hr.job_applicant_api.get_job_applicant_agency
@frappe.whitelist()
def get_job_applicant_agency(doctype="Job Applicant Agency", fields=["name"], filters={}, order_by=None, limit_page_length=20, limit_start=0):
	get_all_query_feilds = []
	table_fields = []
	data = []

	#validate args
	if type(fields) in [str]:
		fields = eval(fields)
	if type(fields) in [str]:
		filters = eval(filters)
	
	#validate fields
	meta = frappe.get_meta(doctype)
	for field in fields:
		if meta.get_field(field):
			if meta.get_field(field).get("fieldtype") in ["Table"]:
				table_fields.append(field)
	
	final_fields = fields
	get_all_query_feilds = list(fields)
	if "name" not in get_all_query_feilds: 
		get_all_query_feilds.append("name")
	if table_fields:
		get_all_query_feilds = filter(lambda v: v not in table_fields, fields)

	#get data
	if get_all_query_feilds:
		agency_list = frappe.get_list(doctype, fields=get_all_query_feilds, filters=filters, order_by=order_by, limit_page_length=limit_page_length, limit_start=limit_start)
		if agency_list:
			for agency in agency_list:
				row = {}
				agency_doc = frappe.get_doc(doctype, agency.name)
				if "*" in final_fields:
					row = agency_doc
				else:
					for field in final_fields:
						row[field] = agency_doc.get(field)
				if row:
					data.append(row)
		result = {"data": data}

	return data

#erpyoupal.events.hr.job_applicant_api.get_parsed_file
@frappe.whitelist()
def get_parsed_file(is_new, file_url, attached_to_name, attached_to_field, attached_to_docType, file_list_filters=None):
	parse_file = None
	date_parsed = None
	confidence_level = None
	parsed_file = None

	file_list = None
	if not file_list_filters:
		if is_new:
			file_list_filters={
				"attached_to_field": attached_to_field,
				"attached_to_docType": attached_to_docType,
				"file_url": file_url,
			}
		else:
			file_list_filters={
				"attached_to_name": attached_to_name,
				"attached_to_field": attached_to_field,
				"attached_to_docType": attached_to_docType,
				"file_url": file_url,
			}
	
	file_list = frappe.get_all("File", filters=file_list_filters, fields=['name', 'is_private'])
	if file_list:
		doc_file = file_list[0]
		file_path = file_url
		parsed_file = parse_resume(file_path, is_private_attachment=doc_file.is_private)
		if parsed_file:
			parsed_json_obj = json.loads(parsed_file)
			confidence_level = parsed_json_obj.get("confidence")

	date_parsed = now()
	parse_file = 0

	return parse_file, date_parsed, confidence_level, parsed_file
