import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';

class ChildProfileScreen extends ConsumerStatefulWidget {
  const ChildProfileScreen({super.key, this.adding = false});
  final bool adding;

  @override
  ConsumerState<ChildProfileScreen> createState() => _State();
}

class _State extends ConsumerState<ChildProfileScreen> {
  final _name = TextEditingController();
  DateTime? _dob;
  Sex _sex = Sex.other;
  ProfileKind _kind = ProfileKind.child;

  bool get _isAdult => _kind == ProfileKind.adult;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isAdult ? "Set up your profile" : "Add your child"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(22, 22, 22, 22),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _KindToggle(
                value: _kind,
                onChanged: (k) => setState(() {
                  _kind = k;
                  _dob = null; // different valid ranges — force re-pick
                }),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.lock_outline,
                        size: 18, color: Colors.green.shade700),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        "This stays on this device only — encrypted and never uploaded.",
                        style: TextStyle(
                          fontSize: 12.5,
                          color: Colors.green.shade900,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 22),
              TextField(
                controller: _name,
                textCapitalization: TextCapitalization.words,
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: _isAdult ? "Your name" : "Name or nickname",
                ),
              ),
              const SizedBox(height: 16),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(_dob == null
                    ? (_isAdult ? "Pick your date of birth" : "Pick date of birth")
                    : "DOB: ${_dob!.toIso8601String().substring(0, 10)}"),
                trailing: const Icon(Icons.calendar_today),
                onTap: _pickDob,
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<Sex>(
                value: _sex,
                items: _isAdult
                    ? const [
                        DropdownMenuItem(
                            value: Sex.girl, child: Text("Female")),
                        DropdownMenuItem(value: Sex.boy, child: Text("Male")),
                        DropdownMenuItem(
                            value: Sex.other, child: Text("Prefer not to say")),
                      ]
                    : const [
                        DropdownMenuItem(value: Sex.girl, child: Text("Girl")),
                        DropdownMenuItem(value: Sex.boy, child: Text("Boy")),
                        DropdownMenuItem(
                            value: Sex.other, child: Text("Prefer not to say")),
                      ],
                onChanged: (v) => setState(() => _sex = v!),
                decoration: const InputDecoration(labelText: "Sex"),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(22, 8, 22, 12),
          child: FilledButton(
            onPressed: _canSubmit ? _reviewAndSubmit : null,
            style: FilledButton.styleFrom(
              minimumSize: const Size.fromHeight(48),
            ),
            child: const Text("Next"),
          ),
        ),
      ),
    );
  }

  bool get _canSubmit => _name.text.trim().isNotEmpty && _dob != null;

  Future<void> _pickDob() async {
    final now = DateTime.now();
    final initialYears = _isAdult ? 30 : 9;
    final minYears = _isAdult ? 18 : 5;
    final maxYears = _isAdult ? 80 : 16;
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(now.year - initialYears, now.month, now.day),
      firstDate: DateTime(now.year - maxYears),
      lastDate: DateTime(now.year - minYears),
    );
    if (picked != null) setState(() => _dob = picked);
  }

  Future<void> _reviewAndSubmit() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Review before saving"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _isAdult
                  ? "The following will be saved on this device only:"
                  : "The following details will be saved on this device only:",
              style: const TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            _reviewRow("Profile type",
                _isAdult ? "Adult (yourself)" : "Child"),
            _reviewRow("Name", _name.text.trim()),
            _reviewRow(
                "Date of birth", _dob!.toIso8601String().substring(0, 10)),
            _reviewRow("Sex", _sexLabel(_sex)),
            const SizedBox(height: 10),
            Text(
              "You can edit or delete this at any time from Profile.",
              style: TextStyle(
                fontSize: 11.5,
                color: Colors.grey.shade600,
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Go back"),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text("Save"),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    await _submit();
  }

  Widget _reviewRow(String label, String value) => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: 100,
              child: Text(
                label,
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey.shade600,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            Expanded(
              child: Text(
                value,
                style: const TextStyle(
                    fontSize: 13, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
      );

  String _sexLabel(Sex s) => switch (s) {
        Sex.boy => _isAdult ? "Male" : "Boy",
        Sex.girl => _isAdult ? "Female" : "Girl",
        Sex.other => "Prefer not to say",
      };

  Future<void> _submit() async {
    final id = DateTime.now().microsecondsSinceEpoch.toString();
    final profile = ChildProfile(
      id: id,
      name: _name.text.trim(),
      dob: _dob!,
      sex: _sex,
      environment: Environment.urban, // picked on the next screen
      kind: _kind,
    );
    await HiveSetup.childBox.put(id, profile);
    if (!mounted) return;
    final addingParam = widget.adding ? '&adding=true' : '';
    context.go("/onboarding/environment?childId=$id$addingParam");
  }
}

class _KindToggle extends StatelessWidget {
  const _KindToggle({required this.value, required this.onChanged});
  final ProfileKind value;
  final ValueChanged<ProfileKind> onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Who is this profile for?",
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
                color: Colors.grey.shade700,
              ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: _KindCard(
                icon: Icons.child_care_outlined,
                title: "My child",
                subtitle: "Age 5–16",
                selected: value == ProfileKind.child,
                onTap: () => onChanged(ProfileKind.child),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: _KindCard(
                icon: Icons.person_outline,
                title: "Myself",
                subtitle: "Age 18+",
                selected: value == ProfileKind.adult,
                onTap: () => onChanged(ProfileKind.adult),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _KindCard extends StatelessWidget {
  const _KindCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.selected,
    required this.onTap,
  });
  final IconData icon;
  final String title;
  final String subtitle;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
          decoration: BoxDecoration(
            color: selected ? cs.primaryContainer : Colors.grey.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: selected ? cs.primary : Colors.grey.shade300,
              width: selected ? 1.8 : 1,
            ),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                size: 28,
                color: selected ? cs.onPrimaryContainer : Colors.grey.shade700,
              ),
              const SizedBox(height: 6),
              Text(
                title,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color:
                      selected ? cs.onPrimaryContainer : Colors.black87,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 11.5,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
