"""Management command: refine the Financial task ladder.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py refine_financial_ladder

Four phases, all idempotent:
  1. Delete 4 duplicate stubs that overlap with richer age-5/6 versions
  2. Retune 14 existing age ranges into proper developmental stages
  3. Add 21 new tasks filling gaps at every tier
  4. Wire ~40 prerequisite edges connecting the ladder properly
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Phase 1 — Duplicates to delete (shallow stubs with better age-5/6 versions)
# ---------------------------------------------------------------------------

DELETE_SLUGS = [
    "identify-coins",          # duplicate of identify-coins-age6
    "count-coins-to-total",    # duplicate of count-small-money-age6
    "distinguish-need-want",   # duplicate of needs-vs-wants-age6
    "pay-cashier",             # duplicate of pay-at-shop-age6
]

# ---------------------------------------------------------------------------
# Phase 2 — Age range updates
# ---------------------------------------------------------------------------

AGE_RANGE_UPDATES = [
    ("recognize-currency-symbol",    6,  8),   # foundational recognition — start at 6
    ("count-change",                 8, 10),   # distinct from count-small-money-age6
    ("check-change",                 8, 10),
    ("donate-small-amount",          7, 10),   # widen earlier
    ("spot-ad-vs-content",           8, 11),   # widen earlier — kids see ads young
    ("track-savings-ledger",         9, 11),
    ("read-receipt",                 9, 11),
    ("compare-prices",               9, 11),
    ("recognize-scam-offer",         9, 12),   # widen earlier
    ("save-for-goal",               10, 12),
    ("calculate-simple-discount",   10, 12),
    ("estimate-grocery-total",      10, 12),
    ("compare-unit-prices",         11, 13),
    ("plan-weekly-budget",          11, 13),
]

# ---------------------------------------------------------------------------
# Phase 3 — New tasks (21 total)
# ---------------------------------------------------------------------------

NEW_TASKS = [
    # ── Age 5-6 (3 tasks) ───────────────────────────────────────────────
    {
        "slug": "coin-vs-note-age5",
        "title": "Know the Difference Between Coins and Notes",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show both** — place a coin and a note on the table. *This is a coin. "
            "This is a note. Both are money.*\n"
            "2. **Compare them** — coins are metal, small, round. Notes are paper, bigger, rectangular.\n"
            "3. **Higher or lower value?** — usually notes are worth more than coins. "
            "A ₹10 coin and a ₹10 note have the same value, but a ₹100 note is worth far more "
            "than any coin.\n"
            "4. **Sort the wallet** — mix up some coins and small notes. "
            "Sort into two piles: coins, notes.\n"
            "5. **Daily quiz** — point to money in a shop or at home. *Coin or note?*"
        ),
        "parent_note_md": (
            "Distinguishing coins from notes is the first classification skill in money "
            "handling. Children who can do this confidently are ready to think about "
            "denominations and values more seriously."
        ),
    },
    {
        "slug": "money-is-earned-age6",
        "title": "Understand That Money is Earned by Working",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the chain** — *Parents go to work. People pay parents money for the work. "
            "Parents use that money to buy food, clothes, toys, and pay for our home.*\n"
            "2. **Name the work** — what do their parents actually do? "
            "Make it concrete: teaching, selling, building, coding, caring.\n"
            "3. **Other jobs they see** — shopkeeper, bus driver, doctor, builder. "
            "Each person is earning money by doing something.\n"
            "4. **Contrast with gifts** — birthday money from grandparents is a gift. "
            "Pocket money for chores is earned. Both are money, but they come differently.\n"
            "5. **Their first earn** — agree on one small task (tidying toys, feeding a pet) "
            "they can do to earn a small coin. Let them feel the difference."
        ),
        "parent_note_md": (
            "The most important financial concept a child can internalise early is that "
            "money is earned, not granted. Children who understand this make better "
            "spending decisions, feel less entitled, and develop a work ethic that "
            "supports adult financial life."
        ),
    },
    {
        "slug": "recognise-bigger-notes-age6",
        "title": "Recognise Larger Notes by Sight",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Lay out every denomination** — ₹10, ₹20, ₹50, ₹100, ₹200, ₹500 notes side by side. "
            "Even if they can't read yet, they can recognise colour and size.\n"
            "2. **Point and name** — *This blue one is ₹100. This orange is ₹10.* "
            "Repeat several times.\n"
            "3. **Which is worth more?** — place two notes side by side. "
            "*Which can buy more?*\n"
            "4. **Relative values** — *A ₹100 note is worth ten ₹10 notes.* "
            "Use real notes to show this if possible.\n"
            "5. **Quiz daily for a week** — hold up a note, they name it. "
            "Build to instant recognition."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Teach: we never put money in our mouths or throw it around — "
            "not because it's dirty, but because it is important and needs respect."
        ),
        "parent_note_md": (
            "Recognising higher-value notes is crucial for a child who may be handed "
            "money by a relative or asked to pay at a shop. A child who can tell ₹500 "
            "from ₹50 at a glance is much harder to shortchange and builds genuine "
            "financial competence."
        ),
    },
    # ── Age 7-8 (4 tasks) ───────────────────────────────────────────────
    {
        "slug": "simple-change-making-age7",
        "title": "Work Out Change from a Small Amount",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start simple** — *The toy costs ₹7. You give ₹10. How much should come back?* "
            "Use real coins to work it out physically first.\n"
            "2. **Counting up method** — from 7, count up to 10. That's 3. "
            "Change = ₹3. This is how real cashiers do it.\n"
            "3. **Practice with ₹20 and ₹50** — *Item is ₹14. You pay ₹20. What's the change?* "
            "Work up to ₹50.\n"
            "4. **The mental check** — teach them to always estimate before handing over "
            "money. *I expect about ₹3 back.*\n"
            "5. **Real purchase** — at a shop, before the cashier gives change, "
            "whisper to them: *How much should come back?*"
        ),
        "parent_note_md": (
            "Working out change teaches subtraction in a real-world context and "
            "prepares children to notice when they've been given the wrong amount. "
            "The counting-up method is the fastest mental tool; teach it explicitly "
            "rather than expecting them to find it."
        ),
    },
    {
        "slug": "pocket-money-basics-age7",
        "title": "Understand and Manage Pocket Money",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Agree the amount and frequency** — e.g., ₹20 every Sunday. "
            "Consistency matters more than amount.\n"
            "2. **Link it to something** — completing daily chores, school-week behaviour. "
            "Earned, not automatic.\n"
            "3. **Three-bucket rule** — save a bit, spend a bit, give a bit. "
            "Even dividing ₹20 into ₹10 save / ₹8 spend / ₹2 donate teaches the principle.\n"
            "4. **Let them spend badly** — if they blow it all on sweets in one day, "
            "don't top them up. Let them wait until next Sunday. That is the lesson.\n"
            "5. **Track it together** — at the end of each month, how much did they "
            "save? What did they spend it on? Were they glad of the choices?"
        ),
        "parent_note_md": (
            "Pocket money is the earliest real financial classroom. Children who are "
            "given it with structure — earned, split into buckets, fully theirs to spend "
            "or save — build practical money skills no textbook can teach. The single "
            "most important rule is: once it's given, it is theirs to succeed or fail with."
        ),
    },
    {
        "slug": "earn-by-small-task-age7",
        "title": "Earn a Small Amount by Doing a Task",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Agree the task** — beyond regular chores, something extra: washing the car, "
            "watering a neighbour's plants, sorting a drawer, a small garden job.\n"
            "2. **Agree the price up front** — ₹20 for washing the car. Written or shaken on. "
            "This is a simple contract.\n"
            "3. **Complete the task properly** — not half-done. The standard was agreed. "
            "If it isn't met, they fix it before payment.\n"
            "4. **Pay them in cash** — they feel the money in their hand. "
            "This matters far more than digital transfer at this age.\n"
            "5. **Reflect** — was it worth the time? Would they do it again? "
            "*Earning ₹20 took 30 minutes* is a real lesson about time and money."
        ),
        "parent_note_md": (
            "Earned money is spent differently than gifted money — children instinctively "
            "value it more. The first time a child works for real payment, even a small "
            "amount, something fundamental shifts in their relationship with money. "
            "Make it real: agreed price, completed standard, cash in hand."
        ),
    },
    {
        "slug": "payment-methods-awareness-age8",
        "title": "Learn the Different Ways People Pay for Things",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Watch real transactions** — at a shop, notice what you or other customers "
            "use. Cash? Card? Phone QR scan?\n"
            "2. **Name each method** — cash, debit card, credit card, UPI (Google Pay/PhonePe), "
            "wallet (Paytm). Each is a way to pay.\n"
            "3. **What's behind each?** — cash is physical money. Cards and UPI take money "
            "from a bank account. Credit cards borrow money that must be paid back.\n"
            "4. **Advantages and limits** — cash doesn't need signal but can be lost. "
            "UPI is fast but needs a phone. Cards work abroad. Discuss trade-offs.\n"
            "5. **Watch a full UPI scan** — let them watch an adult scan a QR code, "
            "enter the amount, and send. See the receipt on both sides."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never scan a QR code from someone you don't trust — it can be fake.\n"
            "- Never share a PIN, OTP, or password with anyone, even someone who says "
            "they're from the bank. Banks never ask for these over phone."
        ),
        "parent_note_md": (
            "India has moved to UPI/digital payments faster than almost anywhere in the "
            "world. A child who doesn't understand digital payments is financially "
            "illiterate for today's economy. Awareness at 8 sets the stage for safe use at 12."
        ),
    },
    # ── Age 9-10 (3 tasks) ──────────────────────────────────────────────
    {
        "slug": "what-is-a-bank-age9",
        "title": "Understand What a Bank Is and What It Does",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The core idea** — a bank is a safe place to keep money. "
            "Instead of cash under the mattress, money lives in an account.\n"
            "2. **What else banks do** — they pay you a little extra (interest) for keeping "
            "your money with them. They also lend money to people who need it (loans).\n"
            "3. **Visit a real branch** — walk in together. Look at the counters, "
            "the locker area if visible, the teller windows. Ask an official if they can "
            "explain to a curious child.\n"
            "4. **Look at a bank statement** — using a parent's with permission. "
            "Deposits are money in. Withdrawals are money out. Balance is what's left.\n"
            "5. **Imagine their future account** — *When you turn 14, you can open your own account. "
            "What do you think you'd save for?*"
        ),
        "parent_note_md": (
            "Understanding banks early demystifies the financial system. Children who "
            "have been inside a branch, seen a statement, and understand why banks pay "
            "interest are not intimidated by their first account at 14. They are ready."
        ),
    },
    {
        "slug": "digital-payment-awareness-age9",
        "title": "Recognise UPI, QR Codes, and Card Payments",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The QR code everywhere** — notice QR codes at every shop, restaurant, "
            "and stall. Each one says *scan me to pay*.\n"
            "2. **Watch a UPI payment** — a parent scans, enters amount, presses send. "
            "Both phones buzz. Trace the flow: money went from one bank account to another.\n"
            "3. **Card at the POS machine** — *tap* or *insert* card. PIN. Receipt. "
            "Again, money moved from bank account to shop.\n"
            "4. **No physical money changed hands** — yet something real happened. "
            "The bank account now has less; the shop's has more.\n"
            "5. **Practise reading the confirmation** — after any payment, read the SMS "
            "or app notification. Amount, time, recipient."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never click a *payment* link someone sends you — real payments don't need you to click.\n"
            "- Double-check the name on the payment screen before confirming any transfer.\n"
            "- Small test amounts first when paying a new merchant."
        ),
        "parent_note_md": (
            "Awareness of how digital payments work — without actually having access to a "
            "payment method at age 9 — gives children the vocabulary and protection "
            "against scams. They understand something real is happening behind the tap."
        ),
    },
    {
        "slug": "save-for-medium-goal-age10",
        "title": "Save for a Goal That Takes Several Weeks",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a real goal** — a book, a game, a specific toy. "
            "Something that costs 4–8 weeks of their pocket money.\n"
            "2. **Calculate the weeks** — cost ÷ weekly saving = number of weeks. "
            "Write it on a calendar so they can see the target.\n"
            "3. **Visible progress tracker** — a savings jar with a marked line, "
            "or a printed thermometer chart. Fill it as they save.\n"
            "4. **Resist the temptation** — halfway there, they'll want to spend on something else. "
            "Coach them through the discomfort. *The goal is still the goal.*\n"
            "5. **The moment of purchase** — when they reach it, they buy it themselves. "
            "The item will feel different because they waited."
        ),
        "parent_note_md": (
            "Saving for weeks — not days — is the first real exercise in delayed "
            "gratification with money. Studies show that children who can save for "
            "multi-week goals develop far better financial discipline as adults. "
            "Don't rescue them if they slip; let them restart."
        ),
    },
    # ── Age 11-12 (4 tasks) ─────────────────────────────────────────────
    {
        "slug": "subscription-hidden-costs-age11",
        "title": "Spot Subscriptions and Hidden In-App Costs",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Audit what the family pays for** — list every subscription the house pays: "
            "Netflix, Hotstar, Prime, Spotify, mobile data, game subscriptions, school apps.\n"
            "2. **Calculate the annual cost** — monthly × 12. A ₹199/month subscription "
            "is ₹2,388 a year. That number surprises most people.\n"
            "3. **Free-to-play reality** — free mobile games earn money from in-app purchases. "
            "Look at three such games, list what you can buy and what it costs.\n"
            "4. **Auto-renewal awareness** — trial offers often auto-renew at full price. "
            "Show how to find and cancel a subscription before the trial ends.\n"
            "5. **The 'is it worth it?' test** — for each subscription, is the use enough to "
            "justify the annual cost? Would it be missed if cancelled for a month?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never link a parent's card or UPI to a game account without permission.\n"
            "- *Free* games almost always have paid shortcuts. That is the business model."
        ),
        "parent_note_md": (
            "Subscriptions and in-app purchases are the primary way money leaks from "
            "households without notice. Children who understand the mechanics are less "
            "likely to accidentally rack up bills and more equipped as adults to audit "
            "their own recurring charges."
        ),
    },
    {
        "slug": "online-shopping-compare-age11",
        "title": "Compare the Same Product Online and Pick the Best Deal",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a real product** — a specific book, toy, gadget, or pair of shoes.\n"
            "2. **Check at least 3 places** — Amazon, Flipkart, the brand's own site, "
            "local shops. Same exact product.\n"
            "3. **Compare beyond price** — shipping cost, delivery time, return policy, "
            "seller rating. The cheapest isn't always best.\n"
            "4. **Read one review and one complaint** — get a feel for the product's "
            "real-world performance.\n"
            "5. **Make the recommendation** — best place to buy, and why. "
            "Present to a parent like a mini-report."
        ),
        "parent_note_md": (
            "Online comparison shopping is a skill most adults use daily but were never "
            "taught. Children who can do it properly — checking multiple sites, "
            "considering total cost including shipping, reading reviews critically — "
            "save significant money over a lifetime and make better purchase decisions."
        ),
    },
    {
        "slug": "understand-family-budget-age12",
        "title": "Understand How a Family Budget Works",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The total picture** — parent shares (in rough terms) monthly income. "
            "Specifics are optional; the concept is the goal.\n"
            "2. **Major expense categories** — rent/home loan, food, school fees, bills, "
            "transport, insurance, savings. Rough percentages of income for each.\n"
            "3. **Fixed vs variable** — rent is fixed. Food varies. Discretionary (eating out, "
            "holidays) is optional. Each has different flexibility.\n"
            "4. **What's left for extras** — after essentials, how much is left? "
            "Where does savings go?\n"
            "5. **The teenager's asks in context** — a new phone, a holiday, a bike — "
            "how do these fit? Not to refuse requests but to teach proportion."
        ),
        "parent_note_md": (
            "Most teenagers ask for things without any sense of household finances. "
            "A single open conversation — at an age-appropriate level — changes this "
            "permanently. Children who have seen a family budget make fewer entitled "
            "demands and show more genuine gratitude for what they receive."
        ),
    },
    {
        "slug": "first-paid-chore-age12",
        "title": "Complete a Paid Job for Someone Outside the Family",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a small opportunity** — helping a neighbour with shopping, "
            "walking a dog, tutoring a younger child, helping at a family friend's shop.\n"
            "2. **Negotiate the price yourself** — not the parent. "
            "They state what they'll do and what they expect to be paid.\n"
            "3. **Do the job well** — on time, to the quality expected. "
            "Reputation is earned one job at a time.\n"
            "4. **Invoice and collect** — a handwritten note: *For walking the dog 3 times "
            "this week — ₹150.* Collect the money directly.\n"
            "5. **Reflect and record** — how much per hour did that work out to? "
            "Would they take it on again? Keep a log of every paid job."
        ),
        "parent_note_md": (
            "A 12-year-old's first paid job outside the family is a milestone experience. "
            "It builds negotiation, delivery-on-promise, and the satisfaction of being "
            "paid for real work by someone who wasn't obligated to. The learning far "
            "exceeds the money earned."
        ),
    },
    # ── Age 13-14 (3 tasks) ─────────────────────────────────────────────
    {
        "slug": "digital-vs-cash-awareness-age13",
        "title": "Know Why Digital Spending Feels Different from Cash",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The research** — look up one study (there are many) showing people "
            "spend 20–50% more when paying digitally than cash.\n"
            "2. **Why it happens** — cash feels tangible; tapping a card or phone "
            "doesn't feel like losing something. This is called the *pain of paying*.\n"
            "3. **Self-experiment** — for one week, use only cash for all discretionary spending. "
            "For the next week, use only UPI. Track total spending.\n"
            "4. **Notice the feeling** — what was different? Did they spend more/less? "
            "Did anything feel different in the moment of paying?\n"
            "5. **Build a personal rule** — based on the experiment, what rule will they "
            "set for themselves? E.g., *always check the balance before tapping.*"
        ),
        "parent_note_md": (
            "The psychological difference between cash and digital spending is one of "
            "the most well-documented findings in behavioural economics. Teenagers who "
            "understand this before they have their own UPI and card are dramatically "
            "less likely to overspend when they do."
        ),
    },
    {
        "slug": "track-week-own-spending-age13",
        "title": "Track Every Rupee You Spend for One Week",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The tool** — a notebook, a note on their phone, or a free spending-tracker app. "
            "Whichever they'll actually use.\n"
            "2. **Record every purchase** — even ₹5 for a chocolate. Date, amount, category. "
            "No minimum.\n"
            "3. **Categories** — food/snacks, transport, entertainment, gifts, other. "
            "Five is enough.\n"
            "4. **End-of-week totals** — add by category. Which was biggest? "
            "What's the total for the week?\n"
            "5. **The one insight** — what surprised them? Often the food/snacks total "
            "shocks teenagers. That's the value of the exercise."
        ),
        "parent_note_md": (
            "A one-week spending track is the simplest path to financial self-awareness. "
            "It's also the precursor to monthly budgeting at 14. Teenagers who have "
            "done this — honestly — are never quite as careless with money afterwards. "
            "The numbers are their own wake-up call."
        ),
    },
    {
        "slug": "save-for-bigger-goal-age14",
        "title": "Save for a Goal That Takes Three or More Months",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a meaningful goal** — a musical instrument, a bike, a weekend trip, "
            "a specific phone. Something that genuinely matters.\n"
            "2. **Calculate with precision** — cost ÷ monthly saving capacity = months. "
            "Be realistic about the saving rate.\n"
            "3. **Keep it in a separate account or envelope** — out of sight, out of mind. "
            "If the savings mix with spending money, they disappear.\n"
            "4. **Monthly check-in** — how is progress? Does the plan need adjustment? "
            "Can they save more? Are there unexpected costs?\n"
            "5. **Resist the tempting alternatives** — 3+ months gives plenty of time for "
            "other desires to pop up. The test is staying with the original goal."
        ),
        "parent_note_md": (
            "Saving for a multi-month goal is a serious exercise in discipline. "
            "Teenagers who complete one arrive at larger financial goals (university fees, "
            "a car, a home deposit) knowing the process works. Those who have only saved "
            "for short-term treats often flounder with big goals as adults."
        ),
    },
    # ── Age 14-16 (2 tasks) ─────────────────────────────────────────────
    {
        "slug": "opportunity-cost-age14",
        "title": "Understand Opportunity Cost in Real Decisions",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The definition** — opportunity cost is what you give up by choosing "
            "one thing over another. Every choice has one.\n"
            "2. **Money examples** — ₹2000 spent on a new game = the trip that could have "
            "been, the book stack, the month's savings goal.\n"
            "3. **Time examples** — 2 hours of scrolling = the piano practice not done, "
            "the project that's still behind.\n"
            "4. **Apply to a real current decision** — something they're choosing about this month. "
            "Explicitly name what is being given up.\n"
            "5. **The reframe** — good decisions account for what you're giving up, "
            "not just what you're getting."
        ),
        "parent_note_md": (
            "Opportunity cost is the single most powerful economic concept, and it "
            "applies to every decision — financial, social, time-based. Teenagers who "
            "think in these terms make consistently better choices because they see "
            "what they're actually trading. This is the heart of adult decision-making."
        ),
    },
    {
        "slug": "manage-subscriptions-age15",
        "title": "Track and Manage Your Recurring Subscriptions",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **List every subscription** — streaming, gaming, productivity, "
            "storage, anything paid monthly or annually.\n"
            "2. **Calculate the annual total** — monthly × 12 plus any annual. "
            "The total is almost always more than expected.\n"
            "3. **Rate each one** — used often / used sometimes / barely used. "
            "Anything in the last category is a candidate to cancel.\n"
            "4. **Cancel what isn't worth it** — actually cancel, not intend to cancel. "
            "Go to the account, find the subscription, cancel.\n"
            "5. **Calendar the renewals** — add each renewal date to their calendar. "
            "Review before auto-renewal happens."
        ),
        "parent_note_md": (
            "Managing subscriptions is one of the most overlooked financial skills. "
            "Most adults pay for things they don't use because they never audit. "
            "A teenager who builds this habit now — reviewing and pruning recurring "
            "charges — saves significant money over a lifetime."
        ),
    },
    # ── Age 16-18 (2 tasks) ─────────────────────────────────────────────
    {
        "slug": "compare-bank-accounts-age16",
        "title": "Compare Bank Accounts and Choose One Systematically",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Shortlist three banks** — two mainstream (SBI, HDFC, ICICI, Axis) and "
            "one newer digital bank. Use official websites only.\n"
            "2. **Build a comparison table** — minimum balance, ATM charges, online banking "
            "features, debit card annual fee, interest on savings, customer service rating.\n"
            "3. **Read the terms** — what happens if the minimum balance isn't maintained? "
            "What hidden fees exist? This is where banks differ most.\n"
            "4. **Match to their needs** — a student with little cash needs zero-balance "
            "options. Someone travelling needs international ATM access.\n"
            "5. **Make and justify the choice** — write a paragraph explaining why they'd "
            "choose this bank for this stage of life. A proper reasoned decision."
        ),
        "parent_note_md": (
            "Most adults choose their bank by accident — because parents banked there, "
            "or because a branch was nearby. A teenager who makes a deliberate, "
            "researched choice has a different relationship with their bank and with "
            "all future financial products. The skill transfers to insurance, loans, "
            "and everything else."
        ),
    },
    {
        "slug": "understand-emi-loans-age16",
        "title": "Understand How Loans and EMIs Actually Work",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The loan equation** — borrow ₹X at Y% interest for Z years. "
            "What will you pay back in total? Usually far more than X.\n"
            "2. **Use an EMI calculator** — online EMI calculators are free. "
            "Try: ₹10 lakh home loan at 9% for 20 years. What's the monthly EMI? "
            "What's the total paid?\n"
            "3. **Principal vs interest** — early EMIs are mostly interest; "
            "later EMIs are mostly principal. Look at an amortisation schedule.\n"
            "4. **Types of loans** — home, car, personal, education, credit card revolving. "
            "Each has typical interest rates and term lengths. Compare them.\n"
            "5. **The golden rule** — only borrow for things that appreciate or earn "
            "(education, home). Never borrow for depreciating items (phones, holidays)."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Credit card interest rates in India are 36–42% per year — catastrophic "
            "if not paid off monthly.\n"
            "- *Pre-approved* loan offers are not free money — they are marketing.\n"
            "- Never co-sign or guarantee a loan for anyone without understanding the full liability."
        ),
        "parent_note_md": (
            "EMIs and loans are the biggest financial commitments most adults ever make. "
            "A teenager who understands the mechanics — that ₹10 lakh borrowed costs "
            "₹22 lakh to repay, that credit card debt compounds viciously, that you "
            "only borrow for appreciating assets — enters adulthood with an enormous "
            "advantage over peers who learn this the hard way."
        ),
    },
]

# ---------------------------------------------------------------------------
# Phase 4 — Prerequisite edges: (to_slug, from_slug, mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    # Existing-task chains that were missing
    ("save-for-goal",                     "save-for-treat-age5",              True),
    ("track-savings-ledger",              "piggy-bank-habit-age6",            True),
    ("read-price-tag",                    "recognize-currency-symbol",        True),
    ("open-bank-account-age14",           "pay-at-shop-age6",                 True),
    ("track-spending-month-age14",        "track-savings-ledger",             True),
    ("create-monthly-budget-age14",       "plan-weekly-budget",               True),
    ("understand-interest-age14",         "save-for-goal",                    True),
    ("invest-basics-age15",               "understand-interest-age14",        True),
    ("read-payslip-tax-age15",            "understand-interest-age14",        True),
    ("negotiate-price-age15",             "compare-prices",                   True),
    ("emergency-fund-plan-age15",         "create-monthly-budget-age14",      True),
    ("understand-insurance-age16",        "emergency-fund-plan-age15",        True),
    ("understand-credit-score-age16",     "understand-interest-age14",        True),
    ("tax-return-basics-age16",           "read-payslip-tax-age15",           True),
    ("earn-and-manage-income-age16",      "earn-outside-home-age14",          True),
    ("read-receipt",                      "count-change",                     True),
    ("spot-ad-vs-content",                "needs-vs-wants-age6",              True),
    ("recognize-scam-offer",              "spot-ad-vs-content",               True),

    # New task chains
    ("money-is-earned-age6",              "money-is-for-buying-age5",         True),
    ("recognise-bigger-notes-age6",       "identify-coins-age6",              True),
    ("coin-vs-note-age5",                 "money-is-for-buying-age5",         True),
    ("simple-change-making-age7",         "count-small-money-age6",           True),
    ("pocket-money-basics-age7",          "save-for-treat-age5",              True),
    ("earn-by-small-task-age7",           "money-is-earned-age6",             True),
    ("payment-methods-awareness-age8",    "pay-at-shop-age6",                 True),
    ("what-is-a-bank-age9",               "piggy-bank-habit-age6",            True),
    ("digital-payment-awareness-age9",    "payment-methods-awareness-age8",   True),
    ("save-for-medium-goal-age10",        "piggy-bank-habit-age6",            True),
    ("subscription-hidden-costs-age11",   "digital-payment-awareness-age9",   True),
    ("online-shopping-compare-age11",     "compare-prices",                   True),
    ("understand-family-budget-age12",    "needs-vs-wants-age6",              True),
    ("first-paid-chore-age12",            "earn-by-small-task-age7",          True),
    ("digital-vs-cash-awareness-age13",   "digital-payment-awareness-age9",   True),
    ("track-week-own-spending-age13",     "track-savings-ledger",             True),
    ("save-for-bigger-goal-age14",        "save-for-medium-goal-age10",       True),
    ("opportunity-cost-age14",            "understand-family-budget-age12",   True),
    ("manage-subscriptions-age15",        "subscription-hidden-costs-age11",  True),
    ("compare-bank-accounts-age16",       "what-is-a-bank-age9",              True),
    ("compare-bank-accounts-age16",       "compare-financial-products-age15", True),
    ("understand-emi-loans-age16",        "understand-interest-age14",        True),
    ("earn-outside-home-age14",           "first-paid-chore-age12",           True),
    ("budget-large-purchase-age16",       "save-for-bigger-goal-age14",       True),
]


class Command(BaseCommand):
    help = "Refine the Financial task ladder: dedupe, retune ages, add new tasks, wire DAG."

    def handle(self, *args, **options):
        financial_tag = Tag.objects.filter(
            name="Money basics", category=Tag.Category.FINANCIAL
        ).first()
        if not financial_tag:
            financial_tag, _ = Tag.objects.get_or_create(
                name="Money basics",
                defaults={"category": Tag.Category.FINANCIAL},
            )

        all_envs = list(Environment.objects.all())

        # ── Phase 1 — Delete duplicates ─────────────────────────────────
        deleted = 0
        for slug in DELETE_SLUGS:
            qs = Task.objects.filter(slug=slug)
            if qs.exists():
                qs.delete()
                deleted += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"  Phase 1: {slug} already gone, skipping")
                )
        self.stdout.write(f"Phase 1: deleted {deleted} duplicate tasks.")

        # ── Phase 2 — Retune age ranges ─────────────────────────────────
        retuned = 0
        for slug, new_min, new_max in AGE_RANGE_UPDATES:
            updated = Task.objects.filter(slug=slug).update(
                min_age=new_min, max_age=new_max
            )
            if updated:
                retuned += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"  Phase 2: {slug} not found, skipping")
                )
        self.stdout.write(f"Phase 2: retuned age ranges on {retuned} tasks.")

        # ── Phase 3 — Add new tasks ─────────────────────────────────────
        added = 0
        for t in NEW_TASKS:
            task, _ = Task.objects.update_or_create(
                slug=t["slug"],
                defaults={
                    "title": t["title"],
                    "how_to_md": t["how_to_md"],
                    "parent_note_md": t.get("parent_note_md", ""),
                    "safety_md": t.get("safety_md", ""),
                    "min_age": t["min_age"],
                    "max_age": t["max_age"],
                    "sex_filter": t.get("sex_filter", "any"),
                    "status": ReviewStatus.APPROVED,
                },
            )
            task.tags.set([financial_tag])
            task.environments.set(all_envs)
            added += 1
        self.stdout.write(f"Phase 3: upserted {added} new financial tasks.")

        # ── Phase 4 — Wire prerequisite DAG ─────────────────────────────
        created_edges = 0
        skipped_edges = 0
        for to_slug, from_slug, mandatory in PREREQ_EDGES:
            to_task = Task.objects.filter(slug=to_slug).first()
            from_task = Task.objects.filter(slug=from_slug).first()
            if not to_task or not from_task:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Phase 4: edge {from_slug} → {to_slug} — task not found, skipping"
                    )
                )
                skipped_edges += 1
                continue
            _, created = PrerequisiteEdge.objects.get_or_create(
                from_task=from_task,
                to_task=to_task,
                defaults={"is_mandatory": mandatory},
            )
            if created:
                created_edges += 1
        self.stdout.write(
            f"Phase 4: added {created_edges} new prerequisite edges ({skipped_edges} skipped)."
        )

        self.stdout.write(self.style.SUCCESS("refine_financial_ladder complete."))
