// Copyright (c) 2024, JF and contributors
// For license information, please see license.txt
frappe.ui.form.on("Project Request", {
    onload(frm){
        if (!frm.is_new()) {
            frm.toggle_display(['sample_section'],true);
            frm.trigger("list_data_sample_asy");

        }else{
            frm.set_value('list_data_sample', '');
            frm.set_df_property("list_data_sample", "options", ' ');
        }
    },
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
            frm.trigger("list_data_sample_asy");
            // frm.set_value('sample__request','');
            // frappe.db.get_list('Sample Request',{
            //     filters :{project_request: frm.doc.name},
            //     fields: ['name','sample_name','sample_group','excepted_start_date','excepted_end_date','qty','workflow_state']
            // }).then(record => {
            
            //     record.forEach(values => {
                    
            //         let row = frm.add_child('sample__request', {
            //             sample_name: values.name,
            //             sample_group: values.sample_group,
            //             excepted_start_date: values.excepted_start_date,
            //             excepted_end_date: values.excepted_end_date,
            //             status: values.workflow_state,
            //             qty: values.qty,
            //         });
            //     });
          
            //    frm.refresh_field('sample__request');
            // })
           
            
        }else{
            frm.set_value('list_data_sample', '');
            frm.set_df_property("list_data_sample", "options", ' ');
        }
    },
    
    async list_data_sample_asy(frm){
        
        // Fetch the data from backend (check above for sample response)
        let html = ''
        html+= `<table class='table table-bordered'>
        <thead>
            <tr>
                <th>Sample Code</th>
                <th>Sample Name</th>
                <th>Sample Group</th>
                <th>Excepted Start Date</th>
                <th>Excepted End Date</th>
                <th>Qty</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>`
        frappe.db.get_list('Sample Request',{
                filters :{project_request: frm.doc.name},
                fields: ['name','sample_code','sample_name','sample_group','excepted_start_date','excepted_end_date','qty','workflow_state']
        }).then(record => {
            //console.log(record);
            record.forEach(values => {
                
                html += `<tr>
                <td>${values.sample_code}</td>
                <td>${values.sample_name}</td>
                <td>${values.sample_group}</td>
                <td>${values.excepted_start_date}</td>
                <td>${values.excepted_end_date}</td>
                <td>${values.qty}</td>
                <td>${values.workflow_state}</td>
            </tr>`
            }); 
            html += `</tbody></table>`
            //console.log(html)   
            frm.set_df_property("list_data_sample", "options", html);
        })
        
        // Set the above `html` as Summary HTML
        
       // $(frm.fields_dict["list_data_sample"].wrapper).html(html);
        
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