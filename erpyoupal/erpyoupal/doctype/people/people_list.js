frappe.listview_settings['People'] = {
    button: {
        show: function(doc) {
            if (doc.people_type=="Consultant"||doc.people_type=="Business / Consultant"){
                return true;
            }
        },
        get_label: function() {
            return __('View Consultant');
        },
        get_description: function(doc) {
            return __('View Consultant {0}', [doc.name])
        },
        action: function(doc) {
            var objWindowOpenResult = window.open(frappe.urllib.get_full_url("/app/it-consultant/"+encodeURIComponent(doc.name)));
            if(!objWindowOpenResult) {
              msgprint(__("Please set permission for pop-up windows in your browser!")); return;
            }
        }
    }
}