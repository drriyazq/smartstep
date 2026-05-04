/// Category-based baseline assessment for ADULT profiles.
///
/// Mirrors the child baseline in shape (category × tier) but each prompt is a
/// SINGLE observable competency. A "Yes" bypasses adult tasks in the same
/// category whose `max_age <= bypassTasksUpToAge` AND whose slug matches any
/// of `bypassMatchKeywords` (substring, lowercased). Empty keyword list
/// bypasses every adult task in the (category, age) tier.
///
/// Tier age-gating:
///   - Basic        (bypass <= 30):  shown for age 20+
///   - Intermediate (<= 45):         shown for age 28+
///   - Advanced     (<= 99):         shown for age 36+
enum AdultTier { basic, intermediate, advanced }

class AdultBaselineQuestion {
  const AdultBaselineQuestion({
    required this.category,
    required this.categoryLabel,
    required this.tier,
    required this.prompt,
    required this.bypassTasksUpToAge,
    required this.minUserAge,
    this.bypassMatchKeywords = const <String>[],
  });
  final String category;
  final String categoryLabel;
  final AdultTier tier;
  final String prompt;
  final int bypassTasksUpToAge;
  final int minUserAge;

  /// Slug-fragment keywords scoping which tasks a "Yes" bypasses.
  /// Empty = bypass every approved adult task in (category, max_age).
  final List<String> bypassMatchKeywords;

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
    prompt: "You have a 6-month emergency fund saved up.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-emergency-fund-6mo'],
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.basic,
    prompt: "You run a monthly SIP / recurring savings.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: [
      'adult-start-sip-index',
      'adult-avoid-lifestyle-creep',
    ],
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.basic,
    prompt: "You can read your own payslip clearly.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-read-payslip'],
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.basic,
    prompt: "You hold real health insurance (not just employer cover).",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-health-insurance-real'],
  ),

  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.intermediate,
    prompt: "You file your own taxes (or actively review them).",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-tax-saving-strategy'],
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.intermediate,
    prompt: "You hold appropriate term-life insurance for your dependents.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-term-life-insurance'],
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.intermediate,
    prompt: "You understand the math behind a home loan / EMI.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-home-loan-math'],
  ),

  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.advanced,
    prompt: "You have a written, signed will.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-will-succession'],
  ),
  AdultBaselineQuestion(
    category: 'financial',
    categoryLabel: 'Financial',
    tier: AdultTier.advanced,
    prompt: "You actively help your parents manage their finances.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-manage-parent-finances'],
  ),

  // ── HOUSEHOLD ──────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.basic,
    prompt: "You can cook a simple meal yourself.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-batch-meal-prep'],
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.basic,
    prompt: "You meal-plan and shop a week within a budget.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-week-meal-plan-budget'],
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.basic,
    prompt: "You handle basic home repairs yourself.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-basic-home-repair'],
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.basic,
    prompt: "You know your tenant rights before signing a lease.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-tenant-rights', 'adult-moving-out-checklist'],
  ),

  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.intermediate,
    prompt: "You handle landlord disputes calmly and effectively.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-deal-with-landlord'],
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.intermediate,
    prompt: "You hire and manage house help fairly.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-manage-house-help'],
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.intermediate,
    prompt: "You deep-clean your home thoroughly each month.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-deep-clean-workflow'],
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.intermediate,
    prompt: "You have a household emergency kit ready.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-home-emergency-kit'],
  ),

  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.advanced,
    prompt: "You can host and cook for ten people confidently.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-cook-for-ten'],
  ),
  AdultBaselineQuestion(
    category: 'household',
    categoryLabel: 'Household',
    tier: AdultTier.advanced,
    prompt: "You've helped aging-proof your parents' home.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-aging-proof-home'],
  ),

  // ── SOCIAL ─────────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.basic,
    prompt: "You can introduce yourself to strangers and make small talk.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-make-friends'],
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.basic,
    prompt: "You apologise properly when you're wrong.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-apologise-properly'],
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.basic,
    prompt: "You date with self-respect and clear standards.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-dating-self-respect'],
  ),

  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.intermediate,
    prompt: "You can have difficult conversations without avoiding them.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-difficult-conversation'],
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.intermediate,
    prompt: "You set clear boundaries with family.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-set-boundaries-family'],
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.intermediate,
    prompt: "You give and receive professional feedback without drama.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-give-receive-feedback'],
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.intermediate,
    prompt: "You can negotiate your salary professionally.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-negotiate-salary'],
  ),

  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.advanced,
    prompt: "You actively mentor someone junior.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-mentor-someone'],
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.advanced,
    prompt: "You've repaired a broken relationship worth keeping.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-repair-broken-relationship'],
  ),
  AdultBaselineQuestion(
    category: 'social',
    categoryLabel: 'Social',
    tier: AdultTier.advanced,
    prompt: "You handle workplace conflict decisively without burning bridges.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-workplace-conflict', 'adult-handle-bad-boss'],
  ),

  // ── DIGITAL ────────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.basic,
    prompt: "You use a password manager.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-password-manager'],
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.basic,
    prompt: "2FA is on for your banking and primary email.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-2fa-everywhere', 'adult-secure-online-banking'],
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.basic,
    prompt: "You can confidently navigate Indian government portals.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-navigate-govt-portals'],
  ),

  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.intermediate,
    prompt: "You're productive with spreadsheets for real decisions.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-spreadsheet-mastery'],
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.intermediate,
    prompt: "You use AI tools (ChatGPT, Claude) responsibly.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-use-ai-properly'],
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.intermediate,
    prompt: "You fact-check before forwarding messages.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-fact-check-discipline'],
  ),

  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.advanced,
    prompt: "You audit and clean up your online digital footprint.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-digital-footprint-audit'],
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.advanced,
    prompt: "You have a clear identity-theft response plan.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-identity-theft-response'],
  ),
  AdultBaselineQuestion(
    category: 'digital',
    categoryLabel: 'Digital',
    tier: AdultTier.advanced,
    prompt: "You maintain a strong, working LinkedIn profile.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-linkedin-that-works'],
  ),

  // ── NAVIGATION ─────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.basic,
    prompt: "You hold a driving licence.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-driving-licence'],
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.basic,
    prompt: "You book your own domestic travel confidently.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-book-domestic-travel'],
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.basic,
    prompt: "You handle Indian government offices independently.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-navigate-govt-offices'],
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.basic,
    prompt: "You can spot rental scams and bad flats.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-spot-rental-scams'],
  ),

  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.intermediate,
    prompt: "You can file an FIR or online police complaint.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-file-fir'],
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.intermediate,
    prompt: "You've travelled internationally on your own.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-international-travel-basics'],
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.intermediate,
    prompt: "You know your rights when stopped by police.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-stopped-by-police'],
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.intermediate,
    prompt: "You can file a consumer complaint that gets action.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-file-consumer-complaint'],
  ),

  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.advanced,
    prompt: "You have an emergency playbook for real situations.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-emergency-playbook'],
  ),
  AdultBaselineQuestion(
    category: 'navigation',
    categoryLabel: 'Navigation',
    tier: AdultTier.advanced,
    prompt: "You handle corrupt officials calmly without paying bribes.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-handle-corrupt-officials'],
  ),

  // ── COGNITIVE ──────────────────────────────────────────────────────
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.basic,
    prompt: "You have a daily routine that actually sticks.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-daily-routine'],
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.basic,
    prompt: "You read non-fiction regularly.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-read-nonfiction'],
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.basic,
    prompt: "You learn new skills on your own without a course.",
    bypassTasksUpToAge: 30,
    minUserAge: 20,
    bypassMatchKeywords: ['adult-learn-new-skill'],
  ),

  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.intermediate,
    prompt: "You use a personal productivity system.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-productivity-system', 'adult-time-blocking'],
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.intermediate,
    prompt: "You say no well — fewer commitments, deeper work.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-say-no'],
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.intermediate,
    prompt: "You can speak in public without panic.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-public-speaking'],
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.intermediate,
    prompt: "You write clearly so people actually read what you send.",
    bypassTasksUpToAge: 45,
    minUserAge: 28,
    bypassMatchKeywords: ['adult-writing-clearly'],
  ),

  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.advanced,
    prompt: "You run a 15-minute weekly review consistently.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-weekly-reflection'],
  ),
  AdultBaselineQuestion(
    category: 'cognitive',
    categoryLabel: 'Thinking',
    tier: AdultTier.advanced,
    prompt: "You finish side projects you start.",
    bypassTasksUpToAge: 99,
    minUserAge: 36,
    bypassMatchKeywords: ['adult-side-project-complete'],
  ),
];

List<AdultBaselineQuestion> adultQuestionsForAge(int age) =>
    adultBaselineQuestions.where((q) => q.minUserAge <= age).toList();
