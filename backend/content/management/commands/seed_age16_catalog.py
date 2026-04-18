"""Management command: seed age-16 tasks across all six categories.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_age16_catalog

Idempotent — safe to re-run. Uses update_or_create throughout.
Age 16 tasks are pre-adult in scope: civic participation, professional
entry, financial independence, and complex self-management.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Tasks grouped by category
# ---------------------------------------------------------------------------

FINANCIAL_TASKS = [
    {
        "slug": "understand-credit-score-age16",
        "title": "Understand Credit Scores and How to Build One",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is a credit score?** — a number (300–900 in India, CIBIL scale) "
            "that tells lenders how reliably you repay debt. Higher = more trustworthy.\n"
            "2. **What affects it** — payment history (most important), credit utilisation, "
            "length of credit history, types of credit, new enquiries.\n"
            "3. **Check a real score** — look up a parent's CIBIL score together "
            "(free once a year at cibil.com). Read the report. What is each section?\n"
            "4. **How to build it from zero** — secured credit card, paying bills on time, "
            "never missing an EMI. The score starts building the moment you have a credit product.\n"
            "5. **Why it matters** — a poor credit score means higher interest rates on "
            "loans, rejected rental applications, even some job background checks. "
            "Show a real loan calculator: the difference in interest paid at 750 vs 600."
        ),
        "parent_note_md": (
            "A credit score is one of the most consequential numbers in an adult's financial "
            "life, yet almost no one is taught how it works before they need it. A 16-year-old "
            "who understands credit will not miss a payment, will not max out a credit card, "
            "and will not apply for products they do not need — the three habits that protect "
            "a score for life."
        ),
        "prereqs": [],
    },
    {
        "slug": "understand-insurance-age16",
        "title": "Understand Insurance and Why You Need It",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The core concept** — insurance is paying a small, certain amount (premium) "
            "to avoid a large, uncertain loss. It is risk transfer.\n"
            "2. **Types of insurance** — health, life, vehicle, home, travel. "
            "What does each cover? Who needs each type and at what life stage?\n"
            "3. **Read a real policy** — look at a family health insurance policy. "
            "What is covered? What is excluded? What is the deductible? What is the claim process?\n"
            "4. **Calculate underinsurance** — if the policy covers ₹3 lakh but a hospital "
            "stay could cost ₹5 lakh, what happens to the gap? Who pays it?\n"
            "5. **The young person's priority** — health insurance is the first purchase "
            "when earning independently. Show the cost at 22 vs 35 — waiting is expensive."
        ),
        "parent_note_md": (
            "Adults who do not understand insurance either over-pay for products they do not "
            "need or are catastrophically under-protected when something goes wrong. "
            "Insurance literacy is as important as investment literacy — perhaps more so, "
            "because it protects what you already have before you begin building wealth."
        ),
        "prereqs": [],
    },
    {
        "slug": "budget-large-purchase-age16",
        "title": "Research, Save For, and Execute a Major Purchase",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real goal** — phone, laptop, camera, bicycle, musical instrument. "
            "Something that costs significantly more than monthly income.\n"
            "2. **Research the market** — compare at least three options. "
            "New vs refurbished? Which features actually matter for the use case?\n"
            "3. **Build the savings plan** — current savings + monthly contribution = "
            "months to goal. Calculate it. Set the monthly transfer.\n"
            "4. **Resist impulse alternatives** — when a cheaper, less-suitable option "
            "tempts, evaluate it against the criteria. Stick to the plan unless the criteria change.\n"
            "5. **The purchase** — when savings reach the target, they make the purchase "
            "independently. Evaluate: was the research accurate? Is the product what was expected?"
        ),
        "parent_note_md": (
            "Saving for a large purchase — rather than asking for it or going into debt — "
            "is one of the clearest demonstrations of financial maturity. The research "
            "process also teaches critical evaluation of marketing claims. A teenager who "
            "has done this once will apply the same process to cars, homes, and every "
            "major financial decision of their adult life."
        ),
        "prereqs": [],
    },
    {
        "slug": "tax-return-basics-age16",
        "title": "Understand How to File a Basic Income Tax Return",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Who needs to file** — anyone earning above the basic exemption limit "
            "(currently ₹3 lakh under the new regime in India). Even below this, filing "
            "is useful for refunds and as proof of income.\n"
            "2. **Key documents** — Form 16 (from employer), bank interest statements, "
            "investment proofs (80C). Identify each one on a real family document.\n"
            "3. **Navigate the ITR portal** — go to incometax.gov.in together. "
            "Explore: where would you log in? Where is the ITR-1 form for salaried individuals?\n"
            "4. **Walk through ITR-1** — using a parent's data, fill in the form together "
            "without actually submitting. See every section: income, deductions, tax payable.\n"
            "5. **The deadline** — ITR must be filed by 31 July each year. "
            "Late filing has penalties. Mark it in their calendar for when they are earning."
        ),
        "parent_note_md": (
            "Filing a tax return is an annual civic and financial obligation that most "
            "first-time earners find overwhelming simply because no one walked them through "
            "it. A 16-year-old who has seen the form, knows the documents, and understands "
            "the deadline will not panic at their first filing. Use a real return as the "
            "teaching tool — there is no substitute for the actual document."
        ),
        "prereqs": [],
    },
    {
        "slug": "earn-and-manage-income-age16",
        "title": "Manage a Regular Income: Split Between Saving, Spending, and Giving",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up the three buckets** — 50% spending, 30% saving, 20% giving/investing "
            "is a common starting framework. Adjust the percentages to fit, but all three "
            "buckets must exist.\n"
            "2. **Automate the saving** — the moment income arrives, the saving amount "
            "moves to a separate account. Not what is left — what is moved first.\n"
            "3. **The giving bucket** — charitable donation, gift to a family member, "
            "or investment in someone else's project. The habit of giving, however small, "
            "matters as much as saving.\n"
            "4. **Track for one month** — did the spending stay within 50%? "
            "If not, what caused the overshoot?\n"
            "5. **Adjust and recommit** — the split is a starting point, not a rule. "
            "Adjust it based on real experience, but never let saving drop below 20%."
        ),
        "parent_note_md": (
            "The pay-yourself-first principle — saving before spending, not from what is "
            "left — is the single habit most associated with long-term financial security. "
            "A teenager with even a small regular income (part-time job, allowance) can "
            "practise this framework now and arrive at their first full-time job with "
            "the system already wired."
        ),
        "prereqs": [],
    },
]

HOUSEHOLD_TASKS = [
    {
        "slug": "manage-home-solo-age16",
        "title": "Manage the Household Independently for a Weekend",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plan before parents leave** — meals for two days, what food is in the "
            "house, emergency contacts, any scheduled deliveries or visitors.\n"
            "2. **Cook all meals** — no ordering in unless planned and budgeted. "
            "Breakfast, lunch, dinner for two days.\n"
            "3. **Keep the house in order** — dishes done after each meal, floors swept, "
            "nothing left in chaos. The standard: the home looks the same when parents "
            "return as when they left.\n"
            "4. **Handle whatever comes up** — a spill, a delivered parcel, a neighbour "
            "at the door, a minor appliance issue. Deal with it calmly.\n"
            "5. **Debrief honestly** — what was harder than expected? "
            "What did they handle well? What would they plan differently?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Parents must be reachable by phone at all times.\n"
            "- No overnight guests without prior parent approval.\n"
            "- Know the location of: mains water shut-off, fuse box, spare key, "
            "first aid kit, and a trusted neighbour's contact."
        ),
        "parent_note_md": (
            "Managing a home alone for a weekend is the most complete rehearsal for "
            "independent living available to a 16-year-old. It integrates cooking, "
            "cleaning, budgeting, problem-solving, and emotional self-management in a "
            "real environment. The first time should be short and well-prepared. "
            "Most teenagers exceed expectations — and gain enormous confidence from it."
        ),
        "prereqs": [],
    },
    {
        "slug": "host-a-meal-age16",
        "title": "Plan and Host a Meal for Guests",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose the menu** — 2–3 courses or a main with sides. "
            "Consider dietary restrictions of guests. Plan it a week in advance.\n"
            "2. **Buy the ingredients** — from their list, within a set budget. "
            "No last-minute shops on the day.\n"
            "3. **Timing plan** — write a cooking timeline working backwards from the "
            "serving time. When does each dish go on? What can be prepared in advance?\n"
            "4. **Set the table and welcome guests** — they are the host. "
            "That means greetings, offering drinks, and keeping conversation going.\n"
            "5. **Clean up afterwards** — hosting includes the full clean-up. "
            "The meal is not done until the kitchen is restored."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Confirm any allergies with every guest before finalising the menu.\n"
            "- Food safety: hot food served hot, cold food kept cold until serving. "
            "Do not leave cooked food at room temperature for more than two hours."
        ),
        "parent_note_md": (
            "Hosting a meal integrates planning, cooking, time management, budgeting, "
            "and social skill in a single exercise. It is also one of the most valued "
            "adult social abilities — the person who can host well builds relationships, "
            "strengthens community, and demonstrates genuine generosity. Starting at 16 "
            "means the skill is comfortable by the time it matters most."
        ),
        "prereqs": [],
    },
    {
        "slug": "handle-home-emergency-age16",
        "title": "Handle a Household Emergency Calmly and Correctly",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the scenarios** — power cut, burst pipe, gas smell, oven fire, "
            "locked out, appliance failure. Cover at least three.\n"
            "2. **Power cut** — locate the fuse box, reset a tripped circuit breaker, "
            "identify which circuits are on which breaker. Practise in daylight.\n"
            "3. **Water leak** — locate and shut the mains water stop-cock. "
            "Time how long it takes to find it. Know what to do before a plumber arrives.\n"
            "4. **Gas smell** — do not switch anything on or off. Open windows. "
            "Leave the building. Call the gas emergency number from outside.\n"
            "5. **Locked out** — who has a spare key? What is the locksmith protocol? "
            "Identify these before the situation arises."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Gas emergency number in India: 1906 (IGL) or the local gas provider number — "
            "save it in your phone now.\n"
            "- Never re-enter a building after a gas smell until cleared by a professional.\n"
            "- A small fire in a pan: lid on the pan, turn off the heat, never use water on oil."
        ),
        "parent_note_md": (
            "Household emergencies happen without warning. A 16-year-old who knows where "
            "the stop-cock is, how to reset a fuse, and what to do if they smell gas is "
            "protecting the family every time they are home alone. Walk through each "
            "scenario physically — not just in conversation."
        ),
        "prereqs": [],
    },
    {
        "slug": "household-budget-week-age16",
        "title": "Manage a Household Budget for One Week",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Get the real numbers** — parent shares the actual weekly household "
            "expenditure: food, transport, utilities, miscellaneous.\n"
            "2. **Take responsibility for one category** — groceries is most practical. "
            "They are given the weekly grocery budget and manage it entirely.\n"
            "3. **Plan before spending** — meal plan → shopping list → price estimate → "
            "shop within the budget. Any underspend they keep track of; any overspend they explain.\n"
            "4. **Track every purchase** — receipt kept, amount logged. "
            "No estimating — actual figures.\n"
            "5. **End of week review** — total spend vs budget. Where did money go? "
            "What choices were made? What would they do differently?"
        ),
        "parent_note_md": (
            "Most young adults moving out for the first time have never had to make food "
            "money last a full week. The experience of running out of budget on Thursday "
            "because Monday's choices were careless is a lesson that sticks. "
            "Give real money and real responsibility — not a simulation."
        ),
        "prereqs": [],
    },
    {
        "slug": "basic-vehicle-maintenance-age16",
        "title": "Carry Out Basic Vehicle or Bicycle Maintenance",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose the vehicle** — bicycle is the best starting point. "
            "If a car is accessible, cover that too.\n"
            "2. **Bicycle** — pump tyres to correct pressure, fix a puncture (remove wheel, "
            "locate puncture, patch or replace inner tube), oil the chain, adjust brakes.\n"
            "3. **Car basics** — check and top up engine oil, check coolant level, "
            "check tyre pressure, check all lights, identify the spare tyre and tools.\n"
            "4. **Know the service schedule** — when was it last serviced? "
            "What are the intervals? What happens if servicing is neglected?\n"
            "5. **Roadside tyre change** — walk through the full process of changing "
            "a flat tyre, even if not doing it for real: jack placement, wheel nut sequence, "
            "spare tyre fitting."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never jack a car on a slope or soft ground — always on flat, firm surface.\n"
            "- Engine oil and coolant are checked cold, not immediately after driving.\n"
            "- A flat tyre on a moving vehicle: do not brake sharply — ease off the "
            "accelerator and steer to the side of the road slowly."
        ),
        "parent_note_md": (
            "Vehicle helplessness — not knowing how to check oil or change a tyre — "
            "is expensive and potentially dangerous. A 16-year-old who knows these basics "
            "can handle a breakdown safely, will not damage a vehicle through neglect, "
            "and is less dependent on roadside assistance for issues they can fix themselves."
        ),
        "prereqs": [],
    },
]

DIGITAL_TASKS = [
    {
        "slug": "protect-identity-online-age16",
        "title": "Take Active Steps to Protect Your Online Identity",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Audit all accounts** — list every online account. "
            "Use haveibeenpwned.com to check if any email has been in a data breach. "
            "Change any compromised passwords immediately.\n"
            "2. **Enable 2FA everywhere** — email, banking, social media. "
            "Authenticator app (Google Authenticator, Authy) is more secure than SMS.\n"
            "3. **Review app permissions** — on the phone, check which apps have access to "
            "location, camera, microphone, contacts. Remove access where not needed.\n"
            "4. **Public Wi-Fi hygiene** — never log into banking or sensitive accounts on "
            "public Wi-Fi without a VPN. Explain why: packet sniffing.\n"
            "5. **Recovery options** — ensure every important account has a recovery email "
            "and phone number that they control. Test recovery for at least one account."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If an account is compromised: change the password immediately, revoke all "
            "active sessions, enable 2FA, check for any outgoing messages or transactions.\n"
            "- Do not reuse any password after a breach — generate a new unique one."
        ),
        "parent_note_md": (
            "Identity theft and account compromise affect millions of people annually. "
            "At 16, a teenager has enough accounts, data, and online activity to make "
            "them a meaningful target. A systematic security audit — done once, then "
            "repeated annually — significantly reduces risk. The 2FA step alone blocks "
            "the majority of account takeover attempts."
        ),
        "prereqs": [],
    },
    {
        "slug": "professional-digital-communication-age16",
        "title": "Communicate Professionally via Email and Video Call",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Professional email** — write to a real external contact "
            "(teacher, coach, potential employer, university admissions). "
            "Subject line, formal greeting, clear purpose, polite close, full name.\n"
            "2. **Response time** — professional communication expects a reply within 24 hours "
            "on working days. Set this standard for themselves now.\n"
            "3. **Video call setup** — camera at eye level (not looking up from a laptop), "
            "neutral background or tidy room, decent lighting (light source in front, not behind), "
            "headphones to avoid echo.\n"
            "4. **Video call conduct** — mute when not speaking, look at the camera not "
            "the screen, no eating, full name displayed.\n"
            "5. **Follow-up** — after any professional conversation, send a brief follow-up "
            "email confirming what was discussed or agreed."
        ),
        "parent_note_md": (
            "Professional digital communication is the primary medium through which "
            "universities, employers, and institutions judge candidates before meeting them. "
            "Teenagers who communicate professionally in writing and on camera stand out "
            "dramatically from peers who write casually or appear unprepared on video calls. "
            "The gap is easy to close with practice."
        ),
        "prereqs": [],
    },
    {
        "slug": "build-portfolio-age16",
        "title": "Build an Online Portfolio of Work or Achievements",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a platform** — a simple free site (Google Sites, Wix, Notion "
            "public page, GitHub Pages for technical students) or a PDF portfolio for "
            "creative work.\n"
            "2. **Curate, don't dump** — 5 excellent pieces of work are better than 20 "
            "average ones. Choose the best. Write a one-paragraph description of each.\n"
            "3. **Context and outcome** — for each piece: what was the brief? What did "
            "you do? What was the result or what did you learn? Numbers help.\n"
            "4. **Make it findable** — share the link on their CV, LinkedIn, and email signature.\n"
            "5. **Keep it updated** — add new work quarterly. Remove older, weaker pieces "
            "as stronger ones replace them. A portfolio is a living document."
        ),
        "parent_note_md": (
            "A portfolio demonstrates what a CV merely claims. For creative, technical, "
            "and academic fields alike, showing work is increasingly expected at "
            "university application and early career stage. A teenager who begins curating "
            "their portfolio at 16 arrives at 18 with two years of documented achievement — "
            "a significant advantage over those who start from scratch."
        ),
        "prereqs": [],
    },
    {
        "slug": "evaluate-online-source-age16",
        "title": "Evaluate the Credibility of Online Sources at an Advanced Level",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The CRAAP test** — Currency (when published?), Relevance (to the topic?), "
            "Authority (who wrote it? what are their credentials?), Accuracy "
            "(evidence cited? peer reviewed?), Purpose (informing or persuading?).\n"
            "2. **Primary vs secondary sources** — a government database is a primary "
            "source; a news article reporting on it is secondary. Know the difference.\n"
            "3. **Lateral reading** — instead of reading deeply into one site, quickly "
            "open multiple tabs to check what other credible sources say about "
            "the same organisation or claim.\n"
            "4. **Evaluate a Wikipedia article** — check the citations at the bottom. "
            "Are they from credible sources? Wikipedia is a starting point, not an endpoint.\n"
            "5. **Apply to a real research task** — for the next essay or project, "
            "evaluate every source using this framework. Note the quality of each."
        ),
        "parent_note_md": (
            "Academic and professional research requires source evaluation — not just "
            "finding information but assessing its reliability. This skill directly "
            "improves essay quality, research projects, and eventually professional "
            "decision-making. It also makes teenagers significantly harder to mislead "
            "with sophisticated misinformation."
        ),
        "prereqs": [],
    },
    {
        "slug": "digital-productivity-system-age16",
        "title": "Build and Use a Personal Digital Productivity System",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **One place for tasks** — all to-dos, assignments, and commitments in one "
            "system (Notion, Todoist, Google Tasks, physical planner). Not across "
            "multiple apps and post-its.\n"
            "2. **One calendar** — all time-based commitments in one calendar, synced "
            "across devices. Colour-code categories (school, personal, work).\n"
            "3. **Weekly review** — every Sunday, 15 minutes: review the week ahead, "
            "move any unfinished tasks, check for conflicts.\n"
            "4. **Capture immediately** — the moment a task or commitment arises, it goes "
            "into the system. Not later, not mentally noted — immediately.\n"
            "5. **One month trial** — use the system for four weeks without changing tools. "
            "After a month, adjust — but do not tool-hop before giving it a real trial."
        ),
        "parent_note_md": (
            "The transition to post-school life — university, work — involves a step-change "
            "in self-management demands. Teenagers who arrive with an established productivity "
            "system are far less likely to miss deadlines, double-book, or feel overwhelmed. "
            "The specific tool matters far less than the habit of having a system and using it."
        ),
        "prereqs": [],
    },
]

NAVIGATION_TASKS = [
    {
        "slug": "overnight-trip-solo-age16",
        "title": "Plan and Execute an Overnight Trip Independently",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Full plan** — destination, transport (both ways), accommodation, "
            "activities, total budget, emergency contacts, return time.\n"
            "2. **Book it themselves** — train/bus tickets, hostel or relative's home, "
            "any activity bookings. Every booking in their name, paid by them.\n"
            "3. **Parent safety brief** — share the full itinerary, check-in times, "
            "and the name of one local contact. Agree on communication frequency.\n"
            "4. **Execute the trip** — travel, navigate, manage the money, handle the "
            "unexpected. No SOS calls for non-emergencies.\n"
            "5. **Financial debrief** — actual spend vs planned spend. What caused "
            "any variance? What would they adjust on the next trip?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Share live location with a parent for the duration of the trip.\n"
            "- Book accommodation with real reviews — do not book anything that cannot "
            "be verified independently.\n"
            "- Carry a small cash emergency reserve separate from the main wallet.\n"
            "- Have the local police station number for the destination saved."
        ),
        "parent_note_md": (
            "An overnight independent trip at 16 — planned and executed by the teenager — "
            "is one of the most significant independence milestones before adulthood. "
            "The planning process builds every skill covered in previous tasks. "
            "The execution builds the confidence that comes only from having actually "
            "done something difficult alone. Most teenagers rise to it."
        ),
        "prereqs": [],
    },
    {
        "slug": "understand-civic-participation-age16",
        "title": "Understand the Electoral and Civic Participation System",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **How elections work in India** — Lok Sabha, Rajya Sabha, state assemblies, "
            "local bodies. Who votes for what, and when?\n"
            "2. **Voter registration** — what is needed to register? "
            "Navigate voter.eci.gov.in together. Understand Form 6 (new voter registration). "
            "They should register the moment they turn 18.\n"
            "3. **How a bill becomes law** — trace one recent law from bill to enactment. "
            "Who proposed it? How was it debated? What is the process?\n"
            "4. **Local civic participation** — find one local civic issue (water, roads, "
            "parks) and identify who is responsible for it and how residents can raise concerns.\n"
            "5. **Attend something civic** — a local council meeting, a town hall, a "
            "political rally (any party), a public consultation. Observe and report back."
        ),
        "parent_note_md": (
            "Young people who understand how civic systems work — and feel that participation "
            "is possible and meaningful — are more likely to vote, engage with local issues, "
            "and contribute to public life. Civic disengagement is partly a knowledge gap. "
            "Registering to vote the day they turn 18 is the most concrete action — "
            "prepare the knowledge now."
        ),
        "prereqs": [],
    },
    {
        "slug": "understand-renting-age16",
        "title": "Understand How Renting Accommodation Works",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The rental process** — search, shortlist, view, apply, sign lease, "
            "pay deposit. Walk through each stage.\n"
            "2. **Read a rental agreement** — find a sample residential tenancy agreement "
            "online. Identify: rent amount, deposit, notice period, maintenance responsibilities, "
            "break clause.\n"
            "3. **Tenant rights** — what is the landlord responsible for? What are the "
            "tenant's obligations? What constitutes unlawful eviction?\n"
            "4. **Calculate the full cost** — rent is not the only cost. Add: deposit "
            "(usually 2–3 months), brokerage, stamp duty, utility connections, initial "
            "furnishing. Total the move-in cost.\n"
            "5. **Research local rents** — look up rental prices in a city they might "
            "study or work in. At what income level does rent become affordable?"
        ),
        "parent_note_md": (
            "Moving into a rental for the first time — typically at 18–22 — is one of "
            "the most financially significant events in a young adult's life. Those who "
            "understand the lease, know their rights, and have calculated the full cost "
            "in advance are far less likely to be exploited or to make an expensive mistake. "
            "Share your own rental experience as context."
        ),
        "prereqs": [],
    },
    {
        "slug": "access-mental-health-support-age16",
        "title": "Know How to Access Mental Health Support",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Normalise the conversation** — mental health is health. "
            "Needing support is not weakness — it is self-awareness. Discuss this directly.\n"
            "2. **Identify the options** — school counsellor, GP referral, iCall (9152987821), "
            "Vandrevala Foundation helpline (1860-2662-345), online therapy platforms.\n"
            "3. **Know the warning signs** — in themselves and in friends: persistent low mood, "
            "withdrawal, sleep changes, inability to function, talk of hopelessness.\n"
            "4. **How to help a friend** — listen without fixing, do not promise secrecy, "
            "encourage professional help, tell a trusted adult if there is any risk to safety.\n"
            "5. **Break the stigma exercise** — read one first-person account of someone "
            "seeking mental health support. Discuss what made it hard and what helped."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If someone expresses thoughts of suicide or self-harm: take it seriously, "
            "stay with them, contact iCall (9152987821) or Vandrevala Foundation (1860-2662-345), "
            "or take them to the nearest hospital.\n"
            "- Do not promise to keep suicidal thoughts secret — a broken confidence "
            "that saves a life is always the right call."
        ),
        "parent_note_md": (
            "Suicide is one of the leading causes of death in 15–29-year-olds in India. "
            "A teenager who knows the helpline numbers, recognises warning signs in "
            "themselves and others, and is not embarrassed to seek help is protected "
            "in a way that most are not. This conversation is not morbid — it is "
            "as practical as knowing how to call an ambulance."
        ),
        "prereqs": [],
    },
    {
        "slug": "full-job-application-age16",
        "title": "Complete a Full Job or Internship Application Process",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a real opportunity** — part-time job, internship, volunteer role, "
            "or work experience placement. Something they genuinely want.\n"
            "2. **Tailored application** — customise the CV and cover letter for this "
            "specific role. Mirror the language of the job description.\n"
            "3. **Submit on time** — before the deadline. Set a personal deadline two "
            "days earlier.\n"
            "4. **Prepare for the interview** — research the organisation, prepare answers "
            "to common questions, prepare two questions to ask the interviewer.\n"
            "5. **Follow up** — if not heard from within the timeframe given, send one "
            "polite follow-up email. If rejected, ask for feedback. Use the feedback."
        ),
        "parent_note_md": (
            "The job application process — search, tailor, submit, interview, follow-up — "
            "is a skill that many people only learn under the pressure of unemployment. "
            "Practising it at 16 on a low-stakes opportunity means the process is "
            "familiar and confident when the stakes are high. Every rejection at 16 "
            "is a rehearsal for success at 22."
        ),
        "prereqs": [],
    },
]

COGNITIVE_TASKS = [
    {
        "slug": "long-term-goal-plan-age16",
        "title": "Create a Personal Development Plan for the Next Two Years",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Vision first** — where do they want to be at 18? "
            "Academic results, skills acquired, experiences had, relationships built. "
            "Write it in one paragraph.\n"
            "2. **Gap analysis** — where are they now? What is the distance between "
            "now and the vision? Be honest.\n"
            "3. **Milestones** — what needs to happen at 6 months, 12 months, 18 months "
            "to stay on track? Make them specific and measurable.\n"
            "4. **Actions this month** — from the milestones, what is the first concrete "
            "action to take in the next 30 days? Start there.\n"
            "5. **Quarterly review** — every three months, review progress, update the plan. "
            "People change; the plan should change with them — but intentionally, not by drift."
        ),
        "parent_note_md": (
            "Most 16-year-olds have plans imposed on them rather than developed by them. "
            "A teenager who has articulated their own two-year vision — and is working "
            "towards it deliberately — has a qualitatively different relationship with "
            "their future. The plan may change completely. The habit of planning intentionally "
            "never goes out of use."
        ),
        "prereqs": [],
    },
    {
        "slug": "learn-skill-independently-age16",
        "title": "Learn a New Skill Entirely Independently",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real skill** — coding (Python basics), a language, video editing, "
            "graphic design, a musical instrument, public speaking, chess at a higher level. "
            "Something that takes weeks, not hours.\n"
            "2. **Find the resources** — free courses (Khan Academy, Coursera audit, YouTube, "
            "freeCodeCamp). No cost required. Research the best learning path.\n"
            "3. **Set a measurable goal** — not *learn Python* — "
            "*build a working programme that does X in 6 weeks.*\n"
            "4. **Consistent practice** — 30 minutes per day beats 4 hours once a week. "
            "Decide the time slot and protect it.\n"
            "5. **Demonstrate the skill** — at the end, show something: a project, a "
            "performance, a certificate, a portfolio piece. Proof of completion."
        ),
        "parent_note_md": (
            "The ability to teach yourself a skill from scratch — without a teacher, "
            "a course, or someone checking — is one of the most valuable capabilities "
            "in the modern world. Teenagers who have done this once know they can do it "
            "again. They approach new challenges with *I can figure this out* rather than "
            "*I need to be taught this.*"
        ),
        "prereqs": [],
    },
    {
        "slug": "analyse-media-bias-age16",
        "title": "Analyse Media Bias and Recognise Propaganda Techniques",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find the same story in three outlets** — choose a politically contested "
            "news story. Read coverage from a left-leaning, right-leaning, and centrist "
            "source. Compare: what facts are included? What is omitted? What language is used?\n"
            "2. **Propaganda techniques** — name calling, glittering generalities, "
            "bandwagon, fear appeal, false dilemma, loaded language. Identify one in each article.\n"
            "3. **Check allsides.com or similar** — look up where the outlets sit on the "
            "bias spectrum. Was their intuition correct?\n"
            "4. **Advertising analysis** — pick a political advertisement or social media "
            "campaign. What technique is it using? What emotion is it targeting?\n"
            "5. **Personal audit** — which sources do they personally consume most? "
            "Where do those sources sit on the bias spectrum? What perspectives are they not seeing?"
        ),
        "parent_note_md": (
            "Media literacy at this level — identifying bias, named propaganda techniques, "
            "and personal blind spots — is a civic necessity in an era of algorithmically "
            "curated content. Teenagers whose news diet is varied and critically analysed "
            "are significantly harder to radicalise and manipulate, in any direction."
        ),
        "prereqs": [],
    },
    {
        "slug": "build-30day-habit-age16",
        "title": "Build and Maintain a Daily Habit for 30 Days",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose one habit** — exercise, journalling, reading, meditation, a "
            "language practice, cold shower. One only. Simplicity is the strategy.\n"
            "2. **Make it tiny** — 10 minutes maximum. The goal in week one is just "
            "to do it, not to do it perfectly. Lower the bar until it feels easy.\n"
            "3. **Habit stacking** — attach it to an existing anchor: *After I brush "
            "my teeth, I will [habit].* The existing habit triggers the new one.\n"
            "4. **Track visually** — a paper calendar or habit tracker app. "
            "Each completed day gets an X. *Don't break the chain* is the motivation.\n"
            "5. **Missing one day** — the rule: never miss twice. One miss is an accident; "
            "two misses is the start of quitting. Get back immediately."
        ),
        "parent_note_md": (
            "The 30-day habit challenge is a well-researched entry point to habit formation. "
            "A teenager who has successfully built one new habit understands that behaviour "
            "change is a process, not a resolution. The specific habit matters less than "
            "the meta-skill: I can decide to change a behaviour and actually follow through."
        ),
        "prereqs": [],
    },
    {
        "slug": "write-structured-essay-age16",
        "title": "Write a Well-Researched, Structured Essay with Citations",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a topic with a genuine argument** — not a description, "
            "an argument. *Social media has a net negative effect on teenage mental health* — "
            "argue for or against with evidence.\n"
            "2. **Research first, write second** — read 4–5 sources before writing a word. "
            "Note the key arguments and evidence on each side.\n"
            "3. **Structure** — introduction (thesis statement), 3 body paragraphs "
            "(point + evidence + analysis), conclusion (restate thesis + broader implication).\n"
            "4. **Cite correctly** — every statistic, quotation, and borrowed idea needs "
            "a citation. Use a consistent format (APA or MLA). Practise one.\n"
            "5. **Read aloud before submitting** — the ear finds unclear sentences and "
            "weak logic that the eye misses. Revise anything that sounds wrong."
        ),
        "parent_note_md": (
            "Essay writing — with research, structure, and citations — is the foundation "
            "of university-level academic work. Teenagers who arrive at degree level "
            "having never written a properly cited essay are disadvantaged from week one. "
            "A structured essay on a topic they care about, written to a high standard, "
            "is one of the most important skills to develop before 18."
        ),
        "prereqs": [],
    },
]

SOCIAL_TASKS = [
    {
        "slug": "volunteer-consistently-age16",
        "title": "Commit to a Regular Volunteering Role",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a cause they care about** — not the most prestigious option, "
            "the one they genuinely connect with. Animal shelter, tutoring, food bank, "
            "environmental work, elderly care.\n"
            "2. **Commit to a schedule** — minimum once a week for at least two months. "
            "A single one-off is not volunteering — it is a visit.\n"
            "3. **Show up on the hard days** — the value of volunteering is commitment, "
            "not convenience. The sessions when they do not feel like going matter most.\n"
            "4. **Build a relationship** — get to know the people or animals they serve. "
            "The relationship is what makes it meaningful, not the task.\n"
            "5. **Reflect monthly** — what has changed in them? What have they learned "
            "about the issue? What do they understand now that they didn't before?"
        ),
        "parent_note_md": (
            "Regular volunteering builds empathy, community connection, perspective, and "
            "commitment — all more effectively than any classroom exercise. It also "
            "strengthens university applications and CVs in a way that is both genuine "
            "and verifiable. The minimum is consistency: a teenager who has shown up "
            "reliably for six months has demonstrated something real."
        ),
        "prereqs": [],
    },
    {
        "slug": "support-peer-difficulty-age16",
        "title": "Support a Friend Going Through a Difficult Time",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The first principle** — presence matters more than advice. "
            "Most people in difficulty do not need solutions — they need to feel heard.\n"
            "2. **Ask before advising** — *Do you want me to help figure this out, "
            "or do you just need to talk?* The answer shapes the whole conversation.\n"
            "3. **Active listening only** — no minimising (*it could be worse*), "
            "no silver lining (*at least…*), no comparing (*I know how you feel, "
            "the same thing happened to me…*). Just listen and reflect.\n"
            "4. **Practical support** — sometimes the best thing is a meal, a lift, "
            "or sitting together in silence. Offer specifically, not vaguely "
            "(*I'll do anything you need*).\n"
            "5. **Know the limit** — if a friend is in danger or in crisis beyond what "
            "peer support can handle, encourage professional help and — if necessary — "
            "tell a trusted adult."
        ),
        "parent_note_md": (
            "The ability to support a friend in difficulty — without projecting, fixing, "
            "or withdrawing — is one of the most valued qualities in any relationship. "
            "Teenagers who develop this skill form deeper friendships, are more trusted, "
            "and are better equipped to handle their own difficulties by observing what "
            "genuinely helps. Teach by modelling it with them when they need support."
        ),
        "prereqs": [],
    },
    {
        "slug": "set-communicate-boundaries-age16",
        "title": "Set and Communicate a Personal Boundary",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Understand what a boundary is** — a limit that defines what behaviour "
            "you will and will not accept. Not a wall — a communicated standard.\n"
            "2. **Identify a real boundary they need** — in a friendship, a family "
            "relationship, or online. Where do they feel consistently uncomfortable "
            "or overstepped?\n"
            "3. **The formula** — *When you [specific behaviour], I feel [impact]. "
            "I need [specific change].* Practise saying it out loud.\n"
            "4. **Deliver it** — in a calm moment, not in the heat of an argument. "
            "One sentence is enough. No over-explaining.\n"
            "5. **What to do if it is not respected** — a stated boundary that is ignored "
            "tells you something important about the relationship. Discuss what the "
            "appropriate response is."
        ),
        "parent_note_md": (
            "Boundary-setting is the foundation of healthy relationships — romantic, "
            "professional, and social. Teenagers who cannot set limits are more vulnerable "
            "to exploitation, resentment, and burnout. The skill is not aggressive — "
            "it is clear and respectful. Model it yourself: set limits with your "
            "teenager and name what you are doing."
        ),
        "prereqs": [],
    },
    {
        "slug": "maintain-professional-relationship-age16",
        "title": "Build and Maintain a Professional Relationship",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Identify the relationship** — a teacher, coach, mentor, employer, "
            "or professional contact they interact with regularly.\n"
            "2. **Show consistent reliability** — every commitment made in this relationship "
            "is kept. Punctual, prepared, follows through. Reliability is the foundation.\n"
            "3. **Communicate proactively** — if something changes (absence, late submission, "
            "changed plans), inform the person in advance. Do not wait to be asked.\n"
            "4. **Show genuine interest** — ask one question about the person's work or "
            "expertise in each interaction. Not performative — genuinely curious.\n"
            "5. **Express gratitude specifically** — at the end of a term, project, or "
            "engagement, write a specific thank you: *Your advice on X made a difference "
            "to Y.* A handwritten note is remembered."
        ),
        "parent_note_md": (
            "Professional relationships — the kind that lead to references, opportunities, "
            "and mentorship — are built on reliability, communication, and genuine interest. "
            "These are learnable behaviours, not personality traits. A teenager who has "
            "cultivated one real professional relationship by 18 has a model they can "
            "replicate for the rest of their career."
        ),
        "prereqs": [],
    },
    {
        "slug": "intentional-social-media-age16",
        "title": "Use Social Media Intentionally and Audit Its Impact",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Intention audit** — for each platform they use, answer: "
            "*Why do I use this? What does it give me? What does it cost me?*\n"
            "2. **Before-and-after mood check** — for one week, note how they feel "
            "before and after a social media session. Any consistent patterns?\n"
            "3. **Curate the feed** — unfollow, mute, or block any account that "
            "consistently makes them feel worse about themselves. No guilt.\n"
            "4. **Follow for growth** — actively add accounts that teach, inspire, "
            "or create in their area of interest. Replace passive consumption with "
            "curated, purposeful content.\n"
            "5. **The create-consume ratio** — track one week: how much time creating "
            "(writing, designing, making) vs consuming (scrolling). Aim to shift the ratio."
        ),
        "parent_note_md": (
            "Most social media use is reactive and unconscious. A 16-year-old who can "
            "audit their own usage — name the cost, curate the feed, and shift from "
            "consumption to creation — has a relationship with technology that will serve "
            "them well into adulthood. The mood-tracking exercise is often the most "
            "revealing: the data is personal and undeniable."
        ),
        "prereqs": [],
    },
]

# ---------------------------------------------------------------------------
# Prerequisite edges: (to_slug, from_slug, is_mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    ("budget-large-purchase-age16",       "understand-credit-score-age16",  False),
    ("full-job-application-age16",        "build-portfolio-age16",          False),
    ("overnight-trip-solo-age16",         "full-job-application-age16",     False),
    ("write-structured-essay-age16",      "learn-skill-independently-age16", False),
    ("intentional-social-media-age16",    "digital-productivity-system-age16", False),
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

ALL_AGE16_TASKS = [
    (FINANCIAL_TASKS,  "Money basics"),
    (HOUSEHOLD_TASKS,  "Home care"),
    (DIGITAL_TASKS,    "Digital literacy"),
    (NAVIGATION_TASKS, "Wayfinding"),
    (COGNITIVE_TASKS,  "Reasoning"),
    (SOCIAL_TASKS,     "Social skills"),
]


class Command(BaseCommand):
    help = "Seed age-16 tasks across all six categories (idempotent)."

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
        for task_list, tag_name in ALL_AGE16_TASKS:
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

        self.stdout.write(f"Upserted {total_upserted} age-16 tasks.")

        all_slugs = [t["slug"] for task_list, _ in ALL_AGE16_TASKS for t in task_list]
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
        self.stdout.write(self.style.SUCCESS("seed_age16_catalog complete."))
