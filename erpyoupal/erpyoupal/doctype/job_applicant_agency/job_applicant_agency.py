# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now

class JobApplicantAgency(Document):
	def before_insert(self):
		self.to_parse_cvs = 1
		self.create_it_consultants = 1

	def after_insert(self):
		frappe.db.commit()
		frappe.enqueue("erpyoupal.erpyoupal.doctype.job_applicant_agency.job_applicant_agency.get_parsedjson_files", document_name=self.name, new_document=1, queue='long', timeout=300, now=False)
		frappe.enqueue("erpyoupal.erpyoupal.doctype.job_applicant_agency.job_applicant_agency.create_it_consultants_from_parsed_file", document_name=self.name, queue='long', timeout=300, now=False)

	def validate(self):
		if not self.is_new():
			if self.to_parse_cvs and not frappe.db.get_value("Job Applicant Agency", self.name, "to_parse_cvs"):
				frappe.enqueue("erpyoupal.erpyoupal.doctype.job_applicant_agency.job_applicant_agency.get_parsedjson_files", document_name=self.name, queue='long', timeout=300, now=False)
			if self.create_it_consultants and not frappe.db.get_value("Job Applicant Agency", self.name, "create_it_consultants"):
				frappe.enqueue("erpyoupal.erpyoupal.doctype.job_applicant_agency.job_applicant_agency.create_it_consultants_from_parsed_file", document_name=self.name, queue='long', timeout=300, now=False)

#erpyoupal.erpyoupal.doctype.job_applicant_agency.job_applicant_agency.get_parsedjson_files
@frappe.whitelist()
def get_parsedjson_files(document_name, new_document=0):
	if frappe.get_all("Job Applicant Agency", filters={"name": document_name}):
		this_doc = frappe.get_doc("Job Applicant Agency", document_name)
		if this_doc.attach_cvs and this_doc.to_parse_cvs:
			from erpyoupal.events.hr.job_applicant.job_applicant_api import get_parsed_file
			for cvs in this_doc.attach_cvs:
				continue_parse = 0
				if not cvs.last_date_parsed:
					continue_parse = 1
				if cvs.to_parse_cv:
					continue_parse = 1
				if this_doc.to_parse_cvs:
					continue_parse = 1
				if continue_parse:
					file_list_filters = {
						"attached_to_docType": "Job Applicant Agency",
						"file_url": cvs.cv
					}
					parse_file, date_parsed, confidence_level, parsed_file = get_parsed_file(
						is_new=new_document, 
						file_url=cvs.cv, 
						attached_to_name=None,
						attached_to_field=None, 
						attached_to_docType="Job Applicant Agency",
						file_list_filters=file_list_filters
					)
					frappe.db.sql(""" UPDATE `tabCV List Table` SET `to_parse_cv`=%s,`last_date_parsed`=%s,`confidence_level`=%s,`parsed_json`=%s 
						WHERE `parent`=%s AND `parenttype`='Job Applicant Agency' """,(parse_file, date_parsed, confidence_level, parsed_file, document_name))
		frappe.db.set_value("Job Applicant Agency", this_doc.name, 'to_parse_cvs', 0)	
		frappe.db.commit()

#erpyoupal.erpyoupal.doctype.job_applicant_agency.job_applicant_agency.create_it_consultants_from_parsed_file
@frappe.whitelist()
def create_it_consultants_from_parsed_file(document_name):
	if frappe.get_all("Job Applicant Agency", filters={"name": document_name}):
		this_doc = frappe.get_doc("Job Applicant Agency", document_name)
		if this_doc.attach_cvs:
			from erpyoupal.events.hr.job_applicant import validate_skills, create_new_it_consultant_document
			for cvs in this_doc.attach_cvs:
				if cvs.parsed_json and not cvs.it_consultant:
					new_it_consultant_entry = {
						"first_name": None,
						"last_name": None,
						"mobile_primary": None,
						"email_primary": None,
						"total_experience": None,
						"rate_hourly": None,
						"verification": "Applicant",
						"resume": cvs.cv,
						"skills": [],
					}
					parsed_json_obj = json.loads(cvs.parsed_json)
					new_it_consultant_entry["first_name"] = parsed_json_obj.get('name')
					new_it_consultant_entry["email_primary"] = parsed_json_obj.get('email')
					new_it_consultant_entry["total_experience"] = parsed_json_obj.get('total_experience')
					new_it_consultant_entry["skills"] = parsed_json_obj.get('skills')
					try:
						if new_it_consultant_entry["skills"]:
							validate_skills(new_it_consultant_entry["skills"])
						new_it_consultant_doc = create_new_it_consultant_document(new_it_consultant_entry)
						if new_it_consultant_doc:
							frappe.db.sql(""" UPDATE `tabCV List Table` SET `it_consultant`=%s, `create_it_consultant`=0 WHERE `parent`=%s AND `parenttype`='Job Applicant Agency' """,(new_it_consultant_doc, document_name))
					except:
						pass
			frappe.db.set_value("Job Applicant Agency", this_doc.name, 'create_it_consultants', 0)