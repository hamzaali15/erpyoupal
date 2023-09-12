# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals

import json
import frappe
import math
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address, now, flt, getdate, get_datetime

from erpnext.hr.doctype.interview.interview import get_interviewers
from erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview import create_interview_availability
from erpyoupal.erpyoupal.doctype.background_check.background_check import create_video_interview
from erpyoupal.erpyoupal.doctype.year.year import validate_year

class DuplicationError(frappe.ValidationError): pass

class JobApplicant(Document):
	def onload(self):
		job_offer = frappe.get_all("Job Offer", filters={"job_applicant": self.name})
		if job_offer:
			self.get("__onload").job_offer = job_offer[0].name

	def autoname(self):
		keys = filter(None, (self.applicant_name, self.email_id, self.job_title))
		if not keys:
			frappe.throw(_("Name or Email is mandatory"), frappe.NameError)
		self.name = " - ".join(keys)

	def validate(self):
		self.get_fullname()
		self.get_job_opening()
		if self.email_id:
			validate_email_address(self.email_id, True)

		if self.employee_referral:
			self.set_status_for_employee_referral()

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split('@')[0]
			self.applicant_name = ' '.join([p.capitalize() for p in guess.split('.')])

		if not self.is_new():
			#if self.to_parse_resume and not frappe.db.get_value("Job Applicant", self.name, "to_parse_resume"):
			#	frappe.enqueue("erpyoupal.events.hr.job_applicant.get_parsedjson_file", document_name=self.name, new_document=0, queue='long', timeout=300, now=False)
			if not self.it_consultant and self.create_it_consultant and not frappe.db.get_value("Job Applicant", self.name, "create_it_consultant"):
				if not self.does_it_consultant_exists():
					pass
					#frappe.enqueue("erpyoupal.events.hr.job_applicant.create_it_consultant_from_parsed_file", document_name=self.name, queue='long', timeout=300, now=False)
				else:
					self.it_consultant = self.does_it_consultant_exists()
					if self.parse_resume_sovren and not frappe.db.get_value("Job Applicant", self.name, "parse_resume_sovren"):
						frappe.enqueue("erpnext.hr.doctype.resume_parsing.resume_parsing.create_resume_parsing", it_consultant=self.does_it_consultant_exists(), resume_file_url=self.resume_attachment, update_it_consultant=1, queue='long', timeout=300, now=False)
				frappe.enqueue("erpyoupal.events.hr.job_applicant.create_lead_candidate", document_name=self.name, candidate_source=self.get("candidate_source"), generated_by_partner=self.get("generated_by_partner"), queue='long', timeout=300, now=False)
		self.update_it_consultant()

	def after_insert(self):
		if self.job_title:
			frappe.enqueue("erpnext.hr.doctype.job_opening.job_opening.scheduled_get_job_opening_job_applicants_count", job_opening=self.job_title, queue='long', timeout=300, now=False)
			application_process = validate_application_process(job_applicant=self.name, job_opening=self.job_title)
			if application_process in ['default', 'skip_background_check']:
				create_self_evaluation(self.name)
			if application_process in ['assessment_first']:
				create_design_skill_tests(job_applicant=self.name)

		peoples = frappe.get_all("People", filters={"email_address": self.email_id}, fields=["name", "people_type"])
		if peoples:
			if peoples[0].people_type in ["Consultant", "Business / Consultant"]:
				create_interview_availability(job_applicant=self.name, from_application_process=application_process, disable_email_sending=1)
				create_video_interview(job_applicant=self.name, disable_email_sending=1)
		else:
			create_interview_availability(job_applicant=self.name, from_application_process=application_process, disable_email_sending=1)
			create_video_interview(job_applicant=self.name, disable_email_sending=1)
		self.create_people_document()
		#Parse Resume
		if not self.get("dont_parse"):
			if self.resume_attachment:
				self.db_set('to_parse_resume', 1)
				self.db_set('create_it_consultant', 1)
				frappe.db.commit()
				#frappe.enqueue("erpyoupal.events.hr.job_applicant.get_parsedjson_file", document_name=self.name, new_document=1, queue='long', timeout=300, now=False)
				if not self.does_it_consultant_exists():
					pass
					#frappe.enqueue("erpyoupal.events.hr.job_applicant.create_it_consultant_from_parsed_file", document_name=self.name, queue='long', timeout=300, now=False)
				else:
					self.db_set("it_consultant", self.does_it_consultant_exists())
					if self.parse_resume_sovren:
						frappe.enqueue("erpnext.hr.doctype.resume_parsing.resume_parsing.create_resume_parsing", it_consultant=self.does_it_consultant_exists(), resume_file_url=self.resume_attachment, update_it_consultant=1, queue='long', timeout=300, now=False)
		frappe.enqueue("erpyoupal.events.hr.job_applicant.create_lead_candidate", document_name=self.name, candidate_source=self.get("candidate_source"), generated_by_partner=self.get("generated_by_partner"), queue='long', timeout=300, now=False)
	
	def on_trash(self):
		self.update_job_opening_applicant_count(additional_count=-1)

	def get_job_opening(self):
		self.job_opening_code = frappe.db.get_value("Job Opening", self.job_title, "code")
		self.designation = frappe.db.get_value("Job Opening", self.job_title, "designation")
		self.sub_designation = frappe.db.get_value("Job Opening", self.job_title, "sub_designation")
	
	def get_fullname(self):
		self.full_name = self.applicant_name
		if self.last_name:
			self.full_name = self.applicant_name+" "+self.last_name
	
	def update_job_opening_applicant_count(self, additional_count=0):
		if self.job_title:
			if self.is_new():
				additional_count=1
			get_job_opening_job_applicants_count(job_opening=self.job_title, save_result=1, additional_count=additional_count)

	def does_it_consultant_exists(self):
		exists = frappe.get_all("IT Consultant", filters={"email_primary": self.email_id}, fields=["name"])
		if exists:
			return exists[0].name
		else:
			return False
	
	def create_people_document(self):
		doc = frappe.get_all("People", filters={"email_address": self.email_id}, fields=["name"])
		if doc:
			pass
		else:
			new_doc = frappe.new_doc("People")
			new_doc.flags.ignore_permissions = True
			new_doc.flags.ignore_links = True
			new_doc.people_type = "Consultant"
			new_doc.first_name = self.applicant_name
			new_doc.last_name = self.last_name
			new_doc.designation = self.designation
			new_doc.sub_designation = self.sub_designation
			new_doc.availability = self.availability
			new_doc.rate_hourly = self.rate
			new_doc.position_title = self.role
			new_doc.resume = self.resume_attachment
			new_doc.location = self.country
			new_doc.date_of_birth = self.date_of_birth
			new_doc.work_type = self.work_type
			if self.years_of_experience:
				years_of_experience = flt(self.years_of_experience)
				years_of_experience = math.ceil(years_of_experience)
				experience_since = flt(getdate(now()).year) - years_of_experience
				experience_since = math.ceil(experience_since)
				new_doc.experience_since = int(experience_since)
				new_doc.total_experience = years_of_experience
				if experience_since:
					validate_year(year=str(int(experience_since)))

			new_doc.status = "Active"
			new_doc.create_user = 1

			new_doc.append("email", {"email": self.email_id})
			new_doc.append("mobile", {"mobile": self.phone_number})
			new_doc.insert()

	def set_status_for_employee_referral(self):
		emp_ref = frappe.get_doc("Employee Referral", self.employee_referral)
		if self.status in ["Open", "Replied", "Hold"]:
			emp_ref.db_set("status", "In Process")
		elif self.status in ["Accepted", "Rejected"]:
			emp_ref.db_set("status", self.status)
	
	def create_it_consultant_from_parsed_json(self):
		frappe.enqueue("erpyoupal.events.hr.job_applicant.create_it_consultant_from_parsed_file", document_name=self.name, queue='long', timeout=300, now=False)
	
