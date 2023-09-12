// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lead Custom', {
	refresh: function(frm) {
		frm.add_custom_button(__("Candidates Kanban View"), function(){
			frappe.call({
				method: "set_kanban_filter",
				doc: frm.doc,
				async: false,
				callback: function(r) {
					frappe.set_route("List", "Lead Candidate", "Kanban", "Lead Candidate");
				}
			});
		});

		frm.fields_dict["talent_calculator"].grid.add_custom_button(__('Search IT Consultant'), function() {
			new frappe.ui.form.MultiSelectDialog({
				doctype: "IT Consultant",
				target: this.cur_frm,
				setters: {
					status: 'Active',
					verification: null,
					data_protection: null,
					hourly_rate_lead_search: null,
					location: null,
					skills: null
				},
				add_filters_group: 1,
				get_query() {
					return {
						filters: { docstatus: ['!=', 2] }
					}
				},
				action(selections) {
					for(let i=0; i<selections.length; i++){
						frappe.model.get_value('IT Consultant', {'name': selections[i]}, 'rate_hourly',
							function(d) {
								let row = frm.add_child('talent_calculator', {
									it_consultant: selections[i],
									rate: d.rate_hourly
								});
								frm.refresh_field('talent_calculator');
							})
					}
					frappe.msgprint({title: __('Success'),indicator: 'green',message: __('Selected Consultants are Added to Calculator!')});
				}
			});
		});
		frm.fields_dict["talent_calculator"].grid.grid_buttons.find('.btn-custom').removeClass('btn-default').addClass('btn-primary');

		frm.trigger('get_expires_in');

		frappe.call({
			method: "load_candidate_stages",
			doc: frm.doc,
			async: false,
			callback: function(r) {
				frm.set_value('candidate_stages', r.message);
				frm.refresh_fields();
			}
		});

		if(!frm.doc.__islocal){
			/* Create Job Opening */
			let create_job_opening_dialog = new frappe.ui.Dialog({
				title: 'Create New Job Opening',
				fields: [
					{
						label: 'Designation',
						fieldname: 'designation',
						fieldtype: 'Link',
						options: 'Designation',
						reqd: 1
					},
					{	
						label: 'Publish to Job Board',
						fieldname: 'publish_to_job_board',
						fieldtype: 'Check'
					},
					{	
						label: 'Publish to Partner Portal',
						fieldname: 'publish_to_partner_portal',
						fieldtype: 'Check'
					},
					{	
						label: 'Publish to Talent App',
						fieldname: 'publish_to_talent_app',
						fieldtype: 'Check'
					},
					{	
						label: 'Talent Title',
						fieldname: 'talent_title',
						fieldtype: 'Data',
						default: frm.doc.talent_title
					},
					{	
						label: 'Talent Description',
						fieldname: 'talent_description',
						fieldtype: 'Text Editor',
						default: frm.doc.talent_description
					},
					{	
						label: 'Talent Required Skills',
						fieldname: 'talent_required_skills',
						fieldtype: 'Small Text'
					},
					{
						label: 'From Lead Custom',
						fieldname: 'from_lead_custom',
						fieldtype: 'Link',
						default: frm.doc.name,
						options: 'Lead Custom',
						read_only: 1,
						hidden: 1
					}
				],
				primary_action_label: 'Submit',
				primary_action(values) {					
					frappe.db.insert({
						doctype: 'Job Opening', 
						from_lead_custom: frm.doc.name,
						job_title: values.talent_title,
						description: frm.doc.talent_description,
						company: "Youpal Group",
						designation: values.designation,
						publish_to_job_board: values.publish_to_job_board,
						publish_to_partner_portal: values.publish_to_partner_portal,
						publish_to_talent_app: values.publish_to_talent_app,
						description: values.talent_description,
						requirements: values.talent_required_skills,
						deadline: frm.doc.talent_request_due_date,
						regions: frm.doc.talent_regions,
						location: frm.doc.talent_location,
						ignore_permissions: 1
					});
					create_job_opening_dialog.hide();
					frappe.msgprint("New Job Opening created");
				}
			});
			cur_frm.page.add_action_item(__("Create Job Opening"), function() {
				create_job_opening_dialog.show();
			});
	
			/* Create Project */
			cur_frm.page.add_action_item(__("Create Project"), function() {
				var doc = frappe.model.get_new_doc('Project');
				doc.project_name = frm.doc.name
				doc.lead = frm.doc.name
				frappe.set_route('Form', 'Project', doc.name);
			});
		}
	},

	talent_request_due_date: function(frm) {
		frm.trigger('get_expires_in');
	},

	contract: function(frm) {
		var name = cur_frm.doc.name+" - Time & Material Agreement"
    
		if(cur_frm.doc.contract === name){
			cur_frm.doc.contract_status = "Completed";
			cur_frm.doc.request_contract = "None";
			frm.set_df_property('request_contract',  'read_only',  1);
			cur_frm.refresh_field('contract_status');
		}
	},

	project_request_due_date: function(frm) {
		frm.trigger('get_expires_in');
	},

	get_expires_in: function(frm) {
		frappe.call({
			method: "get_expires_in",
			doc: frm.doc,
			callback: function(r) {
				frm.refresh_fields();
			}
		});
	},

	organization: function(frm) {
		frappe.call({
			method: "get_organization_data",
			doc: frm.doc,
			callback: function(r) {
				frm.refresh_fields();
			}
		});
	},

	add_lead_candidates: function(frm) {
		var checked_rows = [];
		var talent_calculator_rows = cur_frm.doc.talent_calculator;
		talent_calculator_rows.forEach(function (arrayItem) {
			var is_checked = arrayItem.__checked;
			if(is_checked==1){
				checked_rows.push(arrayItem);
			}
		});
		if(checked_rows.length){
			//console.log(checked_rows);
			frappe.call({
				method: "add_lead_candidates",
				doc: frm.doc,
				args: {"lead_entries": checked_rows},
				async: false,
				callback: function(r) {
					if(!r.message){
						frappe.msgprint("Row(s) selected already exists in Lead Candidates");
					}
					frm.refresh_fields();
				}
			});
		}else{
			frappe.msgprint("No row(s) selected");
		}
	}
});

