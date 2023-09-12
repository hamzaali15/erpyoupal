// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('it_consultant', 'full_name', 'applicant_name');
cur_frm.add_fetch('it_consultant', 'email_primary', 'email');
cur_frm.add_fetch('job_applicant', 'applicant_name', 'applicant_name');
cur_frm.add_fetch('job_applicant', 'email_id', 'email');

frappe.ui.form.on('Video Interview', {
	// refresh: function(frm) {

	// }
});
