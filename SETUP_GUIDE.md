# Quick Setup Guide — Awash Bank Issue Tracker

## One-Time Setup

### Step 1: Install dependencies
```bash
cd "issues tracking/backend"
python -m pip install -r requirements.txt
```

> **Important:** Use `python -m pip` (not just `pip`) to make sure packages install into the same Python that runs the server.

### Step 2: Seed the database
```bash
python -m app.seed
```

Expected output:
```
🌱 Seeding Awash Bank Issue Tracker...
✅ Seed complete!

📋 Demo Accounts:
  admin / Admin@123  (Administrator)
  pm.sara / Pass@123  (Project Manager)
  ...
```

### Step 3: Start the server
```bash
python -m uvicorn main:app --reload
```

### Step 4: Open the app
Navigate to **http://localhost:8000** in your browser.

---

## Demo Accounts

| Username | Password | Role |
|---|---|---|
| admin | Admin@123 | Administrator |
| pm.sara | Pass@123 | Project Manager |
| qa.meron | Pass@123 | QA Engineer |
| dev.yonas | Pass@123 | Developer |
| devops.abel | Pass@123 | DevOps Engineer |
| sec.hana | Pass@123 | Security Engineer |
| ba.daniel | Pass@123 | Business Analyst |

---

## Troubleshooting

### "No module named 'sqlalchemy'" or similar
You have multiple Python versions. Always use `python -m pip install` instead of `pip install`.

### Port 8000 already in use
```bash
python -m uvicorn main:app --reload --port 8001
```
Then open http://localhost:8001

### Database errors / want fresh start
```bash
Remove-Item awash_tracker.db
python -m app.seed
```

### bcrypt / passlib errors
The system uses `bcrypt` directly (not passlib). If you see passlib errors, they are harmless warnings — the system still works.

---

## What's Included

- Dashboard with live charts (status, priority, daily trend)
- All Issues list with filters and search
- My Issues view
- Kanban board (active sprint)
- Backlog management
- Projects management
- Sprint management with progress tracking
- Burndown chart (Reports page)
- SLA Monitor with color-coded status
- Audit Log
- Team management
- Notifications
- Time tracking on issues (log hours per issue)
- File attachments on issues
- CSV export of all issues
- Role-based access (Admin, PM, BA, QA, DevOps, Developer, Security, Viewer)
- Awash Bank branding (Navy #1B1F6B + Orange #F5A623)

## API Documentation

With the server running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
