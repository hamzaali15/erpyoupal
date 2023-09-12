# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from dataclasses import field

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate
from chat.api.room import create_private
from erpyoupal.events.hr.job_applicant import create_new_it_consultant_document
from erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview import create_interview_availability
from erpyoupal.erpyoupal.doctype.background_check.background_check import create_video_interview
from erpyoupal.erpyoupal.doctype.persona_test.persona_test import create_background_check
from erpyoupal.clockify_project.doctype.clockify_user.clockify_user import create_clockify_user_from_people


class People(Document):
	def validate(self):
		self.get_fullname()
		self.get_email_address()
		self.validate_existing_email()
		self.validate_primary_contact_person()
		self.validate_organization_owner()
		self.create_user_profile()
		self.delete_created_user()
		self.crete_chat_room_with_admin()
		self.create_google_calendar()
		self.validate_portal_access()
		self.get_organization_billing_details()
		self.update_connected_docs_image()
		if not self.is_new():
			self.update_it_consultant()

	def on_trash(self):
		consultants = frappe.get_all("IT Consultant", filters={"email_primary": self.email_address}, fields=["name"])
		if consultants:
			doc = frappe.get_doc("IT Consultant", consultants[0].name)
			doc.flags.ignore_permissions = True
			doc.flags.ignore_links = True
			doc.delete()

	def before_insert(self):
		self.get_fullname()
		self.get_email_address()
	
	def after_insert(self):
		self.create_google_calendar()
		if self.people_type in ["Consultant", "Business / Consultant"]:
			self.it_consultant_processess()
		create_clockify_user_from_people(email=self.email_address)
	
	def get_organization_billing_details(self):
		if self.organization_name:
			if frappe.db.get_all("Organizations", filters={"name": self.organization_name}, fields=["name"]):
				doc = frappe.get_doc("Organizations", self.organization_name)
				if doc.bank_name:
					self.billing_bank_name = doc.bank_name
				if doc.vat:
					self.billing_vat_number = doc.vat
				if doc.business_id:
					self.billing_business_id = doc.business_id
				if doc.account_number:
					self.billing_account_number = doc.account_number
				if doc.clearing_number:
					self.billing_clearing_number = doc.clearing_number
				if doc.iban_swift:
					self.billing_iban = doc.iban_swift
				if doc.iban_swift:
					self.billing_swift = doc.iban_swift

	def it_consultant_processess(self):
		if not self.get("ignore_it_consultant_creation"):
			self.create_it_consultant()
			if self.email_address:
				create_interview_availability(it_consultant=self.name, disable_email_sending=1)
				create_video_interview(it_consultant=self.name, disable_email_sending=1)
				create_background_check(it_consultant=self.name, disregard_tests=1, disable_email_sending=1)
				if frappe.get_all("IT Consultant", filters={"name": self.name}, fields=["name"]):
					existing_doc = frappe.get_doc("IT Consultant", self.name)
					existing_doc.flags.ignore_permissions = True
					existing_doc.save()

	def create_it_consultant(self):
		if self.email_address and self.people_type in ["Consultant", "Business / Consultant"]:
			existing_consultants = frappe.get_all("IT Consultant", filters={"email_primary": self.email_address}, fields=["name"])
			if self.email_address and not existing_consultants:
				new_doc = frappe.new_doc("IT Consultant")
				new_doc.it_consultant_name = self.name
				new_doc.email_primary = self.email_address
				if self.first_name:
					new_doc.first_name = self.first_name
				if self.last_name:
					new_doc.last_name = self.last_name
				if self.date_of_birth:
					new_doc.date_of_birth = self.date_of_birth
				if self.gender:
					new_doc.gender = self.gender
				if self.address:
					new_doc.address = self.address
				if self.country:
					new_doc.location = self.country
				if self.image:
					new_doc.image = self.image
				if self.passport_nationality:
					new_doc.passport_nationality = self.passport_nationality
				if self.passport_number:
					new_doc.passport_number = self.passport_number
				if self.passport_dob:
					new_doc.passport_dob = self.passport_dob
				if self.passport_cityofbirth:
					new_doc.passport_cityofbirth = self.passport_cityofbirth
				if self.passport_countryofbirth:
					new_doc.passport_countryofbirth = self.passport_countryofbirth
				if self.passport_gender:
					new_doc.passport_gender = self.passport_gender
				if self.passport_dateofissue:
					new_doc.passport_dateofissue = self.passport_dateofissue
				if self.passport_dateofexpiry:
					new_doc.passport_dateofexpiry = self.passport_dateofexpiry
				if self.passport_issuedby:
					new_doc.passport_issuedby = self.passport_issuedby
				if self.passport_visatype:
					new_doc.passport_visatype = self.passport_visatype
				if self.emergency_contact_name:
					new_doc.emergency_contact_name = self.emergency_contact_name
				if self.emergency_contact_email:
					new_doc.emergency_contact_email = self.emergency_contact_email
				if self.emergency_contact_mobile:
					new_doc.emergency_contact_mobile = self.emergency_contact_mobile
				if self.mobile:
					new_doc.mobile_primary = self.mobile[0].mobile
				if self.organization_name:
					new_doc.agency_name = self.organization_name
				if self.get("availability"):
					new_doc.availability = self.get("availability")
				if self.get("rate_hourly"):
					new_doc.rate_hourly = self.get("rate_hourly")
				if self.get("position_title"):
					new_doc.position_title = self.get("position_title")
				if self.get("resume"):
					new_doc.resume = self.get("resume")
				if self.get("location"):
					new_doc.location = self.get("location")
				if self.get("date_of_birth"):
					new_doc.date_of_birth = self.get("date_of_birth")
				if self.get("experience_since"):
					new_doc.experience_since = self.get("experience_since")
				if self.get("total_experience"):
					new_doc.total_experience = self.get("total_experience")
				if self.get("work_type"):
					new_doc.work_type = self.get("work_type")
				if self.get("work_destination"):
					new_doc.work_destination = self.get("work_destination")
				if self.get("personal_id"):
					new_doc.personal_id = self.get("personal_id")
				if self.get("association"):
					new_doc.association = self.get("association")
				if self.get("nda"):
					new_doc.nda = self.get("nda")
				if self.get("email_secondary"):
					new_doc.email_secondary = self.get("email_secondary")
				if self.get("consultant_description"):
					new_doc.consultant_description = self.get("consultant_description")
				if self.linkedin:
					new_doc.append("platform_social_media", {
						"platform_social_media": "linkedin",
						"link": self.linkedin
					})
				if self.facebook:
					new_doc.append("platform_social_media", {
						"platform_social_media": "facebook",
						"link": self.facebook
					})
				if self.instagram:
					new_doc.append("platform_social_media", {
						"platform_social_media": "instagram",
						"link": self.instagram
					})
				if self.twitter:
					new_doc.append("platform_social_media", {
						"platform_social_media": "twitter",
						"link": self.twitter
					})
				if self.fiverr:
					new_doc.append("platform_social_media", {
						"platform_social_media": "fiverr",
						"link": self.fiverr
					})
				if self.github:
					new_doc.append("platform_social_media", {
						"platform_social_media": "github",
						"link": self.github
					})
				if self.upwork:
					new_doc.append("platform_social_media", {
						"platform_social_media": "upwork",
						"link": self.upwork
					})
				if self.stackoverflow:
					new_doc.append("platform_social_media", {
						"platform_social_media": "stackoverflow",
						"link": self.stackoverflow
					})
				if self.get("skills"):
					for row_skills in self.get("skills"):
						new_doc.append('skills', row_skills)
				if self.get("experience"):
					for row_experience in self.get("experience"):
						new_doc.append('experience', row_experience)
				if self.get("language_proficiency_level"):
					for row_language_proficiency_level in self.get("language_proficiency_level"):
						new_doc.append('language_proficiency_level', row_language_proficiency_level)
				new_doc.flags.ignore_permissions = True
				new_doc.flags.ignore_links = True
				new_doc.save()

	def crete_chat_room_with_admin(self):
		if self.created_user:
			chat_room_name = str(self.created_user)+", Administrator"
			room_users = str([str(self.created_user)])
			room_type="Direct"
			if not frappe.get_all("Chat Room", filters={"type": "Direct", "members": chat_room_name}):
				try:
					create_private(room_name=chat_room_name, users=room_users, type=room_type)
				except Exception as e:
					pass
	
	def update_connected_docs_image(self):
		if self.email_address:
			it_consultants = frappe.get_all("IT Consultant", filters={"email_primary": self.email_address}, fields=["name", "image"])
			if it_consultants:
				frappe.db.set_value('IT Consultant', it_consultants[0].name, 'image', self.image, update_modified=False)
			
			users = frappe.get_all("User", filters={"name": self.email_address}, fields=["name", "user_image"])
			if users:
				frappe.db.set_value('User', users[0].name, 'user_image', self.image, update_modified=False)

	def validate_existing_email(self):
		if self.is_new():
			if frappe.get_all("People", filters={"name": ["not in", [self.name]], "email_address": self.email_address}, fields=["name"]):
				frappe.throw(_("Email already exists"))
	
	def validate_portal_access(self):
		if self.email_address:
			organization_type = None
			if self.organization_name:
				organizations_doc = frappe.get_doc("Organizations", self.organization_name)
				if organizations_doc:
					organization_type = organizations_doc.organization_type
			access_dict = validate_user_portal_access(self.people_type, organization_type)

			self.client_portal_access = access_dict["Client Portal"]
			self.partner_portal_access = access_dict["Partner Portal"]
			self.talent_portal_access = access_dict["Talent Portal"]
	
	def validate_organization_owner(self):
		if self.organization_name and self.access_level in ["Owner"]:
			if frappe.get_all("People", filters={"name": ["not in", [self.name]], "access_level": "Owner", "organization_name": self.organization_name}, fields=["name"]):
				frappe.throw(_("An Owner for this organization already exists"))

	def create_google_calendar(self):
		if self.email_address and not self.google_calendar:
			existing_calendar = frappe.get_all("Google Calendar", filters={"user": self.email_address}, fields=["name"])
			if existing_calendar:
				self.google_calendar = existing_calendar[0].name
				if self.is_new():
					self.db_set('google_calendar', existing_calendar[0].name)
			else:
				new_calendar = frappe.new_doc("Google Calendar")
				new_calendar.calendar_name = self.name
				new_calendar.user = self.email_address
				new_calendar.flags.ignore_permissions = True
				new_calendar.flags.ignore_links = True
				if new_calendar.save():
					self.google_calendar = new_calendar.name
					if self.is_new():
						self.db_set('google_calendar', new_calendar.name)

	def get_email_address(self):
		if self.email:
			for em in self.email:
				self.email_address = em.email
				break
	
	def update_it_consultant(self):
		if not self.get("triggered_from_it_consultant"):
			existing = frappe.get_all("IT Consultant", filters={"email_primary": self.email_address}, fields=["name"])
			if existing:
				cur_doc = frappe.get_doc("IT Consultant", existing[0].name)
				if self.first_name:
					cur_doc.first_name = self.first_name
				if self.last_name:
					cur_doc.last_name = self.last_name
				if self.date_of_birth:
					cur_doc.date_of_birth = self.date_of_birth
				if self.gender:
					cur_doc.gender = self.gender
				if self.address:
					cur_doc.address = self.address
				if self.country:
					cur_doc.location = self.country
				if self.image:
					cur_doc.image = self.image
				if self.passport_nationality:
					cur_doc.passport_nationality = self.passport_nationality
				if self.passport_number:
					cur_doc.passport_number = self.passport_number
				if self.passport_dob:
					cur_doc.passport_dob = self.passport_dob
				if self.passport_cityofbirth:
					cur_doc.passport_cityofbirth = self.passport_cityofbirth
				if self.passport_countryofbirth:
					cur_doc.passport_countryofbirth = self.passport_countryofbirth
				if self.passport_gender:
					cur_doc.passport_gender = self.passport_gender
				if self.passport_dateofissue:
					cur_doc.passport_dateofissue = self.passport_dateofissue
				if self.passport_dateofexpiry:
					cur_doc.passport_dateofexpiry = self.passport_dateofexpiry
				if self.passport_issuedby:
					cur_doc.passport_issuedby = self.passport_issuedby
				if self.passport_visatype:
					cur_doc.passport_visatype = self.passport_visatype
				if self.emergency_contact_name:
					cur_doc.emergency_contact_name = self.emergency_contact_name
				if self.emergency_contact_email:
					cur_doc.emergency_contact_email = self.emergency_contact_email
				if self.emergency_contact_mobile:
					cur_doc.emergency_contact_mobile = self.emergency_contact_mobile
				if self.mobile:
					cur_doc.mobile_primary = self.mobile[0].mobile
				if self.organization_name:
					cur_doc.agency_name = self.organization_name
				if self.get("location"):
					cur_doc.location = self.get("location")
				if self.get("availability"):
					cur_doc.availability = self.get("availability")
				if self.get("rate_hourly"):
					cur_doc.rate_hourly = self.get("rate_hourly")
				if self.get("position_title"):
					cur_doc.position_title = self.get("position_title")
				if self.get("resume"):
					cur_doc.resume = self.get("resume")
				if self.get("date_of_birth"):
					cur_doc.date_of_birth = self.get("date_of_birth")
				if self.get("experience_since"):
					cur_doc.experience_since = self.get("experience_since")
				if self.get("total_experience"):
					cur_doc.total_experience = self.get("total_experience")
				if self.get("work_type"):
					cur_doc.work_type = self.get("work_type")
				if self.get("work_destination"):
					cur_doc.work_destination = self.get("work_destination")
				if self.get("personal_id"):
					cur_doc.personal_id = self.get("personal_id")
				if self.get("association"):
					cur_doc.association = self.get("association")
				if self.get("nda"):
					cur_doc.nda = self.get("nda")
				if self.get("email_secondary"):
					cur_doc.email_secondary = self.get("email_secondary")
				if self.get("consultant_description"):
					cur_doc.consultant_description = self.get("consultant_description")

				no_linkedin = 1
				no_facebook = 1
				no_instagram = 1
				no_twitter = 1
				no_fiverr = 1
				no_github = 1
				no_upwork = 1
				no_stackoverflow = 1
				if cur_doc.platform_social_media:
					for row in cur_doc.platform_social_media:
						if str(row.platform_social_media).lower() in ["linkedin", "linked in"]:
							row.link = self.linkedin
							no_linkedin = 0
						if str(row.platform_social_media).lower() in ["facebook", "face book"]:
							row.link = self.facebook
							no_facebook = 0
						if str(row.platform_social_media).lower() in ["instagram", "insta gram"]:
							row.link = self.instagram
							no_instagram = 0
						if str(row.platform_social_media).lower() in ["twitter", "twit ter"]:
							row.link = self.twitter
							no_twitter = 0
						if str(row.platform_social_media).lower() in ["upwork", "up work"]:
							row.link = self.upwork
							no_upwork = 0
						if str(row.platform_social_media).lower() in ["github", "git hub"]:
							row.link = self.github
							no_github = 0
						if str(row.platform_social_media).lower() in ["fiverr", "fiv err"]:
							row.link = self.fiverr
							no_fiverr = 0
						if str(row.platform_social_media).lower() in ["stackoverflow", "stack overflow"]:
							row.link = self.stackoverflow
				if no_linkedin and self.linkedin:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "linkedin",
						"link": self.linkedin
					})
				if no_facebook and self.facebook:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "facebook",
						"link": self.facebook
					})
				if no_instagram and self.instagram:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "instagram",
						"link": self.instagram
					})
				if no_twitter and self.twitter:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "twitter",
						"link": self.twitter
					})
				if no_fiverr and self.fiverr:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "fiverr",
						"link": self.fiverr
					})
				if no_github and self.github:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "github",
						"link": self.github
					})
				if no_upwork and self.upwork:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "upwork",
						"link": self.upwork
					})
				if no_stackoverflow and self.stackoverflow:
					cur_doc.append("platform_social_media", {
						"platform_social_media": "stackoverflow",
						"link": self.stackoverflow
					})

				cur_doc.triggered_from_people = True
				cur_doc.flags.ignore_permissions = True
				cur_doc.flags.ignore_links = True
				cur_doc.save()
	
	@frappe.whitelist()
	def merge_new_email_to_old(self):
		old_email = frappe.db.get_value('People', self.name, 'email_address')
		new_email = None
		if self.email:
			new_email = self.email[0].email

		if self.created_user and new_email:
			#merge email for IT Consultant
			itcs = frappe.get_all('IT Consultant', filters={"email_primary": old_email}, fields=["name"])
			if itcs:
				for itc in itcs:
					frappe.db.set_value('IT Consultant', itc.name, 'email_primary', new_email)
					frappe.db.commit()
			#merge email for Skill Test Coderbyte
			stcs = frappe.get_all('Skill Test Coderbyte', filters={"email": old_email}, fields=["name"])
			if stcs:
				for stc in stcs:
					frappe.db.set_value('Skill Test Coderbyte', stc.name, 'email', new_email)
					frappe.db.commit()
			#merge email for Persona Test
			pts = frappe.get_all('Persona Test', filters={"email": old_email}, fields=["name"])
			if pts:
				for pt in pts:
					frappe.db.set_value('Persona Test', pt.name, 'email', new_email)
					frappe.db.commit()
			#merge email for Background Check
			bcs = frappe.get_all('Background Check', filters={"email": old_email}, fields=["name"])
			if bcs:
				for bc in bcs:
					frappe.db.set_value('Background Check', bc.name, 'email', new_email)
					frappe.db.commit()
			#merge email for Video Interview
			vis = frappe.get_all('Video Interview', filters={"email": old_email}, fields=["name"])
			if vis:
				for vi in vis:
					frappe.db.set_value('Video Interview', vi.name, 'email', new_email)
					frappe.db.commit()
			#merge email for Candidate Interview
			cis = frappe.get_all('Candidate Interview', filters={"email": old_email}, fields=["name"])
			if cis:
				for ci in cis:
					frappe.db.set_value('Candidate Interview', ci.name, 'email', new_email)
					frappe.db.commit()
			#merge email for Skill Test
			sts = frappe.get_all('Skill Test', filters={"email": old_email}, fields=["name"])
			if sts:
				for st in sts:
					frappe.db.set_value('Skill Test', st.name, 'email', new_email)
					frappe.db.commit()
			#merge email for Job Applicant
			jas = frappe.get_all('Job Applicant', filters={"email_id": old_email}, fields=["name"])
			if jas:
				for ja in jas:
					frappe.db.set_value('Job Applicant', ja.name, 'email_id', new_email)
					frappe.db.commit()
			if str(self.created_user) != str(new_email):
				frappe.rename_doc('User', self.created_user, new_email)
				frappe.db.commit()
				self.db_set('created_user', new_email)
			self.db_set('email_address', new_email)
			frappe.db.sql("""UPDATE `tabEmail` SET `email`='"""+new_email+"""' WHERE `parenttype`='People' AND `parentfield`='email' AND `idx`=1 AND `parent`='"""+self.name+"""' """)
			#self.save()
	
	@frappe.whitelist()
	def validate_if_new_email(self):
		if self.email_address and self.email:
			for row in self.email:
				if str(row.email) != str(self.email_address):
					return False
				else:
					return True

	@frappe.whitelist()
	def go_to_it_consultant(self):
		it_consultants = frappe.get_all("IT Consultant", filters={"email_primary": self.email_address}, fields=["name"])
		if it_consultants:
			return it_consultants[0].name
		else:
			return None

	@frappe.whitelist()
	def validate_user_exists(self):
		result = "True"
		if self.created_user:
			if frappe.get_all("User", filters={'name': self.created_user}):
				result = "False"
		
		if self.email_address:
			if frappe.get_all("User", filters={'name': self.email_address}):
				result = "False"

		return result

	@frappe.whitelist()
	def create_user_profile(self, forced=0):
		if self.create_user and not self.created_user:
			if not self.email_address:
				frappe.throw(_("Email is required to create user"))
			
			if self.validate_user_exists() in ["True", True]:
				new_doc = frappe.new_doc("User")
				new_doc.email = self.email_address
				new_doc.first_name = self.first_name
				new_doc.last_name = self.last_name
				new_doc.organization = self.organization_name
				new_doc.agency = self.agency
				new_doc.send_welcome_email = 0 if not self.get('user_send_welcome_email') else self.get('user_send_welcome_email')
				new_doc.send_welcome_email_talent_portal = 0 if not self.get('user_send_welcome_email_talent_portal') else self.get('user_send_welcome_email_talent_portal')
				new_doc.flags.ignore_permissions = True
				new_doc.disable_desk_access = 1
				new_doc.add_roles('Client Portal User')
				new_doc.add_roles('System Manager')
				if new_doc.save():
					self.created_user = new_doc.name

			if self.validate_user_exists() in ["False", False] and forced:
				existing_user = frappe.get_all("User", filters={'name': self.email_address}, fields=['name'])
				if existing_user:
					self.created_user = existing_user[0].name
					self.db_set('created_user', existing_user[0].name)

	def delete_created_user(self):
		if self.created_user and not self.create_user:
			if frappe.get_all("User", filters={'name': self.created_user}):
				frappe.delete_doc("User", self.created_user, force=1,  for_reload=True, ignore_permissions = True)
			self.created_user = None

	def get_fullname(self):
		fullname = [self.first_name]
		if self.last_name:
			fullname.append(self.last_name)
		self.person_name = " ".join(fullname)

	def link_document_to_agency_or_organization(self):
		if self.organization_name and not self.agency:
			agencies = frappe.get_all("IT Partner Agency", filters={'organization': self.organization_name}, fields=['name'])
			if agencies:
				for agency in agencies:
					self.agency = agency.name
		
		if not self.organization_name and self.agency:
			agencies = frappe.get_all("IT Partner Agency", filters={'name': self.agency}, fields=['organization'])
			if agencies:
				for agency in agencies:
					self.organization_name = agency.organization

	def validate_primary_contact_person(self):
		if self.is_primary_contact_person and self.organization_name:
			existing_people = frappe.get_all('People', filters={'is_primary_contact_person': 1, 'organization_name': self.organization_name, 'name': ['!=', self.name]})
			if existing_people:
				frappe.throw(_( "Primary Contact Person for Organization {0} already exists".format(self.organization_name) ))

