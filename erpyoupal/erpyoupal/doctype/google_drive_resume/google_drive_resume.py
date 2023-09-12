# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
import shutil
import os
import glob
import hashlib
import frappe
from frappe import _
from frappe.model.document import Document
import requests
from frappe.utils import now
from frappe.utils.background_jobs import enqueue

class GoogleDriveResume(Document):
	def before_insert(self):
		self.validate_duplicate_file_id()

	def validate(self):
		if self.is_new():
			self.download_file_from_google_drive()
		if not self.is_new() and self.parse_file and not frappe.db.get_value("Google Drive Resume", self.name, "parse_file"):
			frappe.enqueue("erpyoupal.erpyoupal.doctype.google_drive_resume.google_drive_resume.get_parsed_drive_file", document_name=self.name, queue='long', timeout=300, now=False)
			frappe.enqueue("erpyoupal.erpyoupal.doctype.google_drive_resume.google_drive_resume.create_new_job_applicant_document_from_parsed_file", document_name=self.name, queue='long', timeout=300, now=False)

	def after_insert(self):
		frappe.db.commit()
		frappe.enqueue("erpyoupal.erpyoupal.doctype.google_drive_resume.google_drive_resume.get_parsed_drive_file", document_name=self.name, queue='long', timeout=300, now=False)
		frappe.enqueue("erpyoupal.erpyoupal.doctype.google_drive_resume.google_drive_resume.create_new_job_applicant_document_from_parsed_file", document_name=self.name, queue='long', timeout=300, now=False)

	def get_google_drive_file_id(self):
		file_url = None
		if self.google_drive_file_url:
			sample_url = self.google_drive_file_url
			file_url = sample_url.split('/')[5]
		return file_url

	def download_file_from_google_drive(self):
		file_id = self.get_google_drive_file_id()
		if file_id:
			file_name = str(file_id)+".pdf"
			file_downloaded = save_new_file_document(file_id, file_name, document_name=self.name)
			self.db_set("google_drive_file", "/files/"+str(file_name))
			self.db_set("google_drive_file_id", str(file_id))
			if file_downloaded:
				self.db_set("file_download_status", "File Downloaded")
			else:
				self.db_set("file_download_status", "Error Downloading File")
				frappe.throw(_("Error Downloading File"))
	
	def validate_duplicate_file_id(self):
		file_id = self.get_google_drive_file_id()
		if file_id:
			if frappe.get_all("Google Drive Resume", filters={"google_drive_file_id": file_id, "name": ["!=", self.name]}):
				frappe.throw(_("Google Drive File already exists"))

#erpyoupal.erpyoupal.doctype.google_drive_resume.google_drive_resume.create_new_job_applicant_document_from_parsed_file
@frappe.whitelist()
def create_new_job_applicant_document_from_parsed_file(document_name):
	if frappe.get_all("Google Drive Resume", filters={"name": document_name}):
		this_doc = frappe.get_doc("Google Drive Resume", document_name)
		if this_doc.parsed_file and not this_doc.job_applicant:
			from erpyoupal.events.hr.job_applicant import validate_skills, create_new_job_applicant_document
			new_doc_entry = {
				"first_name": None,
				"last_name": None,
				"mobile_primary": 0,
				"email_primary": this_doc.email,
				"rate_hourly": None,
				"resume_attachment": this_doc.google_drive_file,
				"to_parse_resume": 0,
				"last_date_parsed": this_doc.date_parsed,
				"parsed_json": this_doc.parsed_file,
				"confidence_level": this_doc.confidence_level,
				"skills": [],
				"dont_parse": 1
			}
			parsed_json_obj = json.loads(this_doc.parsed_file)
			new_doc_entry["first_name"] = parsed_json_obj.get('name')
			new_doc_entry["total_experience"] = parsed_json_obj.get('total_experience')
			new_doc_entry["skills"] = parsed_json_obj.get('skills')
			try:
				if new_doc_entry["skills"]:
					validate_skills(new_doc_entry["skills"])
				new_job_applicant_doc = create_new_job_applicant_document(new_doc_entry)
				if new_job_applicant_doc:
					frappe.db.set_value("Google Drive Resume", this_doc.name, 'job_applicant', new_job_applicant_doc)
					frappe.enqueue("erpyoupal.events.hr.job_applicant.create_it_consultant_from_parsed_file", document_name=new_job_applicant_doc, queue='long', timeout=300, now=False)
			except:
				pass

