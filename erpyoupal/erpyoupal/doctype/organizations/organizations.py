# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from dataclasses import field
import frappe
from frappe.utils.nestedset import NestedSet
from frappe.utils import flt
from erpyoupal.clockify_project.doctype.clockify_projects.clockify_projects import create_project_from_organization

class Organizations(NestedSet):
	def validate(self):
		self.unsave_candidates()

	def after_insert(self):
		create_project_from_organization(organization=self.name)
		
	def create_it_partner_agency(self):
		if not self.get("created_from_it_partner_agency"):
			if "Partner" in self.organization_type:
				if not frappe.get_all("IT Partner Agency", filters={'organization_name': self.organization_name}):
					new_doc = frappe.new_doc("IT Partner Agency")
					new_doc.created_from_organizations = 1
					new_doc.company_name = self.organization_name
					new_doc.agency_id = self.organization_id
					new_doc.business_id = self.business_id
					new_doc.bank_name = self.bank_name
					new_doc.vat = self.vat
					new_doc.account_number = self.account_number
					new_doc.clearing_number = self.clearing_number
					new_doc.iban_swift = self.iban_swift
					new_doc.organization = self.name
					new_doc.organization_name = self.organization_name
					new_doc.organization_address = self.address
					new_doc.company_size = self.organization_size
					new_doc.location = self.address
					new_doc.flags.ignore_permissions = True
					new_doc.insert()

	def unsave_candidates(self):
		if not self.is_new():
			old_candidates = []
			old_organization = frappe.get_doc("Organizations", self.name)
			if old_organization:
				for old_cand in old_organization.save_candidate:
					old_candidates.append(old_cand.it_consultant)

			new_candidates = []
			if self.save_candidate:
				for new_cand in self.save_candidate:
					new_candidates.append(new_cand.it_consultant)
			
			removed_candidates = list(filter(lambda v: v not in new_candidates, old_candidates))
			if removed_candidates:
				if len(removed_candidates) > 1:
					removed_candidates = str(tuple(removed_candidates))
				else:
					removed_candidates = str(tuple(removed_candidates))[:-2]
					removed_candidates = removed_candidates+")"

				frappe.db.sql(""" UPDATE `tabLead Candidates Table` LCT INNER JOIN `tabLead Candidate` LC ON LCT.`parent`=LC.`name`
					SET LC.`candidate_is_saved`=0
					WHERE LCT.`parenttype`='Lead Candidate' AND LCT.`parentfield`='candidate' 
					AND LC.`candidate_is_saved`=1 AND LCT.`it_consultant` IN """+removed_candidates+""" """)

#erpyoupal.erpyoupal.doctype.organizations.organizations.get_child_organizations
@frappe.whitelist()
def get_child_organizations(parent):
	lft,rgt = frappe.db.get_value("Organizations",parent,['lft', 'rgt'])
	return frappe.db.sql("""SELECT * FROM `tabOrganizations` WHERE lft > %s AND rgt < %s""",(lft,rgt),as_dict=True)

#erpyoupal.erpyoupal.doctype.organizations.organizations.get_related_lead_custom
@frappe.whitelist()
def get_related_lead_custom(organization,request_type=None,due_date=None,location=None,candidate=None):
	final_data = []
	add_filter = " LC.organization = '"+organization+"'"
	if request_type:
		add_filter	+= " AND LC.request_type = '"+request_type+"'"
	if due_date:
		add_filter += " AND LC.talent_request_due_date ='"+due_date+"'"
	if location:
		add_filter += " AND LC.talent_location ='"+location+"'"

	lead_custom = frappe.db.sql("""SELECT LC.*, (SELECT COUNT('name') FROM `tabLead Candidate` WHERE generated_from_lead = LC.`name`) as lead_candidate_count FROM `tabLead Custom` LC WHERE"""+add_filter,as_dict=True)

	if candidate:
		for lead in lead_custom:
			if lead.lead_candidate_count:
				final_data.append(lead)
		return	final_data
	else:
		return lead_custom

