# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import validate_email_address, now
from erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api import invite_candidate_using_email, get_assessment_details, get_asessment_result
from erpyoupal.events.hr.job_applicant import validate_application_process
from erpyoupal.erpyoupal.doctype.background_check.background_check import create_video_interview

class PersonaTest(Document):
	def validate(self):
		self.validate_entry()
		if not self.assessment_id:
			self.assessment_id = '331132'
		if self.is_new():
			self.send_testgorilla_assessment_invite()
			self.get_assessment_test_details()
		else:
			application_process = validate_application_process(job_applicant=self.job_applicant)
			if self.ready_for_background_check and application_process in ['default']:
				create_background_check(job_applicant=self.job_applicant, persona_test_ready_for_background_check=self.ready_for_background_check)
			if self.ready_for_background_check and application_process in ['skip_background_check']:
				create_video_interview(job_applicant=self.job_applicant)
			if self.ready_for_background_check and application_process in ['assessment_first']:
				create_video_interview(job_applicant=self.job_applicant)

		self.test_status = "Pending"
		if self.ready_for_background_check:
			self.test_status = "Completed"

		self.save_it_consultant()

	def validate_entry(self):
		if not self.it_consultant and not self.job_applicant:
			frappe.throw(_("Job Applicant or IT Consultant is required"))
		if self.it_consultant:
			self.email = frappe.db.get_value("IT Consultant", self.it_consultant, "email_primary")
			self.applicant_name = frappe.db.get_value("IT Consultant", self.it_consultant, "full_name")
		if self.job_applicant:
			self.email = frappe.db.get_value("Job Applicant", self.job_applicant, "email_id")
			self.applicant_name = frappe.db.get_value("Job Applicant", self.job_applicant, "applicant_name")
			self.it_consultant = frappe.db.get_value("Job Applicant", self.job_applicant, "it_consultant")

	def save_it_consultant(self):
		#Trigger Save it consultant
		it_consultant = None
		if self.job_applicant:
			it_consultant = frappe.db.get_value("Job Applicant", self.job_applicant, "it_consultant")
		if self.it_consultant:
			it_consultant = self.it_consultant
		if it_consultant:
			frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=it_consultant, queue='long', timeout=300, now=False)

	def validate_job_applicant(self):
		if not frappe.get_all("Job Applicant", filters={"name": self.job_applicant}):
			frappe.throw(_("Job Applicant not found"))

	def after_insert(self):
		pass
	
	def send_testgorilla_assessment_invite(self):
		if self.assessment_id and self.email and self.applicant_name:
			data = {
				'email': self.email,
				'first_name': self.applicant_name,
			}
			data = json.dumps(data)
			invite_candidate_using_email_result = invite_candidate_using_email(self.assessment_id, data)
			if invite_candidate_using_email_result:
				self.status = invite_candidate_using_email_result.get('status')
				self.invitation_id = invite_candidate_using_email_result.get('id')
				self.test_taker_id = invite_candidate_using_email_result.get('testtaker_id')
				self.invitation_uuid = invite_candidate_using_email_result.get('invitation_uuid')
				self.date_invited = invite_candidate_using_email_result.get('created')
				if invite_candidate_using_email_result.get('invitation_uuid'):
					self.assessment_link = f"https://assessment.testgorilla.com/testtaker/takeinvitation/{invite_candidate_using_email_result.get('invitation_uuid')}"

	def get_assessment_test_details(self):
		if self.assessment_id and self.email and self.applicant_name and self.test_taker_id:
			get_asessment_test_details = get_assessment_details(self.assessment_id)
			if get_asessment_test_details:
				#self.tests_included = None
				if get_asessment_test_details.get('tests_detail'):
					for row in get_asessment_test_details.get('tests_detail'):
						row_test = row.get('test')
						if row_test.get('name') not in ['Custom questions']:
							self.append('tests_included', {
								"test_name": row_test.get('name'),
								"test_result_id": None,
								"score": None,
								"score_display": None,
								"test_status": row_test.get('status'),
								"test_id": row_test.get('id'),
								"completed": 0
							})
	
	@frappe.whitelist()
	def load_testgorilla_data(self):
		if not self.is_new():
			update_persona_test_document(self.name)

