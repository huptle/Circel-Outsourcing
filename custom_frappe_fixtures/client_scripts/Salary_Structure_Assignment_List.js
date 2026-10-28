// Client Script for DocType: Salary Structure Assignment
// Name: Salary Structure Assignment-List
// Enabled: 1


frappe.listview_settings['Salary Structure Assignment'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('✏️ Editable Spreadsheet View'), function() {
            frappe.set_route('report', 'Salary Structure Assignment');
        });
    }
};
