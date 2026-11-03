#!/usr/bin/env python3
"""
Rich Demo Data Seeder for Circle Outsourcing HR Desk
Populates a fresh Frappe/ERPNext site with realistic sample candidates, employees,
departments, designations, and salary structures so developers can test the complete UI.
"""

import sys
import os

def seed_demo_data(site="frontend"):
    # Ensure current directory is sites/ so frappe can locate site config
    for candidate_dir in ["/home/frappe/frappe-bench/sites", "./sites", "."]:
        if os.path.exists(candidate_dir) and os.path.exists(os.path.join(candidate_dir, site)):
            os.chdir(candidate_dir)
            break

    import frappe
    from frappe.utils import nowdate, add_days

    frappe.init(site=site)
    frappe.connect()

    print("==================================================")
    print("  SEEDING SAMPLE DEMO DATA FOR LOCAL TESTING")
    print("==================================================")

    # 0. Ensure Warehouse Type exists to prevent ERPNext company creation hook issues
    if frappe.db.table_exists("Warehouse Type") and not frappe.db.exists("Warehouse Type", "Transit"):
        try:
            frappe.get_doc({"doctype": "Warehouse Type", "name": "Transit"}).insert(ignore_permissions=True)
            print("  ✓ Ensured Warehouse Type: Transit")
        except Exception:
            pass

    # 1. Ensure Companies Exist
    companies = ["Circle Outsourcing Demo", "Global Complete Solutions Demo"]
    for cname in companies:
        if not frappe.db.exists("Company", cname):
            try:
                doc = frappe.get_doc({
                    "doctype": "Company",
                    "company_name": cname,
                    "default_currency": "INR",
                    "country": "India"
                })
                doc.flags.ignore_mandatory = True
                doc.insert(ignore_permissions=True)
                print(f"  ✓ Created Company: {cname}")
            except Exception as e:
                print(f"  ! Note on Company {cname}: {e}")

    # 2. Ensure Departments
    depts = ["Human Resources", "Engineering", "Quality Assurance", "Plant Operations"]
    for dname in depts:
        if not frappe.db.exists("Department", dname):
            try:
                doc = frappe.get_doc({"doctype": "Department", "department_name": dname})
                doc.insert(ignore_permissions=True)
                print(f"  ✓ Created Department: {dname}")
            except Exception:
                pass

    # 3. Ensure Designations
    designations = ["Senior QA Engineer", "Software Developer", "HR Executive", "Plant Operator"]
    for des in designations:
        if not frappe.db.exists("Designation", des):
            try:
                doc = frappe.get_doc({"doctype": "Designation", "designation_name": des})
                doc.insert(ignore_permissions=True)
                print(f"  ✓ Created Designation: {des}")
            except Exception:
                pass

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
            try:
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
            except Exception as e:
                print(f"  ! Job Offer notice: {e}")

    # 5. Create Sample Employees
    demo_employees = [
        {"name": "EMP-DEMO-001", "first_name": "Rohan", "last_name": "Mehta", "company": "Circle Outsourcing Demo", "dept": "Engineering", "des": "Software Developer"},
        {"name": "EMP-DEMO-002", "first_name": "Sunita", "last_name": "Rao", "company": "Circle Outsourcing Demo", "dept": "Human Resources", "des": "HR Executive"},
        {"name": "EMP-DEMO-003", "first_name": "Deepak", "last_name": "Verma", "company": "Global Complete Solutions Demo", "dept": "Plant Operations", "des": "Plant Operator"}
    ]

    for emp in demo_employees:
        if not frappe.db.exists("Employee", {"first_name": emp["first_name"], "last_name": emp["last_name"]}):
            try:
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
            except Exception as e:
                print(f"  ! Employee notice: {e}")

    frappe.db.commit()
    print("==================================================")
    print("  ✓ DEMO DATA SEEDING COMPLETE!")
    print("==================================================")

if __name__ == "__main__":
    # If not running in bench virtualenv, auto re-exec with bench python
    bench_py = "/home/frappe/frappe-bench/env/bin/python"
    if os.path.exists(bench_py) and sys.executable != bench_py:
        os.execv(bench_py, [bench_py] + sys.argv)

    target_site = sys.argv[1] if len(sys.argv) > 1 else "frontend"
    seed_demo_data(target_site)
