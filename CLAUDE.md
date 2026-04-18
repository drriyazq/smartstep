# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend

```bash
cd /home/drriyazq/smartstep/backend

# Dev server
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py runserver 0.0.0.0:8001

# Migrations
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py makemigrations
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py migrate

# Tests (picks up DJANGO_SETTINGS_MODULE from pyproject.toml automatically)
pytest
pytest content/tests/
pytest -k test_cycle_is_rejected

# Lint / format
ruff check .
ruff format .

# Seed / catalog commands (all idempotent)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_demo
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_full_catalog
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py expand_catalog      # extends ages, fills how-tos, approves pending tasks, adds 17 tasks
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_social_catalog # adds 25 Social & Communication tasks

# Django shell
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py shell
```

Always use `venv/bin/python` — system `python` is not available on the VPS.

### Flutter app

```bash
cd app
flutter pub get        # needed after pubspec.yaml changes or new packages
flutter run -d <device-id>
flutter analyze
flutter test           # runs app/test/ladder_test.dart
```

`flutter clean` is only needed when new Hive TypeAdapters are added (new `typeId` or new box). For `.dart` code changes, just `flutter run`.

OTP is stubbed in dev — any phone number + `000000` logs in.

### Docker (full-stack local dev)

```bash
cd infra
docker compose up --build
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/  (admin / admin)
```

---

## Deployment (Production — VPS 187.127.134.77)

Backend is live on port 8001, proxied by Nginx at `https://areafair.in/smartstep-admin/`.

```bash
# Restart if it dies
cd /home/drriyazq/smartstep/backend
DJANGO_SETTINGS_MODULE=smartstep.settings.dev nohup venv/bin/python manage.py runserver 0.0.0.0:8001 &
```

**Admin:** `https://areafair.in/smartstep-admin/`
**Task screening:** `https://areafair.in/smartstep-admin/content/task/screen/`
**DAG graph:** `https://areafair.in/smartstep-admin/content/task/graph/`

After any backend change, always `git push origin main` — the Windows sync script (`sync.bat`) pulls from GitHub, not the VPS directly.

---

## Architecture

### Privacy boundary (hard constraint)

All child PII (name, DOB, sex, environment, task progress) lives **on-device only** in Hive boxes. The server stores only the content graph and anonymous telemetry. Never add child identifiers to any server model or API response.

---

### Backend (`backend/`) — Django 5 + DRF

**Stack:** Django 5 · DRF · SimpleJWT · django-environ · WhiteNoise · SQLite (dev) / PostgreSQL (prod)

**Four apps:**

| App | Owns |
|-----|------|
| `content` | `Task`, `Tag`, `Environment`, `PrerequisiteEdge`, `TaskCompletionEvent` |
| `rewards` | `RewardCategory`, `RewardItem` |
| `notifications` | `ScheduledNotification` |
| `api` | DRF views, serializers, URL wiring |

**Task model key fields:** `slug`, `title`, `how_to_md`, `safety_md`, `parent_note_md`, `min_age`, `max_age`, `sex_filter` (any/male/female), `environments` (M2M), `tags` (M2M), `status` (ReviewStatus).

**Tag.Category choices:** `financial`, `household`, `digital`, `navigation`, `cognitive`, `social`. The category string is what the Flutter app uses to colour-code and icon tasks.

**SexFilter** — `any`, `male`, `female` on each Task. API accepts `?sex=male|female` and filters with `sex_filter__in=["any", sex]`.

**ReviewStatus workflow:** `draft → pending → approved → rejected`. Only `approved` rows are served by the public API.

**DAG integrity** — `PrerequisiteEdge.save()` calls `full_clean()` which runs a DFS cycle check. Never bypass `save()` with `bulk_create` on edges — it skips the cycle check.

**URL layout** (flat, no namespaces):
- `/api/v1/tasks/` — supports `?environment=`, `?sex=`, `?min_age=`, `?max_age=`, `?tag=`
- `/api/v1/rewards/` — supports `?age=`
- `/api/v1/telemetry/task-completion/` — anonymous POST
- `/api/v1/auth/dev-token/` — DEBUG-only JWT shortcut
- `/admin/content/task/screen/` — custom screening UI
- `/admin/content/task/graph/` — Mermaid DAG visualisation

**Custom admin views** — wired via `TaskAdmin.get_urls()` in `content/admin.py`. The screening form uses `TaskScreenForm` (plain `forms.Form`, not `ModelForm`) and honours a `save_action` POST param to override status on save.

**Current DB state:**
- **Tasks:** 142 total, all approved — cognitive (31), household (25), social (25), navigation (21), digital (20), financial (20)
- **Prerequisite edges:** ~76
- **Tags:** 7 (social tag added: "Social skills")
- **Reward items:** 31 across 3 categories (time / experience / material)

