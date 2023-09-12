# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from dataclasses import field
from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import nowdate, getdate, now_datetime, get_datetime, get_site_name
from erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects import assign_user_to_erp_members

class LeadCandidate(Document):
	def before_insert(self):
		it_consultant = None
		if self.candidate:
			it_consultant = self.candidate[0].it_consultant
		if not self.it_consultant:
			self.it_consultant = it_consultant
		email_primary = frappe.get_value("IT Consultant", self.it_consultant, "email_primary")
		if email_primary:
			peoples = frappe.get_all("People", filters={"email_address": email_primary}, fields=["name"])
			if peoples:
				self.people = peoples[0].name
		self.get_cv_pdf_link()
		if not self.title_field:
			self.title_field = self.name

	def validate(self):
		if self.generated_from_lead:
			if frappe.get_all('Lead Custom', filters={'name': self.generated_from_lead}, fields=['name']):
				self.generated_by = frappe.db.get_value('Lead Custom', self.generated_from_lead, 'organization')
		self.create_delay_email()
		self.get_cv_pdf_link()
		if not self.title_field:
			self.title_field = self.name
		self.save_candidate_to_oraganization()
		self.unsave_candidate_to_oraganization()
		self.get_image_from_it_consultant()
		self.get_job_applicant_data()
		self.create_interview_calendar_event()
		self.save_lead_custom()

		old_stage = frappe.db.sql("""SELECT stages FROM `tabLead Candidate` WHERE `name` = %s""",(self.name),as_dict=True)
		if old_stage:
			old_stage = old_stage[0].stages
			if old_stage != self.stages:
				it_consultant = ""
				for can in self.candidate:
					it_consultant = can.it_consultant
				if it_consultant:
					applied_jobs,matched_jobs,in_progress_jobs,hired_jobs,rejected_jobs = frappe.db.get_value('IT Consultant', it_consultant, ["applied_jobs","matched_jobs","in_progress_jobs","hired_jobs","rejected_jobs"])
					if self.stages == "Applied":
						frappe.db.set_value('IT Consultant', it_consultant, 'applied_jobs', applied_jobs+1)
					elif self.stages == "Matched":
						frappe.db.set_value('IT Consultant', it_consultant, 'matched_jobs', matched_jobs+1)
					elif self.stages == "Hired":
						frappe.db.set_value('IT Consultant', it_consultant, 'hired_jobs', hired_jobs+1)
					elif self.stages == "Rejected":
						frappe.db.set_value('IT Consultant', it_consultant, 'rejected_jobs', rejected_jobs+1)
					else:
						frappe.db.set_value('IT Consultant', it_consultant, 'in_progress_jobs', in_progress_jobs+1)

					if old_stage == "Applied":
						frappe.db.set_value('IT Consultant', it_consultant, 'applied_jobs', applied_jobs-1)
					elif old_stage == "Matched":
						frappe.db.set_value('IT Consultant', it_consultant, 'matched_jobs', matched_jobs-1)
					elif old_stage == "Hired":
						frappe.db.set_value('IT Consultant', it_consultant, 'hired_jobs', hired_jobs-1)
					elif old_stage == "Rejected":
						frappe.db.set_value('IT Consultant', it_consultant, 'rejected_jobs', rejected_jobs-1)
					else:
						frappe.db.set_value('IT Consultant', it_consultant, 'in_progress_jobs', in_progress_jobs-1)

	def create_delay_email(self):
		count = frappe.db.sql("""SELECT COUNT(`name`) as email_count FROM `tabLead Candidate Email Queue` WHERE creation >= %s AND linked_document = %s """,(datetime.now() - timedelta(hours=12),self.name),as_dict=True)
		old_stage = frappe.db.get_value("Lead Candidate",self.name,"stages")
		if old_stage != self.stages and self.stages in ["Matched","Rejected"] and count[0]['email_count'] < 1:
			delay_email = frappe.new_doc("Lead Candidate Email Queue")
			delay_email.linked_document = self.name
			delay_email.subject = "Lead Candidate "+self.name+" Status Changed to "+self.stages
			delay_email.message = "Lead Candidate "+self.name+" Status Changed to "+self.stages
			if self.stages == "Matched":
				delay_email.recipient = frappe.session.user
				delay_email.delay = "12h"
			else:
				delay_email.recipient = self.generated_from_job_applicant.split("-")[1].strip()
				delay_email.delay = "24h"
			delay_email.insert()

	def save_lead_custom(self):
		if frappe.get_all("Lead Custom", filters={"name": self.generated_from_lead}):
			doc = frappe.get_doc("Lead Custom", self.generated_from_lead)
			doc.flags.ignore_permissions = True
			doc.flags.ignore_links = True
			doc.save()

	def after_insert(self):
		self.save_stage_status()

		organization = None
		email_primary = None
		if self.generated_from_lead:
			organization = frappe.db.get_value('Lead Custom', self.generated_from_lead, 'organization')
		if self.generated_by:
			organization = self.generated_by
		if self.it_consultant:
			email_primary = frappe.db.get_value('IT Consultant', self.it_consultant, 'email_primary')
		if email_primary and organization:
			client_rate = 0
			if self.candidate:
				for row in self.candidate:
					client_rate = self.candidate[0].client_rate
			try:
				assign_user_to_erp_members(user=email_primary, organization=organization, rate=client_rate)
			except:
				pass

		# old_stage = frappe.db.sql("""SELECT stages FROM `tabLead Candidate` WHERE `name` = %s""",(self.name),as_dict=True)
		# new_stage = self.stages
		it_consultant = ""
		for can in self.candidate:
			it_consultant = can.it_consultant
		if it_consultant:
			applied_jobs,matched_jobs,in_progress_jobs,hired_jobs,rejected_jobs = frappe.db.get_value('IT Consultant', it_consultant, ["applied_jobs","matched_jobs","in_progress_jobs","hired_jobs","rejected_jobs"])
			if self.stages == "Applied":
				frappe.db.set_value('IT Consultant', it_consultant, 'applied_jobs', applied_jobs+1)
			elif self.stages == "Matched":
				frappe.db.set_value('IT Consultant', it_consultant, 'matched_jobs', matched_jobs+1)
			elif self.stages == "Hired":
				frappe.db.set_value('IT Consultant', it_consultant, 'hired_jobs', hired_jobs+1)
			elif self.stages == "Rejected":
				frappe.db.set_value('IT Consultant', it_consultant, 'rejected_jobs', rejected_jobs+1)
			else:
				frappe.db.set_value('IT Consultant', it_consultant, 'in_progress_jobs', in_progress_jobs+1)
		
	def on_update(self):
		self.save_stage_status()

	def on_trash(self):
		self.save_stage_status(deduct_own_doc=1)

	def get_job_applicant_data(self):
		if self.candidate and self.candidate[0].it_consultant:
			job_applicant_data = frappe.get_all("Job Applicant", filters={"it_consultant": self.candidate[0].it_consultant}, fields=['name', 'rate'])
			if job_applicant_data:
				self.generated_from_job_applicant = job_applicant_data[0].name
				if self.candidate:
					for row in self.candidate:
						row.rate = job_applicant_data[0].rate

	def save_stage_status(self, deduct_own_doc=0):
		from erpyoupal.erpyoupal.doctype.lead_custom.lead_custom import save_candidate_stages_status
		deduct_stages = None
		if deduct_own_doc:
			deduct_stages = {self.stages: 1}
		save_candidate_stages_status(self.generated_from_lead, is_db_update=1, deduct_stages=deduct_stages)

	def get_image_from_it_consultant(self):
		if not self.candidate_image and self.it_consultant:
			self.candidate_image = frappe.get_value("IT Consultant", self.it_consultant, "image")

	def get_cv_pdf_link(self):
		if self.candidate:
			it_consultant = self.candidate[0].it_consultant
			if it_consultant:
				self.cv_pdf_link = "https://erp.youpal.se/api/method/frappe.utils.print_format.download_pdf?doctype=IT%20Consultant&name="+it_consultant+"&format=Resume&no_letterhead=0&letterhead=youpal&settings={}&_lang=en"

	def validate_saving_to_organization(self):
		if not self.generated_by:
			frappe.throw(_("No Organization linked"))
		if not self.candidate:
			frappe.throw(_("No Candidate found"))

		it_consultant = self.candidate[0].it_consultant

		organizations = frappe.get_all("Organizations", filters={"name": self.generated_by}, fields=["name"])
		if not organizations:
			frappe.throw(_("Organization cannot be found"))
		
		return organizations, it_consultant

	def save_candidate_to_oraganization(self):
		if self.candidate_is_saved and not frappe.get_value("Lead Candidate", self.name, "candidate_is_saved"):
			organizations, it_consultant = self.validate_saving_to_organization()
			if organizations:
				organization = frappe.get_doc("Organizations", organizations[0].name)
				existing_candidates = []
				if organization.save_candidate:
					for cand in organization.save_candidate:
						existing_candidates.append(cand.it_consultant)

				if it_consultant in existing_candidates:
					frappe.msgprint(_("Candidate is already saved"))
				
				if it_consultant not in existing_candidates:
					organization.append('save_candidate', {
						'it_consultant': it_consultant
					})
					organization.flags.ignore_permissions = True
					if organization.save():
						frappe.db.sql(""" UPDATE `tabLead Candidate` LC INNER JOIN `tabLead Candidates Table` LCT ON LC.`name`=LCT.`parent`
							SET LC.`candidate_is_saved`=1
							WHERE LC.`generated_by`=%s AND LCT.`it_consultant`=%s """,(self.generated_by, it_consultant))
						frappe.msgprint(_("Candidate saved"))
	
	def unsave_candidate_to_oraganization(self):
		if not self.candidate_is_saved and frappe.get_value("Lead Candidate", self.name, "candidate_is_saved"):
			organizations, it_consultant = self.validate_saving_to_organization()
			other_lead_candidates = frappe.db.sql(""" SELECT LCT.`parent`, LCT.`it_consultant`, LC.`candidate_is_saved`
				FROM `tabLead Candidates Table` LCT INNER JOIN `tabLead Candidate` LC ON LCT.`parent`=LC.`name`
				WHERE LCT.`parenttype`='Lead Candidate' AND LCT.`parentfield`='candidate' AND LCT.`parent`!=%s 
				AND LC.`candidate_is_saved`=1 AND LCT.`it_consultant`=%s """,(self.name, it_consultant) , as_dict=1)

			if organizations:
				organization = frappe.get_doc("Organizations", organizations[0].name)
				existing_candidates = []
				candidate_to_remove = None
				if organization.save_candidate:
					for cand in organization.save_candidate:
						existing_candidates.append(cand.it_consultant)
						candidate_to_remove = cand
					
				if it_consultant in existing_candidates and candidate_to_remove and not other_lead_candidates:
					organization.save_candidate.remove(candidate_to_remove)
					organization.flags.ignore_permissions = True
					if organization.save():
						frappe.msgprint(_("Candidate unsaved"))

	def create_interview_calendar_event(self):
		if self.dates and self.generated_by:
			people = frappe.get_all("People", filters={"is_primary_contact_person": 1, "organization_name": self.generated_by}, fields=['name', 'user', 'google_calendar'])
			if people:
				people = people[0]

			if people and people.google_calendar:
				for row in self.dates:
					if row.enabled:
						if not row.google_calendar:
							row.google_calendar = people.google_calendar

						if not row.event and row.google_calendar:
							#Create interview Event
							starts_on = get_datetime(str(getdate(row.date))+" "+str(row.available_from))
							ends_on = get_datetime(str(getdate(row.date))+" "+str(row.available_to))

							new_event = frappe.new_doc("Event")
							new_event.flags.ignore_permissions = True
							new_event.subject = "Booked Interview"
							new_event.event_category = "Meeting"
							new_event.event_type = "Private"
							new_event.create_google_meet_conference = 1
							new_event.starts_on = starts_on
							new_event.ends_on = ends_on
							new_event.status = "Open"
							new_event.sync_with_google_calendar = 1
							new_event.google_calendar = people.google_calendar
							new_event.description = f"Booked Interview\nStarts On : {starts_on}\nEnds On : {ends_on}"
							if self.it_consultant:
								new_event.append('event_attendees', {
										'attendee_email': frappe.get_value("IT Consultant", self.it_consultant, "email_primary"),
										'attendee_name': frappe.get_value("IT Consultant", self.it_consultant, "full_name")
									})
							if new_event.insert():
								row.event = new_event.name

	@frappe.whitelist()
	def get_original_resume(self):
		resume_link = None
		if frappe.get_all("IT Consultant", filters={"name": self.it_consultant}):
			email_primary = frappe.db.get_value('IT Consultant', self.it_consultant, 'email_primary')
			resume_link = frappe.db.get_value('IT Consultant', self.it_consultant, 'resume')
			if not resume_link and email_primary:
				ja_lists = frappe.get_all("Job Applicant", filters={"email_id": email_primary}, fields=["name", "resume_attachment", "creation"], order_by="creation desc")
				if ja_lists:
					for row in ja_lists:
						if row.resume_attachment:
							resume_link = row.resume_attachment
							break
		if resume_link:
			site_name = get_site_name(frappe.local.request.host)
			resume_link = "https://"+str(site_name)+str(resume_link)
			return resume_link
		else:
			frappe.msgprint("No Resume found")
	
	@frappe.whitelist()
	def go_to_it_consultant(self):
		it_consultants = frappe.get_all("IT Consultant", filters={"name": self.it_consultant}, fields=["name"])
		if it_consultants:
			return it_consultants[0].name
		else:
			return None
	
	@frappe.whitelist()
	def go_to_people(self):
		peoples = frappe.get_all("People", filters={"name": self.people}, fields=["name"])
		if peoples:
			return peoples[0].name
		else:
			return None
	
	@frappe.whitelist()
	def go_to_job_applicant(self):
		job_applicants = frappe.get_all("Job Applicant", filters={"name": self.generated_from_job_applicant}, fields=["name"])
		if job_applicants:
			return job_applicants[0].name
		else:
			return None

