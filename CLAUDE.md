# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend

```bash
cd /home/drriyazq/smartstep/backend

# Run tests
pytest                              # all tests
pytest content/tests/               # single app
pytest -k test_cycle_is_rejected    # single test
pytest --cov=content                # with coverage

# Lint / format
ruff check .
ruff format .

# Dev server (SQLite unless DATABASE_URL is set)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py runserver 0.0.0.0:8001

# Migrations
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py makemigrations
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py migrate

# Seed commands (all idempotent — safe to re-run)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_demo          # 15 approved tasks + 7 reward items (original demo set)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_full_catalog  # 85 more tasks (pending review) + full reward bank
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py set_admin_password <username> <password>

# Django shell
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py shell
```

`pytest` picks up `DJANGO_SETTINGS_MODULE=smartstep.settings.dev` from `pyproject.toml` — no env var needed for tests.

### Docker (full-stack local dev)

```bash
cd infra
docker compose up --build
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/  (admin / admin)
# seed_demo runs automatically on first boot
```

### Flutter app

```bash
cd app
flutter pub get
flutter run -d <android-emulator-id>
flutter analyze
flutter test                        # runs app/test/ladder_test.dart
```

OTP is stubbed in dev — any phone number + `000000` logs in.

---

## Deployment (Production — VPS 187.127.134.77)

The backend is live, served via Django's `manage.py runserver` on port 8001 and proxied by Nginx.

**Admin panel URL:** `https://areafair.in/smartstep-admin/`
**Screening page:** `https://areafair.in/smartstep-admin/content/task/screen/`
**DAG graph:** `https://areafair.in/smartstep-admin/content/task/graph/`

The Nginx block in `/etc/nginx/sites-enabled/areafair` proxies `/smartstep-admin/` → `http://127.0.0.1:8001/`.

**Note:** Currently running as `manage.py runserver` (no Gunicorn service yet). To restart if it dies:
```bash
cd /home/drriyazq/smartstep/backend
DJANGO_SETTINGS_MODULE=smartstep.settings.dev nohup venv/bin/python manage.py runserver 0.0.0.0:8001 &
```
Upgrade to Gunicorn + systemd service when ready (same pattern as suredatapro-new.service).

---

## Architecture

### Privacy boundary (hard constraint)

All child PII (name, DOB, sex, environment preference, task progress) lives **on-device only** in Hive boxes. The server stores only the content graph and anonymous aggregate telemetry. Never add child identifiers to any server model or API response. This is the architectural decision that bypasses COPPA compliance requirements.

### Backend (`backend/`) — Django 5 + DRF

**Stack:** Django 5 · DRF · SimpleJWT · django-environ · WhiteNoise · SQLite (dev) / PostgreSQL (prod)

Four apps:

| App | Owns |
|-----|------|
| `content` | `Task`, `Tag`, `Environment`, `PrerequisiteEdge`, `TaskCompletionEvent` |
| `rewards` | `RewardCategory`, `RewardItem` |
| `notifications` | `ScheduledNotification` |
| `api` | DRF views, serializers, URL wiring |

**Review workflow** — `ReviewStatus`: `draft → pending → approved → rejected`. Only `approved` rows are served by the public API. The Django admin has bulk actions for all transitions, plus a dedicated screening UI.

**Task fields** — `slug`, `title`, `how_to_md`, `safety_md`, `parent_note_md` (why this skill matters — shown to parents in the app), `min_age`, `max_age`, `environments` (M2M to `Environment`), `tags` (M2M to `Tag`), `status`, `review_notes`.

**Tag model** — fields: `name`, `category`. The `category` field maps to the 5 task categories: `financial`, `household`, `digital`, `navigation`, `cognitive`. Tags in DB: "Money basics" (financial), "Home care" (household), "Kitchen basics" (household), "Digital literacy" (digital), "Wayfinding" (navigation), "Reasoning" (cognitive).

**Environment model** — field: `kind` (choices: `urban`, `suburban`, `rural`). Tasks tagged with environments via M2M.

**RewardCategory model** — fields: `kind`, `display_name`. Three categories: `time` / `experience` / `material`.

**RewardItem model** — fields: `title`, `category` (FK to RewardCategory), `min_age`, `max_age`, `is_free`, `notes`, `status`, `review_notes`.

**DAG integrity** — `PrerequisiteEdge.save()` calls `full_clean()` which runs a DFS cycle check. Any edit that would close a cycle raises `ValidationError` immediately. Never bypass `save()` with `bulk_create` on edges.

**Settings** — three layers: `base.py` (env-driven via `django-environ`) → `dev.py` / `prod.py`. Always use `venv/bin/python` — system `python` is not available on this VPS.

