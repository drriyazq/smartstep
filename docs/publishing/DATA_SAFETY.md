# Play Console — Data Safety Form Answers

Answer these exactly when filling the **Data Safety** section in the Play Console. Every answer below reflects the app as built (AES-256 on-device, anonymous telemetry only, no third-party sharing).

---

## Does your app collect or share any of the required user data types?
**Yes** — phone number (for auth) and anonymous usage/diagnostics.

---

## Is all of the user data collected by your app encrypted in transit?
**Yes.** All API traffic uses HTTPS with TLS 1.2+. Firebase Auth is HTTPS by default.

## Do you provide a way for users to request that their data is deleted?
**Yes.** From the Profile screen a user can:
- Export their child's data (JSON via share sheet)
- Delete a specific child's data
- Log out (wipes all local data)
- Contact `drdentalmail@gmail.com` for server-side requests (there is no server-side personal data)

---

## Data types collected

### Personal info

| Data type | Collected? | Required/Optional | Purpose | Shared with third parties? | Encrypted in transit? | User can request deletion? |
|---|---|---|---|---|---|---|
| Name | **Not collected by server** — stored only on the device | — | — | No | N/A (never leaves device) | Yes (user deletes locally) |
| Email address | Not collected | — | — | — | — | — |
| User IDs | Not collected (no child identifier sent to server) | — | — | — | — | — |
| Phone number | Collected briefly during Firebase Auth OTP verification | Required | App functionality (authentication) | No | Yes | Yes — contact us |

### Health & fitness
- None collected

### Financial info
- None collected

### Location
- None collected

### Messages
- None collected (app does not read SMS, contacts, or any messages)

### Photos and videos
- None collected

### Files and docs
- None collected

### Calendar, Contacts, Call logs
- None collected

### App activity

| Data type | Collected? | Purpose |
|---|---|---|
| App interactions | Yes — anonymous (task slug + age band + environment on skill completion) | Analytics |
| In-app search history | Not collected |
| Installed apps | Not collected |
| Other user-generated content | Not collected |

### Device or other IDs
- **Not collected** (we don't use advertising ID or device ID)

### Diagnostics (Firebase Crashlytics)

| Data type | Collected? | Purpose | Required? |
|---|---|---|---|
| Crash logs | Yes | Crash diagnostics — fix stability issues | Optional; collected only in release builds |
| Diagnostics | Yes (same — crash stack traces) | App functionality + performance | Optional |

Firebase Crashlytics collects: device model, OS version, app version, crash stack trace. NO user-identifying fields are logged.

---

## Data sharing

**Do you share any of the collected data with third parties?**

**No** — we do not share user data with third parties for advertising, analytics, or any other purpose.

Firebase (Auth, Messaging, Crashlytics, Analytics) acts as a **service provider**, not a third party. Data sent to Firebase is covered by Google's Firebase Privacy Terms and is not shared beyond them.

---

## Security practices

- Data is encrypted in transit (HTTPS / TLS 1.2+)
- Sensitive on-device data (child profile, auth tokens, progress) is encrypted at rest with AES-256 using a key stored in Android Keystore
- Users can request data deletion (in-app per-child delete, full logout, email request for any server-side data)
- Data collection follows Play Families Policy for children's apps
- Independent security review: not yet

---

## Target audience & content

### Who is this app primarily for?
**Mixed audience** — designed for children (age 5+) with parental facilitation AND adults (18+) who use it independently. The app gates content by profile kind: child profiles see only age-appropriate child content; adult profiles see only adult content.

### Does your app include content appropriate for children?
**Yes** — approximately 400 skills target children aged 5–16, always under parent facilitation (the app requires parental consent before any child profile can be created).

### Children's ads policy
- No ads in the app
- No personalised data used for any purpose
- No user-generated content / user-to-user communication
- Parental consent required before child profile creation
- All Firebase services used (Auth, Messaging, Crashlytics, Analytics) are Families Policy compliant

---

## Ads declaration

**Does your app contain ads?** No.

---

## App Access
If login required: the Play review team can use any phone number + OTP `000000` to sign in (dev credentials). **Remove this hint before final production submission** — it's only needed for Internal/Closed testing.

Add as a reviewer note:
```
Internal Testing access:
- Tap "Agree and Continue" on the consent screen
- Enter any 10-digit Indian phone number + OTP 000000
- Create a child or adult profile to enter the app
```
