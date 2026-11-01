#!/usr/bin/env python3
"""
Sync Custom Frappe Fixtures to Local or Remote Frappe Site
Usage:
  python3 sync_fixtures.py [site-name]
"""

import os
import sys
import json
import shutil

def get_fixtures_dir():
    return os.path.dirname(os.path.abspath(__file__))

def sync_client_scripts():
    import frappe
    cs_dir = os.path.join(get_fixtures_dir(), "client_scripts")
    if not os.path.exists(cs_dir):
        return

    print("--> Syncing Client Scripts...")
    for filename in os.listdir(cs_dir):
        if not filename.endswith(".js"):
            continue
        filepath = os.path.join(cs_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        script_name = filename[:-3].replace("___", " - ")
        view = "List" if "List" in filename else "Form"

        # Determine doctype accurately from script content or mapping
        import re
        m = re.search(r"frappe\.ui\.form\.on\(['\"]([^'\"]+)['\"]", code) or re.search(r"frappe\.listview_settings\['([^']+)'\]", code)
        if m:
            doctype = m.group(1)
        elif "Salary_Slip" in filename:
            doctype = "Salary Slip"
        elif "Salary_Structure_Assignment" in filename or "SSA" in filename:
            doctype = "Salary Structure Assignment"
        elif "Job_Offer" in filename:
            doctype = "Job Offer"
        elif "Employee" in filename:
            doctype = "Employee"
        elif "Attendance" in filename:
            doctype = "Attendance"
        else:
            doctype = script_name.split(" - ")[0].replace("_", " ")

        existing = frappe.db.get_value("Client Script", {"name": script_name}) or frappe.db.get_value("Client Script", {"dt": doctype, "view": view})
        if existing:
            doc = frappe.get_doc("Client Script", existing)
            doc.script = code
            doc.enabled = 1
            doc.save(ignore_permissions=True)
            print(f"  ✓ Updated Client Script: {existing}")
        else:
            doc = frappe.get_doc({
                "doctype": "Client Script",
                "name": script_name,
                "dt": doctype,
                "view": view,
                "script": code,
                "enabled": 1
            })
            doc.insert(ignore_permissions=True)
            print(f"  ✓ Created Client Script: {script_name}")
    frappe.db.commit()

def sync_print_formats():
    import frappe
    pf_dir = os.path.join(get_fixtures_dir(), "print_formats")
    if not os.path.exists(pf_dir):
        return

    print("--> Syncing Print Formats...")
    # 1. HTML Formats
    for filename in os.listdir(pf_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(pf_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()

            pf_name = filename[:-5].replace("_", " ")
            doc_type = "Job Offer"
            if "Appointment Letter - Employee" in pf_name:
                doc_type = "Employee"
            elif "Appointment" in pf_name:
                doc_type = "Job Offer"
            elif "Experience" in pf_name or "Relieving" in pf_name or "1099" in pf_name:
                doc_type = "Employee"
            elif "Salary" in pf_name:
                doc_type = "Salary Structure Assignment"

            if frappe.db.exists("Print Format", pf_name):
                doc = frappe.get_doc("Print Format", pf_name)
                doc.html = html
                doc.doc_type = doc_type
                doc.custom_format = 1
                doc.print_format_type = "Jinja"
                doc.save(ignore_permissions=True)
                print(f"  ✓ Updated Print Format: {pf_name}")
            else:
                doc = frappe.get_doc({
                    "doctype": "Print Format",
                    "name": pf_name,
                    "standard": "No",
                    "custom_format": 1,
                    "print_format_type": "Jinja",
                    "doc_type": doc_type,
                    "html": html
                })
                doc.insert(ignore_permissions=True)
                print(f"  ✓ Created Print Format: {pf_name}")

        # 2. JSON Formats (e.g. Salary Slip Standard / Timesheet)
        elif filename.endswith(".json"):
            filepath = os.path.join(pf_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                pf_dict = json.load(f)

            pf_name = pf_dict.get("name")
            if not pf_name:
                continue

            if frappe.db.exists("Print Format", pf_name):
                update_fields = {}
                for k in ["format_data", "css", "disabled", "custom_format", "print_format_builder", "print_format_type"]:
                    if k in pf_dict:
                        update_fields[k] = pf_dict[k]
                frappe.db.set_value("Print Format", pf_name, update_fields)
                print(f"  ✓ Updated JSON Print Format: {pf_name}")
            else:
                doc = frappe.get_doc(pf_dict)
                doc.flags.in_import = True
                doc.insert(ignore_permissions=True)
                print(f"  ✓ Inserted JSON Print Format: {pf_name}")

    # Disable Salary Slip with Year to Date
    if frappe.db.exists("Print Format", "Salary Slip with Year to Date"):
        frappe.db.set_value("Print Format", "Salary Slip with Year to Date", "disabled", 1)

    frappe.db.commit()

def sync_company_logos():
    import frappe
    fixtures_logo_dir = os.path.join(get_fixtures_dir(), "logos")
    public_files_dir = frappe.get_site_path("public", "files")
    
    circle_logo_src = os.path.join(fixtures_logo_dir, "circle_outsourcing_logo.png")
    gcs_logo_src = os.path.join(fixtures_logo_dir, "gcs_logo.png")
    
    if os.path.exists(circle_logo_src) and os.path.exists(public_files_dir):
        dest = os.path.join(public_files_dir, "circle_outsourcing_logo.png")
        shutil.copy2(circle_logo_src, dest)
        if frappe.db.exists("Company", "Circle Outsourcing"):
            frappe.db.set_value("Company", "Circle Outsourcing", "company_logo", "/files/circle_outsourcing_logo.png")
            print("  ✓ Linked Circle Outsourcing logo")
            
    if os.path.exists(gcs_logo_src) and os.path.exists(public_files_dir):
        dest = os.path.join(public_files_dir, "gcs_logo.png")
        shutil.copy2(gcs_logo_src, dest)
        if frappe.db.exists("Company", "Global Complete Solutions"):
            frappe.db.set_value("Company", "Global Complete Solutions", "company_logo", "/files/gcs_logo.png")
            print("  ✓ Linked Global Complete Solutions logo")
    frappe.db.commit()

def sync_all():
    import frappe
    sync_client_scripts()
    sync_print_formats()
    sync_company_logos()
    frappe.clear_cache()
    print("✓ All custom fixtures synced successfully and cache cleared!")

if __name__ == "__main__":
    import frappe
    site = sys.argv[1] if len(sys.argv) > 1 else "frontend"
    sites_path = "/home/frappe/frappe-bench/sites" if os.path.exists("/home/frappe/frappe-bench/sites") else None
    if sites_path:
        frappe.init(site=site, sites_path=sites_path)
    else:
        frappe.init(site=site)
    frappe.connect()
    sync_all()
