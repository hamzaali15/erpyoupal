# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import validate_email_address, now, flt, get_datetime
from erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api import invite_candidate_using_email, get_assessment_details, get_asessment_result, delete_candidate_assessment
from erpyoupal.erpyoupal.doctype.persona_test.persona_test import create_persona_test, create_background_check
from erpyoupal.events.hr.job_applicant import validate_application_process, create_self_evaluation
from erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview import create_interview_availability
from erpyoupal.erpyoupal.doctype.background_check.background_check import create_video_interview

class SkillTest(Document):
	def validate(self):
		if self.job_applicant:
			if not self.it_consultant:
				self.email = frappe.db.get_value("Job Applicant",self.job_applicant,"email_id")
		
		if self.email:
			self.it_consultant  = frappe.db.get_value("IT Consultant",{"email_primary": self.email}, "name")
			self.applicant_name = frappe.db.get_value("IT Consultant",{"email_primary": self.email}, "full_name")

		if self.is_new():
			self.send_testgorilla_assessment_invite()
			self.get_assessment_test_details()

		if not self.is_new():
			if self.job_applicant:
				application_process = validate_application_process(job_applicant=self.job_applicant)
				if self.ready_for_background_check and application_process in ['default', 'skip_background_check']:
					create_background_check(job_applicant=self.job_applicant, skill_test_ready_for_background_check=self.ready_for_background_check)
				if self.ready_for_background_check and application_process in ['assessment_first']:
					self.validate_score_assessment_first()
		
		self.test_status = "Pending"
		if self.ready_for_background_check:
			self.test_status = "Completed"

		self.save_it_consultant()
		self.update_applicant_highest_score()
	
	def update_applicant_highest_score(self):
		if self.average_score:
			applicants = frappe.get_all("Job Applicant", filters={"email_id": self.email}, fields=["name", "email_id", "highest_test_score"])
			if applicants:
				for applicant in applicants:
					if applicant.highest_test_score in ["N/A"]:
						frappe.db.set_value('Job Applicant', applicant.name, 'highest_test_score', self.average_score, update_modified=False)
					else:
						if str(applicant.highest_test_score).isnumeric() and flt(applicant.highest_test_score) < flt(self.average_score):
							frappe.db.set_value('Job Applicant', applicant.name, 'highest_test_score', self.average_score, update_modified=False)

	def save_it_consultant(self):
		#Trigger Save it consultant
		if self.it_consultant:
			frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=self.it_consultant, queue='long', timeout=300, now=False)

	def validate_job_applicant(self):
		if not frappe.get_all("Job Applicant", filters={"name": self.job_applicant}):
			frappe.throw(_("Job Applicant not found"))

	def after_insert(self):
		if self.job_applicant:
			application_process = validate_application_process(job_applicant=self.job_applicant)
			if application_process in ['default', 'skip_background_check']:
				entry = {
					"job_applicant": self.job_applicant,
					"applicant_name": self.applicant_name,
					"email": self.email
				}
				create_persona_test(entry)
	
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
		if self.assessment_id and self.email and self.applicant_name:
			get_asessment_test_details = get_assessment_details(self.assessment_id)
			if get_asessment_test_details:
				if get_asessment_test_details.get('tests_detail'):
					for row in get_asessment_test_details.get('tests_detail'):
						row_test = row.get('test')
						#if row_test.get('name') not in ['Custom questions']:
						self.append('tests_included', {
							"test_name": row_test.get('name'),
							"test_result_id": None,
							"score": None,
							"score_display": None,
							"test_status": row_test.get('status'),
							"test_id": row_test.get('id'),
							"completed": 0
						})

	def send_test_email(self):
		if self.email and self.test:
			for row in self.test:
				if row.test_link:
					frappe.sendmail(
						recipients=self.email,
						subject="Skill Test",
						message="""
							Dear """+self.applicant_name+""",\n

							Thank you for submitting an application to us.\n

							As part of your application. You are invited to take a Skill Test for you Top Skills.\n

							"""+row.test_link+"""\n

							\nGoodluck!
						"""
					)

	def validate_score_assessment_first(self):
		#all_test_completed = 1
		#if self.tests_included:
		#	for row in self.tests_included:
		#		if str(row.test_name) not in ['Custom questions'] and not row.completed:
		#			all_test_completed = 0

		#if all_test_completed:
		average_score = self.average_score
		if not self.average_score:
			average_score = 0
		else:
			if flt(self.average_score) <= 0:
				average_score = 0

		if flt(average_score) <= 65:
			#FAILED
			create_self_evaluation(job_applicant=self.job_applicant, from_application_process="Assessment First")
			frappe.db.set_value("Job Applicant", self.job_applicant, 'skill_test', 1)
		else:
			#PASSED
			create_interview_availability(job_applicant=self.job_applicant, from_application_process="Assessment First")

	@frappe.whitelist()
	def get_skill_testgorilla(self):
		if self.test:
			for row in self.test:
				if not row.test_title:
					row.test_title = row.skill
				row.test_link = frappe.get_value('Skill', row.skill, 'testgorilla_skill_test')
	
	@frappe.whitelist()
	def get_top_skills(self):
		doc = frappe.get_doc('Job Applicant', self.job_applicant)
		if doc.top_skill:
			for ts in doc.top_skill:
				self.append('top_skills', {
					'skill': ts.skill
				})
	
	@frappe.whitelist()
	def load_testgorilla_data(self):
		if not self.is_new():
			update_skill_test_document(self.name)

