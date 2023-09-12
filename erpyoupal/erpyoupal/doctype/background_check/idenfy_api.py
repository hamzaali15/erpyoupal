from __future__ import unicode_literals
from hashlib import new
import frappe
from frappe import _
from frappe.utils import get_datetime, get_time, nowtime, today, now
import json
import shutil
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime
import os
import glob
import hashlib
from frappe.utils.background_jobs import enqueue

MY_API_KEY = 'goVYkO9WUHq '
MY_API_SECRET = 'fKwr1w642JRWPGuwduMO'

#erpyoupal.erpyoupal.doctype.background_check.idenfy_api.generate_idenfy_token_for_verification
@frappe.whitelist(allow_guest=True)
def generate_idenfy_token_for_verification(clientId):
	IDENFY_GENERATE_TOKEN_URL = 'https://ivs.idenfy.com/api/v2/token'
	response = requests.post(
		url=IDENFY_GENERATE_TOKEN_URL,
		json=dict(clientId=clientId),
		auth=(MY_API_KEY, MY_API_SECRET)
	)
	result = response.json()

	return result.get('authToken')

#erpyoupal.erpyoupal.doctype.background_check.idenfy_api.get_idenfy_token_for_verification
@frappe.whitelist(allow_guest=False)
def get_idenfy_token_for_verification(clientId):
	# Redirect user to iDenfy platform with a newly generated verification token.
	IDENFY_REDIRECT_URL = 'https://ivs.idenfy.com/api/v2/redirect'
	return f'{IDENFY_REDIRECT_URL}?authToken={generate_idenfy_token_for_verification(clientId)}'


#erpyoupal.erpyoupal.doctype.background_check.idenfy_api.callback_endpoint
@frappe.whitelist(allow_guest=True)
def callback_endpoint(*args, **kwargs):
	saved_args = locals()
	idenfy_response_data = saved_args['kwargs']
	new_doc = frappe.new_doc("Idenfy Callback")
	new_doc.response = str(idenfy_response_data)
	new_doc.flags.ignore_permissions = True
	new_doc.insert()

	return 'success', 200

#erpyoupal.erpyoupal.doctype.background_check.idenfy_api.update_background_check_document
@frappe.whitelist(allow_guest=False)
def update_background_check_document(data):
	docs = None
	document_name = None
	files_to_download = []
	if data.get('clientId') and not str(data.get('clientId')) in ['none', None, 'None', 'NONE']:
		docs = frappe.get_all("Background Check", filters={'email': str(data.get('clientId'))}, fields=['name'])
	if docs:
		doc = frappe.get_doc("Background Check", docs[0].name)
		doc.status = "Completed"
		doc.country = data.get('documentIssuingCountry')
		doc.platform = data.get('platform')
		doc.person_scan_reference = data.get('personScanRef')
		doc.scan_reference = data.get('scanRef')

		doc.document_type = data['data'].get('docType')
		doc.document_number = data['data'].get('docNumber')
		doc.document_first_name = data['data'].get('docFirstName')
		doc.document_last_name = data['data'].get('docLastName')
		doc.document_full_name = data['data'].get('fullName')
		doc.document_date_of_issue = data['data'].get('docDateOfIssue')
		doc.document_personal_code = data['data'].get('docPersonalCode')
		doc.document_date_of_birth = data['data'].get('docDob')
		doc.document_birth_place = data['data'].get('birthPlace')
		doc.document_sex = data['data'].get('docSex')
		doc.document_issuing_country = data['data'].get('docIssuingCountry')
		doc.document_nationality = data['data'].get('docNationality')
		doc.document_address = data['data'].get('address')

		doc.identification_status = data.get('identificationStatus')
		doc.id_type = data.get('idType')
		doc.id_number = data.get('idNumber')
		doc.id_first_name = data.get('idFirstName')
		doc.id_last_name = data.get('idLastName')
		doc.id_nationality = data.get('idNationality')
		doc.id_date_of_birth = data.get('idDob')
		doc.id_sex = data.get('idSex')
		doc.id_personal_code = data.get('idPersonalCode')
		doc.id_expiry = data.get('idExpiry')

		doc.client_id = data.get('clientId')
		doc.client_ip = data.get('clientIp')
		doc.client_ip_country = data.get('clientIpCountry')
		doc.client_location = data.get('clientLocation')
		doc.file_urls = None
		if data['fileUrls'].get('FRONT'):
			doc.append('file_urls', {
				'title': "Front",
				'url': data['fileUrls'].get('FRONT')
			})
			files_to_download.append({
				'title': 'front',
				'url': data['fileUrls'].get('FRONT')
			})
		
		if data['fileUrls'].get('BACK'):
			doc.append('file_urls', {
				'title': "Back",
				'url': data['fileUrls'].get('BACK')
			})
			files_to_download.append({
				'title': 'back',
				'url': data['fileUrls'].get('BACK')
			})
		
		if data['fileUrls'].get('FACE'):
			doc.append('file_urls', {
				'title': "Face",
				'url': data['fileUrls'].get('FACE')
			})
			files_to_download.append({
				'title': 'face',
				'url': data['fileUrls'].get('FACE')
			})
		
		if data['files']['text'].get('url'):
			doc.append('file_urls', {
				'title': "Text",
				'url': data['files']['text'].get('url')
			})

		#for file_doc in data['files']['documents']:
		#    if file_doc.get('url'):
		#        doc.append('file_urls', {
		#            'title': "Document",
		#            'url': file_doc.get('url')
		#        })

		document_name = doc.name
		if files_to_download:
			for file_to_download in files_to_download:
				if not doc.get(file_to_download.get('title')):
					file_name = "/files/"+str(document_name)+"_"+str(file_to_download.get('title'))+".jpeg"
					doc.update({file_to_download.get('title'): file_name})

		doc.flags.ignore_permissions = True
		doc.save()

	if files_to_download:
		for file_to_download in files_to_download:
			file_name = str(document_name)+"_"+str(file_to_download.get('title'))
			try:
				download_file_urls(file_url=file_to_download.get('url'), file_name=file_name, document_name=document_name, attached_to_field=file_to_download.get('title'))
			except Exception as e:
				raise Exception( e )
				#pass

