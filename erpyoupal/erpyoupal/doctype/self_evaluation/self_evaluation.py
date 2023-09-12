# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
from erpyoupal.erpyoupal.doctype.persona_test.persona_test import create_persona_test
from erpyoupal.events.hr.job_applicant import validate_application_process

class SelfEvaluation(Document):
	def after_insert(self):
		self.save_it_consultant()

	def validate(self):
		self.save_it_consultant()
		if not self.is_new() and self.self_evaluation:
			self.validate_application_process()

		self.status = "Pending"
		if self.self_evaluation:
			self.status = "Completed"

	def validate_application_process(self):
		#If process type is assessment_first
		application_process = validate_application_process(job_applicant=self.job_applicant)
		if application_process in ['assessment_first']:
			entry = {
				"job_applicant": self.job_applicant,
				"applicant_name": frappe.db.get_value('Job Applicant',self.job_applicant,'applicant_name'),
				"email": frappe.db.get_value('Job Applicant',self.job_applicant,'email_id')
			}
			create_persona_test(entry)

	def save_it_consultant(self):
		#Trigger Save it consultant
		it_consultant = frappe.db.get_value("Job Applicant", self.job_applicant, "it_consultant")
		if it_consultant:
			frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=it_consultant, queue='long', timeout=300, now=False)

	def record_self_evaluation_to_itconsultant(self):
		it_consultant = frappe.get_value('Job Applicant', self.job_applicant, 'it_consultant')
		if it_consultant:
			existing_doc = frappe.get_all("IT Consultant", filters={"name": it_consultant}, fields=['name'])
			if existing_doc:
				doc = frappe.get_doc("IT Consultant", existing_doc[0].name)
				doc.append('self_evaluation_history', {
					"self_evaluation_id": self.name,
					"job_applicant_id": self.job_applicant,
					"date_created": self.creation,
					"status": self.self_evaluation_status
					})
				doc.flags.ignore_permissions = True
				doc.save()

@frappe.whitelist(allow_guest=True)
def get_questions(self_evaluation):
	doc = frappe.get_doc('Self Evaluation',self_evaluation)


	final_dict = doc.as_dict()
	for idx,question in enumerate(final_dict["questions"]):
		if question["choices"]:
			final_dict["questions"][idx]["choices"] = question["choices"].split("\n")
	final_dict.update({"applicant_name":frappe.db.get_value('Job Applicant',doc.job_applicant,'applicant_name')})
	final_dict.update({"skill_test":frappe.db.get_value('Job Applicant',doc.job_applicant,'skill_test')})

	return final_dict

