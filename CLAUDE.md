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

# Django shell
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py shell
```

Always use `venv/bin/python` — system `python` is not available on the VPS.

### Content catalog management (all idempotent, safe to re-run)

The catalog ships via management commands rather than migrations. **The `refine_*_ladder.py` commands are the source of truth** for each category's final state — they delete duplicates, retune age ranges, add tasks, and wire prerequisite edges in one pass.

```bash
# Original seeds (run once, in this order, to build the base catalog)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_demo
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_full_catalog
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py expand_catalog
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_social_catalog

# Per-age children's catalogs (fill ladder gaps at every age)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_age5_catalog
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_age6_catalog
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_age14_catalog
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_age15_catalog
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_age16_catalog

# Category ladder refinements — the canonical state for each category
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py refine_cognitive_ladder
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py refine_social_ladder
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py refine_financial_ladder
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py refine_digital_ladder
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py refine_navigation_ladder
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py refine_household_ladder

# Adult catalog (ages 17-99)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_adult_catalog
```

To rebuild from scratch: flush the Task/Tag tables, then run the commands above in order. If you need to rewrite catalog content, **edit the relevant `refine_*_ladder.py` command and re-run it** — don't hand-patch the DB.

### Flutter app

```bash
cd app
flutter pub get        # needed after pubspec.yaml changes or new packages
flutter run -d <device-id>
flutter analyze
flutter test           # runs app/test/ladder_test.dart
```

`flutter clean` is **only** needed when Hive TypeAdapters change (new `typeId`, new box, or changed field layout). For pure `.dart` code changes, just `flutter run`.

OTP is stubbed in dev — any phone number + `000000` logs you in.

Sensitive Hive boxes are encrypted at rest (AES-256, key in Android Keystore). After changing the encryption layer or `ProfileKind`-level schema, existing installs need reinstall or **Settings → Apps → SmartStep → Clear storage** — the old data won't decrypt.

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

After any backend change, always `git push origin main` — the Windows development machine runs `sync.bat` which pulls from GitHub, not from the VPS. The Flutter build happens on that Windows machine.

---

## Architecture

### Target audience: children 5–16 AND adults 18+

Originally a parent-facilitated children's app, SmartStep now also supports adults who want to build street-smart real-life skills for themselves. Profiles have a **`ProfileKind` (child / adult)**; everything (ladder, onboarding, baseline, dashboard, task detail) adapts from that one flag. A single device can hold a mix of child and adult profiles.

### Privacy boundary (hard constraint)

All child/adult PII (name, DOB, sex, environment, task progress, custom tasks, auth tokens) lives **on-device only** in Hive boxes, and the sensitive ones are **encrypted at rest** with AES-256 (key in Android Keystore via `flutter_secure_storage`). The server stores only the content graph and anonymous telemetry (age band + environment + task slug). Never add user identifiers to any server model or API response.

### Compliance surface

The onboarding flow exists in its current shape to meet Google Play Families Policy and Indian DPDP Act 2023 requirements:
- **`/consent`** is the first screen; parental-guardian attestation + policy agreement are required before any data is entered.
- **In-app privacy policy** at `/legal/privacy` and terms at `/legal/terms` are fully authored in markdown and always reachable.
- **Profile → Privacy & Data** surfaces what is stored/sent/never-collected, offers per-child Export (JSON via share sheet) and Delete, and a contact-privacy action.

When changing anything that touches data handling, update the privacy policy content too — the legal screens render directly from markdown constants in their respective files.

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

**Task model key fields:** `slug`, `title`, `how_to_md`, `safety_md`, `parent_note_md`, `min_age`, `max_age`, `sex_filter` (any/male/female), `environments` (M2M), `tags` (M2M), `status` (ReviewStatus), `repetitions_required`.

**Tag.Category choices (6):** `financial`, `household`, `digital`, `navigation`, `cognitive`, `social`. The category string is what the Flutter app uses to colour-code and icon tasks.

**Age conventions:**
- Child tasks: `min_age ∈ 5–16`, typically `max_age ≤ 16`
- Adult tasks: `min_age ≥ 17`, typically `max_age = 99`
- Flutter slices the catalog by profile kind using these thresholds. No backend column for "audience".

**ReviewStatus workflow:** `draft → pending → approved → rejected`. Only `approved` rows are served by the public API.

**DAG integrity** — `PrerequisiteEdge.save()` calls `full_clean()` which runs a DFS cycle check. Never bypass `save()` with `bulk_create` on edges — it skips the cycle check.

**URL layout** (flat, no namespaces):
- `/api/v1/tasks/` — supports `?environment=`, `?sex=`, `?min_age=`, `?max_age=`, `?tag=` (no age-filter by default — Flutter filters locally)
- `/api/v1/rewards/` — supports `?age=`
- `/api/v1/telemetry/task-completion/` — anonymous POST (task slug + age band + environment)
- `/api/v1/auth/dev-token/` — DEBUG-only JWT shortcut
- `/admin/content/task/screen/` — custom screening UI
- `/admin/content/task/graph/` — Mermaid DAG visualisation

**Custom admin views** — wired via `TaskAdmin.get_urls()` in `content/admin.py`. The screening form uses `TaskScreenForm` (plain `forms.Form`, not `ModelForm`) and honours a `save_action` POST param to override status on save.

**Current catalog state:** ~484 approved tasks across 6 laddered categories (cognitive 84, social 72, household 67, digital 64, navigation 63, financial 62, plus 72 adult tasks with `min_age ≥ 17` spread across the 6 categories). Every age year 5–16 has dedicated content in every category. DAG is fully chained — ~400+ prerequisite edges.

---

### Flutter app (`app/`)

**Stack:** Riverpod · go_router · Hive (encrypted for PII) · Dio · flutter_markdown · share_plus · flutter_secure_storage

**Key files beyond what's obvious:**

```
lib/
  app.dart                              # go_router + consent-first redirect guard
  providers.dart                        # progressVersionProvider
  domain/
    ladder.dart                         # computeLadderState() — pure DAG evaluator
    prioritise.dart                     # Next-Up scoring + category balancing
    baseline.dart                       # child baseline questions (by category×tier)
    adult_baseline.dart                 # adult baseline questions
    models.dart                         # Task, Tag, Prerequisite, Reward (hand JSON)
  data/
    local/
      hive_setup.dart                   # encrypted box setup + AES key provisioning
      child_profile.dart                # ChildProfile + Sex + Environment + ProfileKind
      task_progress.dart                # TaskProgress + ProgressStatus enum
      custom_task.dart / custom_reward.dart
      active_child.dart                 # activeChildIdProvider (profile, not just child)
  features/
    onboarding/
      consent_screen.dart               # first screen: DPDP consent + policy checkboxes
      phone_screen.dart                 # OTP via Firebase Auth
      child_profile_screen.dart         # kind toggle + DOB + sex + review dialog
      environment_screen.dart
      baseline_screen.dart              # dispatches to child or adult questions
    legal/
      privacy_policy_screen.dart        # in-app markdown privacy policy
      terms_screen.dart
    ladder/dashboard_screen.dart        # filter chips, Today's Pick, priority ordering
    task/
      task_detail_screen.dart           # practice flow, celebration, skip flows
      reward_picker_sheet.dart
      custom_task_detail_screen.dart
    profile/
      profile_screen.dart
      data_export.dart                  # JSON export via share sheet (DPDP "access")