#erpyoupal.erpyoupal.doctype.people.people..validate_user_portal_access
@frappe.whitelist(allow_guest=True)
def validate_user_portal_access(people_type, organization_type):
	access_dict = {
		"Client Portal": 0,
		"Partner Portal": 0,
		"Talent Portal": 0,
		"Jobs Portal": 0
	}

	if people_type in ["Business"]:
		if organization_type:
			if organization_type in ["Partner", "Individual"]:
				access_dict["Partner Portal"] = 1
			if organization_type in ["Client"]:
				access_dict["Client Portal"] = 1
			if organization_type in ["Client/Partner"]:
				access_dict["Client Portal"] = 1
				access_dict["Partner Portal"] = 1
		else:
			pass
			#no access till connected to organization

	if people_type in ["Consultant"]:
		if organization_type:
			if organization_type in ["Partner", "Individual"]:
				access_dict["Talent Portal"] = 1
			if organization_type in ["Client"]:
				access_dict["Talent Portal"] = 1
			if organization_type in ["Client/Partner"]:
				access_dict["Talent Portal"] = 1
		else:
			access_dict["Talent Portal"] = 1
			
	if people_type in ["Business / Consultant"]:
		if organization_type:
			if organization_type in ["Partner", "Individual"]:
				access_dict["Partner Portal"] = 1
				access_dict["Talent Portal"] = 1
			if organization_type in ["Client"]:
				access_dict["Client Portal"] = 1
				access_dict["Talent Portal"] = 1
			if organization_type in ["Client/Partner"]:
				access_dict["Partner Portal"] = 1
				access_dict["Talent Portal"] = 1
				access_dict["Client Portal"] = 1
		else:
			access_dict["Talent Portal"] = 1
	
	return access_dict

