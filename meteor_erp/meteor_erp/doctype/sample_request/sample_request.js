// Copyright (c) 2025, JF and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Request", {
 	refresh(frm) {
        //frm.set_df_property('Marketi', 'read_only', 1);
        // Jika pengguna memiliki role 'R&D Staff', aktifkan field
        // if (frappe.user.has_role('R&D Staff')) {
        //     alert("Test");
        //    // frm.set_df_property('bom', 'read_only', 0);
        //     frm.fields_dict['bom'].grid.get_field('is_approved').df.read_only = 1;
        //     frm.fields_dict['bom'].grid.refresh(); 
        // } 
        // else {
        //     // Selain itu, jadikan field read-only
        //     frm.set_df_property('bom', 'read_only', 1);
        //     frm.fields_dict['bom'].grid.get_field('is_approved').df.read_only = 1;
        // }
        if (frappe.user.has_role('Marketing Staff')) {
             frm.fields_dict['bom'].grid.get_field('is_approved').df.read_only = 0;
         }
	},
});
frappe.ui.form.on('BOM', {
    is_approved: function(frm, cdt, cdn) {
        if (frappe.user.has_role('R&D Staff')) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, 'is_approved', 1); // Set read-only via model
        }
       
    },
    onload: function(frm, cdt, cdn) {
        if (frappe.user.has_role('R&D Staff')) {
           // alert("llll")
            frm.fields_dict['bom_list_table'].grid.fields_map['is_approved'].read_only = 1;
        }
        if (frappe.user.has_role('Marketing Staff')) {
            //alert("fff")
            frm.fields_dict['bom_list_table'].grid.get_field('is_approved').df.read_only = 1;
        }
    }
});