#	def create_skill_test(self):
#		if self.top_skill:
#			new_doc = frappe.new_doc('Skill Test')
#			new_doc.job_applicant = self.name
#			new_doc.applicant_name = self.applicant_name
#			new_doc.date_created = now()
#			new_doc.email = self.email_id
#			for skill in self.top_skill:
#				testgorilla_skill_test = frappe.get_value('Skill', skill.skill, 'testgorilla_skill_test')
#				if testgorilla_skill_test:
#					email_sent = 0
#					if self.email_id:
#						email_sent = 1
#
#					new_doc.append('test', {
#						'skill': skill.skill,
#						'test_title': skill.skill,
#						'test_link': testgorilla_skill_test,
#						'score': 0,
#						'status': 'invited',
#						'email_sent': email_sent 
#					})
#
#				new_doc.append('top_skills', {
#					'skill': skill.skill
#				})
#			new_doc.flags.ignore_permissions = True
#			new_doc.insert()

	def update_it_consultant(self):
		it_consultant = frappe.get_all("IT Consultant", filters={"email_primary": self.email_id}, fields=['name'])
		if it_consultant:
			it_consultant = frappe.get_doc("IT Consultant", it_consultant[0].name)

			if self.rate:
				it_consultant.rate_hourly = self.rate

			if self.role:
				it_consultant.position_title = self.role

			if self.resume_attachment:
				it_consultant.resume = self.resume_attachment
			
			if self.country:
				it_consultant.location = self.country
			
			if self.years_of_experience:
				years_of_experience = flt(self.years_of_experience)
				years_of_experience = math.ceil(years_of_experience)
				experience_since = flt(getdate(now()).year) - years_of_experience
				experience_since = math.ceil(experience_since)
				it_consultant.experience_since = int(experience_since)
				it_consultant.total_experience = years_of_experience
				if experience_since:
					validate_year(year=str(int(experience_since)))
			
			if self.date_of_birth:
				it_consultant.date_of_birth = self.date_of_birth
			
			if self.availability:
				it_consultant.availability = self.availability

			if self.skill:
				for self_skill in self.skill:
					existing_row = list(filter(lambda d: d.get('skill') in [self_skill.skill], it_consultant.skills))
					if not existing_row:
						it_consultant.append("skills", {"skill": self_skill.skill})

			if self.education:
				for self_education in self.education:
					edu_row = {
						"school_univ": self_education.get('school_univ'),
						"qualification": self_education.get('qualification'),
						"level": self_education.get('level'),
						"starting_year": self_education.get('starting_year'),
						"passing_year": self_education.get('passing_year'),
						"description": self_education.get('description')
					}
					existing_row = list(filter(lambda d: {
						"school_univ": d.get('school_univ'),
						"qualification": d.get('qualification'),
						"level": d.get('level'),
						"starting_year": d.get('starting_year'),
						"passing_year": d.get('passing_year'),
						"description": d.get('description')
					} == edu_row, it_consultant.degrees))
					if not existing_row:
						it_consultant.append("degrees", edu_row)

			if self.languages:
				for self_education in self.languages:
					lang_row = {
						"language": self_education.get('language'),
						"language_level": self_education.get('language_level')
					}
					existing_row = list(filter(lambda d: {
						"language": d.get('language'),
						"language_level": d.get('language_level')
					} == lang_row, it_consultant.language_proficiency_level))
					if not existing_row:
						it_consultant.append("language_proficiency_level", lang_row)

			if self.social_media:
				for self_social_media in self.social_media:
					social_media_row = {
						"platform_social_media": self_social_media.get('platform_social_media'),
						"link": self_social_media.get('link')
					}
					existing_row = list(filter(lambda d: {
						"platform_social_media": d.get('platform_social_media'),
						"link": d.get('link')
					} == social_media_row, it_consultant.platform_social_media))
					if not existing_row:
						it_consultant.append("platform_social_media", social_media_row)

			it_consultant.flags.ignore_permissions = True
			it_consultant.flags.ignore_linkse = True
			it_consultant.save()
	
	@frappe.whitelist()
	def go_to_it_consultant(self):
		it_consultants = frappe.get_all("IT Consultant", filters={"email_primary": self.email_id}, fields=["name"])
		if it_consultants:
			return it_consultants[0].name
		else:
			return None
	
	@frappe.whitelist()
	def go_to_people(self):
		peoples = frappe.get_all("People", filters={"email_address": self.email_id}, fields=["name"])
		if peoples:
			return peoples[0].name
		else:
			return None