#erpyoupal.erpyoupal.doctype.people.people.get_user_portal_access
@frappe.whitelist(allow_guest=True)
def get_user_portal_access(user):
	access_dict = {
		"Client Portal": 0,
		"Partner Portal": 0,
		"Talent Portal": 0,
		"Jobs Portal": 0
	}

	peoples = frappe.get_all("People", filters={"email_address": user}, fields=["*"])
	if peoples:
		people = peoples[0]
		organization_type = None
		if people.organization_name:
			organizations_doc = frappe.get_doc("Organizations", people.organization_name)
			if organizations_doc:
				organization_type = organizations_doc.organization_type
		access_dict = validate_user_portal_access(people.people_type, organization_type)
	
	return access_dict

@frappe.whitelist()
def refill_fullname():
	doc_lists = frappe.get_all("People", fields=['name', 'first_name', 'last_name', 'person_name'])
	if doc_lists:
		for doc in doc_lists:
			if not doc.first_name and not doc.last_name:
				people_doc = frappe.get_doc("People", doc.name)
				people_doc_person_name = people_doc.person_name
				first_name = people_doc_person_name.split()[0]
				last_name = people_doc_person_name.split()[1:]
				last_name = " ".join(last_name)
				people_doc.first_name = first_name
				people_doc.last_name = last_name
				people_doc.flags.ignore_permissions = True
				people_doc.save()

