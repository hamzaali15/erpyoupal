// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Organizations', {
	refresh: function(frm) {
		let orgID = 0;
		orgID = frm.doc.name.split("-")[1];
		
		frm.set_value("organization_id", orgID);

		if(frm.doc.__islocal){
			cur_frm.toggle_display("organization_id", false);
		}
	}
});
