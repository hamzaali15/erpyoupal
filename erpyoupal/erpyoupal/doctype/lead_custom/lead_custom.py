# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from re import M
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate, now_datetime, cstr
from frappe.model.naming import getseries, make_autoname


class LeadCustom(Document):
	def autoname(self):
		#{company_name}-{talent_title}/{project_title}-{#####}
		naming_format = "company-type-.#####"
		if self.organization:
			naming_format = self.organization+"-.#####"
			if self.request_type:
				if self.request_type in ["Talent"]:
					if self.talent_title:
						naming_format = self.organization+"-"+self.talent_title+"-.#####"
				if self.request_type in ["Project"]:
					if self.project_title:
						naming_format = self.organization+"-"+self.project_title+"-.#####"
		self.name = make_autoname(cstr(naming_format))

	def validate(self):
		self.get_lead_candidates_count()
		self.get_expires_in()
		self.get_organization_data()
		self.get_lead_candidates_job_openings()
		#self.validate_candidates()
	
	def after_insert(self):
		pass
	
	def validate_candidates(self):
		if self.lead_candidates:
			new_lead_candidates = []
			with_changes = 0
			for row in self.lead_candidates:
				if not frappe.get_all("IT Consultant", filter={"name": row.it_consultant}, fields=["name"]):
					with_changes = 1
				else:
					new_lead_candidates.append(row)
			if with_changes:
				self.lead_candidates = new_lead_candidates

	def get_lead_candidates_count(self):
		self.lead_candidates_count = len(frappe.get_all("Lead Candidate", filters={"generated_from_lead": self.name}, fields=["name"]))

	def get_lead_candidates_job_openings(self):
		candidates = frappe.get_all("Lead Candidate", filters={"generated_from_lead": self.name}, fields=["name", "generated_from_job_opening"])
		if candidates:
			for can in candidates:
				if can.generated_from_job_opening:
					existing_row = list(filter(lambda d: d.get('job_opening') in [can.generated_from_job_opening], self.job_openings))
					if not existing_row:
						self.append("job_openings", {
							"job_opening": can.generated_from_job_opening
							})

	@frappe.whitelist()
	def get_organization_data(self):
		client_first_name = None
		client_role = None
		client_last_name = None
		client_mobile = None
		client_company_name = None
		client_email = None

		filtered_people = frappe.get_all("People", filters={"organization_name": self.organization, "is_primary_contact_person": 1}, fields=['name'])
		if filtered_people:
			people_doc = frappe.get_doc("People", filtered_people[0].name)
			client_first_name = people_doc.first_name
			if people_doc.email:
				client_email = people_doc.email[0].email
			client_role = people_doc.designation
			client_last_name = people_doc.last_name
			if people_doc.mobile:
				client_mobile = people_doc.mobile[0].mobile
			client_company_name = frappe.db.get_value('Organizations', self.organization, 'organization_name')

		self.client_first_name = client_first_name
		self.client_role = client_role
		self.client_last_name = client_last_name
		self.client_mobile = client_mobile
		self.client_company_name = client_company_name
		self.client_email = client_email

	@frappe.whitelist()
	def get_expires_in(self):
		deadline = None
		if self.request_type == "Talent":
			if self.talent_request_due_date:
				deadline = getdate(self.talent_request_due_date)

		if self.request_type == "Project":
			if self.project_request_due_date:
				deadline = getdate(self.project_request_due_date)

		if deadline:
			currentTime = getdate(nowdate())
			days_diff = (deadline - currentTime).days
			expires_in = str(days_diff)+" days"
			if days_diff <= 0:
				expires_in = "Expired"
			self.expires_in = expires_in

	@frappe.whitelist()
	def load_lead_candidates(self):
		self.get_lead_candidates_count()
		self.lead_candidates = None
		candidates = frappe.get_all("Lead Candidate", filters={'generated_from_lead':self.name}, fields=['name'])
		if candidates:
			for candidate in candidates:
				doc = frappe.get_doc("Lead Candidate", candidate.name)
				if frappe.get_all("IT Consultant", filters={"name": doc.it_consultant}, fields=["name"]):
					self.append('lead_candidates', {
						"it_consultant": doc.it_consultant,
						"stages": doc.stages,
						"candidate_source": doc.candidate_source
					})

	@frappe.whitelist()
	def add_lead_candidates(self, lead_entries):
		entries_created = 0
		for entry in lead_entries:
			if entry.get('it_consultant'):
				existing_doc = frappe.db.sql("""SELECT LCR.`name`, LC.`generated_from_lead` FROM `tabLead Candidates Table` LCR INNER JOIN `tabLead Candidate` LC ON LCR.`parent`=LC.`name`
					WHERE LCR.`parenttype`='Lead Candidate' AND LC.`generated_from_lead`=%s AND LCR.`it_consultant`=%s """,(self.name, entry.get('it_consultant')))
				if not existing_doc:
					new_doc = frappe.new_doc("Lead Candidate")
					new_doc.generated_from_lead = self.name
					new_doc.stages = "Applied"
					new_doc.append('candidate', {
						"it_consultant": entry.get('it_consultant'),
						"rate": entry.get('rate'),
						"hours": entry.get('hours'),
						"consultant_sub_total": entry.get('consultant_sub_total'),
						"client_rate": entry.get('client_rate'),
						"client_sub_total": entry.get('client_sub_total'),
						"gross_margin": entry.get('gross_margin'),
						"check_dailyrate": entry.get('check_dailyrate'),
						"define_day": entry.get('define_day'),
						"daily_rate": entry.get('daily_rate'),
						"check_monthlyrate": entry.get('check_monthlyrate'),
						"define_month": entry.get('define_month'),
						"monthly_rate": entry.get('monthly_rate'),
						"set_utilization": entry.get('set_utilization')
					})
					new_doc.flags.ignore_permissions = True
					if new_doc.insert():
						entries_created = 1
		
		if entries_created:
			frappe.msgprint(_("Lead Candidate(s) created"))

	@frappe.whitelist()
	def load_candidate_stages(self):
		self.load_lead_candidates()
		return get_candidate_stages_status(self.name)
	
	@frappe.whitelist()
	def set_kanban_filter(self):
		new_filter_value = '[["Lead Candidate","generated_from_lead","=","'+self.name+'",false]]'
		frappe.db.set_value('Kanban Board', 'Lead Candidate', 'filters', new_filter_value, update_modified=False)

