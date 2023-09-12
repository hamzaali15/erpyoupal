# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import validate_email_address, now, flt
from erpyoupal.events.hr.job_applicant import validate_application_process
from erpyoupal.erpyoupal.doctype.persona_test.persona_test import create_persona_test

class SkillTestCoderbyte(Document):
	def validate(self):
		if self.job_applicant:
			if not self.it_consultant:
				self.email = frappe.db.get_value("Job Applicant",self.job_applicant,"email_id")
				self.it_consultant,self.applicant_name = frappe.db.get_value("IT Consultant",{"email_primary":self.email},["name","full_name"])

			application_process = validate_application_process(job_applicant=self.job_applicant)
			if application_process in ['assessment_first']:
				entry = {
					"job_applicant": self.job_applicant,
					"applicant_name": self.applicant_name,
					"email": self.email
				}
				create_persona_test(entry)
		frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=self.it_consultant, queue='long', timeout=300, now=False)

@frappe.whitelist(allow_guest=True)
def create_skill_test(assessment_id,job_applicant=None,it_consultant=None):
	# if not frappe.get_all('Skill Test Coderbyte', filters={'email': frappe.get_value('Job Applicant', job_applicant, 'email_id'), 'assessment_title': assessment_id}, fields=['name']):
	new_doc = frappe.new_doc('Skill Test Coderbyte')
	new_doc.it_consultant = it_consultant
	new_doc.job_applicant = job_applicant
	new_doc.applicant_name = frappe.get_value('Job Applicant', job_applicant, 'applicant_name')
	new_doc.email = frappe.get_value('Job Applicant', job_applicant, 'email_id')
	new_doc.date_created = now()
	new_doc.assessment_title = assessment_id
	new_doc.assessment_link = frappe.get_value('Coderbyte Assessments', assessment_id, 'assessment_link')
	new_doc.flags.ignore_permissions = True
	new_doc.save()