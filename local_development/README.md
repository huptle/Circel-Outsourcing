# Local Development & Full Software Testing Guide

This directory allows any frontend or full-stack developer on the team to spin up the **complete ERPNext + Frappe HR software locally with Docker** and test UI and backend changes with sample demo data.

---

## 🚀 Quick Start (Run Locally in 2 Steps)

### 1. Start the Local ERPNext Stack
Ensure **Docker Desktop** is running, then run:

```bash
cd local_development
docker compose up -d
```

The stack will start MariaDB, Redis, Frappe Backend, and Nginx Frontend.
*On the first run, the `create-site` container automatically initializes a fresh local site named `frontend` with Frappe HR installed (takes ~1–2 minutes).*

### 2. Seed Realistic Demo Data
Once the containers are running, populate your local database with sample demo employees, companies, departments, designations, and job offers:

```bash
docker compose exec backend python3 /home/frappe/frappe-bench/seed_demo_data.py frontend
```

### 3. Open the App in Your Browser
Visit: **[http://localhost:8090/hr-desk](http://localhost:8090/hr-desk)**

* **Username:** `Administrator`
* **Password:** `admin`

---

## 🔄 Live UI Development & Hot Reload

The local stack mounts the repository's files directly into the running container:
* Editing `../hr-desk.html` reflects **instantly on browser refresh (Ctrl+Shift+R)**.
* Editing `../hr_desk.py` (context/session) reflects after running:
  ```bash
  docker compose restart backend
  ```

---

## 📦 Custom Client Scripts & Print Formats

All corporate print formats (Appointment Letter, Offer Letter, Experience Certificate) and Client Scripts are stored in:
`custom_frappe_fixtures/`

To sync them into your local Frappe site, run:
```bash
docker compose exec backend bench --site frontend execute custom_frappe_fixtures.sync_fixtures.sync_all
```

---

## 🛑 Stopping the Local Stack

To pause the local environment:
```bash
docker compose stop
```

To remove containers while keeping your local test data:
```bash
docker compose down
```