@frappe.whitelist()
def get_candidate_stages_status(lead_custom, deduct_stages=None):
	stages_data = {
		"Applied": 0,
		"Matched": 0,
		"Presented": 0,
		"Vetting": 0,
		"Negotiation": 0,
		"Accepted": 0,
		"Deal": 0,
		"Rejected": 0
	}
	candidates_list = frappe.get_all("Lead Candidate", filters={'generated_from_lead': lead_custom}, fields=['name', 'stages'])
	for candidate in candidates_list:
		if str(candidate.stages) in stages_data:
			stages_data[candidate.stages] += 1

	if deduct_stages:
		for dstage in deduct_stages:
			if dstage in stages_data:
				stages_data[dstage] -= int(deduct_stages[dstage])

	stages_string_data = (
		str(stages_data["Applied"])+"|"+
		str(stages_data["Matched"])+"|"+
		str(stages_data["Presented"])+"|"+
		str(stages_data["Vetting"])+"|"+
		str(stages_data["Negotiation"])+"|"+
		str(stages_data["Accepted"])+"|"+
		str(stages_data["Deal"])+"|"+
		str(stages_data["Rejected"])
		)

	return stages_string_data

@frappe.whitelist()
def save_candidate_stages_status(lead_custom, is_db_update=0, deduct_stages=None):
	status = get_candidate_stages_status(lead_custom, deduct_stages=deduct_stages)
	if is_db_update:
		frappe.db.set_value("Lead Custom", lead_custom, "candidate_stages", status)
	else:
		return status

