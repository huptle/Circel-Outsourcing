# FIX-1 #1: HR Desk page served by Frappe (was: static file served by nginx).
# This file and hr-desk.html are new files added to the Frappe HR app's www folder,
# so the page works with the current server permissions without rebuilding the image.
import frappe
from frappe import _

no_cache = 1

HR_DESK_ROLES = {"System Manager", "HR Manager", "HR User"}


def has_hr_desk_access() -> bool:
    if frappe.session.user == "Administrator":
        return True
    return bool(HR_DESK_ROLES & set(frappe.get_roles()))


# FIX-7b: Frappe reads this file only when the backend starts; the deploy workflows restart the backend when it changes.
def get_default_company() -> str:
    """User default company, else the site default. The setup-wizard company often stays as the site
    default with no employees; then the company with the most active employees is used."""
    company = frappe.defaults.get_user_default("Company") or frappe.defaults.get_global_default("company")
    if not company or not frappe.db.exists("Employee", {"company": company, "status": "Active"}):
        rows = frappe.db.sql(
            "select company from `tabEmployee` where status = 'Active' group by company order by count(*) desc limit 1"
        )
        if rows:
            company = rows[0][0]
    return company or ""


def get_context(context):
    # FIX-1 #8: login required (was: public static page)
    if frappe.session.user == "Guest":
        # FIX-0: return to the page that was requested (/hr-desk or /hr-desk-dev)
        page = "/hr-desk-dev" if frappe.local.request.path.startswith("/hr-desk-dev") else "/hr-desk"
        frappe.local.flags.redirect_location = "/login?redirect-to=" + page
        raise frappe.Redirect

    if not has_hr_desk_access():
        frappe.throw(_("You do not have access to HR Desk."), frappe.PermissionError)

    user = frappe.get_cached_doc("User", frappe.session.user)
    full_name = user.full_name or user.name
    major = int(frappe.__version__.split(".")[0])
    desk_url = "/desk" if major >= 16 else "/app"

    # FIX-1 #1: security token so the page can make save/submit calls (needed for later fixes)
    context.csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()

    # FIX-1 #3 / #7: real user instead of the hard-coded Administrator
    context.full_name = full_name
    context.user_email = user.email or user.name
    context.user_initial = (full_name[:1] or "U").upper()
    context.frappe_major = major
    # FIX-7 #5: default company and roles, so new forms start like the classic desk does
    default_company = get_default_company()
    context.hr_desk_boot = {
        "user": user.name,
        "fullName": full_name,
        "deskUrl": desk_url,
        "defaultCompany": default_company or "",
        "roles": frappe.get_roles(),
    }
    context.no_cache = 1
    return context