#erpyoupal.erpyoupal.doctype.skill_test.skill_test.create_skill_test
@frappe.whitelist(allow_guest=True)
def create_skill_test(assessment_id,job_applicant=None,it_consultant=None):
	assessment_details = get_assessment_details(assessment_id)
	# if frappe.get_value('Job Applicant', job_applicant, 'email_id') and not frappe.get_all('Skill Test', filters={'email': frappe.get_value('Job Applicant', job_applicant, 'email_id'), 'assessment_title': assessment_details.get('name')}, fields=['name']):
	new_doc = frappe.new_doc('Skill Test')
	new_doc.job_applicant = job_applicant
	new_doc.it_consultant = it_consultant
	new_doc.applicant_name = frappe.get_value('Job Applicant', job_applicant, 'applicant_name')
	new_doc.email = frappe.get_value('Job Applicant', job_applicant, 'email_id')
	#new_doc.status
	new_doc.date_created = now()
	#new_doc.date_completed
	new_doc.assessment_title = assessment_details.get('name')
	new_doc.assessment_id = assessment_details.get('id')
	#new_doc.assessment_link
	#new_doc.score
	#new_doc.rating
	#new_doc.invitation_section
	#new_doc.invitation_id
	#new_doc.test_taker_id
	#new_doc.invitation_uuid
	#new_doc.date_invited
	new_doc.flags.ignore_permissions = True
	new_doc.save()

#erpyoupal.erpyoupal.doctype.skill_test.skill_test.update_skill_test_document
@frappe.whitelist(allow_guest=True)
def update_skill_test_document(document_name=None):
	skill_tests = None
	if document_name:
		skill_tests = frappe.get_all('Skill Test', filters={'name': document_name}, fields=['name'])
	else:
		skill_tests = frappe.get_all('Skill Test', fields=['name'])

	if skill_tests:
		for skill_test in skill_tests:
			skill_test_doc = frappe.get_doc('Skill Test', skill_test.name)
			is_valid_entry = 0
			if frappe.get_all("Job Applicant", filters={"name": skill_test_doc.job_applicant}):
				is_valid_entry = 1
			if skill_test_doc.it_consultant:
				if frappe.get_all("IT Consultant", filters={"name": skill_test_doc.it_consultant}):
					is_valid_entry = 1

			if is_valid_entry and skill_test_doc.assessment_id and skill_test_doc.test_taker_id:
				skill_test_doc.average_score = flt(skill_test_doc.average_score)
				old_version = dict(skill_test_doc.__dict__)

				asessment_result = get_asessment_result(skill_test_doc.assessment_id, skill_test_doc.test_taker_id)
				all_test_completed = 0
				avg_score = 0
				test_count = len(skill_test_doc.tests_included)
				if asessment_result:
					if asessment_result.get('results'):
						for res in asessment_result.get('results'):
							for row in skill_test_doc.tests_included:
								if str(res.get('test_id')) == str(row.get('test_id')):
									row.status = res.get('status')
									row.completed = res.get('completed')
									row.score = res.get('score')
									row.score_display = str(res.get('score_display')).upper()
									#row.score_description = res.get('score_description')
									avg_score += flt(res.get('score'))
									#if row.completed and not str(res.get('name')) == "Custom questions":
									#	all_test_completed = 1
									#if all_test_completed and not row.completed and not str(res.get('name')) == "Custom questions":
									#	all_test_completed = 0

				test_count -= 1
				if test_count <= 1:
					test_count = 1
				avg_score = avg_score / test_count
				if avg_score > 0:
					skill_test_doc.average_score = flt(avg_score)
				for row in skill_test_doc.tests_included:
					if str("Custom questions") != str(row.test_name):
						if row.completed:
							all_test_completed = 1
				skill_test_doc.ready_for_background_check = all_test_completed
				new_version = dict(skill_test_doc.__dict__)
				if old_version != new_version:
					skill_test_doc.flags.ignore_permissions = True
					skill_test_doc.flags.ignore_linkss = True
					skill_test_doc.save()
					frappe.db.commit()