#erpyoupal.erpyoupal.doctype.organizations.organizations.transfer_it_partner_agency_data_to_organizations
@frappe.whitelist()
def transfer_it_partner_agency_data_to_organizations():
	doc_lists = frappe.get_all("IT Partner Agency", fields=["name"])
	for doc_row in doc_lists:
		it_partner_agency_doc = frappe.get_doc("IT Partner Agency", doc_row.name)
		if it_partner_agency_doc.organization:
			if frappe.get_all("Organizations", filters={"name":it_partner_agency_doc.organization}, fields=["name"]):
				organizations_doc = frappe.get_doc("Organizations", it_partner_agency_doc.organization)
				organizations_doc.flags.ignore_permissions = True
				organizations_doc.logo = it_partner_agency_doc.company_logo
				#organizations_doc.organization_id = None
				#organizations_doc.organization_name = None
				#organizations_doc.address = None
				#organizations_doc.organization_type = None
				organizations_doc.status = it_partner_agency_doc.status
				organizations_doc.verification = it_partner_agency_doc.verification
				#organizations_doc.lft = None
				#organizations_doc.rgt = None
				#organizations_doc.is_group = None
				#organizations_doc.old_parent = None
				#organizations_doc.parent_organizations = None
				organizations_doc.company_email = it_partner_agency_doc.email_primary
				organizations_doc.company_mobile = it_partner_agency_doc.mobile_primary
				#organizations_doc.company_website = None
				#organizations_doc.linkedin = None
				#organizations_doc.facebook = None
				#organizations_doc.instagram = None
				#organizations_doc.twitter = None
				organizations_doc.founded = it_partner_agency_doc.founded
				organizations_doc.organization_size = it_partner_agency_doc.company_size
				#organizations_doc.hq = None
				#organizations_doc.save_candidate = None
				#organizations_doc.business_id = None
				#organizations_doc.bank_name = None
				#organizations_doc.vat = None
				#organizations_doc.account_number = None
				#organizations_doc.clearing_number = None
				#organizations_doc.iban_swift = None
				#organizations_doc.invoice_contact = None
				#organizations_doc.invoice_name = None
				#organizations_doc.invoice_email = None
				#organizations_doc.invoice_mobile = None
				#organizations_doc.oneflow_contracts = None
				organizations_doc.rate_hourly = it_partner_agency_doc.rate_hourly
				organizations_doc.eu_zone = it_partner_agency_doc.eu_zone
				if it_partner_agency_doc.speciality:
					organizations_doc.speciality = None
					for row in it_partner_agency_doc.speciality:
						organizations_doc.append("speciality", {"speciality": row.speciality})
				organizations_doc.location = it_partner_agency_doc.location
				organizations_doc.data_protection = it_partner_agency_doc.data_protection
				organizations_doc.agreement_link = it_partner_agency_doc.agreement_link
				organizations_doc.lead_first_name = it_partner_agency_doc.lead_first_name
				organizations_doc.email_primary = it_partner_agency_doc.email_primary
				organizations_doc.lead_last_name = it_partner_agency_doc.lead_last_name
				organizations_doc.mobile_primary = it_partner_agency_doc.mobile_primary
				organizations_doc.role_in_company = it_partner_agency_doc.role_in_company
				organizations_doc.currency = it_partner_agency_doc.currency
				organizations_doc.employees = it_partner_agency_doc.employees
				organizations_doc.hourly_rate = it_partner_agency_doc.hourly_rate
				organizations_doc.minimum_project_size = it_partner_agency_doc.minimum_project_size
				organizations_doc.work_type = it_partner_agency_doc.work_type
				organizations_doc.work_destination = it_partner_agency_doc.work_destination
				if it_partner_agency_doc.add_social:
					organizations_doc.add_social = None
					for row in it_partner_agency_doc.add_social:
						organizations_doc.append("add_social", {"social": row.social, "link": row.link})
				organizations_doc.platforms = it_partner_agency_doc.platforms
				if it_partner_agency_doc.platforms:
					organizations_doc.platforms = None
					for row in it_partner_agency_doc.platforms:
						organizations_doc.append("platforms", {"platform": row.platform, "link": row.link})
				organizations_doc.tagline = it_partner_agency_doc.tagline
				organizations_doc.description = it_partner_agency_doc.description
				if it_partner_agency_doc.skill:
					organizations_doc.skill = None
					for row in it_partner_agency_doc.skill:
						organizations_doc.append("skill", {"skill": row.skill})
				if it_partner_agency_doc.add_projects:
					organizations_doc.add_projects = None
					for row in it_partner_agency_doc.add_projects:
						organizations_doc.append("add_projects", {
							"company_name": row.company_name,
							"location": row.location,
							"industry": row.industry,
							"technologies_and_methodologies_used": row.technologies_and_methodologies_used,
							"description": row.description
							})
				if it_partner_agency_doc.add_certifications:
					organizations_doc.add_certifications = None
					for row in it_partner_agency_doc.add_certifications:
						organizations_doc.append("add_certifications", {
							"certification_name": row.certification_name,
							"certification_number": row.certification_number,
							"year_recieved": row.year_recieved,
							"provided_by": row.provided_by,
							"description": row.description
							})
				if it_partner_agency_doc.language_proficiency_level:
					organizations_doc.language_proficiency_level = None
					for row in it_partner_agency_doc.language_proficiency_level:
						organizations_doc.append("language_proficiency_level", {
							"language": row.language,
							"language_level": row.language_level
							})
				organizations_doc.nda_link = it_partner_agency_doc.nda_link
				organizations_doc.nda_expiry_date = it_partner_agency_doc.nda_expiry_date
				if it_partner_agency_doc.contracts:
					organizations_doc.contracts = None
					for row in it_partner_agency_doc.contracts:
						organizations_doc.append("contracts", {
							"contract": row.contract,
							"contract_expiry_date": row.contract_expiry_date
							})
				organizations_doc.id_document_verification = it_partner_agency_doc.id_document_verification
				organizations_doc.visual_verification = it_partner_agency_doc.visual_verification
				organizations_doc.id_dateofverification = it_partner_agency_doc.id_dateofverification
				organizations_doc.visual_dateofverification = it_partner_agency_doc.visual_dateofverification
				organizations_doc.identity_document_type = it_partner_agency_doc.identity_document_type
				organizations_doc.idcard_nationality = it_partner_agency_doc.idcard_nationality
				organizations_doc.idcard_personalidnum = it_partner_agency_doc.idcard_personalidnum
				organizations_doc.id_card_gender = it_partner_agency_doc.id_card_gender
				organizations_doc.idcard_dob = it_partner_agency_doc.idcard_dob
				organizations_doc.idcard_cityofbirth = it_partner_agency_doc.idcard_cityofbirth
				organizations_doc.idcard_countryofbirth = it_partner_agency_doc.idcard_countryofbirth
				organizations_doc.id_card_date_of_issue = it_partner_agency_doc.id_card_date_of_issue
				organizations_doc.id_card_date_of_expiry = it_partner_agency_doc.id_card_date_of_expiry
				organizations_doc.id_card_issued_by = it_partner_agency_doc.id_card_issued_by
				organizations_doc.passport_nationality = it_partner_agency_doc.passport_nationality
				organizations_doc.passport_no = it_partner_agency_doc.passport_no
				organizations_doc.passport_visa_type = it_partner_agency_doc.passport_visa_type
				organizations_doc.passport_date_of_birth = it_partner_agency_doc.passport_date_of_birth
				organizations_doc.passport_city_of_birth = it_partner_agency_doc.passport_city_of_birth
				organizations_doc.passport_country_of_birth = it_partner_agency_doc.passport_country_of_birth
				organizations_doc.passport_date_of_issue = it_partner_agency_doc.passport_date_of_issue
				organizations_doc.passport_date_of_expiry = it_partner_agency_doc.passport_date_of_expiry
				organizations_doc.passport_issued_by = it_partner_agency_doc.passport_issued_by
				organizations_doc.preferred_currency = it_partner_agency_doc.preferred_currency
				organizations_doc.save()

