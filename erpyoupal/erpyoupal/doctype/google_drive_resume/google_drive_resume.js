// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Google Drive Resume', {
	refresh: function(frm) {
		if(frm.doc.parse_file){
			frm.set_df_property('parse_file', 'read_only', 1);
		}else{
			frm.set_df_property('parse_file', 'read_only', 0);
		}
	}
});
