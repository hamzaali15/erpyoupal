# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe import _,msgprint
from frappe.model.document import Document

class ManualJobFetching(Document):
	def validate(self):
		pass
@frappe.whitelist()
def fetch_assignments_now():
	settings = frappe.get_doc('Manual Job Fetching')
	sources = ""
	for r in settings.sources:
		sources += r.source + ","
	sources = sources[:-1]
	ploads = {}
	if settings.company_name:
		ploads.update({'company_name':settings.company_name})
	if settings.country:
		ploads.update({'country':settings.country})
	if settings.posted_date_from:
		ploads.update({'posted_date_from':settings.posted_date_from})
	if settings.keywords:
		ploads.update({'keywords':settings.keywords})
	if settings.project_id:
		ploads.update({'project_id':settings.project_id})
	if settings.sources:
		ploads.update({'sources':sources})
	if settings.offset:
		ploads.update({'offset':settings.offset})
	if settings.limit:
		ploads.update({'limit':settings.limit})
	
	r = requests.get('https://api.youdata.se/assignments',params=ploads,headers={'X-Api-Key': 'd4d684f98c2390fa5a21f39abec94b6ba23d92f4fed5fb334310a3f8f2ee81b5'})
	result = r.json()
	result = result["result"]
	
	fetch_jobs = []
	duplicate = 0
	if settings.with_description_only:
		for res in result:
			if res["description"]:
				title = frappe.scrub(res["title"]).replace('_', '-').replace(',', '').replace('---', '-').replace('--', '-').replace('(', '').replace(')', '').replace('.', '')
				if not frappe.db.exists("Job Opening", {"youdata_id": res["id"]}) and title not in fetch_jobs and not frappe.db.exists('Job Opening',title):
					fetch_jobs.append(title)
					new_doc = frappe.new_doc("Job Opening")
					new_doc.youdata_id = res["title"]
					new_doc.job_title = res["title"]
					new_doc.company = "Youpal Group"
					# new_doc.company = res["company_name"]
					# new_doc.status = res["status"]
					new_doc.status = "Open"
					new_doc.designation = "Scraped Job"
					new_doc.description = res["description"]
					new_doc.work_format = res["work_format"].capitalize()
					new_doc.location = res["country"]
					new_doc.deadline = res["due_date"]
					new_doc.regions = res["regions"]
					new_doc.flags.ignore_permissions = True
					try:
						new_doc.insert()
					except Exception as e:
						msgprint(fetch_jobs)
				else:
					duplicate += 1

					
	else:
		for res in result:
			title = frappe.scrub(res["title"]).replace('_', '-').replace(',', '').replace('---', '-').replace('--', '-').replace('(', '').replace(')', '').replace('.', '')
			if not frappe.db.exists("Job Opening", {"youdata_id": res["id"]}) and title not in fetch_jobs and not frappe.db.exists('Job Opening',title):
				fetch_jobs.append(title)
				new_doc = frappe.new_doc("Job Opening")
				new_doc.youdata_id = res["title"]
				new_doc.job_title = res["title"]
				new_doc.company = "Youpal Group"
				# new_doc.company = res["company_name"]
				# new_doc.status = res["status"]
				new_doc.status = "Open"
				new_doc.designation = "Scraped Job"
				new_doc.description = res["description"]
				new_doc.work_format = res["work_format"].capitalize()
				new_doc.location = res["country"]
				new_doc.deadline = res["due_date"]
				new_doc.regions = res["regions"]
				new_doc.flags.ignore_permissions = True
				try:
					new_doc.insert()
				except Exception as e:
					msgprint(fetch_jobs)
			else:
				duplicate += 1

	msgprint(str(len(fetch_jobs)) + " Fetch Jobs, "+str(duplicate)+" Duplicates")
	