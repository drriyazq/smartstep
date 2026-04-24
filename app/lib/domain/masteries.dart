/// Mastery capabilities — bundles of related tasks that combine into a
/// share-worthy real-world competence.
///
/// When a child completes ALL required task slugs for a mastery, the app
/// auto-surfaces a premium certificate image they can share.
///
/// The source of truth for what each mastery means (title, celebration copy,
/// required prerequisites) lives here. Drafted in
/// `docs/publishing/mastery_capabilities_draft.md`.
library;

class Mastery {
  const Mastery({
    required this.id,
    required this.title,
    required this.celebration,
    required this.category,
    required this.emoji,
    required this.earnedAtAge,
    required this.requiredTaskSlugs,
    this.isAdult = false,
  });

  /// Stable machine identifier. Used as Hive key for earned-mastery tracking.
  final String id;

  /// One-liner bragging-rights title shown on the certificate.
  final String title;

  /// Celebration sentence describing what the child can now do.
  /// Goes on the certificate, in the share caption, and in the Achievements tab.
  final String celebration;

  /// Category slug for color theming. Must match dashboard categoryMeta():
  /// financial | household | digital | navigation | cognitive | social
  final String category;

  /// Single emoji shown prominently on the certificate.
  final String emoji;

  /// Typical age when earned — shown on certificate metadata.
  final int earnedAtAge;

  /// Task slugs that must ALL be completed (or bypassed) to earn this mastery.
  final List<String> requiredTaskSlugs;

  /// Adult-mode masteries are only surfaced for adult profiles.
  final bool isAdult;
}