@frappe.whitelist()
def get_job_opening_job_applicants_count(job_opening=None, all_document=0, save_result=0, additional_count=0):
	result = 0
	job_openings = []

	if all_document:
		job_openings = frappe.get_all("Job Opening", fields=['name'])
	else:
		job_openings = frappe.get_all("Job Opening", filters={"name": job_opening}, fields=['name'])
	
	if job_openings:
		for opening in job_openings:
			result = 0
			job_applicants = frappe.get_all("Job Applicant", filters={"job_title": opening.name}, fields=['name', 'status'])
			if job_applicants:
				result = len(job_applicants)
			result = result + additional_count
			if result < 0:
				result = 0
			if save_result:
				frappe.db.set_value("Job Opening", opening.name, 'job_applicants_count', result)

	return result

#erpyoupal.events.hr.job_applicant.get_parsedjson_file
@frappe.whitelist()
def get_parsedjson_file(document_name, new_document=0):
	if frappe.get_all("Job Applicant", filters={"name": document_name}):
		this_doc = frappe.get_doc("Job Applicant", document_name)
		this_doc.to_parse_resume = 1
		
		if this_doc.to_parse_resume and this_doc.resume_attachment:
			from erpyoupal.events.hr.job_applicant_api import get_parsed_file
			parse_file, date_parsed, confidence_level, parsed_file = get_parsed_file(
				is_new=new_document, 
				file_url=this_doc.resume_attachment,
				attached_to_name=this_doc.name,
				attached_to_field="resume_attachment", 
				attached_to_docType="Job Applicant"
			)
			if not confidence_level:
				confidence_level = 0
			frappe.db.set_value("Job Applicant", this_doc.name, 'confidence_level', confidence_level)
			frappe.db.set_value("Job Applicant", this_doc.name, 'parsed_json', parsed_file)
			frappe.db.set_value("Job Applicant", this_doc.name, 'last_date_parsed', date_parsed)
			frappe.db.set_value("Job Applicant", this_doc.name, 'to_parse_resume', parse_file)