#erpyoupal.erpyoupal.doctype.people.people.populate_chat_rooms
@frappe.whitelist()
def populate_chat_rooms():
	ap_docs = frappe.get_all("People", fields=["name"])
	for ap_doc in ap_docs:
		doc = frappe.get_doc("People", ap_doc.name)
		doc.run_method("crete_chat_room_with_admin")

#erpyoupal.erpyoupal.doctype.people.people.add_itconsultant_to_people
@frappe.whitelist()
def add_itconsultant_to_people():
	consultants = frappe.get_all("IT Consultant", fields=["name"])
	for consultant in consultants:
		consultant_doc = frappe.get_doc("IT Consultant", consultant.name)
		if not frappe.get_all("People", filters={"email_address": consultant_doc.email_primary}, fields=["name"]):
			new_doc = frappe.new_doc("People")
			new_doc.flags.ignore_permissions = True
			new_doc.people_type = "Consultant"
			new_doc.first_name = consultant_doc.first_name
			new_doc.last_name = consultant_doc.last_name
			#new_doc.person_name = None
			#new_doc.is_primary_contact_person = None
			#new_doc.organization_name = None
			#new_doc.agency = None
			#new_doc.designation = None
			new_doc.status = "Active"
			#new_doc.address = None
			#new_doc.reports_to = None
			#new_doc.email_address = None
			new_doc.create_user = 1
			#new_doc.created_user = None
			#new_doc.google_calendar = None
			new_doc.date_of_birth = consultant_doc.date_of_birth
			if consultant_doc.platform_social_media:
				for row in consultant_doc.platform_social_media:
					if str(row.platform_social_media).lower() in ["linkedin", "linked in", "linked_in"]:
						new_doc.linkedin = row.link
					if str(row.platform_social_media).lower() in ["facebook", "face book"]:
						new_doc.facebook = row.link
					if str(row.platform_social_media).lower() in ["instagram", "insta gram"]:
						new_doc.instagram = row.link
					if str(row.platform_social_media).lower() in ["twitter", "twit ter"]:
						new_doc.twitter = row.link
			new_doc.append("email", {"email": consultant_doc.email_primary})
			new_doc.append("mobile", {"mobile": consultant_doc.mobile_primary})
			new_doc.insert()

#erpyoupal.erpyoupal.doctype.people.people.enable_disable_people_user
@frappe.whitelist()
def enable_disable_people_user(people, action):
	if not action in ["enable", "disable"]:
		frappe.throw(_('action must be in "enable", "disable"'))
	
	new_action = 0
	if action in ["enable"]:
		new_action = 1
	if action in ["disable"]:
		new_action = 0

	if frappe.get_all("People", filters={"name": people}, fields=["name"]):
		doc = frappe.get_doc("People", people)
		if doc.created_user:
			user_doc = frappe.get_doc("User", doc.created_user)
			user_doc.enabled = new_action
			user_doc.flags.ignore_permissions = True
			user_doc.save()
			return "ok"
	else:
		frappe.throw(_("People not found"))

#erpyoupal.erpyoupal.doctype.people.people.disable_desk_for_all_user_people
@frappe.whitelist()
def disable_desk_for_all_user_people():
	peoples = frappe.get_all("People", fields=["name", "email_address"])
	if peoples:
		for row in peoples:
			if frappe.get_all("User", filters={"name": row.email_address, "disable_desk_access": 0}, fields=["name"]):
				user_doc = frappe.get_doc("User", row.email_address)
				user_doc.flags.ignore_permissions = True
				user_doc.disable_desk_access = 1
				try:
					user_doc.save()
				except Exception as e:
					pass

#erpyoupal.erpyoupal.doctype.people.people.rename_it_consultant_to_people
@frappe.whitelist()
def rename_it_consultant_to_people():
	failed_consultants = []
	consultants = frappe.get_all("IT Consultant", fields=["name", "email_primary"])
	if consultants:
		for cons in consultants:
			peoples = frappe.get_all("People", filters={"email_address": cons.email_primary}, fields=["name"])
			if peoples and str(peoples[0].name) != str(cons.name):
				try:
					frappe.rename_doc('IT Consultant', cons.name, peoples[0].name)
					frappe.db.commit()
				except:
					failed_consultants.append(cons.name)
	print(failed_consultants)


#erpyoupal.erpyoupal.doctype.people.people.fill_people_it_consultant_field
@frappe.whitelist()
def fill_people_it_consultant_field():
	peoples = frappe.get_all("People", fields=["name", "email_address"])
	if peoples:
		for pep in peoples:
			doc = frappe.get_doc("People", pep.name)
			if doc.email_address and doc.email:
				consultants = frappe.get_all("IT Consultant", filters={"email_primary": pep.email_address}, fields=["name"])
				if consultants:
					doc.it_consultant = consultants[0].name
					doc.flags.ignore_permissions = True
					doc.flags.ignore_links = True
					doc.save()

