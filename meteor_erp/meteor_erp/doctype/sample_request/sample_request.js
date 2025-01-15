// Copyright (c) 2025, JF and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Request", {
 	refresh(frm) {
        //frm.set_df_property('Marketi', 'read_only', 1);
        // Jika pengguna memiliki role 'R&D Staff', aktifkan field
        if (frappe.user.has_role('R&D Staff')) {
            //frm.set_df_property('bom', 'read_only', 0);
            frm.fields_dict['bom'].grid.get_field('is_approved').df.read_only = 0;
        } else {
            // Selain itu, jadikan field read-only
            frm.set_df_property('bom', 'read_only', 1);
            frm.fields_dict['bom'].grid.get_field('is_approved').df.read_only = 1;
        }
        if (frappe.user.has_role('Marketing Staff')) {
             frm.fields_dict['bom'].grid.get_field('is_approved').df.read_only = 0;
         }
	},
});
