// Copyright (c) 2022, Frappe Technologies and contributors
// For license information, please see license.txt

var selection_loaded = 0;
var fielddict_list = {};
if(this.frm.doc.kanban_doctype){
	frappe.call({
		method: "frappe.core.doctype.custom_kanban_card_fields.custom_kanban_card_fields.get_allowed_fields",
		args: {
			doctype: this.frm.doc.kanban_doctype
		},
		async: false,
		callback: function(r) {
			if(r.message){
				frappe.meta.get_docfield('Custom Kanban Card Fields Table', 'fieldname', cur_frm.doc.name).options = r.message[0];
				cur_frm.refresh_field('kanban_card_fields');
				selection_loaded = 1;
				fielddict_list = r.message[1];
			}
		}
	});
}

frappe.ui.form.on('Custom Kanban Card Fields', {	
	refresh: function(frm){
		if(frm.doc.__islocal==1){
			selection_loaded = 0;
			cur_frm.set_value("is_enabled", 1);
			cur_frm.toggle_display("is_enabled", false);
			cur_frm.toggle_display("show_label", false);
			cur_frm.toggle_display("kanban_card_fields", false);
		}else{
			selection_loaded = 1;
			cur_frm.toggle_display("is_enabled", true);
			cur_frm.toggle_display("show_label", true);
			cur_frm.toggle_display("kanban_card_fields", true);
		}
	},

	after_save: function(frm){
		if(selection_loaded==0){
			window.location.reload();
		}
	}
});

frappe.ui.form.on("Custom Kanban Card Fields Table", {
	fieldname: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var fieldname = d.fieldname;
		d.fieldlabel = fielddict_list[fieldname]['fieldlabel'];
		d.fieldtype = fielddict_list[fieldname]['fieldtype'];
		frm.refresh_field("kanban_card_fields");
	}
});