#erpyoupal.erpyoupal.doctype.people.people.youpal_onboard_internal_users
@frappe.whitelist()
def youpal_onboard_internal_users():
	onboarding_data = [{
		'email': 'karl@youpal.se',
		'full_name': 'Karl Leahlander',
		'country': 'Sweden',
		'role': 'CEO- Partner',
		'date_started': '1-Jan-2016'
		},
		{
		'email': 'james.bakerduly@gmail.com',
		'full_name': 'James Baker- Duly',
		'country': 'Sweden',
		'role': 'Chief Operations Officer',
		'date_started': '1-Jan-2016'
		},
		{
		'email': 'ruben@youpal.se',
		'full_name': 'Ruben Teijeiro',
		'country': 'Sweden',
		'role': 'CTO- Partner',
		'date_started': '1-Jan-2016'
		},
		{
		'email': 'abderazakhouaiss@gmail.com',
		'full_name': 'Abderazak Houaiss',
		'country': 'Morocco',
		'role': 'Drupal Fullstack Developer',
		'date_started': '20-May-2021'
		},
		{
		'email': 'adhammagdy.dev@gmail.com',
		'full_name': 'Adham Magdy Ahmed Rushdy',
		'country': '',
		'role': 'QA Engineer',
		'date_started': ''
		},
		{
		'email': 'interact2amit@gmail.com',
		'full_name': 'Amit Mohan Prithyani',
		'country': 'India',
		'role': 'UI Developer',
		'date_started': '30-Jun-2021'
		},
		{
		'email': 'aposarga@gmail.com',
		'full_name': 'Apostolis Argatzopoulos',
		'country': 'Greece',
		'role': 'Lead Data',
		'date_started': '18-Jun-2020'
		},
		{
		'email': 'berdartem@gmail.com',
		'full_name': 'Artem Berdyshev',
		'country': 'Ukraine',
		'role': 'Lead- Frontend Architect',
		'date_started': '1-Jan-2020'
		},
		{
		'email': 'khanazhar70@gmail.com',
		'full_name': 'Azharullah Khan',
		'country': 'India',
		'role': 'UX Designer',
		'date_started': '27-May-2022'
		},
		{
		'email': 'cidzaragoza@yahoo.com',
		'full_name': 'Cid Amaro Zaragoza',
		'country': 'Philippines',
		'role': 'Frappe Developer',
		'date_started': '19-Feb-2022'
		},
		{
		'email': 'trincudan@gmail.com',
		'full_name': 'Dan-Andrei Trincu',
		'country': 'Armenia',
		'role': 'DevOps Engineer',
		'date_started': '25-Mar-2022'
		},
		{
		'email': 'dilan@youpal.se',
		'full_name': 'Dilan Samuelsson',
		'country': 'Sweden',
		'role': 'Head of Legal',
		'date_started': '1-Jan-2016'
		},
		{
		'email': 'dorilyn15@gmail.com',
		'full_name': 'Dorilyn Sambrano',
		'country': 'Philippines',
		'role': 'IT Service Desk',
		'date_started': '16-Nov-2020'
		},
		{
		'email': 'f.ac.simoes@gmail.com	',
		'full_name': 'Fernando Simoes',
		'country': 'Portugal',
		'role': 'Drupal Developer',
		'date_started': '22-Jun-2022'
		},
		{
		'email': 'floris@040lab.com',
		'full_name': 'Floris van Geel',
		'country': 'The Netherlands',
		'role': 'Head of YouCloud',
		'date_started': '1-Jan-2016'
		},
		{
		'email': 'fredrik@youpal.se',
		'full_name': 'Fredrik Stafberg',
		'country': 'Sweden',
		'role': 'Agile PM',
		'date_started': ''
		},
		{
		'email': 'gustaffndalo@gmail.com',
		'full_name': 'Gustaff Amboka Ndalo',
		'country': 'Kenya',
		'role': 'Social Media & Content Specialist',
		'date_started': '18-Oct-2021'
		},
		{
		'email': 'henrik.albrechtsson@gmail.com',
		'full_name': 'Henrik Albrechtsson',
		'country': 'Sweden',
		'role': 'Drupal Developer',
		'date_started': '22-Aug-2022'
		},
		{
		'email': 'jtosino@yahoo.com',
		'full_name': 'Jeanette I. Tosino',
		'country': 'Malaysia',
		'role': 'Data Entry',
		'date_started': '27-Jan-2021'
		},
		{
		'email': 'jessical__@hotmail.com',
		'full_name': 'Jessica Landin',
		'country': 'Sweden',
		'role': 'EA',
		'date_started': '1-Jan-2020'
		},
		{
		'email': 'joeljeru1@gmail.com',
		'full_name': 'Joel Jerushan Jeyaratnam',
		'country': 'Sri Lanka',
		'role': 'DevOps React Developer',
		'date_started': '6-Jun-2022'
		},
		{
		'email': 'dyenlouie03@gmail.com',
		'full_name': 'John Louie Torres',
		'country': 'Philippines',
		'role': 'Service Desk Support',
		'date_started': '16-Nov-2020'
		},
		{
		'email': 'diazjohnmatthew@gmail.com',
		'full_name': 'John Matthew Diaz',
		'country': 'Philippines',
		'role': 'ERP Developer',
		'date_started': '5-May-2022'
		},
		{
		'email': 'jovana@youpal.se',
		'full_name': 'Jovana Bajic',
		'country': 'Serbia',
		'role': 'Products',
		'date_started': '16-Nov-2020'
		},
		{
		'email': 'k.pirumyan@gmail.com',
		'full_name': 'Karen Pirumyan',
		'country': 'Armenia',
		'role': 'Fullstack Developer',
		'date_started': '14-Jan-2022'
		},
		{
		'email': 'kb.nawaz@gmail.com',
		'full_name': 'Khurram Bilal Nawaz',
		'country': 'Pakistan',
		'role': 'React Native Developer',
		'date_started': '17-Nov-2021'
		},
		{
		'email': 'kkumaren@gmail.com',
		'full_name': 'Kistnasamy Kumaren',
		'country': 'France',
		'role': 'Senior Drupal Developer',
		'date_started': '7-Jun-2022'
		},
		{
		'email': 'lev.ananikyan@gmail.com',
		'full_name': 'Lev Ananikyan',
		'country': 'Armenia',
		'role': 'Drupal Architect (Vectus CTO)',
		'date_started': ''
		},
		{
		'email': 'marat@youpal.se',
		'full_name': 'Marat Sadykov',
		'country': 'Sweden',
		'role': 'Fullstack Developer',
		'date_started': '2-Feb-2021'
		},
		{
		'email': 'marianna.karapetyan@gmail.com',
		'full_name': 'Marianna Karapetyan',
		'country': 'Armenia',
		'role': 'QA Engineer',
		'date_started': '1-Feb-2021'
		},
		{
		'email': 'melvin.mathews@hotmail.com',
		'full_name': 'Melvin Mathews',
		'country': 'Finland',
		'role': 'QA Engineer',
		'date_started': '23-Dec-2020'
		},
		{
		'email': 'mumtozvalijonov@gmail.com',
		'full_name': 'Mumtozbek Valijonov',
		'country': 'Uzbekistan',
		'role': 'Data Engineer',
		'date_started': '19-Feb-2021'
		},
		{
		'email': 'gospodin.p.zh@gmail.com',
		'full_name': 'Mykola Dolynskyi',
		'country': 'Ukraine',
		'role': 'Drupal Dev',
		'date_started': '11-Jan-2021'
		},
		{
		'email': 'natalia4rn@gmail.com',
		'full_name': 'Natalie Cherniavska',
		'country': 'Ukraine',
		'role': 'IT Project Manager',
		'date_started': '1-Jan-2020'
		},
		{
		'email': 'nizreen.ismail@gmail.com',
		'full_name': 'Nizreen Ismail',
		'country': 'Sri Lanka',
		'role': 'Agency Application & Candidate Coordinator',
		'date_started': '13-Sep-2021'
		},
		{
		'email': 'oleh.ch@youpal.se',
		'full_name': 'Oleh Chuchman',
		'country': 'Ukraine',
		'role': 'Lawyer - Contracts',
		'date_started': '30-Sep-2019'
		},
		{
		'email': 'rajka@youpal.se',
		'full_name': 'Rajka Stjepanovic',
		'country': 'Serbia',
		'role': 'Head of Accounting',
		'date_started': '22-Jan-2021'
		},
		{
		'email': 'rawat.ranvirsingh@gmail.com',
		'full_name': 'Ranbir Singh',
		'country': 'India',
		'role': 'ERPnext Consultant',
		'date_started': ''
		},
		{
		'email': 'razv4n.bogdan@yahoo.com',
		'full_name': 'Raz Bulmaga',
		'country': 'France',
		'role': 'Senior Drupal Developer',
		'date_started': '6-Apr-2022'
		},
		{
		'email': 'itszaidi@gmail.com',
		'full_name': 'Sajjad Raza',
		'country': 'Pakistan',
		'role': 'React Native Developer',
		'date_started': '2-Nov-2021'
		},
		{
		'email': 'sanal.k@youpal.es',
		'full_name': 'Sanal Kappakkuth',
		'country': 'India',
		'role': 'Wordpress developer',
		'date_started': '16-Sep-2020'
		},
		{
		'email': 'birwalsandeep@gmail.com',
		'full_name': 'Sandeep Birwal',
		'country': 'India',
		'role': 'UX/UI Designer',
		'date_started': '19-May-2022'
		},
		{
		'email': 'sara.upworkid@gmail.com',
		'full_name': 'Sara Romany',
		'country': 'Egypt',
		'role': 'Consultant Manager',
		'date_started': '8-Feb-2021'
		},
		{
		'email': 'shah.shah.2001.22@gmail.com',
		'full_name': 'Shakhzodbek Khudayshukurov',
		'country': 'Uzbekistan',
		'role': 'Data Engineer',
		'date_started': '11-May-2022'
		},
		{
		'email': 'Shahalam7303@gmail.com',
		'full_name': 'Shah Alam',
		'country': 'Bangladesh',
		'role': 'UX/UI Product designer',
		'date_started': '17-Oct-2022'
		},
		{
		'email': 'shalini10april@gmail.com',
		'full_name': 'Shalini Singh',
		'country': 'India',
		'role': 'Drupal Developer',
		'date_started': '8-Mar-2021'
		},
		{
		'email': 'shievasaavedra28@gmail.com',
		'full_name': 'Shieva Saavedra',
		'country': 'Philippines',
		'role': 'HR Manager',
		'date_started': '16-Nov-2020'
		},
		{
		'email': 'kicheodinga@gmail.com',
		'full_name': 'Stephen Kanyi',
		'country': 'Kenya',
		'role': 'Technical Writer',
		'date_started': '1-Dec-2020'
		},
		{
		'email': 'sherath8@gmail.com',
		'full_name': 'Sudarshini Herath',
		'country': 'Sri Lanka',
		'role': 'Process Owner',
		'date_started': '23-May-2022'
		},
		{
		'email': 'taimooryousaf69@gmail.com',
		'full_name': 'Taimur Hussain Khan',
		'country': 'Pakistan',
		'role': 'ERP Product Owner',
		'date_started': '27-Oct-2021'
		},
		{
		'email': 'onipko32@gmail.com',
		'full_name': 'Yevhenii Onipko',
		'country': 'Ukraine',
		'role': 'React native/swift/kotlin software engineer',
		'date_started': '18-Aug-2022'
		},
		{
		'email': 'zikrilloislomov@gmail.com',
		'full_name': 'Zikrillo Islomov',
		'country': 'United Kingdom',
		'role': 'QA Specialist',
		'date_started': '20-Jun-2022'
		},
		{
		'email': 'harshinigunathilaka94@gmail.com',
		'full_name': 'Harshini Waththala Gunathilaka',
		'country': None,
		'role': 'Executive Assistant',
		'date_started': '06-Dec-2022'
		},
		{
		'email': 'jyotisirswa@gmail.com',
		'full_name': 'Jyoti Sirswa',
		'country': None,
		'role': 'iOS Developer',
		'date_started': '08-Dec-2022'
		}
	]

	total_rows = 0
	existing_erp_count = 0
	new_erp_entry = 0
	existing_users_reset_password_count = 0
	existing_users = []
	new_users = []
	existing_users_reset_password = []
	for row in onboarding_data:
		total_rows += 1
		existing_doc = frappe.get_all("People", filters={"email_address": row['email']}, fields=['name','email_address'])
		if existing_doc:
			existing_erp_count += 1
			existing_users.append(existing_doc[0].email_address)
			from frappe.core.doctype.user.user import reset_password
			if frappe.get_all("User", filters={"name": row['email']}, fields=["name"]):
				user = frappe.get_doc("User", row['email'])
				talent_portal_logs = frappe.get_all("Talent Portal Activity Log", filters={"user": row['email']}, fields=["name"])
				if not talent_portal_logs:
					user.reset_password(send_email=True, for_portal=1)
					talent_portal_log_status = 'Logged Out'
					talent_portal_last_login = None
					talent_portal_invitation_status = 'Invited'
					talent_portal_invite_date = nowdate()
					talent_portal_user_account_status = 'Inactive'
					frappe.db.set_value('People', row['email'], 'talent_portal_log_status', talent_portal_log_status)
					frappe.db.set_value('People', row['email'], 'talent_portal_last_login', talent_portal_last_login)
					frappe.db.set_value('People', row['email'], 'talent_portal_invitation_status', talent_portal_invitation_status)
					frappe.db.set_value('People', row['email'], 'talent_portal_user_account_status', talent_portal_user_account_status)
					frappe.db.set_value('People', row['email'], 'talent_portal_invite_date', talent_portal_invite_date)
					existing_users_reset_password_count += 1
					existing_users_reset_password.append(existing_doc[0].email_address)
		else:
			new_users.append(row['email'])
			new_erp_entry += 1
			if not frappe.get_all("User", filters={"name": row['email']}, fields=["name"]):
				new_doc = frappe.new_doc("People")
				new_doc.flags.ignore_permissions = True
				new_doc.flags.ignore_links = True
				new_doc.first_name = row['full_name']
				new_doc.people_type = "Consultant"
				new_doc.status = "Active"
				new_doc.create_user = 1
				new_doc.country = row['country']
				new_doc.append('email', {'email': row['email']})
				new_doc.user_send_welcome_email = 0
				new_doc.user_send_welcome_email_talent_portal = 1
				try:
					new_doc.insert()
					talent_portal_log_status = 'Logged Out'
					talent_portal_last_login = None
					talent_portal_invitation_status = 'Invited'
					talent_portal_invite_date = nowdate()
					talent_portal_user_account_status = 'Inactive'
					frappe.db.set_value('People', row['email'], 'talent_portal_log_status', talent_portal_log_status)
					frappe.db.set_value('People', row['email'], 'talent_portal_last_login', talent_portal_last_login)
					frappe.db.set_value('People', row['email'], 'talent_portal_invitation_status', talent_portal_invitation_status)
					frappe.db.set_value('People', row['email'], 'talent_portal_user_account_status', talent_portal_user_account_status)
					frappe.db.set_value('People', row['email'], 'talent_portal_invite_date', talent_portal_invite_date)
				except:
					pass
			#print(row_data)
	print("Total Rows: "+str(total_rows)+", Existing in ERP: "+str(existing_erp_count)+", Reset Existing Users: "+str(existing_users_reset_password_count)+", New ERP Entry: "+str(new_erp_entry))
	print("Existing users: "+str(existing_users))
	print("Reset Existing Users: "+str(existing_users_reset_password))
	print("New users: "+str(new_users))