#erpyoupal.erpyoupal.doctype.google_drive_resume.google_drive_resume.get_parsed_drive_file
@frappe.whitelist()
def get_parsed_drive_file(document_name):
	if frappe.get_all("Google Drive Resume", filters={"name": document_name}):
		this_doc = frappe.get_doc("Google Drive Resume", document_name)
		this_doc.parse_file = 1
		if this_doc.parse_file and this_doc.google_drive_file and this_doc.file_download_status in ["File Downloaded"]:
			from erpyoupal.events.hr.job_applicant.job_applicant_api import get_parsed_file
			parse_file, date_parsed, confidence_level, parsed_file = get_parsed_file(
				is_new=this_doc.is_new(), 
				file_url=this_doc.google_drive_file, 
				attached_to_name=this_doc.name,
				attached_to_field="google_drive_file", 
				attached_to_docType="Google Drive Resume",
				file_list_filters={
					"attached_to_field": "google_drive_file", 
					"attached_to_docType": "Google Drive Resume",
					"file_url": this_doc.google_drive_file,
				}
			)
			#frappe.db.set_value("Google Drive Resume", this_doc.name, 'confidence_level', confidence_level)
			#frappe.db.set_value("Google Drive Resume", this_doc.name, 'parsed_file', parsed_file)
			#frappe.db.set_value("Google Drive Resume", this_doc.name, 'date_parsed', date_parsed)
			#frappe.db.set_value("Google Drive Resume", this_doc.name, 'parse_file', parse_file)
			file_download_status = str(this_doc.file_download_status)
			if parsed_file in ['{"message": "Expecting value: line 1 column 1 (char 0)"}']:
				file_download_status = "File cannot be read"

			frappe.db.sql("""UPDATE `tabGoogle Drive Resume` SET `confidence_level`=%s,`parsed_file`=%s,`date_parsed`=%s,`parse_file`=%s,`file_download_status`=%s WHERE `name`=%s """,(
				confidence_level, parsed_file, date_parsed, parse_file, file_download_status, this_doc.name))
			frappe.db.commit()
			#create_new_job_applicant_document_from_parsed_file(this_doc.name)

def save_new_file_document(file_id, file_name, document_name):
	file_url = "https://docs.google.com/uc?export=download"
	params = { 'id' : file_id }
	file_path = frappe.utils.get_site_path("public", "files", file_name)
	file_downloaded = 0
	file_readable = 0

	with requests.get(file_url, params=params, stream=True) as r:
		file_downloaded = 1
		print('File Downloaded')
	
		with open(file_path, 'wb') as f:
			content = shutil.copyfileobj(r.raw, f)
			new_file = frappe.new_doc('File')
			new_file.content = content
			new_file.file_url = "/files/"+file_name
			new_file.file_size = os.path.getsize(file_path)
			new_file.file_name = file_name
			if content:
				new_content_hash = content.encode()
				new_content_hash = hashlib.md5(new_content_hash).hexdigest()
				new_file.content_hash = new_content_hash
			new_file.folder = "Home"
			new_file.is_private = 0
			new_file.attached_to_doctype = 'Google Drive Resume'
			new_file.attached_to_name = document_name
			new_file.attached_to_field = 'google_drive_file'
			new_file.flags.ignore_existing_file_check=True
			new_file.flags.ignore_permissions = True
			new_file.save()
			print('File Attached')
	
	try:
		with open(file_path, 'rb') as to_read_file:
			read_file_content = to_read_file.read()
			if "Contents" in str(read_file_content):
				file_readable = 1
	except:
		pass

	if not file_readable:
		file_downloaded = 0

	return file_downloaded