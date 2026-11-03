# Circle Outsourcing — HR Desk

Custom HR Desk interface for Circle Outsourcing, served by Frappe HR / ERPNext.

## Repository Structure

| File / Folder | What it is |
| :--- | :--- |
| `hr-desk.html` | The HR Desk page (Frappe web page template). **The main page file.** |
| `hr_desk.py` | Page controller: login check, allowed roles, logged-in user details, security token. |
| `run_local.py` | **Instant Local Preview Runner** (Zero-Docker, runs in 1 second with mock data). |
| `custom_frappe_fixtures/` | All Client Scripts, Corporate Print Formats (Increment Letter, Appointment Letter, Offer Letter), and Workspaces. |
| `local_development/` | Full-stack local Docker Compose setup with sample demo data seeder. |
| `.github/workflows/deploy-dev.yml` | Full-stack CI/CD workflow deploying `dev` to the development environment. |
| `.github/workflows/deploy-production.yml` | Full-stack CI/CD workflow deploying `main` to the production environment. |

---

## ⚡ Quick Start: 2 Ways to Run Locally

### Option A: Instant Local Preview (Recommended for quick UI testing — Zero Docker)
Run with Python standard library (no pip packages or Docker required):

```bash
python run_local.py
```

* **Local URL:** [http://localhost:8000/hr-desk](http://localhost:8000/hr-desk)
* Automatically launches your browser with pre-loaded mock candidates, employees, salary slips, and attendance.
* Perfect for fast UI development, styling, and checking how the app looks.

---

### Option B: Full-Stack Local Docker Environment (ERPNext + MariaDB Backend)
For full backend testing with a real local database:

```bash
cd local_development
docker compose up -d
docker compose exec backend python3 /home/frappe/frappe-bench/seed_demo_data.py frontend
```

* **Local URL:** [http://localhost:8090/hr-desk](http://localhost:8090/hr-desk)
* **Login:** `Administrator` / `admin`
* See [`local_development/README.md`](local_development/README.md) for full instructions.

---

## 🌐 Hosted Environments

| Environment | Branch | URL (login required) | Server files |
| :--- | :--- | :--- | :--- |
| Development | `dev` | http://187.127.133.225:8090/hr-desk-dev | `apps/hrms/hrms/www/hr-desk-dev.html`, `hr_desk_dev.py` |
| Production | `main` | http://187.127.133.225:8090/hr-desk | `apps/hrms/hrms/www/hr-desk.html`, `hr_desk.py` |

Both environments are deployed 100% automatically via GitHub Actions CI/CD with zero manual intervention on the server.

---

## Workflow

1. Create a branch from `dev`: `git checkout dev && git pull && git checkout -b fix/<short-name>`
2. Test locally using `python run_local.py` or Docker Compose.
3. Open a pull request into `dev`. After merge, the dev page updates automatically. Test it at `/hr-desk-dev`.
4. Open a pull request from `dev` into `main`. After approval and merge, production updates automatically.