#erpyoupal.erpyoupal.doctype.people.people.patch_people_tables
@frappe.whitelist()
def patch_people_tables():
	peoples = frappe.get_all('People', fields=['name'])
	for row in peoples:
		doc = frappe.get_doc('People', row.name)
		if doc.email:
			for row_email in doc.email:
				doc.append('people_email', {
					'email': row_email.get('email')
				})
		if doc.mobile:
			for row_mobile in doc.mobile:
				doc.append('people_mobile', {
					'mobile': row_mobile.get('mobile')
				})
		doc.flags.ignore_permissions = True
		doc.flags.ignore_links = True
		doc.save()

#erpyoupal.erpyoupal.doctype.people.people.patch_repeople_tables
@frappe.whitelist()
def patch_repeople_tables():
	peoples = frappe.get_all('People', fields=['name'])
	for row in peoples:
		doc = frappe.get_doc('People', row.name)
		if doc.people_email:
			for row_email in doc.people_email:
				doc.append('email', {
					'email': row_email.get('email')
				})
		if doc.people_mobile:
			for row_mobile in doc.people_mobile:
				doc.append('mobile', {
					'mobile': row_mobile.get('mobile')
				})
		doc.flags.ignore_permissions = True
		doc.flags.ignore_links = True
		doc.save()

