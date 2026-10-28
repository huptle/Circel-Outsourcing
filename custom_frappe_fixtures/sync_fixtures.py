#!/usr/bin/env python3
"""
Sync Custom Frappe Fixtures to Local or Remote Frappe Site
Usage:
  bench --site <site-name> execute custom_frappe_fixtures.sync_fixtures.sync_all
Or:
  python3 sync_fixtures.py [site-name]
"""

import os
import sys
import json

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
        doctype = script_name.split(" - ")[0].split("_")[0]

        # Determine if it's Form or List
        view = "List" if "List" in filename else "Form"

        # Check existing
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
    for filename in os.listdir(pf_dir):
        if not filename.endswith(".html"):
            continue
        filepath = os.path.join(pf_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        pf_name = filename[:-5].replace("_", " ")
        doc_type = "Job Offer"
        if "Appointment" in pf_name:
            doc_type = "Job Offer"
        elif "Experience" in pf_name or "Relieving" in pf_name:
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
    frappe.db.commit()

def sync_all():
    import frappe
    sync_client_scripts()
    sync_print_formats()
    frappe.clear_cache()
    print("✓ All custom fixtures synced successfully and cache cleared!")

if __name__ == "__main__":
    import frappe
    site = sys.argv[1] if len(sys.argv) > 1 else "frontend"
    frappe.init(site=site)
    frappe.connect()
    sync_all()
