// Client Script for DocType: Salary Slip
// Name: Salary Slip-Form
// Enabled: 1


frappe.ui.form.on('Salary Slip', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('📄 Download Payslip (PDF)'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Salary%20Slip&name=' + encodeURIComponent(frm.doc.name) + '&format=Salary%20Slip%20Standard&no_letterhead=0';
                window.open(url, '_blank');
            }).addClass('btn-primary');
        }
    }
});