#erpyoupal.erpyoupal.doctype.lead_candidate.lead_candidate.get_booked_interviews
@frappe.whitelist(allow_guest=False)
def get_booked_interviews(it_consultant):
	result = []
	lead_candidates = frappe.get_all("Lead Candidate", filters={"it_consultant": it_consultant}, fields=['name'])
	if lead_candidates:
		for lead_candidate in lead_candidates:
			doc = frappe.get_doc("Lead Candidate", lead_candidate.name)
			if doc.dates:
				for booking in doc.dates:
					row = {
						"lead_candidate": doc.name,
						"date": booking.date,
						"d_week": booking.d_week,
						"available_from": booking.available_from,
						"available_to": booking.available_to,
						"enabled": booking.enabled,
						"google_calendar": booking.google_calendar,
						"event": booking.event
					}
					result.append(row)

	return result

#erpyoupal.erpyoupal.doctype.lead_candidate.lead_candidate.get_candidate_data
@frappe.whitelist(allow_guest=False)
def get_candidate_data(lead_candidate):
	result = "Lead Candidate not found"
	if frappe.get_all("Lead Candidate", filters={"name": lead_candidate}):
		result = {}
		lead_candidate_data = None
		it_consultant_data = None
		job_applicant_data = None

		#get datas
		lead_candidate_data = frappe.get_doc("Lead Candidate", lead_candidate)
		if lead_candidate_data.candidate and lead_candidate_data.candidate[0].it_consultant:
			it_consultant_data = frappe.get_doc("IT Consultant", lead_candidate_data.candidate[0].it_consultant)
			job_applicant_data = frappe.get_all("Job Applicant", filters={"it_consultant": lead_candidate_data.candidate[0].it_consultant}, fields=['name'])
			if job_applicant_data:
				job_applicant_data = frappe.get_doc("Job Applicant", job_applicant_data[0].name)

		if lead_candidate_data and it_consultant_data:
			doc_fields=[]
			meta = frappe.get_meta("IT Consultant")
			for i in meta.get("fields"):
				doc_fields.append(i.fieldname)
				result[i.fieldname] = it_consultant_data.get(i.fieldname)
			result["rate"] = it_consultant_data.rate_hourly
			if job_applicant_data:
				if job_applicant_data.rate:
					result["rate"] = job_applicant_data.rate
				result["cv_pdf_link"] = lead_candidate_data.cv_pdf_link
				result["portal_chat_contact"] = lead_candidate_data.portal_chat_contact
				result["lead_candidate_id"] = lead_candidate
				result["stages"] = lead_candidate_data.stages
				result["candidate_is_saved"] = lead_candidate_data.candidate_is_saved
				result["recommendations"] = job_applicant_data.recommendations
				result["availability"] = job_applicant_data.availability

				#GET SELF EVALUATION HISTORY
				it_consultant_data_self_evaluation_history = []
				for icdsehr in it_consultant_data.self_evaluation_history:
					if str(icdsehr.job_applicant_id) in [str(job_applicant_data.name)]:
						if frappe.get_all("Self Evaluation", filters={"name": icdsehr.self_evaluation_id}):
							self_evaluation_data = frappe.get_doc("Self Evaluation", icdsehr.self_evaluation_id)
							it_consultant_data_self_evaluation_history.append(self_evaluation_data)
				result["self_evaluation_history"] = it_consultant_data_self_evaluation_history

				#GET Skill Test HISTORY
				it_consultant_data_skill_test_history = []
				for icd_sth in it_consultant_data.skill_test_history:
					if str(icd_sth.job_applicant_id) in [str(job_applicant_data.name)]:
						if frappe.get_all("Skill Test", filters={"name": icd_sth.skill_test_id}):
							skill_test_data = frappe.get_doc("Skill Test", icd_sth.skill_test_id)
							it_consultant_data_skill_test_history.append(skill_test_data)
				result["skill_test_history"] = it_consultant_data_skill_test_history

				#GET Skill Test Coderbyte HISTORY
				it_consultant_data_skill_test_coderbyte_history = []
				for icd_stch in it_consultant_data.skill_test_coderbyte_history:
					if str(icd_stch.job_applicant_id) in [str(job_applicant_data.name)]:
						if frappe.get_all("Skill Test", filters={"name": icd_stch.skill_test_coderbyte_id}):
							skill_test_coderbyte_data = frappe.get_doc("Skill Test Coderbyte", icd_stch.skill_test_coderbyte_id)
							it_consultant_data_skill_test_coderbyte_history.append(skill_test_coderbyte_data)
				result["skill_test_coderbyte_history"] = it_consultant_data_skill_test_history

				#GET Persona Test History
				it_consultant_data_persona_test_history = []
				for icd_pth in it_consultant_data.persona_test_history:
					if str(icd_pth.job_applicant_id) in [str(job_applicant_data.name)]:
						if frappe.get_all("Persona Test", filters={"name": icd_pth.persona_test_id}):
							persona_test_history_data = frappe.get_doc("Persona Test", icd_pth.persona_test_id)
							it_consultant_data_persona_test_history.append(persona_test_history_data)
				result["persona_test_history"] = it_consultant_data_persona_test_history

				#Get Background Check History
				it_consultant_data_background_check_history = []
				for icd_bch in it_consultant_data.background_check_history:
					if str(icd_bch.job_applicant_id) in [str(job_applicant_data.name)]:
						if frappe.get_all("Background Check", filters={"name": icd_bch.background_check_id}):
							background_check_history_data = frappe.get_doc("Background Check", icd_bch.background_check_id)
							it_consultant_data_background_check_history.append(background_check_history_data)
				result["background_check_history"] = it_consultant_data_background_check_history

				#Get Video Interview History
				it_consultant_data_video_interview_history = []
				for icd_vih in it_consultant_data.video_interview_history:
					if str(icd_vih.job_applicant_id) in [str(job_applicant_data.name)]:
						if frappe.get_all("Video Interview", filters={"name": icd_vih.video_interview_id}):
							video_interview_history_data = frappe.get_doc("Video Interview", icd_vih.video_interview_id)
							it_consultant_data_video_interview_history.append(video_interview_history_data)
				result["video_interview_history"] = it_consultant_data_video_interview_history

				#Get Video Interview History
				it_consultant_data_candidate_interview_history = []
				for icd_cih in it_consultant_data.candidate_interview_history:
					if str(icd_cih.job_applicant_id) in [str(job_applicant_data.name)]:
						if frappe.get_all("Candidate Interview", filters={"name": icd_cih.candidate_interview_id}):
							candidate_interview_history_data = frappe.get_doc("Candidate Interview", icd_cih.candidate_interview_id)
							it_consultant_data_candidate_interview_history.append(candidate_interview_history_data)
				result["candidate_interview_history"] = it_consultant_data_candidate_interview_history

	return result



