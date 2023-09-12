// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Clockify Workspace', {

	refresh: function(frm) {
		if(!frm.doc.is__islocal && frm.doc.default_owner && frm.doc.clockify_workspace_id){
			frm.add_custom_button(__("Users"), function() {
				frappe.call({
					method: "erpnext.clockify_project.clockify_api.pull_workspace_users",
					args: {
						workspace_id: frm.doc.clockify_workspace_id
					},
					callback: function(r) {
						frappe.msgprint('Completed');
					}
				});
			}, __("Pull Clockify Data"));

			frm.add_custom_button(__("Projects"), function() {
				frappe.call({
					method: "erpnext.clockify_project.clockify_api.pull_projects",
					args: {
						email: frm.doc.default_owner,
						workspace_id: frm.doc.clockify_workspace_id
					},
					callback: function(r) {
						frappe.msgprint('Completed');
					}
				});
			}, __("Pull Clockify Data"));

			frm.add_custom_button(__("Timelogs"), function() {
				frappe.call({
					method: "erpnext.clockify_project.clockify_api.pull_workspace_timelogs",
					args: {
						workspace_id: frm.doc.clockify_workspace_id
					},
					callback: function(r) {
						frappe.msgprint('Completed');
					}
				});
			}, __("Pull Clockify Data"));
		}
	}

});