def download_file_urls(file_url, file_name, document_name, attached_to_field):
	file_path = frappe.utils.get_site_path("public", "files", file_name)
	file_downloaded = 0
	file_readable = 0

	with requests.get(file_url, stream=True) as read_file:
		read_file_url = read_file.url
		file_path_to_save = file_path
		if not read_file_url.lower().endswith(('.jpeg')):
			file_path_to_save = file_path+".jpeg"
		open(file_path_to_save, "wb").write(read_file.content)
		file_downloaded = 1
		print('File Downloaded')

		with open(file_path, 'wb') as f:
			content = shutil.copyfileobj(read_file.raw, f)
			new_file = frappe.new_doc('File')
			new_file.content = content
			new_file.file_url = "/files/"+file_name+".jpeg"
			new_file.file_size = os.path.getsize(file_path)
			new_file.file_name = file_name
			if content:
				new_content_hash = content.encode()
				new_content_hash = hashlib.md5(new_content_hash).hexdigest()
				new_file.content_hash = new_content_hash
			new_file.folder = "Home"
			new_file.is_private = 0
			new_file.attached_to_doctype = 'Background Check'
			new_file.attached_to_name = document_name
			new_file.attached_to_field = attached_to_field
			new_file.flags.ignore_existing_file_check=True
			new_file.flags.ignore_permissions = True
			new_file.save()
			print('File Attached')

	return file_downloaded

# cmd
# manualAddressMatch
# manualAddress
# gdcMatch
# additionalData
# utility_data
# externalRef
# clientLocation
# clientIpCountry
# clientIp
# finishTime
# startTime
# clientId
# platform
# personScanRef
# scanRef
# identificationStatus
# idFirstName
# idLastName
# idPersonalCode
# idNumber
# idType
# idExpiry
# idDob
# idSex
# idNationality
# files
# documentIssuingCountry
# document_issuing_country
# suspectionReason
# final
# status = {
#     overall
#     suspicionReasons
#     fraudTags
#     mismatchTags
#     autoDocument
#     autoFace
#     manualDocument
#     manualFace
#     denyReasons
#     amlResultClass
#     additionalSteps
# }
# data = {
#     docFirstName
#     docLastName
#     docNumber
#     docPersonalCode
#     docExpiry
#     docDob
#     docDateOfIssue
#     docType
#     docSex
#     docNationality
#     docIssuingCountry
#     birthPlace
#     authority
#     address
#     mothersMaidenName
#     driverLicenseCategory
#     manuallyDataChanged
#     fullName
#     orgFirstName
#     orgLastName
#     orgNationality
#     orgBirthPlace
#     orgAuthority
#     orgAddress
#     selectedCountry
#     ageEstimate
#     clientIpProxyRiskLevel
#     duplicateFaces
#     duplicateDocFaces
# }
# fileUrls = {
#     BACK
#     FACE
#     FRONT
# }