#erpyoupal.events.hr.job_applicant.create_it_consultant_from_parsed_file
@frappe.whitelist()
def create_it_consultant_from_parsed_file(document_name):
	if frappe.get_all("Job Applicant", filters={"name": document_name}):
		this_doc = frappe.get_doc("Job Applicant", document_name)
		if this_doc.parsed_json and not this_doc.it_consultant:
			new_it_consultant_entry = {
				"job_applicant": this_doc.name,
				"job_opening": this_doc.job_title,
				"job_applicant_creation": this_doc.creation,
				"job_applicant_status": this_doc.status,
				"first_name": this_doc.applicant_name,
				"last_name": this_doc.last_name,
				"mobile_primary": this_doc.phone_number,
				"email_primary": this_doc.email_id,
				"total_experience": None,
				"rate_hourly": this_doc.rate,
				"verification": "Applicant",
				"resume": this_doc.resume_attachment,
				"skills": [],
				"location": this_doc.country,
				"rate": this_doc.rate
			}
			parsed_json_obj = json.loads(this_doc.parsed_json)
			#new_it_consultant_entry["first_name"] = parsed_json_obj.get('name')
			#new_it_consultant_entry["email_primary"] = parsed_json_obj.get('email')
			new_it_consultant_entry["total_experience"] = parsed_json_obj.get('total_experience')
			new_it_consultant_entry["skills"] = parsed_json_obj.get('skills')
			if this_doc.skill:
				if not new_it_consultant_entry["skills"]:
					new_it_consultant_entry["skills"] = []
				for sk in this_doc.skill:
					new_it_consultant_entry["skills"].append(sk.skill)
			try:
				if new_it_consultant_entry["skills"]:
					validate_skills(new_it_consultant_entry["skills"])
				new_it_consultant_doc = create_new_it_consultant_document(new_it_consultant_entry)
				if new_it_consultant_doc:
					frappe.db.set_value("Job Applicant", this_doc.name, 'it_consultant', new_it_consultant_doc)
					frappe.db.set_value("Job Applicant", this_doc.name, 'create_it_consultant', 1)
			except Exception as e:
				frappe.db.set_value("Job Applicant", this_doc.name, 'create_it_consultant', 0)
				#raise Exception(e)

@frappe.whitelist(allow_guest=True)
def validate_application_process(job_applicant, job_opening=None):
	result = "default"
	if not job_opening:
		job_opening = frappe.db.get_value("Job Applicant", job_applicant, "job_title")

	skip_background_checking = frappe.db.get_value("Job Opening", job_opening, "skip_background_checking")
	if skip_background_checking:
		result = "skip_background_check"

	if job_opening and str(job_opening) in ['ux-ui-designer']:
		result = "assessment_first"

	return result

@frappe.whitelist()
def create_interview(doc, interview_round):
	import json

	from six import string_types

	if isinstance(doc, string_types):
		doc = json.loads(doc)
		doc = frappe.get_doc(doc)

	round_designation = frappe.db.get_value("Interview Round", interview_round, "designation")

	if round_designation and doc.designation and round_designation != doc.designation:
		frappe.throw(_("Interview Round {0} is only applicable for the Designation {1}").format(interview_round, round_designation))

	interview = frappe.new_doc("Interview")
	interview.interview_round = interview_round
	interview.job_applicant = doc.name
	interview.designation = doc.designation
	interview.resume_link = doc.resume_link
	interview.job_opening = doc.job_title
	interviewer_detail = get_interviewers(interview_round)

	for d in interviewer_detail:
		interview.append("interview_details", {
			"interviewer": d.interviewer
		})
	return interview

@frappe.whitelist()
def get_interview_details(job_applicant):
	interview_details = frappe.db.get_all("Interview",
		filters={"job_applicant":job_applicant, "docstatus": ["!=", 2]},
		fields=["name", "interview_round", "expected_average_rating", "average_rating", "status"]
	)
	interview_detail_map = {}

	for detail in interview_details:
		interview_detail_map[detail.name] = detail

	return interview_detail_map

@frappe.whitelist()
def validate_skills(skill_list, parsed_from_sovren=0):
	if skill_list:
		for skill in skill_list:
			if len(skill) < 140:
				if not frappe.get_all("Skill", filters={'name': skill}):
					new_skill = frappe.new_doc("Skill")
					new_skill.skill_name = skill
					new_skill.parsed_from_sovren = parsed_from_sovren
					new_skill.flags.ignore_permissions = True
					new_skill.flags.ignore_links = True
					new_skill.insert()

@frappe.whitelist()
def create_new_it_consultant_document(entry):
	doc = None
	existing_it_consultants = frappe.get_all("IT Consultant", filters={"email_primary": entry.get("email_primary")}, fields=['name'])
	if existing_it_consultants:
		doc = frappe.get_doc("IT Consultant", existing_it_consultants[0].name)
	else:
		doc = frappe.new_doc("IT Consultant")

	if doc:
		doc.update({
			"it_consultant_name": entry.get('it_consultant_name'),
			"first_name": entry.get('first_name'),
			"last_name": entry.get("last_name"),
			"mobile_primary": entry.get("mobile_primary"),
			"email_primary": entry.get("email_primary"),
			"total_experience": entry.get("total_experience"),
			"rate_hourly": entry.get("rate"),
			"verification": entry.get("verification"),
			"resume": entry.get("resume"),
			"location": entry.get("location")
			})
		#doc.append('job_applicant_history', {
		#	"job_applicant": entry.get("job_applicant"),
		#	"job_opening": entry.get("job_opening"),
		#	"date_created": entry.get("job_applicant_creation"),
		#	"rate": entry.get("rate")
		#	})
		if entry.get("skills"):
			for skill in entry.get("skills"):
				if len(skill) < 140:
					doc.append('skills', {
						"skill": skill
						})
		doc.flags.ignore_permissions = True
		doc.flags.ignore_links = True
		if existing_it_consultants:
			if doc.save():
				return doc.name
		else:
			if doc.insert():
				return doc.name

