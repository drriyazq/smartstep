import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class TermsScreen extends StatelessWidget {
  const TermsScreen({super.key});

  static const _content = '''
# SmartStep Terms of Use

**Last updated:** April 2026

By using SmartStep you agree to these terms.

## 1. Who can use SmartStep

SmartStep is intended for **parents or legal guardians** aged 18 or over to use *with or on behalf of* their children aged 5–16. Children should not set up or use the app without an adult present. You confirm during onboarding that you meet these requirements.

## 2. How SmartStep works

SmartStep presents a curated ladder of real-life skills. You review each skill, decide whether it is appropriate for your child, and mark it as practised, skipped, or already known. The app is a guide for parent-led learning. It is **not** a substitute for supervision, professional education, medical advice, or safety training.

## 3. Your responsibilities

You are responsible for:
- Deciding which skills are right for your child
- Supervising your child during any skill practice, particularly those involving safety (roads, cooking, tools, travel, etc.)
- Protecting the device on which SmartStep is installed (the child's data lives only here)
- Keeping your parental consent current — if you no longer consent, log out to wipe all data

## 4. Safety disclaimer

Any skill that may pose physical risk includes a *Safety* section with clear cautions. You alone decide if and when your child is ready. SmartStep provides guidance, not certification. **We accept no liability for injury, loss, or damage arising from how skills are practised.**

## 5. Your child's data

We handle your child's data as described in the Privacy Policy. In particular:
- Your child's name, date of birth, sex and progress stay on your device only
- Only anonymous aggregates are sent to our servers
- You can export or delete the data at any time from Profile

## 6. Rewards

Rewards shown in the app are suggestions. They are not purchased or delivered by SmartStep. Any physical or experiential reward you provide to your child is your own choice and responsibility.

## 7. Content accuracy

We work hard to keep skill content accurate and age-appropriate. If you find content that is incorrect, outdated, or concerning, please report it to **drdentalmail@gmail.com**. We will review and act on reports within 7 days.

## 8. Account and sign-in

Sign-in uses a phone number + OTP via Google Firebase. You are responsible for keeping access to that phone number. If you lose access, you can set up the app again on a new device; local data does not transfer.

## 9. Changes

We may update these terms. The *Last updated* date will change and material changes will be announced in-app before they take effect. Continuing to use SmartStep after changes means you accept them. If you disagree, you can log out at any time to stop using the app.

## 10. Contact

**Email:** drdentalmail@gmail.com

For complaints, include the word *Terms* in the subject line. We acknowledge receipt within 7 days.
''';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Terms of Use")),
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
