# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend

```bash
cd /home/drriyazq/smartstep/backend

# Dev server
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py runserver 0.0.0.0:8007

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

# Rewards catalog (clears and reseeds all reward items)
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_rewards

# Gap-fill tasks (fitness, digital creation, eco, healthcare self-management)
# Required for the Active Body / Young Digital Creator / Eco-Conscious Kid /
# Handles Their Own Healthcare masteries to work.
DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_gap_tasks
```

Religion seed commands (`seed_islam_tasks*`, `seed_christianity_tasks`, `seed_hinduism_tasks`) still exist but the feature was removed from the app — do not run them unless you're explicitly re-enabling religion content.

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

Sign-in is phone-OTP based. India (+91) gets the code on WhatsApp via the shared Tru Smile WABA + System User token (`POST /auth/otp/{send,verify}/` — see `api/whatsapp.py` and `api/otp.py`). Other countries fall back to Firebase Phone Auth, then exchange the Firebase ID token for a Django JWT at `POST /auth/firebase/`. Successful WhatsApp verifies create or reuse a user via `AppUserPhone(user, phone_e164)`; Firebase verifies that carry a `phone_number` claim do the same so accounts unify across paths. Test bypass: phones in `OTP_TEST_PHONES` skip the WhatsApp send and accept `OTP_TEST_CODE` directly. Existing pre-OTP accounts (`firebase_<google_uid>`) keep their JWTs (30d access / 180d refresh) and can be re-claimed by phone via `python manage.py link_user_phone <username_or_email> <+91…>` (or `--csv path`).

**Critical for Play Store installs:** Firebase Phone Auth still needs BOTH SHA-1 fingerprints registered — the upload keystore SHA-1 (for `flutter install --release` builds) AND the Play App Signing SHA-1 (for Play Store installs, found in Play Console → App integrity → App signing). Only relevant for the non-+91 fallback path; +91 OTP doesn't depend on SHA-1.

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

Backend is live on port 8007, proxied by Nginx at `https://areafair.in/smartstep-admin/`.

```bash
# Restart if it dies (runserver fallback — Gunicorn systemd service preferred)
cd /home/drriyazq/smartstep/backend
DJANGO_SETTINGS_MODULE=smartstep.settings.dev nohup venv/bin/python manage.py runserver 0.0.0.0:8007 &

# Gunicorn via systemd (once installed)
sudo systemctl start smartstep-backend
sudo journalctl -u smartstep-backend -f
```

**Admin:** `http://187.127.134.77:8007/admin/`
**Task list:** `http://187.127.134.77:8007/admin/content/task/`
**Task screening:** `http://187.127.134.77:8007/admin/content/task/screen/`
**DAG graph:** `http://187.127.134.77:8007/admin/content/task/graph/`

After any backend change, always `git push origin main` — the Windows development machine runs `sync.bat` which pulls from GitHub, not from the VPS. The Flutter build happens on that Windows machine.

---

## Architecture

### Target audience: children 5–16 AND adults 18+

Originally a parent-facilitated children's app, SmartStep now also supports adults who want to build street-smart real-life skills for themselves. Profiles have a **`ProfileKind` (child / adult)**; everything (ladder, onboarding, baseline, dashboard, task detail) adapts from that one flag. A single device can hold a mix of child and adult profiles.

### Storage architecture (2026-05-20 cutover)

User data **now lives server-side** (Django/Postgres in `userdata/`). The original on-device-only Hive store was killed because reinstalls and lost phones cost users their entire history. Architecture:

- **Server is source of truth** for profiles, task progress, custom tasks, custom rewards, reward usage, earned masteries, and per-profile UI session items (filter chips, today's pick, collapsed-done flags). Models in `backend/userdata/models.py`. URLs at `/api/v1/me/`. Every endpoint scopes by `request.user`; cross-user reads are impossible by construction.
- **Hive boxes remain as a transparent cache** for fast synchronous reads in screens. On every cold start (`SmartStepApp.initState`) we call `RemoteSync.bootstrap()` which pulls `GET /api/v1/me/state/` and rebuilds the boxes from scratch. The encrypted boxes (`childBox`, `progressBox`, `customTaskBox`, `sessionBox`) keep their AES-256 encryption — they hold sensitive data for the length of a session, even though it's no longer the only copy.
- **All writes from screens must go through `RemoteSync.persist*`** (`data/sync/remote_sync.dart`). The pattern is: send to server first, then update Hive on success. Online-required: if the server call fails, the function throws `SyncException` and the screen surfaces a snackbar — there is no offline write queue.
- **JWT + Hive encryption key stay in `flutter_secure_storage`** (Android Keystore). They are NOT moved to the server.
- **Anonymous telemetry** (skill slug + age band + environment, no identifiers) still flows to `content.TaskCompletionEvent` exactly as before. Independent of the per-user data above.

When changing any user-data write path, route through `RemoteSync`. Never call `progressBox.put` / `childBox.put` / `customTaskBox.put` / `customRewardBox.put` from a screen — those are reserved for the bootstrap hydrator.

### Compliance surface

The onboarding flow exists in its current shape to meet Google Play Families Policy and Indian DPDP Act 2023 requirements:
- **`/consent`** is the first screen; parental-guardian attestation + policy agreement are required before any data is entered.
- **In-app privacy policy** at `/legal/privacy` and terms at `/legal/terms` are fully authored in markdown and always reachable.
- **Profile → Privacy & Data** surfaces what is stored/sent/never-collected, offers per-child Export (JSON via share sheet) and Delete, and a contact-privacy action.

When changing anything that touches data handling, update the privacy policy content too — the legal screens render directly from markdown constants in their respective files.

---

### Backend (`backend/`) — Django 5 + DRF

**Stack:** Django 5 · DRF · SimpleJWT · django-environ · WhiteNoise · SQLite (dev) / PostgreSQL (prod)

**Five apps:**

| App | Owns |
|-----|------|
| `content` | `Task`, `Tag`, `Environment`, `PrerequisiteEdge`, `TaskCompletionEvent` |
| `rewards` | `RewardCategory`, `RewardItem` |
| `notifications` | `ScheduledNotification` |
| `api` | DRF views, serializers, URL wiring + auth-side models `AppUserPhone` (1:1 user ↔ E.164 phone, the lookup target for OTP flows) and `OtpDeliveryLog` (audit row for every WhatsApp send). `whatsapp.py` (Meta Graph client) and `otp.py` (Redis-backed code store) live here too. |
| `userdata` | Server-of-truth for per-user data (2026-05-20): `Profile`, `TaskProgress`, `CustomTask`, `CustomReward`, `RewardUsage`, `EarnedMastery`, `SessionItem`. All mounted under `/api/v1/me/` via `userdata/urls.py` (DRF router). Each ViewSet's `get_queryset()` filters on `request.user`. Bulk hydration via `GET /api/v1/me/state/`. DPDP-mandated wipe via `DELETE /api/v1/me/wipe/`. |

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

**Current catalog state:** 509 universal child tasks (484 from refine_*_ladder commands + 25 from seed_gap_tasks) + 72 adult tasks. Gap-fill tasks cover fitness, digital creation, eco-conscious habits, and healthcare self-management — they exist to support the corresponding mastery certificates. The `religion` field on `Task` is legacy — there are no religion tasks in the DB anymore.

**Telemetry `AgeBand`** — has both child bands (`7_8`, `9_10`, `11`) and adult bands (`18_25`, `26_35`, `36_45`, `46_55`, `56_plus`). If you add a new adult age cohort, add the band here too or the POST will silently 400.

---

### Flutter app (`app/`)

**Stack:** Riverpod · go_router · Hive (encrypted for PII) · Dio · flutter_markdown · share_plus · flutter_secure_storage · firebase_auth (Phone Auth, non-+91 fallback only) · qr_flutter · path_provider

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
      signin_screen.dart                # Phone OTP — WhatsApp (+91) or Firebase Phone Auth (other) → Django JWT
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
3. Consent + at least one profile → onboarding URLs redirect to `/dashboard`, UNLESS the URL carries `?adding=true` or `?childId=…` (mid-onboarding for a new/specific profile).
4. Consent + no profile → redirect to `/signin`.

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
- `/consent` → `/signin` → `/onboarding/child` → `/onboarding/environment` → `/onboarding/baseline` → `/dashboard`
- `/dashboard`, `/profile`, `/achievements`, `/task/:slug`, `/custom-task/:id`
- `/category/:cat`
- `/legal/privacy`, `/legal/terms` (always accessible)

`ChildProfile` still has `religionInterest` and `religion` fields on the Hive adapter (backward-compat with older installs) but they're no longer used. Do not remove the fields from the TypeAdapter — it would break Hive reads for anyone with existing data.

---

### Certificates & mastery milestones (viral share loop)

Two shareable certificate types, both generated client-side as PNG from Flutter widgets via `RepaintBoundary` → `ui.toImage` → `Share.shareXFiles`. All child PII stays on-device — caption contains only first name + the short URL `areafair.in/smartstep` (nginx 302 → Play Store with UTM tracking).

- **Skill certificate** — 1080×1080, shown when any single task is fully mastered. Replaces the old text-only "Share this win" button.
- **Mastery certificate** — 1080×1350 gold-framed, auto-triggered when a child completes ALL prerequisite tasks for a mastery bundle (e.g. "Metro & Transit Solo Traveler" needs 6 specific tasks).

**Key files:**
- `lib/domain/masteries.dart` — 29 mastery definitions (26 child + 3 adult). Each has `id`, `title`, `celebration`, `category`, `emoji`, `earnedAtAge`, `requiredTaskSlugs`, `isAdult`. This is the source of truth.
- `lib/domain/mastery_evaluator.dart` — pure eval functions + sessionBox storage. `claimNewlyEarnedMasteries()` runs after each task completion and returns masteries just-earned (not previously earned). `earnedAt()` / `isAlreadyEarned()` for the Achievements screen.
- `lib/features/task/certificate_card.dart` — two widget designs. `categoryColor(category)` maps slug to brand color. QR code via `qr_flutter`.
- `lib/features/task/certificate_share.dart` — `SkillCertificatePreview` + `MasteryCertificatePreview` screens with capture & share.
- `lib/features/profile/achievements_screen.dart` — lists earned/in-progress/locked masteries with per-mastery share button.

**Earned masteries are stored in `sessionBox`** under keys like `mastery::{childId}::{masteryId}` (value: ISO earned-timestamp). Uses existing sessionBox rather than a new Hive adapter (simpler — no TypeId needed, no migration on upgrade).

**Trigger flow in `task_detail_screen.dart → _handleCompletion`:**
1. Task completed → progress saved → telemetry POST fires.
2. Celebration sheet shown with **Share Certificate** button → opens `SkillCertificatePreview`.
3. After sheet dismisses, `claimNewlyEarnedMasteries()` runs against all progress; any new mastery pushes a `MasteryCertificatePreview` in sequence.

**Adding a new mastery:** edit `masteries.dart`, add a `Mastery(...)` entry with valid `requiredTaskSlugs`. No backend change needed. Task slugs must exist in the live catalog (verify before shipping or the mastery will never trigger).

**Nginx `/smartstep` short URL** — configured by `docs/publishing/patch_nginx.py`. Two 302 redirects (`/smartstep` and `/smartstep/`) both go to Play Store with UTM params `utm_source=cert_share&utm_medium=whatsapp`. Used on every certificate QR code + caption.

---

## What is NOT yet done

- Push notifications: `ScheduledNotification` model exists, no send mechanism yet
- Gunicorn systemd service not yet active on VPS — service file at `docs/publishing/smartstep-backend.service`, install with `sudo cp … /etc/systemd/system/ && sudo systemctl enable --now smartstep-backend`
- Hive migration for existing installs when encryption/schema changes — current policy is "uninstall + reinstall"
- Play Console: 10 App-content declarations still in progress — Internal Testing release is live, Closed Testing needs 14-day opt-in with 20+ testers before Production
