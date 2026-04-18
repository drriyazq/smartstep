/// Category-based baseline assessment for ADULT profiles.
///
/// Mirrors the child baseline in shape (category × tier), but the prompts
/// and age ceilings target adult life-stage competencies:
///   - Basic:        up to max_age 30  → shown for age 20+
///   - Intermediate: up to max_age 45  → shown for age 28+
///   - Advanced:     up to max_age 99  → shown for age 36+
///
/// A "Yes" answer marks ALL adult tasks in that category with
/// max_age <= bypassTasksUpToAge as `bypassed`.
enum AdultTier { basic, intermediate, advanced }

class AdultBaselineQuestion {
  const AdultBaselineQuestion({
    required this.category,
    required this.categoryLabel,
    required this.tier,
    required this.prompt,
    required this.bypassTasksUpToAge,
    required this.minUserAge,
  });
  final String category;
  final String categoryLabel;
  final AdultTier tier;
  final String prompt;
  final int bypassTasksUpToAge;
  final int minUserAge;

  String get tierLabel => switch (tier) {
        AdultTier.basic => 'Basic',
        AdultTier.intermediate => 'Intermediate',
        AdultTier.advanced => 'Advanced',
      };
}

const adultBaselineQuestions = <AdultBaselineQuestion>[
  // ── FINANCIAL ──────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.basic,
    prompt:
        "You have an emergency fund and have started a monthly SIP / recurring savings.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.intermediate,
    prompt:
        "You read your payslip, file your own taxes, and hold appropriate health + term insurance.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.advanced,
    prompt:
        "You have a written will, nominees set everywhere, and a long-term investment plan.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
  ),

  // ── HOUSEHOLD ──────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.basic,
    prompt:
        "You can cook a simple meal, do your own laundry, and run the basics of a flat solo.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.intermediate,
    prompt:
        "You meal-plan a week, fix simple things yourself (fuse, tap, lock), and manage house help fairly.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.advanced,
    prompt:
        "You can host 10 people for a meal, handle landlord disputes, and have an emergency home kit ready.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
  ),

  // ── SOCIAL ─────────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.basic,
    prompt:
        "You can introduce yourself to strangers, make small talk, and ask for help without anxiety.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.intermediate,
    prompt:
        "You can have difficult conversations, set boundaries with family, and give honest feedback at work.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.advanced,
    prompt:
        "You mentor someone, repair broken relationships, and handle workplace conflict decisively.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
  ),

  // ── DIGITAL ────────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.basic,
    prompt:
        "You use a password manager, 2FA is on for banking/email, and you spot obvious scams.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.intermediate,
    prompt:
        "You are productive with spreadsheets, navigate government portals confidently, and use AI tools responsibly.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.advanced,
    prompt:
        "You maintain a clean digital footprint, run a strong LinkedIn, and have an identity-theft response plan.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
  ),

  // ── NAVIGATION ─────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.basic,
    prompt:
        "You hold a driving licence, book your own travel, and handle government offices independently.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.intermediate,
    prompt:
        "You can file an FIR, travel internationally alone, and recognise rental / job / investment scams.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.advanced,
    prompt:
        "You have an emergency playbook, know your legal rights with police, and handle corrupt officials calmly.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
  ),

  // ── COGNITIVE ──────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.basic,
    prompt:
        "You have a daily routine that sticks, read non-fiction regularly, and learn new skills on your own.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.intermediate,
    prompt:
        "You use a productivity system, say no to commit fewer but deeper, and fact-check before sharing.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.advanced,
    prompt:
        "You run weekly reviews, speak publicly without panic, and ship side projects to completion.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
  ),
];

List<AdultBaselineQuestion> adultQuestionsForAge(int age) =>
    adultBaselineQuestions.where((q) => q.minUserAge <= age).toList();