#erpyoupal.erpyoupal.doctype.skill_test.skill_test.retake_assessment
@frappe.whitelist()
def retake_assessment(skill_test_id):
	result = None
	if frappe.get_all("Skill Test", filters={"name": skill_test_id}, fields=['name']):
		doc = frappe.get_doc("Skill Test", skill_test_id)
		if doc.invitation_id:
			delete_candidate_assessment_result = delete_candidate_assessment(candidature_id=doc.invitation_id)
			if delete_candidate_assessment_result in ["Candidate removed"]:
				#Create Skill Test delted data
				skill_test_deleted_data = {}
				skill_test_deleted = frappe.new_doc("Skill Test Retake Data")
				skill_test_deleted_data = dict(doc.__dict__)
				tests_included = []
				if doc.tests_included:
					for row in doc.tests_included:
						tests_included.append(str(row.__dict__))
				skill_test_deleted_data['tests_included'] = tests_included
				retakes_history = []
				if doc.retakes:
					for retake_row in doc.retakes:
						retakes_history.append(str(retake_row.__dict__))
				skill_test_deleted_data['retakes'] = retakes_history
				skill_test_deleted.skill_test_name = doc.name
				skill_test_deleted.job_applicant = doc.job_applicant
				skill_test_deleted.applicant_name = doc.applicant_name
				skill_test_deleted.applicant_email = doc.email
				skill_test_deleted.data = str(skill_test_deleted_data)
				skill_test_deleted.flags.ignore_permissions = True
				skill_test_deleted.save()

				#Create new skill test
				new_skill_test = frappe.new_doc("Skill Test")
				new_skill_test.job_applicant = doc.job_applicant
				new_skill_test.applicant_name = doc.applicant_name
				new_skill_test.email = doc.email
				new_skill_test.assessment_title = doc.assessment_title
				new_skill_test.assessment_id = doc.assessment_id
				if doc.retakes:
					for retake in doc.retakes:
						new_skill_test.append('retakes', {
								"date_created": get_datetime(retake.date_created),
								"assessment_title": retake.assessment_title,
								"assessment_id": retake.assessment_id,
								"average_score": retake.average_score,
								"skill_test_data": retake.skill_test_data
							})
				new_skill_test.append('retakes', {
						"date_created": now(),
						"assessment_title": doc.assessment_title,
						"assessment_id": doc.assessment_id,
						"average_score": doc.average_score,
						"skill_test_data": skill_test_deleted.name if skill_test_deleted.name else None
					})
				new_skill_test.flags.ignore_permissions = True
				new_skill_test.save()

				#Delete Skill Test
				doc.flags.ignore_permissions = True
				doc.delete()
				result = new_skill_test.name
			else:
				result = delete_candidate_assessment_result
	else:
		result = "Skill Test not found"

	return result

#erpyoupal.erpyoupal.doctype.skill_test.skill_test.fill_applicants_highest_score
@frappe.whitelist()
def fill_applicants_highest_score():
	applicants = frappe.get_all("Job Applicant", fields=["name", "email_id"])
	for applicant in applicants:
		highest_score = "N/A"
		tests = frappe.get_all("Skill Test", filters={"email": applicant.email_id}, fields=["name", "average_score"])
		for test in tests:
			if test.average_score:
				if str(test.average_score).isnumeric():
					if highest_score == "N/A":
						highest_score = test.average_score
					else:
						if flt(test.average_score) > flt(highest_score):
							highest_score = test.average_score
		frappe.db.set_value('Job Applicant', applicant.name, 'highest_test_score', highest_score, update_modified=False)
		frappe.db.commit()