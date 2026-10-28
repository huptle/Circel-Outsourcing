// Client Script for DocType: Job Offer
// Name: Job Offer - Letters and Breakdown
// Enabled: 1


frappe.ui.form.on('Job Offer', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // 1. Download Offer Letter
            frm.add_custom_button(__('📄 Download Offer Letter'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Job%20Offer&name=' + encodeURIComponent(frm.doc.name) + '&format=Exact%20Corporate%20Offer%20Letter&no_letterhead=0';
                window.open(url, '_blank');
            }, __('Letters')).addClass('btn-primary');

            // 2. Download Appointment Letter
            frm.add_custom_button(__('📄 Download Appointment Letter'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Job%20Offer&name=' + encodeURIComponent(frm.doc.name) + '&format=Exact%20Corporate%20Appointment%20Letter&no_letterhead=0';
                window.open(url, '_blank');
            }, __('Letters'));

            // 3. Status Action: If Confirmed or Accepted, offer 1-click employee creation
            if (['Confirm', 'Accepted', 'Yet to join'].includes(frm.doc.status)) {
                frm.page.set_indicator(frm.doc.status, 'green');
            }
        }
    }
});
