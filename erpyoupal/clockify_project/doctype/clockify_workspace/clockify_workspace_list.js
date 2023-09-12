frappe.listview_settings['Clockify Workspace'] = {
	onload: function(listview) {
		listview.page.add_menu_item(__("Pull Clockify Workspaces"), function() {
			frappe.call({
				method:'erpnext.clockify_project.clockify_api.pull_workspaces',
				callback: function() {
					frappe.msgprint("Completed");
					listview.refresh();
				}
			});
		});
	}
};