#erpyoupal.erpyoupal.doctype.people.people.patch_populate_portal_status
@frappe.whitelist()
def patch_populate_portal_status():
	talent_invited = {
		'dorilyn15@gmail.com': '2022-10-21 16:00:30.613515',
		'zikrilloislomov@gmail.com': '2022-10-21 15:56:31.353319',
		'onipko32@gmail.com': '2022-10-21 15:56:29.368195',
		'sherath8@gmail.com': '2022-10-21 15:56:27.317014',
		'kicheodinga@gmail.com': '2022-10-21 15:56:25.177264',
		'shievasaavedra28@gmail.com': '2022-10-21 15:56:23.080268',
		'shalini10april@gmail.com': '2022-10-21 15:56:21.137524',
		'shah.shah.2001.22@gmail.com': '2022-10-21 15:56:18.569026',
		'sara.upworkid@gmail.com': '2022-10-21 15:56:16.328029',
		'birwalsandeep@gmail.com': '2022-10-21 15:56:13.433781',
		'sanal.k@youpal.es': '2022-10-21 15:56:10.768099',
		'itszaidi@gmail.com': '2022-10-21 15:56:08.773255',
		'razv4n.bogdan@yahoo.com': '2022-10-21 15:56:06.261369',
		'rawat.ranvirsingh@gmail.com': '2022-10-21 15:56:03.968265',
		'rajka@youpal.se': '2022-10-21 15:56:02.152849',
		'oleh.ch@youpal.se': '2022-10-21 15:55:59.631558',
		'nizreen.ismail@gmail.com': '2022-10-21 15:55:57.184424',
		'natalia4rn@gmail.com': '2022-10-21 15:55:54.460139',
		'gospodin.p.zh@gmail.com': '2022-10-21 15:55:52.118600',
		'mumtozvalijonov@gmail.com': '2022-10-21 15:55:49.350198',
		'melvin.mathews@hotmail.com': '2022-10-21 15:55:47.040405',
		'marianna.karapetyan@gmail.com': '2022-10-21 15:55:44.546475',
		'marat@youpal.se': '2022-10-21 15:55:41.882870',
		'lev.ananikyan@gmail.com': '2022-10-21 15:55:37.379663',
		'kkumaren@gmail.com': '2022-10-21 15:55:35.013014',
		'kb.nawaz@gmail.com': '2022-10-21 15:55:32.339241',
		'k.pirumyan@gmail.com': '2022-10-21 15:55:29.658744',
		'dyenlouie03@gmail.com': '2022-10-21 15:55:27.120943',
		'joeljeru1@gmail.com': '2022-10-21 15:55:24.946943',
		'jessical__@hotmail.com': '2022-10-21 15:55:22.269050',
		'jtosino@yahoo.com': '2022-10-21 15:55:19.157343',
		'henrik.albrechtsson@gmail.com': '2022-10-21 15:55:16.411801',
		'gustaffndalo@gmail.com': '2022-10-21 15:55:13.539038',
		'floris@040lab.com': '2022-10-21 15:55:10.714912',
		'dorilyn15@gmail.com': '2022-10-21 15:51:58.893864',
		'dilan@youpal.se': '2022-10-21 15:51:56.807749',
		'trincudan@gmail.com': '2022-10-21 15:51:54.856503',
		'khanazhar70@gmail.com': '2022-10-21 15:51:52.568145',
		'berdartem@gmail.com': '2022-10-21 15:51:50.458650',
		'aposarga@gmail.com': '2022-10-21 15:51:48.317621',
		'interact2amit@gmail.com': '2022-10-21 15:51:45.770039',
		'adhammagdy.dev@gmail.com': '2022-10-21 15:51:43.835496',
		'abderazakhouaiss@gmail.com': '2022-10-21 15:51:41.900898',
		'ruben@youpal.se': '2022-10-21 15:51:38.942267',
		'cidzaragoza@yahoo.com': '2022-10-21 15:50:08.698938',
	}

	peoples = frappe.get_all('People', fields=['name','email_address','talent_portal_access','partner_portal_access','client_portal_access'])
	for row in peoples:
		talent_portal_log_status = 'Logged Out'
		talent_portal_last_login = None
		talent_portal_invitation_status = 'Not Invited'
		talent_portal_invite_date = None
		talent_portal_user_account_status = 'Inactive'
		
		partner_portal_log_status = 'Logged Out'
		partner_portal_last_login = None
		partner_portal_invitation_status = 'Not Invited'
		partner_portal_invite_date = None
		partner_portal_user_account_status = 'Inactive'

		client_portal_log_status = 'Logged Out'
		client_portal_last_login = None
		client_portal_invitation_status = 'Not Invited'
		client_portal_invite_date = None
		client_portal_user_account_status = 'Inactive'

		if row.email_address in talent_invited:
			talent_portal_invitation_status = 'Invited'
			talent_portal_invite_date = talent_invited[row.email_address]

		user_doc = frappe.get_all('User', filters={'name': row.email_address}, fields=['name', 'enabled'])
		if row.talent_portal_access:
			if user_doc and user_doc[0].enabled:
				talent_portal_user_account_status = 'Active'
		if row.partner_portal_access:
			if user_doc and user_doc[0].enabled:
				partner_portal_user_account_status = 'Active'
		if row.client_portal_access:
			if user_doc and user_doc[0].enabled:
				client_portal_user_account_status = 'Active'
		
		frappe.db.set_value('People', row.name, 'talent_portal_log_status', talent_portal_log_status)
		frappe.db.set_value('People', row.name, 'talent_portal_last_login', talent_portal_last_login)
		frappe.db.set_value('People', row.name, 'talent_portal_invitation_status', talent_portal_invitation_status)
		frappe.db.set_value('People', row.name, 'talent_portal_user_account_status', talent_portal_user_account_status)
		frappe.db.set_value('People', row.name, 'talent_portal_invite_date', talent_portal_invite_date)

		frappe.db.set_value('People', row.name, 'partner_portal_log_status', partner_portal_log_status)
		frappe.db.set_value('People', row.name, 'partner_portal_last_login', partner_portal_last_login)
		frappe.db.set_value('People', row.name, 'partner_portal_invitation_status', partner_portal_invitation_status)
		frappe.db.set_value('People', row.name, 'partner_portal_invite_date', partner_portal_invite_date)
		frappe.db.set_value('People', row.name, 'partner_portal_user_account_status', partner_portal_user_account_status)

		frappe.db.set_value('People', row.name, 'client_portal_log_status', client_portal_log_status)
		frappe.db.set_value('People', row.name, 'client_portal_last_login', client_portal_last_login)
		frappe.db.set_value('People', row.name, 'client_portal_invitation_status', client_portal_invitation_status)
		frappe.db.set_value('People', row.name, 'client_portal_invite_date', client_portal_invite_date)
		frappe.db.set_value('People', row.name, 'client_portal_user_account_status', client_portal_user_account_status)

		frappe.db.commit()

#erpyoupal.erpyoupal.doctype.people.people.patch_populate_talent_portal_status
@frappe.whitelist()
def patch_populate_talent_portal_status():
	talent_invited = {
		"harshinigunathilaka94@gmail.com": "2023-01-16 18:02:51",
		"onipko32@gmail.com": "2023-01-16 18:02:49",
		"sherath8@gmail.com": "2023-01-16 18:02:49",
		"kicheodinga@gmail.com": "2023-01-16 18:02:48",
		"shievasaavedra28@gmail.com": "2023-01-16 18:02:47",
		"shahalam7303@gmail.com": "2023-01-16 18:02:45",
		"sara.upworkid@gmail.com": "2023-01-16 18:02:44",
		"birwalsandeep@gmail.com": "2023-01-16 18:02:42",
		"sanal.k@youpal.es": "2023-01-16 18:02:41",
		"itszaidi@gmail.com": "2023-01-16 18:02:40",
		"razv4n.bogdan@yahoo.com": "2023-01-16 18:02:39",
		"rawat.ranvirsingh@gmail.com": "2023-01-16 18:02:38",
		"rajka@youpal.se": "2023-01-16 18:02:37",
		"oleh.ch@youpal.se": "2023-01-16 18:02:35",
		"natalia4rn@gmail.com": "2023-01-16 18:02:35",
		"gospodin.p.zh@gmail.com": "2023-01-16 18:02:33",
		"mumtozvalijonov@gmail.com": "2023-01-16 18:02:30",
		"melvin.mathews@hotmail.com": "2023-01-16 18:02:29",
		"marianna.karapetyan@gmail.com": "2023-01-16 18:02:28",
		"marat@youpal.se": "2023-01-16 18:02:27",
		"lev.ananikyan@gmail.com": "2023-01-16 18:02:25",
		"kkumaren@gmail.com": "2023-01-16 18:02:25",
		"kb.nawaz@gmail.com": "2023-01-16 18:02:24",
		"k.pirumyan@gmail.com": "2023-01-16 18:02:23",
		"diazjohnmatthew@gmail.com": "2023-01-16 18:02:22",
		"dyenlouie03@gmail.com": "2023-01-16 18:02:20",
		"jessical__@hotmail.com": "2023-01-16 18:02:19",
		"jtosino@yahoo.com": "2023-01-16 18:02:19",
		"henrik.albrechtsson@gmail.com": "2023-01-16 18:02:18",
		"gustaffndalo@gmail.com": "2023-01-16 18:02:17",
		"floris@040lab.com": "2023-01-16 18:02:16",
		"dilan@youpal.se": "2023-01-16 18:02:15",
		"khanazhar70@gmail.com": "2023-01-16 18:02:14",
		"berdartem@gmail.com": "2023-01-16 18:02:14",
		"aposarga@gmail.com": "2023-01-16 18:02:14",
		"adhammagdy.dev@gmail.com": "2023-01-16 18:02:13",
		"ruben@youpal.se": "2023-01-16 18:02:12",
		"james.bakerduly@gmail.com": "2023-01-16 18:02:12",
		"dilan@youpal.se": "2023-01-16 17:57:23",
		"khanazhar70@gmail.com": "2023-01-16 17:57:22",
		"berdartem@gmail.com": "2023-01-16 17:57:21",
		"aposarga@gmail.com": "2023-01-16 17:57:20",
		"adhammagdy.dev@gmail.com": "2023-01-16 17:57:19",
		"ruben@youpal.se": "2023-01-16 17:57:19",
		"james.bakerduly@gmail.com": "2023-01-16 17:57:18"
	}
	for row in talent_invited:
		existing_doc = frappe.get_all("People", filters={"email_address": row}, fields=['name','email_address'])
		if existing_doc:
			talent_portal_invite_date = talent_invited[row]
			frappe.db.set_value('People', existing_doc[0].name, 'talent_portal_invite_date', talent_portal_invite_date)
			frappe.db.set_value('People', existing_doc[0].name, 'talent_portal_invitation_status', 'Invited')

