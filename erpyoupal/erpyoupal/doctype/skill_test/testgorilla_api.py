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

#https://help.testgorilla.com/testgorilla-public-api-documentation


#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.get_testgorilla_settings
def get_testgorilla_settings():
    testgorilla_settings = None
    #testgorilla_settings = frappe.get_doc('TestGorilla Settings')
    testgorilla_settings = frappe.get_single("TestGorilla Settings")
    testgorilla_settings.strPassword = testgorilla_settings.get_password('password')
    if not testgorilla_settings.username or not testgorilla_settings.password:
        return False
    else:
        return testgorilla_settings

#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.get_authentication_token_testgorilla
def get_authentication_token_testgorilla():
    result = "No response"
    testgorilla_settings = get_testgorilla_settings()
    if testgorilla_settings:
        url = "https://app.testgorilla.com/api/profiles/login/"
        headers = CaseInsensitiveDict()
        headers["content-type"] = "application/json"
        headers["Origin"] = "https://app.testgorilla.com"
        data = '{"username":"'+str(testgorilla_settings.username)+'",'+'"password":"'+str(testgorilla_settings.strPassword)+'"}'
        json_response = requests.post(url, headers=headers, data=data).json()
        result = json_response
        if result.get('token'):
            return result.get('token')
        else:
            return False
    else:
        return False

#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.get_list_of_assessment
@frappe.whitelist(allow_guest=True)
def get_list_of_assessment():
    #GET https://app.testgorilla.com/api/assessments/
    result = "No response"
    authentication_token = get_authentication_token_testgorilla()
    if authentication_token:
        url = "https://app.testgorilla.com/api/assessments/?limit=999"
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Token "+authentication_token
        json_response = requests.get(url, headers=headers).json()
        result = json_response
    else:
        result = "Insufficient TestGorilla Settings"

    return result

#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.get_assessment_details
@frappe.whitelist()
def get_assessment_details(assessment_id):
    #GET https://app.testgorilla.com/api/assessments/<ASSESSMENT_ID>
    result = "No response"
    authentication_token = get_authentication_token_testgorilla()
    if authentication_token:
        url = f"https://app.testgorilla.com/api/assessments/{assessment_id}"
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Token "+authentication_token
        json_response = requests.get(url, headers=headers).json()
        result = json_response
    else:
        result = "Insufficient TestGorilla Settings"

    return result

#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.delete_candidate_assessment
@frappe.whitelist()
def delete_candidate_assessment(candidature_id):
    #DELETE 'https://app.testgorilla.com/api/assessments/candidature/<CANDIDATURE_ID>/' \
    result = "No response"
    authentication_token = get_authentication_token_testgorilla()
    if authentication_token:
        url = f"https://app.testgorilla.com/api/assessments/candidature/{candidature_id}/"
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Token "+authentication_token
        requests_response = requests.delete(url, headers=headers)
        if requests_response.status_code in [404, '404']:
            result = "Unable to delete candidate"
        elif requests_response.status_code in [204, '204']:
            result = "Candidate removed"
        else:
            result = "Failed"
        requests_response.close()
    else:
        result = "Insufficient TestGorilla Settings"

    return result


#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.invite_candidate_using_email
@frappe.whitelist()
#Inviting a candidate using their email address
def invite_candidate_using_email(assessment_id, data):
    #DATA MUST HAVE:
    #1. email
    #2. first_name
    #3. last_name (OPTIONAL)
    
    result = "No response"
    authentication_token = get_authentication_token_testgorilla()
    if authentication_token:
        url = f"https://app.testgorilla.com/api/assessments/{assessment_id}/invite_candidate/"
        headers = CaseInsensitiveDict()
        headers["content-type"] = "application/json"
        headers["Authorization"] = "Token "+authentication_token
        json_response = requests.post(url, headers=headers, data=data).json()
        result = json_response
    else:
        result = "Insufficient TestGorilla Settings"

    return result

#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.get_asessment_result
@frappe.whitelist()
def get_asessment_result(assessment_id=None, testtaker_id=None):
    #GET https://app.testgorilla.com/api/assessments/results/?candidature__assessment=<ASSESSMENT_ID>&candidature__test_taker=<TESTTAKER_ID>
    result = "No response"
    authentication_token = get_authentication_token_testgorilla()
    if authentication_token:
        url = f"https://app.testgorilla.com/api/assessments/results/?candidature__assessment={assessment_id}&candidature__test_taker={testtaker_id}"
        headers = CaseInsensitiveDict()
        headers["content-type"] = "application/json"
        headers["Authorization"] = "Token "+authentication_token
        json_response = requests.get(url, headers=headers).json()
        result = json_response
    else:
        result = "Insufficient TestGorilla Settings"

    return result


