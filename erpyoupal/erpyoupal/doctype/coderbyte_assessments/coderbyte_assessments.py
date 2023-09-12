# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CoderbyteAssessments(Document):
	pass

# erpyoupal.erpyoupal.doctype.coderbyte_assessments.coderbyte_assessments.list_coderbyte_assessments
@frappe.whitelist(allow_guest=True)
def list_coderbyte_assessments(job_applicant=None,it_consultant=None):
	skill_test_list = []
	if job_applicant:
		it_consultant = frappe.db.get_value('Job Applicant History',{'job_applicant':job_applicant},'parent')
	if it_consultant:
		skill_test = frappe.get_all("Skill Test Coderbyte History", filters={"parent":it_consultant}, pluck="skill_test_coderbyte_id")
		for skill in skill_test:
			skill_test_list.append(frappe.db.get_value('Skill Test',skill,'assessment_id'))

		final_dict = []
		assessment_list = frappe.db.sql("""SELECT `name` as assessment_id,`name` as assessment_name FROM `tabCoderbyte Assessments` WHERE disable_assessment = 0""",as_dict=True)
		for assessment in assessment_list:
			if assessment['assessment_id'] not in skill_test_list:
				final_dict.append(assessment)
		return final_dict
	else:
		return []
# erpyoupal.erpyoupal.doctype.coderbyte_assessments.coderbyte_assessments.check_enable_skill_test
@frappe.whitelist(allow_guest=True)
def check_enable_skill_test():
	enable_testgorilla = frappe.db.get_single_value('System Settings', 'enable_testgorilla')
	enable_coderbyte = frappe.db.get_single_value('System Settings', 'enable_coderbyte')
	return enable_testgorilla,enable_coderbyte


