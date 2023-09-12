// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

var table_fields = cur_frm.fields_dict.candidate.grid.meta.fields;
table_fields.forEach(function (arrayItem) {
	var fieldname = arrayItem.fieldname;
	let read_only_fields = ['it_consultant','consultant_sub_total','client_sub_total','gross_margin'];
	if(read_only_fields.includes(fieldname)){
			var df = frappe.meta.get_docfield("Lead Candidates Table", fieldname, cur_frm.doc.name);
			df.read_only = 1;           
	}
});
this.frm.get_field("candidate").grid.only_sortable();
frappe.ui.form.on('Lead Candidate', {
	refresh: function(frm) {
			frm.trigger("toggle_table_candidate");
			if(!frm.doc.__islocal){
					frm.add_custom_button(__("People"), function(){
				frappe.call({
					method: "go_to_people",
					doc: frm.doc,
					async: false,
					callback: function(r) {
						if (r.message){
							frappe.set_route("Form", "People", r.message);
						}else{
							frappe.msgprint("People not found");
						}
					}
				});
			}, __("View"));

			frm.add_custom_button(__("IT Consultant"), function(){
				frappe.call({
					method: "go_to_it_consultant",
					doc: frm.doc,
					async: false,
					callback: function(r) {
						if (r.message){
							frappe.set_route("Form", "IT Consultant", r.message);
						}else{
							frappe.msgprint("IT Consultant not found");
						}
					}
				});
			}, __("View"));
			
					frm.add_custom_button(__("Job Applicant"), function(){
				frappe.call({
					method: "go_to_job_applicant",
					doc: frm.doc,
					async: false,
					callback: function(r) {
						if (r.message){
							frappe.set_route("Form", "Job Applicant", r.message);
						}else{
							frappe.msgprint("Job Applicant not found");
						}
					}
				});
			}, __("View"));
		}
	},

	stages: function(frm) {
			frm.trigger("toggle_table_candidate");
	},

	toggle_table_candidate: function(frm) {
			if(frm.doc.stages!='Matched' && frm.doc.stages!='Applied' ){
					cur_frm.set_df_property("candidate", "read_only", 1);
			}else{
					cur_frm.set_df_property("candidate", "read_only", 0);
			}
	},

	resume_pdf: function(frm) {
			window.open(frm.doc.cv_pdf_link);
	},

	original_resume: function(frm) {
			frappe.call({
					method: "get_original_resume",
					doc: frm.doc,
					async: false,
					callback: function(r) {
							if (r.message){
								window.open(r.message);
							}
							
					}
			});
			
	}
});

frappe.ui.form.on("Lead Candidates Table", "rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "consultant_sub_total", d.rate * d.hours);
	refresh_field("consultant_sub_total");

});

frappe.ui.form.on("Lead Candidates Table", "hours", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "consultant_sub_total", d.rate * d.hours);
	refresh_field("consultant_sub_total");

});


/* Client calculation */
frappe.ui.form.on("Lead Candidates Table", "client_rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "client_sub_total", d.client_rate * d.hours);
	refresh_field("client_sub_total");

});

frappe.ui.form.on("Lead Candidates Table", "hours", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "client_sub_total", d.client_rate * d.hours);
	refresh_field("client_sub_total");

});

/* Daily Rate Calculation*/
frappe.ui.form.on("Lead Candidates Table", "check_dailyrate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "daily_rate", d.define_day * d.rate);
	refresh_field("daily_rate");

});

frappe.ui.form.on("Lead Candidates Table", "define_day", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "daily_rate", d.define_day * d.rate);
	refresh_field("daily_rate");

});

/* Monthly Rate Calculation */
frappe.ui.form.on("Lead Candidates Table", "check_monthlyrate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "monthly_rate", d.define_month * d.rate);
	refresh_field("monthly_rate");

});

frappe.ui.form.on("Lead Candidates Table", "define_month", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "monthly_rate", d.define_month * d.rate);
	refresh_field("monthly_rate");

});

/* Utilization */
frappe.ui.form.on("Lead Candidates Table", "set_utilization", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "monthly_rate", d.define_month * d.rate * (d.set_utilization/100));
	refresh_field("monthly_rate");

});

frappe.ui.form.on("Lead Candidates Table", "set_utilization", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "daily_rate", d.define_day * d.rate * (d.set_utilization/100));
	refresh_field("daily_rate");

});


/* Gross Margin Calculation */

frappe.ui.form.on("Lead Candidates Table", "rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	var gross_margin = d.client_sub_total - d.consultant_sub_total;
	
	frappe.model.set_value(cdt, cdn, "gross_margin",  (gross_margin / d.client_sub_total)*100);
	refresh_field("gross_margin");
	
	if(d.gross_margin < 28) {
		($('input[data-fieldname="gross_margin"]').css("background-color","red").css("color","white")); 
		} else if(d.gross_margin > 28) {
		($('input[data-fieldname="gross_margin"]').css("background-color","#228B22").css("color","white"));
		} else if(d.gross_margin == 28) {
		($('input[data-fieldname="gross_margin"]').css("background-color","#FFFF00").css("color","black"));
	}
	refresh_field("gross_margin");
	
	
});

frappe.ui.form.on("Lead Candidates Table", "client_rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	var gross_margin = d.client_sub_total - d.consultant_sub_total;
	
	frappe.model.set_value(cdt, cdn, "gross_margin",  (gross_margin / d.client_sub_total)*100);
	refresh_field("gross_margin");
	
		if(d.gross_margin < 28) {
		($('input[data-fieldname="gross_margin"]').css("background-color","red").css("color","white")); 
		} else if(d.gross_margin > 28) {
		($('input[data-fieldname="gross_margin"]').css("background-color","#228B22").css("color","white"));
		} else if(d.gross_margin == 28) {
		($('input[data-fieldname="gross_margin"]').css("background-color","#FFFF00").css("color","black"));
	}
	refresh_field("gross_margin");
	
	
});