**URL layout** (flat, no namespaces):
- `/admin/` — Django admin
- `/admin/content/task/screen/` — custom task screening page (list + quick approve/reject/edit)
- `/admin/content/task/screen/add/` — add new task
- `/admin/content/task/screen/<pk>/` — edit task
- `/admin/content/task/graph/` — Mermaid DAG visualisation (approved tasks only)
- `/api/v1/tasks/` · `/api/v1/rewards/` · `/api/v1/notifications/active/` · `/api/v1/telemetry/task-completion/`
- `/api/v1/auth/dev-token/` — DEBUG-only JWT shortcut

**Custom admin views** — wired via `TaskAdmin.get_urls()` in `content/admin.py`. The screening list handles quick-action POSTs (approve/reject/draft/delete) via `?status=` tab + search + category filter. The form view uses `TaskScreenForm` (a plain `forms.Form`, not a `ModelForm`) and honours a `save_action` POST param to override status on save.

### Current DB state (as of 2026-04-18)

- **Tasks:** 100 total — 28 approved, 72 pending review
- **Prerequisite edges:** 57
- **Tags:** 6 (one per category except household which has 2)
- **Environments:** urban, suburban, rural
- **Reward items:** 31 across 3 categories (time / experience / material)
- **Scheduled notifications:** 0 (none created yet)

### Flutter app (`app/`)

**Stack:** Riverpod (state) · go_router (routing) · Hive (local storage) · Dio (HTTP) · flutter_markdown (content rendering)

**Directory structure:**
```
lib/
  main.dart
  app.dart               # go_router setup + redirect guard
  domain/
    models.dart          # Task, RewardItem, ChildProfile domain models (hand-written fromJson)
    ladder.dart          # computeLadderState() — pure DAG evaluation function
    baseline.dart        # baseline assessment logic
  data/
    api/
      client.dart        # Dio HTTP client
      task_repository.dart
      reward_repository.dart
    local/
      hive_setup.dart    # Hive box initialisation
      child_profile.dart # ChildProfile Hive adapter
      task_progress.dart # TaskProgress Hive adapter
      reward_usage.dart  # RewardUsage Hive adapter
  features/
    onboarding/
      phone_screen.dart
      child_profile_screen.dart
      environment_screen.dart
      baseline_screen.dart
    ladder/
      dashboard_screen.dart
    task/
      task_detail_screen.dart
      reward_picker_sheet.dart
```

**Hive boxes** (initialised in `data/local/hive_setup.dart`):
- `childBox` — `ChildProfile` (name, dob, sex, environment)
- `progressBox` — `TaskProgress` keyed `childId::taskSlug`
- `rewardUsageBox` — `RewardUsage` (tracks reward category history for rotation nudging)
- `sessionBox` — generic session data (JWT token)

**Onboarding flow** (routes in `app.dart`):
`/phone` → `/onboarding/child` → `/onboarding/environment` → `/onboarding/baseline` → `/dashboard`

Redirect guard: `childBox.isNotEmpty` skips onboarding to `/dashboard`; empty box redirects away from `/dashboard` to `/phone`.

**Ladder logic** — `domain/ladder.dart` exports `computeLadderState()`, a pure function. All prerequisite evaluation lives here — no business logic in widgets. `LadderState` enum: `unlocked`, `lockedWithWarning`, `locked`, `completed`, `satisfied`.

**`ProgressStatus` semantics** (critical for `computeLadderState`):
- `completed` / `bypassed` → `satisfies = true` — fully clears a mandatory prereq
- `skippedKnown` → `softSkipped = true` — triggers `lockedWithWarning` downstream (task is tappable but flagged)
- `skippedUnsuitable` → hard lock on downstream tasks

**`_TaskRow.warningPrereqTitle`** — `dashboard_screen.dart` resolves the specific skipped prereq title at build time (by walking `task.prerequisites` against progress) and stores it in `_TaskRow`. The subtitle reads `'Requires skipped: "<title>"'` rather than the generic fallback.

**Content rendering** — `how_to_md`, `safety_md`, and `parent_note_md` are all Markdown. Use `MarkdownBody` from `flutter_markdown` everywhere — never `Text()` for these fields.

**API client** — `data/api/client.dart` (Dio). Repositories in `data/api/`: manual JSON parsing, no codegen (`freezed`/`json_serializable` not used). Domain models in `domain/models.dart` with hand-written `fromJson` factories.

### Infra (`infra/`)

`docker-compose.yml` brings up Postgres + Django. Local port overrides go in `docker-compose.override.yml` (gitignored).

---

## What is NOT yet done

- Push notifications: `ScheduledNotification` model exists but no sending mechanism wired up
- Gunicorn + systemd service for production (currently `manage.py runserver`)
- Reward picker fully wired to task completion flow (sheet exists, integration TBD)
- Baseline assessment scoring logic (screen scaffolded, auto-mark-complete logic TBD)
