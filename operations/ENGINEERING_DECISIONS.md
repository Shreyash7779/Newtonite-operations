
# Engineering Decisions — Newtonite Operations

## 1. Technology Choices
- **Backend:** Django and Python for rapid development and built-in security features.
- **Frontend:** HTML, CSS, and Django templates for server-rendered pages.
- **Database:** SQLite for straightforward local development and evaluation.
- **Version control:** Git and GitHub.

## 2. Authentication and Authorization
- Django's built-in authentication system manages login, passwords, and sessions.
- Login is required to access the dashboard, tasks, and task API.
- Users can access tasks belonging to their teams.
- Task editing is restricted to the task creator, an authorized team manager, or a superuser.
- Team membership is checked on the server rather than relying on frontend controls.

## 3. Concurrency Handling
- Task updates use database transactions and version checks.
- If a task has changed since a user opened the edit form, a stale update is rejected to avoid overwriting newer changes.
- Task claiming uses a conditional database update so that only one request can claim an unassigned task.
- Activity logs record important task actions.

## 4. Database and Data Integrity
- Django ORM is used for database queries and model relationships.
- Foreign keys maintain relationships between tasks, teams, users, comments, and activity records.
- Database migrations manage schema changes.

## 5. Design Trade-offs
- SQLite was selected for easy setup and local evaluation. A production deployment with concurrent workloads may benefit from PostgreSQL.
- Django templates keep the frontend simple and avoid the overhead of a separate React application and API integration.
- Django's built-in authentication reduces custom security code.
- Server-side authorization provides stronger access control than hiding interface elements alone.

## 6. Known Limitations
- SQLite is intended for development and modest workloads, not every production deployment scenario.
- The application requires deployment configuration before it can be used as a public production service.
- Authentication and authorization should be tested with different users, teams, and permission levels before release.
- Production deployment should include secure environment-based settings, HTTPS, backups, and appropriate database configuration.

## 7. Testing
Automated tests are included in the operations app for authentication requirements, dashboard access, task claiming, team-based access, stale edits, permissions, and the task API.

Run the tests with:

```bash
python manage.py test operations
```
