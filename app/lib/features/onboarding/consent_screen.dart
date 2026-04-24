import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/hive_setup.dart';

/// First screen in the onboarding flow. Satisfies the parental-consent and
/// privacy-notice obligations under the Indian DPDP Act 2023 and the Google
/// Play Store Families Policy: explicit, informed, age-gated consent before
/// any child-related data is entered or processed.
///
/// Consent is recorded in the (encrypted) session box under `consent_given`
/// so subsequent launches skip this screen.
class ConsentScreen extends StatefulWidget {
  const ConsentScreen({super.key});

  @override
  State<ConsentScreen> createState() => _ConsentScreenState();
}

class _ConsentScreenState extends State<ConsentScreen> {
  bool _isGuardian = false;
  bool _agreesToPolicy = false;

  bool get _canContinue => _isGuardian && _agreesToPolicy;

  Future<void> _accept() async {
    await HiveSetup.sessionBox.put('consent_given', '1');
    await HiveSetup.sessionBox.put(
      'consent_ts',
      DateTime.now().toIso8601String(),
    );
    if (!mounted) return;
    context.go('/signin');
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(22, 24, 22, 20),
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: cs.primaryContainer,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(
                Icons.shield_outlined,
                size: 36,
                color: cs.onPrimaryContainer,
              ),
            ),
            const SizedBox(height: 20),
            Text(
              "Welcome to SmartStep",
              style: Theme.of(context)
                  .textTheme
                  .headlineSmall
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              "Before you begin, please read how we handle your child's information.",
              style: Theme.of(context)
                  .textTheme
                  .bodyLarge
                  ?.copyWith(color: Colors.grey.shade700),
            ),
            const SizedBox(height: 24),
            _PromiseItem(
              icon: Icons.phonelink_lock_outlined,
              title: "Your child's data stays on this phone",
              body:
                  "Your child's name, date of birth, sex, and progress are stored only on this device. They are never uploaded to our servers.",
            ),
            _PromiseItem(
              icon: Icons.bar_chart_outlined,
              title: "Only anonymous counts are shared",
              body:
                  "When your child completes a skill, we record an anonymous tally (age band + environment + skill slug) to improve the app. No name, phone number, or child identifier is ever sent.",
            ),
            _PromiseItem(
              icon: Icons.block_outlined,
              title: "No ads, no tracking, no data sale",
              body:
                  "We do not show ads. We do not share your child's data with advertisers, brokers, or third parties. Ever.",
            ),
            _PromiseItem(
              icon: Icons.delete_sweep_outlined,
              title: "You can delete everything at any time",
              body:
                  "From Profile you can export your child's data or delete it permanently. Logging out wipes every trace from this device.",
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.description_outlined, size: 16),
                    label: const Text("Privacy Policy"),
                    onPressed: () => context.push('/legal/privacy'),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    icon: const Icon(Icons.article_outlined, size: 16),
                    label: const Text("Terms"),
                    onPressed: () => context.push('/legal/terms'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 22),
            _ConsentTile(
              value: _isGuardian,
              onChanged: (v) => setState(() => _isGuardian = v ?? false),
              label:
                  "I am the parent or legal guardian of this child and I am 18 years or older.",
            ),
            const SizedBox(height: 8),
            _ConsentTile(
              value: _agreesToPolicy,
              onChanged: (v) => setState(() => _agreesToPolicy = v ?? false),
              label:
                  "I have read and agree to SmartStep's Privacy Policy and Terms, and I consent to the processing of my child's information as described above.",
            ),
            const SizedBox(height: 28),
            FilledButton(
              onPressed: _canContinue ? _accept : null,
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 15),
                minimumSize: const Size.fromHeight(52),
              ),
              child: const Text(
                "Agree and Continue",
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              "By continuing, you confirm parental consent under the Digital Personal Data Protection Act 2023 and the Google Play Families Policy.",
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey.shade600,
                    fontSize: 11.5,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PromiseItem extends StatelessWidget {
  const _PromiseItem({
    required this.icon,
    required this.title,
    required this.body,
  });
  final IconData icon;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primaryContainer,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              icon,
              size: 20,
              color: Theme.of(context).colorScheme.onPrimaryContainer,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14.5,
                    fontWeight: FontWeight.w700,
                    height: 1.25,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  body,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade700,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ConsentTile extends StatelessWidget {
  const _ConsentTile({
    required this.value,
    required this.onChanged,
    required this.label,
  });
  final bool value;
  final ValueChanged<bool?> onChanged;
  final String label;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () => onChanged(!value),
      borderRadius: BorderRadius.circular(10),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Checkbox(
              value: value,
              onChanged: onChanged,
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(top: 11),
                child: Text(
                  label,
                  style: const TextStyle(fontSize: 13.5, height: 1.35),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
