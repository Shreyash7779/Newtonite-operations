# Engineering Decisions

## 1. Django and server-rendered UI
**Decision:** Use Django templates, forms, and a small amount of CSS rather than a separate React application.

**Reasoning:** The assessment allows technology choices and gives one working day. A single Django application reduces setup and integration overhead while still delivering a usable full-stack web app. A React client can be added later if the product needs richer client-side state.

**Trade-off:** Less client-side interactivity than a separate SPA; easier local setup and fewer moving parts.

## 2. SQLite for the local prototype
**Decision:** Use SQLite by default.

**Reasoning:** It makes the project runnable on a fresh Windows machine without installing a database server.

**Trade-off:** SQLite is not the intended final choice for a multi-thousand-user production system. PostgreSQL should be used for production concurrency and operational growth.

## 3. Team-level visibility and server-side authorization
**Decision:** Every task query is scoped to the user's teams (unless the user is a superuser). Editing is limited to the creator, a team manager, or an administrator.

**Reasoning:** Hiding buttons in HTML is not security. The server checks access on each task endpoint.

**Trade-off:** This is a deliberately small authorization model. A mature product would likely support more granular permissions and explicit organization boundaries.

## 4. Optimistic concurrency for task edits
**Decision:** Each work item has a version number. The edit form submits the version it originally loaded; if the database version has changed, the update is rejected and the user is asked to review the current item.

**Reasoning:** This prevents a stale form from silently overwriting a more recent edit.

**Trade-off:** The user may need to reload and reapply changes. Database-specific locking behaviour should be tested against PostgreSQL for production.

## 5. Atomic task claiming and activity history
**Decision:** Claiming uses a conditional update requiring the task to remain unassigned. Important operations create activity records; comments are stored separately.

**Reasoning:** The database condition determines the winner when multiple users try to claim one task. A history record makes changes explainable.

**Trade-off:** The simple prototype does not yet implement a transactional outbox or background notification delivery. Production asynchronous side effects should be retry-safe and observable.

## Deliberately not built
- External email/push notifications and background queues.
- Complex approval workflows and custom workflow builders.
- WebSocket-based live updates.
- Production deployment, observability, and rate limiting.
