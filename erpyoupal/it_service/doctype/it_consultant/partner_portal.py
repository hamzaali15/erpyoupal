import frappe
from frappe.utils import flt, getdate, now

#Add IT Consultant staff
#erpyoupal.it_service.doctype.it_consultant.partner_portal.add_itconsultant_staff
@frappe.whitelist()
def add_itconsultant_staff(data_entry):
    email_primary = data_entry.get("email_primary")
    if not email_primary:
        frappe.throw("Email Primary is required")

    if frappe.get_all("IT Consultant", filters={"email_primary": email_primary}):
        frappe.throw("Email already used")
    else:
        new_doc = frappe.new_doc("People")
        new_doc.language_proficiency_level = data_entry.get("language_proficiency_level")
        data_entry.pop("language_proficiency_level")
        new_doc.experience = data_entry.get("experience")
        data_entry.pop("experience")
        new_doc.skills = data_entry.get("skills")
        data_entry.pop("skills")
        new_doc.update(data_entry)
        new_doc.append('email', {'email': email_primary})
        if data_entry.get("email_secondary"):
            new_doc.append('email', {'email': data_entry.get("email_secondary")})
        if data_entry.get("mobile_primary"):
            new_doc.append('mobile', {'mobile': data_entry.get("mobile_primary")})
        new_doc.flags.ignore_permissions = True
        new_doc.flags.ignore_links = True
        new_doc_response = new_doc.insert()
        new_doc_response = new_doc_response.__dict__
        final_new_doc_response = {
            "personal_id": new_doc_response.get("personal_id"),
            "position_title": new_doc_response.get("position_title"),
            "first_name": new_doc_response.get("first_name"),
            "last_name": new_doc_response.get("last_name"),
            "mobile_primary": new_doc_response.get("mobile_primary"),
            "date_of_birth": new_doc_response.get("date_of_birth"),
            "gender": new_doc_response.get("gender"),
            "resume": new_doc_response.get("resume"),
            "experience_since": new_doc_response.get("experience_since"),
            "email_primary": new_doc_response.get("email_primary"),
            "association": new_doc_response.get("association"),
            "rate_hourly": new_doc_response.get("rate_hourly"),
            "nda": new_doc_response.get("nda"),
            "location": new_doc_response.get("location"),
            "email_secondary": new_doc_response.get("email_secondary"),
            "work_type": new_doc_response.get("work_type"),
            "work_destination": new_doc_response.get("work_destination"),
            "consultant_description": new_doc_response.get("consultant_description"),
            "linkedin": new_doc_response.get("linkedin"),
            "facebook": new_doc_response.get("facebook"),
            "instagram": new_doc_response.get("instagram"),
            "twitter": new_doc_response.get("twitter"),
            "fiverr": new_doc_response.get("fiverr"),
            "github": new_doc_response.get("github"),
            "upwork": new_doc_response.get("upwork"),
            "stackoverflow": new_doc_response.get("stackoverflow"),
            "skills": new_doc_response.get("skills"),
            "experience": new_doc_response.get("experience"),
            "language_proficiency_level": new_doc_response.get("language_proficiency_level")
        }
        frappe.local.response['data'] = final_new_doc_response
        frappe.local.response['message'] = "success"

#Edit IT Consultant staff
#erpyoupal.it_service.doctype.it_consultant.partner_portal.edit_itconsultant_staff
@frappe.whitelist()
def edit_itconsultant_staff(data_entry):
    email_primary = data_entry.get("email_primary")
    if not email_primary:
        frappe.throw("Email Primary is required")
    existing_people = frappe.get_all("People", filters={"email_address": email_primary}, fields=['name', 'email_address'])
    if not existing_people:
        frappe.throw("Staff not found")
    else:
        cur_doc = frappe.get_doc("People", existing_people[0].name)
        cur_doc.language_proficiency_level = data_entry.get("language_proficiency_level")
        data_entry.pop("language_proficiency_level")
        cur_doc.experience = data_entry.get("experience")
        data_entry.pop("experience")
        cur_doc.skills = data_entry.get("skills")
        data_entry.pop("skills")
        cur_doc.update(data_entry)
        #cur_doc.append('email', {'email': email_primary})
        if data_entry.get("email_secondary"):
            cur_doc.append('email', {'email': data_entry.get("email_secondary")})
        if data_entry.get("mobile_primary"):
            cur_doc.append('mobile', {'mobile': data_entry.get("mobile_primary")})
        cur_doc.flags.ignore_permissions = True
        cur_doc.flags.ignore_links = True
        cur_doc_response = cur_doc.save()
        cur_doc_response = cur_doc_response.__dict__
        final_cur_doc_response = {
            "personal_id": cur_doc_response.get("personal_id"),
            "position_title": cur_doc_response.get("position_title"),
            "first_name": cur_doc_response.get("first_name"),
            "last_name": cur_doc_response.get("last_name"),
            "mobile_primary": cur_doc_response.get("mobile_primary"),
            "date_of_birth": cur_doc_response.get("date_of_birth"),
            "gender": cur_doc_response.get("gender"),
            "resume": cur_doc_response.get("resume"),
            "experience_since": cur_doc_response.get("experience_since"),
            "email_primary": cur_doc_response.get("email_primary"),
            "association": cur_doc_response.get("association"),
            "rate_hourly": cur_doc_response.get("rate_hourly"),
            "nda": cur_doc_response.get("nda"),
            "location": cur_doc_response.get("location"),
            "email_secondary": cur_doc_response.get("email_secondary"),
            "work_type": cur_doc_response.get("work_type"),
            "work_destination": cur_doc_response.get("work_destination"),
            "consultant_description": cur_doc_response.get("consultant_description"),
            "linkedin": cur_doc_response.get("linkedin"),
            "facebook": cur_doc_response.get("facebook"),
            "instagram": cur_doc_response.get("instagram"),
            "twitter": cur_doc_response.get("twitter"),
            "fiverr": cur_doc_response.get("fiverr"),
            "github": cur_doc_response.get("github"),
            "upwork": cur_doc_response.get("upwork"),
            "stackoverflow": cur_doc_response.get("stackoverflow"),
            "skills": cur_doc_response.get("skills"),
            "experience": cur_doc_response.get("experience"),
            "language_proficiency_level": cur_doc_response.get("language_proficiency_level")
        }
        frappe.local.response['data'] = final_cur_doc_response
        frappe.local.response['message'] = "success"