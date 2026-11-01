#!/usr/bin/env python3
"""
Rich Demo Data Seeder for Circle Outsourcing HR Desk
Populates a fresh Frappe/ERPNext site with realistic sample candidates, employees,
departments, designations, and salary structures so developers can test the complete UI.
"""

import sys

def seed_demo_data(site="frontend"):
    import frappe
    from frappe.utils import nowdate, add_days

    frappe.init(site=site)
    frappe.connect()

    print("==================================================")
    print("  SEEDING SAMPLE DEMO DATA FOR LOCAL TESTING")
    print("==================================================")

    # 1. Ensure Companies Exist
    companies = ["Circle Outsourcing Demo", "Global Complete Solutions Demo"]
    for cname in companies:
        if not frappe.db.exists("Company", cname):
            doc = frappe.get_doc({
                "doctype": "Company",
                "company_name": cname,
                "default_currency": "INR",
                "country": "India"
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Company: {cname}")

    # 2. Ensure Departments
    depts = ["Human Resources", "Engineering", "Quality Assurance", "Plant Operations"]
    for dname in depts:
        if not frappe.db.exists("Department", dname):
            doc = frappe.get_doc({"doctype": "Department", "department_name": dname})
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Department: {dname}")

    # 3. Ensure Designations
    designations = ["Senior QA Engineer", "Software Developer", "HR Executive", "Plant Operator"]
    for des in designations:
        if not frappe.db.exists("Designation", des):
            doc = frappe.get_doc({"doctype": "Designation", "designation_name": des})
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Designation: {des}")

    # 4. Create Sample Job Offers (All Stages)
    demo_offers = [
        {
            "applicant_name": "Aarav Sharma",
            "email": "aarav.sharma@example.com",
            "designation": "Software Developer",
            "company": "Circle Outsourcing Demo",
            "status": "Accepted",
            "offer_date": nowdate()
        },
        {
            "applicant_name": "Priya Patel",
            "email": "priya.patel@example.com",
            "designation": "Senior QA Engineer",
            "company": "Circle Outsourcing Demo",
            "status": "Confirm",
            "offer_date": add_days(nowdate(), -5)
        },
        {
            "applicant_name": "Vikram Singh",
            "email": "vikram.singh@example.com",
            "designation": "Plant Operator",
            "company": "Global Complete Solutions Demo",
            "status": "Yet to join",
            "offer_date": add_days(nowdate(), -10)
        },
        {
            "applicant_name": "Neha Gupta",
            "email": "neha.gupta@example.com",
            "designation": "HR Executive",
            "company": "Circle Outsourcing Demo",
            "status": "Placed",
            "offer_date": add_days(nowdate(), -15)
        }
    ]

    for offer in demo_offers:
        if not frappe.db.exists("Job Offer", {"applicant_name": offer["applicant_name"]}):
            doc = frappe.get_doc({
                "doctype": "Job Offer",
                "applicant_name": offer["applicant_name"],
                "applicant_email": offer["email"],
                "designation": offer["designation"],
                "company": offer["company"],
                "status": offer["status"],
                "offer_date": offer["offer_date"]
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Job Offer: {offer['applicant_name']} ({offer['status']})")

    # 5. Create Sample Employees
    demo_employees = [
        {"name": "EMP-DEMO-001", "first_name": "Rohan", "last_name": "Mehta", "company": "Circle Outsourcing Demo", "dept": "Engineering", "des": "Software Developer"},
        {"name": "EMP-DEMO-002", "first_name": "Sunita", "last_name": "Rao", "company": "Circle Outsourcing Demo", "dept": "Human Resources", "des": "HR Executive"},
        {"name": "EMP-DEMO-003", "first_name": "Deepak", "last_name": "Verma", "company": "Global Complete Solutions Demo", "dept": "Plant Operations", "des": "Plant Operator"}
    ]

    for emp in demo_employees:
        if not frappe.db.exists("Employee", {"first_name": emp["first_name"], "last_name": emp["last_name"]}):
            doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": emp["first_name"],
                "last_name": emp["last_name"],
                "company": emp["company"],
                "department": emp["dept"],
                "designation": emp["des"],
                "status": "Active",
                "date_of_joining": add_days(nowdate(), -180),
                "date_of_birth": "1995-05-15",
                "gender": "Male" if emp["first_name"] in ["Rohan", "Deepak"] else "Female"
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Employee: {emp['first_name']} {emp['last_name']}")

    frappe.db.commit()
    print("==================================================")
    print("  ✓ DEMO DATA SEEDING COMPLETE!")
    print("==================================================")

if __name__ == "__main__":
    target_site = sys.argv[1] if len(sys.argv) > 1 else "frontend"
    seed_demo_data(target_site)
