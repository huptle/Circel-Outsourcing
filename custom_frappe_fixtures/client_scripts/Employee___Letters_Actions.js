// Client Script for DocType: Employee
// Name: Employee - Letters Actions
// Enabled: 1


frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            // HR Letters Group
            frm.add_custom_button(__('📄 Download Relieving Letter'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Employee&name=' + encodeURIComponent(frm.doc.name) + '&format=Exact%20Corporate%20Relieving%20Letter&no_letterhead=0';
                window.open(url, '_blank');
            }, __('HR Letters'));

            frm.add_custom_button(__('📄 Download Experience Certificate'), function() {
                const url = '/api/method/frappe.utils.print_format.download_pdf?doctype=Employee&name=' + encodeURIComponent(frm.doc.name) + '&format=Exact%20Corporate%20Experience%20Certificate&no_letterhead=0';
                window.open(url, '_blank');
            }, __('HR Letters'));

            // If employee has left or is in separation, show FnF button
            if (frm.doc.status === 'Left' || frm.doc.relieving_date) {
                frm.add_custom_button(__('💰 View Full & Final Settlement'), function() {
                    frappe.set_route('List', 'Full and Final Statement', { employee: frm.doc.name });
                }, __('HR Letters'));
            }
        }
    }
});