cur_frm.fields_dict['contract'].get_query = function(doc, cdt, cdn) {
		return {
			filters:{
			    'party_name': doc.name,
			}
		};

};



frappe.ui.form.on("Lead Calculator", "rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "consultant_sub_total", d.rate * d.hours);
	refresh_field("consultant_sub_total");

});

frappe.ui.form.on("Lead Calculator", "hours", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "consultant_sub_total", d.rate * d.hours);
	refresh_field("consultant_sub_total");

});


/* Client calculation */
frappe.ui.form.on("Lead Calculator", "client_rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "client_sub_total", d.client_rate * d.hours);
	refresh_field("client_sub_total");

});

frappe.ui.form.on("Lead Calculator", "hours", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "client_sub_total", d.client_rate * d.hours);
	refresh_field("client_sub_total");

});

/* Daily Rate Calculation*/
frappe.ui.form.on("Lead Calculator", "check_dailyrate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "daily_rate", d.define_day * d.rate);
	refresh_field("daily_rate");

});

frappe.ui.form.on("Lead Calculator", "define_day", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "daily_rate", d.define_day * d.rate);
	refresh_field("daily_rate");

});

/* Monthly Rate Calculation */
frappe.ui.form.on("Lead Calculator", "check_monthlyrate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "monthly_rate", d.define_month * d.rate);
	refresh_field("monthly_rate");

});

frappe.ui.form.on("Lead Calculator", "define_month", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "monthly_rate", d.define_month * d.rate);
	refresh_field("monthly_rate");

});

/* Utilization */
frappe.ui.form.on("Lead Calculator", "set_utilization", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "monthly_rate", d.define_month * d.rate * (d.set_utilization/100));
	refresh_field("monthly_rate");

});

frappe.ui.form.on("Lead Calculator", "set_utilization", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "daily_rate", d.define_day * d.rate * (d.set_utilization/100));
	refresh_field("daily_rate");

});


/* Gross Margin Calculation */