#erpyoupal.erpyoupal.doctype.people.people.patch_remove_test_people_data
@frappe.whitelist()
def patch_remove_test_people_data():
	result = {
		"total_poeple_deleted": 0,
		"total_it_consultant_deleted": 0,
		"total_job_applicant_deleted": 0,
		"total_connected_doc_deleted": 0,
		"deleted_people_list": [],
		"deleted_it_consultant_list": [],
		"deleted_job_applicant_list": [],
		"deleted_connected_doc_list": []
	}
	default_filters = [['name', 'like', '%test%']]
	final_filters = []
	if not final_filters:
		final_filters = default_filters
	people_list = frappe.get_all("People", filters=final_filters, fields=["name", "email_address"])
	for row_pl in people_list:
		#delete all connected it consultant to people
		it_consultant_list = frappe.get_all("IT Consultant", filters={"email_primary": row_pl.email_address}, fields=["name"])
		for row_icl in it_consultant_list:
			#delete all connected documents to it consultant
			it_consultant_connected_docs = frappe.db.sql("SELECT DF.`name`,DF.`parent`,DF.`fieldname`,DT.`istable` FROM `tabDocField` DF INNER JOIN `tabDocType` DT ON DF.`parent`=DT.`name` WHERE DF.`options`='IT Consultant' AND DT.`istable`=0 AND DF.`parent`!='Job Applicant' ", as_dict=1)
			if it_consultant_connected_docs:
				for row_iccd in it_consultant_connected_docs:
					row_iccd_list = frappe.get_all(row_iccd.parent, filters={row_iccd.fieldname: row_icl.name}, fields=["name"])
					if row_iccd_list:
						for row_doc_iccd_list in row_iccd_list:
							#finally delete connected doc
							if frappe.get_all(row_iccd.parent, filters={"name": row_doc_iccd_list.name}, fields=["name"]):
								frappe.delete_doc(row_iccd.parent, row_doc_iccd_list.name, force=1)
								#doc_to_del = frappe.get_doc(row_iccd.parent, row_doc_iccd_list.name)
								#doc_to_del.flags.ignore_permissions = True
								#doc_to_del.flags.ignore_links = True
								#doc_to_del.delete()
								#frappe.db.commit()
								if str(row_iccd.parent) in ["Job Applicant"]:
									result["total_job_applicant_deleted"] += 1
									result["deleted_job_applicant_list"].append(row_doc_iccd_list.name)
								else:
									result["total_connected_doc_deleted"] += 1
									result["deleted_connected_doc_list"].append(row_doc_iccd_list.name)
			#get connectd job applicants
			job_applicant_list = frappe.get_all("Job Applicant", filters={"email_id": row_pl.email_address}, fields=["name"])
			for row_jal in job_applicant_list:
				job_applicant_connected_docs = frappe.db.sql("""SELECT DF.`name`,DF.`parent`,DF.`fieldname`,DT.`istable` 
					FROM `tabDocField` DF INNER JOIN `tabDocType` DT ON DF.`parent`=DT.`name` 
					WHERE DF.`options`='Job Applicant' AND DT.`istable`=0 
					AND (DF.`parent`='Lead Candidate' OR
					DF.`parent`='Background Check' OR
					DF.`parent`='Skill Test' OR
					DF.`parent`='Persona Test' OR
					DF.`parent`='Skill Test Coderbyte' OR
					DF.`parent`='Video Interview' OR
					DF.`parent`='Candidate Interview' OR
					DF.`parent`='Self Evaluation' OR
					DF.`parent`='Google Drive Resume') """, as_dict=1)
				if job_applicant_connected_docs:
					for row_jacd in job_applicant_connected_docs:
						row_jacd_list = frappe.get_all(row_jacd.parent, filters={row_jacd.fieldname: row_jal.name}, fields=["name"])
						if row_jacd_list:
							for row_rjl in row_jacd_list:
								#finally deleted connected docs to job applicant
								if frappe.get_all(row_iccd.parent, filters={"name": row_rjl.name}, fields=["name"]):
									frappe.delete_doc(row_iccd.parent, row_rjl.name, force=1)
									#jac_doc_to_del = frappe.get_doc(row_iccd.parent, row_rjl.name)
									#jac_doc_to_del.flags.ignore_permissions = True
									#jac_doc_to_del.flags.ignore_links = True
									#jac_doc_to_del.delete()
									#frappe.db.commit()
									result["total_connected_doc_deleted"] += 1
									result["deleted_connected_doc_list"].append(row_rjl.name)
			#finally delete it consultant doc
			if frappe.get_all("IT Consultant", filters={"name": row_icl.name}, fields=["name"]):
				frappe.delete_doc("IT Consultant", row_icl.name, force=1)
				#it_consultant_doc_to_del = frappe.get_doc("IT Consultant", row_icl.name)
				#it_consultant_doc_to_del.flags.ignore_permissions = True
				#it_consultant_doc_to_del.flags.ignore_links = True
				#it_consultant_doc_to_del.delete()
				#frappe.db.commit()
				result["total_it_consultant_deleted"] += 1
				result["deleted_it_consultant_list"].append(row_icl.name)
		#finally delete people doc
		if frappe.get_all("People", filters={"name": row_pl.name}, fields=["name"]):
			frappe.delete_doc("People", row_pl.name, force=1)
			#people_doc_to_del = frappe.get_doc("People", row_pl.name)
			#people_doc_to_del.flags.ignore_permissions = True
			#people_doc_to_del.flags.ignore_links = True
			#people_doc_to_del.delete()
			#frappe.db.commit()
			result["total_poeple_deleted"] += 1
			result["deleted_people_list"].append(row_pl.name)

	return result

#erpyoupal.erpyoupal.doctype.people.people.create_partner_people
@frappe.whitelist(allow_guest=True)
def create_partner_people(data):
	result = None
	if str(data.get('password')) != str(data.get('confirm_password')):
		frappe.throw(_("Password did not match"))
	
	if not data.get('agree_to_terms_and_conditions'):
		frappe.throw(_("You must agree to the terms and conditions"))

	doc = frappe.get_all("People", filters={"email_address": data.get('email')}, fields=["name"])
	if doc:
		pass
	else:
		new_doc = frappe.new_doc("People")
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.people_type = "Business"
		new_doc.status = "Active"
		new_doc.create_user = 1
		new_doc.first_name = data.get("first_name")
		new_doc.last_name = data.get("last_name")
		new_doc.country = data.get("country")
		new_doc.append("email", {"email": data.get("email")})
		new_doc.append("mobile", {"mobile": data.get("mobile")})
		result = new_doc.insert()
		frappe.db.commit()
		user_doc = frappe.get_doc("User", data.get("email"))
		user_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		user_doc.new_password = str(data.get('password'))
		user_doc.save()
	return result
