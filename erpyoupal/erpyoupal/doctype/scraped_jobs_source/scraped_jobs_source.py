# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests
from frappe.model.document import Document

class ScrapedJobsSource(Document):
	pass

@frappe.whitelist()
def update_sources():
	r = requests.get('https://api.youdata.se/assignments/sources',params={},headers={'X-Api-Key': '2c104c46a14f1281a3a8eb925d8e3baef3af6a4ffa077f55656b461b1d4e716b'})
	result = r.json()
	frappe.db.sql("""DELETE FROM `tabScraped Jobs Source`""")
	for r in result:
		source = r['collection']
		if not frappe.db.exists("Scraped Jobs Source", source):
			new = frappe.new_doc("Scraped Jobs Source")
			new.source_name = source
			new.flags.ignore_permissions = True
			new.parent = "Manual Job Fetching"
			new.parenttype = "sources"
			new.insert()
