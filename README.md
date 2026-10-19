# Newtonite Operations — Working Challenge Project

A practical full-stack work-item management app inspired by the Newtonite Software Engineering Challenge. Built with Django templates, Python, and SQLite so it can be run locally quickly on Windows. It includes authentication, teams, task ownership, priority/status, search/filtering, comments, activity history, a JSON API, and tests.

## Quick start (Windows PowerShell)

1. Install Python 3.11+ from python.org.
2. Extract this ZIP and open the `newtonite_operations` folder in VS Code.
3. Open Terminal → PowerShell and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python seed_demo.py
python manage.py runserver
```

4. Open http://127.0.0.1:8000/
5. Sign in using **demo** / **Newtonite123!**

If PowerShell blocks virtual-environment activation, run this for the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## What works

- Login/logout using Django authentication and CSRF protection.
- Dashboard with work-item counts and urgent items.
- Create, view, edit, claim, and filter tasks.
- Teams and team membership-based visibility.
- Creator/team-manager/admin edit authorization enforced on the server.
- Comments and activity timeline.
- Optimistic version check for edits: stale forms are rejected rather than silently overwriting newer values.
- Atomic conditional claim: only one request can claim an unassigned task.
- JSON API: `GET /api/tasks/` and `GET /api/tasks/?status=open` (login required).
- Database indexes for common status/team/assignee queries.
- Automated tests for login protection, dashboard, claim action, team-level visibility, and API response.

## Run tests

```powershell
python manage.py test
```

## Admin

Create an admin account with `python manage.py createsuperuser`, then visit http://127.0.0.1:8000/admin/.

## Engineering decisions

See [ENGINEERING_DECISIONS.md](ENGINEERING_DECISIONS.md).

## Important limitations

- This is an assessment-ready local prototype, not a hardened production deployment.
- SQLite is selected for zero-configuration local setup. For real concurrent production traffic, use PostgreSQL and review transaction/locking behaviour under that database.
- The UI displays up to 100 filtered records; a production deployment should use explicit page-number pagination.
- Notifications and background jobs are not implemented; they are secondary to the required core workflow.
- Demo credentials are public to anyone with this ZIP. Change or remove them before deployment.
- `DEBUG=True` and the development secret key are for local use only. Set secure environment-based settings before deployment.
- The claim endpoint enforces a single winner using a conditional database update; automated race tests should also be run against the production database.