```

**Hive boxes** — all opened in `hive_setup.dart`:

| Box | Type | Key | TypeId | Encrypted |
|-----|------|-----|--------|-----------|
| `childBox` | `ChildProfile` | profile id (microsecondsSinceEpoch string) | 1 | **yes** |
| `progressBox` | `TaskProgress` | `childId::taskSlug` | 2 | **yes** |
| `sessionBox` | dynamic | arbitrary string | — | **yes** |
| `customTaskBox` | `CustomTask` | millisecondsSinceEpoch string | 5 | **yes** |
| `rewardUsageBox` | `RewardUsage` | auto | 3 | no |
| `customRewardBox` | `CustomReward` | millisecondsSinceEpoch string | 4 | no |

The encryption key is a 256-bit AES key persisted in `flutter_secure_storage` (Android Keystore backed). It is generated on first launch and never leaves secure storage.

**`ChildProfile` is used for both children and adults** (historical name). The `kind: ProfileKind` field (defaults to `child` for backward-compat Hive reads) determines everything. `isAdult` getter is available. Adult-profile age-band (for anonymous telemetry) is `18_25 / 26_35 / 36_45 / 46_55 / 56_plus`; child is `7_8 / 9_10 / 11`.

`sessionBox` stores the encrypted consent flag (`consent_given`, `consent_ts`), JWT tokens, reward titles (`reward::{childId}::{taskSlug}`), practice counts (`count::{childId}::{taskSlug}`), per-category filter state, collapsed-done toggles, and Today's Pick slugs. Keys are arbitrary strings.

**Router redirect guard (`app.dart`):**
1. Paths starting with `/legal/` are always allowed.
2. No consent → must be on `/consent`.
3. Consent + at least one profile → onboarding URLs redirect to `/dashboard`.
4. Consent + no profile → redirect to `/phone`.

`progressVersionProvider` (StateProvider<int>) — increment it after any Hive write to trigger dashboard rebuild. Widgets that need reactivity should `ref.watch(progressVersionProvider)`.

**`activeChildIdProvider`** — the currently selected profile's id (child OR adult). Use `setActiveChild()` from `active_child.dart` to change it (persists to sessionBox).

---

### Ladder algorithm

**`computeLadderState(task, progressBySlug, {knownSlugs})`** in `domain/ladder.dart` — pure function returning `unlocked` / `lockedWithWarning` / `locked` / `completed` / `satisfied`. Evaluates mandatory prerequisites recursively via the passed progress map. Optional `knownSlugs` gracefully handles missing prereq tasks (content renamed/removed).

**`scoreTasks(...)` + `orderByPriorityWithBalance(...)`** in `domain/prioritise.dart` — picks what appears in Next Up, in what order. Score blends:
- base state (unlocked > lockedWithWarning)
- close-to-done (practice started but not finished)
- gateway boost (+5 per downstream task)
- sweet-spot (child's age in task's age band)
- stable daily jitter (seeded by date — fresh daily, stable within a day)

Then a category-balance pass prevents more than 2 consecutive tiles sharing one category.

**Dashboard classification** (in `_LadderListState.build()`):
1. `skippedUnsuitable` progress → **Skipped** section (always visible)
2. `LadderState.completed` or `satisfied` → **Done by category** sections (collapsible per category)
3. `unlocked` or `lockedWithWarning`:
   - No prerequisites AND above child's age → **hidden** (age gates the start)
   - Otherwise → **Next Up** section (dynamic limit 5–10 based on unlocked count), with `isAboveAge` badge if unlocked via prereqs despite age; `Unlocks N` gateway badge if ≥3 downstream tasks depend on it
4. `locked` with no explicit skip → hidden entirely

**Age filtering** — age is NOT sent to the API. The dashboard's `_catalogProvider` fetches all tasks matching environment+sex, then slices by profile kind:
- Adult profile: `minAge ≥ 17`
- Child profile: `minAge ≤ 16`

Age-gating at the start of the ladder + age-unlocked-via-prereqs appearing with an "Advanced" badge happens inside the classification logic, not in the API.

**`ProgressStatus` semantics:**
- `completed` / `bypassed` → `satisfies = true` (clears mandatory prereq)
- `skippedKnown` → `softSkipped = true` → downstream becomes `lockedWithWarning`, still usable
- `skippedUnsuitable` → `LadderState.locked`, shown in Skipped section, blocks descendants

**Baseline check-in** — runs after onboarding. Child profiles use `baseline.dart` (18 questions gated by age: Basic 7+, Intermediate 10+, Advanced 13+). Adult profiles use `adult_baseline.dart` (18 questions gated: Basic 20+, Intermediate 28+, Advanced 36+). A "Yes" answer bypasses all matching tasks up to that tier's age ceiling, scoped to the profile kind (an adult "Yes" never touches child tasks and vice versa). Re-runnable at any time from Profile → Recalibrate Ladder; never overwrites already-completed tasks.

**Custom tasks** use `progressSlug = 'custom::$id'` as the Hive key suffix — same `progressBox` as API tasks.

**Content rendering** — `how_to_md`, `safety_md`, `parent_note_md` are Markdown. Always use `MarkdownBody` (for inline) or `Markdown` (for full screens) from `flutter_markdown`, never `Text()`. Markdown links use `onTapLink` to copy the URL to clipboard + show a snackbar (avoids a `url_launcher` dependency).

**Profile kind adapts UI throughout** — AppBar titles, "For Parents" vs "Why This Matters" note card, celebration sheet copy, share message tone, and onboarding prompts all branch on `child.isAdult`.

**Routes** (in `app.dart`):
- `/consent` → `/phone` → `/onboarding/child` → `/onboarding/environment` → `/onboarding/baseline` → `/dashboard`
- `/dashboard`, `/profile`, `/task/:slug`, `/custom-task/:id`
- `/legal/privacy`, `/legal/terms` (always accessible)

---

## What is NOT yet done

- Push notifications: `ScheduledNotification` model exists, no send mechanism yet
- Gunicorn + systemd service for production backend (currently `manage.py runserver`)
- Hive migration for existing installs when encryption/schema changes — current policy is "uninstall + reinstall" (acceptable pre-production)
- Public-URL hosted privacy policy (in-app version exists; need a copy at `areafair.in/smartstep/privacy` for the Play Console submission)
- Play Console submission: Data Safety declaration, target-audience content rating questionnaire
