// Client Script for DocType: Salary Structure Assignment
// Name: SSA - Increment Letter Action
// Enabled: 1


frappe.ui.form.on('Salary Structure Assignment', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('📄 Download Increment / Appraisal Letter'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Salary%20Structure%20Assignment&name=' + encodeURIComponent(frm.doc.name) + '&format=Corporate%20Salary%20Increment%20Letter&no_letterhead=0';
                window.open(url, '_blank');
            }).addClass('btn-primary');
        }
    }
});
