# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import base64
import json
import requests
import math
from frappe import _
from requests.structures import CaseInsensitiveDict
from frappe.model.document import Document
from frappe.utils import get_site_name, getdate, now, flt
from erpyoupal.erpyoupal.doctype.resume_parsing.sovern_api import resume_parser
from erpyoupal.events.hr.job_applicant import validate_skills


class ResumeParsing(Document):
	def validate(self):
		self.parsed_data = None
		self.validate_usage()
		if self.unparsed_resume and str(self.parsing_usage_log) == "Parsing allowed":
			self.parse_resume_file()
	
	def validate_usage(self):
		self.parsing_usage_log = "Parsing allowed"
		if self.it_consultant:
			self.parsing_usage_log = validate_resume_parsing_usage(it_consultant=self.it_consultant, portal=self.requested_from_portal)
	
	def update_it_consultant_data(self):
		entry = {
			"info": eval(str(self.info)),
			"resume_data": eval(str(self.resume_data)),
			"contact_information": eval(str(self.contact_information)),
			"personal_attributes": eval(str(self.personal_attributes)),
			"education": eval(str(self.education)),
			"employment_history": eval(str(self.employment_history)),
			"skills_data": eval(str(self.skills_data)),
			"skills": eval(str(self.skills)),
			"certifications": eval(str(self.certifications)),
			"licenses": eval(str(self.licenses)),
			"associations": eval(str(self.associations)),
			"language_competencies": eval(str(self.language_competencies)),
			"military_experience": eval(str(self.military_experience)),
			"security_credentials": eval(str(self.security_credentials)),
			"references": eval(str(self.references)),
			"achievements": eval(str(self.achievements)),
			"training": eval(str(self.training)),
			"resume_metadata": eval(str(self.resume_metadata)),
			"user_defined_tags": eval(str(self.user_defined_tags)),
		}
		update_it_consultant_from_parsed_data(entry)

	def convert_unparsed_file_to_base64(self):
		unparsed_resume_base64 = None
		file_path = None
		if not "/public" in str(self.unparsed_resume) and not "/private" in str(self.unparsed_resume):
			file_path = "./erp.youpalgroup.se/public"+str(self.unparsed_resume)
		else:
			file_path = "./erp.youpalgroup.se"+str(self.unparsed_resume)
		
		if file_path:
			with open(file_path, "rb") as pdf_file:
				my_string = base64.b64encode(pdf_file.read())
				unparsed_resume_base64 = my_string.decode("utf-8")

		return unparsed_resume_base64

	def parse_resume_file(self):
		self.info = None
		self.resume_data = None
		self.contact_information = None
		self.personal_attributes = None
		self.education = None
		self.employment_history = None
		self.skills_data = None
		self.skills = None
		self.certifications = None
		self.licenses = None
		self.associations = None
		self.language_competencies = None
		self.military_experience = None
		self.security_credentials = None
		self.references = None
		self.achievements = None
		self.training = None
		self.resume_metadata = None
		self.user_defined_tags = None

		unparsed_resume_base64 = self.convert_unparsed_file_to_base64()
		if unparsed_resume_base64:
			result_resume_parser = resume_parser(unparsed_resume_base64=unparsed_resume_base64)
			result_resume_parser["resume_fileurl"] = self.unparsed_resume
			self.info = str(result_resume_parser.get("info"))
			self.resume_data = str(result_resume_parser.get("resume_data"))
			self.contact_information = str(result_resume_parser.get("contact_information"))
			self.personal_attributes = str(result_resume_parser.get("personal_attributes"))
			self.education = str(result_resume_parser.get("education"))
			self.employment_history = str(result_resume_parser.get("employment_history"))
			self.skills_data = str(result_resume_parser.get("skills_data"))
			self.skills = str(result_resume_parser.get("skills"))
			self.certifications = str(result_resume_parser.get("certifications"))
			self.licenses = str(result_resume_parser.get("licenses"))
			self.associations = str(result_resume_parser.get("associations"))
			self.language_competencies = str(result_resume_parser.get("language_competencies"))
			self.military_experience = str(result_resume_parser.get("military_experience"))
			self.security_credentials = str(result_resume_parser.get("security_credentials"))
			self.references = str(result_resume_parser.get("references"))
			self.achievements = str(result_resume_parser.get("achievements"))
			self.training = str(result_resume_parser.get("training"))
			self.resume_metadata = str(result_resume_parser.get("resume_metadata"))
			self.user_defined_tags = str(result_resume_parser.get("user_defined_tags"))
			self.parsed_data = collect_parsed_data(entry=result_resume_parser)
			if self.it_consultant and self.update_it_consultant:
				result_resume_parser["email_primary"] = frappe.db.get_value("IT Consultant", self.it_consultant, "email_primary")
				update_it_consultant_from_parsed_data(it_consultant=self.it_consultant, entry=result_resume_parser)