---

### Flutter app (`app/`)

**Stack:** Riverpod · go_router · Hive · Dio · flutter_markdown · share_plus

**Key files beyond what's obvious:**
```
lib/
  app.dart                          # go_router + redirect guard
  providers.dart                    # progressVersionProvider, activeChildIdProvider
  domain/
    ladder.dart                     # computeLadderState() — pure function, all DAG logic here
    models.dart                     # Task, Reward domain models (hand-written fromJson)
  data/
    local/
      hive_setup.dart               # all box declarations + open() call
      child_profile.dart            # ChildProfile + Sex + Environment enums
      task_progress.dart            # TaskProgress + ProgressStatus enum
      custom_reward.dart            # CustomReward (typeId=4)
      custom_task.dart              # CustomTask (typeId=5), has progressSlug getter
      active_child.dart             # activeChildIdProvider + setActiveChild()
  features/
    ladder/dashboard_screen.dart    # main screen — _LadderListState, _ProgressCard
    task/task_detail_screen.dart    # completion flow + _CelebrationSheet
    task/reward_picker_sheet.dart   # reward selection bottom sheet
    task/custom_task_detail_screen.dart
    profile/profile_screen.dart     # settings, custom tasks/rewards, logout, share
```

**Hive boxes** (all opened in `hive_setup.dart`):

| Box | Type | Key | TypeId |
|-----|------|-----|--------|
| `childBox` | `ChildProfile` | child id (uuid string) | 1 |
| `progressBox` | `TaskProgress` | `childId::taskSlug` | 2 |
| `rewardUsageBox` | `RewardUsage` | auto | 3 |
| `customRewardBox` | `CustomReward` | millisecondsSinceEpoch string | 4 |
| `customTaskBox` | `CustomTask` | millisecondsSinceEpoch string | 5 |
| `sessionBox` | dynamic | arbitrary string | — |

`sessionBox` stores JWT tokens and reward titles keyed as `reward::{childId}::{taskSlug}`.

**Redirect guard** — `childBox.isNotEmpty` → `/dashboard`; empty → `/phone`. Logout clears all boxes and calls `context.go('/phone')`.

**`progressVersionProvider`** (StateProvider<int>) — increment it after any Hive write to trigger dashboard rebuild. Every widget that needs reactivity should `ref.watch(progressVersionProvider)`.

**`activeChildIdProvider`** — the currently selected child's id. Use `setActiveChild()` from `active_child.dart` to change it (persists to sessionBox).

**Ladder classification logic** (in `_LadderListState.build()`):
1. `skippedUnsuitable` progress → **Skipped** section (always visible)
2. `LadderState.completed` or `satisfied` → **done by category** section
3. `unlocked` or `lockedWithWarning`:
   - No prerequisites AND above child's age → **hidden** (age gates the start of the ladder)
   - Otherwise → **Next Up** section (max 5 visible, expand button for more), with `isAboveAge` badge if unlocked via prereqs despite age
4. `locked` with no explicit skip → **hidden entirely**

**Age filtering** — Age is NOT sent to the API. All tasks for the child's sex + environment are fetched. Age logic runs in Flutter during ladder classification (see above). This allows tasks unlocked via prerequisites to appear even if above the child's age.

**`computeLadderState()`** — pure function in `domain/ladder.dart`. Takes a `Task` and `Map<String, TaskProgress>`. Returns `LadderState`. All prerequisite evaluation lives here — no business logic in widgets.

**`ProgressStatus` semantics:**
- `completed` / `bypassed` → `satisfies = true` (clears mandatory prereq)
- `skippedKnown` → `softSkipped = true` → `LadderState.satisfied` (treated as "already mastered")
- `skippedUnsuitable` → `LadderState.locked` but shown in Skipped section

**Custom tasks** use `progressSlug = 'custom::$id'` as the Hive key suffix — same `progressBox` as API tasks.

**Post-completion share** — `_CelebrationSheet` in `task_detail_screen.dart` shows a pre-filled achievement message using `share_plus`. Parents can post to WhatsApp, Instagram, Facebook, etc.

**Content rendering** — `how_to_md`, `safety_md`, `parent_note_md` are Markdown. Always use `MarkdownBody` from `flutter_markdown`, never `Text()`.

**Routes** (in `app.dart`):
- `/phone` → `/onboarding/child` → `/onboarding/environment` → `/onboarding/baseline` → `/dashboard`
- `/dashboard`, `/profile`, `/task/:slug`, `/custom-task/:id`

---

## What is NOT yet done

- Push notifications: `ScheduledNotification` model exists, no send mechanism yet
- Baseline assessment: screen scaffolded, auto-mark-complete scoring logic not implemented
- Gunicorn + systemd service for production backend (currently `manage.py runserver`)