#erpyoupal.erpyoupal.doctype.organizations.organizations.get_organization_data
@frappe.whitelist()
def get_organization_data(organization):
	if frappe.get_all("Organizations", filters={"name": organization}, fields=["name"]):
		result = {}
		organizations_doc = frappe.get_doc("Organizations", organization)
		meta = frappe.get_meta("Organizations")
		for i in meta.get("fields"):
			if organizations_doc.get(i.fieldname):
				result[i.fieldname] = organizations_doc.get(i.fieldname)
			else:
				if i.fieldtype in ['Table', 'Table MultiSelect']:
					result[i.fieldname] = []
				else:
					result[i.fieldname] = ""
		
		organizations_people = []
		peoples_doc = frappe.get_all("People", filters={"organization_name": organizations_doc.name, "people_type": ["in", ["Business", "Business / Consultant"]]}, fields=["name"])
		if peoples_doc:
			for people_doc in peoples_doc:
				people = frappe.get_doc("People", people_doc.name)
				people_data = {
					"first_name": people.first_name,
					"last_name": people.last_name,
					"person_name": people.person_name,
					"designation": people.designation,
					"email": people.email_address,
					"mobile": None
				}
				if people.mobile:
					people_data["mobile"] = people.mobile[0].mobile
				organizations_people.append(people_data)

		result["peoples"] = organizations_people

		return result
	else:
		frappe.throw(_("Organization not found"))


