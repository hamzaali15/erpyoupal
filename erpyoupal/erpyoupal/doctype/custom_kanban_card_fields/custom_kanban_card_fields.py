# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document

class CustomKanbanCardFields(Document):
	pass

@frappe.whitelist()
def get_allowed_fields(doctype):
	fields_dict = {}
	fieldname_list = [""]

	if not doctype:
		return fieldname_list

	allowed_fields = [
		"Check",
		"Currency",
		"Data",
		"Date",
		"Datetime",
		"Float",
		"Int",
		"Link",
		"Long Text",
		"Percent",
		"Read Only",
		"Rating",
		"Select",
		"Small Text",
		"Text",
		"Time"
	]

	custom_fields = frappe.get_all('Custom Field', filters={'dt': doctype}, fields=['*'])
	if custom_fields:
		for custom_field in custom_fields:
			if custom_field.fieldtype in allowed_fields:
				fieldname_list.append(custom_field.fieldname)
				fields_dict[custom_field.fieldname] = {
					"fieldname": custom_field.fieldname,
					"fieldlabel": custom_field.label,
					"fieldtype": custom_field.fieldtype
				}
	
	docfields = frappe.db.sql("""SELECT `label`, `fieldname`, `fieldtype` FROM `tabDocField` WHERE `parent` = %s """,(doctype), as_dict=True)
	for df in docfields:
		if df.fieldtype in allowed_fields:
			fieldname_list.append(df.fieldname)
			fields_dict[df.fieldname] = {
				"fieldname": df.fieldname,
				"fieldlabel": df.label,
				"fieldtype": df.fieldtype
			}

	return fieldname_list, fields_dict

@frappe.whitelist()
def get_kanban_card_fields(doctype, docname):
	result = []
	show_label = 0
	fields_included = []
	field_label = {}
	kanban_card_setup = frappe.get_all('Custom Kanban Card Fields', filters={'name': doctype, 'is_enabled': 1})
	if kanban_card_setup:
		kanban_card_setup = frappe.get_doc('Custom Kanban Card Fields', doctype)

		if kanban_card_setup.show_label:
			show_label = 1

		if kanban_card_setup.kanban_card_fields:
			for kcd in kanban_card_setup.kanban_card_fields:
				fields_included.append(kcd.fieldname)
				field_label[kcd.fieldname] = kcd.fieldlabel

		lead_doc = frappe.get_all(doctype, filters={'name': docname}, fields=['*'])
		if lead_doc:
			lead_doc = lead_doc[0]
			for fieldname in lead_doc:
				if fieldname in fields_included:
					if lead_doc[fieldname]:
						if show_label:
							result.append(str(field_label[fieldname])+": "+str(lead_doc[fieldname]))
						else:
							result.append(str(lead_doc[fieldname]))

	return result

@frappe.whitelist()
def get_all_kanban_card_fields(doctype):
	result = {}
	show_label = 0
	fields_included = []
	field_label = {}
	field_fontsize = {}
	field_fontbold = {}
	kanban_card_setup = frappe.get_all('Custom Kanban Card Fields', filters={'name': doctype, 'is_enabled': 1})
	if kanban_card_setup:
		kanban_card_setup = frappe.get_doc('Custom Kanban Card Fields', doctype)
		if kanban_card_setup.show_label:
			show_label = 1

		if kanban_card_setup.kanban_card_fields:
			for kcd in kanban_card_setup.kanban_card_fields:
				fields_included.append(kcd.fieldname)
				field_label[kcd.fieldname] = kcd.fieldlabel
				field_fontsize[kcd.fieldname] = kcd.font_size_px if kcd.font_size_px else 12
				field_fontbold[kcd.fieldname] = "bold" if kcd.bold_font else "normal"

		doc_referencing_list = frappe.get_all(doctype, fields=['*'])
		if doc_referencing_list:
			for doc_referencing in doc_referencing_list:
				if doc_referencing.name not in result:
					result[doc_referencing.name] = []

				for fieldname in doc_referencing:
					if fieldname in fields_included:
						if doc_referencing[fieldname]:
							style = "font-size: "+str(field_fontsize[fieldname])+"px; font-weight: "+str(field_fontbold[fieldname])+";"
							value = str(doc_referencing[fieldname])
							if show_label:
								value = str(field_label[fieldname])+": "+str(doc_referencing[fieldname])
							result[doc_referencing.name].append({
								"value": value,
								"style": style
								})
	return result