#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.get_asessment_result
@frappe.whitelist()
def get_asessment_candidate_list(assessment_id=None):
    #GET https://app.testgorilla.com/api/assessments/candidature?assessment=<ASSESSMENT_ID>
    result = "No response"
    authentication_token = get_authentication_token_testgorilla()
    if authentication_token:
        url = f"https://app.testgorilla.com/api/assessments/candidature?assessment={assessment_id}"
        headers = CaseInsensitiveDict()
        headers["content-type"] = "application/json"
        headers["Authorization"] = "Token "+authentication_token
        json_response = requests.get(url, headers=headers).json()
        result = json_response
    else:
        result = "Insufficient TestGorilla Settings"

    return result


#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.populate_testgorilla_assessments
@frappe.whitelist(allow_guest=True)
def populate_testgorilla_assessments():
    list_of_assessment = get_list_of_assessment()
    if list_of_assessment and list_of_assessment.get('results'):
        for assessment in list_of_assessment.get('results'):
            disable_assessment = 0
            if str(assessment.get('status')) in ['archived']:
                disable_assessment = 1

            erp_asessments = frappe.get_all("TestGorilla Asessment", filters={"assessment_id": assessment.get('id')}, fields=["name", "disable_assessment"])
            if erp_asessments:
                erp_asessment = frappe.get_doc("TestGorilla Asessment", erp_asessments[0].name)
                erp_asessment.disable_assessment = disable_assessment
                erp_asessment.flags.ignore_permissions = True
                erp_asessment.save()
            else:
                assessment['disable_assessment'] = disable_assessment
                new_doc = frappe.new_doc("TestGorilla Asessment")
                new_doc.assessment_name = assessment.get('name')
                new_doc.assessment_id = assessment.get('id')
                new_doc.disable_assessment = disable_assessment
                new_doc.flags.ignore_permissions = True
                new_doc.insert()

#erpyoupal.erpyoupal.doctype.skill_test.testgorilla_api.get_testgorilla_assessments
#@frappe.whitelist(allow_guest=True)
#def get_testgorilla_assessments(job_applicant=None):
#    list_of_assessment = get_list_of_assessment()
#    final_dict = []
    

    #getting existing assessment
#    skill_test_list = []
#    if job_applicant:
#        skill_test = frappe.get_all("Skill Test", filters={"job_applicant": job_applicant}, fields=["assessment_id"])
#    else:
#        skill_test = frappe.get_all("Skill Test", fields=["assessment_id"])
#    for skill in skill_test:
#        skill_test_list.append(skill.get("assessment_id"))


#    if list_of_assessment.get('results'):
#        for assessment in list_of_assessment.get('results'):
#            erp_asessments = frappe.get_all("TestGorilla Asessment", filters={"assessment_id": assessment.get('id')}, fields=["name", "disable_assessment"])
#            if erp_asessments:
#                assessment['disable_assessment'] = erp_asessments[0].disable_assessment
#            else:
#                assessment['disable_assessment'] = 0
#                new_doc = frappe.new_doc("TestGorilla Asessment")
#                new_doc.assessment_name = assessment.get('name')
#                new_doc.assessment_id = assessment.get('id')
#                new_doc.flags.ignore_permissions = True
#                new_doc.insert()

#            if str(assessment.get('id')) not in skill_test_list:
#                final_dict.append({'assessment_id':assessment.get('id'),'assessment_name':assessment.get('name')})

#    return final_dict

@frappe.whitelist(allow_guest=True)
def get_testgorilla_assessments(job_applicant=None,it_consultant=None,job_opening=None):
    skill_test_list = []
    testgorilla_relevant_tests = []
    if job_opening:
        if frappe.get_all('Job Opening', filters={'name': job_opening}, fields=['name']):
            job_opening_doc = frappe.get_doc('Job Opening', job_opening)
            if job_opening_doc.testgorilla_relevant_tests:
                for row in job_opening_doc.testgorilla_relevant_tests:
                    if row.assessment_id not in testgorilla_relevant_tests:
                        testgorilla_relevant_tests.append(row.assessment_id)

    if job_applicant:
        it_consultant = frappe.db.get_value('Job Applicant History',{'job_applicant':job_applicant},'parent')
    if it_consultant:
        skill_test = frappe.get_all("Skill Test History", filters={"parent":it_consultant}, pluck="skill_test_id")
        # else:
        #     skill_test = frappe.get_all("Skill Test", fields=["assessment_id"])
        for skill in skill_test:
            skill_test_list.append(frappe.db.get_value('Skill Test',skill,'assessment_id'))

        final_dict = []
        assessment_list = frappe.db.sql("""SELECT `name` as assessment_id, assessment_name FROM `tabTestGorilla Asessment` WHERE disable_assessment = 0""",as_dict=True)
        for assessment in assessment_list:
            if assessment['assessment_id'] not in skill_test_list:
                if testgorilla_relevant_tests:
                    if assessment['assessment_id'] in testgorilla_relevant_tests:
                        final_dict.append(assessment)
                else:
                    final_dict.append(assessment)
        return final_dict
    else:
        return []
