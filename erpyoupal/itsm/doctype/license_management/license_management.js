// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('License Management', {
	onload: function(frm) {
		frm.get_field("license_seats").grid.cannot_add_rows = true;
	},
	refresh: function(frm) {
		frm.get_field("license_seats").grid.df.cannot_delete_rows = true;
	},
	seats: function(frm) {
		frm.doc.license_seats = []
		for (let i = 1; i < frm.doc.seats+1; i++){
			var childTable = cur_frm.add_child("license_seats");
			childTable.seat_no= i;
		}
		cur_frm.refresh_fields("license_seats");
	}
});