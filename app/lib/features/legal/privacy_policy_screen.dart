import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  static const _content = '''
# SmartStep Privacy Policy

**Last updated:** April 2026
**Applies to:** SmartStep Android application

SmartStep is a parent-facilitated life-skills app for children aged 5–16. This policy explains what information we handle, where it is stored, and your rights under the Digital Personal Data Protection Act 2023 (India) and the Google Play Families Policy.

## 1. Who we are

SmartStep is published by the SmartStep team (an initiative of the owner of this device's account). You can reach us at **drdentalmail@gmail.com** for any privacy question, grievance, or data-rights request.

## 2. What information we handle

### On this device (never uploaded)
We store the following on your phone only, using encrypted local storage (AES-256 via Android Keystore):

- Your child's **name or nickname**
- Your child's **date of birth, sex**, and **living environment** (urban / suburban / rural)
- **Skill progress** — which skills your child has practised, mastered, or skipped
- **Reward choices** you select after completed skills
- **Custom tasks and rewards** you add yourself
- Your **parental consent** confirmation and timestamp

### Sent to our servers
- The **phone number** you enter is sent to Google Firebase Authentication solely to verify that you are the real owner via OTP, then exchanged for an app login token. We do not store your phone number outside of that.
- **Anonymous telemetry** when a skill is completed: the skill's identifier, your child's age band (e.g. "7–8"), and your child's environment. This is used only to improve which skills are surfaced. It contains no child name, phone number, child identifier, or precise date of birth.

### Never collected
- Location, contacts, camera, microphone, SMS content, or device storage
- Advertising identifiers
- Biometric data
- Photos, recordings, or writings of your child

## 3. Why we handle this information

1. To run the ladder of skills on your device (all on-device data)
2. To verify you are a real person during sign-in (phone OTP)
3. To improve the app for all families (anonymous telemetry only)

## 4. How long we keep it

- **On-device data:** stays until you delete it. You can delete individual children, reset progress, or log out at any time from the Profile screen.
- **Anonymous telemetry:** retained indefinitely in aggregate form, with no way to re-identify a child.
- **Phone number during authentication:** handled by Google Firebase under their terms. Firebase does not share it back to us as a usable identifier.

## 5. Your rights

Under the Digital Personal Data Protection Act 2023 (India), you have the right to:

- **Access** your child's data — use *Export my child's data* in Profile to download a JSON file of everything stored
- **Correct** any information — edit the child's profile or environment from Profile at any time
- **Erase** the data — delete individual children or log out to wipe everything
- **Withdraw consent** — logging out withdraws consent and erases all on-device data
- **Raise a grievance** — write to **drdentalmail@gmail.com** for any complaint. We will acknowledge within 7 days and respond within 30 days

## 6. Children's privacy

SmartStep is designed to be used *by parents or guardians on behalf of children*. No child ever creates an account or interacts with the app without an adult present. Parental consent is obtained explicitly before any child information is entered.

If you believe a child has set up the app without guardian consent, please contact us at **drdentalmail@gmail.com** and we will delete all associated data within 7 days.

## 7. Third-party services

SmartStep uses the following third-party services, each with their own privacy practices:

- **Google Firebase Authentication** — to send OTP and verify your phone number
- **Google Firebase Cloud Messaging** — reserved for future use to send important notifications (e.g. weekly practice reminders). Not active yet.

No advertising SDKs, analytics platforms, or data brokers are used.

## 8. Security

- All sensitive local data (your child's profile, auth tokens, progress) is encrypted at rest using AES-256 with a key held in the platform's secure keystore.
- Network traffic uses HTTPS with TLS 1.2 or higher.
- We follow Google Play's Data Safety standards.

## 9. Changes to this policy

If we update this policy, the *Last updated* date at the top will change. Material changes will be announced in-app before they take effect.

## 10. Contact

**Email:** drdentalmail@gmail.com

For privacy requests, please include:
- The word *Privacy* in the subject line
- Which child's data the request concerns (if applicable)
- The type of request (access / correct / delete / withdraw consent / grievance)

We acknowledge receipt within 7 days and respond fully within 30 days.
''';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Privacy Policy")),
      body: Markdown(
        data: _content,
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
        styleSheet: MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(
          p: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.55),
          h1: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
          h2: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
        ),
      ),
    );
  }
}