#erpyoupal.erpyoupal.doctype.organizations.organizations.remove_test_organizations
@frappe.whitelist()
def remove_test_organizations():
	data = frappe.db.sql("""
		SELECT
			`name`
		FROM `tabOrganizations`
		WHERE 
			`name` LIKE '%test%'
	""", as_dict=1)
	if data:
		for row in data:
			peoples = frappe.get_all("People", filters={"organization_name": row.name}, fields=["name"])
			if peoples:
				for pep in peoples:
					frappe.db.set_value('People', pep.name, 'organization_name', None, update_modified=False)
				#frappe.db.commit()
			users = frappe.get_all("User", filters={"organization": row.name}, fields=["name"])
			if users:
				for usr in users:
					frappe.db.set_value('User', usr.name, 'organization', None, update_modified=False)
			
			leads = frappe.get_all("Lead Candidate", filters={"generated_by": row.name}, fields=["name"])
			if leads:
				for lead in leads:
					frappe.db.set_value('Lead Candidate', lead.name, 'generated_by', None, update_modified=False)

			cleads = frappe.get_all("Lead Custom", filters={"organization": row.name}, fields=["name"])
			if cleads:
				for clead in cleads:
					frappe.db.set_value('Lead Custom', clead.name, 'organization', None, update_modified=False)

			doc = frappe.get_doc("Organizations", row.name)
			if not doc.parent_organizations:
				frappe.db.set_value('Organizations', doc.name, 'parent_organizations', 'ADDWEB SOLUTION-01450', update_modified=False)

			doc.flags.ignore_permissions = True
			doc.delete()

