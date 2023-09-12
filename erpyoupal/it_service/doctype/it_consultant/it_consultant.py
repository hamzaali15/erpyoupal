# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt, getdate, now
from erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview import create_interview_availability
from erpyoupal.erpyoupal.doctype.background_check.background_check import create_video_interview
from erpyoupal.erpyoupal.doctype.persona_test.persona_test import create_background_check
from erpyoupal.erpyoupal.doctype.year.year import validate_year

class ITConsultant(Document):
	def autoname(self):
		self.name = self.email_primary
		if self.it_consultant_name:
			self.name = self.it_consultant_name
	
	#def before_insert(self):
	#	self.validate_experience_since()

	def validate(self):
		self.get_full_name()
		self.get_people_image()
		self.validate_experience_since()
		self.vaidate_platform_social_media()
		self.record_job_applicants()
		self.record_self_evaluations()
		self.record_skill_tests()
		self.record_skill_tests_coderbyte()
		self.record_persona_tests()
		self.record_background_checks()
		self.record_video_interviews()
		self.record_candidate_interviews()
		self.validate_user_account()
		if not self.is_new():
			self.update_people_document()
	
	def after_insert(self):
		self.create_people_document()
	
	def validate_experience_since(self):
		if self.experience_since:
			validate_year(year=self.experience_since)
			total_experience = int(getdate(now()).year) - int(self.experience_since)
			if total_experience > 0:
				self.total_experience = total_experience
	
	def vaidate_platform_social_media(self):
		if self.platform_social_media:
			included_platform = []
			final_rows = []
			for row in self.platform_social_media:
				if not row.platform_social_media in included_platform:
					included_platform.append(row.platform_social_media)
					final_rows.append({
						"platform_social_media": row.platform_social_media,
						"link": row.link
					})
			if final_rows:
				self.platform_social_media = []
				for fin in final_rows:
					self.append("platform_social_media", fin)

	def create_people_document(self):
		if not self.get("ignore_people_creation"):
			existing_peoples = frappe.get_all("People", filters={"email_address": self.email_primary}, fields=["name"])
			if not existing_peoples:
				new_doc = frappe.new_doc("People")
				new_doc.ignore_it_consultant_creation = True
				new_doc.flags.ignore_permissions = True
				new_doc.flags.ignore_links = True
				new_doc.people_type = "Consultant"
				new_doc.first_name = self.first_name
				new_doc.last_name = self.last_name
				new_doc.status = "Active"
				new_doc.date_of_birth = self.date_of_birth
				new_doc.gender = self.gender
				new_doc.it_consultant = self.name
				new_doc.create_user = 1
				new_doc.address = self.address
				new_doc.country = self.location
				new_doc.image = self.image
				new_doc.passport_nationality = self.passport_nationality
				new_doc.passport_number = self.passport_number
				new_doc.passport_dob = self.passport_dob
				new_doc.passport_cityofbirth = self.passport_cityofbirth
				new_doc.passport_countryofbirth = self.passport_countryofbirth
				new_doc.passport_gender = self.passport_gender
				new_doc.passport_dateofissue = self.passport_dateofissue
				new_doc.passport_dateofexpiry = self.passport_dateofexpiry
				new_doc.passport_issuedby = self.passport_issuedby
				new_doc.passport_visatype = self.passport_visatype
				new_doc.emergency_contact_name = self.emergency_contact_name
				new_doc.emergency_contact_email = self.emergency_contact_email
				new_doc.emergency_contact_mobile = self.emergency_contact_mobile
				new_doc.append("email", {"email": self.email_primary})
				new_doc.append("mobile", {"mobile": self.mobile_primary})
				if self.platform_social_media:
					for row in self.platform_social_media:
						if row.link:
							if str(row.platform_social_media).lower() in ["linkedin", "linked in"]:
								new_doc.linkedin = row.link
							if str(row.platform_social_media).lower() in ["facebook", "face book"]:
								new_doc.facebook = row.link
							if str(row.platform_social_media).lower() in ["instagram", "insta gram"]:
								new_doc.instagram = row.link
							if str(row.platform_social_media).lower() in ["twitter", "twit ter"]:
								new_doc.twitter = row.link
				new_doc.triggered_from_it_consultant = True
				new_doc.insert()
				frappe.db.commit()
				create_interview_availability(it_consultant=self.name, disable_email_sending=1)
				create_video_interview(it_consultant=self.name, disable_email_sending=1)
				create_background_check(it_consultant=self.name, disregard_tests=1, disable_email_sending=1)
				frappe.rename_doc('IT Consultant', self.name, new_doc.name)

	def update_people_document(self):
		if not self.get("triggered_from_people"):
			existing_peoples = frappe.get_all("People", filters={"email_address": self.email_primary}, fields=["name"])
			if existing_peoples:
				cur_doc = frappe.get_doc("People", existing_peoples[0].name)
				cur_doc.ignore_it_consultant_creation = True
				cur_doc.flags.ignore_permissions = True
				cur_doc.flags.ignore_links = True
				cur_doc.first_name = self.first_name
				cur_doc.last_name = self.last_name
				cur_doc.date_of_birth = self.date_of_birth
				cur_doc.gender = self.gender
				cur_doc.it_consultant = self.name
				cur_doc.address = self.address
				cur_doc.country = self.location
				#cur_doc.image = self.image
				cur_doc.passport_nationality = self.passport_nationality
				cur_doc.passport_number = self.passport_number
				cur_doc.passport_dob = self.passport_dob
				cur_doc.passport_cityofbirth = self.passport_cityofbirth
				cur_doc.passport_countryofbirth = self.passport_countryofbirth
				cur_doc.passport_gender = self.passport_gender
				cur_doc.passport_dateofissue = self.passport_dateofissue
				cur_doc.passport_dateofexpiry = self.passport_dateofexpiry
				cur_doc.passport_issuedby = self.passport_issuedby
				cur_doc.passport_visatype = self.passport_visatype
				cur_doc.emergency_contact_name = self.emergency_contact_name
				cur_doc.emergency_contact_email = self.emergency_contact_email
				cur_doc.emergency_contact_mobile = self.emergency_contact_mobile
				#cur_doc.append("email", {"email": self.email_primary})
				if cur_doc.mobile:
					new_mobile = 1
					for row in cur_doc.mobile:
						if row.mobile == self.mobile_primary:
							new_mobile = 0
					if new_mobile:
						cur_doc.append("mobile", {"mobile": self.mobile_primary})	
				else:
					cur_doc.append("mobile", {"mobile": self.mobile_primary})
				if self.platform_social_media:
					for row in self.platform_social_media:
						if row.link:
							if str(row.platform_social_media).lower() in ["linkedin", "linked in"]:
								cur_doc.linkedin = row.link
							if str(row.platform_social_media).lower() in ["facebook", "face book"]:
								cur_doc.facebook = row.link
							if str(row.platform_social_media).lower() in ["instagram", "insta gram"]:
								cur_doc.instagram = row.link
							if str(row.platform_social_media).lower() in ["twitter", "twit ter"]:
								cur_doc.twitter = row.link
							if str(row.platform_social_media).lower() in ["fiverr", "fiv err"]:
								cur_doc.fiverr = row.link
							if str(row.platform_social_media).lower() in ["github", "git hub"]:
								cur_doc.github = row.link
							if str(row.platform_social_media).lower() in ["upwork", "up work"]:
								cur_doc.upwork = row.link
							if str(row.platform_social_media).lower() in ["stackoverflow", "stack overflow"]:
								cur_doc.stackoverflow = row.link
				cur_doc.triggered_from_it_consultant = True
				cur_doc.save()

	def get_people_image(self):
		if not self.image or (frappe.db.get_value('IT Consultant', self.name, 'image') != self.image):
			peoples = frappe.get_all("People", filters={"email_address": self.email_primary}, fields=["name", "image"])
			if peoples:
				self.image = peoples[0].image
		
	def get_full_name(self):
		if self.first_name:
			self.full_name = self.first_name
		if self.last_name:
			self.full_name = self.last_name
		if self.first_name and self.last_name:
			self.full_name = self.first_name+" "+self.last_name

	def get_all_job_applicant(self):
		result = []
		docs = frappe.get_all("Job Applicant", filters={"email_id": self.email_primary}, fields=['name'])
		if docs:
			for doc in docs:
				result.append(doc.name)
		return result

	def validate_user_account(self):
		result = None
		if self.email_primary:
			users = frappe.get_all("User", filters={"name": self.email_primary}, fields=["name"])
			if not users:
				new_doc = frappe.new_doc("User")
				new_doc.email = self.email_primary
				new_doc.first_name = self.first_name
				new_doc.last_name = self.last_name
				new_doc.it_consultant = self.name
				new_doc.user_type = "Website User"
				#new_doc.enabled = 0
				new_doc.send_welcome_email = 0
				new_doc.flags.ignore_permissions = True
				new_doc.save()
				from frappe.core.doctype.user.user import generate_keys
				generate_keys(user=new_doc.name)
			else:
				cur_doc = frappe.get_doc("User", users[0].name)
				if not cur_doc.it_consultant or (cur_doc.it_consultant != self.name):
					cur_doc.it_consultant = self.name
					cur_doc.flags.ignore_permissions = True
					cur_doc.save()

			with_candidate_interview = frappe.get_all("Candidate Interview", filters={"email": self.email_primary}, fields=['name'])
			if with_candidate_interview:
				self.talent_app_access = 1
			else:
				self.talent_app_access = 0

			if self.manual_talent_app_access:
				self.talent_app_access = 1

		return result

	def record_job_applicants(self):
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				existing_row = list(filter(lambda d: d.get('job_applicant') in [job_applicant], self.job_applicant_history))
				if not existing_row:
					self.append("job_applicant_history", {
						"job_applicant": job_applicant,
						"job_opening": frappe.db.get_value("Job Applicant", job_applicant, "job_title"),
						"date_created": frappe.db.get_value("Job Applicant", job_applicant, "creation"),
						"rate": frappe.db.get_value("Job Applicant", job_applicant, "rate"),
						"designation": frappe.db.get_value("Job Applicant", job_applicant, "designation"),
						"sub_designation": frappe.db.get_value("Job Applicant", job_applicant, "sub_designation")
					})
				else:
					table_idx = flt(existing_row[0].idx) - 1
					table_idx = int(table_idx)
					self.job_applicant_history[table_idx].job_applicant = job_applicant
					self.job_applicant_history[table_idx].job_opening = frappe.db.get_value("Job Applicant", job_applicant, "job_title")
					self.job_applicant_history[table_idx].date_created = frappe.db.get_value("Job Applicant", job_applicant, "creation")
					self.job_applicant_history[table_idx].rate = frappe.db.get_value("Job Applicant", job_applicant, "rate")
					self.job_applicant_history[table_idx].designation = frappe.db.get_value("Job Applicant", job_applicant, "designation")
					self.job_applicant_history[table_idx].sub_designation = frappe.db.get_value("Job Applicant", job_applicant, "sub_designation")

	def record_self_evaluations(self):
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				docs = frappe.get_all("Self Evaluation", filters={"job_applicant": job_applicant}, fields=['name', 'creation', 'job_applicant', 'self_evaluation'])
				for doc in docs:
					self_evaluation_status = "Not Completed"
					if doc.self_evaluation:
						self_evaluation_status = "Completed"

					existing_row = list(filter(lambda d: d.get('self_evaluation_id') in [doc.name], self.self_evaluation_history))
					if not existing_row:
						self.append("self_evaluation_history", {
							"self_evaluation_id": doc.name,
							"job_applicant_id": doc.job_applicant,
							"date_created": doc.creation,
							"status": self_evaluation_status
							})
					else:
						table_idx = flt(existing_row[0].idx) - 1
						table_idx = int(table_idx)
						self.self_evaluation_history[table_idx].self_evaluation_id = doc.name
						self.self_evaluation_history[table_idx].job_applicant_id = doc.job_applicant
						self.self_evaluation_history[table_idx].date_created = doc.creation
						self.self_evaluation_history[table_idx].status = self_evaluation_status

	def record_skill_tests(self):
		#created from IT Consultant
		st_docs = frappe.get_all("Skill Test", filters={"it_consultant": self.name}, fields=['name', 'creation', 'job_applicant', 'status', 'test_status', 'average_score'])
		for doc in st_docs:
			existing_row = list(filter(lambda d: d.get('skill_test_id') in [doc.name], self.skill_test_history))
			test_status = doc.test_status
			if not test_status:
				test_status = doc.status
			if not existing_row:
				self.append("skill_test_history", {
					"skill_test_id": doc.name,
					"job_applicant_id": doc.job_applicant,
					"date_created": doc.creation,
					"status": test_status,
					"average_score": doc.average_score
					})
			else:
				table_idx = flt(existing_row[0].idx) - 1
				table_idx = int(table_idx)
				self.skill_test_history[table_idx].skill_test_id = doc.name
				self.skill_test_history[table_idx].job_applicant_id = doc.job_applicant
				self.skill_test_history[table_idx].date_created = doc.creation
				self.skill_test_history[table_idx].status = test_status
				self.skill_test_history[table_idx].average_score = doc.average_score
		#created from Job Applicant
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				docs = frappe.get_all("Skill Test", filters={"job_applicant": job_applicant}, fields=['name', 'creation', 'job_applicant', 'status', 'test_status', 'average_score'])
				for doc in docs:
					existing_row = list(filter(lambda d: d.get('skill_test_id') in [doc.name], self.skill_test_history))
					test_status = doc.test_status
					if not test_status:
						test_status = doc.status
					if not existing_row:
						self.append("skill_test_history", {
							"skill_test_id": doc.name,
							"job_applicant_id": doc.job_applicant,
							"date_created": doc.creation,
							"status": test_status,
							"average_score": doc.average_score
							})
					else:
						table_idx = flt(existing_row[0].idx) - 1
						table_idx = int(table_idx)
						self.skill_test_history[table_idx].skill_test_id = doc.name
						self.skill_test_history[table_idx].job_applicant_id = doc.job_applicant
						self.skill_test_history[table_idx].date_created = doc.creation
						self.skill_test_history[table_idx].status = test_status
						self.skill_test_history[table_idx].average_score = doc.average_score

	def record_skill_tests_coderbyte(self):
		#created from IT Consultant
		st_docs = frappe.get_all("Skill Test Coderbyte", filters={"it_consultant": self.name}, fields=['name', 'creation', 'job_applicant', 'assessment_link', 'email'])
		for doc in st_docs:
			final_score = None
			if doc.assessment_link and doc.email:
				result_link_key = str(doc.assessment_link)			
				result_link_key = result_link_key.strip("https://coderbyte.com/sl-candidate?promo=youpalab-lmhum:")
				result_link_key = '%'+result_link_key+'%'
				coderbyte_result = frappe.get_all("Coderbyte Result", filters=[['assessment_link', 'like', result_link_key], ['email', '=', doc.email]], fields=['name', 'final_score'])
				if coderbyte_result:
					final_score = coderbyte_result[0].final_score

			existing_row = list(filter(lambda d: d.get('skill_test_coderbyte_id') in [doc.name], self.skill_test_coderbyte_history))
			if not existing_row:
				self.append("skill_test_coderbyte_history", {
					"skill_test_coderbyte_id": doc.name,
					"job_applicant_id": doc.job_applicant,
					"date_created": doc.creation,
					"final_score": final_score
					})
			else:
				table_idx = flt(existing_row[0].idx) - 1
				table_idx = int(table_idx)
				self.skill_test_coderbyte_history[table_idx].skill_test_coderbyte_id = doc.name
				self.skill_test_coderbyte_history[table_idx].job_applicant_id = doc.job_applicant
				self.skill_test_coderbyte_history[table_idx].date_created = doc.creation
				self.skill_test_coderbyte_history[table_idx].final_score = final_score
		#created from Job Applicant
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				docs = frappe.get_all("Skill Test Coderbyte", filters={"job_applicant": job_applicant}, fields=['name', 'creation', 'job_applicant', 'assessment_link', 'email'])
				for doc in docs:
					final_score = None
					if doc.assessment_link and doc.email:
						result_link_key = str(doc.assessment_link)			
						result_link_key = result_link_key.strip("https://coderbyte.com/sl-candidate?promo=youpalab-lmhum:")
						result_link_key = '%'+result_link_key+'%'
						coderbyte_result = frappe.get_all("Coderbyte Result", filters=[['assessment_link', 'like', result_link_key], ['email', '=', doc.email]], fields=['name', 'final_score'])
						if coderbyte_result:
							final_score = coderbyte_result[0].final_score

					existing_row = list(filter(lambda d: d.get('skill_test_coderbyte_id') in [doc.name], self.skill_test_coderbyte_history))
					if not existing_row:
						self.append("skill_test_coderbyte_history", {
							"skill_test_coderbyte_id": doc.name,
							"job_applicant_id": doc.job_applicant,
							"date_created": doc.creation,
							"final_score": final_score
							})
					else:
						table_idx = flt(existing_row[0].idx) - 1
						table_idx = int(table_idx)
						self.skill_test_coderbyte_history[table_idx].skill_test_coderbyte_id = doc.name
						self.skill_test_coderbyte_history[table_idx].job_applicant_id = doc.job_applicant
						self.skill_test_coderbyte_history[table_idx].date_created = doc.creation
						self.skill_test_coderbyte_history[table_idx].final_score = final_score

	def record_persona_tests(self):
		#created from IT Consultant
		docs = frappe.get_all("Persona Test", filters={"it_consultant": self.name}, fields=['name', 'creation', 'job_applicant', 'status', 'test_status', 'score'])
		for doc in docs:
			existing_row = list(filter(lambda d: d.get('persona_test_id') in [doc.name], self.persona_test_history))
			test_status = doc.test_status
			if not test_status:
				test_status = doc.status
			if not existing_row:
				score_description = None
				if doc.tests_included:
					score_description = doc.tests_included[0].score_description
				self.append("persona_test_history", {
					"persona_test_id": doc.name,
					"job_applicant_id": doc.job_applicant,
					"date_created": doc.creation,
					"status": test_status,
					"score": doc.score,
					"score_description": score_description
					})
			else:
				table_idx = flt(existing_row[0].idx) - 1
				table_idx = int(table_idx)
				self.persona_test_history[table_idx].persona_test_id = doc.name
				self.persona_test_history[table_idx].job_applicant_id = doc.job_applicant
				self.persona_test_history[table_idx].date_created = doc.creation
				self.persona_test_history[table_idx].status = test_status
				self.persona_test_history[table_idx].score = doc.score
				if doc.tests_included:
					self.persona_test_history[table_idx].score_description = doc.tests_included[0].score_description
		#created from Job Applicant
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				docs = frappe.get_all("Persona Test", filters={"job_applicant": job_applicant}, fields=['name', 'creation', 'job_applicant', 'status', 'test_status', 'score'])
				for doc in docs:
					doc = frappe.get_doc("Persona Test", doc.name)
					existing_row = list(filter(lambda d: d.get('persona_test_id') in [doc.name], self.persona_test_history))
					test_status = doc.test_status
					if not test_status:
						test_status = doc.status
					if not existing_row:
						score_description = None
						if doc.tests_included:
							score_description = doc.tests_included[0].score_description
						self.append("persona_test_history", {
							"persona_test_id": doc.name,
							"job_applicant_id": doc.job_applicant,
							"date_created": doc.creation,
							"status": test_status,
							"score": doc.score,
							"score_description": score_description
							})
					else:
						table_idx = flt(existing_row[0].idx) - 1
						table_idx = int(table_idx)
						self.persona_test_history[table_idx].persona_test_id = doc.name
						self.persona_test_history[table_idx].job_applicant_id = doc.job_applicant
						self.persona_test_history[table_idx].date_created = doc.creation
						self.persona_test_history[table_idx].status = test_status
						self.persona_test_history[table_idx].score = doc.score
						if doc.tests_included:
							self.persona_test_history[table_idx].score_description = doc.tests_included[0].score_description

	def record_background_checks(self):
		#created from IT Consultant
		bc_consultants = frappe.get_all("Background Check", filters={"it_consultant": self.name}, fields=['name', 'creation', 'job_applicant', 'identification_status', 'status', 'pdf_link', 'public_printview_link'])
		for bcc in bc_consultants:
			existing_row = list(filter(lambda d: d.get('background_check_id') in [bcc.name], self.background_check_history))
			if not existing_row:
				self.append("background_check_history", {
					"background_check_id": bcc.name,
					"job_applicant_id": bcc.job_applicant,
					"date_created": bcc.creation,
					"status": bcc.status,
					"identification_status": bcc.identification_status,
					"pdf_link": bcc.pdf_link,
					"public_printview_link": bcc.public_printview_link
					})
			else:
				table_idx = flt(existing_row[0].idx) - 1
				table_idx = int(table_idx)
				self.background_check_history[table_idx].background_check_id = bcc.name
				self.background_check_history[table_idx].job_applicant_id = bcc.job_applicant
				self.background_check_history[table_idx].date_created = bcc.creation
				self.background_check_history[table_idx].status = bcc.status
				self.background_check_history[table_idx].identification_status = bcc.identification_status
				self.background_check_history[table_idx].pdf_link = bcc.pdf_link
				self.background_check_history[table_idx].public_printview_link = bcc.public_printview_link
		#created from Job Applicant
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				docs = frappe.get_all("Background Check", filters={"job_applicant": job_applicant}, fields=['name', 'creation', 'job_applicant', 'identification_status', 'status', 'pdf_link', 'public_printview_link'])
				for doc in docs:
					existing_row = list(filter(lambda d: d.get('background_check_id') in [doc.name], self.background_check_history))
					if not existing_row:
						self.append("background_check_history", {
							"background_check_id": doc.name,
							"job_applicant_id": doc.job_applicant,
							"date_created": doc.creation,
							"status": doc.status,
							"identification_status": doc.identification_status,
							"pdf_link": doc.pdf_link,
							"public_printview_link": doc.public_printview_link
							})
					else:
						table_idx = flt(existing_row[0].idx) - 1
						table_idx = int(table_idx)
						self.background_check_history[table_idx].background_check_id = doc.name
						self.background_check_history[table_idx].job_applicant_id = doc.job_applicant
						self.background_check_history[table_idx].date_created = doc.creation
						self.background_check_history[table_idx].status = doc.status
						self.background_check_history[table_idx].identification_status = doc.identification_status
						self.background_check_history[table_idx].pdf_link = doc.pdf_link
						self.background_check_history[table_idx].public_printview_link = doc.public_printview_link

	def record_video_interviews(self):
		self.video_interview_history = None
		#created from IT Consultant
		vi_consultants = frappe.get_all("Video Interview", filters={"it_consultant": self.name}, fields=["name"])
		if vi_consultants:
			for vic in vi_consultants:
				doc_video_interview = frappe.get_doc("Video Interview", vic.name)
				if doc_video_interview.record_history:
					for row in doc_video_interview.record_history:
						self.append("video_interview_history", {
							"video_interview_id": row.video_interview_id,
							"job_applicant_id": row.job_applicant_id,
							"date_created": row.date_created,
							"status": row.status
						})
		#created from Job Applicant
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				docs = frappe.get_all("Video Interview", filters={"job_applicant": job_applicant}, fields=['name', 'creation', 'job_applicant', 'status'])
				for doc in docs:
					doc_video_interview = frappe.get_doc("Video Interview", doc.name)
					if doc_video_interview.record_history:
						for row in doc_video_interview.record_history:
							self.append("video_interview_history", {
								"video_interview_id": row.video_interview_id,
								"job_applicant_id": row.job_applicant_id,
								"date_created": row.date_created,
								"status": row.status
							})

	def record_candidate_interviews(self):
		#created from IT Consultant
		ci_consultants = frappe.get_all("Candidate Interview", filters={"it_consultant": self.name}, fields=['name', 'creation', 'job_applicant'])
		for cic in ci_consultants:
			existing_row = list(filter(lambda d: d.get('candidate_interview_id') in [cic.name], self.candidate_interview_history))
			if not existing_row:
				self.append("candidate_interview_history", {
					"candidate_interview_id": cic.name,
					"job_applicant_id": cic.job_applicant,
					"date_created": cic.creation
					})
				self.candidate_interview = cic.name
			else:
				table_idx = flt(existing_row[0].idx) - 1
				table_idx = int(table_idx)
				self.candidate_interview_history[table_idx].candidate_interview_id = cic.name
				self.candidate_interview_history[table_idx].job_applicant_id = cic.job_applicant
				self.candidate_interview_history[table_idx].date_created = cic.creation
				self.candidate_interview = cic.name
		#created from Job Applicant
		job_applicants = self.get_all_job_applicant()
		if job_applicants:
			for job_applicant in job_applicants:
				docs = frappe.get_all("Candidate Interview", filters={"job_applicant": job_applicant}, fields=['name', 'creation', 'job_applicant'])
				for doc in docs:
					existing_row = list(filter(lambda d: d.get('candidate_interview_id') in [doc.name], self.candidate_interview_history))
					if not existing_row:
						self.append("candidate_interview_history", {
							"candidate_interview_id": doc.name,
							"job_applicant_id": doc.job_applicant,
							"date_created": doc.creation
							})
						self.candidate_interview = doc.name
					else:
						table_idx = flt(existing_row[0].idx) - 1
						table_idx = int(table_idx)
						self.candidate_interview_history[table_idx].candidate_interview_id = doc.name
						self.candidate_interview_history[table_idx].job_applicant_id = doc.job_applicant
						self.candidate_interview_history[table_idx].date_created = doc.creation
						self.candidate_interview = doc.name

	@frappe.whitelist()
	def default_platform_social_media(self):
		for item in ["linkedin","facebook","instagram","twitter","Platforms","Fiverr","StackoverFlow","Github"]:
			self.append('platform_social_media', {
				"platform_social_media": item
				})
	
	@frappe.whitelist()
	def go_to_agency(self):
		peoples = frappe.get_all("People", filters={"email_address": self.email_primary}, fields=["name", "organization_name"])
		if peoples:
			if peoples[0].organization_name:
				return peoples[0].organization_name
			else:
				frappe.msgprint(_("No Agency/Organization was set for this IT Consultant"))
		else:
			return None
	
	@frappe.whitelist()
	def go_to_people(self):
		peoples = frappe.get_all("People", filters={"email_address": self.email_primary}, fields=["name"])
		if peoples:
			return peoples[0].name
		else:
			return None


#erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant
@frappe.whitelist()
def trigger_save_it_consultant(it_consultant):
	if frappe.get_all("IT Consultant", filters={"name": it_consultant}):
		doc = frappe.get_doc("IT Consultant", it_consultant)
		doc.flags.ignore_permissions = True
		doc.flags.ignore_links = True
		doc.save()

#erpyoupal.it_service.doctype.it_consultant.it_consultant.get_candidate_data
@frappe.whitelist()
def get_candidate_data(it_consultant="Cid-IT Consultant-000004632"):
	if frappe.get_all("IT Consultant", filters={"name": it_consultant}):
		data = frappe.get_doc("IT Consultant", it_consultant)
		return data

#erpyoupal.it_service.doctype.it_consultant.it_consultant.get_it_consultant_list
@frappe.whitelist()
def get_it_consultant_list(filters=None):
	result = []
	doc_lists = None

	if filters:
		doc_lists = frappe.get_all("IT Consultant", filters=filters, fields=['name'])
	else:
		doc_lists = frappe.get_all("IT Consultant", fields=['name'])

	if doc_lists:
		for doc_list in doc_lists:
			doc = frappe.get_doc("IT Consultant", doc_list.name)
			result.append(doc)

	return result

#erpyoupal.it_service.doctype.it_consultant.it_consultant.get_it_consultant_data
@frappe.whitelist()
def get_it_consultant_data(it_consultant):
	result = None

	doc_lists = frappe.get_all("IT Consultant", filters={"name": it_consultant}, fields=["name"])
	if doc_lists:
		result = {}
		it_consultant_data = frappe.get_doc("IT Consultant", it_consultant)
		
		meta = frappe.get_meta("IT Consultant")
		for i in meta.get("fields"):
			if it_consultant_data.get(i.fieldname):
				result[i.fieldname] = it_consultant_data.get(i.fieldname)
			else:
				if i.fieldtype in ['Table', 'Table MultiSelect']:
					result[i.fieldname] = []
				else:
					result[i.fieldname] = ""
		
		it_consultant_data_self_evaluation_history = []
		it_consultant_data_skill_test_history = []
		it_consultant_data_skill_coderbyte_test_history = []
		it_consultant_data_persona_test_history = []
		it_consultant_data_background_check_history = []
		it_consultant_data_video_interview_history = []
		it_consultant_data_candidate_interview_history = []

		result['linkedin'] = ""
		result['facebook'] = ""
		result['instagram'] = ""
		result['twitter'] = ""
		result['fiverr'] = ""
		result['github'] = ""
		result['upwork'] = ""
		result['stackoverflow'] = ""
		#defrag platform_social_media list
		for psm in it_consultant_data.platform_social_media:
			if str(psm.platform_social_media).lower() in ['linkedin'] and psm.link:
				result['linkedin'] = psm.link
			if str(psm.platform_social_media).lower() in ['facebook'] and psm.link:
				result['facebook'] = psm.link
			if str(psm.platform_social_media).lower() in ['instagram'] and psm.link:
				result['instagram'] = psm.link
			if str(psm.platform_social_media).lower() in ['twitter'] and psm.link:
				result['twitter'] = psm.link
			if str(psm.platform_social_media).lower() in ['fiverr'] and psm.link:
				result['fiverr'] = psm.link
			if str(psm.platform_social_media).lower() in ['github'] and psm.link:
				result['github'] = psm.link
			if str(psm.platform_social_media).lower() in ['upwork'] and psm.link:
				result['upwork'] = psm.link
			if str(psm.platform_social_media).lower() in ['stackoverflow'] and psm.link:
				result['stackoverflow'] = psm.link

		#NO JOB APPLICANT HISTORY
		#Get Video Interview History
		for icd_vih in it_consultant_data.video_interview_history:
			if not icd_vih.job_applicant_id:
				if frappe.get_all("Video Interview", filters={"name": icd_vih.video_interview_id}):
					video_interview_history_data = frappe.get_doc("Video Interview", icd_vih.video_interview_id)
					it_consultant_data_video_interview_history.append(video_interview_history_data)
		#Get candidate Interview History
		for icd_cih in it_consultant_data.candidate_interview_history:
			if not icd_cih.job_applicant_id:
				if frappe.get_all("Candidate Interview", filters={"name": icd_cih.candidate_interview_id}):
					candidate_interview_history_data = frappe.get_doc("Candidate Interview", icd_cih.candidate_interview_id)
					it_consultant_data_candidate_interview_history.append(candidate_interview_history_data)
		#Get candidate Interview History
		for bcd_cih in it_consultant_data.background_check_history:
			if not bcd_cih.job_applicant_id:
				if frappe.get_all("Background Check", filters={"name": bcd_cih.background_check_id}):
					background_check_history_data = frappe.get_doc("Background Check", bcd_cih.background_check_id)
					it_consultant_data_background_check_history.append(background_check_history_data)
		#Get Skill Test History
		for bcd_sth in it_consultant_data.skill_test_history:
			if not bcd_sth.job_applicant_id:
				if frappe.get_all("Skill Test", filters={"name": bcd_sth.skill_test_id}):
					skill_test_history_data = frappe.get_doc("Skill Test", bcd_sth.skill_test_id)
					it_consultant_data_skill_test_history.append(skill_test_history_data)
		#Get Skill Test Coderbyte History
		for stc_cih in it_consultant_data.skill_test_coderbyte_history:
			if not stc_cih.job_applicant_id:
				if frappe.get_all("Skill Test Coderbyte", filters={"name": stc_cih.skill_test_coderbyte_id}):
					skill_test_coderbyte_history_data = frappe.get_doc("Skill Test Coderbyte", stc_cih.skill_test_coderbyte_id)
					it_consultant_data_skill_coderbyte_test_history.append(skill_test_coderbyte_history_data)
		#Get Persona Test History
		for pth_cih in it_consultant_data.persona_test_history:
			if not pth_cih.job_applicant_id:
				if frappe.get_all("Persona Test", filters={"name": pth_cih.persona_test_id}):
					persona_test_history_data = frappe.get_doc("Persona Test", pth_cih.persona_test_id)
					it_consultant_data_persona_test_history.append(persona_test_history_data)

		job_applicant_data = frappe.get_all("Job Applicant", filters={"it_consultant": it_consultant}, fields=['name'])
		if job_applicant_data:
			for job_applicant in job_applicant_data:
				#GET SELF EVALUATION HISTORY
				for icdsehr in it_consultant_data.self_evaluation_history:
					if str(icdsehr.job_applicant_id) in [str(job_applicant.name)]:
						if frappe.get_all("Self Evaluation", filters={"name": icdsehr.self_evaluation_id}):
							self_evaluation_data = frappe.get_doc("Self Evaluation", icdsehr.self_evaluation_id)
							it_consultant_data_self_evaluation_history.append(self_evaluation_data)

				#GET Skill Test HISTORY
				for icd_sth in it_consultant_data.skill_test_history:
					if str(icd_sth.job_applicant_id) in [str(job_applicant.name)]:
						if frappe.get_all("Skill Test", filters={"name": icd_sth.skill_test_id}):
							skill_test_data = frappe.get_doc("Skill Test", icd_sth.skill_test_id)
							it_consultant_data_skill_test_history.append(skill_test_data)

				#GET Skill Test Coderbyte HISTORY
				for icd_stch in it_consultant_data.skill_test_coderbyte_history:
					if str(icd_stch.job_applicant_id) in [str(job_applicant.name)]:
						if frappe.get_all("Skill Test Coderbyte", filters={"name": icd_stch.skill_test_coderbyte_id}):
							skill_test_coderbyte_data = frappe.get_doc("Skill Test Coderbyte", icd_stch.skill_test_coderbyte_id)
							it_consultant_data_skill_coderbyte_test_history.append(skill_test_coderbyte_data)

				#GET Persona Test History
				for icd_pth in it_consultant_data.persona_test_history:
					if str(icd_pth.job_applicant_id) in [str(job_applicant.name)]:
						if frappe.get_all("Persona Test", filters={"name": icd_pth.persona_test_id}):
							persona_test_history_data = frappe.get_doc("Persona Test", icd_pth.persona_test_id)
							it_consultant_data_persona_test_history.append(persona_test_history_data)

				#Get Background Check History
				for icd_bch in it_consultant_data.background_check_history:
					if str(icd_bch.job_applicant_id) in [str(job_applicant.name)]:
						if frappe.get_all("Background Check", filters={"name": icd_bch.background_check_id}):
							background_check_history_data = frappe.get_doc("Background Check", icd_bch.background_check_id)
							it_consultant_data_background_check_history.append(background_check_history_data)

				#Get Video Interview History
				for icd_vih in it_consultant_data.video_interview_history:
					if str(icd_vih.job_applicant_id) in [str(job_applicant.name)]:
						if frappe.get_all("Video Interview", filters={"name": icd_vih.video_interview_id}):
							video_interview_history_data = frappe.get_doc("Video Interview", icd_vih.video_interview_id)
							it_consultant_data_video_interview_history.append(video_interview_history_data)

				#Get candidate Interview History
				for icd_cih in it_consultant_data.candidate_interview_history:
					if str(icd_cih.job_applicant_id) in [str(job_applicant.name)]:
						if frappe.get_all("Candidate Interview", filters={"name": icd_cih.candidate_interview_id}):
							candidate_interview_history_data = frappe.get_doc("Candidate Interview", icd_cih.candidate_interview_id)
							it_consultant_data_candidate_interview_history.append(candidate_interview_history_data)

		result["self_evaluation_history"] = it_consultant_data_self_evaluation_history
		result["skill_test_history"] = it_consultant_data_skill_test_history
		result["skill_test_coderbyte_history"] = it_consultant_data_skill_coderbyte_test_history
		result["persona_test_history"] = it_consultant_data_persona_test_history
		result["background_check_history"] = it_consultant_data_background_check_history
		result["video_interview_history"] = it_consultant_data_video_interview_history
		result["candidate_interview_history"] = it_consultant_data_candidate_interview_history

	return result