frappe.ui.form.on("Lead Calculator", "rate", function(frm, cdt, cdn) {
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

frappe.ui.form.on("Lead Calculator", "client_rate", function(frm, cdt, cdn) {
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

/* Grand Total Calculation */

/* Gross Margin */
frappe.ui.form.on("Lead Calculator", "gross_margin", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total = 0;
var count = 0;
var gt = 0;

frm.doc.talent_calculator.forEach(function(d) 
{ 
    total += d.gross_margin;
    count++;
});

gt = parseFloat((total / count).toFixed(2));


frm.set_value("grand_total", gt);
frm.refresh_field("grand_total");

});

/* Total Hours */
frappe.ui.form.on("Lead Calculator", "hours", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total1 = 0;
frm.doc.talent_calculator.forEach(function(d) { total1 += d.hours; });

frm.set_value("total_hours", total1);
frm.refresh_field("total_hours");

});

/* Consultant Total */
frappe.ui.form.on("Lead Calculator", "consultant_sub_total", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total2 = 0;
frm.doc.talent_calculator.forEach(function(d) { total2 += d.consultant_sub_total; });

frm.set_value("consultant_total", total2);
frm.refresh_field("consultant_total");

});


/* Client Total */
frappe.ui.form.on("Lead Calculator", "client_sub_total", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total3 = 0;
frm.doc.talent_calculator.forEach(function(d) { total3 += d.client_sub_total; });

frm.set_value("client_total", total3);
frm.refresh_field("client_total");

});





/* Project Table Calculation */

/* Total Cost Calculation */

frappe.ui.form.on("Lead Project Calculator", "cost", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "total_cost", d.cost * d.hours);
	refresh_field("total_cost");

});

frappe.ui.form.on("Lead Project Calculator", "hours", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "total_cost", d.cost * d.hours);
	refresh_field("total_cost");

});


/* Client calculation */
frappe.ui.form.on("Lead Project Calculator", "client_rate", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "client_total", d.client_rate * d.hours);
	refresh_field("client_total");

});

frappe.ui.form.on("Lead Project Calculator", "hours", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "client_total", d.client_rate * d.hours);
	refresh_field("client_total");

});

/* Gross Margin Calculation */

frappe.ui.form.on("Lead Project Calculator", "total_cost", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	var gross_margin = d.client_total - d.total_cost;
	
	frappe.model.set_value(cdt, cdn, "gross_margin",  (gross_margin / d.client_total)*100);
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

frappe.ui.form.on("Lead Project Calculator", "client_total", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	var gross_margin = d.client_total - d.total_cost;
	
	frappe.model.set_value(cdt, cdn, "gross_margin",  (gross_margin / d.client_total)*100);
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


/* Grand Total Calculation */

/* Gross Margin */
frappe.ui.form.on("Lead Project Calculator", "gross_margin", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total_gross_project = 0;
var count_project = 0;
var gt_project = 0;

frm.doc.project_calculator.forEach(function(d) 
{ 
    total_gross_project += d.gross_margin;
    count_project++;
});

gt_project = total_gross_project / count_project;

frm.set_value("project_total_gross_margin", gt_project);
frm.refresh_field("project_total_gross_margin");

});

/* Project Total Hours */
frappe.ui.form.on("Lead Project Calculator", "hours", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total1 = 0;
frm.doc.project_calculator.forEach(function(d) { total1 += d.hours; });

frm.set_value("project_total_hours", total1);
frm.refresh_field("project_total_hours");

});

/* Cost Total */
frappe.ui.form.on("Lead Project Calculator", "total_cost", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total2 = 0;
frm.doc.project_calculator.forEach(function(d) { total2 += d.total_cost; });

frm.set_value("project_total_cost", total2);
frm.refresh_field("project_total_cost");

});


/* Project Client Total */
frappe.ui.form.on("Lead Project Calculator", "client_total", function(frm, cdt, cdn){
var d = locals[cdt][cdn];
var total3 = 0;
frm.doc.project_calculator.forEach(function(d) { total3 += d.client_total; });

frm.set_value("project_total_client_rate", total3);
frm.refresh_field("project_total_client_rate");

});
