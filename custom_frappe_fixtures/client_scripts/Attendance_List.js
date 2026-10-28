// Client Script for DocType: Attendance
// Name: Attendance-List
// Enabled: 1


frappe.listview_settings['Attendance'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('📥 Download Template (Excel)'), function() {
            window.open('/files/Attendance_Upload_Template.xlsx', '_blank');
        });
        listview.page.add_inner_button(__('✏️ Editable Attendance Sheet'), function() {
            frappe.set_route('report', 'Attendance');
        });
        listview.page.add_inner_button(__('⚡ Monthly Attendance Sheet'), function() {
            frappe.set_route('query-report', 'Monthly Attendance Sheet');
        });
    }
};