@frappe.whitelist()
def fill_parsedjson_confidence_level():
	job_applicants = frappe.get_all("Job Applicant", fields=["name", "parsed_json"])
	for applicant in job_applicants:
		if applicant.parsed_json:
			parsed_json_obj = json.loads(applicant.parsed_json)
			frappe.db.set_value("Job Applicant", applicant.name, 'confidence_level', parsed_json_obj.get("confidence"))

@frappe.whitelist()
def create_new_job_applicant_document(entry):
	new_doc = frappe.new_doc("Job Applicant")
	new_doc.dont_parse = entry.get("dont_parse")
	new_doc.applicant_name = entry.get("first_name")
	new_doc.last_name = entry.get("last_name")
	new_doc.phone_number = entry.get("mobile_primary")
	new_doc.email_id = entry.get("email_primary")
	new_doc.hourly_rate = entry.get("rate_hourly")
	new_doc.resume_attachment = entry.get("resume_attachment")
	new_doc.to_parse_resume = entry.get("to_parse_resume")
	new_doc.last_date_parsed = entry.get("last_date_parsed")
	new_doc.parsed_json = entry.get("parsed_json")
	new_doc.confidence_level = entry.get("confidence_level")
	if entry.get("skills"):
		for skill in entry.get("skills"):
			if len(skill) < 140:
				new_doc.append('skill', {
					"skill": skill
				})
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	new_doc.flags.ignore_mandatory = True
	if new_doc.insert():
		return new_doc.name

#erpyoupal.events.hr.job_applicant.create_lead_candidate
@frappe.whitelist()
def create_lead_candidate(document_name, candidate_source="Public Job Board", generated_by_partner=None, from_lead_custom=None):
	if frappe.get_all("Job Applicant", filters={'name': document_name}):
		from_lead_custom =None
		job_app = frappe.get_doc("Job Applicant", document_name)
		if not from_lead_custom:
			from_lead_custom = frappe.db.get_value("Job Opening", job_app.job_title, "from_lead_custom")
		if from_lead_custom:
			it_consultant = None
			it_consultants = frappe.get_all("IT Consultant", filters={"email_primary": job_app.email_id}, fields=["name"])
			if it_consultants:
				it_consultant = it_consultants[0].name
			if it_consultant:
				new_doc = frappe.new_doc("Lead Candidate")
				new_doc.generated_from_lead = from_lead_custom
				new_doc.generated_from_job_opening = job_app.job_title
				new_doc.generated_from_job_applicant = document_name
				#new_doc.generated_by = None
				new_doc.generated_by_partner = generated_by_partner
				new_doc.candidate_source = candidate_source
				new_doc.stages = "Applied"
				new_doc.candidate_is_saved = 0
				new_doc.linked_job_applicant = document_name
				new_doc.append('candidate', {
					"it_consultant": it_consultant,
					"rate": job_app.rate
					#"hours": None,
					#"consultant_sub_total": None,
					#"client_rate": None,
					#"client_sub_total": None,
					#"gross_margin": None,
					#"check_dailyrate": None,
					#"define_day": None,
					#"daily_rate": None,
					#"check_monthlyrate": None,
					#"define_month": None,
					#"monthly_rate": None,
					#"set_utilization": None,
				})
				new_doc.flags.ignore_permissions = True
				new_doc.flags.ignore_links = True
				new_doc.insert()
				frappe.db.commit()

