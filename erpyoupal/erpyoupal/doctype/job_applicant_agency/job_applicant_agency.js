// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Applicant Agency', {
	refresh: function(frm) {
		if(frm.doc.to_parse_cvs){
			frm.set_df_property('to_parse_cvs', 'read_only', 1);
		}else{
			frm.set_df_property('to_parse_cvs', 'read_only', 0);
		}

		if(frm.doc.create_it_consultants){
			frm.set_df_property('create_it_consultants', 'read_only', 1);
		}else{
			frm.set_df_property('create_it_consultants', 'read_only', 0);
		}

		if (frm.doc.__islocal){
			frm.set_value('create_it_consultants', 1);
			frm.set_value('to_parse_cvs', 1);
			frm.set_df_property('create_it_consultants', 'read_only', 1);
			frm.set_df_property('to_parse_cvs', 'read_only', 1);
		}
	}
});
