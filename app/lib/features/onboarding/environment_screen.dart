import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';

class EnvironmentScreen extends ConsumerStatefulWidget {
  const EnvironmentScreen({
    super.key,
    required this.childId,
    this.adding = false,
  });
  final String childId;
  final bool adding;

  @override
  ConsumerState<EnvironmentScreen> createState() => _State();
}

class _State extends ConsumerState<EnvironmentScreen> {
  Environment _env = Environment.urban;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Where do you live?")),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text("We tailor tasks to your surroundings."),
            const SizedBox(height: 24),
            for (final env in Environment.values)
              RadioListTile<Environment>(
                title: Text(env.name[0].toUpperCase() + env.name.substring(1)),
                subtitle: Text(_describe(env)),
                value: env,
                groupValue: _env,
                onChanged: (v) => setState(() => _env = v!),
              ),
            const Spacer(),
            FilledButton(onPressed: _submit, child: const Text("Continue")),
          ],
        ),
      ),
    );
  }

  String _describe(Environment env) {
    switch (env) {
      case Environment.urban:
        return "City with public transit, shops close by";
      case Environment.suburban:
        return "Quieter streets, mostly walkable";
      case Environment.rural:
        return "Countryside or small village";
    }
  }

  Future<void> _submit() async {
    final existing = HiveSetup.childBox.get(widget.childId)!;
    await HiveSetup.childBox.put(
      widget.childId,
      ChildProfile(
        id: existing.id,
        name: existing.name,
        dob: existing.dob,
        sex: existing.sex,
        environment: _env,
      ),
    );
    if (!mounted) return;
    final addingParam = widget.adding ? '&adding=true' : '';
    context.go("/onboarding/baseline?childId=${widget.childId}$addingParam");
  }
}
