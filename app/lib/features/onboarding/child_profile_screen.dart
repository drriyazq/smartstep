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
            const Text("This information stays on this device only."),
            const SizedBox(height: 24),
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
                DropdownMenuItem(value: Sex.other, child: Text("Prefer not to say")),
              ],
              onChanged: (v) => setState(() => _sex = v!),
              decoration: const InputDecoration(labelText: "Sex"),
            ),
            const Spacer(),
            FilledButton(
              onPressed: _canSubmit ? _submit : null,
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