#erpyoupal.erpyoupal.doctype.persona_test.persona_test.update_persona_test_document
@frappe.whitelist(allow_guest=True)
def update_persona_test_document(document_name=None):
	if document_name:
		persona_tests = frappe.get_all('Persona Test', filters={'name': document_name}, fields=['name'])
	else:
		persona_tests = frappe.get_all('Persona Test', fields=['name'])

	if persona_tests:
		for persona_test in persona_tests:
			persona_test_doc = frappe.get_doc('Persona Test', persona_test.name)
			is_valid_job_applicant = 0
			if persona_test_doc.it_consultant:
				if frappe.get_all("IT Consultant", filters={"name": persona_test_doc.it_consultant}):
					is_valid_job_applicant = 1
			if persona_test_doc.job_applicant:
				if frappe.get_all("Job Applicant", filters={"name": persona_test_doc.job_applicant}):
					is_valid_job_applicant = 1
			if is_valid_job_applicant and persona_test_doc.assessment_id and persona_test_doc.test_taker_id:
				old_version = dict(persona_test_doc.__dict__)
				asessment_result = get_asessment_result(persona_test_doc.assessment_id, persona_test_doc.test_taker_id)
				all_test_completed = 0
				if asessment_result:
					if asessment_result.get('results'):
						for res in asessment_result.get('results'):
							for row in persona_test_doc.tests_included:
								if str(res.get('test_id')) == str(row.get('test_id')):
									row.status = res.get('status')
									row.completed = res.get('completed')
									row.score = res.get('score')
									row.score_display = str(res.get('score_display')).upper()
									row.score_description = res.get('score_description')
									if str(res.get('name')) == 'DISC':
										persona_test_doc.score = str(res.get('score_display')).upper()
									if row.completed and not str(res.get('name')) == "Custom questions":
										all_test_completed = 1
									if all_test_completed and not row.completed and not str(res.get('name')) == "Custom questions":
										all_test_completed = 0
				persona_test_doc.ready_for_background_check = all_test_completed
				new_version = dict(persona_test_doc.__dict__)
				if old_version != new_version:
					persona_test_doc.flags.ignore_permissions = True
					persona_test_doc.flags.ignore_links = True
					persona_test_doc.save()

@frappe.whitelist(allow_guest=True)
def create_persona_test(entry):
	if not entry.get('email'):
		frappe.throw(_("No email passed"))
	existing_doc = frappe.get_all("Persona Test", filters={"email": entry.get('email')}, fields=["name"])
	if not existing_doc:
		new_doc = frappe.new_doc("Persona Test")
		new_doc.job_applicant = entry.get('job_applicant')
		new_doc.it_consultant = entry.get('it_consultant')
		new_doc.flags.ignore_permissions = True
		return new_doc.insert()
	else:
		return frappe.get_doc("Persona Test", existing_doc[0].name)

#erpyoupal.erpyoupal.doctype.persona_test.persona_test.create_background_check
@frappe.whitelist(allow_guest=True)
def create_background_check(job_applicant=None, it_consultant=None, persona_test_ready_for_background_check=0, skill_test_ready_for_background_check=0, disregard_tests=0, disable_email_sending=0):
	result = None
	exams_completed = 0
	if disregard_tests:
		exams_completed = 1
	else:
		skill_tests = frappe.get_all("Skill Test", filters={"job_applicant": job_applicant}, fields=['name', 'ready_for_background_check'])
		if skill_tests and (skill_tests[0].ready_for_background_check or skill_test_ready_for_background_check):
			persona_tests = frappe.get_all("Persona Test", filters={"job_applicant": job_applicant}, fields=['name', 'ready_for_background_check'])
			if persona_tests and (persona_tests[0].ready_for_background_check or persona_test_ready_for_background_check):
				exams_completed = 1	

	email_id = None
	if it_consultant:
		email_id = frappe.get_value('IT Consultant', it_consultant, 'email_primary')
	if job_applicant:
		email_id = frappe.get_value('Job Applicant', job_applicant, 'email_id')

	existing_doc = frappe.get_all("Background Check", filters={'email': email_id}, fields=["name"])
	if existing_doc:
		pass
		#frappe.throw(_("Background Check for this email already exists."))
		frappe.local.response["data"] = frappe.get_doc("Background Check", existing_doc[0].name)
	else:
		if exams_completed:
			new_doc = frappe.new_doc("Background Check")
			new_doc.job_applicant = job_applicant
			new_doc.it_consultant = it_consultant
			if disable_email_sending:
				new_doc.disable_email_sending = 1
			new_doc.flags.ignore_links = True
			new_doc.flags.ignore_permissions = True
			result = new_doc.insert()
			frappe.local.response["data"] = result
			frappe.local.response["message"] = result