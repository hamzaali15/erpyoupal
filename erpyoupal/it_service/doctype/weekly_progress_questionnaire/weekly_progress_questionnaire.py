# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WeeklyProgressQuestionnaire(Document):
	def validate(self):
		if self.is_new():
			self.set_default_questions()
		self.update_status()

	def set_default_questions(self):
		self.questionnaire = None
		default_questions = [
			"Do you have an understanding of the assignment requirements to fulfill?",
			"Do you have access to all the needed environments you need in order to do your tasks effectively?",
			"From a PM perspective have you been invited to the all required meetings so you have a regular update on your progress?",
			"Have you participated in all the necessary meetings?",
			"Do you feel confident with tasks that you have been delegated to perform?"
		]
		for row in default_questions:
			self.append('questionnaire', {
				'question': row,
				'answer': None
			})

	def validate_duplicate_entry(self):
		pass
	
	def update_status(self):
		is_completed = 1
		for row in self.questionnaire:
			if not row.answer:
				is_completed = 0
		
		if not is_completed:
			self.status  = "Pending"
		else:
			self.status  = "Completed"

#erpyoupal.it_service.doctype.weekly_progress_questionnaire.weekly_progress_questionnaire.get_unanswered_questions
@frappe.whitelist()
def get_unanswered_questions(it_consultant):
	result = []
	wpq_list = frappe.get_all('Weekly Progress Questionnaire', filters={'it_consultant': it_consultant}, fields=['name'])
	if wpq_list:
		doc = frappe.get_doc('Weekly Progress Questionnaire', wpq_list[0].name)
		if doc.questionnaire:
			for row in doc.questionnaire:
				if not row.answer:
					result.append(row.question)
	frappe.local.response.update({"data": result})
	#return result

@frappe.whitelist()
def create_weekly_progress_questionnaire(it_consultant):
	if not frappe.get_all('Weekly Progress Questionnaire', filters={'it_consultant': it_consultant}, fields=['name']):
		new_doc = frappe.new_doc('Weekly Progress Questionnaire')
		new_doc.it_consultant = it_consultant
		new_doc.email = frappe.db.get_value('IT Consultant', it_consultant, 'email_primary')
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.insert()

#erpyoupal.it_service.doctype.weekly_progress_questionnaire.weekly_progress_questionnaire.submit_answer
@frappe.whitelist()
def submit_answer(it_consultant, question, answer):
	wpq_list = frappe.get_all('Weekly Progress Questionnaire', filters={'it_consultant': it_consultant}, fields=['name'])
	if wpq_list:
		doc = frappe.get_doc('Weekly Progress Questionnaire', wpq_list[0].name)
		if doc.questionnaire:
			for row in doc.questionnaire:
				if str(row.question) == str(question):
					row.answer = answer
		doc.flags.ignore_permissions = True
		doc.flags.ignore_links = True
		result = doc.save()
		frappe.local.response.update({"data": result})
		#return result

#erpyoupal.it_service.doctype.weekly_progress_questionnaire.weekly_progress_questionnaire.patch_create_weekly_progress_questionnaires
@frappe.whitelist()
def patch_create_weekly_progress_questionnaires():
	it_list = frappe.get_all('IT Consultant', fields=['name'])
	for row in it_list:
		create_weekly_progress_questionnaire(it_consultant=row.name)