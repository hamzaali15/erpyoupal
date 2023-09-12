# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from dataclasses import field
import json
import random
import frappe
import requests
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address, now, flt, get_datetime
from erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview import create_interview_availability


class VideoInterview(Document):
	def after_insert(self):
		if not self.get("disable_email_sending"):
			if self.email and self.interview_link:
				self.send_email_to_applicant()

	def validate(self):
		self.validate_entry()
		self.interview_link = f"http://interview.youpalgroup.com/welcome/{self.name}"
		if self.is_new() or not self.question_table:
			self.set_questions()

		if not self.is_new() and self.status in ['Completed']:
			self.do_create_interview_availability()

		if self.get("trigger_record_creation_history") or self.is_new() or (frappe.db.get_value("Video Interview", self.name, "status") != self.status):
			self.record_creation_history()

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
	
	def do_create_interview_availability(self):
		to_create = 0
		if self.email:
			peoples = frappe.get_all("People", filters={"email_address": self.email}, fields=["name", "people_type"])
			if peoples:
				if peoples[0].people_type in ["Consultant", "Business / Consultant"]:
					existing_candidate_interviews = frappe.get_all("Candidate Interview", filters={"email": self.email}, fields=["name"])
					if existing_candidate_interviews:
						candidate_interviews_doc = frappe.get_doc("Candidate Interview", existing_candidate_interviews[0].name)
						candidate_interviews_doc.flags.ignore_permissions = True
						candidate_interviews_doc.run_method("send_email")
					else:
						to_create = 1
				else:
					to_create = 1
			else:
				to_create = 1
			
			if to_create:
				create_interview_availability(job_applicant=self.job_applicant)

	def record_creation_history(self):
		for row in self.record_history:
			row.status = "Revised"
		self.append("record_history", {
			"video_interview_id": self.name,
			"job_applicant_id": self.job_applicant,
			"status": self.status,
			"date_created": self.creation
		})

	def save_it_consultant(self):
		#Trigger Save it consultant
		it_consultant = self.it_consultant
		if self.job_applicant and not it_consultant:
			it_consultant = frappe.db.get_value("Job Applicant", self.job_applicant, "it_consultant")
		if it_consultant:
			frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=it_consultant, queue='long', timeout=300, now=False)

	def set_questions(self):
		self.question_table = None
		default_questions = frappe.db.sql("""SELECT question, question_time_limit FROM `tabVideo Questions` WHERE is_default = 1""",as_dict=True)
		non_default_question = frappe.db.sql("""SELECT question, question_time_limit FROM `tabVideo Questions` WHERE is_default = 0""",as_dict=True)

		question_count = 6 if len(default_questions+non_default_question) >= 6 else len(default_questions+non_default_question)
		max_random_question = question_count - len(default_questions)

		random_array = []
		while len(random_array) < max_random_question:
			n = random.randint(0,question_count)
			if not n in random_array:
				random_array.append(n)

		for question in default_questions:
			self.append('question_table', {
				"question": question.question,
				"question_timing":  question.question_time_limit,
				"answer": None,
				"answer_time": None,
			})

		for rnd in random_array:
			self.append('question_table', {
				"question": non_default_question[rnd].question,
				"question_timing":  non_default_question[rnd].question_time_limit,
				"answer": None,
				"answer_time": None,
			})

	def send_email_to_applicant(self):
		frappe.sendmail(recipients=self.email,subject="Video Interview",message= """
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
		        <h4>Attend Video Interview here</h4>
		        <br>
		        <h4>Hey, """+self.applicant_name+"""</h4>
		        <p>We are the global network of top developers, design and</p>
		        <p>bussiness exprerts. With Youpal Group, you'll build an amazing</p>
		        <p>career, wherever you live</p>
		        <br>
		        <a href='"""+self.interview_link+"""' target="_blank"><button type="button">Continue</button></a>
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


#https://erp.youpal.se/api/method/erpyoupal.erpyoupal.doctype.video_interview.video_interview.get_video_interview
#erpyoupal.erpyoupal.doctype.video_interview.video_interview.get_video_interview
@frappe.whitelist(allow_guest=True)
def get_video_interview(docname):
	from erpyoupal.api import get_document_list
	docs = frappe.get_all("Video Interview", filters={"name": docname})
	#docs = get_document_list(doctype="Video Interview", fields=["*"], filters={"name": docname})
	if docs:
		return frappe.get_doc("Video Interview", docname)
	else:
		return "No Document Found"


#https://erp.youpal.se/api/method/erpyoupal.erpyoupal.doctype.video_interview.video_interview.submit_interview_answer
#erpyoupal.erpyoupal.doctype.video_interview.video_interview.submit_interview_answer
@frappe.whitelist(allow_guest=True)
def submit_interview_answer(docname, questions_table, interview_completed=0):
	list_of_answers = questions_table.get('answers')

	docs = frappe.get_all("Video Interview", filters={'name':docname}, fields=['name'])
	if docs and list_of_answers:
		doc = frappe.get_doc("Video Interview", docs[0].name)		
		for row in list_of_answers:
			exis = list(filter(lambda d: str(row["question"]) == str(d.get('question')), doc.question_table))
			if exis:
				table_row = int(flt(exis[0].idx) - 1)
				doc.question_table[table_row].answer = row["answer"]
				doc.question_table[table_row].answer_time = row["answer_time"]
				doc.question_table[table_row].video_url = row["video_url"]
				doc.question_table[table_row].filename = row["filename"]

		doc.status = 'Pending'
		if interview_completed:
			doc.status = 'Completed'

		doc.flags.ignore_permissions = True
		return doc.save()
	else:
		return "No Document Found"


#erpyoupal.erpyoupal.doctype.video_interview.video_interview.retake_video_interview
@frappe.whitelist(allow_guest=True)
def retake_video_interview(video_interview):
	result = None
	if frappe.get_all("Video Interview", filters={"name": video_interview}, fields=["name"]):
		doc = frappe.get_doc("Video Interview", video_interview)
		doc.status = "Pending"
		if doc.question_table:
			for row in doc.question_table:
				row.status = "Revised"
		doc.append("record_history", {
			"video_interview_id": doc.name,
			"job_applicant_id": doc.job_applicant,
			"status": doc.status,
			"date_created": doc.creation
		})
		doc.trigger_record_creation_history = 1
		doc.flags.ignore_permissions = True
		doc.save()
		result = "Success"
	else:
		result = "Video Interview not found"

	return result


#erpyoupal.erpyoupal.doctype.video_interview.video_interview.patch_video_interview_record
@frappe.whitelist()
def patch_video_interview_record():
	doc_list = frappe.get_all("Video Interview", fields=["name"])
	if doc_list:
		for row in doc_list:
			doc = frappe.get_doc("Video Interview", row.name)
			if not doc.record_history:
				doc.append("record_history", {
						"video_interview_id": doc.name,
						"job_applicant_id": doc.job_applicant,
						"status": doc.status,
						"date_created": doc.creation
					})
			else:
				for row_record_history in doc.record_history[:-1]:
					row_record_history.status = "Revised"
				for row_record_history in doc.record_history[-1:]:
					row_record_history.status = doc.status
			doc.flags.ignore_permissions = True
			doc.save()

#erpyoupal.erpyoupal.doctype.video_interview.video_interview.regenerate_video_interview_url
@frappe.whitelist()
def regenerate_video_interview_url():
	video_interview_list = frappe.get_all("Video Interview", fields=['name'])
	if video_interview_list:
		for video_interview in video_interview_list:
			with_changes = 0
			doc = frappe.get_doc("Video Interview", video_interview.name)
			if doc.question_table:
				for row in doc.question_table:
					if row.filename:
						last_date_updated = None
						if row.modified:
							last_date_updated = row.modified
						else:
							last_date_updated = row.creation
						days_diff = (get_datetime(now()) - get_datetime(last_date_updated)).days
						if last_date_updated and flt(days_diff) >= 6:
							regenerate_video_url_result = regenerate_video_url(row.filename)
							if regenerate_video_url_result:
								if "status" in regenerate_video_url_result and regenerate_video_url_result["status"] in ["success"]:
									row.video_url = regenerate_video_url_result["url"]
									with_changes = 1
			if with_changes:
				doc.flags.ignore_permissions = True
				doc.save()

@frappe.whitelist()
def regenerate_video_url(filename):
    result = "No response"
    authentication_token = True
	#get_authentication_token_testgorilla()
    if authentication_token:
        url = "https://api.interview.youpalgroup.com/regenerate-video-link-from-minio"
        headers = {}
        headers["content-type"] = "application/json"
        #headers["Authorization"] = "Token "+authentication_token
        data = '{"fname":"'+str(filename)+'"}'
        request_result = requests.post(url, headers=headers, data=data)
        result = request_result.json()
        request_result.close()
    else:
        result = "Insufficient TestGorilla Settings"

    return result