#erpyoupal.erpyoupal.doctype.resume_parsing.resume_parsing.validate_resume_parsing_usage
@frappe.whitelist()
def validate_resume_parsing_usage(it_consultant, portal=None):
	portal_usage_limit_per_month = {
		"Talent": 2,
		"Partner": 10,
		"Client": 0
	}
	usage_allowed = 0
	if portal and portal in portal_usage_limit_per_month:
		doc_lists = frappe.db.sql("""SELECT `name`, `it_consultant` FROM `tabResume Parsing` 
			WHERE `it_consultant`='"""+it_consultant+"""' AND DATE_FORMAT(`creation`,'%Y%m') """, as_dict=1)
		if doc_lists:
			if len(doc_lists) >= portal_usage_limit_per_month[portal]:
				usage_allowed = 0
			else:
				usage_allowed = 1
		else:
			usage_allowed = 1
	else:
		usage_allowed = 1
	
	if not usage_allowed:
		return "Parsing blocked. Maximum usage reached"
	else:
		return "Parsing allowed"

@frappe.whitelist()
def collect_parsed_data(entry):
	doc = {}
	doc['resume'] = entry.get("resume_fileurl")
	if "contact_information" in entry and "CandidateName" in entry["contact_information"]:
		doc['first_name'] = entry["contact_information"]["CandidateName"]["GivenName"]

	if "contact_information" in entry and "CandidateName" in entry["contact_information"]:
		doc['last_name'] = entry["contact_information"]["CandidateName"]["FamilyName"]

	if "contact_information" in entry and "Telephones" in entry["contact_information"]:
		if entry["contact_information"]["Telephones"]:
			doc['mobile_primary'] = entry["contact_information"]["Telephones"][0]["Normalized"]

	if 'email_primary' in entry:
		if "contact_information" in entry and "EmailAddresses" in entry["contact_information"]:
			if entry["contact_information"]["EmailAddresses"]:
				for row in entry["contact_information"]["EmailAddresses"]:
						if str(row) != str(entry['email_primary']):
							doc['email_secondary'] = row
							break

	if "contact_information" in entry and "CountryCode" in entry["contact_information"]:
		country_doc = frappe.get_all("Country", filters={"code": entry["contact_information"]["CountryCode"]}, fields=["name"])
		if country_doc:
			doc['location'] = country_doc.name

	if "contact_information" in entry and "Location" in entry["contact_information"] and "StreetAddressLines" in entry["contact_information"]["Location"] and entry["contact_information"]["Location"]["StreetAddressLines"]:
		doc['address'] = entry["contact_information"]["Location"]["StreetAddressLines"][0]

	if "personal_attributes" in entry and "DateOfBirth" in entry["personal_attributes"] and entry["personal_attributes"]["DateOfBirth"]["Date"]:
		doc['date_of_birth'] = entry["personal_attributes"]["DateOfBirth"]["Date"]

	if "personal_attributes" in entry and "Gender" in entry["personal_attributes"]:
		doc['gender'] = entry["personal_attributes"]["Gender"]

	if "personal_attributes" in entry and "PassportNumber" in entry["personal_attributes"]:
		doc['passport_number'] = entry["personal_attributes"]["PassportNumber"]

	if "employment_history" in entry and "ExperienceSummary" in entry["employment_history"] and "ManagementStory" in entry["employment_history"]["ExperienceSummary"]:
		if entry["employment_history"]["ExperienceSummary"]["ManagementStory"]:
			doc['consultant_description'] = entry["employment_history"]["ExperienceSummary"]["ManagementStory"].replace("\n","<br>")

	if "employment_history" in entry and "ExperienceSummary" in entry["employment_history"] and "Description" in entry["employment_history"]["ExperienceSummary"]:
		if entry["employment_history"]["ExperienceSummary"]["Description"]:
			doc['consultant_description'] = entry["employment_history"]["ExperienceSummary"]["Description"].replace("\n","<br>")

	if "resume_data" in entry and "ProfessionalSummary" in entry["resume_data"]:
		if entry["resume_data"]["ProfessionalSummary"]:
			doc['consultant_description'] = entry["resume_data"]["ProfessionalSummary"].replace("\n","<br>")

	if "employment_history" in entry and "ExperienceSummary" in entry["employment_history"] and "MonthsOfWorkExperience" in entry["employment_history"]["ExperienceSummary"]:
		months_work_experience = entry["employment_history"]["ExperienceSummary"]["MonthsOfWorkExperience"]
		months_work_experience = flt(months_work_experience) / 12
		months_work_experience = math.ceil(months_work_experience)
		experience_since = flt(getdate(now()).year) - months_work_experience
		experience_since = math.ceil(experience_since)
		doc['experience_since'] = int(experience_since)

	if "education" in entry and "EducationDetails" in entry["education"]:
		for row in entry["education"]["EducationDetails"]:
			if not "degrees" in doc:
				doc['degrees'] = []
			doc["degrees"].append({
				"school_univ": row["SchoolName"]["Normalized"] if "SchoolName" in row and "Normalized" in row["SchoolName"] else None,
				"degree": row["Degree"]["Name"]["Normalized"] if "Degree" in row and "Name" in row["Degree"] and "Normalized" in row["Degree"]["Name"] else None,
				"field_of_study": row["Degree"]["Type"] if "Degree" in row and "Type" in row["Degree"] else None,
				"qualification": None,
				"level": None,
				"start_date": row["LastEducationDate"]["Date"] if "LastEducationDate" in row and "Date" in row["LastEducationDate"] else None,
				"end_date": row["LastEducationDate"]["Date"] if "LastEducationDate" in row and "Date" in row["LastEducationDate"] else None,
				"start_month": getdate(row["LastEducationDate"]["Date"]).month if "LastEducationDate" in row and "Date" in row["LastEducationDate"] else None,
				"start_year": getdate(row["LastEducationDate"]["Date"]).year if "LastEducationDate" in row and "Date" in row["LastEducationDate"] else None,
				"end_month": getdate(row["LastEducationDate"]["Date"]).month if "LastEducationDate" in row and "Date" in row["LastEducationDate"] else None,
				"end_year": getdate(row["LastEducationDate"]["Date"]).year if "LastEducationDate" in row and "Date" in row["LastEducationDate"] else None,
				"starting_year": None,
				"passing_year": None,
				"grade": row["GPA"]["Score"] if "GPA" in row and "Score" in row["GPA"] else None,
				"activities_and_societies": None,
				"description": row["Text"].replace("\n","<br>") if "Text" in row else None,
				"media": None
				})

	if "employment_history" in entry and "Positions" in entry["employment_history"]:
		for row in entry["employment_history"]["Positions"]:
			if not "experience" in doc:
				doc["experience"] = []
			doc['experience'].append({
				"designation": row["JobTitle"]["Normalized"] if "JobTitle" in row and "Normalized" in row["JobTitle"] else None,
				"employment_type": None, #row["JobType"] if "JobType" in row else None,
				"company": row["Employer"]["Name"]["Normalized"] if "Employer" in row and "Name" in row["Employer"] and "Normalized" in row["Employer"]["Name"] else None,
				"city": row["Employer"]["Location"]["Municipality"] if "Employer" in row and "Location" in row["Employer"] and "Municipality" in row["Employer"]["Location"] else None,
				"industry": None, #row["JobTitle"]["Variations"][0] if "JobTitle" in row and "Variations" in row["JobTitle"] else None,
				"i_am_currently_working_in_this_role": None,
				"from_date": row["StartDate"]["Date"] if "StartDate" in row and "Date" in row["StartDate"] else None,
				"start_month": getdate(row["StartDate"]["Date"]).month if "StartDate" in row and "Date" in row["StartDate"] else None,
				"start_year": getdate(row["StartDate"]["Date"]).year if "StartDate" in row and "Date" in row["StartDate"] else None,
				"to_date": row["EndDate"]["Date"] if "EndDate" in row and "Date" in row["EndDate"] else None,
				"end_month": getdate(row["EndDate"]["Date"]).month if "EndDate" in row and "Date" in row["EndDate"] else None,
				"end_year": getdate(row["EndDate"]["Date"]).year if "EndDate" in row and "Date" in row["EndDate"] else None,
				"description": row["Description"].replace("\n","<br>") if "Description" in row else None,
				"attachments": None,
				"media": None
				})

	if "language_competencies" in entry:
		for row in entry["language_competencies"]:
			if not "language_proficiency_level" in doc:
				doc["language_proficiency_level"] = []
			doc["language_proficiency_level"].append({
				"language": row["Language"] if "Language" in row else None,
				"language_level": None
				})

	if "skills" in entry and "Normalized" in entry["skills"]:
		for row in entry["skills"]["Normalized"]:
			if "Name" in row:
				validate_skills([row["Name"]], parsed_from_sovren=1)
				if not "skills" in doc:
					doc["skills"] = []
				doc["skills"].append({
					"skill": row["Name"]
					})
	return doc

