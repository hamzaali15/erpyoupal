# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import validate_email_address, now, flt
from erpyoupal.erpyoupal.doctype.background_check.idenfy_api import get_idenfy_token_for_verification
from erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview import create_interview_availability

class BackgroundCheck(Document):
	def validate(self):
		self.validate_entry()
		self.get_printview_links()
		clientId = str(self.email).replace(" ", "")
		clientId = clientId.lower()
		if not self.token_generated:
			self.token_generated = get_idenfy_token_for_verification(clientId)
			if self.token_generated and self.email and not self.get("disable_email_sending"):
				self.send_email_to_applicant()
		
		if not self.is_new():
			if str(self.status) in ["Completed"] and str(frappe.db.get_value("Background Check", self.name, 'status')) != "Completed":
				self.do_create_video_interview()
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
	
	def do_create_video_interview(self):
		to_create = 0
		email_id = frappe.db.get_value("Job Applicant", self.job_applicant, "email_id")
		peoples = frappe.get_all("People", filters={"email_address": email_id}, fields=["name", "people_type"])
		if peoples:
			if peoples[0].people_type in ["Consultant", "Business / Consultant"]:
				existing_video_interviews = frappe.get_all("Video Interview", filters={"job_applicant": self.job_applicant}, fields=["name"])
				if existing_video_interviews:
					video_interview_doc = frappe.get_doc("Video Interview", existing_video_interviews[0].name)
					video_interview_doc.flags.ignore_permissions = True
					video_interview_doc.run_method("send_email_to_applicant")
				else:
					to_create = 1
			else:
				to_create = 1
		else:
			to_create = 1
		
		if to_create:
			create_video_interview(job_applicant=self.job_applicant)

	def get_printview_links(self):
		if not self.pdf_link:
			self.pdf_link = f"https://erp.youpal.se/printview?doctype=Background%20Check&name={self.name}&format=Background%20Check%20PDF&no_letterhead=0&letterhead=youpal&settings=%7B%7D&_lang=en"
		if not self.public_printview_link:
			self.public_printview_link = generate_public_printview(background_check=self.name) 

	def save_it_consultant(self):
		#Trigger Save it consultant
		it_consultant = frappe.db.get_value("Job Applicant", self.job_applicant, "it_consultant")
		if it_consultant:
			frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=it_consultant, queue='long', timeout=300, now=False)

	def after_insert(self):
		pass

	def send_email_to_applicant(self):
		frappe.sendmail(recipients=self.email,subject="Idenfy Verification",message= """
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
				<h4>Verify your identity using Idenfy</h4>
				<br>
				<h4>Hey, """+self.applicant_name+"""</h4>
				<p>We are the global network of top developers, design and</p>
				<p>bussiness exprerts. With Youpal Group, you'll build an amazing</p>
				<p>career, wherever you live</p>
				<br>
				<a href='"""+self.token_generated+"""' target="_blank"><button type="button">Continue</button></a>
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

@frappe.whitelist(allow_guest=True)
def create_candidate_interview(job_applicant):
	if frappe.get_all("Job Applicant", filters={'name': job_applicant}):
		new_doc = frappe.new_doc("Candidate Interview")
		new_doc.job_applicant = job_applicant
		new_doc.flags.ignore_permissions = True
		new_doc.insert()

@frappe.whitelist(allow_guest=True)
def create_video_interview(job_applicant=None, disable_email_sending=0, it_consultant=None):
	to_continue = 0
	if job_applicant and frappe.get_all("Job Applicant", filters={'name': job_applicant}) and not frappe.get_all("Video Interview", filters={'email': frappe.get_value('Job Applicant', job_applicant, 'email_id')}):
		to_continue = 1
	if it_consultant and frappe.get_all("IT Consultant", filters={'name': it_consultant}) and not frappe.get_all("Video Interview", filters={'email': frappe.get_value('IT Consultant', it_consultant, 'email_primary')}):
		to_continue = 1
	if to_continue:
		new_doc = frappe.new_doc("Video Interview")
		new_doc.job_applicant = job_applicant
		new_doc.it_consultant = it_consultant
		new_doc.status = "Pending"
		if it_consultant:
			new_doc.applicant_name = frappe.db.get_value("IT Consultant", it_consultant, 'full_name')
			new_doc.email = frappe.db.get_value("IT Consultant", it_consultant, 'email_primary')
		if job_applicant:
			new_doc.applicant_name = frappe.db.get_value("Job Applicant", job_applicant, 'applicant_name')
			new_doc.email = frappe.db.get_value("Job Applicant", job_applicant, 'email_id')
		new_doc.disable_email_sending = disable_email_sending
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.insert()

#erpyoupal.erpyoupal.doctype.background_check.background_check.generate_public_printview
@frappe.whitelist()
def generate_public_printview(background_check):
	from frappe.utils import get_url
	result = None
	if frappe.get_all("Background Check", filters={"name": background_check}, fields=["name"]):
		doc = frappe.get_doc("Background Check", background_check)
		if doc:
			result = f"{get_url()}/background_check/{doc.name}?key={doc.get_signature()}&format=Background%20Check%20PDF&no_letterhead=0"
	return result

#erpyoupal.erpyoupal.doctype.background_check.background_check.complete_all_background_checks
@frappe.whitelist()
def complete_all_background_checks():
	doc_lists = frappe.get_all("Background Check", filters={"status": ["not in", ["Completed"]]}, fields=["name"])
	if doc_lists:
		for doc_ in doc_lists:
			doc = frappe.get_doc("Background Check", doc_.name)
			doc.flags.ignore_permissions = True
			doc.status = "Completed"
			doc.save()