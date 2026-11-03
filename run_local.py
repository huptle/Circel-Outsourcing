#!/usr/bin/env python3
"""
Circle Outsourcing — HR Desk Instant Local Preview Runner
Allows anyone to run and preview the complete HR Desk UI locally without Docker or Frappe.
Uses only Python standard library (no pip packages required).

Usage:
    python run_local.py [port]
"""

import sys
import os
import json
import re
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
HR_DESK_HTML_PATH = os.path.join(REPO_DIR, "hr-desk.html")

# --- Realistic Sample Mock Data for Instant Preview ---
MOCK_COMPANIES = [
    {"name": "Circle Outsourcing", "company_name": "Circle Outsourcing", "default_currency": "INR"},
    {"name": "Global Complete Solutions", "company_name": "Global Complete Solutions", "default_currency": "INR"}
]

MOCK_DEPARTMENTS = [
    {"name": "Human Resources", "department_name": "Human Resources"},
    {"name": "Engineering", "department_name": "Engineering"},
    {"name": "Quality Assurance", "department_name": "Quality Assurance"},
    {"name": "Operations", "department_name": "Operations"}
]

MOCK_DESIGNATIONS = [
    {"name": "Senior Software Engineer", "designation_name": "Senior Software Engineer"},
    {"name": "HR Executive", "designation_name": "HR Executive"},
    {"name": "QA Specialist", "designation_name": "QA Specialist"},
    {"name": "Operations Lead", "designation_name": "Operations Lead"},
    {"name": "Cook", "designation_name": "Cook"}
]

MOCK_EMPLOYEES = [
    {"name": "HR-EMP-00599", "employee": "HR-EMP-00599", "employee_name": "Arjun Pun", "first_name": "Arjun", "last_name": "Pun", "company": "Circle Outsourcing", "department": "Operations", "designation": "Cook", "status": "Active", "date_of_joining": "2024-01-15", "custom_ctc": 170275},
    {"name": "HR-EMP-00400", "employee": "HR-EMP-00400", "employee_name": "Sandeep Kumar", "first_name": "Sandeep", "last_name": "Kumar", "company": "Circle Outsourcing", "department": "Engineering", "designation": "Senior Software Engineer", "status": "Active", "date_of_joining": "2023-06-01", "custom_ctc": 240000},
    {"name": "HR-EMP-00399", "employee": "HR-EMP-00399", "employee_name": "Sukhvir Singh", "first_name": "Sukhvir", "last_name": "Singh", "company": "Circle Outsourcing", "department": "Quality Assurance", "designation": "QA Specialist", "status": "Active", "date_of_joining": "2023-11-10", "custom_ctc": 153557},
    {"name": "HR-EMP-00398", "employee": "HR-EMP-00398", "employee_name": "Praveen Kumar", "first_name": "Praveen", "last_name": "Kumar", "company": "Global Complete Solutions", "department": "Human Resources", "designation": "HR Executive", "status": "Active", "date_of_joining": "2024-03-01", "custom_ctc": 153557},
    {"name": "HR-EMP-00397", "employee": "HR-EMP-00397", "employee_name": "Anil Kumar", "first_name": "Anil", "last_name": "Kumar", "company": "Circle Outsourcing", "department": "Operations", "designation": "Operations Lead", "status": "Active", "date_of_joining": "2022-09-15", "custom_ctc": 153557}
]

MOCK_OFFERS = [
    {"name": "JOB-OFFER-2026-001", "applicant_name": "Aarav Sharma", "applicant_email": "aarav.sharma@example.com", "designation": "Senior Software Engineer", "company": "Circle Outsourcing", "status": "Accepted", "offer_date": "2026-10-25", "custom_ctc": 450000},
    {"name": "JOB-OFFER-2026-002", "applicant_name": "Priya Patel", "applicant_email": "priya.patel@example.com", "designation": "QA Specialist", "company": "Circle Outsourcing", "status": "Confirm", "offer_date": "2026-10-28", "custom_ctc": 320000},
    {"name": "JOB-OFFER-2026-003", "applicant_name": "Vikram Singh", "applicant_email": "vikram.singh@example.com", "designation": "Operations Lead", "company": "Global Complete Solutions", "status": "Yet to join", "offer_date": "2026-11-01", "custom_ctc": 280000},
    {"name": "JOB-OFFER-2026-004", "applicant_name": "Neha Gupta", "applicant_email": "neha.gupta@example.com", "designation": "HR Executive", "company": "Circle Outsourcing", "status": "Placed", "offer_date": "2026-10-15", "custom_ctc": 260000}
]

