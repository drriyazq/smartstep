"""Seeds the full 85-task catalog into the review queue (status=pending).

Existing rows (from seed_demo) are left untouched — this command only inserts
slugs that don't already exist. Reviewers then screen/approve them in admin.

Safe to run repeatedly.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task


# --- Tags -----------------------------------------------------------------------
TAGS = [
    ("money-basics",     "Money basics",     Tag.Category.FINANCIAL),
    ("kitchen-basics",   "Kitchen basics",   Tag.Category.HOUSEHOLD),
    ("home-care",        "Home care",        Tag.Category.HOUSEHOLD),
    ("digital-literacy", "Digital literacy", Tag.Category.DIGITAL),
    ("wayfinding",       "Wayfinding",       Tag.Category.NAVIGATION),
    ("reasoning",        "Reasoning",        Tag.Category.COGNITIVE),
]

ALL_ENVS = ("urban", "suburban", "rural")
URBAN_ONLY = ("urban", "suburban")

# slug → parent note explaining the skill's importance
PARENT_NOTES = {
    # FINANCIAL
    "identify-coins": (
        "Children cannot handle money confidently until they can identify every denomination "
        "without hesitation. This is the irreplaceable foundation of financial literacy — "
        "skipping it leads to social anxiety at checkouts and reliance on cards over understanding."
    ),
    "recognize-currency-symbol": (
        "Currency symbols appear on every price tag, receipt, and bank statement. "
        "Recognising them across contexts (£, $, ₹, €) gives children a global awareness "
        "of money as a universal system rather than a local habit."
    ),
    "count-coins-to-total": (
        "Counting coins to a target trains mental arithmetic in a meaningful context. "
        "Unlike maths worksheets, the child understands immediately why precision matters — "
        "being a few coins short has a real consequence. "
    ),
    "distinguish-need-want": (
        "The need/want distinction is the first and most durable filter in personal finance. "
        "Children who internalise it from a young age make dramatically fewer impulsive "
        "purchases and develop a values-driven relationship with money."
    ),
    "track-savings-ledger": (
        "A savings ledger — even a notebook — teaches children that money has a running total "
        "that changes with every decision. Knowing your balance is the single most important "
        "habit separating financial stress from financial security in adulthood."
    ),
    "save-for-goal": (
        "Saving for a specific named goal activates delayed gratification in a tangible way. "
        "Longitudinal studies consistently show that children who practise this regularly "
        "develop stronger self-control, resilience, and long-term planning capacity."
    ),
    "donate-small-amount": (
        "Giving money away — even a tiny amount — changes how children think about money's purpose. "
        "It teaches that wealth is a tool for values, not just personal consumption, "
        "and builds empathy and civic awareness alongside financial literacy."
    ),
    "read-receipt": (
        "Reading and checking a receipt teaches children that every transaction leaves a record, "
        "that errors happen, and that they have the right and ability to verify. "
        "These habits prevent both overpayment and passive financial behaviour in adulthood."
    ),
    "calculate-simple-discount": (
        "Discounts and sales are designed to trigger spending, not saving. "
        "Children who can quickly calculate the actual pound/dollar saving learn to evaluate "
        "offers on their real merit — a consumer skill that most adults still lack."
    ),
    "estimate-grocery-total": (
        "Mentally estimating a basket total before checkout ties arithmetic to consequence. "
        "Children who do this regularly develop number fluency, budget awareness, "
        "and the confidence to catch obvious errors at the till."
    ),
    "compare-unit-prices": (
        "Unit pricing (cost per 100g, per litre) is the fairest way to compare products "
        "across different pack sizes — and the one supermarkets make hardest to find. "
        "Children who learn it become lifelong smart shoppers and critical consumers."
    ),
    "spot-ad-vs-content": (
        "Advertising is woven into every platform children use. Recognising the difference "
        "between an ad and genuine content is a foundational media literacy skill that "
        "protects children from manipulative marketing for the rest of their lives."
    ),
    "plan-weekly-budget": (
        "A weekly budget turns abstract money concepts into a practical decision-making system. "
        "Children who plan how to allocate a limited amount across needs and wants "
        "are practising the same skill used in household and business budgeting."
    ),
    "recognize-scam-offer": (
        "\"Too good to be true\" is the oldest scam signal, but children (and many adults) "
        "still fall for it. Training this recognition early — with real examples — "
        "is one of the simplest fraud-prevention lessons possible."
    ),
    # HOUSEHOLD
    "make-bed": (
        "Making a bed is far more than tidiness. Admiral William McRaven's famous address "
        "cites it as the foundational daily discipline: completing one task at the start "
        "of the day creates momentum, a sense of control, and a visible measure of order."
    ),
    "sort-laundry-by-color": (
        "Sorting laundry correctly preserves clothes and teaches categorisation — "
        "a foundational cognitive skill. Children who learn this early also understand "
        "that objects have properties that determine how they should be treated."
    ),
    "fold-tshirt": (
        "Folding a t-shirt neatly combines fine motor coordination with care for belongings. "
        "Children who manage their own clothes develop ownership of their space "
        "and are significantly more prepared for independent living."
    ),
    "sweep-small-area": (
        "Sweeping provides immediate visual feedback — dirty floor becomes clean. "
        "This before/after clarity makes it one of the most satisfying early household tasks "
        "and builds the habit of noticing and responding to a household need."
    ),
    "wipe-kitchen-counters": (
        "Kitchen hygiene is a direct public health skill. Children who routinely wipe surfaces "
        "understand the link between cleanliness and preventing illness — "
        "building a hygiene habit that protects their future households."
    ),
    "water-plants": (
        "Caring for plants teaches children that living things depend on consistent, "
        "attentive care. The consequence of forgetting — a wilted plant — "
        "is gentle but real, making it one of the best early lessons in responsibility."
    ),
    "take-out-trash-sort-recycle": (
        "Sorting recycling from general waste teaches environmental responsibility in a daily, "
        "concrete way. Children who do this regularly develop ecological awareness "
        "and the understanding that individual actions have collective environmental impact."
    ),
    "make-cold-sandwich": (
        "Preparing food without heat is the first step to genuine kitchen independence. "
        "A child who can make their own lunch is not just saving a parent's time — "
        "they are building agency, nutrition awareness, and confidence in self-provision."
    ),
    "use-microwave-safely": (
        "Safe microwave use means understanding heat, containers, timing, and the risk of burns. "
        "Children who master this can reheat food independently — a meaningful safety "
        "and autonomy milestone for after-school hours."
    ),
    "load-dishwasher": (
        "Loading a dishwasher correctly requires spatial reasoning and method — "
        "racks, angles, item types. It also builds follow-through: starting and completing "
        "a household process from dirty dishes to clean cupboard."
    ),
    "operate-washing-machine": (
        "Doing laundry independently is one of the clearest markers of self-sufficiency. "
        "Children who can operate a washing machine before leaving home report significantly "
        "less stress in the transition to independence and university life."
    ),
    # DIGITAL
    "turn-device-on-off": (
        "Physical device literacy — powering on, off, and charging correctly — "
        "is the starting point for all digital competence. Children who understand "
        "their device as a physical object requiring proper care use it more responsibly."
    ),
    "type-own-name": (
        "Keyboard input is now as fundamental as handwriting. Children who are comfortable "
        "typing early have a measurable advantage in school assignments, tests, "
        "and all future digital work."
    ),
    "open-close-app": (
        "Navigating between apps purposefully — opening what you need, closing what you don't — "
        "builds intentional device use versus passive scrolling. "
        "It is the digital equivalent of picking up a book and putting it back on the shelf."
    ),
    "take-and-delete-photo": (
        "Ownership over one's own digital content starts with knowing how to create and remove it. "
        "Children who can delete unwanted photos understand that they control their "
        "digital presence — an important foundation for privacy awareness."
    ),
    "use-kid-safe-search": (
        "Guided information retrieval on age-appropriate platforms builds research skills "
        "while limiting exposure to harmful content. It also teaches children "
        "that not all search results are equal or trustworthy."
    ),
    "adjust-volume-brightness": (
        "Self-regulation of a device's sensory output — volume, brightness — "
        "reflects broader self-regulation. Children who manage these settings mindfully "
        "are practising the same skill as managing their own attention and comfort."
    ),
    "passwords-are-private": (
        "The concept that a password is private — shared with no one, not even friends — "
        "is the first and most critical digital security lesson. "
        "Children who understand this resist social engineering at its most basic level."
    ),
    "dont-share-personal-info": (
        "Oversharing personal information is the primary way children become targets online. "
        "Children who can list exactly what to protect (name, address, school, phone, photos) "
        "are far safer than those given only vague warnings about 'strangers'."
    ),
    "ask-before-downloading": (
        "App downloads can install malware, incur costs, or expose children to inappropriate content. "
        "Building the habit of asking permission before downloading establishes "
        "a parental checkpoint that significantly reduces risk across the board."
    ),
    "recognize-ad-banner": (
        "Digital advertising is deliberately designed to look like content. "
        "Children who can reliably distinguish ads from organic search results and articles "
        "are more critical consumers of information and less susceptible to manipulation."
    ),
    "close-suspicious-popup": (
        "Pop-ups and fake alerts are a primary delivery mechanism for malware and scams. "
        "Children who know to close suspicious windows without clicking inside them "
        "provide a first line of defence for the whole household's devices."
    ),
    "report-block-content": (
        "Knowing how to report and block is an act of digital citizenship. "
        "Children who use these tools move from passive bystander to active participant "
        "in maintaining a safer online environment for themselves and others."
    ),
    "video-call-etiquette": (
        "Video calls are now a core educational and professional communication format. "
        "Children who learn camera awareness, muting, and respectful turn-taking early "
        "are significantly better prepared for remote schooling and future careers."
    ),
    "respect-screen-time": (
        "Self-imposed screen time limits are more effective than parent-enforced restrictions. "
        "Children who set and honour their own limits practise the self-regulation "
        "that predicts academic success, sleep quality, and overall wellbeing."
    ),
    "create-strong-password": (
        "Weak passwords are the most common gateway for account compromise. "
        "Children who create strong, unique passphrases develop a security habit "
        "that protects their data and identity for life."
    ),
    "spot-phishing-link": (
        "Phishing — fake emails and login pages — affects all ages and is the most common "
        "form of cybercrime. Children trained to spot suspicious links are protecting "
        "not just themselves but often the household devices and accounts they use."
    ),
    "digital-footprint-awareness": (
        "Everything posted online can persist indefinitely and be seen by future employers, "
        "universities, and relationships. Children who understand their digital footprint "
        "make more thoughtful choices now that protect their future reputation."
    ),
    "evaluate-source-credibility": (
        "Misinformation spreads fastest among those who haven't been taught to question sources. "
        "Children who habitually check who wrote something, when, and why "
        "are dramatically more resistant to false claims across all topics."
    ),
    "recognize-ai-generated-media": (
        "AI-generated images, audio, and text are now indistinguishable to the untrained eye. "
        "Teaching children early to recognise the signs of synthetic media "
        "is one of the most future-relevant critical thinking skills we can give them."
    ),
    "use-two-step-verification": (
        "Two-step verification (2FA) is the single most effective account security measure "
        "available to ordinary users. Children who set it up themselves understand "
        "why it exists and will use it habitually on every important account."
    ),
    # NAVIGATION
    "know-full-name-address-phone": (
        "A child who cannot say their name, address, and a contact number cannot be reunited "
        "with their family in an emergency. This is the most important information "
        "a child can hold in memory — and it takes less than a week to learn."
    ),
    "know-parent-phone-memorized": (
        "In an emergency, a child with no phone can borrow any adult's device — "
        "but only if they know the number by heart. Screen dependence means most children "
        "no longer know any phone numbers; this reverses that dangerous gap."
    ),
    "identify-home-school-shop": (
        "A mental map anchored to three key locations (home, school, nearest shop) "
        "is the foundation of neighbourhood navigation. It is also a memory exercise "
        "that builds spatial confidence in a genuinely useful context."
    ),
    "walk-to-mailbox-and-back": (
        "A supervised micro-trip to the end of the drive and back is the first taste of "
        "solo movement in the world. The distance is safe; the independence is real. "
        "This early experience seeds the confidence needed for larger journeys later."
    ),
    "look-both-ways": (
        "Road traffic accidents are the leading cause of death for children aged 5–14 worldwide. "
        "The look-both-ways reflex, drilled until it is automatic, directly saves lives. "
        "There is no safer or higher-priority navigation skill to build first."
    ),
    "cross-crosswalk-with-parent": (
        "Practising pedestrian rules with a parent builds the habit before independence. "
        "Children who have crossed hundreds of times with supervision are calmer, "
        "more methodical, and safer when they eventually cross alone."
    ),
    "use-pedestrian-signal": (
        "Traffic signals encode rules about when it is safe to move. "
        "Children who read them correctly are engaging with civic infrastructure "
        "and developing the rule-following skills that make urban environments work."
    ),
    "stranger-safety-basics": (
        "Stranger safety is not 'never talk to strangers' — it is the judgement to distinguish "
        "safe adults (shop staff, uniformed workers) from unsafe situations. "
        "Children with this nuanced understanding are safer and less fearful."
    ),
    "dial-911-emergency": (
        "Children are more often first on scene in household emergencies than parents expect. "
        "A child who can dial an emergency number, give their address, and stay calm "
        "can summon help before any adult is even aware of the crisis."
    ),
    "identify-landmarks-near-home": (
        "Landmark navigation is the oldest and most reliable wayfinding method. "
        "Children who can name visible landmarks near home have a mental map that "
        "works even when devices fail, batteries die, or signals drop."
    ),
    "follow-simple-sketch-map": (
        "Following a hand-drawn map requires translating symbols into real-world geography. "
        "This cognitive step — from representation to reality — underpins map reading, "
        "architectural plans, and all spatial reasoning in later education."
    ),
    "read-street-transit-signs": (
        "Street signs are a visual language governing shared public space. "
        "Children who read them fluently are safer pedestrians, better-prepared cyclists, "
        "and more confident in any urban or suburban environment."
    ),
    "ride-bike-with-helmet": (
        "Cycling with road awareness combines motor skill, spatial judgment, and safety rules. "
        "Children given cycling independence (with proper training) show higher independence "
        "scores and greater physical confidence than peers who are driven everywhere."
    ),
    "take-bus-with-parent": (
        "First exposure to public transit with a parent present reduces anxiety "
        "and builds familiarity with the system — route numbers, stops, tickets, behaviour. "
        "This foundation makes later solo travel feel manageable rather than daunting."
    ),
    "buy-transit-ticket": (
        "Buying a ticket combines a financial transaction with system navigation. "
        "Children who have done this with a parent watching transition to solo "
        "transit use with much greater confidence and significantly fewer mistakes."
    ),
    "cross-busy-intersection-solo": (
        "A busy intersection is the highest-stakes pedestrian environment a child will face. "
        "The first solo crossing — after extensive supervised practice — is a milestone "
        "that signals genuine road competence and readiness for independent travel."
    ),
    "walk-to-friend-house-solo": (
        "Children given age-appropriate outdoor independence show higher self-esteem, "
        "stronger problem-solving skills, and better risk assessment than those "
        "kept in close supervision. A solo walk to a friend's house is a turning point."
    ),
    "use-phone-maps-app": (
        "Maps apps are powerful tools — but children who understand underlying concepts "
        "(north, scale, route options) use them far more effectively than those who "
        "just follow arrows. Digital tools should build on, not replace, spatial literacy."
    ),
    "plan-route-with-stops": (
        "Planning a route with waypoints and arrival times is applied forward-thinking. "
        "Children who practise this develop the anticipation and contingency mindset "
        "that make them effective planners in every area of life."
    ),
    "ride-transit-independently": (
        "Independent public transit use is one of the most significant autonomy milestones "
        "in a child's development. Research shows children given this independence "
        "develop stronger executive function, problem-solving, and self-reliance."
    ),
    # COGNITIVE
    "follow-three-step-instruction": (
        "Following multi-step instructions is a direct measure of working memory capacity. "
        "Children who practise this regularly develop the ability to hold and sequence "
        "information — a core academic skill used in every subject."
    ),
    "tell-time-analog-clock": (
        "Reading an analog clock requires understanding a circular scale, fractions, "
        "and two simultaneous representations of time. It is a rich mathematical and "
        "spatial task disguised as an everyday life skill."
    ),
    "use-calendar-find-date": (
        "A calendar is a child's first tool for managing the future. "
        "Children who use one regularly develop a structured sense of time beyond today — "
        "essential for planning, anticipating events, and managing expectations."
    ),
    "sort-by-invented-rule": (
        "Inventing a sorting rule requires abstraction — pulling out a property and "
        "applying it consistently. This cognitive operation underpins mathematics, "
        "science classification, and systematic thinking across all disciplines."
    ),
    "spot-pattern-in-sequence": (
        "Pattern recognition is the engine of mathematical thinking. "
        "Children who can identify a rule in a sequence are developing inductive reasoning — "
        "the same skill used in algebra, coding, and scientific hypothesis generation."
    ),
    "summarize-short-story": (
        "Summarisation requires reading comprehension, selection of key information, "
        "and reformulation in one's own words. Research shows it is one of the highest-value "
        "reading strategies, strongly linked to recall, understanding, and academic writing."
    ),
    "ask-why-research-answer": (
        "Curiosity is the seed of all learning, but it must be paired with the habit "
        "of seeking answers. Children who ask 'why?' and then look it up independently "
        "develop intrinsic motivation and information literacy simultaneously."
    ),
    "explain-process-in-order": (
        "Teaching something is the deepest form of learning. Children who can explain "
        "a process in order are demonstrating genuine understanding, not just recall. "
        "This skill builds communication ability and metacognitive awareness."
    ),
    "estimate-before-measuring": (
        "Estimating before measuring builds number sense and the habit of predicting outcomes "
        "before testing them — the foundation of the scientific method. "
        "Children who estimate regularly are less intimidated by unfamiliar quantities."
    ),
    "make-pros-cons-list": (
        "Decision frameworks like pros-and-cons lists externalise thinking and reduce "
        "the role of emotion in choices. Children who use them for small decisions "
        "apply the same structure to large ones, making better choices across their lives."
    ),
    "set-personal-goal-weekly": (
        "Setting a goal — even a small, weekly one — transforms intention into action. "
        "Children who practise goal-setting develop self-direction and the understanding "
        "that outcomes are not just things that happen to them but things they create."
    ),
    "break-task-into-steps": (
        "The ability to decompose a big task into manageable steps is the core of project "
        "management and the antidote to procrastination. Children who develop this skill "
        "start hard tasks more readily and complete them more consistently."
    ),
    "manage-homework-schedule": (
        "Self-managing a homework schedule means seeing one's time as a finite resource "
        "to be allocated. Children who do this independently from primary school "
        "show significantly better time management in secondary education and beyond."
    ),
    "resolve-disagreement-words": (
        "Resolving disagreements without aggression or withdrawal is a social-cognitive skill "
        "that most adults never master. Children who learn it early build healthier "
        "friendships, family relationships, and future professional collaborations."
    ),
    "accept-feedback-calmly": (
        "The ability to hear criticism without becoming defensive or shutting down "
        "is the practical expression of a growth mindset. Children who develop this "
        "learn faster, improve more, and handle challenge with resilience."
    ),
    "ask-clarifying-question": (
        "Asking a clarifying question when uncertain is an act of intellectual courage — "
        "admitting not-knowing and seeking resolution. Children who practise this "
        "learn more effectively in school and communicate more clearly in every context."
    ),
    "decide-with-incomplete-info": (
        "Real decisions almost always happen with incomplete information. "
        "Children who practise making reasonable choices under uncertainty — "
        "and evaluating them afterward — develop the tolerance for ambiguity that adult life requires."
    ),
    "detect-biased-argument": (
        "Bias detection is the foundation of critical thinking. Children who can identify "
        "when an argument omits contrary evidence or appeals only to emotion "
        "are far more resistant to manipulation in media, advertising, and politics."
    ),
    "spot-basic-logical-fallacy": (
        "Logical fallacies — false equivalence, ad hominem, straw-man — are the building blocks "
        "of bad arguments. Children who can name and spot them are equipped with "
        "a vocabulary for evaluating reasoning that pays dividends for life."
    ),
    "teach-younger-kid-skill": (
        "Teaching consolidates mastery more effectively than any other review method. "
        "When a child teaches a younger sibling or friend, they must organise knowledge, "
        "find analogies, and respond to questions — all forms of deep learning."
    ),
}


# (slug, title, tag_key, min_age, max_age, ceiling_us, envs, prereqs, benefit)
TASKS = [
    # === FINANCIAL (14 new) ===
    ("identify-coins",               "Identify coins & bills",                         "money-basics", 7, 9,  7,  ALL_ENVS,   [], "Foundation — cannot transact without recognizing currency."),
    ("recognize-currency-symbol",    "Recognize currency symbols ($ / ₹ / €)",         "money-basics", 7, 9,  7,  ALL_ENVS,   [], "Reads prices in any context."),
    ("count-coins-to-total",         "Count coins up to a target total",               "money-basics", 7, 10, 8,  ALL_ENVS,   ["identify-coins"], "Core arithmetic under real constraints."),
    ("distinguish-need-want",        "Distinguish needs vs wants",                     "money-basics", 8, 11, 9,  ALL_ENVS,   [], "First decision-making filter."),
    ("track-savings-ledger",         "Track savings in a simple ledger",               "money-basics", 8, 11, 10, ALL_ENVS,   [], "Builds the habit of knowing your balance."),
    ("save-for-goal",                "Save towards a named goal",                      "money-basics", 9, 11, 10, ALL_ENVS,   ["track-savings-ledger"], "Delayed gratification → discipline."),
    ("donate-small-amount",          "Donate a small amount to charity",               "money-basics", 8, 11, 10, ALL_ENVS,   [], "Money as a tool for values."),
    ("read-receipt",                 "Read and verify a receipt",                      "money-basics", 9, 11, 10, ALL_ENVS,   ["read-price-tag"], "Catches billing errors."),
    ("calculate-simple-discount",    "Calculate a simple % discount",                  "money-basics", 9, 11, 11, ALL_ENVS,   ["compare-prices"], "Applies math to real decisions."),
    ("estimate-grocery-total",       "Estimate a grocery-basket total",                "money-basics", 9, 11, 11, ALL_ENVS,   ["read-price-tag", "count-coins-to-total"], "Keeps spending within budget."),
    ("compare-unit-prices",          "Compare unit prices (per-kg / per-ml)",          "money-basics", 10, 11, 12, ALL_ENVS,  ["compare-prices"], "True cost comparison across pack sizes."),
    ("spot-ad-vs-content",           "Spot an advertisement vs editorial content",     "money-basics", 9, 11, 11, ALL_ENVS,   [], "Media literacy — resists manipulation."),
    ("plan-weekly-budget",           "Plan a small weekly budget",                     "money-basics", 10, 11, 12, ALL_ENVS,  ["save-for-goal", "distinguish-need-want"], "Allocates across categories under a cap."),
    ("recognize-scam-offer",         "Recognize a 'too good to be true' offer",        "money-basics", 10, 11, 12, ALL_ENVS,  [], "Fraud awareness before carrying own money."),

    # === HOUSEHOLD (11 new) ===
    ("make-bed",                     "Make your bed",                                  "home-care",      7, 11, 7,  ALL_ENVS,  [], "Daily habit that anchors the morning routine."),
    ("sort-laundry-by-color",        "Sort laundry by color",                          "home-care",      7, 11, 8,  ALL_ENVS,  [], "Prevents ruined clothes; pattern recognition."),
    ("fold-tshirt",                  "Fold a t-shirt neatly",                          "home-care",      7, 11, 8,  ALL_ENVS,  [], "Fine motor + care for belongings."),
    ("sweep-small-area",             "Sweep a small area",                             "home-care",      7, 11, 8,  ALL_ENVS,  [], "Tool use with visible before/after."),
    ("wipe-kitchen-counters",        "Wipe down kitchen counters",                     "home-care",      7, 11, 8,  ALL_ENVS,  [], "Kitchen hygiene basics."),
    ("water-plants",                 "Water the plants",                               "home-care",      7, 11, 8,  ALL_ENVS,  [], "Responsibility for a living thing."),
    ("take-out-trash-sort-recycle",  "Take out trash & sort recycling",                "home-care",      8, 11, 9,  ALL_ENVS,  [], "Environmental awareness + household rhythm."),
    ("make-cold-sandwich",           "Make a cold sandwich",                           "kitchen-basics", 8, 11, 9,  ALL_ENVS,  [], "First complete food prep without heat."),
    ("use-microwave-safely",         "Use a microwave safely",                         "kitchen-basics", 8, 11, 10, ALL_ENVS,  [], "Safe independent reheating."),
    ("load-dishwasher",              "Load a dishwasher",                              "home-care",      9, 11, 10, ALL_ENVS,  [], "Appliance competence."),
    ("operate-washing-machine",      "Operate a washing machine",                      "home-care",      10, 11, 11, ALL_ENVS, ["sort-laundry-by-color"], "Full laundry cycle — major independence leap."),

    # === DIGITAL (20 new) ===
    ("turn-device-on-off",           "Turn a device on/off and charge it",             "digital-literacy", 7, 11, 7,  ALL_ENVS,   [], "Physical device literacy."),
    ("type-own-name",                "Type your own name on a keyboard",               "digital-literacy", 7, 11, 7,  ALL_ENVS,   [], "Keyboard input basics."),
    ("open-close-app",               "Open and close an app",                          "digital-literacy", 7, 11, 7,  ALL_ENVS,   ["turn-device-on-off"], "OS navigation."),
    ("take-and-delete-photo",        "Take and delete a photo",                        "digital-literacy", 8, 11, 8,  ALL_ENVS,   ["turn-device-on-off"], "Ownership over own content."),
    ("use-kid-safe-search",          "Use a kid-safe search engine",                   "digital-literacy", 8, 11, 8,  ALL_ENVS,   ["open-close-app"], "First guided information retrieval."),
    ("adjust-volume-brightness",     "Adjust volume and brightness",                   "digital-literacy", 8, 11, 8,  ALL_ENVS,   ["turn-device-on-off"], "Self-regulation of the device."),
    ("passwords-are-private",        "Understand passwords are private",               "digital-literacy", 8, 11, 8,  ALL_ENVS,   [], "First security concept."),
    ("dont-share-personal-info",     "Never share personal info online",               "digital-literacy", 9, 11, 9,  ALL_ENVS,   ["passwords-are-private"], "Stranger-danger, internet edition."),
    ("ask-before-downloading",       "Ask permission before downloading",              "digital-literacy", 9, 11, 9,  ALL_ENVS,   [], "Guards against malware."),
    ("recognize-ad-banner",          "Recognize an ad vs organic content",             "digital-literacy", 9, 11, 10, ALL_ENVS,   ["open-close-app"], "Separates persuasion from information."),
    ("close-suspicious-popup",       "Close a pop-up or suspicious page",              "digital-literacy", 9, 11, 10, ALL_ENVS,   ["open-close-app"], "First-line device defence."),
    ("report-block-content",         "Report or block inappropriate content",          "digital-literacy", 9, 11, 10, ALL_ENVS,   [], "Digital citizenship in practice."),
    ("video-call-etiquette",         "Video-call etiquette (mute, camera, framing)",   "digital-literacy", 9, 11, 10, ALL_ENVS,   ["open-close-app"], "Remote communication skills."),
    ("respect-screen-time",          "Respect screen-time limits",                     "digital-literacy", 10, 11, 11, ALL_ENVS,  [], "Self-regulation — hardest digital skill."),
    ("create-strong-password",       "Create a strong password",                       "digital-literacy", 10, 11, 11, ALL_ENVS,  ["passwords-are-private"], "Account security basics."),
    ("spot-phishing-link",           "Spot a phishing link or fake login",             "digital-literacy", 10, 11, 11, ALL_ENVS,  ["recognize-ad-banner"], "Most common consumer cyber threat."),
    ("digital-footprint-awareness",  "Understand digital footprint (posts persist)",   "digital-literacy", 10, 11, 11, ALL_ENVS,  ["dont-share-personal-info"], "Future-self protection."),
    ("evaluate-source-credibility",  "Evaluate source credibility",                    "digital-literacy", 10, 11, 11, ALL_ENVS,  ["spot-phishing-link"], "Combats misinformation."),
    ("recognize-ai-generated-media", "Recognize AI-generated / deepfake content",      "digital-literacy", 10, 11, 11, ALL_ENVS,  ["evaluate-source-credibility"], "Modern critical literacy."),
    ("use-two-step-verification",    "Use two-step verification",                      "digital-literacy", 10, 11, 11, ALL_ENVS,  ["create-strong-password"], "Real-world account hardening."),

    # === NAVIGATION (20 new) ===
    ("know-full-name-address-phone", "Know full name, address, and parent phone",      "wayfinding", 7, 11, 7,  ALL_ENVS,   [], "Most basic lost-child recovery info."),
    ("know-parent-phone-memorized",  "Know parent phone number by heart",              "wayfinding", 7, 11, 7,  ALL_ENVS,   [], "Reachable from any unfamiliar phone."),
    ("identify-home-school-shop",    "Identify home, school, and nearest shop",        "wayfinding", 7, 11, 7,  ALL_ENVS,   [], "Mental map of their immediate world."),
    ("walk-to-mailbox-and-back",     "Walk to the mailbox/gate and back solo",         "wayfinding", 7, 11, 7,  ALL_ENVS,   [], "First supervised micro-trip."),
    ("look-both-ways",               "Look both ways before crossing",                 "wayfinding", 7, 11, 7,  ALL_ENVS,   [], "Reflex that saves lives."),
    ("cross-crosswalk-with-parent",  "Cross at a crosswalk with parent",               "wayfinding", 7, 11, 8,  ALL_ENVS,   ["look-both-ways"], "Rule-following in real traffic."),
    ("use-pedestrian-signal",        "Use a pedestrian signal correctly",              "wayfinding", 8, 11, 8,  URBAN_ONLY, ["cross-crosswalk-with-parent"], "Decodes urban infrastructure."),
    ("stranger-safety-basics",       "Stranger safety — who to trust",                 "wayfinding", 7, 11, 8,  ALL_ENVS,   [], "Situational judgment with adults."),
    ("dial-emergency-number",        "Dial the emergency number and give address",     "wayfinding", 8, 11, 8,  ALL_ENVS,   ["know-full-name-address-phone"], "Summons help when adults can't."),
    ("identify-landmarks-near-home", "Identify landmarks near home",                   "wayfinding", 8, 11, 9,  ALL_ENVS,   [], "Orients without a map or device."),
    ("follow-simple-sketch-map",     "Follow a simple sketch map",                     "wayfinding", 8, 11, 9,  ALL_ENVS,   ["identify-landmarks-near-home"], "Symbol-to-reality translation."),
    ("read-street-transit-signs",    "Read common street and transit signs",           "wayfinding", 8, 11, 9,  ALL_ENVS,   [], "Public-space literacy."),
    ("ride-bike-with-helmet",        "Ride a bike with helmet and road rules",         "wayfinding", 9, 11, 10, ALL_ENVS,   ["look-both-ways"], "First powered mobility."),
    ("take-bus-with-parent",         "Take a bus/train with parent",                   "wayfinding", 9, 11, 10, URBAN_ONLY, ["read-street-transit-signs"], "Public transit exposure."),
    ("buy-transit-ticket",           "Buy a transit ticket / tap a card",              "wayfinding", 10, 11, 11, URBAN_ONLY, ["take-bus-with-parent"], "Transaction + system combined."),
    ("cross-busy-intersection-solo", "Cross a busy intersection solo",                 "wayfinding", 10, 11, 11, URBAN_ONLY, ["use-pedestrian-signal"], "First high-stakes solo decision."),
    ("walk-to-friend-house-solo",    "Walk to a friend's house on known route",        "wayfinding", 10, 11, 11, ALL_ENVS,   ["cross-busy-intersection-solo", "identify-landmarks-near-home"], "First purposeful solo trip."),
    ("use-phone-maps-app",           "Use a phone maps app for directions",            "wayfinding", 10, 11, 11, ALL_ENVS,   ["follow-simple-sketch-map"], "Modern wayfinding tool."),
    ("plan-route-with-stops",        "Plan a route with stops and arrival time",       "wayfinding", 10, 11, 11, ALL_ENVS,   ["use-phone-maps-app"], "Full trip-planning cognition."),
    ("ride-transit-independently",   "Ride public transport independently",            "wayfinding", 11, 11, 11, URBAN_ONLY, ["take-bus-with-parent", "buy-transit-ticket"], "Real autonomy milestone."),

    # === COGNITIVE (20 new) ===
    ("follow-three-step-instruction", "Follow a 3-step instruction",                   "reasoning", 7, 11, 7,  ALL_ENVS,   [], "Working memory + sequencing."),
    ("tell-time-analog-clock",        "Tell time on an analog clock",                  "reasoning", 7, 11, 8,  ALL_ENVS,   [], "Translates a visual into a number."),
    ("use-calendar-find-date",        "Use a calendar to find a date",                 "reasoning", 7, 11, 8,  ALL_ENVS,   [], "Time beyond today."),
    ("sort-by-invented-rule",         "Sort objects by a rule you invent",             "reasoning", 7, 11, 8,  ALL_ENVS,   [], "Abstracts categories."),
    ("spot-pattern-in-sequence",      "Spot a pattern in a sequence",                  "reasoning", 8, 11, 9,  ALL_ENVS,   [], "Foundation of math and prediction."),
    ("summarize-short-story",         "Summarize a short story in 3 sentences",        "reasoning", 8, 11, 9,  ALL_ENVS,   [], "Compresses information."),
    ("ask-why-research-answer",       "Ask 'why?' and look up the answer",             "reasoning", 8, 11, 9,  ALL_ENVS,   [], "Curiosity becomes a habit."),
    ("explain-process-in-order",      "Explain a process in step-by-step order",       "reasoning", 8, 11, 9,  ALL_ENVS,   [], "Teaching others = deeper understanding."),
    ("estimate-before-measuring",     "Estimate before measuring",                     "reasoning", 9, 11, 10, ALL_ENVS,   [], "Builds number sense."),
    ("make-pros-cons-list",           "Make a pros/cons list",                         "reasoning", 9, 11, 10, ALL_ENVS,   [], "Externalizes decision-making."),
    ("set-personal-goal-weekly",      "Set a personal goal for the week",              "reasoning", 10, 11, 11, ALL_ENVS,  [], "Self-direction."),
    ("break-task-into-steps",         "Break a big task into smaller steps",           "reasoning", 10, 11, 11, ALL_ENVS,  ["set-personal-goal-weekly"], "Project decomposition."),
    ("manage-homework-schedule",      "Manage a simple homework schedule",             "reasoning", 10, 11, 11, ALL_ENVS,  ["break-task-into-steps", "use-calendar-find-date"], "Time management."),
    ("resolve-disagreement-words",    "Resolve a disagreement with words only",        "reasoning", 10, 11, 11, ALL_ENVS,  [], "Social cognition + impulse control."),
    ("accept-feedback-calmly",        "Accept feedback without shutting down",         "reasoning", 10, 11, 11, ALL_ENVS,  [], "Growth mindset in practice."),
    ("ask-clarifying-question",       "Ask a clarifying question when unsure",         "reasoning", 10, 11, 11, ALL_ENVS,  [], "Confident not-knowing."),
    ("decide-with-incomplete-info",   "Make a decision with incomplete information",   "reasoning", 10, 11, 11, ALL_ENVS,  ["make-pros-cons-list"], "Real-world reasoning."),
    ("detect-biased-argument",        "Detect a biased or one-sided argument",         "reasoning", 10, 11, 11, ALL_ENVS,  [], "Critical thinking starter."),
    ("spot-basic-logical-fallacy",    "Spot a basic logical fallacy",                  "reasoning", 10, 11, 11, ALL_ENVS,  ["detect-biased-argument"], "Resists poor persuasion."),
    ("teach-younger-kid-skill",       "Teach a younger child a skill you know well",   "reasoning", 10, 11, 11, ALL_ENVS,  ["explain-process-in-order"], "Consolidates mastery + empathy."),
]


HOW_TO_TEMPLATE = (
    "## {title}\n\n"
    "_Reviewer: expand this how-to before approving._\n\n"
    "1. Talk through why this skill matters before you start.\n"
    "2. Demonstrate it yourself, narrating each step.\n"
    "3. Let the child try while you observe — resist the urge to take over.\n"
    "4. Debrief: what was hard? what would they do differently?\n"
    "5. Mark complete once the child can do it without prompting.\n"
)


def _review_notes(benefit: str, ceiling_us: int) -> str:
    return (
        f"**Benefit:** {benefit}\n"
        f"**US mastery ceiling age:** {ceiling_us}\n"
        "_Auto-loaded from seed_full_catalog — expand how-to/safety, then approve._"
    )


class Command(BaseCommand):
    help = "Loads the full task catalog into the review queue (status=pending). Idempotent."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Ensuring environments…")
        for kind, _ in Environment.Kind.choices:
            Environment.objects.get_or_create(kind=kind)

        self.stdout.write("Ensuring tags…")
        tags: dict[str, Tag] = {}
        for key, display_name, category in TAGS:
            tag, _ = Tag.objects.get_or_create(name=display_name, defaults={"category": category})
            if tag.category != category:
                tag.category = category
                tag.save(update_fields=["category"])
            tags[key] = tag

        env_cache = {e.kind: e for e in Environment.objects.all()}

        self.stdout.write("Inserting new tasks as 'pending'…")
        new_count = 0
        skipped_count = 0
        for (slug, title, tag_key, lo, hi, ceiling_us, envs, _prereqs, benefit) in TASKS:
            parent_note = PARENT_NOTES.get(slug, "")
            task, created = Task.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "how_to_md": HOW_TO_TEMPLATE.format(title=title),
                    "safety_md": "Parent must be present for the first attempt.",
                    "parent_note_md": parent_note,
                    "min_age": lo,
                    "max_age": hi,
                    "status": ReviewStatus.PENDING,
                    "review_notes": _review_notes(benefit, ceiling_us),
                },
            )
            if created:
                task.environments.set([env_cache[e] for e in envs if e in env_cache])
                task.tags.set([tags[tag_key]])
                new_count += 1
            else:
                skipped_count += 1

        self.stdout.write("Linking prerequisites…")
        edge_count = 0
        for (slug, _title, _tag, _lo, _hi, _cu, _envs, prereqs, _benefit) in TASKS:
            try:
                to_task = Task.objects.get(slug=slug)
            except Task.DoesNotExist:
                continue
            for p_slug in prereqs:
                try:
                    from_task = Task.objects.get(slug=p_slug)
                except Task.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"  prereq missing: {p_slug} → {slug} (skipped)")
                    )
                    continue
                if PrerequisiteEdge.objects.filter(from_task=from_task, to_task=to_task).exists():
                    continue
                PrerequisiteEdge(from_task=from_task, to_task=to_task, is_mandatory=True).save()
                edge_count += 1

        pending_total = Task.objects.filter(status=ReviewStatus.PENDING).count()
        self.stdout.write(self.style.SUCCESS(
            f"Done. Inserted {new_count} new task(s) "
            f"(skipped {skipped_count} already present). "
            f"Added {edge_count} prerequisite edge(s). "
            f"Pending review: {pending_total}."
        ))