@frappe.whitelist()
def get_applied_jobs(it_consultant):
	applied = []
	called_for_interview = []
	hired = []
	closed = []
	final_dict = {}

	jobs = frappe.db.sql("""SELECT JAH.job_applicant,JAH.job_opening,JAH.date_created,JO.*,LC.stages FROM `tabJob Applicant History` JAH 
		INNER JOIN `tabJob Opening` JO ON JAH.job_opening = JO.`name`
		INNER JOIN `tabLead Candidate` LC ON JAH.job_applicant = LC.generated_from_job_applicant
		WHERE JAH.parent = %s""",(it_consultant),as_dict=True)
	for j in jobs:
		if j.stages == 'Matched' or j.stages == 'Presented' or j.stages == 'Applied':
			applied.append(j)
		elif j.stages == 'Interviewing' or j.stages == 'Accepted By Client':
			called_for_interview.append(j)
		elif j.stages == 'Accepted By Candidate' or j.stages == 'Hired':
			hired.append(j)
		elif j.stages == 'Rejected':
			closed.append(j)

	return {"Applied":applied,"Called For Interviewing":called_for_interview,"Hired":hired,"Closed":closed}

#erpyoupal.it_service.doctype.it_consultant.it_consultant.repopulate_resume_field
@frappe.whitelist()
def repopulate_resume_field():
	it_consultants = frappe.get_all("IT Consultant", fields=["name", "resume"])
	for itc in it_consultants:
		if not itc.resume:
			jas = frappe.get_all("Job Applicant", filters={"email_id": itc.email_primary}, fields=["name", "resume_attachment"], order_by="creation desc")
			if jas:
				for ja in jas:
					frappe.db.set_value('IT Consultant', itc.name, 'resume', ja.resume_attachment, update_modified=False)
					frappe.db.commit()
					break

