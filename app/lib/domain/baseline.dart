/// Category-based baseline assessment.
///
/// Each question represents a competency level within a category. A "Yes"
/// answer marks ALL tasks in that category with `max_age <= bypassTasksUpToAge`
/// as `bypassed` — letting the child skip content they've already mastered.
///
/// Questions are filtered by the child's age via [questionsForAge]:
///   - Basic  (bypass ≤ 8):  shown for age 7+
///   - Intermediate (≤ 11):  shown for age 10+
///   - Advanced (≤ 14):      shown for age 13+
///
/// Children aged 5–6 see no questions (they're at the start of the ladder).

enum BaselineTier { basic, intermediate, advanced }

class BaselineQuestion {
  const BaselineQuestion({
    required this.category,
    required this.categoryLabel,
    required this.tier,
    required this.prompt,
    required this.bypassTasksUpToAge,
    required this.minChildAge,
  });
  final String category;
  final String categoryLabel;
  final BaselineTier tier;
  final String prompt;
  final int bypassTasksUpToAge;
  final int minChildAge;

  String get tierLabel => switch (tier) {
        BaselineTier.basic => 'Basic',
        BaselineTier.intermediate => 'Intermediate',
        BaselineTier.advanced => 'Advanced',
      };
}

const baselineQuestions = <BaselineQuestion>[
  // ── FINANCIAL ──────────────────────────────────────────────────────
  BaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: BaselineTier.basic,
    prompt:
        "Knows money is used to buy things, tells coins from notes, recognises common coins.",
    bypassTasksUpToAge: 8,
    minChildAge: 7,
  ),
  BaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: BaselineTier.intermediate,
    prompt:
        "Counts change, reads price tags, saves pocket money, tells needs from wants.",
    bypassTasksUpToAge: 11,
    minChildAge: 10,
  ),
  BaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: BaselineTier.advanced,
    prompt:
        "Budgets pocket money, compares prices online, understands digital payments.",
    bypassTasksUpToAge: 14,
    minChildAge: 13,
  ),

  // ── HOUSEHOLD ──────────────────────────────────────────────────────
  BaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: BaselineTier.basic,
    prompt:
        "Brushes teeth, washes hands, dresses themselves, makes their bed, pours own drink.",
    bypassTasksUpToAge: 8,
    minChildAge: 7,
  ),
  BaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: BaselineTier.intermediate,
    prompt:
        "Showers thoroughly, follows a simple recipe, hangs laundry, sets the table.",
    bypassTasksUpToAge: 11,
    minChildAge: 10,
  ),
  BaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: BaselineTier.advanced,
    prompt:
        "Cooks simple meals, uses the washing machine, cleans a room properly, changes bed sheets.",
    bypassTasksUpToAge: 14,
    minChildAge: 13,
  ),

  // ── SOCIAL ─────────────────────────────────────────────────────────
  BaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: BaselineTier.basic,
    prompt:
        "Uses please and thank you, greets adults, shares toys, says sorry when needed.",
    bypassTasksUpToAge: 8,
    minChildAge: 7,
  ),
  BaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: BaselineTier.intermediate,
    prompt:
        "Listens without interrupting, apologises sincerely, asks adults for help, accepts compliments.",
    bypassTasksUpToAge: 11,
    minChildAge: 10,
  ),
  BaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: BaselineTier.advanced,
    prompt:
        "Disagrees respectfully, resolves conflicts, handles teasing calmly, writes thank-you notes.",
    bypassTasksUpToAge: 14,
    minChildAge: 13,
  ),

  // ── DIGITAL ────────────────────────────────────────────────────────
  BaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: BaselineTier.basic,
    prompt:
        "Opens and closes apps, adjusts volume, knows not to share personal info online.",
    bypassTasksUpToAge: 8,
    minChildAge: 7,
  ),
  BaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: BaselineTier.intermediate,
    prompt:
        "Searches with good keywords, ignores ads and popups, sends a basic email.",
    bypassTasksUpToAge: 11,
    minChildAge: 10,
  ),
  BaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: BaselineTier.advanced,
    prompt:
        "Creates strong passwords, spots phishing and misinformation, uses spreadsheets.",
    bypassTasksUpToAge: 14,
    minChildAge: 13,
  ),

  // ── NAVIGATION ─────────────────────────────────────────────────────
  BaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: BaselineTier.basic,
    prompt:
        "Knows home address and parents' full names, holds hand at roads, stays close in busy places.",
    bypassTasksUpToAge: 8,
    minChildAge: 7,
  ),
  BaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: BaselineTier.intermediate,
    prompt:
        "Reads road signs, walks to a friend's house alone, uses public transport with a parent.",
    bypassTasksUpToAge: 11,
    minChildAge: 10,
  ),
  BaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: BaselineTier.advanced,
    prompt:
        "Travels on public transport solo, uses map apps, plans a day trip independently.",
    bypassTasksUpToAge: 14,
    minChildAge: 13,
  ),

  // ── COGNITIVE ──────────────────────────────────────────────────────
  BaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: BaselineTier.basic,
    prompt:
        "Counts, names shapes, follows two-step instructions, remembers a short list of items.",
    bypassTasksUpToAge: 8,
    minChildAge: 7,
  ),
  BaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: BaselineTier.intermediate,
    prompt:
        "Tells analog time, uses a calendar, makes pros-cons lists, summarises a story.",
    bypassTasksUpToAge: 11,
    minChildAge: 10,
  ),
  BaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: BaselineTier.advanced,
    prompt:
        "Takes structured notes, participates in debates, applies the scientific method.",
    bypassTasksUpToAge: 14,
    minChildAge: 13,
  ),
];

/// Returns only the questions appropriate for a child of the given age.
List<BaselineQuestion> questionsForAge(int childAge) =>
    baselineQuestions.where((q) => q.minChildAge <= childAge).toList();
