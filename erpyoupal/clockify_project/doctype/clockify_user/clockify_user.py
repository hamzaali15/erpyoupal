# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ClockifyUser(Document):
	def validate(self):
		if self.first_name:
			self.full_name = self.first_name
		
		if self.last_name:
			self.full_name = self.last_name

		if self.first_name and self.last_name:
			self.full_name = self.first_name+" "+self.last_name


#erpyoupal.clockify_project.doctype.clockify_user.clockify_user.get_clockify_user
@frappe.whitelist()
def get_clockify_user(filters={}):
	result = []
	docs = frappe.get_all("Clockify User", filters=filters, fields=["name"])
	if docs:
		for dos in docs:
			doc = frappe.get_doc("Clockify User", dos.name)
			result.append(doc)

	return result


#erpyoupal.clockify_project.doctype.clockify_user.clockify_user.create_internal_youpal_users
@frappe.whitelist()
def create_internal_youpal_users():
	internal_youpal_members = {
		'James Baker-Duly': 'james.bakerduly@gmail.com',
		'Karl Leahlander': 'karl@youpal.se',
		'Jessica L': 'jessical__@hotmail.com',
		'Rajka Stjepanovic': 'rajka@youpal.se',
		'Ruben Teijeiro': 'ruben@youpal.se',
		'Mykola Dolynskyi': 'gospodin.p.zh@gmail.com',
		'Melvin Mathews': 'melvin.mathews@hotmail.com',
		'Dilan Samuelsson': 'dilan@youpal.se',
		'Oleh Chuchman': 'oleh.ch@youpal.se',
		'Abraham Mathews': None,
		'Apostolis Argatzopoulos': 'aposarga@gmail.com',
		'Mumtoz': 'mumtozvalijonov@gmail.com',
		'Amit Prithyani': 'interact2amit@gmail.com',
		'Floris van Geel': 'floris@040lab.com',
		'Jovana Bajic': 'jovana@youpal.se',
		'Shalini kamboj': 'shalini10april@gmail.com',
		'Marat Sadykov': 'marat@youpal.se',
		'Cid Amaro Zaragoza': 'cidzaragoza@yahoo.com',
		'John Matthew Diaz': 'diazjohnmatthew@gmail.com',
		'Ranbir Balbir Singh': 'rawat.ranvirsingh@gmail.com',
		'Sandeep Birwal': 'birwalsandeep@gmail.com',
		'Taimur Hussain Khan': 'taimooryousaf69@gmail.com',
		'Shieva Saavedra': 'shievasaavedra28@gmail.com',
		'Khurram Bilal': 'kb.nawaz@gmail.com',
		'shah.a': 'Shahalam7303@gmail.com',
		'Gustaff Amboka Ndalo': 'gustaffndalo@gmail.com',
		'Stephen Kanyi': 'kicheodinga@gmail.com',
		'Karen Pirumyan': 'k.pirumyan@gmail.com',
		'Dorilyn Sambrano': 'dorilyn15@gmail.com',
		'John Louie Torres': 'dyenlouie03@gmail.com',
		'Sanal Kappakkuth': 'sanal.k@youpal.es',
		'Trincu Dan-Andrei': 'trincudan@gmail.com',
		'Adham Magdy Ahmed': 'adhammagdy.dev@gmail.com',
		'HOUAISS ABDERAZAK': 'abderazakhouaiss@gmail.com',
		'Sajjad Raza': 'itszaidi@gmail.com',
		'Umair Rafique': None
	}

	for usr in internal_youpal_members:
		email = internal_youpal_members[usr]
		if email:
			if not frappe.get_all("Clockify User", filters={"email": email}, fields=["name"]):
				new_doc = frappe.new_doc("Clockify User")
				new_doc.first_name = frappe.db.get_value('People', {'email_address': email}, 'first_name')
				new_doc.last_name = frappe.db.get_value('People', {'email_address': email}, 'last_name')
				new_doc.full_name = frappe.db.get_value('People', {'email_address': email}, 'person_name')
				new_doc.workspace_id = 'Youpal Group - App'
				new_doc.user_id = email
				new_doc.email = email
				new_doc.flags.ignore_permissions = True
				new_doc.flags.ignore_links = True
				new_doc.insert()
				#try:
				#	new_doc.insert()
				#except:
				#	pass

#erpyoupal.clockify_project.doctype.clockify_user.clockify_user.create_clockify_user_from_people
@frappe.whitelist()
def create_clockify_user_from_people(email):
	workspace_id = None
	peoples = frappe.get_all('People', filters={'email_address': email}, fields=['name', 'first_name', 'last_name', 'person_name', 'organization_name'])
	if peoples:
		if peoples[0].organization_name:
			workspace_id = frappe.db.get_value('Clockify Workspace', {'organization': peoples[0].organization_name}, 'name')

		if not frappe.get_all("Clockify User", filters={"email": email}, fields=["name"]):
			new_doc = frappe.new_doc("Clockify User")
			new_doc.first_name = peoples[0].first_name
			new_doc.last_name = peoples[0].last_name
			new_doc.full_name = peoples[0].person_name
			new_doc.workspace_id = 'Youpal Group'
			new_doc.user_id = email
			new_doc.email = email
			new_doc.flags.ignore_permissions = True
			new_doc.flags.ignore_links = True
			new_doc.insert()

#erpyoupal.clockify_project.doctype.clockify_user.clockify_user.patch_create_clockify_user_from_people
@frappe.whitelist()
def patch_create_clockify_user_from_people():
	peoples = frappe.get_all('People', fields=['name', 'first_name', 'last_name', 'person_name', 'organization_name', 'email_address'])
	if peoples:
		for row_peoples in peoples:
			if row_peoples.email_address:
				create_clockify_user_from_people(email=row_peoples.email_address)

#erpyoupal.clockify_project.doctype.clockify_user.clockify_user.patch_default_workspace_clockify_user
@frappe.whitelist()
def patch_default_workspace_clockify_user():
	users = frappe.get_all('Clockify User', fields=['name'])
	for row in users:
		frappe.db.set_value('Clockify User', row.name, 'workspace_id', 'Youpal Group')
		frappe.db.commit()