#erpyoupal.it_service.doctype.it_consultant.it_consultant.populate_records_view_field
@frappe.whitelist()
def populate_records_view_field():
	consultants = frappe.get_all("IT Consultant", fields=["name"])
	if consultants:
		for con in consultants:
			with_changes = 0
			doc = frappe.get_doc("IT Consultant", con.name)
			if doc.job_applicant_history:
				for row in doc.job_applicant_history:
					row.view = f"https://erp.youpal.se/app/job-applicant/{row.job_applicant}"
					with_changes = 1
			if with_changes:
				doc.flags.ignore_permissions = True
				doc.save()


#erpyoupal.it_service.doctype.it_consultant.it_consultant.resave_it_consultants
@frappe.whitelist()
def resave_it_consultants():
	consultants = frappe.get_all("IT Consultant", fields=["name"])
	if consultants:
		for con in consultants:
			doc = frappe.get_doc("IT Consultant", con.name)
			doc.flags.ignore_links = True
			doc.flags.ignore_permissions = True
			try:
				doc.save()
			except:
				pass

#erpyoupal.it_service.doctype.it_consultant.it_consultant.get_it_consultant_billing_details
@frappe.whitelist()
def get_it_consultant_billing_details(it_consultant):
	result = {}
	it_consultants = frappe.get_all("IT Consultant", filters={"name": it_consultant}, fields=["name", "email_primary"])
	if it_consultants:
		people_doc = frappe.get_all("People", filters={"name": it_consultants[0].name}, fields=["name"])
		if not people_doc:
			people_doc = frappe.get_all("People", filters={"email_address": it_consultants[0].email_primary}, fields=["name"])
		if people_doc:
			doc = frappe.get_doc("People", people_doc[0].name)
			result["billing_organization_name"] = doc.billing_organization_name
			result["billing_organization_address"] = doc.billing_organization_address
			result["billing_vat_number"] = doc.billing_vat_number
			result["billing_business_id"] = doc.billing_business_id
			result["billing_account_holder_name"] = doc.billing_account_holder_name
			result["billing_bank_name"] = doc.billing_bank_name
			result["billing_address"] = doc.billing_address
			result["billing_clearing_number"] = doc.billing_clearing_number
			result["billing_account_number"] = doc.billing_account_number
			result["billing_iban"] = doc.billing_iban
			result["billing_swift"] = doc.billing_swift
			result["billing_bic"] = doc.billing_bic
			result["billing_paypal"] = doc.billing_paypal
			result["billing_payoneer"] = doc.billing_payoneer
			result["billing_skrill"] = doc.billing_skrill
			result["billing_neteller"] = doc.billing_neteller
			result["billing_wise"] = doc.billing_wise
			result["default_payment_method"] = doc.default_payment_method
			return result
		else:
			frappe.throw("People document not found")
	else:
		frappe.throw("IT Consultant document not found")

