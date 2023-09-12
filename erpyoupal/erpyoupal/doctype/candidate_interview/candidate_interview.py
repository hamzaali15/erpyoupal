9# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _,throw
import datetime

class CandidateInterview(Document):
	def validate(self):
		self.validate_entry()
		self.save_it_consultant()
	
	def validate_entry(self):
		if not self.job_applicant and not self.it_consultant:
			frappe.throw(_("Job Applicant or IT Consultant is required"))
		if self.it_consultant:
			self.email = frappe.db.get_value("IT Consultant", self.it_consultant, "email_primary")
		if self.job_applicant:
			self.email = frappe.db.get_value("Job Applicant", self.job_applicant, "email_id")

	def save_it_consultant(self):
		#Trigger Save it consultant
		it_consultant = self.it_consultant
		if self.job_applicant:
			it_consultant = frappe.db.get_value("Job Applicant", self.job_applicant, "it_consultant")
		if it_consultant:
			frappe.enqueue("erpyoupal.it_service.doctype.it_consultant.it_consultant.trigger_save_it_consultant", it_consultant=it_consultant, queue='long', timeout=300, now=False)

	def send_email(self, from_application_process=None):
		email = None
		applicant_name = None

		if self.it_consultant:
			email = frappe.get_value("IT Consultant",self.it_consultant,"email_primary")
			applicant_name = frappe.get_value("IT Consultant",self.it_consultant,"full_name")

		if self.job_applicant:
			email = frappe.get_value("Job Applicant",self.job_applicant,"email_id")
			applicant_name = frappe.get_value("Job Applicant",self.job_applicant,"applicant_name")

		if email:
			if from_application_process and from_application_process in ['Assessment First']:
				frappe.sendmail(recipients=email,subject="Interview Availability",message= """
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
						<h4>Welcome to the Youpal Group Application Process!</h4>
						<br>
						<h4>Hello, """+applicant_name+"""</h4>
						<p>Congratualtions for passing your test with a good score!</p>
						<p>With regards to your performance, we would like to have an online interview with you at the earliest.</p>
						<p>Before this interview we want you to prepare a case that shows your competence as a digital designer. Please can you prepare a case that verifies understanding of digital product design, digital application design or likewise to present to the interviewer. This can be a previous case from your portfolio or a case that you would create and present to us.</p>
						<p>Please note we are not interested in cases of simple applications (like food or date apps), small websites or landing pages, we need to understand how complex solutions you can work with.</p>
						<br>
						<a href="https://jobs.youpalgroup.com/availability/"""+self.name+"""" target="_blank"><button type="button">Click here to book your available timeslots</button></a>
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
			else:
				frappe.sendmail(recipients=email,subject="Interview Availability",message= """
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
						<h4>Select your Interview Availability</h4>
						<br>
						<h4>Hey, """+applicant_name+"""</h4>
						<p>We are the global network of top developers, design and</p>
						<p>bussiness exprerts. With Youpal Group, you'll build an amazing</p>
						<p>career, wherever you live</p>
						<br>
						<a href="https://jobs.youpalgroup.com/availability/"""+self.name+"""" target="_blank"><button type="button">Continue</button></a>
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

#erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview.create_interview_availability
@frappe.whitelist()
def create_interview_availability(job_applicant=None, from_application_process=None, disable_email_sending=1, it_consultant=None):
	email = None
	applicant_name = None
	if it_consultant:
		email = frappe.get_value("IT Consultant", it_consultant, "email_primary")
		applicant_name = frappe.get_value("IT Consultant", it_consultant, "full_name")
	if job_applicant:
		email = frappe.get_value("Job Applicant", job_applicant, "email_id")
		applicant_name = frappe.get_value("Job Applicant", job_applicant, "applicant_name")
	
	if email and not frappe.get_all("Candidate Interview", filters={'email': email}):
		new_doc = frappe.new_doc("Candidate Interview")
		new_doc.job_applicant = job_applicant
		new_doc.it_consultant = it_consultant
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		new_doc.save()

		if not disable_email_sending:
			if from_application_process and from_application_process in ['Assessment First']:
				frappe.sendmail(recipients=email,subject="Interview Availability",message= """
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
						<h4>Welcome to the Youpal Group Application Process!</h4>
						<br>
						<h4>Hello, """+applicant_name+"""</h4>
						<p>Congratualtions for passing your test with a good score!</p>
						<p>With regards to your performance, we would like to have an online interview with you at the earliest.</p>
						<p>Before this interview we want you to prepare a case that shows your competence as a digital designer. Please can you prepare a case that verifies understanding of digital product design, digital application design or likewise to present to the interviewer. This can be a previous case from your portfolio or a case that you would create and present to us.</p>
						<p>Please note we are not interested in cases of simple applications (like food or date apps), small websites or landing pages, we need to understand how complex solutions you can work with.</p>
						<br>
						<a href="https://jobs.youpalgroup.com/availability/"""+new_doc.name+"""" target="_blank"><button type="button">Click here to book your available timeslots</button></a>
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
			else:
				frappe.sendmail(recipients=email,subject="Interview Availability",message= """
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
						<h4>Select your Interview Availability</h4>
						<br>
						<h4>Hey, """+applicant_name+"""</h4>
						<p>We are the global network of top developers, design and</p>
						<p>bussiness exprerts. With Youpal Group, you'll build an amazing</p>
						<p>career, wherever you live</p>
						<br>
						<a href="https://jobs.youpalgroup.com/availability/"""+new_doc.name+"""" target="_blank"><button type="button">Continue</button></a>
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

#erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview.list_interview_availability
@frappe.whitelist()
def list_interview_availability(job_applicant):
	available_dates = []
	doc = frappe.get_doc("Candidate Interview", job_applicant)
	for d in doc.dates:
		if d.available_from and d.available_to and d.selected == 0:
			available_dates.append(d)

	return available_dates

#erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview.select_interview_availability
@frappe.whitelist()
def select_interview_availability(name, candidate, google_calendar=None):
	doc = frappe.get_doc('Candidate Interview Dates', name)
	doc.selected = 1
	doc.save()

	new_doc = frappe.new_doc('Candidate Interview Dates')
	new_doc.date = doc.date
	new_doc.d_week = doc.d_week
	new_doc.available_from = doc.available_from
	new_doc.available_to = doc.available_to
	new_doc.selected = 1
	new_doc.enabled = 1
	new_doc.parent = candidate
	new_doc.parenttype = "Lead Candidate"
	new_doc.parentfield = "dates"
	if google_calendar:
		new_doc.google_calendar = google_calendar
	new_doc.insert()


	return "Time Slot Selected"

#erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview.get_google_calendars
@frappe.whitelist(allow_guest=False)
def get_google_calendars(filters={}):
	return frappe.get_all("Google Calendar", filters=filters, fields=['*'])

#erpyoupal.erpyoupal.doctype.candidate_interview.candidate_interview.get_candidate_interview_link
@frappe.whitelist()
def get_candidate_interview_link(it_consultant):
	result = "No interview availability found"
	it_consultant_doc = frappe.get_all("IT Consultant", filters={'name': it_consultant}, fields=['name', 'email_primary'])
	if it_consultant_doc:
		candidate_interview = frappe.get_all("Candidate Interview", filters={"email": it_consultant_doc[0].email_primary}, fields=['name'])
		if candidate_interview:
			result =  f"https://jobs.youpalgroup.com/availability/{candidate_interview[0].name}"

	return result