@frappe.whitelist()
def update_it_consultant_from_parsed_data(it_consultant, entry):
	parsed_data = None
	if frappe.get_all("IT Consultant", filters={"name": it_consultant}, fields=["name"]):
		doc = frappe.get_doc("IT Consultant", it_consultant)
		doc.flags.ignore_permissions = True
		parsed_data = collect_parsed_data(entry)
		if parsed_data:
			if parsed_data.get("first_name"):
				parsed_data.pop("first_name")
			if parsed_data.get("last_name"):
				parsed_data.pop("last_name")
			if doc.mobile_primary and parsed_data.get("mobile_primary"):
				parsed_data.pop("mobile_primary")
			doc.update(parsed_data)
		return doc.save()

#erpyoupal.erpyoupal.doctype.resume_parsing.resume_parsing.create_resume_parsing
@frappe.whitelist()
def create_resume_parsing(resume_file_url, requested_from_portal=None, update_it_consultant=0, it_consultant=None):
	if it_consultant:
		if not frappe.get_all("IT Consultant", filters={"name": it_consultant}, fields=["name"]):
			frappe.throw(_("IT Consultant does not exists"))

	new_doc = frappe.new_doc("Resume Parsing")
	new_doc.it_consultant = it_consultant if it_consultant else None
	new_doc.update_it_consultant = update_it_consultant if it_consultant else 0
	new_doc.requested_from_portal = requested_from_portal
	new_doc.unparsed_resume = resume_file_url
	new_doc.flags.ignore_permissions = True
	new_doc.insert()
	return new_doc.parsed_data
#	return {
#		"name": new_doc.name,
#		"unparsed_resume": new_doc.unparsed_resume,
#		"requested_from_portal": new_doc.requested_from_portal,
#		"parsing_usage_log": new_doc.parsing_usage_log,
#		"it_consultant": new_doc.it_consultant,
#		"update_it_consultant": new_doc.update_it_consultant
#	}
