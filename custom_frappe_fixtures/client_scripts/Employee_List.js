// Client Script for DocType: Employee
// Name: Employee-List
// Enabled: 1


frappe.listview_settings['Employee'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('📥 Download Master Data (Excel)'), function() {
            window.open('/files/Master_Data_Employees.xlsx', '_blank');
        });
        listview.page.add_inner_button(__('📥 Download Attendance Template'), function() {
            window.open('/files/Attendance_Upload_Template.xlsx', '_blank');
        });
        listview.page.add_inner_button(__('✏️ Editable Spreadsheet View'), function() {
            frappe.set_route('report', 'Employee');
        });
    }
};
