// Copyright (c) 2025, JF and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sample Request", {
 	refresh(frm) {
       
       // frm.trigger('update_actual_time');
        if (frappe.user.has_role('Marketing Staff','System Manager')) {
             frm.fields_dict['bom'].grid.get_field('is_approved').df.read_only = 0;
         }
         
         
	},
    sample_code(frm){
        
        frappe.db.get_doc('Item', frm.doc.sample_code)
        .then(doc => {
            
            frm.set_value('sample_name', doc.item_name)
        })
   
    },
    // timeline_refresh(frm){
    //     alert(frm.doc.workflow_state)
    // },
    timeline_refresh: function(frm) {
        if (!frm.doc.workflow_state) return;

        let state = frm.doc.workflow_state;
        
        console.log("🔎 Menambahkan State Baru:", state);

    //     // Cek apakah state ini sudah ada di child table
        let exists = frm.doc.sample_request_actual_time.some(row => row.state === state);
        if (exists) {
            console.log("⚠️ State sudah ada, tidak menambahkan lagi:", state);
            return;
        }
        let from_time_set = new Date(frappe.datetime.now_datetime());
        let to_time_set = new Date(frappe.datetime.now_datetime());

        let differenceMs = to_time_set - from_time_set; // Selisih dalam milidetik
        let differenceMinutes = differenceMs / (1000 * 60); // Konversi ke menit

        console.log(`Selisih waktu: ${differenceMinutes} menit`);
        let row = frm.add_child('sample_request_actual_time', {
            time:frappe.datetime.now_datetime(),
            state: state
        });

        frm.refresh_field('sample_request_actual_time');
        console.log("✅ Data Ditambahkan ke Child Table:", row);
        frm.save();  // Simpan perubahan di child table
    }
    // workflow_state(frm){
    //     alert(frm.doc.workflow_state);
    //     if(frm.doc.workflow_state == 'Draft'){
    //         //frappe.utils.now_datetime() - self.creation
    //         let row = frm.add_child('sample_request_actual_time', {
    //             from_time: frappe.datetime.now_datetime(),
    //             to_time: frappe.datetime.now_datetime(),
    //             state: "Draft"
    //         });
            
    //         frm.refresh_field('sample_request_actual_time');
    //     }else if(frm.doc.workflow_state == 'Submitted to Marketing'){
    //         //frappe.utils.now_datetime() - self.creation
    //         let row = frm.add_child('sample_request_actual_time', {
    //             from_time: frappe.datetime.now_datetime(),
    //             to_time: frappe.datetime.now_datetime(),
    //             state: "Submitted to Marketing"
    //         });
            
    //         frm.refresh_field('sample_request_actual_time');
    //     }else if(frm.doc.workflow_state == 'Review Marketing'){
    //         //frappe.utils.now_datetime() - self.creation
    //         let row = frm.add_child('sample_request_actual_time', {
    //             from_time: frappe.datetime.now_datetime(),
    //             to_time: frappe.datetime.now_datetime(),
    //             state: "Review Marketing"
    //         });
            
    //         frm.refresh_field('sample_request_actual_time');
    //     }else if(frm.doc.workflow_state == 'Reviewed Customer'){
    //         //frappe.utils.now_datetime() - self.creation
    //         let row = frm.add_child('sample_request_actual_time', {
    //             from_time: frappe.datetime.now_datetime(),
    //             to_time: frappe.datetime.now_datetime(),
    //             state: "Reviewed Customer"
    //         });
            
    //         frm.refresh_field('sample_request_actual_time');
    //     }
    // }
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
