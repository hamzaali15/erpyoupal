# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe import _,msgprint
from frappe.model.document import Document
from datetime import datetime

class JobFetchingSetup(Document):
	pass

@frappe.whitelist()
def fetch_assignments_now():
	settings = frappe.get_doc('Job Fetching Setup')
	if not settings.disable_job_fetching:
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

		r = requests.get('https://api.youdata.se/assignments',params=ploads,headers={'X-Api-Key': '2c104c46a14f1281a3a8eb925d8e3baef3af6a4ffa077f55656b461b1d4e716b'})
		result = r.json()
		result = result["result"]
		fetch_jobs = []
		duplicate = 0
		duplicate_jobs = []

		for res in result:
			if not frappe.db.exists("Job Opening", {"youdata_id": res["id"]}) and res["id"] not in fetch_jobs:
				try:
					publish_to_job_board = 1
					if not res["title"] or res["title"] == "":
						publish_to_job_board = 0
					frappe.db.sql("""INSERT INTO `tabJob Opening` (`name`,youdata_id,job_title,description,creation,modified,company,status,source,designation,workmode,work_load,job_applicants_count,work_format,location,deadline,regions,url,publish_to_job_board,source_company,source_city,source_country) VALUES 
					(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
					(res["id"],res["id"],res["title"],res["description"],res["posted_date"],datetime.now(),"Youpal Group","Open","Scraped Job","General",res["workmode"],res["workload"],res["applications_count"],res["work_format"].capitalize(),str(res["city"]) + str(res["country_code"]),res["due_date"],res["regions"],res["source"]["url"],publish_to_job_board,res["company_name"],res["city"],res["country"]),as_dict=True)
					fetch_jobs.append(res["id"])
					# new_doc = frappe.new_doc("Job Opening")
					# new_doc.route = res["id"]
					# new_doc.name = res["id"]
					# new_doc.youdata_id = res["id"]
					# new_doc.job_title = res["title"]
					# new_doc.description = res["description"]
					# new_doc.creation = res["posted_date"]
					# new_doc.company = "Youpal Group"
					# # new_doc.company = res["company_name"]
					# new_doc.status = "Open"
					# new_doc.source = "Scraped Job"
					# new_doc.designation = "Scraped Job"
					# new_doc.workmode = res["workmode"]
					# new_doc.workload = res["workload"]
					# new_doc.job_applicants_count = res["applications_count"]
					# new_doc.work_format = res["work_format"].capitalize()
					# new_doc.location = res["country"]
					# new_doc.deadline = res["due_date"]
					# new_doc.regions = res["regions"]
				except Exception as e:
					msgprint(str(e))
			else:
				duplicate += 1
				duplicate_jobs.append(res["id"])
				
		log = str(len(fetch_jobs)) + " Fetch Jobs, "+str(duplicate)+" Duplicates\nFertch Jobs:\n"
		for job in fetch_jobs:
			log += str(job)+"\n"
		log += "Duplicate Jobs:\n"
		for job in duplicate_jobs:
			log += str(job)+"\n"
		new_doc = frappe.new_doc('Job Fetching Logs')
		new_doc.log = log
		new_doc.insert()
		msgprint(str(len(fetch_jobs)) + " Fetch Jobs, "+str(duplicate)+" Duplicates")
	else:
		frappe.throw(_("Job Fetching Disabled"))