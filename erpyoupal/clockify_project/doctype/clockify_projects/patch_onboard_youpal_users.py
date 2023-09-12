import json

import frappe
from frappe import _
from frappe.utils import flt, getdate, time_diff_in_hours, get_datetime
from erpyoupal.clockify_project.clockify_api import add_project_to_clockify, validate_clockify_user, update_clockify_project, delete_clockify_project


#erpyoupal.clockify_project.doctype.clockify_projects.patch_onboard_youpal_users.create_internal_clockify_projects
@frappe.whitelist()
def create_internal_clockify_projects():
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
		'Umair Rafique': None,
		'Shekhar Kumar': None
		}

	internal_youpal_projects = [
		{
			'Project': 'Admin',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Karl Leahlander'],
				internal_youpal_members['Jessica L'],
				internal_youpal_members['Rajka Stjepanovic'],
				internal_youpal_members['Ruben Teijeiro']
			]
		},
		{
			'Project': 'Ajlan & Bros Ecommerce',
			'Members': [
				internal_youpal_members['Abraham Mathews'],
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Melvin Mathews'],
				internal_youpal_members['Dilan Samuelsson'],
				internal_youpal_members['Oleh Chuchman']
			]
		},
		{
			'Project': 'Amara Ecommerce',
			'Members': []
		},
		{
			'Project': 'AmoebaCRM Product',
			'Members': []
		},
		{
			'Project': 'Anomolies',
			'Members': [
				internal_youpal_members['Apostolis Argatzopoulos'],
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Dilan Samuelsson'],
				internal_youpal_members['Oleh Chuchman']
			]
		},
		{
			'Project': 'Contracts',
			'Members': [
				internal_youpal_members['Dilan Samuelsson']
			]
		},
		{
			'Project': 'DAM Product',
			'Members': []
		},
		{
			'Project': 'Delta Traffic Project Management',
			'Members': []
		},
		{
			'Project': 'Delta Traffic System ',
			'Members': [
				internal_youpal_members['Apostolis Argatzopoulos'],
				internal_youpal_members['Mumtoz']
			]
		},
		{
			'Project': 'Doktorsjouren 2019',
			'Members': []
		},
		{
			'Project': 'Doktorsjouren 2020 CRM',
			'Members': [
				internal_youpal_members['Amit Prithyani'],
				internal_youpal_members['Apostolis Argatzopoulos'],
				internal_youpal_members['Floris van Geel'],
				internal_youpal_members['Jovana Bajic'],
				internal_youpal_members['Mykola Dolynskyi']
			]
		},
		{
			'Project': 'Doktorsjouren 2020 WEB',
			'Members': [
				internal_youpal_members['Jovana Bajic'],
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'EPICA',
			'Members': [
				internal_youpal_members['Apostolis Argatzopoulos'],
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Ericsson Lighthouse 10',
			'Members': [
				internal_youpal_members['Marat Sadykov']
			]
		},
		{
			'Project': 'ERP Youpal',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Cid Amaro Zaragoza'],
				internal_youpal_members['John Matthew Diaz'],
				internal_youpal_members['Ranbir Balbir Singh'],
				internal_youpal_members['Sandeep Birwal'],
				internal_youpal_members['Taimur Hussain Khan']
			]
		},
		{
			'Project': 'EU- Everis',
			'Members': []
		},
		{
			'Project': 'Exeger Intranet',
			'Members': []
		},
		{
			'Project': 'Exeger Powerfoyle',
			'Members': []
		},
		{
			'Project': 'Exeger Web Builder',
			'Members': []
		},
		{
			'Project': 'Exove Green Deal Office',
			'Members': []
		},
		{
			'Project': 'Exove KT',
			'Members': []
		},
		{
			'Project': 'Exove Taike',
			'Members': []
		},
		{
			'Project': 'Forefront_Greencargo',
			'Members': []
		},
		{
			'Project': 'Futurelab',
			'Members': []
		},
		{
			'Project': 'General Communications',
			'Members': []
		},
		{
			'Project': 'HR',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Shieva Saavedra']
			]
		},
		{
			'Project': 'Integration Fortnox',
			'Members': [
				internal_youpal_members['Rajka Stjepanovic']
			]
		},
		{
			'Project': 'Legal Youpal',
			'Members': [
				internal_youpal_members['Dilan Samuelsson'],
				internal_youpal_members['Oleh Chuchman']
			]
		},
		{
			'Project': 'Legal Youradvisors',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Oleh Chuchman']
			]
		},
		{
			'Project': 'Lenx Product',
			'Members': [
				internal_youpal_members['Apostolis Argatzopoulos'],
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Khurram Bilal'],
				internal_youpal_members['Mumtoz'],
				internal_youpal_members['Shekhar Kumar']
			]
		},
		{
			'Project': 'Letswork',
			'Members': [
				internal_youpal_members['Apostolis Argatzopoulos'],
				internal_youpal_members['shah.a']
			]
		},
		{
			'Project': 'MarCom',
			'Members': [
				internal_youpal_members['Gustaff Amboka Ndalo'],
				internal_youpal_members['Stephen Kanyi'],
			]
		},
		{
			'Project': 'Mautic Product',
			'Members': []
		},
		{
			'Project': 'Niels- Groenlinks',
			'Members': []
		},
		{
			'Project': 'NordFK',
			'Members': []
		},
		{
			'Project': 'Pandemic App Product',
			'Members': []
		},
		{
			'Project': 'Partner Management',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Paternity Leave',
			'Members': [
				internal_youpal_members['Shieva Saavedra']
			]
		},
		{
			'Project': 'Phase 2 Transcom Web 2022',
			'Members': [
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Floris van Geel'],
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Karen Pirumyan']
			]
		},
		{
			'Project': 'Product Management',
			'Members': [
				internal_youpal_members['Jovana Bajic']
			]
		},
		{
			'Project': 'Project Admin',
			'Members': []
		},
		{
			'Project': 'Sales',
			'Members': []
		},
		{
			'Project': 'Service Desk',
			'Members': [
				internal_youpal_members['Dorilyn Sambrano'],
				internal_youpal_members['John Louie Torres']
			]
		},
		{
			'Project': 'Sinch',
			'Members': []
		},
		{
			'Project': 'Snipe IT Product',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Time Off',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Transcom PM',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Transcom SLA',
			'Members': [
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'Transcom T&M',
			'Members': [
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'Transcom web refresh 2021 Phase 1',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Karen Pirumyan'],
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Ruben Teijeiro'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'UN- Softescu',
			'Members': []
		},
		{
			'Project': 'Uteckie Website',
			'Members': [
				internal_youpal_members['Sanal Kappakkuth']
			]
		},
		{
			'Project': 'Web Builder Product',
			'Members': []
		},
		{
			'Project': 'Welinoco Migration',
			'Members': [
				internal_youpal_members['Shekhar Kumar']
			]
		},
		{
			'Project': 'Welinoco SLA',
			'Members': [
				internal_youpal_members['Floris van Geel'],
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Ruben Teijeiro'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'Welinoco T&M',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Ruben Teijeiro'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'WTO_Softescu',
			'Members': []
		},
		{
			'Project': 'XShore Boat Configurator',
			'Members': []
		},
		{
			'Project': 'XShore DevOps',
			'Members': []
		},
		{
			'Project': 'XShore IoT',
			'Members': []
		},
		{
			'Project': 'XShore Postmortem',
			'Members': []
		},
		{
			'Project': 'XShore Project Management',
			'Members': []
		},
		{
			'Project': 'XShore PWA',
			'Members': []
		},
		{
			'Project': 'Youbot Product',
			'Members': [
				internal_youpal_members['Floris van Geel']
			]
		},
		{
			'Project': 'Youchat Product',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Youcloud DevOps',
			'Members': [
				internal_youpal_members['Trincu Dan-Andrei']
			]
		},
		{
			'Project': 'Youcloud Web',
			'Members': [
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'Yougig',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Mumtoz'],
				internal_youpal_members['Apostolis Argatzopoulos']
			]
		},
		{
			'Project': 'Youincubator',
			'Members': [
				internal_youpal_members['Floris van Geel'],
				internal_youpal_members['Ruben Teijeiro']
			]
		},
		{
			'Project': 'Youmedico App Product',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Jovana Bajic'],
				internal_youpal_members['Rajka Stjepanovic'],
				internal_youpal_members['Adham Magdy Ahmed'],
				internal_youpal_members['HOUAISS ABDERAZAK'],
				internal_youpal_members['Sajjad Raza']
			]
		},
		{
			'Project': 'Youmeet Product',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Youpal Group Email',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Youpal Group Website',
			'Members': [
				internal_youpal_members['Rajka Stjepanovic']
			]
		},
		{
			'Project': 'youpal internal devops',
			'Members': [
				internal_youpal_members['Dorilyn Sambrano'],
				internal_youpal_members['Floris van Geel'],
				internal_youpal_members['Mumtoz'],
				internal_youpal_members['Mykola Dolynskyi'],
				internal_youpal_members['Shekhar Kumar'],
				internal_youpal_members['Shieva Saavedra'],
				internal_youpal_members['Trincu Dan-Andrei'],
			]
		},
		{
			'Project': 'Youpal Tech Lead',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Mykola Dolynskyi']
			]
		},
		{
			'Project': 'YourAdvisorsWebsite',
			'Members': []
		},
		{
			'Project': 'Youschool App Product',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		},
		{
			'Project': 'Youschool Website',
			'Members': [
				internal_youpal_members['HOUAISS ABDERAZAK'],
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Shalini kamboj']
			]
		},
		{
			'Project': 'YouSuite Product',
			'Members': [
				internal_youpal_members['James Baker-Duly'],
				internal_youpal_members['Melvin Mathews'],
				internal_youpal_members['Umair Rafique']
			]
		},
		{
			'Project': 'Zammad Product',
			'Members': [
				internal_youpal_members['James Baker-Duly']
			]
		}
	]

	for proj in internal_youpal_projects:
		if proj['Project']:
			new_doc = frappe.new_doc("Clockify Projects")
			new_doc.workspace = 'Youpal Group - App'
			new_doc.erp_project_name = proj['Project']
			if proj['Members']:
				for memb in proj['Members']:
					if memb:
						new_doc.append('erp_members', {
							'clockify_user': memb
						})
			new_doc.flags.ignore_permissions = True
			new_doc.flags.ignore_links = True
			new_doc.insert()
			#try:
			#	new_doc.insert()
			#except:
			#	pass