#erpyoupal.events.hr.job_applicant.create_self_evaluation
@frappe.whitelist()
def create_self_evaluation(job_applicant, from_application_process=None):
	to_continue = 1
	job_opening = frappe.db.get_value('Job Applicant',job_applicant,'job_title')
	
	designation = frappe.db.get_value('Job Opening',job_opening,'designation')
	default_question = frappe.db.sql("""SELECT question,question_type,choices FROM `tabDefault Questions`""",as_dict=True)
	parent_designation_question = frappe.db.sql("""SELECT question,question_type,choices FROM `tabDesignation Questions` WHERE parent = %s""",(designation),as_dict=True)
	questions = default_question + parent_designation_question

	sub_designation = frappe.db.get_value('Job Opening',job_opening,'sub_designation')
	if sub_designation:
		sub_designation_question = frappe.db.sql("""SELECT question,question_type,choices,progressive_question FROM `tabDesignation Questions` WHERE parent = %s""",(sub_designation),as_dict=True)
		questions = default_question + sub_designation_question
	
	eval_filters = {"job_applicant": job_applicant}
	if from_application_process:
		eval_filters["from_application_process"] = from_application_process
	if frappe.get_all("Self Evaluation", filters=eval_filters):
		to_continue = 0

	if to_continue:
		new_doc = frappe.new_doc("Self Evaluation")
		new_doc.job_applicant = job_applicant
		if from_application_process:
			new_doc.from_application_process = from_application_process
		for question in questions:
			if question.question_type == "Progressive Question":
				choices = question.progressive_question
			else:
				choices = question.choices
			new_doc.append('questions', {
				'question': question.question,
				'question_type':question.question_type,
				'choices':choices
			})
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.save()

		email = frappe.get_value("Job Applicant",job_applicant,"email_id")
		applicant_name = frappe.get_value("Job Applicant",job_applicant,"applicant_name")
		frappe.sendmail(recipients=email,subject="Start Self Evaluation",message= """
		<style>
		table, td, div, h1, p {font-family: Arial, sans-serif;}
		button {background-color:#FF851A;border-radius: 12px;border: none;padding: 14px 40px;font-size: 15px;font-weight: bold;color: white;}
		button:hover {background-color: #FFA95E;}
		.card {
		/* Add shadows to create the "card" effect */
		box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
		transition: 0.3s;
		}
		</style>
		<div style="width:100%;margin:0;padding:0;text-align: center;background-color: #FCFCFD;">
		<br>
		<br>
		<div class="card" style="width:602px;margin: auto;background-color: FFFFFF;">
		<br><br>
		<h4>Welcome to the Youpal Group Application Proccess!</h4>
		<br>
		<h4>Hey, """+applicant_name+"""</h4>
		<p>We are the global network of top developers, design and</p>
		<p>bussiness exprerts. With Youpal Group, you'll build an amazing</p>
		<p>career, wherever you live</p>
		<br>
		<a href="https://jobs.youpalgroup.com/evaluation/"""+new_doc.name+"""" target="_blank"><button type="button">Continue</button></a>
		<br>
		<br>
		<br>
		<br>
		<br>
		<br>
		<br>
		<br>
		<h4>Thank you</h4>
		<h4>Youpal Group</h4>
		<br><br>
		</div>
		<p>@ 2022 YouPal Group</p>
		<p>Alströmergatan 36, 112 47 Stockholm, Sweden</p>
		<p><a href="https://youpalgroup.com/privacy-policy/">Privacy Policy</a>&emsp;&emsp;&emsp;<a href="https://youpalgroup.com/contact-us/">Help Center</a></p>
		</div>
		""")

@frappe.whitelist()
def create_design_skill_tests(job_applicant):
	new_doc = frappe.new_doc("Skill Test")
	new_doc.job_applicant = job_applicant
	new_doc.assessment_title = 'Design'
	new_doc.assessment_id = '351749'
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	new_doc.insert()

#erpyoupal.events.hr.job_applicant.verify_job_application_email
@frappe.whitelist(allow_guest=True)
def verify_job_application_email(email):
	result = 'No job application found'
	existing_doc = frappe.get_all("Job Applicant", filters={"email_id": email}, fields=["name"])
	if existing_doc:
		result = str(len(existing_doc))+" job application(s) found"
	return result

#erpyoupal.events.hr.job_applicant.verify_candidate_access
@frappe.whitelist(allow_guest=True)
def verify_candidate_access(email):
	result = 'No Access'
	existing_doc = frappe.get_all("IT Consultant", filters={"email_primary": email}, fields=["name", "talent_app_access"])
	if existing_doc:
		result = 'Jobs Board Access'
		if existing_doc[0].talent_app_access:
			result = 'Talent App Access'
	return result

#erpyoupal.events.hr.job_applicant.jobs_board_create_application
@frappe.whitelist(allow_guest=True)
def jobs_board_create_application(data):
	new_doc = frappe.new_doc("Job Applicant")
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	for data_key in data:
		if data_key not in ["skill", "languages", "social_media"]:
			new_doc.update({data_key: data[data_key]})
		else:
			for data_row in data[data_key]:
				new_doc.append(data_key, data_row)
				
	new_doc.insert()
	job_applicant = frappe.db.get_value("Job Applicant",{"email_id":new_doc.email_id},"name")
	self_evaluation = frappe.db.get_value("Self Evaluation",{"job_applicant":job_applicant},"name")
	return self_evaluation

#erpyoupal.events.hr.job_applicant.partner_portal_apply_job
@frappe.whitelist(allow_guest=True)
def partner_portal_apply_job(data):
	result = "Error, please try again"
	if not data.get("email_id"):
		frappe.throw("Incomplete data passed")
	if not data.get("job_title"):
		frappe.throw("Incomplete data passed")
	if not data.get("cover_letter"):
		frappe.throw("Incomplete data passed")
	if not data.get("hourly_rate"):
		frappe.throw("Incomplete data passed")
	if not data.get("partner"):
		frappe.throw("Incomplete data passed")

	it_consultant = frappe.get_all("IT Consultant", filters={"email_primary": data.get("email_id")}, fields=["name"])
	if it_consultant:
		it_consultant_data = frappe.get_doc("IT Consultant", it_consultant[0].name)
		new_doc = frappe.new_doc("Job Applicant")
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.applicant_name = it_consultant_data.get("first_name")
		new_doc.last_name = it_consultant_data.get("last_name")
		new_doc.email_id = it_consultant_data.get("email_primary")
		new_doc.phone_number = it_consultant_data.get("mobile_primary") if it_consultant_data.get("mobile_primary") else 0000
		new_doc.country = it_consultant_data.get("location")
		new_doc.date_of_birth = it_consultant_data.get("date_of_birth")
		new_doc.hourly_rate = data.get("hourly_rate")
		new_doc.job_title = data.get("job_title")
		new_doc.role = it_consultant_data.get("role")
		new_doc.years_of_experience = it_consultant_data.get("experience_since")
		new_doc.work_type = it_consultant_data.get("work_type")
		new_doc.seniority = it_consultant_data.get("seniority")
		new_doc.cover_letter = data.get("cover_letter")
		new_doc.availability = it_consultant_data.get("availability")
		new_doc.status = "Open"
		new_doc.candidate_source = "Partner's Portal"
		new_doc.generated_by_partner = data.get("partner")
		result = new_doc.insert()
	else:
		frappe.throw("Email not found")

	return result

