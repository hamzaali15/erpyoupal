// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manual Job Fetching', {
	refresh: function(frm) {
		frm.add_custom_button(__("Pull Sources"), function() {
			frappe.call({
				method: "erpnext.hr.doctype.scraped_jobs_source.scraped_jobs_source.update_sources",
				callback: function(r) {
					frappe.msgprint('Completed');
				}
			});
		}, __("Update"));

		frm.add_custom_button(__("Pull Job Opening"), function() {
			frappe.call({
				method: "erpnext.hr.doctype.manual_job_fetching.manual_job_fetching.fetch_assignments_now",
				callback: function(r) {
					frappe.msgprint('Completed');
				}
			});
		}, __("Update"));
	}
});