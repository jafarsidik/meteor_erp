// Copyright (c) 2024, JF and contributors
// For license information, please see license.txt
frappe.ui.form.on("Project Request", {
    refresh: function(frm) {
       // frappe.breadcrumbs.clear()
        //$("#navbar-breadcrumbs").css({'visibility':'hidden'});
        if (!frm.doc.created_by) {
            frm.set_value('created_by', frappe.session.user);
        }
        // Menjadikan field Created By read-only setelah diisi
        frm.set_df_property('created_by', 'read_only', 1);
        if (!frm.is_new()) {
            

            frm.toggle_display(['sample_section'],true);
            frm.set_value('sample__request','');
            frappe.db.get_list('Sample Request',{
                filters :{project_request: frm.doc.name},
                fields: ['name','sample_name','sample_group','excepted_start_date','excepted_end_date','qty','workflow_state']
            }).then(record => {
            
                record.forEach(values => {
                    
                    let row = frm.add_child('sample__request', {
                        sample_name: values.name,
                        sample_group: values.sample_group,
                        excepted_start_date: values.excepted_start_date,
                        excepted_end_date: values.excepted_end_date,
                        status: values.workflow_state,
                        qty: values.qty,
                    });
                });
          
               frm.refresh_field('sample__request');
            })
           
            
        }
    },
    create_sample(frm){
        
        frappe.new_doc("Sample Request", {subject: "Sample R"},
            doc => {
           //     frm.set_value('project_request', frm.doc.name);
            //    frm.set_value('qty', '100');
                doc.project_request = frm.doc.name;
                //doc.qty = "100";
            }
        );
    }
    //onload: function () {
    //    $('.breadcrumb-wrapper').hide();
   // }
});