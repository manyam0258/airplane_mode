// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Airplane Ticket", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Airplane Ticket", {
    refresh(frm) {
        if (!frm.doc.flight) return;

        frm.add_custom_button(__('Assign Seat'), () => {
            const dialog = new frappe.ui.Dialog({
                title: __('Assign Seat'),
                fields: [
                    {
                        fieldname: 'seat',
                        fieldtype: 'Data',
                        label: __('Seat (e.g. 12A)'),
                        reqd: 1
                    }
                ],
                primary_action_label: __('Assign'),
                primary_action(values) {
                    frm.set_value('seat', values.seat);
                    dialog.hide();
                }
            });
            dialog.show();
        }, __('Actions'));
    },

    // UX-only duplicate prevention
    validate(frm) {
        const seen = new Set();
        (frm.doc.add_ons || []).forEach(row => {
            if (seen.has(row.item)) {
                frappe.validated = false;
                frappe.msgprint({
                    title: __('Error'),
                    message: __('Duplicate add-on: {0}', [row.item]),
                    indicator: 'red'
                });
            }
            seen.add(row.item);
        });
    },

    update_total_amount(frm) {
        let total = 0;
        (frm.doc.add_ons || []).forEach(r => {
            total += flt(r.amount);
        });
        frm.set_value('total_amount', flt(frm.doc.flight_price) + total);
    },

    flight_price(frm) {
        frm.trigger('update_total_amount');
    }
});

frappe.ui.form.on("Airplane Ticket Add-on Item", {
    add_ons_add(frm) {
        frm.trigger('update_total_amount');
    },
    add_ons_remove(frm) {
        frm.trigger('update_total_amount');
    },
    amount(frm) {
        frm.trigger('update_total_amount');
    }
});
