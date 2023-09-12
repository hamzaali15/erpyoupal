// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('People', {
	refresh: function(frm) {
		if(!frm.doc.__islocal){
			frm.add_custom_button(__("IT Consultant"), function(){
				frappe.call({
					method: "go_to_it_consultant",
					doc: frm.doc,
					async: false,
					callback: function(r) {
						if (r.message){
							frappe.set_route("Form", "IT Consultant", r.message);
						}else{
							frappe.msgprint("IT Consultant not found");
						}
					}
				});
			}, __("View"));
		}

		if(frm.doc.__islocal){
			frm.set_value('country', null);
			frm.set_value('passport_nationality', null);
		}
	},

	onload: function(frm) {
		if(frm.doc.__islocal){
			frm.set_value('country', null);
			frm.set_value('passport_nationality', null);
		}
	},

	create_user: function(frm) {
		if(!frm.doc.__islocal){
			if(frm.doc.create_user==0){
				frappe.confirm('Delete created user?',
					() => {
						frm.set_value('create_user', 0);
						frm.save();
					}, () => {
						frm.set_value('create_user', 1);
				})
			}
		}
	},

	validate: function(frm) {
		if(!frm.doc.__islocal){
			frappe.call({
				method: "validate_if_new_email",
				doc: frm.doc,
				async: false,
				callback: function(r) {
					if(!r.message){
						frappe.confirm('Do you want to merge the new email?',
							() => {
								frappe.call({
									method: "merge_new_email_to_old",
									doc: frm.doc,
									async: false,
									callback: function(r) {
										//pass
										frm.refresh_fields();
									}
								});
							}, () => {
								// action to perform if No is selected
						})
					}
				}
			});
		}
		if(!frm.doc.created_user && frm.doc.create_user){
			frappe.call({
				method: "validate_user_exists",
				doc: frm.doc,
				async: false,
				callback: function(r) {
					if(r.message == "False"){
						frappe.confirm('User already exists, do you want to attach User to this People',
							() => {
								frappe.call({
									method: "create_user_profile",
									doc: frm.doc,
									async: false,
									args: {
										'forced': 1
									},
									callback: function(r) {
										//pass
										frm.refresh_fields();
									}
								});
							}, () => {
								// action to perform if No is selected
						})
					}
				}
			});
		}
	}
});

cur_frm.fields_dict['reports_to'].get_query = function(doc, cdt, cdn) {
		return {
			filters:{
			    'organization_name': doc.organization_name,
			}
		};

};