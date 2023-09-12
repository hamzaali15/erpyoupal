// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('OneFlow Legal', {
	refresh: function(frm) {
		//ADD COUNTERPARTY INDIVIDUAL
		let add_individual_counterparty_dialog = new frappe.ui.Dialog({
		    title: 'Individual Participant',
		    fields: [
		    	{
		            label: 'Country Code',
		            fieldname: 'country_code',
		            fieldtype: 'Data',
		            reqd: 1
		        },
		    	{
		            label: 'Title',
		            fieldname: 'title',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Name',
		            fieldname: 'name',
		            fieldtype: 'Data',
		            reqd: 1
		        },
		        {
		            label: 'Delivery Channel',
		            fieldname: 'delivery_channel',
		            fieldtype: 'Select',
		            options: 'email\nsms\nnone\nunknown',
		            default: 'email',
		            reqd: 1
		        },
		        {
		            label: 'Birth Date',
		            fieldname: 'identification_number',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Email',
		            fieldname: 'email',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Phone Number',
		            fieldname: 'phone_number',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Sign Method',
		            fieldname: 'sign_method',
		            fieldtype: 'Select',
		            options: 'standard_esign\nsms\nswedish_bankid\nnorwegian_bankid\ndanish_nemid\nfinnish_bankid\nunknown',
		            default: 'standard_esign'
		        },
		        {
		            label: 'Signatory',
		            fieldname: 'signatory',
		            fieldtype: 'Select',
		            options: 'True\nFalse',
		            default: 'True'
		        }
		    ],
		    primary_action_label: 'Add',
		    primary_action(values) {
		        frappe.call({
					method: "add_individual_counterparty",
					doc: frm.doc,
					args: {
						'country_code': values.country_code,
						'title': values.title,
						'name': values.name,
						'delivery_channel': values.delivery_channel,
						'identification_number': values.identification_number,
						'email': values.email,
						'phone_number': values.phone_number,
						'sign_method': values.sign_method,
						'signatory': values.signatory,
					},
					async: false,
					callback: function(r) {
						frm.refresh_fields();
					}
				});
		        add_individual_counterparty_dialog.hide();
		    }
		});
		frm.add_custom_button(__('Individual'), function(){
	        add_individual_counterparty_dialog.show();
	    }, __("Add Counterparty Participant"));

		//ADD COUNTERPARTY COMPANY
	    let add_company_counterparty_dialog = new frappe.ui.Dialog({
		    title: 'Company Participant',
		    fields: [
		   		{
		            label: 'Company name',
		            fieldname: 'company_name',
		            fieldtype: 'Data',
		            reqd: 1
		        },
		        {
		            label: 'Registration number',
		            fieldname: 'company_identification_number',
		            fieldtype: 'Data',
		            reqd: 1
		        },
		        {
		            label: 'Country Code',
		            fieldname: 'country_code',
		            fieldtype: 'Data',
		            reqd: 1
		        },
		    	{
		            label: 'Title',
		            fieldname: 'title',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Name',
		            fieldname: 'name',
		            fieldtype: 'Data',
		            reqd: 1
		        },
		        {
		            label: 'Delivery Channel',
		            fieldname: 'delivery_channel',
		            fieldtype: 'Select',
		            options: 'email\nsms\nnone\nunknown',
		            default: 'email',
		            reqd: 1
		        },
		        {
		            label: 'Birth Date',
		            fieldname: 'identification_number',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Email',
		            fieldname: 'email',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Phone Number',
		            fieldname: 'phone_number',
		            fieldtype: 'Data'
		        },
		        {
		            label: 'Delivery Channel',
		            fieldname: 'delivery_channel',
		            fieldtype: 'Select',
		            options: 'email\nsms\nnone\nunknown',
		            default: 'email'
		        },
		        {
		            label: 'Sign Method',
		            fieldname: 'sign_method',
		            fieldtype: 'Select',
		            options: 'standard_esign\nsms\nswedish_bankid\nnorwegian_bankid\ndanish_nemid\nfinnish_bankid\nunknown',
		            default: 'standard_esign'
		        },
		        {
		            label: 'Signatory',
		            fieldname: 'signatory',
		            fieldtype: 'Select',
		            options: 'True\nFalse',
		            default: 'True'
		        }
		    ],
		    primary_action_label: 'Add',
		    primary_action(values) {
		        frappe.call({
					method: "add_company_counterparty",
					doc: frm.doc,
					args: {
						'company_name': values.company_name,
						'company_identification_number': values.company_identification_number,
						'country_code': values.country_code,
						'title': values.title,
						'name': values.name,
						'delivery_channel': values.delivery_channel,
						'identification_number': values.identification_number,
						'email': values.email,
						'phone_number': values.phone_number,
						'sign_method': values.sign_method,
						'signatory': values.signatory,
					},
					async: false,
					callback: function(r) {
						frm.refresh_fields();
					}
				});
		        add_company_counterparty_dialog.hide();
		    }
		});
	    frm.add_custom_button(__('Company'), function(){
	        add_company_counterparty_dialog.show();
	    }, __("Add Counterparty Participant"));

	    //PUBLISH CONTRACT
	    let publish_contract_dialog = new frappe.ui.Dialog({
		    title: 'Enter Details',
		    fields: [
		   		{
		            label: 'Subject',
		            fieldname: 'subject',
		            fieldtype: 'Data',
		            reqd: 1
		        },
		        {
		            label: 'Message',
		            fieldname: 'message',
		            fieldtype: 'Text',
		            reqd: 1
		        }
		    ],
		    primary_action_label: 'Publish',
		    primary_action(values) {
		        frappe.call({
					method: "do_publish_contract",
					doc: frm.doc,
					args: {
						'subject': values.subject,
						'message': values.message
					},
					async: false,
					callback: function(r) {
						frm.refresh_fields();
					}
				});
		        publish_contract_dialog.hide();
		    }
		});
	    frm.add_custom_button(__('Publish Contract'), function(){
	        publish_contract_dialog.show();
	    });

		if(!frm.doc.is__local){
			frm.add_custom_button(__('Generate Contract Links'), function(){
				frappe.call({
					method: "generate_contract_links",
					doc: frm.doc,
					async: false,
					callback: function(r) {
						frm.refresh_fields();
						frappe.msgprint(r.message);
					}
				});
			});
		}
	}
});
