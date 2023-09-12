// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Skill Test', {
	refresh: function(frm) {
		frm.add_custom_button(__("Fetch Latest Data"), function(){
			frappe.call({
				method: "load_testgorilla_data",
				doc: frm.doc,
				callback: function(r) {
					frm.refresh_fields();
					frappe.msgprint("Fetched, refresh page");
				}
			});
		});	

		frm.add_custom_button(__("Retake Asessment"), function(){
			frappe.confirm('Are you sure you want to retake?',
				() => {
					frappe.call({
						method: "erpnext.hr.doctype.skill_test.skill_test.retake_assessment",
						args: {
							'skill_test_id': frm.doc.name
						},
						callback: function(r) {
							frm.refresh_fields();
							frappe.msgprint("Result: "+r.message);
						}
					});
				}, () => {
				// action to perform if No is selected
			})
			
		});		
	}
});
