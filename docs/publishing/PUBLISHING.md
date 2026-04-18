# Publishing SmartStep — End-to-End Checklist

A linear walk-through from today's state to a live Internal Testing release, then Closed Testing.

---

## Phase 1 — One-time setup (~2 hours)

### 1.1 Generate the upload keystore (on Windows)

```bat
cd smartstep\app\android
make-keystore.bat
```

This creates `%USERPROFILE%\smartstep-upload.jks` and prints instructions for `key.properties`.

**Back it up to two places.** If you lose the keystore, Play Store will never accept an update again — you'd have to publish under a new package name and rebuild your user base.

### 1.2 Create `android/key.properties`

Copy `android/key.properties.template` → `android/key.properties` and fill in the real values. Already gitignored.

### 1.3 Enable Firebase Crashlytics in Firebase Console

1. Go to <https://console.firebase.google.com/> → SmartStep project
2. Build → **Crashlytics** → **Get started**
3. No code changes needed — we already added the plugin + SDK

**Note:** Crashlytics collects data only in release builds (guarded by `kReleaseMode` in `main.dart`). Debug/profile runs are silent.

### 1.4 Host Privacy Policy + Terms on `areafair.in`

Upload these two files to your web server:
- `docs/publishing/hosted/privacy.html` → `areafair.in/smartstep/privacy/index.html`
- `docs/publishing/hosted/terms.html` → `areafair.in/smartstep/terms/index.html`

Verify both render at:
- <https://areafair.in/smartstep/privacy/>
- <https://areafair.in/smartstep/terms/>

### 1.5 Deploy Gunicorn on the VPS (backend stability)

```bash
# On the VPS
cd /home/drriyazq/smartstep/backend
venv/bin/pip install gunicorn

# Stop runserver
pkill -f "manage.py runserver 0.0.0.0:8001"

# Install systemd unit
sudo cp /home/drriyazq/smartstep/docs/publishing/smartstep-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smartstep-backend
sudo systemctl start smartstep-backend

# Verify
sudo systemctl status smartstep-backend
curl -s https://areafair.in/smartstep-admin/api/v1/tasks/ | head -c 200
```

---

## Phase 2 — Build the release bundle (~15 minutes)

### 2.1 Sync + build

```bat
cd smartstep
sync.bat

cd app
flutter pub get
flutter build appbundle --release
```

Output: `app\build\app\outputs\bundle\release\app-release.aab`

### 2.2 Smoke test the release APK on your phone first

Don't upload the AAB to Play Store before you've confirmed the release build actually runs. The release build has ProGuard/R8 minification enabled, which sometimes breaks reflection-based code that worked in debug.

```bat
cd app
flutter build apk --release
flutter install --release
```

Then run through the full flow on your phone: consent → OTP → create child profile → baseline → dashboard → open a task → complete a practice. If anything crashes, check `adb logcat | grep Flutter` and fix before uploading.

---

## Phase 3 — Play Console submission (~2–3 hours for Internal Testing)

### 3.1 Create the Play Console app

1. <https://play.google.com/console/> → **Create app**
2. App name: `SmartStep — Life Skills for Kids & Adults` (or the 30-char variant)
3. Default language: English (India)
4. App or game: **App**
5. Free or paid: **Free**
6. Declarations: accept both Developer Program Policies and US export laws

### 3.2 Fill the dashboard setup tasks (left sidebar)

- **App access** — follow `DATA_SAFETY.md` ("App Access" section; mention the dev OTP `000000`)
- **Ads** — No ads
- **Content rating** — fill the IARC questionnaire using `CONTENT_RATING.md`
- **Target audience and content** — Mixed audience; select age groups **5–12** and **18+**; confirm parental gate is in place; declare Firebase SDKs as families-policy-compliant
- **News app** — No
- **COVID-19 contact tracing** — No
- **Data safety** — copy answers from `DATA_SAFETY.md`
- **Government apps** — No
- **Financial features** — No (educational content only; no actual transactions)
- **Health** — No
- **Privacy policy URL** — `https://areafair.in/smartstep/privacy/`

### 3.3 Store listing

Use content from `STORE_LISTING.md`:
- App icon, feature graphic, screenshots → upload the assets you created
- Short description, full description → paste
- Support email → `drdentalmail@gmail.com`
- Website → `https://areafair.in/smartstep/`
- Category → Education

### 3.4 Create the Internal Testing release

1. **Testing → Internal testing → Create new release**
2. **Upload** `app-release.aab`
3. **Release name**: `0.1.0 (Internal)` (auto-populates from versionName)
4. **Release notes**:
    ```
    Initial internal testing release.
    - Child and adult life-skill ladders (6 categories)
    - Parental consent + AES-256 on-device encryption
    - Anonymous telemetry only
    - Firebase Auth (OTP), Crashlytics, Analytics
    Please test the full onboarding flow and report any crashes or UI overflow.
    ```
5. **Testers** — create a "Smartstep Internal" list; add 2–3 Google accounts you control
6. **Review release** → **Start rollout to Internal testing**

Google reviews this typically within a few hours. You'll get an email when it's live.

### 3.5 Share the opt-in link

Once approved, Play Console shows an opt-in URL. Send it to testers. They click it, accept the invitation, and install SmartStep from the Play Store (not the APK).

---

## Phase 4 — Moving to Closed Testing (~1 week later)

Prerequisites met? Check the additional items in `CLOSED_TESTING_CHECKLIST.md` (after 7+ days of stable internal testing):

1. Zero unresolved crashes in Crashlytics for 7 days
2. At least 3 different Android versions / OEMs tested
3. Target audience & content questionnaire passes (no warnings)
4. 20+ real testers added to the Closed track (required if you want to graduate to Production later)
5. Backend healthy under load (check `systemctl status smartstep-backend` + Nginx access logs)

### Then:

1. **Testing → Closed testing → Create track** (name: "Beta")
2. Promote the reviewed Internal release, OR upload a fresh `0.2.0 (Closed)` release
3. Add the 20+ testers
4. Fill any newly-triggered policy questions
5. Roll out

---

## Files in this directory

| File | Purpose |
|---|---|
| `STORE_LISTING.md` | Copy-paste content for Play Console store listing |
| `DATA_SAFETY.md` | Exact answers for the Data Safety form |
| `CONTENT_RATING.md` | Exact answers for the IARC questionnaire |
| `hosted/privacy.html` | Privacy Policy to upload to your web server |
| `hosted/terms.html` | Terms of Use to upload to your web server |
| `smartstep-backend.service` | systemd unit for production Gunicorn |
| `PUBLISHING.md` | This file |

---

## Things that will bite you (common mistakes)

1. **Forgetting to back up the keystore** — do it twice, in different places (cloud + USB). This is the single most catastrophic mistake.
2. **Uploading the debug AAB** — always `--release`. The debug build won't even be accepted.
3. **Skipping the release-APK smoke test** — ProGuard can break reflection paths that worked in debug. Test first.
4. **Not deploying Gunicorn** — `runserver` dies under concurrent tester load and the support emails arrive.
5. **Using `com.example.*` as package name** — already fixed; our package is `com.smartstep.app`.
6. **Forgetting to enable Crashlytics in Firebase Console** — SDK is installed but you must click "Get started" in the Firebase dashboard or the uploads are dropped.
