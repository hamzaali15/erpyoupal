# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now, get_datetime, flt
from erpyoupal.erpyoupal.doctype.oneflow_legal.oneflow_api import create_contrect_from_teplate, delete_contract, create_contract_party, publish_contract, create_contract_access_link, download_contract_file

class OneFlowLegal(Document):
	def validate(self):
		if self.is_new() and not self.oneflow_contract_id:
			contract_result = create_contrect_from_teplate(
				document_title=self.title, 
				workspace_id=self.oneflow_workspace_id, 
				template_id=frappe.db.get_value("OneFlow Template", self.oneflow_template_id, "template_id"), 
				user_email=self.user_email
				)
			if contract_result:
				if contract_result.get("id"):
					self.oneflow_contract_id = contract_result.get("id")
					self.contract_state = contract_result.get("state")
					included_participants = []
					if contract_result.get("parties"):
						for party in contract_result['parties']:
							if party.get('participants'):
								for participant in party['participants']:
									row = {
										"participant_id": participant.get("id"),
										"participant_name": participant.get("name"),
										"participant_email": participant.get("email"),
										"sign_method": participant.get("sign_method"),
										"sign_state": participant.get("sign_state"),
										"party_id": party.get('id'),
										"party_name": party.get('name')
										}
									if row not in included_participants:
										included_participants.append(row)

							if party.get('participant'):
								participant = party['participant']
								row = {
									"participant_id": participant.get("id"),
									"participant_name": participant.get("name"),
									"participant_email": participant.get("email"),
									"sign_method": participant.get("sign_method"),
									"sign_state": participant.get("sign_state"),
									"party_id": party.get('id'),
									"party_name": party.get('name')
									}
								if row not in included_participants:
									included_participants.append(row)

					if included_participants:
						self.participants = None
						for new_row in included_participants:
							self.append("participants", new_row)

		self.generate_contract_links()
		self.download_contract_pdf_file()

	def download_contract_pdf_file(self):
		if not self.contract_pdf:
			try:
				contract_file = download_contract_file(contract_id=self.oneflow_contract_id, document_name=self.name)
				if "/files/" in str(contract_file):
					self.contract_pdf = contract_file
			except Exception as e:
				pass

	@frappe.whitelist()
	def generate_contract_links(self):
		result = "No new contract links generated"
		if self.participants:
			for new_row in self.participants:
				to_generate = 0
				if not new_row.contract_link or not new_row.contract_link_creation:
					to_generate = 1
				if new_row.contract_link_creation:
					generation_diff = get_datetime(now()) - get_datetime(new_row.contract_link_creation)
					generation_diff_hrs = generation_diff.total_seconds() / 3600
					if generation_diff_hrs and flt(generation_diff_hrs) >= 5:
						to_generate = 1
				if to_generate:
					access_link = create_contract_access_link(contract_id=self.oneflow_contract_id, participant_id=new_row.participant_id, user_email=self.user_email)
					if access_link and access_link.get("access_link"):
						new_row.contract_link = access_link.get("access_link")
						new_row.contract_link_creation = get_datetime(now())
						result = "New contract links generated"
		
		return result

	def on_trash(self):
		if self.oneflow_contract_id:
			delete_contract(contract_id=self.oneflow_contract_id, user_email=self.user_email)

	@frappe.whitelist()
	def add_individual_counterparty(self, country_code=None, title=None, name=None, delivery_channel=None, identification_number=None, email=None, phone_number=None, sign_method=None, signatory=None):
		participant_data = {
			"_permissions": {
				"contract:update": True
			},
		}
		if title:
			participant_data["title"] = title
		if name:
			participant_data["name"] = name
		if delivery_channel:
			participant_data["delivery_channel"] = delivery_channel
		if identification_number:
			participant_data["identification_number"] = identification_number
		if email:
			participant_data["email"] = email
		if phone_number:
			participant_data["phone_number"] = phone_number
		if sign_method:
			participant_data["sign_method"] = sign_method
		if signatory:
			participant_data["signatory"] = eval(signatory)

		data = {
			"participant": participant_data,
			"type": "individual"
		}
		if country_code:
			data["country_code"] = country_code

		contract_party = create_contract_party(contract_id=self.oneflow_contract_id, user_email=self.user_email, data=data)
		if contract_party.get("id"):
			frappe.msgprint("Counterparty added")
			update_oneflow_legals(docname=self.name)
			self.generate_contract_links()
		else:
			frappe.msgprint(str(contract_party))

	@frappe.whitelist()
	def add_company_counterparty(self, company_name=None, company_identification_number=None, country_code=None, title=None, name=None, delivery_channel=None, identification_number=None, email=None, phone_number=None, sign_method=None, signatory=None):
		participant_data = {
			"_permissions": {
				"contract:update": True
			},
		}
		if title:
			participant_data["title"] = title
		if name:
			participant_data["name"] = name
		if delivery_channel:
			participant_data["delivery_channel"] = delivery_channel
		if identification_number:
			participant_data["identification_number"] = identification_number
		if email:
			participant_data["email"] = email
		if phone_number:
			participant_data["phone_number"] = phone_number
		if sign_method:
			participant_data["sign_method"] = sign_method
		if signatory:
			participant_data["signatory"] = eval(signatory)

		data = {
			"participants": [participant_data],
			"type": "company"
		}
		if country_code:
			data["country_code"] = country_code
		if company_identification_number:
			data["identification_number"] = company_identification_number
		if company_name:
			data["name"] = company_name

		contract_party = create_contract_party(contract_id=self.oneflow_contract_id, user_email=self.user_email, data=data)
		if contract_party.get("id"):
			frappe.msgprint("Counterparty added")
			update_oneflow_legals(docname=self.name)
			self.generate_contract_links()
		else:
			frappe.msgprint(str(contract_party))

	@frappe.whitelist()
	def do_publish_contract(self, subject=None, message=None):
		data = {
			"subject": subject,
			"message": message
		}
		publish_contract_result = publish_contract(contract_id=self.oneflow_contract_id, user_email=self.user_email, data=data)
		if publish_contract_result.get("id"):
			frappe.msgprint("Contract published")
			update_oneflow_legals(docname=self.name)
			self.generate_contract_links()
		else:
			frappe.msgprint(str(publish_contract_result))