#erpyoupal.events.hr.job_applicant.recreate_job_applicant
@frappe.whitelist(allow_guest=True)
def recreate_job_applicant(email_id, hourly_rate, job_title, cover_letter=None, resume_attachment=None, applicant_name=None, phone_number=None, country=None, status=None):
	data = None
	status = None

	it_consultants = frappe.get_all("IT Consultant", filters={"email_primary": email_id}, fields=["name"])
	if it_consultants:
		it_consultant = frappe.get_doc("IT Consultant", it_consultants[0].name)
		new_doc = frappe.new_doc("Job Applicant")
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.applicant_name = applicant_name if applicant_name else it_consultant.full_name
		new_doc.email_id = email_id
		new_doc.cover_letter = cover_letter
		new_doc.phone_number = phone_number if phone_number else it_consultant.mobile_primary
		new_doc.country = country if country else it_consultant.location
		new_doc.hourly_rate = hourly_rate
		new_doc.job_title = job_title
		new_doc.status = status if status else "Open"
		new_doc.resume_attachment = resume_attachment if resume_attachment else it_consultant.resume
		if not new_doc.resume_attachment:
			pass
			#frappe.throw(_("Resume not found"))
		if not new_doc.phone_number:
			frappe.throw(_("Failed. User has no mobile phone number"))
		data = new_doc.insert()
		status = "success"
		frappe.msgprint(_("Job Application created"))
		frappe.enqueue("erpyoupal.events.hr.job_applicant.resave_itconsultant", document_name=it_consultants[0].name, queue='long', timeout=300, now=False)
	else:
		frappe.throw(_("This email has no job application record yet"))

	frappe.local.response.update({"data": data})

#erpyoupal.events.hr.job_applicant.resave_itconsultant
@frappe.whitelist(allow_guest=True)
def resave_itconsultant(document_name):
	if frappe.get_all('IT Consultant', filters={'name': document_name}, fields=['name']):
		it_consultant = frappe.get_doc("IT Consultant", document_name)
		it_consultant.flags.ignore_links = True
		it_consultant.flags.ignore_permissions = True
		it_consultant.save()

#erpyoupal.events.hr.job_applicant.get_all_location
@frappe.whitelist(allow_guest=True)
def get_all_location():
	return_list = []
	designation = frappe.db.sql("""SELECT `name` FROM `tabLocation`""",as_dict=True)
	for d in designation:
		return_list.append(d.name)
	return return_list

#erpyoupal.events.hr.job_applicant.get_all_designation
@frappe.whitelist(allow_guest=True)
def get_all_designation():
	return_list = []
	designation = frappe.db.sql("""SELECT `name` FROM `tabDesignation`""",as_dict=True)
	for d in designation:
		return_list.append(d.name)
	return return_list

#erpyoupal.events.hr.job_applicant.get_all_skill
@frappe.whitelist(allow_guest=True)
def get_all_skill():
	return frappe.db.get_list('Skill', pluck='name')

#erpyoupal.events.hr.job_applicant.get_all_job_title
@frappe.whitelist(allow_guest=True)
def get_all_job_title():
	return frappe.db.get_list('Job Opening', pluck='job_title')

#erpyoupal.events.hr.job_applicant.get_all_popular_searches
@frappe.whitelist(allow_guest=True)
def get_all_popular_searches():
	return "Ongoing"


#erpyoupal.events.hr.job_applicant.patch_populate_fullname_field
@frappe.whitelist()
def patch_populate_fullname_field():
	jas = frappe.get_all("Job Applicant", fields=["name"])
	for ja in jas:
		doc = frappe.get_doc("Job Applicant", ja.name)
		doc.flags.update_modified = False
		doc.run_method('get_fullname')

#erpyoupal.events.hr.job_applicant.patch_lead_candidate_without_it_consultant
@frappe.whitelist()
def patch_lead_candidate_without_it_consultant():
	jas = frappe.get_all("Job Applicant", fields=["name"])
	for ja in jas:
		doc = frappe.get_doc("Job Applicant", ja.name)

		it_consultant = None
		it_consultants = frappe.get_all("IT Consultant", filters={"email_primary": doc.email_id}, fields=["name"])
		if it_consultants:
			it_consultant = it_consultants[0].name

		if doc.job_title and it_consultant:
			from_lead_custom = frappe.db.get_value('Job Opening', doc.job_title, 'from_lead_custom')
			if from_lead_custom:
				if not frappe.get_all("Lead Candidate", filters={"it_consultant": it_consultant, "generated_from_lead": from_lead_custom, "generated_from_job_opening": doc.job_title, "candidate_source": "Public Job Board"}, fields=["name"]):
					try:
						create_lead_candidate(doc.name)
					except:
						pass