#erpyoupal.erpyoupal.doctype.organizations.organizations.transfer_it_partner_agency_data_to_non_existing_organizations
@frappe.whitelist()
def transfer_it_partner_agency_data_to_non_existing_organizations():
	doc_lists = frappe.get_all("IT Partner Agency", fields=["name"])
	for doc_row in doc_lists:
		it_partner_agency_doc = frappe.get_doc("IT Partner Agency", doc_row.name)
		if not it_partner_agency_doc.organization:
			organizations_doc = frappe.new_doc("Organizations")
			organizations_doc.flags.ignore_permissions = True
			organizations_doc.flags.ignore_links = True
			organizations_doc.logo = it_partner_agency_doc.company_logo
			#organizations_doc.organization_id = None
			organizations_doc.organization_name = it_partner_agency_doc.company_name
			#organizations_doc.address = None
			organizations_doc.organization_type = 'Partner'
			organizations_doc.status = it_partner_agency_doc.status
			organizations_doc.verification = it_partner_agency_doc.verification
			#organizations_doc.lft = None
			#organizations_doc.rgt = None
			#organizations_doc.is_group = None
			#organizations_doc.old_parent = None
			#organizations_doc.parent_organizations = None
			organizations_doc.company_email = it_partner_agency_doc.email_primary
			organizations_doc.company_mobile = it_partner_agency_doc.mobile_primary
			#organizations_doc.company_website = None
			#organizations_doc.linkedin = None
			#organizations_doc.facebook = None
			#organizations_doc.instagram = None
			#organizations_doc.twitter = None
			organizations_doc.founded = it_partner_agency_doc.founded
			organizations_doc.organization_size = it_partner_agency_doc.company_size
			#organizations_doc.hq = None
			#organizations_doc.save_candidate = None
			#organizations_doc.business_id = None
			#organizations_doc.bank_name = None
			#organizations_doc.vat = None
			#organizations_doc.account_number = None
			#organizations_doc.clearing_number = None
			#organizations_doc.iban_swift = None
			#organizations_doc.invoice_contact = None
			#organizations_doc.invoice_name = None
			#organizations_doc.invoice_email = None
			#organizations_doc.invoice_mobile = None
			#organizations_doc.oneflow_contracts = None
			organizations_doc.rate_hourly = it_partner_agency_doc.rate_hourly
			organizations_doc.eu_zone = it_partner_agency_doc.eu_zone
			if it_partner_agency_doc.speciality:
				organizations_doc.speciality = None
				for row in it_partner_agency_doc.speciality:
					organizations_doc.append("speciality", {"speciality": row.speciality})
			organizations_doc.location = it_partner_agency_doc.location
			organizations_doc.data_protection = it_partner_agency_doc.data_protection
			organizations_doc.agreement_link = it_partner_agency_doc.agreement_link
			organizations_doc.lead_first_name = it_partner_agency_doc.lead_first_name
			organizations_doc.email_primary = it_partner_agency_doc.email_primary
			organizations_doc.lead_last_name = it_partner_agency_doc.lead_last_name
			organizations_doc.mobile_primary = it_partner_agency_doc.mobile_primary
			organizations_doc.role_in_company = it_partner_agency_doc.role_in_company
			organizations_doc.currency = it_partner_agency_doc.currency
			organizations_doc.employees = it_partner_agency_doc.employees
			organizations_doc.hourly_rate = it_partner_agency_doc.hourly_rate
			organizations_doc.minimum_project_size = it_partner_agency_doc.minimum_project_size
			organizations_doc.work_type = it_partner_agency_doc.work_type
			organizations_doc.work_destination = it_partner_agency_doc.work_destination
			if it_partner_agency_doc.add_social:
				organizations_doc.add_social = None
				for row in it_partner_agency_doc.add_social:
					organizations_doc.append("add_social", {"social": row.social, "link": row.link})
			organizations_doc.platforms = it_partner_agency_doc.platforms
			if it_partner_agency_doc.platforms:
				organizations_doc.platforms = None
				for row in it_partner_agency_doc.platforms:
					organizations_doc.append("platforms", {"platform": row.platform, "link": row.link})
			organizations_doc.tagline = it_partner_agency_doc.tagline
			organizations_doc.description = it_partner_agency_doc.description
			if it_partner_agency_doc.skill:
				organizations_doc.skill = None
				for row in it_partner_agency_doc.skill:
					organizations_doc.append("skill", {"skill": row.skill})
			if it_partner_agency_doc.add_projects:
				organizations_doc.add_projects = None
				for row in it_partner_agency_doc.add_projects:
					organizations_doc.append("add_projects", {
						"company_name": row.company_name,
						"location": row.location,
						"industry": row.industry,
						"technologies_and_methodologies_used": row.technologies_and_methodologies_used,
						"description": row.description
						})
			if it_partner_agency_doc.add_certifications:
				organizations_doc.add_certifications = None
				for row in it_partner_agency_doc.add_certifications:
					organizations_doc.append("add_certifications", {
						"certification_name": row.certification_name,
						"certification_number": row.certification_number,
						"year_recieved": row.year_recieved,
						"provided_by": row.provided_by,
						"description": row.description
						})
			if it_partner_agency_doc.language_proficiency_level:
				organizations_doc.language_proficiency_level = None
				for row in it_partner_agency_doc.language_proficiency_level:
					organizations_doc.append("language_proficiency_level", {
						"language": row.language,
						"language_level": row.language_level
						})
			organizations_doc.nda_link = it_partner_agency_doc.nda_link
			organizations_doc.nda_expiry_date = it_partner_agency_doc.nda_expiry_date
			if it_partner_agency_doc.contracts:
				organizations_doc.contracts = None
				for row in it_partner_agency_doc.contracts:
					organizations_doc.append("contracts", {
						"contract": row.contract,
						"contract_expiry_date": row.contract_expiry_date
						})
			organizations_doc.id_document_verification = it_partner_agency_doc.id_document_verification
			organizations_doc.visual_verification = it_partner_agency_doc.visual_verification
			organizations_doc.id_dateofverification = it_partner_agency_doc.id_dateofverification
			organizations_doc.visual_dateofverification = it_partner_agency_doc.visual_dateofverification
			organizations_doc.identity_document_type = it_partner_agency_doc.identity_document_type
			organizations_doc.idcard_nationality = it_partner_agency_doc.idcard_nationality
			organizations_doc.idcard_personalidnum = it_partner_agency_doc.idcard_personalidnum
			organizations_doc.id_card_gender = it_partner_agency_doc.id_card_gender
			organizations_doc.idcard_dob = it_partner_agency_doc.idcard_dob
			organizations_doc.idcard_cityofbirth = it_partner_agency_doc.idcard_cityofbirth
			organizations_doc.idcard_countryofbirth = it_partner_agency_doc.idcard_countryofbirth
			organizations_doc.id_card_date_of_issue = it_partner_agency_doc.id_card_date_of_issue
			organizations_doc.id_card_date_of_expiry = it_partner_agency_doc.id_card_date_of_expiry
			organizations_doc.id_card_issued_by = it_partner_agency_doc.id_card_issued_by
			organizations_doc.passport_nationality = it_partner_agency_doc.passport_nationality
			organizations_doc.passport_no = it_partner_agency_doc.passport_no
			organizations_doc.passport_visa_type = it_partner_agency_doc.passport_visa_type
			organizations_doc.passport_date_of_birth = it_partner_agency_doc.passport_date_of_birth
			organizations_doc.passport_city_of_birth = it_partner_agency_doc.passport_city_of_birth
			organizations_doc.passport_country_of_birth = it_partner_agency_doc.passport_country_of_birth
			organizations_doc.passport_date_of_issue = it_partner_agency_doc.passport_date_of_issue
			organizations_doc.passport_date_of_expiry = it_partner_agency_doc.passport_date_of_expiry
			organizations_doc.passport_issued_by = it_partner_agency_doc.passport_issued_by
			organizations_doc.preferred_currency = it_partner_agency_doc.preferred_currency
			try:
				organizations_doc.insert()
			except:
				pass

