"""Management command: seed age-14 tasks across all six categories.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_age14_catalog

Idempotent — safe to re-run. Uses update_or_create throughout.
Age 14 tasks are more independent, self-directed, and real-world focused.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Tasks grouped by category
# ---------------------------------------------------------------------------

FINANCIAL_TASKS = [
    {
        "slug": "open-bank-account-age14",
        "title": "Open a Junior Bank Account",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Research options together** — look at two or three banks or fintech apps "
            "that offer accounts for under-18s. Compare: fees, app quality, features.\n"
            "2. **Gather documents** — identify what is needed: ID (school ID, birth certificate), "
            "parent's ID, address proof. Collect them before going.\n"
            "3. **Visit or apply online** — go to the branch or complete the online form. "
            "The teenager leads — parent is present but not doing it for them.\n"
            "4. **Understand the account** — once open, review together: "
            "What is the account number? What is the IFSC? How do you check the balance?\n"
            "5. **First transaction** — deposit a small amount (pocket money or a gift). "
            "Verify it appears in the statement."
        ),
        "parent_note_md": (
            "Having a bank account at 14 is the gateway to financial independence. "
            "It teaches statement reading, balance awareness, and the basic mechanics of "
            "the banking system before the stakes are high. Resist managing the account for "
            "them — let them operate it from day one."
        ),
        "prereqs": [],
    },
    {
        "slug": "track-spending-month-age14",
        "title": "Track Every Expense for One Month",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a method** — notebook, spreadsheet, or a free budgeting app. "
            "The tool matters less than consistency.\n"
            "2. **Record every purchase** — date, item, amount. No minimum — even ₹5 goes in.\n"
            "3. **Categorise at the end of each week** — food, transport, entertainment, "
            "clothes, other. Totals per category.\n"
            "4. **Monthly review** — add up totals. Which category surprised them most? "
            "Where did the most money go?\n"
            "5. **One insight** — identify one spending pattern they want to change. "
            "Not a rule imposed by the parent — one they choose themselves."
        ),
        "parent_note_md": (
            "Most adults have never tracked their spending for a full month. Those who have "
            "are almost always surprised by what they find. This exercise builds financial "
            "self-awareness — the foundation of every budgeting skill. The surprise is the "
            "lesson; do not pre-empt it by telling them where they will overspend."
        ),
        "prereqs": [],
    },
    {
        "slug": "create-monthly-budget-age14",
        "title": "Create a Simple Monthly Budget",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **List income** — pocket money, earnings from tasks, birthday money averaged "
            "over the year. Total monthly income.\n"
            "2. **List fixed expenses** — things that happen every month regardless: "
            "bus pass, phone top-up, subscriptions.\n"
            "3. **Estimate variable expenses** — food, entertainment, clothes. "
            "Use last month's tracking data if available.\n"
            "4. **Income minus expenses** — is there anything left? If not, where can "
            "something be reduced?\n"
            "5. **Set one savings goal** — a specific amount to put aside each month. "
            "Even ₹100 demonstrates the principle."
        ),
        "parent_note_md": (
            "A budget is simply a spending plan made in advance. Teenagers who learn to "
            "build one — even on a small income — are far better prepared for managing "
            "rent, bills, and a salary as adults. The skill is the process, not the numbers. "
            "Walk through your own budget briefly to show it is something adults use too."
        ),
        "prereqs": ["track-spending-month-age14"],
    },
    {
        "slug": "understand-interest-age14",
        "title": "Understand How Interest Works on Savings and Debt",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Savings interest** — if you keep ₹1000 in a savings account at 5% per year, "
            "you earn ₹50 after a year without doing anything. Show the maths.\n"
            "2. **Debt interest** — if you borrow ₹1000 on a credit card at 36% per year "
            "and pay nothing, after a year you owe ₹1360. Show the maths.\n"
            "3. **Compound interest** — show what happens over 5 years in both cases. "
            "Use a simple calculator or spreadsheet together.\n"
            "4. **The rule of 72** — divide 72 by the interest rate to find how many years "
            "to double money. E.g., 8% → 9 years.\n"
            "5. **Apply to real products** — look up the actual interest rate on a local "
            "savings account and a credit card. Compare."
        ),
        "parent_note_md": (
            "Interest is the mechanism behind both wealth-building and debt traps. "
            "Teenagers who understand compound interest are far less likely to carry "
            "credit card balances as adults — and far more likely to start saving early. "
            "The visual of a number growing (or exploding) over time makes this concrete."
        ),
        "prereqs": [],
    },
    {
        "slug": "earn-outside-home-age14",
        "title": "Earn Money from an Outside Source",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Identify options** — tutoring younger children, helping neighbours, "
            "dog walking, freelance design or video editing, selling crafts or baked goods.\n"
            "2. **Define the service and price** — what exactly will they offer? "
            "What is a fair price? Research what others charge.\n"
            "3. **First customer** — find one person to pay for the service. "
            "Parent can help identify the first opportunity but should not do the work.\n"
            "4. **Deliver and collect payment** — complete the task, invoice if relevant, "
            "collect and record the payment.\n"
            "5. **Reflect** — how long did it take? Was the price fair? What would they "
            "do differently? This is the foundation of understanding earned income."
        ),
        "parent_note_md": (
            "Earning outside the home — even a small amount — changes a teenager's "
            "relationship with money permanently. Earned money is spent differently from "
            "gifted money. The experience of pricing, delivering, and being paid for "
            "something teaches more financial literacy in one transaction than any lesson."
        ),
        "prereqs": [],
    },
]

HOUSEHOLD_TASKS = [
    {
        "slug": "cook-full-meal-age14",
        "title": "Cook a Complete Meal from Start to Finish",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a realistic recipe** — something with a protein, a carbohydrate, "
            "and a vegetable. Not a snack — a real meal for the family.\n"
            "2. **Plan before shopping** — read the full recipe first. Write the ingredient "
            "list. Check what is already in the kitchen.\n"
            "3. **Cook independently** — parent is available for questions but does not "
            "take over. Let them manage timing, heat, and taste themselves.\n"
            "4. **Serve it** — they plate and serve. The family eats it.\n"
            "5. **Clean up** — cooking includes washing up and wiping surfaces. "
            "The meal is not done until the kitchen is clean."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Always turn pan handles inward so they cannot be knocked off the stove.\n"
            "- Use oven gloves — not tea towels — for anything coming out of the oven.\n"
            "- Never leave the kitchen while oil is heating.\n"
            "- Know where the fire extinguisher or fire blanket is before starting."
        ),
        "parent_note_md": (
            "A teenager who can cook a complete meal is functionally independent for one "
            "of the most basic human needs. Beyond nutrition, cooking builds planning, "
            "timing, chemistry intuition, and the satisfaction of making something from "
            "scratch. Make this a weekly expectation, not a one-off event."
        ),
        "prereqs": [],
    },
    {
        "slug": "do-own-laundry-age14",
        "title": "Do a Full Load of Laundry Independently",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Sort clothes** — darks, lights, and delicates go in separate loads. "
            "Show the labels: the symbols explain washing temperature.\n"
            "2. **Load the machine** — not too full. Add the correct amount of detergent "
            "(usually less than the cap suggests).\n"
            "3. **Choose the right cycle** — cottons, synthetics, or delicates. "
            "Match to what is in the load.\n"
            "4. **Dry correctly** — hang or machine-dry based on labels. "
            "Polyester and cotton have different rules.\n"
            "5. **Fold and put away** — laundry is not done when it comes out of the machine. "
            "It is done when it is folded and in the drawer."
        ),
        "parent_note_md": (
            "Many students leave home at 18 without knowing how to operate a washing machine. "
            "This is a straightforward mechanical skill with lifelong daily use. "
            "Once taught, make it their responsibility to wash their own clothes every week. "
            "Independence in laundry removes a significant household burden from parents."
        ),
        "prereqs": [],
    },
    {
        "slug": "grocery-shop-alone-age14",
        "title": "Do the Weekly Grocery Shop from a List",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with the list** — parent writes the shopping list (or they help plan "
            "a week of meals and derive the list). Budget is given in advance.\n"
            "2. **Navigate the shop** — they find items independently, compare prices where "
            "relevant, and make substitutions if something is out of stock.\n"
            "3. **Manage the budget** — keep a running total mentally or on their phone. "
            "Stay within the given amount.\n"
            "4. **Pay independently** — cash or card, they handle the transaction.\n"
            "5. **Debrief** — what did they spend? Were there good-value swaps? "
            "Did they stick to the list or add extras?"
        ),
        "parent_note_md": (
            "Grocery shopping is a weekly adult skill involving navigation, prioritisation, "
            "budgeting, and decision-making under mild pressure. Starting at 14 (with a list "
            "and a budget) builds all of these. By 16, a teenager should be able to plan "
            "the week's meals and shop for them without a list."
        ),
        "prereqs": [],
    },
    {
        "slug": "basic-home-repair-age14",
        "title": "Carry Out a Basic Home Repair or Maintenance Task",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real task** — change a light bulb, tighten a loose door handle, "
            "unblock a sink drain, re-hang a picture, replace a tap washer.\n"
            "2. **Gather the right tools** — identify what is needed before starting. "
            "Teach them where tools are kept and why each is used.\n"
            "3. **Follow a process** — for anything involving electricity or plumbing, "
            "look up the correct procedure first. Safety before speed.\n"
            "4. **Do it themselves** — parent watches but does not take over. "
            "Let them work through it.\n"
            "5. **Build a repertoire** — aim for one new repair skill per month. "
            "Keep a list of what they can now do independently."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Always switch off the relevant circuit breaker before touching any electrical fitting.\n"
            "- Turn off the water supply before any plumbing work.\n"
            "- If uncertain about a step, stop and look it up — do not guess."
        ),
        "parent_note_md": (
            "Basic home maintenance is a life skill that most adults outsource unnecessarily "
            "because they were never taught it. A teenager who can change a fuse, fix a "
            "leaking tap, or assemble flat-pack furniture saves significant money and gains "
            "confidence in their practical capability. Start with low-risk tasks and build up."
        ),
        "prereqs": [],
    },
    {
        "slug": "manage-own-schedule-age14",
        "title": "Manage Your Own Weekly Schedule",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a tool** — a physical diary, a phone calendar, or a free app. "
            "They choose what works for them.\n"
            "2. **Enter everything** — school timetable, extra-curricular activities, "
            "assignments due, family commitments, social plans.\n"
            "3. **Plan the week on Sunday** — 10 minutes reviewing what is coming up. "
            "Identify any clashes or busy days.\n"
            "4. **Add study/prep time** — for every assignment or exam, block time to prepare "
            "in advance. Not the night before.\n"
            "5. **Review on Friday** — what did not happen? Why? Adjust the system, not "
            "the standard."
        ),
        "parent_note_md": (
            "Time management is the skill that separates teenagers who thrive academically "
            "and socially from those who are constantly overwhelmed. Teaching them to manage "
            "a calendar at 14 — rather than relying on parents to remind them of everything — "
            "is one of the most meaningful independence steps of this age. Withdraw reminders "
            "as the habit builds."
        ),
        "prereqs": [],
    },
]

DIGITAL_TASKS = [
    {
        "slug": "identify-misinformation-age14",
        "title": "Identify and Fact-Check Online Misinformation",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the red flags** — emotional headlines, no named author, "
            "unfamiliar domain, single source, older story re-shared as new.\n"
            "2. **The SIFT method** — Stop (don't share immediately), Investigate the source, "
            "Find better coverage, Trace claims to the original.\n"
            "3. **Fact-check a claim together** — take a viral WhatsApp message or social "
            "media post and verify it using two independent sources.\n"
            "4. **Check the date** — many false stories are old news recycled. "
            "Always check when the source was published.\n"
            "5. **Before sharing anything** — ask: Do I know this is true? "
            "Have I checked one independent source? Practise this as a habit."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Sharing misinformation — even unintentionally — can cause real harm to "
            "people mentioned in the content.\n"
            "- If a story seems designed to make you angry or scared, that is a signal "
            "to slow down, not speed up."
        ),
        "parent_note_md": (
            "Teenagers are among the most active sharers of misinformation, not from malice "
            "but from speed. The SIFT method gives a structured pause before sharing. "
            "This skill protects them, their contacts, and public discourse. "
            "Model it yourself — say out loud when you are fact-checking something."
        ),
        "prereqs": [],
    },
    {
        "slug": "digital-footprint-age14",
        "title": "Understand and Manage Your Digital Footprint",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Search yourself** — Google your own name. What comes up? "
            "This is what a college admissions officer or future employer sees.\n"
            "2. **Audit social accounts** — review privacy settings on every platform. "
            "Who can see posts? Who can find the profile? Tighten what is public.\n"
            "3. **The 10-year test** — before posting anything: *Would I be comfortable "
            "if this was shown to a teacher, employer, or parent in 10 years?*\n"
            "4. **Delete the embarrassing** — find and delete any old posts, photos, or "
            "comments that would not pass the 10-year test.\n"
            "5. **Build a positive presence** — start thinking about what they do want "
            "to appear online: achievements, interests, projects."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Content shared online may be permanent even after deletion — "
            "screenshots and archives exist.\n"
            "- Location data in photos can reveal your home address or school — turn off "
            "location in camera settings."
        ),
        "parent_note_md": (
            "Universities and employers routinely search candidates online. Teenagers who "
            "understand this at 14 have years to build a positive presence and avoid "
            "reputation-damaging posts. This is not about fear — it is about intentionality. "
            "The same creativity they use in their interests can be channelled into a "
            "deliberate, positive online identity."
        ),
        "prereqs": [],
    },
    {
        "slug": "strong-password-age14",
        "title": "Create and Manage Strong Passwords",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What makes a strong password** — 12+ characters, mix of uppercase, "
            "lowercase, numbers, symbols. No dictionary words. No personal info.\n"
            "2. **The passphrase method** — four random words strung together "
            "(*correct-horse-battery-staple*) is both strong and memorable.\n"
            "3. **Never reuse passwords** — if one account is breached, all reused "
            "passwords are compromised. Unique password per account.\n"
            "4. **Use a password manager** — set up a free password manager (Bitwarden). "
            "Generate and store unique passwords for every account.\n"
            "5. **Enable 2FA** — turn on two-factor authentication on email, banking, "
            "and social accounts. Show them how."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never share passwords with friends, even trusted ones.\n"
            "- If a site is breached (check haveibeenpwned.com), change that password immediately.\n"
            "- The master password to the password manager must be memorised — "
            "never written down or stored digitally."
        ),
        "parent_note_md": (
            "Password hygiene is the most basic and most neglected aspect of personal "
            "cybersecurity. The majority of account compromises involve reused or weak "
            "passwords. Teaching password management at 14 — before they have a bank "
            "account, email linked to everything, and a digital identity worth stealing — "
            "is the right time."
        ),
        "prereqs": [],
    },
    {
        "slug": "build-simple-project-age14",
        "title": "Build a Simple Digital Project",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose the format** — a blog post, a short video, a designed poster, "
            "a simple spreadsheet tool, a basic website, or a short app using Scratch/MIT. "
            "Match the tool to their interest.\n"
            "2. **Define the purpose** — who is it for? What problem does it solve or "
            "what story does it tell? Write one sentence.\n"
            "3. **Build it** — set a two-week deadline. Use free tools: Canva, Google Sites, "
            "Blogger, YouTube. Parent does not help with the creation.\n"
            "4. **Share it** — post it, show it at dinner, send it to a relative. "
            "An audience, even a small one, matters.\n"
            "5. **Reflect** — what worked? What would they do differently? "
            "What could be a next version?"
        ),
        "parent_note_md": (
            "Making something digital — not just consuming — changes a teenager's "
            "relationship with technology. Creators understand the effort behind content, "
            "are more critical consumers, and develop confidence in their ability to make "
            "things. Any format counts: the act of creating and completing is the goal."
        ),
        "prereqs": [],
    },
    {
        "slug": "online-safety-privacy-age14",
        "title": "Set Up and Review Privacy Settings on Social Media",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Audit each platform** — open privacy settings on every account they use. "
            "Go through each setting together: who can see posts, who can message them, "
            "who can find them by phone number or email.\n"
            "2. **Set to private** — any account that is not intentionally public should "
            "be set to private/friends-only.\n"
            "3. **Review followers/friends** — scroll through the list. Are there people "
            "they do not know personally? Remove them.\n"
            "4. **Turn off location sharing** — check which apps have access to location. "
            "Remove location access from anything that does not need it.\n"
            "5. **Repeat every 6 months** — apps change default settings in updates. "
            "Set a calendar reminder to re-audit."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- A public profile means anyone in the world can see posts, school, location, "
            "and photos — not just people the user intends.\n"
            "- Screenshots mean *nothing is truly private* once shared — but reducing "
            "public exposure significantly reduces risk."
        ),
        "parent_note_md": (
            "Most teenagers set up social accounts quickly without reading privacy settings. "
            "Sitting down together for a privacy audit is more effective than a general "
            "warning. Make it a routine — not a one-off triggered by something going wrong."
        ),
        "prereqs": ["digital-footprint-age14"],
    },
]

NAVIGATION_TASKS = [
    {
        "slug": "travel-independently-age14",
        "title": "Travel Independently on Public Transport",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plan the route first** — using Google Maps or a local transit app, "
            "plan the journey: which bus/train, which stop to board, where to get off, "
            "any changes needed.\n"
            "2. **Dry run together** — take the journey once with a parent before they do "
            "it alone. Point out landmarks, notice the stops.\n"
            "3. **First solo trip** — a short, familiar journey. They travel, parent is "
            "reachable by phone but does not accompany.\n"
            "4. **Handle disruptions** — what if the bus doesn't come? What if they miss "
            "the stop? Discuss the options before they go.\n"
            "5. **Build the range** — start with a 2-stop journey, extend to a 30-minute "
            "cross-town trip over a few months."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Keep the phone charged before travelling. Share live location with a parent "
            "for the first few solo trips.\n"
            "- Sit near the driver or in populated carriages, especially in the evening.\n"
            "- If they feel unsafe, get off at the next stop in a busy area and call a parent.\n"
            "- Have the parent's number memorised, not just saved."
        ),
        "parent_note_md": (
            "Independent travel is one of the most significant markers of teenage autonomy. "
            "Teenagers who can navigate public transport have access to school, friends, "
            "opportunities, and employment that those dependent on parent lifts do not. "
            "Start small, build trust, and extend range gradually. Every solo trip builds "
            "both competence and confidence."
        ),
        "prereqs": [],
    },
    {
        "slug": "read-map-navigate-age14",
        "title": "Navigate to an Unfamiliar Location Using a Map",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with a printed map** — of your local area. Identify your location, "
            "north, main roads, landmarks.\n"
            "2. **Plan a walking route** — to somewhere 20 minutes away they haven't been. "
            "Plan it on paper before using a phone.\n"
            "3. **Walk the route** — phone away until needed. Use the map and landmarks. "
            "Only check the phone if genuinely lost.\n"
            "4. **Digital maps** — teach Google Maps: satellite vs map view, walking vs "
            "driving, how to pin a destination, how to share location.\n"
            "5. **The offline fallback** — what to do when there is no signal: "
            "ask a local, find a landmark, retrace the route."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Walk in well-lit, populated routes when navigating unfamiliar areas.\n"
            "- Download offline maps before travelling to areas with poor signal.\n"
            "- Tell someone where you are going and when to expect you back."
        ),
        "parent_note_md": (
            "Spatial awareness and navigation are increasingly atrophied skills as GPS "
            "becomes the default. A teenager who can read a map, orient themselves, and "
            "navigate without a signal is resilient in a way GPS-dependent peers are not. "
            "The paper map exercise also builds spatial reasoning that transfers to maths and science."
        ),
        "prereqs": [],
    },
    {
        "slug": "handle-emergency-alone-age14",
        "title": "Know How to Handle a Common Emergency Independently",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose one emergency to learn thoroughly** — options: "
            "calling an ambulance, what to do if someone collapses, a house fire, "
            "a road accident, a theft.\n"
            "2. **Learn the steps** — look up the correct procedure together. "
            "Write or print the key steps.\n"
            "3. **Know the numbers** — emergency services (100/101/102/108/112 in India). "
            "Memorise them, don't just save them.\n"
            "4. **Roleplay the scenario** — run through the steps as if it were real. "
            "What do you say when the operator answers?\n"
            "5. **Learn one emergency per month** — build a repertoire over time. "
            "Revisit each one after six months."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Emergency numbers in India: Police 100, Fire 101, Ambulance 102/108, "
            "National Emergency 112.\n"
            "- Stay on the line with the operator — they will guide you through what to do.\n"
            "- Do not move an injured person unless they are in immediate danger."
        ),
        "parent_note_md": (
            "A teenager who knows how to call for help, give a clear location, and follow "
            "operator instructions can save a life — including their own. Most young people "
            "have never rehearsed an emergency call. The roleplay step is critical: "
            "rehearsed actions are available under stress; unrehearsed ones often are not."
        ),
        "prereqs": [],
    },
    {
        "slug": "plan-trip-independently-age14",
        "title": "Plan and Execute a Day Trip Independently",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a destination** — somewhere reachable in half a day by public transport. "
            "Not too far for the first attempt.\n"
            "2. **Full plan** — transport (which route, what time, cost), what to do there, "
            "what to bring, what to eat, total budget, return time.\n"
            "3. **Present the plan** — they present the full plan to a parent for safety review "
            "before going. Parent approves, suggests, but does not replan.\n"
            "4. **Execute the trip** — they go, navigate, manage the money, handle the unexpected.\n"
            "5. **Debrief** — what went to plan? What didn't? What would they do differently?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Share the full plan and live location with a parent.\n"
            "- Agree on check-in times (e.g., text when arriving, text when leaving).\n"
            "- Have a contingency amount of money for emergencies.\n"
            "- Know how to get home from any point on the route if plans change."
        ),
        "parent_note_md": (
            "Planning and executing a trip — even a small one — integrates every navigation, "
            "financial, and social skill in a real context. The planning process is as "
            "valuable as the trip itself. A teenager who can do this has a skill set that "
            "most adults use their whole lives."
        ),
        "prereqs": ["travel-independently-age14"],
    },
    {
        "slug": "read-official-document-age14",
        "title": "Read and Understand an Official Document",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real document** — a utility bill, a bank statement, a terms-and-conditions "
            "summary, a school report, an insurance policy summary.\n"
            "2. **Read it fully before discussing** — give them 10 minutes to read it alone. "
            "No phone, no help.\n"
            "3. **Key questions** — what is this document for? Who sent it? "
            "What action (if any) is required? What is the most important piece of information?\n"
            "4. **Vocabulary** — identify three words they did not know. Look them up together.\n"
            "5. **Real consequence** — find a document that requires a response (form, renewal, etc.) "
            "and let them draft the response."
        ),
        "parent_note_md": (
            "Adults receive dozens of official documents per year and many ignore them "
            "because they were never taught how to read them. Teenagers who can parse a "
            "document, extract key information, and identify required actions are far more "
            "competent adults. Start with simple documents and build to complex ones like "
            "tenancy agreements and employment contracts."
        ),
        "prereqs": [],
    },
]

COGNITIVE_TASKS = [
    {
        "slug": "set-achieve-personal-goal-age14",
        "title": "Set and Achieve a Personal Goal Over 4 Weeks",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real goal** — something they actually want, not something a parent "
            "suggests. Academic, physical, creative, or personal.\n"
            "2. **Make it SMART** — Specific, Measurable, Achievable, Relevant, Time-bound. "
            "Not *get fitter* — *run 5km without stopping within 4 weeks.*\n"
            "3. **Break it into weekly milestones** — what needs to happen each week to "
            "reach the goal? Write it down.\n"
            "4. **Weekly check-in** — 5 minutes reviewing progress against the plan. "
            "Adjust if needed — but don't lower the goal.\n"
            "5. **End of 4 weeks** — did they hit it? If not, what got in the way? "
            "This debrief is as important as the goal itself."
        ),
        "parent_note_md": (
            "Self-directed goal-setting is the cognitive skill that separates people who "
            "achieve things from those who don't. Teenagers who practise this consistently "
            "are more motivated at school, in sport, and in work — not because of talent "
            "but because of process. The parent's role here is to ask questions, not to "
            "set the goal or monitor the execution."
        ),
        "prereqs": [],
    },
    {
        "slug": "manage-study-no-reminder-age14",
        "title": "Complete All School Assignments Without Being Reminded",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Their system, not yours** — they choose how to track assignments: "
            "planner, phone app, sticky notes. Whatever they will actually use.\n"
            "2. **Record at the point of assignment** — homework goes into the tracker "
            "the moment it is given, not at the end of the day.\n"
            "3. **No parent reminders for one week** — agree in advance: the parent will "
            "not remind them of homework this week. Any missed work is their consequence.\n"
            "4. **Review together on Friday** — what was due? What was submitted? "
            "No punishment — just data. Adjust the system.\n"
            "5. **Extend to two weeks, then the whole term** — each success builds "
            "the case for more independence."
        ),
        "parent_note_md": (
            "Constantly reminding teenagers about homework erodes their executive function "
            "rather than building it. Every time a parent reminds, the teenager learns that "
            "the consequence of not tracking is simply a parental reminder. Withdrawing "
            "reminders — with clear advance notice — is uncomfortable but is how autonomy "
            "and self-regulation are actually built."
        ),
        "prereqs": [],
    },
    {
        "slug": "solve-real-problem-age14",
        "title": "Work Through a Real-Life Problem Independently",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Identify a real problem they face** — a disagreement with a friend, "
            "a missing item, a double-booked commitment, a failed application.\n"
            "2. **Define the problem clearly** — *The problem is…* in one sentence. "
            "Not a feeling — a situation.\n"
            "3. **Generate options** — list at least three possible responses. "
            "No evaluation yet — just generate.\n"
            "4. **Evaluate and choose** — for each option: what is the likely outcome? "
            "What are the trade-offs? Which is best and why?\n"
            "5. **Act, then reflect** — execute the chosen option. Afterwards: "
            "was it the right choice? What happened?"
        ),
        "parent_note_md": (
            "Problem-solving as a structured skill — define, generate options, evaluate, "
            "act — is rarely taught explicitly. Teenagers who approach problems this way "
            "are less likely to be paralysed by difficulty, less likely to react impulsively, "
            "and far more resilient. The parent's role is to coach the process, not solve "
            "the problem for them."
        ),
        "prereqs": [],
    },
    {
        "slug": "critical-thinking-argument-age14",
        "title": "Argue Both Sides of a Topic You Care About",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a topic they have a strong opinion on** — a school rule, "
            "a social issue, a family decision.\n"
            "2. **State their own position first** — clearly, with reasons. "
            "Write it down in 3–4 sentences.\n"
            "3. **Now argue the opposite side** — write the strongest possible case for "
            "the view they disagree with. This is the hard part.\n"
            "4. **Identify the best counter-argument to their own view** — what is the "
            "strongest thing the other side could say? Can they answer it?\n"
            "5. **Discuss** — has thinking through the other side changed their view at all? "
            "Even partially? Why or why not?"
        ),
        "parent_note_md": (
            "The ability to genuinely understand and articulate a position you disagree with "
            "is the foundation of intellectual integrity, debate skill, and empathy. "
            "Teenagers who can do this are harder to manipulate, better at recognising "
            "their own biases, and more persuasive communicators. Practise it on topics "
            "that matter to them — not abstract ones."
        ),
        "prereqs": [],
    },
    {
        "slug": "reflect-handle-failure-age14",
        "title": "Reflect on and Learn From a Failure",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the failure** — a failed exam, a team loss, a broken friendship, "
            "a missed opportunity. Be specific and honest.\n"
            "2. **Separate what happened from what they feel** — *I felt embarrassed* is "
            "different from *I made three errors in section B*. Both matter — keep them separate.\n"
            "3. **Identify what was in their control** — what could they have done differently? "
            "Only focus on variables they could influence.\n"
            "4. **Extract one lesson** — one specific, actionable thing to do differently "
            "next time. Not a vague resolution — a concrete behaviour.\n"
            "5. **Write it down and revisit** — keep a brief failure log. "
            "Review it monthly. Patterns become visible over time."
        ),
        "parent_note_md": (
            "The capacity to fail, reflect, and adjust — rather than blame, avoid, or collapse — "
            "is the psychological foundation of resilience. Teenagers who are never allowed to "
            "experience failure do not develop this capacity. The parent's role here is to "
            "sit with them in the reflection, not to fix the feeling or explain what went wrong."
        ),
        "prereqs": [],
    },
]

SOCIAL_TASKS = [
    {
        "slug": "navigate-peer-pressure-age14",
        "title": "Recognise and Resist Peer Pressure",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the mechanisms** — direct pressure (*just do it*), indirect pressure "
            "(*everyone does it*), social exclusion pressure (*you're not cool if you don't*).\n"
            "2. **The delay response** — *Let me think about it* buys time without a "
            "confrontation. Practise saying it calmly and confidently.\n"
            "3. **The hard no** — some situations require a clear no. "
            "Practise: *No, that's not something I do.* No explanation required.\n"
            "4. **Exit strategy** — roleplay walking away from a group pressure scenario. "
            "What do you say? Where do you go? Who do you contact?\n"
            "5. **Post-event debrief** — if a real situation happens, discuss it without "
            "judgement: what was the pressure? How did they handle it? What options existed?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If a teenager feels unsafe in a peer pressure situation, they can always "
            "use the parent as an excuse: *My mum/dad would kill me* removes the social "
            "cost of the refusal.\n"
            "- Agree on a code word or text signal that means *come and get me* "
            "without explanation."
        ),
        "parent_note_md": (
            "Peer pressure is at its strongest between ages 13–16 and is the primary "
            "driver of risk-taking behaviour in this age group. Teenagers who have "
            "rehearsed responses — not just been warned — are significantly more likely "
            "to use them. The parent-as-excuse strategy is particularly effective and "
            "worth explicitly offering."
        ),
        "prereqs": [],
    },
    {
        "slug": "resolve-conflict-peer-age14",
        "title": "Resolve a Conflict with a Peer Without Adult Intervention",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose the right moment** — not in public, not when either person is "
            "angry. Request a conversation: *Can we talk about what happened?*\n"
            "2. **I-statements only** — *I felt* not *You always*. "
            "Prepare two I-statements before the conversation.\n"
            "3. **Listen fully before responding** — let the other person finish. "
            "Summarise what they said before adding your perspective.\n"
            "4. **Find common ground** — what does each person actually need? "
            "Usually it is respect, fairness, or acknowledgement.\n"
            "5. **Agree on next steps** — what is the specific change going forward? "
            "Name it. Both agree."
        ),
        "parent_note_md": (
            "At 14, teenagers should be taking primary ownership of their peer conflicts. "
            "A parent who jumps in to resolve friendships — by calling other parents, "
            "teachers, or mediating directly — delays the development of interpersonal "
            "competence. Coach from the sideline; let them lead the conversation."
        ),
        "prereqs": [],
    },
    {
        "slug": "active-listening-age14",
        "title": "Practise Active Listening in a Real Conversation",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What active listening is** — full attention (phone away), eye contact, "
            "body facing the speaker, no interrupting, no formulating your reply while "
            "the other person talks.\n"
            "2. **Summarise back** — after someone speaks, summarise in your own words: "
            "*So what you're saying is…* Confirm with them.\n"
            "3. **Ask one follow-up question** — based only on what they said, "
            "not on what you want to say.\n"
            "4. **Practise in a 5-minute conversation** — partner speaks about anything "
            "for 5 minutes. Listener only listens and asks one question. Swap.\n"
            "5. **Notice the impact** — how does the speaker feel when genuinely listened to? "
            "Ask them after the exercise."
        ),
        "parent_note_md": (
            "Active listening is described by therapists, managers, and relationship "
            "researchers as the single most important interpersonal skill. Teenagers who "
            "practise it are better friends, better students (because they actually absorb "
            "information), and more trusted by others. The phone-away step alone makes "
            "a measurable difference."
        ),
        "prereqs": [],
    },
    {
        "slug": "empathy-perspective-age14",
        "title": "Take Someone Else's Perspective in a Disagreement",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real disagreement** — with a parent, a friend, or a sibling. "
            "Something recent with genuine tension.\n"
            "2. **The role reversal** — argue the other person's case. "
            "What would they say? What do they care about? What are they afraid of?\n"
            "3. **Name their emotions** — *They probably feel… because…* "
            "Say this out loud. It feels odd at first.\n"
            "4. **Find one valid point** — find one thing in the other person's position "
            "that is reasonable or understandable, even if you still disagree overall.\n"
            "5. **Discuss the outcome** — does understanding the other side change "
            "how they want to respond? It does not have to — the understanding is the goal."
        ),
        "parent_note_md": (
            "Empathy at this age is not automatic — it is a learned cognitive skill. "
            "Teenagers who can step into another person's perspective — even a person "
            "they are in conflict with — de-escalate faster, resolve conflicts better, "
            "and are significantly less likely to be drawn into harmful group dynamics. "
            "Model this yourself by naming others' perspectives in family discussions."
        ),
        "prereqs": [],
    },
    {
        "slug": "mentor-younger-child-age14",
        "title": "Teach or Mentor a Younger Child in a Skill",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose the skill** — something they are good at: a sport, a school subject, "
            "a craft, cooking, a game.\n"
            "2. **Plan the session** — how will they explain it? What will the younger child "
            "practise? How long? Plan it before the session.\n"
            "3. **Teach it** — one session of at least 20 minutes. They lead, the younger "
            "child learns. No adult interference.\n"
            "4. **Adapt in the moment** — if the explanation is not working, try another "
            "approach. This is the heart of teaching.\n"
            "5. **Reflect** — what was hard about explaining something you know well? "
            "What would you do differently?"
        ),
        "parent_note_md": (
            "Teaching is the deepest form of learning — the *protégé effect*. Teenagers "
            "who teach others master their subject more fully, develop patience, communication "
            "skills, and leadership. It also builds a positive relationship between older "
            "and younger siblings or community members. If no sibling is available, "
            "a neighbour's child, cousin, or community tutoring opportunity works equally well."
        ),
        "prereqs": [],
    },
]

# ---------------------------------------------------------------------------
# Prerequisite edges: (to_slug, from_slug, is_mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    ("create-monthly-budget-age14",      "track-spending-month-age14",   True),
    ("online-safety-privacy-age14",      "digital-footprint-age14",      True),
    ("plan-trip-independently-age14",    "travel-independently-age14",   True),
]

# ---------------------------------------------------------------------------
# Tag mappings
# ---------------------------------------------------------------------------

CATEGORY_TAGS = [
    ("Money basics",     Tag.Category.FINANCIAL),
    ("Home care",        Tag.Category.HOUSEHOLD),
    ("Digital literacy", Tag.Category.DIGITAL),
    ("Wayfinding",       Tag.Category.NAVIGATION),
    ("Reasoning",        Tag.Category.COGNITIVE),
    ("Social skills",    Tag.Category.SOCIAL),
]

ALL_AGE14_TASKS = [
    (FINANCIAL_TASKS,  "Money basics"),
    (HOUSEHOLD_TASKS,  "Home care"),
    (DIGITAL_TASKS,    "Digital literacy"),
    (NAVIGATION_TASKS, "Wayfinding"),
    (COGNITIVE_TASKS,  "Reasoning"),
    (SOCIAL_TASKS,     "Social skills"),
]


class Command(BaseCommand):
    help = "Seed age-14 tasks across all six categories (idempotent)."

    def handle(self, *args, **options):
        tags = {}
        for display_name, category in CATEGORY_TAGS:
            tag, _ = Tag.objects.get_or_create(
                name=display_name,
                defaults={"category": category},
            )
            tags[display_name] = tag

        all_envs = list(Environment.objects.all())

        total_upserted = 0
        for task_list, tag_name in ALL_AGE14_TASKS:
            tag = tags[tag_name]
            for t in task_list:
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
                task.tags.set([tag])
                task.environments.set(all_envs)
                total_upserted += 1

        self.stdout.write(f"Upserted {total_upserted} age-14 tasks.")

        all_slugs = [t["slug"] for task_list, _ in ALL_AGE14_TASKS for t in task_list]
        task_map = {t.slug: t for t in Task.objects.filter(slug__in=all_slugs)}
        created_edges = 0
        for to_slug, from_slug, mandatory in PREREQ_EDGES:
            to_task = task_map.get(to_slug)
            from_task = task_map.get(from_slug)
            if not to_task or not from_task:
                self.stdout.write(
                    self.style.WARNING(f"  Skipped edge {from_slug}→{to_slug}: task not found")
                )
                continue
            _, created = PrerequisiteEdge.objects.get_or_create(
                from_task=from_task,
                to_task=to_task,
                defaults={"is_mandatory": mandatory},
            )
            if created:
                created_edges += 1

        self.stdout.write(f"Added {created_edges} new prerequisite edges.")
        self.stdout.write(self.style.SUCCESS("seed_age14_catalog complete."))