@frappe.whitelist(allow_guest=False)
def get_candidate_list(lead_custom,stages=None):
	data = {"count":0,"data":[]}
	skills = []
	add_filter = ""
	if stages:
		add_filter += " and LC.stages ='"+stages+"'"
	lead_candidates = frappe.db.sql("""SELECT LC.`name`,LC.candidate_image,LC.candidate_is_saved,(SELECT availability FROM `tabJob Applicant` WHERE `name` = LC.generated_from_job_applicant)as availability,(SELECT it_consultant FROM `tabLead Candidates Table` WHERE parent = LC.`name` LIMIT 1) as it_consultant FROM `tabLead Candidate` LC WHERE LC.generated_from_lead = %s AND LC.hide_in_portal = 0"""+add_filter,(lead_custom),as_dict=True)
	for lead in lead_candidates:
		if frappe.db.exists("IT Consultant",lead.it_consultant):
			doc = frappe.get_doc("IT Consultant",lead.it_consultant)
			bgcheck_status = "UNAPPROVED"
			for check in doc.background_check_history:
				if check.identification_status == "APPROVED":
					bgcheck_status = "APPROVED"
			for s in doc.skills:
				skills.append(s.skill)
			interview = frappe.db.get_list('Candidate Interview History',filters={'parent':lead.it_consultant},pluck='candidate_interview_id')
			data["data"].append({'first_name':doc.first_name,'last_name':doc.last_name,'backgroud_check_status':bgcheck_status,'rate':doc.rate_hourly,'lead_candidate':lead.name,'candidate_image':lead.candidate_image,'it_consultant':lead.it_consultant,'position_title':doc.position_title,'location':doc.location,'availability':lead.availability,'consultant_description':doc.consultant_description,'candidate_is_saved':lead.candidate_is_saved,'skills':skills,'interview':interview})
	data["count"] = len(data["data"])
	return data