#erpyoupal.erpyoupal.doctype.organizations.organizations.patch_check_it_partner_agency_not_in_organizations
@frappe.whitelist()
def patch_check_it_partner_agency_not_in_organizations():
	non_existing = []
	partners = frappe.get_all('IT Partner Agency', fields=['*'])
	if partners:
		for row_partners in partners:
			if not frappe.get_all("Organizations", filters={"organization_name": row_partners.company_name}, fields=['name']):
				non_existing.append(row_partners.name)
	raise Exception(non_existing)


#erpyoupal.erpyoupal.doctype.organizations.organizations.create_partner_organization
@frappe.whitelist(allow_guest=True)
def create_partner_organization(data):
	result = None
	update_user_organization = 0
	generated_oragnization_name = None

	if frappe.get_all("Organizations", filters={"organization_name": data.get('organization_name')}, fields=['name']):
		if data.get("user_email"):
			update_user_organization = 1
	else:
		new_doc = frappe.new_doc("Organizations")
		new_doc.organization_type = "Partner"
		new_doc.organization_name = data.get("organization_name")
		new_doc.address = data.get("address")
		new_doc.founded = data.get("founded")
		new_doc.organization_size = data.get("organization_size")
		new_doc.tagline = data.get("tagline")
		new_doc.about = data.get("about")
		if data.get("skill"):
			for s_row in data.get("skill"):
				new_doc.append("skill", {"skill": s_row.get("skill")})
		if data.get("language_proficiency_level"):
			for lpl_row in data.get("language_proficiency_level"):
				new_doc.append("language_proficiency_level", {"language": lpl_row.get("language"), "language_level": lpl_row.get("language_level")})
		new_doc.flags.ignore_permissions = True
		new_doc.flags.ignore_links = True
		result = new_doc.insert()
		generated_oragnization_name = new_doc.name
		frappe.db.commit()
		if data.get("user_email"):
			update_user_organization = 1
	
	if update_user_organization and generated_oragnization_name:
		user_doc = frappe.get_doc("User", data.get("user_email"))
		user_doc.flags.ignore_permissions = True
		user_doc.flags.ignore_links = True
		user_doc.organization = generated_oragnization_name
		user_doc.save()

	return result


#erpyoupal.erpyoupal.doctype.organizations.organizations.get_organization_contracts
@frappe.whitelist(allow_guest=False)
def get_organization_contracts(organization, oneflow_legal=None):
	result = []
	if frappe.get_all("Organizations", filters={"name": organization}, fields=["name"]):
		doc = frappe.get_doc("Organizations", organization)
		for row in doc.oneflow_contracts:
			is_included = 0
			if oneflow_legal:
				if row.oneflow_legal == oneflow_legal:
					is_included = 1
			else:
				is_included = 1

			if is_included:
				result.append({
					"oneflow_legal": row.oneflow_legal,
					"title": frappe.db.get_value("OneFlow Legal", row.oneflow_legal, "title"),
					"state": frappe.db.get_value("OneFlow Legal", row.oneflow_legal, "contract_state"),
					"contract_pdf": frappe.db.get_value("OneFlow Legal", row.oneflow_legal, "contract_pdf"),
					"creation": frappe.db.get_value("OneFlow Legal", row.oneflow_legal, "creation")
					})
	else:
		frappe.throw("Organization not found")

	return result
