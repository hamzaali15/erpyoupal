import frappe
from frappe.utils import flt

#Get Logged In User Organization details
#erpyoupal.erpyoupal.doctype.organizations.partner_portal.get_loggedin_user_organization
@frappe.whitelist()
def get_loggedin_user_organization(user_id):
    existing_user = frappe.get_all("User", filters={"name": user_id}, fields=["name", "organization"])
    if existing_user:
        organization = existing_user[0].organization
        if not organization:
            frappe.throw("User has no organization linked")

        if frappe.get_all("Organizations", filters={"name": organization}):
            result = {
                "add_social": "",
                "logo": "",
                "organization_name": "",
                "hq": "",
                "founded": "",
                "speciality": "",
                "organization_size": "",
                "company_website": "",
                "bank_name": "",
                "account_number": "",
                "clearing_number": "",
                "iban_swift": "",
                "invoice_name": "",
                "invoice_email": "",
                "invoice_mobile": ""
            }

            doc = frappe.get_doc("Organizations", organization)
            speciality_list = []
            if doc.speciality:
                for row_speciality in doc.speciality:
                    speciality_list.append(row_speciality.speciality)

            social_list = []
            if doc.add_social:
                for row_add_social in doc.add_social:
                    social_name = row_add_social.social
                    social_name = str(social_name).lower()
                    if social_name in ["facebook", "fb", "face book"]:
                        social_name = "facebook"
                    if social_name in ["instagram", "ig", "insta gram"]:
                        social_name = "instagram"
                    if social_name in ["linkedin", "linked in"]:
                        social_name = "linkedin"
                    if social_name in ["twitter", "twit ter"]:
                        social_name = "twitter"

                    speciality_list.append({
                        social_name: row_add_social.link,
                    })

            if doc.logo:
                result["logo"] = doc.logo
            if doc.organization_name:
                result["organization_name"] = doc.organization_name
            if doc.hq:
                result["hq"] = doc.hq
            if doc.founded:
                result["founded"] = doc.founded
            if speciality_list:
                result["speciality"] = speciality_list
            if doc.organization_size:
                result["organization_size"] = doc.organization_size
            if doc.company_website:
                result["company_website"] = doc.company_website
            if doc.bank_name:
                result["bank_name"] = doc.bank_name
            if doc.account_number:
                result["account_number"] = doc.account_number
            if doc.clearing_number:
                result["clearing_number"] = doc.clearing_number
            if doc.iban_swift:
                result["iban_swift"] = doc.iban_swift
            if doc.invoice_name:
                result["invoice_name"] = doc.invoice_name
            if doc.invoice_email:
                result["invoice_email"] = doc.invoice_email
            if doc.invoice_mobile:
                result["invoice_mobile"] = doc.invoice_mobile
            if social_list:
                result["add_social"] = social_list

            frappe.local.response['data'] = result
    else:
        frappe.throw("User not found")


#Update User Organization data
#erpyoupal.erpyoupal.doctype.organizations.partner_portal.update_user_organization_data
@frappe.whitelist()
def update_user_organization_data(organization, new_data):
    if frappe.get_all("Organizations", filters={"name": organization}):
        cur_doc = frappe.get_doc("Organizations", organization)
#        doc_new_data = {
#            "logo": new_data.get("organization_logo"),
#            "organization_name": new_data.get("organization_name"),
#            "hq": new_data.get("head_quearters"),
#            "founded": new_data.get("founded"),
#            "organization_size": new_data.get("organization_size"),
#            "company_website": new_data.get("website"),
#            "bank_name": new_data.get("banking_bank_name"),
#            "account_number": new_data.get("banking_account_number"),
#            "clearing_number": new_data.get("banking_clearing_number"),
#            "iban_swift": new_data.get("banking_iban_swift"),
#            "invoice_name": new_data.get("invoice_name"),
#            "invoice_email": new_data.get("invoice_email"),
#            "invoice_mobile": new_data.get("invoice_mobile"),
#            "speciality": new_data.get("speciality"),
#            "add_social": new_data.get("socials")
#        }
        cur_doc.update(new_data)
        cur_doc.flags.ignore_permissions = True
        cur_doc.flags.ignore_links = True
        doc_save_response = cur_doc.save()
        doc_save_response = doc_save_response.__dict__
        
        final_doc_save_response = {
            "logo": doc_save_response.get("logo") if doc_save_response.get("logo") else "",
            "organization_name": doc_save_response.get("organization_name") if doc_save_response.get("organization_name") else "",
            "hq": doc_save_response.get("hq") if doc_save_response.get("hq") else "",
            "founded": doc_save_response.get("founded") if doc_save_response.get("founded") else "",
            "organization_size": doc_save_response.get("organization_size") if doc_save_response.get("organization_size") else "",
            "company_website": doc_save_response.get("company_website") if doc_save_response.get("company_website") else "",
            "bank_name": doc_save_response.get("bank_name") if doc_save_response.get("bank_name") else "",
            "account_number": doc_save_response.get("account_number") if doc_save_response.get("account_number") else "",
            "clearing_number": doc_save_response.get("clearing_number") if doc_save_response.get("clearing_number") else "",
            "iban_swift": doc_save_response.get("iban_swift") if doc_save_response.get("iban_swift") else "",
            "invoice_name": doc_save_response.get("invoice_name") if doc_save_response.get("invoice_name") else "",
            "invoice_email": doc_save_response.get("invoice_email") if doc_save_response.get("invoice_email") else "",
            "invoice_mobile": doc_save_response.get("invoice_mobile") if doc_save_response.get("invoice_mobile") else "",
            "speciality": doc_save_response.get("speciality") if doc_save_response.get("speciality") else "",
            "add_social": doc_save_response.get("add_social") if doc_save_response.get("add_social") else ""
        }
        frappe.local.response['data'] = final_doc_save_response
    else:
        frappe.throw("Organization not found")