#erpyoupal.erpyoupal.doctype.lead_candidate.lead_candidate.get_lead_candidate_by_partner
@frappe.whitelist(allow_guest=False)
def get_lead_candidate_by_partner(partner,stages):
	return frappe.db.sql("""SELECT IC.`name`,LC.it_consultant,IC.image,IC.full_name,IC.rate_hourly,LC.creation FROM `tabLead Candidate` LC INNER JOIN `tabLead Candidates Table` LCT ON LCT.parent = LC.`name` INNER JOIN `tabIT Consultant` IC ON IC.`name` = LCT.it_consultant WHERE LC.generated_by_partner = %s AND LC.stages = %s""",(partner,stages),as_dict=True)

#erpyoupal.erpyoupal.doctype.lead_candidate.lead_candidate.rename_siteurl_resumepdf
@frappe.whitelist(allow_guest=True)
def rename_siteurl_resumepdf():
	doc_lists = frappe.get_all("Lead Candidate", fields=["name", "cv_pdf_link"])
	if doc_lists:
		for row in doc_lists:
			cv_pdf_link = str(row.cv_pdf_link).replace("erp.youpal.tech", "app.youpal.se")
			frappe.db.set_value('Lead Candidate', row.name, 'cv_pdf_link', cv_pdf_link, update_modified=False)