MOCK_SALARY_SLIPS = [
    {"name": "Sal Slip/HR-EMP-00599/00001", "employee": "HR-EMP-00599", "employee_name": "Arjun Pun", "start_date": "2026-09-01", "end_date": "2026-09-30", "gross_pay": 14189.58, "total_deduction": 1214.50, "net_pay": 12975.08, "status": "Draft", "company": "Circle Outsourcing"},
    {"name": "Sal Slip/HR-EMP-00400/00001", "employee": "HR-EMP-00400", "employee_name": "Sandeep Kumar", "start_date": "2026-09-01", "end_date": "2026-09-30", "gross_pay": 20091.00, "total_deduction": 2150.68, "net_pay": 17940.32, "status": "Draft", "company": "Circle Outsourcing"},
    {"name": "Sal Slip/HR-EMP-00399/00001", "employee": "HR-EMP-00399", "employee_name": "Sukhvir Singh", "start_date": "2026-09-01", "end_date": "2026-09-30", "gross_pay": 12796.44, "total_deduction": 1095.26, "net_pay": 11701.18, "status": "Draft", "company": "Circle Outsourcing"}
]

LOGIN_PAGE_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sign In - HR Desk</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f17;
      --card: #111827;
      --border: rgba(255, 255, 255, 0.1);
      --primary: #4f46e5;
      --primary-hover: #4338ca;
      --text: #f3f4f6;
      --muted: #9ca3af;
    }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .login-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 36px 32px;
      width: 100%;
      max-width: 380px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      background: rgba(79, 70, 229, 0.2);
      color: #818cf8;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      margin-bottom: 16px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 24px;
    }
    .brand-icon {
      width: 40px;
      height: 40px;
      background: var(--primary);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      color: #ffffff;
    }
    .brand-title {
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }
    .brand-subtitle {
      font-size: 12px;
      color: var(--muted);
    }
    .form-group {
      margin-bottom: 18px;
    }
    label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 6px;
      color: var(--muted);
    }
    input {
      width: 100%;
      box-sizing: border-box;
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 10px 12px;
      color: #fff;
      font-size: 14px;
      outline: none;
    }
    input:focus {
      border-color: var(--primary);
    }
    .btn {
      width: 100%;
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 6px;
      padding: 12px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 8px;
      transition: background 0.2s;
    }
    .btn:hover {
      background: var(--primary-hover);
    }
    .info-note {
      margin-top: 18px;
      font-size: 12px;
      color: var(--muted);
      text-align: center;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="login-card">
    <span class="badge">LOCAL PREVIEW MODE</span>
    <div class="brand">
      <div class="brand-icon">H</div>
      <div>
        <div class="brand-title">HR Desk</div>
        <div class="brand-subtitle">Circle Outsourcing</div>
      </div>
    </div>
    <form action="/hr-desk" method="GET">
      <div class="form-group">
        <label>User ID</label>
        <input type="text" name="usr" value="Administrator" readonly>
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" name="pwd" value="••••••••" readonly>
      </div>
      <button type="submit" class="btn">Sign In to HR Desk</button>
    </form>
    <div class="info-note">
      You logged out of the local session.<br>Click above to sign back in with demo credentials.
    </div>
  </div>
</body>
</html>"""

class HRDeskPreviewHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        try:
            sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")
        except Exception:
            pass

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ["/", "/hr-desk", "/hr-desk-dev", "/login"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Main Page routes
        if path in ["/", "/hr-desk", "/hr-desk-dev"]:
            self.serve_hr_desk_html()
            return

        # 2. Login Page route (triggered after clicking Log out)
        if path == "/login":
            self.serve_login_html()
            return

        # 3. Mock REST API calls
        if path.startswith("/api/resource/"):
            doctype = urllib.parse.unquote(path.split("/api/resource/")[1])
            self.serve_mock_resource(doctype, query)
            return

        # 4. Mock Frappe Method calls
        if path.startswith("/api/method/"):
            self.serve_mock_method(path, query)
            return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/api/method/logout", "/api/method/login", "/login"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Logged Out" if "logout" in path else "Logged In"}).encode("utf-8"))
            return

        if path.startswith("/api/resource/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"data": {"name": "DEMO-NEW-RECORD", "status": "Draft"}}).encode("utf-8"))
            return

        super().do_POST()

    def serve_login_html(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(LOGIN_PAGE_HTML.encode("utf-8"))

    def serve_hr_desk_html(self):
        if not os.path.exists(HR_DESK_HTML_PATH):
            self.send_error(404, "hr-desk.html not found")
            return

        with open(HR_DESK_HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()

        # Render Jinja variables with realistic administrator demo session
        replacements = [
            (r"window\.csrf_token\s*=\s*\{\{\s*csrf_token\s*\|\s*tojson\s*\}\};", 'window.csrf_token = "demo_local_preview_token";'),
            (r"window\.hrDesk\s*=\s*\{\{\s*hr_desk_boot\s*\|\s*tojson\s*\}\};", 'window.hrDesk = {"defaultCompany": "Circle Outsourcing", "deskUrl": "#", "frappeMajor": 16, "full_name": "Administrator", "roles": ["HR Manager", "HR User", "System Manager"], "user": "admin@circleoutsourcing.com"};'),
            (r"\{\{\s*frappe_major\s*\|\s*e\s*\}\}", "16"),
            (r"\{\{\s*user_initial\s*\|\s*e\s*\}\}", "A"),
            (r"\{\{\s*full_name\s*\|\s*e\s*\}\}", "Administrator"),
            (r"\{\{\s*user_email\s*\|\s*e\s*\}\}", "admin@circleoutsourcing.com"),
        ]

        for pattern, repl in replacements:
            html = re.sub(pattern, repl, html)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def serve_mock_resource(self, doctype, query):
        clean_dt = doctype.split("/")[0].strip()
        data = []

        if clean_dt == "Employee":
            data = MOCK_EMPLOYEES
        elif clean_dt == "Job Offer":
            data = MOCK_OFFERS
        elif clean_dt == "Salary Slip":
            data = MOCK_SALARY_SLIPS
        elif clean_dt == "Department":
            data = MOCK_DEPARTMENTS
        elif clean_dt == "Designation":
            data = MOCK_DESIGNATIONS
        elif clean_dt == "Company":
            data = MOCK_COMPANIES

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"data": data}).encode("utf-8"))

    def serve_mock_method(self, path, query):
        res = {"message": {}}
        if "get_count" in path:
            doctype = query.get("doctype", [""])[0]
            count_map = {
                "Employee": len(MOCK_EMPLOYEES),
                "Job Offer": len(MOCK_OFFERS),
                "Salary Slip": len(MOCK_SALARY_SLIPS),
                "Notification Log": 0
            }
            res = {"message": count_map.get(doctype, 5)}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(res).encode("utf-8"))

def main():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, HRDeskPreviewHandler)

    url = f"http://localhost:{PORT}/hr-desk"
    print("\n" + "=" * 65)
    print("  Circle Outsourcing — HR Desk Instant Local Preview Runner")
    print("=" * 65)
    print(f"  > URL:     {url}")
    print(f"  > Mode:    Zero-Docker Standalone Preview (Mock Data)")
    print(f"  > Status:  Server running on port {PORT}")
    print("=" * 65)
    print("  Press Ctrl+C to stop the local preview server.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local preview server. Goodbye!")
        httpd.server_close()

if __name__ == "__main__":
    main()