const kMasteries = <Mastery>[
  // ─────────────────────────────────────────────── Navigation ──
  Mastery(
    id: 'street-safe-pedestrian',
    title: 'Street-Safe Solo Pedestrian',
    celebration:
        'Can walk on their own in the neighbourhood — crosses roads safely, knows our address, handles getting lost, and recognises safe landmarks.',
    category: 'navigation',
    emoji: '🚸',
    earnedAtAge: 8,
    requiredTaskSlugs: [
      'walk-safely-age6',
      'look-both-ways',
      'cross-crosswalk-with-parent',
      'know-full-name-address-phone',
      'identify-landmarks-near-home',
      'walk-to-mailbox-and-back',
      'stranger-safety-basics',
    ],
  ),
  Mastery(
    id: 'metro-transit-solo',
    title: 'Metro & Transit Solo Traveler',
    celebration:
        'Can use public transport on their own, end-to-end — reads maps, buys tickets, handles disruptions, travels safely.',
    category: 'navigation',
    emoji: '🚇',
    earnedAtAge: 12,
    requiredTaskSlugs: [
      'read-bus-metro-map-age8',
      'buy-transit-ticket',
      'ride-transit-independently',
      'walk-home-from-school-age11',
      'handle-transit-disruption-age11',
      'cross-busy-intersection-solo',
    ],
  ),
  Mastery(
    id: 'navigate-new-city',
    title: 'Navigate a New City',
    celebration:
        'Can find their way around a city they\'ve never been to — using maps, transport hubs, and street signs — entirely on their own.',
    category: 'navigation',
    emoji: '🗺️',
    earnedAtAge: 14,
    requiredTaskSlugs: [
      'multi-transfer-transit-age12',
      'navigate-transport-hub-age12',
      'read-map-navigate-age14',
      'navigate-new-city-age14',
      'use-phone-maps-app',
    ],
  ),
  Mastery(
    id: 'intercity-traveler',
    title: 'Independent Intercity Traveler',
    celebration:
        'Can plan and take solo intercity trips — books tickets, manages logistics, handles the unexpected.',
    category: 'navigation',
    emoji: '🚆',
    earnedAtAge: 15,
    requiredTaskSlugs: [
      'online-travel-booking-age14',
      'plan-route-with-stops',
      'day-trip-unfamiliar-area-age14',
      'plan-trip-independently-age14',
      'intercity-train-bus-alone-age15',
    ],
  ),
  Mastery(
    id: 'airport-ready-traveler',
    title: 'Airport-Ready Global Traveler',
    celebration:
        'Can navigate an airport from check-in to boarding, and is ready for international travel — solo.',
    category: 'navigation',
    emoji: '✈️',
    earnedAtAge: 16,
    requiredTaskSlugs: [
      'navigate-airport-age16',
      'overnight-trip-solo-age16',
      'travel-abroad-basics-age16',
      'online-travel-booking-age14',
    ],
  ),

  // ─────────────────────────────────────────────── Financial ──
  Mastery(
    id: 'money-aware-shopper',
    title: 'Money-Aware Little Shopper',
    celebration:
        'Knows what money is worth — counts coins, reads price tags, pays at shops, and counts their change.',
    category: 'financial',
    emoji: '🪙',
    earnedAtAge: 8,
    requiredTaskSlugs: [
      'coins-vs-notes-age5',
      'identify-coins-age6',
      'pay-at-shop-age6',
      'read-price-tag',
      'pay-at-till-count-change-age7',
      'simple-change-making-age7',
    ],
  ),
  Mastery(
    id: 'smart-young-saver',
    title: 'Smart Young Saver',
    celebration:
        'Saves money consistently and with purpose — earns small amounts, tracks savings, and delays gratification to reach goals.',
    category: 'financial',
    emoji: '🏦',
    earnedAtAge: 11,
    requiredTaskSlugs: [
      'save-piggy-bank-goal-age8',
      'earn-by-small-task-age7',
      'save-for-goal',
      'save-for-medium-goal-age10',
      'track-savings-ledger',
      'pocket-money-basics-age7',
    ],
  ),
  Mastery(
    id: 'independent-smart-shopper',
    title: 'Independent Smart Shopper',
    celebration:
        'Can do the shopping solo — compares prices per unit, reads labels, checks receipts, and spots bad deals.',
    category: 'financial',
    emoji: '🛒',
    earnedAtAge: 12,
    requiredTaskSlugs: [
      'compare-prices',
      'check-change',
      'read-receipt',
      'help-grocery-age10',
      'compare-unit-prices',
      'recognize-scam-offer',
    ],
  ),
  Mastery(
    id: 'budget-ready-teen',
    title: 'Budget-Ready Teen',
    celebration:
        'Manages their own money — sets a budget, tracks spending, runs a bank account, and saves for meaningful goals.',
    category: 'financial',
    emoji: '📊',
    earnedAtAge: 14,
    requiredTaskSlugs: [
      'plan-weekly-budget',
      'spending-diary-week-age11',
      'monthly-allowance-budget-age12',
      'track-week-own-spending-age13',
      'open-bank-account-age14',
      'save-for-bigger-goal-age14',
    ],
  ),
  Mastery(
    id: 'adulting-money-manager',
    title: 'Adulting-Ready Money Manager',
    celebration:
        'Ready for real financial adulting — reads payslips, understands credit & EMI, handles utilities, and negotiates like a pro.',
    category: 'financial',
    emoji: '💳',
    earnedAtAge: 17,
    requiredTaskSlugs: [
      'read-payslip-age15',
      'negotiate-price-age15',
      'handle-utility-bill-age15',
      'understand-credit-score-age16',
      'understand-emi-loans-age16',
      'compare-bank-accounts-age16',
    ],
  ),

  // ─────────────────────────────────────────────── Household ──
  Mastery(
    id: 'kitchen-helper',
    title: 'Capable Kitchen Helper',
    celebration:
        'Safe and useful in the kitchen — preps food, makes cold meals, washes dishes, and cleans up.',
    category: 'household',
    emoji: '🍴',
    earnedAtAge: 9,
    requiredTaskSlugs: [
      'help-prep-veg-age7',
      'pour-drink-no-spill-age7',
      'crack-egg',
      'make-cold-sandwich',
      'wash-dishes',
      'clear-table',
      'wipe-kitchen-counters',
    ],
  ),
  Mastery(
    id: 'breakfast-chef',
    title: 'Breakfast Chef',
    celebration:
        'Can make their own breakfast from scratch — uses the stove safely, handles heat, and cleans up after themselves.',
    category: 'household',
    emoji: '🍳',
    earnedAtAge: 10,
    requiredTaskSlugs: [
      'boil-water',
      'make-breakfast-age9',
      'crack-egg',
      'use-stove-knob',
      'use-microwave-safely',
      'safe-knife-use-age9',
    ],
  ),
  Mastery(
    id: 'home-chef',
    title: 'Independent Home Chef',
    celebration:
        'Can prepare a full home-cooked meal from start to finish — chops, cooks, serves, and cleans up after.',
    category: 'household',
    emoji: '👨‍🍳',
    earnedAtAge: 12,
    requiredTaskSlugs: [
      'cook-egg',
      'cook-pasta',
      'cook-full-meal',
      'kitchen-knife-chop-age11',
      'understand-food-storage-age11',
    ],
  ),
  Mastery(
    id: 'live-alone-ready',
    title: 'Ready to Live Alone',
    celebration:
        'Can run a household solo — cooks full meals, does laundry, cleans deeply, handles repairs and emergencies.',
    category: 'household',
    emoji: '🏡',
    earnedAtAge: 15,
    requiredTaskSlugs: [
      'do-own-laundry-age14',
      'cook-full-meal-age14',
      'deep-clean-space-age15',
      'handle-emergency-alone-age14',
      'basic-home-repair-age14',
      'change-bulb-reset-breaker-age15',
    ],
  ),

  // ─────────────────────────────────────────────── Digital ──
  Mastery(
    id: 'safe-little-tech-user',
    title: 'Safe Little Tech User',
    celebration:
        'Uses screens safely — asks before downloading, respects limits, never shares private info, video-calls family with ease.',
    category: 'digital',
    emoji: '📱',
    earnedAtAge: 8,
    requiredTaskSlugs: [
      'ask-before-screen-age6',
      'no-strangers-screen-age5',
      'screen-time-stop-age6',
      'private-info-rule-age6',
      'video-call-family-age6',
      'ask-before-downloading',
    ],
  ),
  Mastery(
    id: 'online-safety-savvy',
    title: 'Online Safety Savvy',
    celebration:
        'Can spot and avoid online dangers on their own — scams, strangers, fake content, cyberbullying.',
    category: 'digital',
    emoji: '🛡️',
    earnedAtAge: 12,
    requiredTaskSlugs: [
      'spot-phishing-link',
      'recognize-scam-offer',
      'online-stranger-safety-age11',
      'recognize-cyberbullying-age11',
      'spot-phishing-age12',
      'recognize-ai-generated-media',
    ],
  ),
  Mastery(
    id: 'digital-citizen',
    title: 'Digital Citizen',
    celebration:
        'Runs their own digital life responsibly — strong passwords, 2FA, locked-down privacy, and a clean digital footprint.',
    category: 'digital',
    emoji: '🔐',
    earnedAtAge: 15,
    requiredTaskSlugs: [
      'strong-password-age14',
      'turn-on-2fa-age11',
      'online-safety-privacy-age14',
      'digital-footprint-age14',
      'setup-social-account-age13',
      'backup-important-data-age12',
    ],
  ),

  // ─────────────────────────────────────────────── Safety ──
  Mastery(
    id: 'emergency-ready-kid',
    title: 'Emergency-Ready Kid',
    celebration:
        'Knows what to do when things go wrong — can call for help, apply first aid, handle a small emergency, and stay home alone safely.',
    category: 'household',
    emoji: '🚑',
    earnedAtAge: 11,
    requiredTaskSlugs: [
      'call-for-help-emergency',
      'dial-emergency-number',
      'fire-escape-plan',
      'first-aid-small-cut',
      'what-counts-as-emergency-age6',
      'home-alone-safely',
    ],
  ),

  // ─────────────────────────────────────────────── Social ──
  Mastery(
    id: 'confident-communicator',
    title: 'Confident Communicator',
    celebration:
        'Can hold a conversation with anyone — greets adults, introduces themselves, takes turns, and holds a real small-talk conversation.',
    category: 'social',
    emoji: '💬',
    earnedAtAge: 9,
    requiredTaskSlugs: [
      'greet-adults-age6',
      'social-greet-adult',
      'social-introduce-yourself',
      'small-talk-basics-age8',
      'wait-turn-speak-age8',
      'make-eye-contact-age5',
    ],
  ),
  Mastery(
    id: 'social-emotional-pro',
    title: 'Social-Emotional Pro',
    celebration:
        'Handles the hard social stuff — resists peer pressure, resolves conflicts calmly, says no with confidence, recognises bullying.',
    category: 'social',
    emoji: '🫂',
    earnedAtAge: 13,
    requiredTaskSlugs: [
      'handle-peer-pressure',
      'resist-peer-pressure-age12',
      'social-resolve-conflict',
      'recognise-bullying-age10',
      'social-say-no-confidently',
      'social-disagree-respectfully',
    ],
  ),
  Mastery(
    id: 'professional-young-adult',
    title: 'Professional Young Adult',
    celebration:
        'Ready for formal adult interactions — interviews, professional emails, networking, leading projects.',
    category: 'social',
    emoji: '👔',
    earnedAtAge: 16,
    requiredTaskSlugs: [
      'interview-for-opportunity-age15',
      'introduce-professionally-age15',
      'professional-digital-communication-age16',
      'network-follow-up-age16',
      'lead-a-group-project-age15',
    ],
  ),

  // ─────────────────────────────────────────────── Active Body ──
  Mastery(
    id: 'active-body-champion',
    title: 'Active Body Champion',
    celebration:
        'Has built a consistent physical activity habit — warms up properly, knows a sport, works out at home, and has kept it going for a month.',
    category: 'household',
    emoji: '💪',
    earnedAtAge: 13,
    requiredTaskSlugs: [
      'outdoor-play-hour-age7',
      'daily-movement-habit-age8',
      'basic-warmup-stretches-age9',
      'learn-sport-basics-age10',
      'home-bodyweight-routine-age11',
      'track-fitness-progress-age12',
      'build-exercise-habit-age13',
    ],
  ),

  // ─────────────────────────────────────────────── Digital Creator ──
  Mastery(
    id: 'young-digital-creator',
    title: 'Young Digital Creator',
    celebration:
        'Can create and share real digital work — takes good photos, records clean videos, edits with judgement, and has published their first piece.',
    category: 'digital',
    emoji: '🎬',
    earnedAtAge: 12,
    requiredTaskSlugs: [
      'take-good-photo-age8',
      'record-clear-video-age9',
      'edit-photo-basics-age10',
      'make-slideshow-age10',
      'edit-video-basics-age11',
      'publish-first-creation-age12',
    ],
  ),

  // ─────────────────────────────────────────────── Sustainability ──
  Mastery(
    id: 'eco-conscious-kid',
    title: 'Eco-Conscious Kid',
    celebration:
        'Lives lighter on the planet — saves water and power without being asked, carries reusables, reuses before throwing, composts, and repairs instead of replacing.',
    category: 'household',
    emoji: '🌱',
    earnedAtAge: 11,
    requiredTaskSlugs: [
      'turn-off-lights-age6',
      'save-water-tap-age7',
      'sort-recycle-age6',
      'reuse-before-throw-age8',
      'carry-reusable-age9',
      'compost-kitchen-waste-age10',
      'repair-before-replace-age11',
    ],
  ),

  // ─────────────────────────────────────────────── Healthcare ──
  Mastery(
    id: 'healthcare-self-managed',
    title: 'Handles Their Own Healthcare',
    celebration:
        'Owns their health — knows their medicines, reads labels safely, keeps their own records, books their own appointments, knows the family history.',
    category: 'household',
    emoji: '🩺',
    earnedAtAge: 14,
    requiredTaskSlugs: [
      'know-own-medicines-age11',
      'medicine-dosage-safety-age12',
      'when-to-see-doctor-age12',
      'keep-health-record-age13',
      'manage-own-health-routine-age13',
      'book-doctor-appt-age14',
      'know-family-medical-history-age14',
      'medical-appointment-solo-age15',
    ],
  ),

  // ─────────────────────────────────────────────── Cognitive ──
  Mastery(
    id: 'master-young-researcher',
    title: 'Master Young Researcher',
    celebration:
        'Can research any topic independently — finds good sources, evaluates credibility, summarises, and presents.',
    category: 'cognitive',
    emoji: '🔍',
    earnedAtAge: 12,
    requiredTaskSlugs: [
      'ask-why-research-answer',
      'find-info-in-book-age8',
      'summarize-short-story',
      'evaluate-source-credibility',
      'fact-check-simple-age11',
      'research-and-present-age10',
    ],
  ),

  // ─────────────────────────────────────────────── Adult ──
  Mastery(
    id: 'adult-financial-independence',
    title: 'Financial Independence Foundation',
    celebration:
        'Has the financial foundation to weather anything — emergency fund, monthly SIP, credit-card discipline, and no lifestyle creep.',
    category: 'financial',
    emoji: '🏛️',
    earnedAtAge: 25,
    isAdult: true,
    requiredTaskSlugs: [
      'adult-emergency-fund-6mo',
      'adult-start-sip-index',
      'adult-credit-card-discipline',
      'adult-avoid-lifestyle-creep',
      'adult-read-payslip',
    ],
  ),
  Mastery(
    id: 'adult-living-alone-ready',
    title: 'Living-On-Your-Own Ready',
    celebration:
        'Handles a solo home completely — moving in, paying rent, knowing tenant rights, fixing what breaks, cooking ahead.',
    category: 'household',
    emoji: '🔑',
    earnedAtAge: 25,
    isAdult: true,
    requiredTaskSlugs: [
      'adult-moving-out-checklist',
      'adult-basic-home-repair',
      'adult-batch-meal-prep',
      'adult-tenant-rights',
      'adult-week-meal-plan-budget',
    ],
  ),
  Mastery(
    id: 'adult-full-life-admin',
    title: 'Full Life Admin',
    celebration:
        'Grown-up life admin is handled — insurance in place, will written, loan math understood, tax optimised.',
    category: 'financial',
    emoji: '📋',
    earnedAtAge: 35,
    isAdult: true,
    requiredTaskSlugs: [
      'adult-term-life-insurance',
      'adult-health-insurance-real',
      'adult-home-loan-math',
      'adult-will-succession',
      'adult-tax-saving-strategy',
    ],
  ),
];
