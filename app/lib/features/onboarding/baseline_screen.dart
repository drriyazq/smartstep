import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../data/api/task_repository.dart';
import '../../data/local/active_child.dart';
import '../../data/local/child_profile.dart';
import '../../data/local/hive_setup.dart';
import '../../data/local/task_progress.dart';
import '../../domain/adult_baseline.dart';
import '../../domain/baseline.dart';

String _sexParam(Sex sex) => switch (sex) {
      Sex.boy => "male",
      Sex.girl => "female",
      Sex.other => "any",
    };

class BaselineScreen extends ConsumerStatefulWidget {
  const BaselineScreen({
    super.key,
    required this.childId,
    this.adding = false,
  });
  final String childId;
  final bool adding;

  @override
  ConsumerState<BaselineScreen> createState() => _State();
}

class _State extends ConsumerState<BaselineScreen> {
  // question index → answer (true = Yes, false = Not yet, null = unanswered)
  final _answers = <int, bool>{};
  bool _submitting = false;

  List<_BaselineQ> _questionsFor(ChildProfile p) {
    final age = p.ageOn(DateTime.now());
    if (p.isAdult) {
      return adultQuestionsForAge(age)
          .map((q) => _BaselineQ(
                category: q.category,
                categoryLabel: q.categoryLabel,
                tierLabel: q.tierLabel,
                tier: q.tier.index,
                prompt: q.prompt,
                bypassTasksUpToAge: q.bypassTasksUpToAge,
              ))
          .toList();
    }
    return questionsForAge(age)
        .map((q) => _BaselineQ(
              category: q.category,
              categoryLabel: q.categoryLabel,
              tierLabel: q.tierLabel,
              tier: q.tier.index,
              prompt: q.prompt,
              bypassTasksUpToAge: q.bypassTasksUpToAge,
            ))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    final child = HiveSetup.childBox.get(widget.childId)!;
    final questions = _questionsFor(child);

    if (questions.isEmpty) {
      return _buildNoQuestionsScreen(context, child.name, child.isAdult);
    }

    // Group by category for scannable display
    final byCategory = <String, List<({int index, _BaselineQ q})>>{};
    for (int i = 0; i < questions.length; i++) {
      byCategory
          .putIfAbsent(questions[i].category, () => [])
          .add((index: i, q: questions[i]));
    }

    final yesCount = _answers.values.where((v) => v == true).length;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Quick check-in"),
        actions: [
          TextButton(
            onPressed: _submitting ? null : _skipToDashboard,
            child: const Text("Skip"),
          ),
        ],
      ),
      body: _submitting
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text("Setting up the ladder…"),
                ],
              ),
            )
          : ListView(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 120),
              children: [
                Padding(
                  padding: const EdgeInsets.only(bottom: 18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        child.isAdult
                            ? "Where are you already strong?"
                            : "What can ${child.name} already do?",
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        child.isAdult
                            ? "Tick 'Yes' for areas you've already got handled — we'll skip those and focus on what's next. 'Not yet' or unanswered keeps them in your ladder."
                            : "Tick 'Yes' for skills they've already mastered — we'll skip those and focus on what's new. 'Not yet' or unanswered keeps them in the ladder.",
                        style: Theme.of(context)
                            .textTheme
                            .bodyMedium
                            ?.copyWith(color: Colors.grey.shade700),
                      ),
                    ],
                  ),
                ),
                for (final entry in byCategory.entries) ...[
                  Padding(
                    padding: const EdgeInsets.only(top: 14, bottom: 8),
                    child: Text(
                      entry.value.first.q.categoryLabel,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.w800,
                            color: Theme.of(context).colorScheme.primary,
                            letterSpacing: 0.3,
                          ),
                    ),
                  ),
                  for (final item in entry.value)
                    _QuestionCard(
                      question: item.q,
                      answer: _answers[item.index],
                      onYes: () => setState(() => _answers[item.index] = true),
                      onNo: () => setState(() => _answers[item.index] = false),
                    ),
                ],
              ],
            ),
      bottomNavigationBar: _submitting
          ? null
          : SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: FilledButton(
                  onPressed: _submit,
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: Text(
                    yesCount == 0
                        ? "Continue"
                        : "Continue — skip $yesCount skill group${yesCount == 1 ? '' : 's'}",
                    style: const TextStyle(
                        fontSize: 15, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ),
    );
  }

  Widget _buildNoQuestionsScreen(BuildContext context, String name, bool isAdult) {
    return Scaffold(
      appBar: AppBar(title: const Text("Quick check-in")),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.celebration_outlined,
                  size: 64, color: Colors.blueAccent),
              const SizedBox(height: 16),
              Text(
                isAdult ? "Ready to begin, $name!" : "Ready to start $name's journey!",
                style: Theme.of(context).textTheme.titleLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              Text(
                isAdult
                    ? "You're at the start of the adult ladder. We'll build up from the foundations."
                    : "We'll start with the foundational skills right from the beginning.",
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey.shade600,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              FilledButton(
                onPressed: _submitting ? null : _skipToDashboard,
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                      vertical: 14, horizontal: 32),
                ),
                child: const Text("Let's go"),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _skipToDashboard() async {
    if (widget.adding) {
      setActiveChild(
          ref.read(activeChildIdProvider.notifier), widget.childId);
    }
    if (!mounted) return;
    context.go("/dashboard");
  }

  Future<void> _submit() async {
    setState(() => _submitting = true);
    try {
      final child = HiveSetup.childBox.get(widget.childId)!;
      final questions = _questionsFor(child);

      // Collect Yes'd questions
      final yesQuestions = <_BaselineQ>[];
      for (final entry in _answers.entries) {
        if (entry.value == true && entry.key < questions.length) {
          yesQuestions.add(questions[entry.key]);
        }
      }

      if (yesQuestions.isNotEmpty) {
        final tasks = await ref.read(taskRepositoryProvider).fetchAll(
              environment: child.environment.name,
              sex: _sexParam(child.sex),
            );

        // Adult vs child: bypass applies only within the relevant age slice
        // so an adult "Yes" never touches child tasks and vice versa.
        bool inKindAgeRange(int taskMinAge) {
          if (child.isAdult) return taskMinAge >= 17;
          return taskMinAge <= 16;
        }

        for (final q in yesQuestions) {
          final matching = tasks.where((t) {
            final cat = t.tags.isEmpty ? 'other' : t.tags.first.category;
            return cat == q.category &&
                t.maxAge <= q.bypassTasksUpToAge &&
                inKindAgeRange(t.minAge);
          });
          for (final task in matching) {
            final key = TaskProgress.key(widget.childId, task.slug);
            if (HiveSetup.progressBox.get(key) != null) continue;
            await HiveSetup.progressBox.put(
              key,
              TaskProgress(
                taskSlug: task.slug,
                childId: widget.childId,
                status: ProgressStatus.bypassed,
              ),
            );
          }
        }
      }

      if (!mounted) return;
      if (widget.adding) {
        setActiveChild(
          ref.read(activeChildIdProvider.notifier),
          widget.childId,
        );
      }
      context.go("/dashboard");
    } catch (e) {
      if (!mounted) return;
      setState(() => _submitting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Couldn't save: $e")),
      );
    }
  }
}

/// View-model that unifies child + adult baseline questions so the UI and
/// submit code don't need two parallel paths.
class _BaselineQ {
  const _BaselineQ({
    required this.category,
    required this.categoryLabel,
    required this.tierLabel,
    required this.tier,
    required this.prompt,
    required this.bypassTasksUpToAge,
  });
  final String category;
  final String categoryLabel;
  final String tierLabel;
  final int tier;
  final String prompt;
  final int bypassTasksUpToAge;
}

class _QuestionCard extends StatelessWidget {
  const _QuestionCard({
    required this.question,
    required this.answer,
    required this.onYes,
    required this.onNo,
  });
  final _BaselineQ question;
  final bool? answer;
  final VoidCallback onYes;
  final VoidCallback onNo;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final tierColor = switch (question.tier) {
      0 => Colors.green.shade600,        // Basic
      1 => Colors.orange.shade700,       // Intermediate
      _ => Colors.purple.shade700,       // Advanced
    };
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: answer != null ? cs.primary : Colors.grey.shade300,
          width: answer != null ? 1.5 : 1,
        ),
        color: Colors.white,
      ),
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: tierColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              question.tierLabel,
              style: TextStyle(
                fontSize: 10.5,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.3,
                color: tierColor,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            question.prompt,
            style: const TextStyle(
              fontSize: 14.5,
              fontWeight: FontWeight.w500,
              height: 1.35,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _AnswerButton(
                  label: "Yes",
                  selected: answer == true,
                  color: Colors.green,
                  icon: Icons.check,
                  onTap: onYes,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _AnswerButton(
                  label: "Not yet",
                  selected: answer == false,
                  color: Colors.grey,
                  icon: Icons.radio_button_unchecked,
                  onTap: onNo,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _AnswerButton extends StatelessWidget {
  const _AnswerButton({
    required this.label,
    required this.selected,
    required this.color,
    required this.icon,
    required this.onTap,
  });
  final String label;
  final bool selected;
  final Color color;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: selected ? color.withOpacity(0.15) : Colors.grey.shade100,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: selected ? color : Colors.grey.shade300,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                selected ? Icons.check_circle : icon,
                size: 18,
                color: selected ? color : Colors.grey.shade500,
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: selected ? color : Colors.grey.shade700,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