#erpyoupal.erpyoupal.doctype.oneflow_legal.oneflow_legal.update_oneflow_legals
@frappe.whitelist()
def update_oneflow_legals(docname=None):
	from erpyoupal.erpyoupal.doctype.oneflow_legal.oneflow_api import get_contract
	docs = frappe.get_all("OneFlow Legal", fields=['name'])
	if docs:
		for doc in docs:
			has_changes = 1
			doc = frappe.get_doc("OneFlow Legal", doc.get("name"))
			if doc.oneflow_contract_id and doc.user_email:
				contract_res = get_contract(contract_id=doc.oneflow_contract_id, user_email=doc.user_email)
				if str(doc.contract_state) != str(contract_res.get("state")):
					doc.contract_state = contract_res.get("state")

				included_participants = []
				if contract_res.get("parties"):					
					for party in contract_res['parties']:
						if party.get('participants'):
							for participant in party['participants']:
								row = {
									"participant_id": participant.get("id"),
									"participant_name": participant.get("name"),
									"participant_email": participant.get("email"),
									"sign_method": participant.get("sign_method"),
									"sign_state": participant.get("sign_state"),
									"party_id": party.get('id'),
									"party_name": party.get('name')
									}
								if row not in included_participants:
									included_participants.append(row)

						if party.get('participant'):
							participant = party['participant']
							row = {
								"participant_id": participant.get("id"),
								"participant_name": participant.get("name"),
								"participant_email": participant.get("email"),
								"sign_method": participant.get("sign_method"),
								"sign_state": participant.get("sign_state"),
								"party_id": party.get('id'),
								"party_name": party.get('name')
								}
							if row not in included_participants:
								included_participants.append(row)

				if included_participants:
					doc.participants = None
					for new_row in included_participants:
						doc.append('participants', new_row)

				if has_changes:
					doc.flags.ignore_permissions = True
					doc.save()

#erpyoupal.erpyoupal.doctype.oneflow_legal.oneflow_legal.create_partner_oneflow_nda
@frappe.whitelist(allow_guest=True)
def create_partner_oneflow_nda(organization, email):
	result = "Error, Please try again later"
	new_doc = frappe.new_doc("OneFlow Legal")
	new_doc.flags.ignore_permissions = True
	new_doc.flags.ignore_links = True
	new_doc.oneflow_workspace_id = "423427"
	new_doc.oneflow_workspace_name = "ERP Test"
	new_doc.oneflow_template_id = "OFT00019"
	new_doc.oneflow_template_name = "NDA"
	new_doc.title = "Non Disclosure Agreement"
	new_doc.user_email = "cid.z@youpalgroup.com"
	result = new_doc.insert()
	if frappe.get_all("Organizations", filters={"name": organization}, fields=["name"]):
		frappe.db.commit()
		org_doc = frappe.get_doc("Organizations", organization)
		org_doc.append("oneflow_contracts", {
			"oneflow_legal": org_doc.name,
			"title": new_doc.title,
			"state": new_doc.contract_state,
			"date_created": new_doc.creation,
			"template_id": new_doc.oneflow_template_id
		})
		org_doc.flags.ignore_permissions = True
		org_doc.flags.ignore_links = True
		org_doc.save()
	return result

#erpyoupal.erpyoupal.doctype.oneflow_legal.oneflow_legal.create_partner_oneflow_nda
@frappe.whitelist(allow_guest=False)
def get_organization_oneflow_legal():
	pass

