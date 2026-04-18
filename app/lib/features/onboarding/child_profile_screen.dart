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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Add your child")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
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
                      "This information stays on this device only — encrypted and never uploaded.",
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
              decoration: const InputDecoration(labelText: "Name or nickname"),
            ),
            const SizedBox(height: 16),
            ListTile(
              title: Text(_dob == null
                  ? "Pick date of birth"
                  : "DOB: ${_dob!.toIso8601String().substring(0, 10)}"),
              trailing: const Icon(Icons.calendar_today),
              onTap: _pickDob,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<Sex>(
              value: _sex,
              items: const [
                DropdownMenuItem(value: Sex.girl, child: Text("Girl")),
                DropdownMenuItem(value: Sex.boy, child: Text("Boy")),
                DropdownMenuItem(
                    value: Sex.other, child: Text("Prefer not to say")),
              ],
              onChanged: (v) => setState(() => _sex = v!),
              decoration: const InputDecoration(labelText: "Sex"),
            ),
            const Spacer(),
            FilledButton(
              onPressed: _canSubmit ? _reviewAndSubmit : null,
              child: const Text("Next"),
            ),
          ],
        ),
      ),
    );
  }

  bool get _canSubmit => _name.text.trim().isNotEmpty && _dob != null;

  Future<void> _pickDob() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(now.year - 9, now.month, now.day),
      firstDate: DateTime(now.year - 16),
      lastDate: DateTime(now.year - 5),
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
            const Text(
              "The following details will be saved on this device only:",
              style: TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            _reviewRow("Name", _name.text.trim()),
            _reviewRow("Date of birth",
                _dob!.toIso8601String().substring(0, 10)),
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
              width: 90,
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
        Sex.boy => "Boy",
        Sex.girl => "Girl",
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
    );
    await HiveSetup.childBox.put(id, profile);
    if (!mounted) return;
    final addingParam = widget.adding ? '&adding=true' : '';
    context.go("/onboarding/environment?childId=$id$addingParam");
  }
}