#erpyoupal.it_service.doctype.it_consultant.it_consultant.update_it_consultant_billing_details
@frappe.whitelist()
def update_it_consultant_billing_details(it_consultant, entry):
	it_consultants = frappe.get_all("IT Consultant", filters={"name": it_consultant}, fields=["name", "email_primary"])
	if it_consultants:
		people_doc = frappe.get_all("People", filters={"name": it_consultants[0].name}, fields=["name"])
		if not people_doc:
			people_doc = frappe.get_all("People", filters={"email_address": it_consultants[0].email_primary}, fields=["name"])
		if people_doc:
			doc = frappe.get_doc("People", people_doc[0].name)
			doc.billing_organization_name = entry.get("billing_organization_name")
			doc.billing_organization_address = entry.get("billing_organization_address")
			doc.billing_vat_number = entry.get("billing_vat_number")
			doc.billing_business_id = entry.get("billing_business_id")
			doc.billing_account_holder_name = entry.get("billing_account_holder_name")
			doc.billing_bank_name = entry.get("billing_bank_name")
			doc.billing_address = entry.get("billing_address")
			doc.billing_clearing_number = entry.get("billing_clearing_number")
			doc.billing_account_number = entry.get("billing_account_number")
			doc.billing_iban = entry.get("billing_iban")
			doc.billing_swift = entry.get("billing_swift")
			doc.billing_bic = entry.get("billing_bic")
			doc.billing_paypal = entry.get("billing_paypal")
			doc.billing_payoneer = entry.get("billing_payoneer")
			doc.billing_skrill = entry.get("billing_skrill")
			doc.billing_neteller = entry.get("billing_neteller")
			doc.billing_wise = entry.get("billing_wise")
			doc.default_payment_method = entry.get("default_payment_method")
			doc.flags.ignore_permissions = True
			doc.flags.ignore_links = True
			return doc.save()
		else:
			frappe.throw("People document not found")
	else:
		frappe.throw("IT Consultant document not found")

#erpyoupal.it_service.doctype.it_consultant.it_consultant.create_it_consultant
@frappe.whitelist()
def create_it_consultant(entry):
	new_doc = frappe.new_doc("IT Consultant")
	new_doc.update(entry)
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	new_doc.insert()