@frappe.whitelist()
def update_expires_in():
	lead_customs = frappe.get_all("Lead Custom", fields=['name', 'talent_request_due_date', 'request_type', 'project_request_due_date'])
	for lead in lead_customs:
		deadline = None
		if lead.request_type == "Talent":
			if lead.talent_request_due_date:
				deadline = getdate(lead.talent_request_due_date)

		if lead.request_type == "Project":
			if lead.project_request_due_date:
				deadline = getdate(lead.project_request_due_date)

		if deadline:
			currentTime = getdate(nowdate())
			days_diff = (deadline - currentTime).days
			expires_in = str(days_diff)+" days"
			if days_diff <= 0:
				expires_in = "Expired"
			frappe.db.set_value("Lead Custom", lead.name, "expires_in", expires_in)


#erpyoupal.erpyoupal.doctype.lead_custom.lead_custom.get_candidate_stages_list
@frappe.whitelist(allow_guest=True)
def get_candidate_stages_list():
	result = []
	meta = frappe.get_meta('Lead Candidate')
	if meta and meta.has_field('stages'):
		result = meta.get_field("stages").options
		if result:
			result = result.split('\n')

	return result


#erpyoupal.erpyoupal.doctype.lead_custom.lead_custom.patchfix_empty_lead_candidate
@frappe.whitelist()
def patchfix_empty_lead_candidate():
	#clear lead candidates without it consultant
	lead_customs = frappe.get_all("Lead Custom", fields=["name"])
	if lead_customs:
		for row_lead_customs in lead_customs:
			new_lead_candidates = []
			has_empty_it_consultant = 0
			doc = frappe.get_doc("Lead Custom", row_lead_customs.name)
			if doc.lead_candidates:
				for row_table in doc.lead_candidates:
					if row_table.it_consultant:
						existing_it_consultant = frappe.get_all("IT Consultant", filters={"name": row_table.it_consultant}, fields=["name"])
						if len(existing_it_consultant):
							new_lead_candidates.append(row_table)
						else:
							has_empty_it_consultant = 1
					else:
						has_empty_it_consultant = 1
			if has_empty_it_consultant:
				doc.lead_candidates = new_lead_candidates
				doc.flags.ignore_permissions = True
				doc.flags.update_modified = False
				doc.save()
	
	#delete lead candidate with empty it consultant
	lead_candidates = frappe.get_all("Lead Candidate", fields=["name"])
	if lead_candidates:
		for row_lead_candidates in lead_candidates:
			doc_lead_candidate = frappe.get_doc("Lead Candidate", row_lead_candidates.name)
			has_empty_it_consultant = 0
			it_consultant_populated = 0
			if not doc_lead_candidate.it_consultant:
				if not doc_lead_candidate.candidate:
					has_empty_it_consultant = 1
				else:
					for dlcc in doc_lead_candidate.candidate:
						if not dlcc.it_consultant:
							has_empty_it_consultant = 1
						else:
							doc_lead_candidate.it_consultant = dlcc.it_consultant
							it_consultant_populated = 1
			if it_consultant_populated or has_empty_it_consultant:
				doc_lead_candidate.flags.ignore_permissions = True
				doc_lead_candidate.flags.update_modified = False
				if it_consultant_populated:
					doc_lead_candidate.save()
				if has_empty_it_consultant:
					doc_lead_candidate.delete()

#erpyoupal.erpyoupal.doctype.lead_custom.lead_custom.resave_lead_customs
@frappe.whitelist()
def resave_lead_customs():
	lead_customs = frappe.get_all("Lead Custom", fields=["name"])
	for lc in lead_customs:
		doc = frappe.get_doc("Lead Custom", lc.name)
		doc.flags.ignore_permissions = True
		try:
			doc.save()
		except:
			pass

#erpyoupal.erpyoupal.doctype.lead_custom.lead_custom.save_candidates_count
@frappe.whitelist()
def save_candidates_count():
	lead_customs = frappe.get_all("Lead Custom", fields=["name"])
	for lc in lead_customs:
		doc = frappe.get_doc("Lead Custom", lc.name)
		lead_candidates_count = len(frappe.get_all("Lead Candidate", filters={"generated_from_lead": doc.name}, fields=["name"]))
		frappe.db.set_value('Lead Custom', doc.name, 'lead_candidates_count', lead_candidates_count, update_modified=False)
		frappe.db.commit()