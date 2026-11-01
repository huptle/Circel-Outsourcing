# Circle Outsourcing — HR Desk

Custom HR Desk interface for Circle Outsourcing, served by Frappe HR / ERPNext (v16).

## Repository Structure

| File / Folder | What it is |
| :--- | :--- |
| `hr-desk.html` | The HR Desk page (Frappe web page template). **The only page file — edit this one.** |
| `hr_desk.py` | Page controller: login check, allowed roles, logged-in user details, security token. |
| `custom_frappe_fixtures/` | All Client Scripts, Corporate Print Formats (Appointment Letter, Offer Letter), and Workspaces. |
| `local_development/` | Full-stack local Docker Compose setup with sample demo data seeder. |
| `.github/workflows/deploy-dev.yml` | Deploys `dev` to the dev page. |
| `.github/workflows/deploy-production.yml` | Deploys `main` to production. |

Every code change is marked with a comment naming the fix and issue, for example `FIX-1 #3: ...`.

---

## 💻 Local Testing & Full Software Development

Developers can run the **entire ERPNext + Frappe HR stack locally on their laptop** with sample demo data (no real company data needed):

```bash
cd local_development
docker compose up -d
docker compose exec backend python3 /home/frappe/frappe-bench/seed_demo_data.py frontend
```

* **Local URL:** [http://localhost:8090/hr-desk](http://localhost:8090/hr-desk) (Login: `Administrator` / `admin`)
* Editing `hr-desk.html` updates locally on page refresh immediately!
* See [`local_development/README.md`](local_development/README.md) for full instructions.

---

## 🌐 Hosted Environments

| Environment | Branch | URL (login required) | Server files |
| :--- | :--- | :--- | :--- |
| Development | `dev` | http://187.127.133.225:8090/hr-desk-dev | `apps/hrms/hrms/www/hr-desk-dev.html`, `hr_desk_dev.py` |
| Production | `main` | http://187.127.133.225:8090/hr-desk | `apps/hrms/hrms/www/hr-desk.html`, `hr_desk.py` |

Both environments are served by Frappe with the same login, roles and security token, so what works on dev works the same on production. Both use the live site data.

---

## Workflow

1. Create a branch from `dev`: `git checkout dev && git pull && git checkout -b fix/<short-name>`
2. Test locally using `local_development/docker-compose.yml` or edit `hr-desk.html` (and `hr_desk.py` if needed). Mark each change with a `FIX-<n> #<issue>` comment.
3. Open a pull request into `dev`. After merge, the dev page updates automatically. Test it at `/hr-desk-dev`.
4. Open a pull request from `dev` into `main`. After approval and merge, production updates automatically.

---

## GitHub Secrets

Set under **Settings > Secrets and variables > Actions**. Never write secret values in this repository.

| Secret | Purpose |
| :--- | :--- |
| `SERVER_HOST` | Server address |
| `SERVER_USER` | Deployment user |
| `SERVER_SSH_KEY` | SSH private key for deployment (preferred) |
| `SERVER_PASSWORD` | Fallback only |

---

## Server notes

- Do not use `sudo erpnext-ctl reload-ui`; it copies an old static page into the containers.
- After changing `frappe.conf.template` on the server, recreate the frontend container: `sudo erpnext-ctl compose up -d --no-deps --force-recreate frontend`.
