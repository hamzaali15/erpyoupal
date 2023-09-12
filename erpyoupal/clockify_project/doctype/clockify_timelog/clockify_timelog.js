// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Clockify Timelog', {
	refresh: function(frm) {
//		if (frm.doc.time_in){
//			var time_out_datepicker = frm.fields_dict.time_out.datepicker;
//			var max_date = frappe.datetime.str_to_obj(frm.doc.time_in)
//			max_date.setDate(max_date + 1);
//			time_out_datepicker.update({
//				minDate: frappe.datetime.str_to_obj(frm.doc.time_in),
//				maxDate: frappe.datetime.str_to_obj(max_date)
//			});
//		}
//
//		if (frm.doc.time_out){
//			var time_in_datepicker = frm.fields_dict.time_in.datepicker;
//			var max_date = new Date();
//			max_date.setDate(frappe.datetime.str_to_obj(frm.doc.time_out).getDate() + 1);
//			time_in_datepicker.update({
//				minDate: frappe.datetime.str_to_obj(frm.doc.time_out),
//				maxDate: frappe.datetime.str_to_obj(max_date)
//			});
//		}
	}
});
