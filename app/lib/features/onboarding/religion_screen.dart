import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';

/// Religion opt-in picker shown during onboarding (right after the
/// environment screen). Users who opt in pick one of the five most-populous
/// world religions; the pick is saved on-device in ChildProfile.religion.
/// Religion is optional — the default is "no thanks" and most of the app
/// works the same either way.
class ReligionScreen extends ConsumerStatefulWidget {
  const ReligionScreen({
    super.key,
    required this.childId,
    this.adding = false,
  });
  final String childId;
  final bool adding;

  @override
  ConsumerState<ReligionScreen> createState() => _ReligionScreenState();
}

class _Religion {
  const _Religion({required this.id, required this.label, required this.emoji});
  final String id;
  final String label;
  final String emoji;
}

const _religions = <_Religion>[
  _Religion(id: "christianity", label: "Christianity", emoji: "✝️"),
  _Religion(id: "islam",        label: "Islam",        emoji: "☪️"),
  _Religion(id: "hinduism",     label: "Hinduism",     emoji: "🕉️"),
  _Religion(id: "buddhism",     label: "Buddhism",     emoji: "☸️"),
  _Religion(id: "sikhism",      label: "Sikhism",      emoji: "🪯"),
];

class _ReligionScreenState extends ConsumerState<ReligionScreen> {
  bool? _optedIn;        // null = undecided, true/false = chosen
  String? _selectedId;   // id of selected religion when opted in

  @override
  Widget build(BuildContext context) {
    final existing = HiveSetup.childBox.get(widget.childId)!;
    final isAdult = existing.isAdult;
    final whoLabel = isAdult ? "yourself" : existing.name;

    return Scaffold(
      appBar: AppBar(title: const Text("Faith & values")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              isAdult
                  ? "Would you like to include religion-based practices in your growth?"
                  : "Would you like $whoLabel to include religion-based practices in their growth?",
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              "Optional. We'll add tasks rooted in your chosen tradition alongside the regular ones. You can change this later in Profile.",
              style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 20),

            // Yes / No toggle
            Row(
              children: [
                Expanded(
                  child: _ChoiceButton(
                    label: "Yes, add faith-based tasks",
                    selected: _optedIn == true,
                    onTap: () => setState(() => _optedIn = true),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _ChoiceButton(
                    label: "No thanks",
                    selected: _optedIn == false,
                    onTap: () => setState(() {
                      _optedIn = false;
                      _selectedId = null;
                    }),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Religion picker — only shown once user says yes
            if (_optedIn == true) ...[
              Text(
                "Pick your tradition",
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 10),
              Expanded(
                child: ListView.separated(
                  itemCount: _religions.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (_, i) {
                    final r = _religions[i];
                    final selected = _selectedId == r.id;
                    return _ReligionTile(
                      religion: r,
                      selected: selected,
                      onTap: () => setState(() => _selectedId = r.id),
                    );
                  },
                ),
              ),
            ] else
              const Spacer(),

            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _canContinue ? _submit : null,
                child: const Text("Continue"),
              ),
            ),
          ],
        ),
      ),
    );
  }

  bool get _canContinue {
    if (_optedIn == null) return false;
    if (_optedIn == true && _selectedId == null) return false;
    return true;
  }

  Future<void> _submit() async {
    final existing = HiveSetup.childBox.get(widget.childId)!;
    final optedIn = _optedIn == true;
    final updated = existing.copyWith(
      religionInterest: optedIn,
      religion: optedIn ? _selectedId : null,
      clearReligion: !optedIn,
    );
    await HiveSetup.childBox.put(widget.childId, updated);
    if (!mounted) return;
    final addingParam = widget.adding ? '&adding=true' : '';
    context.go("/onboarding/baseline?childId=${widget.childId}$addingParam");
  }
}

class _ChoiceButton extends StatelessWidget {
  const _ChoiceButton({
    required this.label,
    required this.selected,
    required this.onTap,
  });
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Material(
      color: selected ? scheme.primary : Colors.grey.shade100,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: selected ? Colors.white : Colors.black87,
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
        ),
      ),
    );
  }
}

class _ReligionTile extends StatelessWidget {
  const _ReligionTile({
    required this.religion,
    required this.selected,
    required this.onTap,
  });
  final _Religion religion;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Material(
      color: selected
          ? scheme.primary.withOpacity(0.08)
          : Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: selected ? scheme.primary : Colors.grey.shade200,
          width: selected ? 1.6 : 1,
        ),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
          child: Row(
            children: [
              Text(religion.emoji, style: const TextStyle(fontSize: 22)),
              const SizedBox(width: 14),
              Expanded(
                child: Text(
                  religion.label,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              if (selected)
                Icon(Icons.check_circle,
                    color: scheme.primary, size: 22),
            ],
          ),
        ),
      ),
    );
  }
}
