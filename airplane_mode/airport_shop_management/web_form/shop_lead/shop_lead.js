frappe.web_form.after_load = function () {
	if (frappe.route_options && frappe.route_options.shop) {
		frappe.web_form.set_value("shop", frappe.route_options.shop);
	}
};
