import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/baseline.dart';

class BaselineScreen extends ConsumerStatefulWidget {
  const BaselineScreen({super.key, required this.childId});
  final String childId;

  @override
  ConsumerState<BaselineScreen> createState() => _State();
}

class _State extends ConsumerState<BaselineScreen> {
  final _answers = <int, bool>{};

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Quick check-in")),
      body: ListView.builder(
        padding: const EdgeInsets.all(24),
        itemCount: baselineQuestions.length + 1,
        itemBuilder: (context, i) {
          if (i == baselineQuestions.length) {
            return Padding(
              padding: const EdgeInsets.only(top: 24),
              child: FilledButton(
                onPressed: _answers.length == baselineQuestions.length
                    ? _submit
                    : null,
                child: const Text("Start my child's ladder"),
              ),
            );
          }
          final q = baselineQuestions[i];
          final answer = _answers[i];
          return Card(
            margin: const EdgeInsets.symmetric(vertical: 8),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(q.prompt, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => setState(() => _answers[i] = true),
                          style: OutlinedButton.styleFrom(
                            backgroundColor: answer == true
                                ? Theme.of(context).colorScheme.primaryContainer
                                : null,
                          ),
                          child: const Text("Yes"),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => setState(() => _answers[i] = false),
                          style: OutlinedButton.styleFrom(
                            backgroundColor: answer == false
                                ? Theme.of(context).colorScheme.primaryContainer
                                : null,
                          ),
                          child: const Text("Not yet"),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Future<void> _submit() async {
    for (final entry in _answers.entries) {
      if (entry.value != true) continue;
      for (final slug in baselineQuestions[entry.key].bypassSlugs) {
        final key = TaskProgress.key(widget.childId, slug);
        await HiveSetup.progressBox.put(
          key,
          TaskProgress(
            taskSlug: slug,
            childId: widget.childId,
            status: ProgressStatus.bypassed,
          ),
        );
      }
    }
    if (!mounted) return;
    context.go("/dashboard");
  }
}
