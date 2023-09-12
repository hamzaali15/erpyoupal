// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch('workspace', 'organization', 'organization');

frappe.ui.form.on('Clockify Projects', {
	refresh: function(frm) {
		cur_frm.set_query("task_id", "tasks", function(doc, cdt, cdn) {
			var d = locals[cdt][cdn];
			return{
				filters: [
					['Clockify Task', 'project_id', '=', frm.doc.project_id]
				]
			}
		});
		if(frm.doc.__islocal){
			cur_frm.page.add_action_item(__("Disable/Enable SS"), function() {
				$.each(frm.doc.erp_members,  function(i,  d) {
					if(d.disable_ss == 0) {
						d.disable_ss = 1;
					}
					else if (d.disable_ss == 1) {
						d.disable_ss = 0;
					}
				});
				cur_frm.refresh_fields();
			});
			cur_frm.page.add_action_item(__("Disable/Enable Link"), function() {
				$.each(frm.doc.erp_members,  function(i,  d) {
					if(d.disable_link == 0) {
						d.disable_link = 1;
					}
					else if (d.disable_link == 1) {
						d.disable_link = 0;
					}
				});
				cur_frm.refresh_fields();
			});
		}
	}
});