#erpyoupal.erpyoupal.doctype.lead_candidate.lead_candidate.patch_lead_candidates_without_job_applicant
@frappe.whitelist()
def patch_lead_candidates_without_job_applicant():
	doc_lists = frappe.get_all("Lead Candidate", fields=["name", "generated_from_job_applicant", "candidate_source", "it_consultant", "generated_from_job_opening"])
	if doc_lists:
		for row in doc_lists:
			if not row.generated_from_job_applicant and str(row.candidate_source) in ["Public Job Board"]:
				email_primary = frappe.db.get_value('IT Consultant', row.it_consultant, 'email_primary')
				jas = frappe.get_all("Job Applicant", filters={"email_id": email_primary, "job_title": row.generated_from_job_opening}, fields=["name"])
				if jas:
					frappe.db.set_value('Lead Candidate', row.name, 'generated_from_job_applicant', jas[0].name, update_modified=False)

def send_delay_email():
	to_send = frappe.db.sql("""SELECT * FROM `tabLead Candidate Email Queue` WHERE creation <= %s AND status != 'Sent'""",(datetime.now() - timedelta(hours=12)),as_dict=True)
	for s in to_send:
		frappe.sendmail(recipients=s.recipient,subject=s.subject,message="""
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
		<h4>We Have an Update on Your Job Application</h4>
		<br>
		<p>"""+s.message+"""</p>
		<br>
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
		frappe.db.set_value('Lead Candidate Email Queue', s.name, 'status', 'Sent')

def update_lead_candidate_counts():
	it_consultant_dict = {}
	lead_candidates = frappe.db.sql("""SELECT LC.`name`,LCT.it_consultant,LC.stages FROM `tabLead Candidate` LC INNER JOIN `tabLead Candidates Table` LCT""",as_dict=True)
	for lead in lead_candidates:
			if lead.it_consultant:
				if lead.it_consultant not in it_consultant_dict:
					it_consultant_dict[lead.it_consultant] = {"applied_jobs":0,"matched_jobs":0,"in_progress_jobs":0,"hired_jobs":0,"rejected_jobs":0}

				if lead.stages == "Applied":
					it_consultant_dict[lead.it_consultant]["applied_jobs"] += 1
				elif lead.stages == "Matched":
					it_consultant_dict[lead.it_consultant]["matched_jobs"] += 1
				elif lead.stages == "Hired":
					it_consultant_dict[lead.it_consultant]["hired_jobs"] += 1
				elif lead.stages == "Rejected":
					it_consultant_dict[lead.it_consultant]["rejected_jobs"] += 1
				else:
					it_consultant_dict[lead.it_consultant]["in_progress_jobs"] += 1
	for cosultant in it_consultant_dict:
		frappe.db.set_value('IT Consultant', cosultant, 'applied_jobs', it_consultant_dict[cosultant]["applied_jobs"])
		frappe.db.set_value('IT Consultant', cosultant, 'matched_jobs', it_consultant_dict[cosultant]["matched_jobs"])
		frappe.db.set_value('IT Consultant', cosultant, 'hired_jobs', it_consultant_dict[cosultant]["hired_jobs"])
		frappe.db.set_value('IT Consultant', cosultant, 'rejected_jobs', it_consultant_dict[cosultant]["rejected_jobs"])
		frappe.db.set_value('IT Consultant', cosultant, 'in_progress_jobs', it_consultant_dict[cosultant]["in_progress_jobs"])
