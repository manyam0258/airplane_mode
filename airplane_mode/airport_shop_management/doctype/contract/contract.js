// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract", {
    refresh(frm) {
        // Make status read-only after submit
        if (frm.doc.docstatus === 1) {
            frm.set_df_property("status", "read_only", 1);
        }
    },

    shop(frm) {
        // Recalculate rent when shop changes
        frm.trigger("calculate_rent_amount");
    },

    calculate_rent_amount(frm) {
        // Do not override if user has manually entered rent
        if (frm.doc.rent_amount) {
            return;
        }

        if (!frm.doc.shop) {
            return;
        }

        // Fetch Shop area
        frappe.db.get_value("Shop", frm.doc.shop, "area")
            .then(r => {
                const area = r.message.area;

                if (!area) {
                    return;
                }

                // Fetch default rate per sqft from settings
                frappe.db.get_single_value(
                    "Shop Settings",
                    "default_rent_amount"
                ).then(rate => {

                    if (!rate) {
                        return;
                    }

                    const calculated_amount = area * rate;
                    frm.set_value("rent_amount", calculated_amount);
                });
            });
    }
});
