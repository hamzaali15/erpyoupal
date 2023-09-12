// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('IT Consultant', {
	refresh: function(frm) {
		frm.set_df_property('job_applicant_history', 'cannot_add_rows', true);
		frm.set_df_property('job_applicant_history', 'cannot_delete_rows', true);
		frm.set_df_property('self_evaluation_history', 'cannot_add_rows', true);
		frm.set_df_property('self_evaluation_history', 'cannot_delete_rows', true);
		frm.set_df_property('skill_test_history', 'cannot_add_rows', true);
		frm.set_df_property('skill_test_history', 'cannot_delete_rows', true);
		frm.set_df_property('skill_test_coderbyte_history', 'cannot_add_rows', true);
		frm.set_df_property('skill_test_coderbyte_history', 'cannot_delete_rows', true);
		frm.set_df_property('persona_test_history', 'cannot_add_rows', true);
		frm.set_df_property('persona_test_history', 'cannot_delete_rows', true);
		frm.set_df_property('background_check_history', 'cannot_add_rows', true);
		frm.set_df_property('background_check_history', 'cannot_delete_rows', true);
		frm.set_df_property('video_interview_history', 'cannot_add_rows', true);
		frm.set_df_property('video_interview_history', 'cannot_delete_rows', true);
		frm.set_df_property('candidate_interview_history', 'cannot_add_rows', true);
		frm.set_df_property('candidate_interview_history', 'cannot_delete_rows', true);
		frm.refresh_fields();

		//Default platform_social_media
		if(frm.doc.__islocal == 1){
			frm.call({
    			method: "default_platform_social_media",
    			doc: frm.doc,
    			callback: function(r) {
    				frm.refresh_fields();
    			}
        	});
		}

		frm.add_custom_button(__("CV"),
		function() {
			window.open("https://erp2.youpal.se/jasperserver/flow.html?_flowId=viewReportFlow&_flowId=viewReportFlow&ParentFolderUri=%2FReports&reportUnit=%2FReports%2Fcv&standAlone=true&j_username=jasperadmin&j_password=jasperadmin&output=pdf&filter1="+frm.doc.name);
		});

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

			frm.add_custom_button(__("Agency/Organization"), function(){
				frappe.call({
					method: "go_to_agency",
					doc: frm.doc,
					async: false,
					callback: function(r) {
						if (r.message){
							frappe.set_route("Form", "Organizations", r.message);
						}else{
							frappe.msgprint("Agency/Organization not found");
						}
					}
				});
			}, __("View"));

			frm.add_custom_button(__("CV"), function(){
				
			}, __("View"));
		}
	},

	new_address: function(frm){
		if(frm.doc.new_address){
    		return frm.call({
    			method: "frappe.contacts.doctype.address.address.get_address_display",
    			args: {
    				"address_dict": frm.doc.new_address
    			},
    			callback: function(r) {
    			if(r.message)
    				frm.set_value("full_address", r.message);
        
    			}
        	});
   		}
	    else{
	        frm.set_value("full_address", "");
	    }
	},

	rate_hourly: function(frm){
		if(frm.doc.rate_hourly >= 10 && frm.doc.rate_hourly <20){
        	frm.set_value("hourly_rate_lead_search", "10-19");
	    }
	    else if(frm.doc.rate_hourly >= 20 && frm.doc.rate_hourly <30){
	        frm.set_value("hourly_rate_lead_search", "20-29");
	    }
	     else if(frm.doc.rate_hourly >= 30 && frm.doc.rate_hourly <40){
	        frm.set_value("hourly_rate_lead_search", "30-39");
	    }
	     else if(frm.doc.rate_hourly >= 40 && frm.doc.rate_hourly <50){
	        frm.set_value("hourly_rate_lead_search", "40-49");
	    }
	     else if(frm.doc.rate_hourly >= 50 && frm.doc.rate_hourly <100){
	        frm.set_value("hourly_rate_lead_search", "50-99");
	    }
	    else if(frm.doc.rate_hourly >= 100){
	        frm.set_value("hourly_rate_lead_search", "100+");
	    }

	    if(frm.doc.rate_hourly < 10) {
	    	($('input[data-fieldname="rate_hourly"]').css("background-color","red").css("color","white")); 
	    } else if(frm.doc.rate_hourly > 10) {
	    	($('input[data-fieldname="rate_hourly"]').css("background-color","#228B22").css("color","white"));
	    } else if(frm.doc.rate_hourly == 10) {
	    	($('input[data-fieldname="rate_hourly"]').css("background-color","#FFFF00").css("color","black"));
	    }
	},

	location: function(frm){
		if(cur_frm.doc.location === "Sweden" || cur_frm.doc.location === "Poland" || cur_frm.doc.location === "Poland" || cur_frm.doc.location === "Iceland" || cur_frm.doc.location === "Liechtenstein" || cur_frm.doc.location === "Norway"|| cur_frm.doc.location === "Austria" || cur_frm.doc.location === "Belgium" || cur_frm.doc.location === "Bulgaria"|| cur_frm.doc.location === "Croatia"|| cur_frm.doc.location === "Republic of Cyprus"|| cur_frm.doc.location === "Czech Republic"|| cur_frm.doc.location === "Denmark"|| cur_frm.doc.location === "Estonia" || cur_frm.doc.location === "Finland"|| cur_frm.doc.location === "France" || cur_frm.doc.location === "Germany" || cur_frm.doc.location === "Greece"|| cur_frm.doc.location === "Hungary"|| cur_frm.doc.location === "Ireland"|| cur_frm.doc.location === "Italy" || cur_frm.doc.location === "Latvia" || cur_frm.doc.location === "Lithuania"|| cur_frm.doc.location === "Luxembourg"|| cur_frm.doc.location === "Malta"|| cur_frm.doc.location === "Netherlands"|| cur_frm.doc.location === "Portugal"|| cur_frm.doc.location === "Romania"|| cur_frm.doc.location === "Slovakia"|| cur_frm.doc.location === "Slovenia"|| cur_frm.doc.location === "Spain"){
			cur_frm.doc.data_protection = "Inside EEA";
			frm.set_df_property('data_protection',  'read_only',  1);
			cur_frm.refresh_field('data_protection');
		}
		else if(cur_frm.doc.location === "Armenia" || cur_frm.doc.location === "Andorra" || cur_frm.doc.location === "Argentina" || cur_frm.doc.location === "Canada" || cur_frm.doc.location === "Faroe Islands" || cur_frm.doc.location === "Guernsey" || cur_frm.doc.location === "Isle of Man" || cur_frm.doc.location === "Japan" || cur_frm.doc.location === "Jersey" || cur_frm.doc.location === "New Zealand" || cur_frm.doc.location === "Republic of Korea" || cur_frm.doc.location === "Switzerland" || cur_frm.doc.location === "United Kingdom" ||  cur_frm.doc.location === "South Korea"){
			cur_frm.doc.data_protection = "Outside EEA | GDPR Safe";
			frm.set_df_property('data_protection',  'read_only',  1);
			cur_frm.refresh_field('data_protection');
		}
		else if(cur_frm.doc.location === null){
			cur_frm.doc.data_protection = "";
			frm.set_df_property('data_protection',  'read_only',  1);
			cur_frm.refresh_field('data_protection');
		}
		else{
			cur_frm.doc.data_protection = "Outside EEA | GDPR Unsafe";
			frm.set_df_property('data_protection',  'read_only',  1);
			cur_frm.refresh_field('data_protection');
		}
	},

	experience_since: function(frm){
		var currentTime = new Date();
		var year = currentTime.getFullYear();

		let total_Exp = year - frm.doc.experience_since;
    	frm.set_value("total_experience", total_Exp);
	}

});

frappe.ui.form.on("Job Applicant History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/job-applicant/"+d.job_applicant)
});

frappe.ui.form.on("Self Evaluation History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/self-evaluation/"+d.self_evaluation_id)
});

frappe.ui.form.on("Skill Test History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/skill-test/"+d.skill_test_id)
});

frappe.ui.form.on("Skill Test Coderbyte History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/skill-test-coderbyte/"+d.skill_test_coderbyte_id)
});

frappe.ui.form.on("Persona Test History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/persona-test/"+d.persona_test_id)
});

frappe.ui.form.on("Background Check History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/background-check/"+d.background_check_id)
});

frappe.ui.form.on("Video Interview History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/video-interview/"+d.video_interview_id)
});

frappe.ui.form.on("Candidate Interview History", "view", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	window.open("https://erp.youpal.se/app/candidate-interview/"+d.candidate_interview_id)
});