// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Shop Rent Payment", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Shop Rent Payment", {
    contract(frm) {
        // Ensure validations re-run correctly
        frm.refresh_field("payment_date");
    }
});