#erpyoupal.events.hr.job_applicant.patch_job_applicant_without_designation
@frappe.whitelist()
def patch_job_applicant_without_designation():
	jas = frappe.get_all("Job Applicant", fields=["name", "job_title", "designation"])
	for ja in jas:
		if not ja.designation:
			new_designation = frappe.db.get_value("Job Opening", ja.job_title, "designation")
			if new_designation:
				frappe.db.set_value("Job Applicant", ja.name, 'designation', new_designation, update_modified=False)
				frappe.db.commit()

#erpyoupal.events.hr.job_applicant.resave_job_applicants
@frappe.whitelist()
def resave_job_applicants(document_name=None):
	jas = None
	if document_name:
		jas = frappe.get_all("Job Applicant", filters={"name": document_name}, fields=["name"])
	else:
		jas = frappe.get_all("Job Applicant", fields=["name"])
	if jas:
		for ja in jas:
			doc = frappe.get_doc("Job Applicant", ja.name)
			doc.flags.ignore_permissions = True
			doc.flags.ignore_links = True
			doc.save()

#erpyoupal.events.hr.job_applicant.load_applicant_scores
@frappe.whitelist()
def load_applicant_scores(job_applicant):
	result = {
		'self_evaluation_list': [],
		'skill_test_list': [],
		'skill_test_coderbyte_list': [],
		'persona_test_list': [],
		'video_interview_list': []
	}
	
	self_evaluation_list = frappe.get_all("Self Evaluation", filters={'job_applicant': job_applicant}, fields=['name', 'status', 'creation'])
	if self_evaluation_list:
		for row_self_evaluation_list in self_evaluation_list:
			result['self_evaluation_list'].append({
				"name": row_self_evaluation_list.name,
				"status": row_self_evaluation_list.status,
				"creation": get_datetime(row_self_evaluation_list.creation) if row_self_evaluation_list.creation else None,
			})
	
	skill_test_list = frappe.get_all("Skill Test", filters={'job_applicant': job_applicant}, fields=['name', 'test_status', 'creation', 'assessment_title', 'average_score'])
	if skill_test_list:
		for row_skill_test_list in skill_test_list:
			result['skill_test_list'].append({
				"name": row_skill_test_list.name,
				"assessment_title": row_skill_test_list.assessment_title,
				"status": row_skill_test_list.test_status,
				"average_score": row_skill_test_list.average_score,
				"creation": get_datetime(row_skill_test_list.creation) if row_skill_test_list.creation else None,
			})
	
	skill_test_coderbyte_list = frappe.get_all("Skill Test Coderbyte", filters={'job_applicant': job_applicant}, fields=['name', 'assessment_title', 'creation', 'assessment_link', 'email'])
	if skill_test_coderbyte_list:
		for row_skill_test_coderbyte_list in skill_test_coderbyte_list:
			final_score = None
			if row_skill_test_coderbyte_list.assessment_link and row_skill_test_coderbyte_list.email:
				result_link_key = str(row_skill_test_coderbyte_list.assessment_link)
				result_link_key = result_link_key.strip("https://coderbyte.com/sl-candidate?promo=youpalab-lmhum:")
				result_link_key = '%'+result_link_key+'%'
				coderbyte_result = frappe.get_all("Coderbyte Result", filters=[['assessment_link', 'like', result_link_key], ['email', '=', row_skill_test_coderbyte_list.email]], fields=['name', 'final_score'])
				if coderbyte_result:
					final_score = coderbyte_result[0].final_score
			result['skill_test_coderbyte_list'].append({
				"name": row_skill_test_coderbyte_list.name,
				"assessment_title": row_skill_test_coderbyte_list.assessment_title,
				"score": final_score,
				"creation": get_datetime(row_skill_test_coderbyte_list.creation) if row_skill_test_coderbyte_list.creation else None,
			})
	
	persona_test_list = frappe.get_all("Persona Test", filters={'job_applicant': job_applicant}, fields=['name', 'score', 'creation', 'test_status'])
	if persona_test_list:
		for row_persona_test_list in persona_test_list:
			result['persona_test_list'].append({
				"name": row_persona_test_list.name,
				"status": row_persona_test_list.test_status,
				"score": row_persona_test_list.score,
				"creation": get_datetime(row_persona_test_list.creation) if row_persona_test_list.creation else None,
			})
	
	video_interview_list = frappe.get_all("Video Interview", filters={'job_applicant': job_applicant}, fields=['name', 'status', 'creation'])
	if video_interview_list:
		for row_video_interview_list in video_interview_list:
			result['video_interview_list'].append({
				"name": row_video_interview_list.name,
				"status": row_video_interview_list.status,
				"creation": get_datetime(row_video_interview_list.creation) if row_video_interview_list.creation else None,
			})
	
	return result
