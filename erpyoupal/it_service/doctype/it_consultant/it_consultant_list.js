frappe.listview_settings['IT Consultant'] = {
    onload: function(doc) {
        $('[data-fieldname="skills"]').css({"min-width": "500px", "margin-left": "5px", "font-size": "13px"});
    },
    button: {
        show: function(doc) {
            return true;
        },
        get_label: function() {
            return __('PDF');
        },
        get_description: function(doc) {
            return __('Print {0}', [doc.name])
        },
        action: function(doc) {
            frappe.model.get_value('IT Consultant', {'name': doc.name}, 'resume',
            function(d) {
                window.open(frappe.urllib.get_full_url("/"+encodeURIComponent(d.resume)));
                window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                + "doctype=" + encodeURIComponent("IT Consultant")
                + "&name=" + encodeURIComponent(doc.name)
                + "&trigger_print=0"
                + "&format=Resume"
                + "&no_letterhead=0"
                + "&_lang=en"
                ));
            })
        }
    }
}