"""Management command: seed age-15 tasks across all six categories.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_age15_catalog

Idempotent — safe to re-run. Uses update_or_create throughout.
Age 15 tasks are near-adult in scope: independent decision-making,
civic awareness, professional preparation, and complex real-world execution.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Tasks grouped by category
# ---------------------------------------------------------------------------

FINANCIAL_TASKS = [
    {
        "slug": "read-payslip-tax-age15",
        "title": "Read a Payslip and Understand Basic Tax",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Get a real payslip** — use a parent's (with permission) or find a "
            "sample online. Identify every line: gross pay, deductions, net pay.\n"
            "2. **Understand deductions** — in India: PF (Provident Fund), ESI, "
            "professional tax, TDS. What is each one for? Who receives it?\n"
            "3. **Calculate net from gross** — given a gross salary and a fixed deduction "
            "percentage, calculate the take-home amount. Use a real example.\n"
            "4. **Income tax slabs** — look up the current income tax slabs. "
            "At what income does tax begin? What are the rates?\n"
            "5. **The real question** — if someone offers a job paying ₹30,000/month, "
            "what will they actually receive? Work it out together."
        ),
        "parent_note_md": (
            "Most young people start their first job with no idea that their gross salary "
            "and their bank deposit are different numbers. Understanding tax before earning "
            "prevents the shock of a first payslip and builds awareness of how public "
            "services are funded. Share your own payslip as a teaching tool."
        ),
        "prereqs": [],
    },
    {
        "slug": "compare-financial-products-age15",
        "title": "Research and Compare Two Financial Products",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a product category** — savings accounts, mobile data plans, "
            "health insurance plans, or fixed deposits. Pick one.\n"
            "2. **Identify two options** — two different banks, two different insurers, "
            "two telecom providers. Use their official websites.\n"
            "3. **Build a comparison table** — columns: price, features, terms, "
            "exit conditions, hidden fees. Fill it in for both options.\n"
            "4. **Identify the catch** — every attractive product has a limitation: "
            "lock-in period, exclusions, minimum balance. Find it.\n"
            "5. **Make a recommendation** — based on a specific scenario "
            "(*a 22-year-old starting their first job*), which product is better and why?"
        ),
        "parent_note_md": (
            "Adults make poor financial decisions primarily because they do not compare "
            "products before committing. Teaching structured comparison — with a table, "
            "not just a gut feeling — is a skill that saves money throughout a lifetime. "
            "Insurance and banking products are deliberately complex; practise reading "
            "the fine print now."
        ),
        "prereqs": [],
    },
    {
        "slug": "invest-basics-age15",
        "title": "Understand the Basics of Investing",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is investing?** — putting money into something expecting it to grow. "
            "Contrast with saving (low risk, low return) and spending (no return).\n"
            "2. **Asset classes** — explain stocks (ownership in a company), bonds (lending "
            "money), mutual funds (pooled investments), real estate, gold. One paragraph each.\n"
            "3. **Risk vs return** — draw the spectrum: savings account (low risk, low return) "
            "→ stocks (higher risk, higher potential return). Nothing is guaranteed.\n"
            "4. **Index funds in simple terms** — a fund that buys a little of everything in "
            "an index (Nifty 50, Sensex). Lower fees, broad diversification.\n"
            "5. **The time advantage** — show what ₹1000/month invested at 10% per year "
            "grows to over 10, 20, and 30 years. Starting at 25 vs 35 makes a dramatic "
            "difference. Show the maths."
        ),
        "parent_note_md": (
            "The greatest financial advantage a young person has is time. Compound growth "
            "over decades is genuinely extraordinary — but only for those who start. "
            "A 15-year-old who understands index funds, risk, and compound interest is "
            "equipped to make their first investment at 18. The concept, not the product, "
            "is the lesson here."
        ),
        "prereqs": [],
    },
    {
        "slug": "negotiate-price-age15",
        "title": "Successfully Negotiate a Price or Deal",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Research first** — know the market price before negotiating. "
            "You cannot negotiate without a reference point.\n"
            "2. **The opening** — start lower than your target, leaving room to move. "
            "State it confidently, not apologetically.\n"
            "3. **Silence is powerful** — after making an offer, stop talking. "
            "The first person to speak after the offer is often the one who gives ground.\n"
            "4. **The trade** — if price cannot move, negotiate terms: "
            "faster delivery, added items, longer warranty, free service.\n"
            "5. **Real practice** — negotiate at a local market, with a second-hand seller, "
            "or for a service. Even ₹50 off is a win. Report back on what worked."
        ),
        "parent_note_md": (
            "Negotiation is used in every adult domain: salary, rent, purchases, contracts, "
            "and relationships. Most people never negotiate because they were never taught "
            "it is acceptable or shown how. A teenager who has practised negotiating even "
            "small amounts has a significant advantage in every future financial interaction."
        ),
        "prereqs": [],
    },
    {
        "slug": "emergency-fund-plan-age15",
        "title": "Build a Personal Emergency Fund Plan",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is an emergency fund?** — money set aside for unexpected events: "
            "phone breaks, illness, transport breakdown, lost income.\n"
            "2. **How much?** — for adults, 3–6 months of expenses. For a teenager with "
            "pocket money: enough to cover one month of their own spending.\n"
            "3. **Where to keep it** — a separate savings account, not the spending account. "
            "Out of sight, out of mind.\n"
            "4. **How to build it** — set a monthly savings target. Calculate how many months "
            "to reach the goal at that rate.\n"
            "5. **The rule** — an emergency fund is only for genuine emergencies. "
            "Define in advance what counts. *Wanting something* does not count."
        ),
        "parent_note_md": (
            "The emergency fund is the single most important buffer between a financial "
            "setback and a financial crisis. Adults without one go into debt when anything "
            "unexpected happens. Building the habit of maintaining a separate reserve — "
            "even a small one — at 15 makes it natural by adulthood."
        ),
        "prereqs": [],
    },
]

HOUSEHOLD_TASKS = [
    {
        "slug": "plan-week-meals-budget-age15",
        "title": "Plan a Week of Meals on a Fixed Budget",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set the budget** — parent gives a realistic weekly food budget for the family "
            "or just for the teenager's meals for the week.\n"
            "2. **Plan seven dinners** — a mix of quick meals and one more involved meal. "
            "Write the menu out.\n"
            "3. **Derive the shopping list** — go through each recipe and list every ingredient needed. "
            "Check what is already in the kitchen.\n"
            "4. **Price it** — estimate the cost of each item. Does the total stay within budget? "
            "If not, swap one expensive meal for a cheaper one.\n"
            "5. **Execute at least two meals from the plan** — they cook, from scratch, "
            "two of the planned meals that week."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Check for any family allergy or dietary restrictions before planning.\n"
            "- Raw meat requires separate chopping boards and thorough cooking to safe temperatures."
        ),
        "parent_note_md": (
            "Meal planning is a convergence of budgeting, nutrition awareness, cooking skill, "
            "and logistics. Adults who can do this spend significantly less on food and eat "
            "better. Starting at 15 — before they are doing it under the pressure of a job "
            "and independent living — is the ideal time."
        ),
        "prereqs": [],
    },
    {
        "slug": "handle-complaint-service-age15",
        "title": "Handle a Consumer Complaint or Service Issue",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a real example** — a faulty product, a wrong delivery, an incorrect "
            "bill, a subscription that was not cancelled. Use a real family issue.\n"
            "2. **Gather evidence** — receipt, order confirmation, photos of the fault. "
            "Know the timeline of events before contacting anyone.\n"
            "3. **First contact** — call or email customer service. They lead — parent nearby "
            "but silent. State the problem clearly, state the desired resolution.\n"
            "4. **If rejected** — what is the escalation path? Consumer court? "
            "Email to the manager? Chargeback on the card? Research the options.\n"
            "5. **Document everything** — keep a record of every contact: date, person spoken to, "
            "what was agreed."
        ),
        "parent_note_md": (
            "Navigating consumer complaints — knowing your rights, communicating assertively "
            "but professionally, and escalating correctly — is a practical adult skill that "
            "most people find uncomfortable. The discomfort decreases with practice. "
            "Finding a real family grievance to resolve makes this immediately meaningful."
        ),
        "prereqs": [],
    },
    {
        "slug": "medical-appointment-solo-age15",
        "title": "Attend a Medical Appointment Independently",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Book it themselves** — call the clinic or use the booking app. "
            "Name, date of birth, reason for visit. They make the call.\n"
            "2. **Prepare for the appointment** — what symptoms? Since when? Any medications? "
            "Any relevant history? Write it down before going.\n"
            "3. **Attend independently** — for a routine appointment (dental check, GP follow-up), "
            "go without a parent. Parent is reachable by phone.\n"
            "4. **During the appointment** — they explain the problem, ask questions, understand "
            "the advice. If they do not understand something, they ask for clarification.\n"
            "5. **After** — report back: what was said? What is the treatment or advice? "
            "Is there a follow-up needed? They manage it."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- For any serious, complex, or first-time medical issue, a parent should attend.\n"
            "- The teenager should know their blood type, any allergies, and any regular "
            "medications before attending alone."
        ),
        "parent_note_md": (
            "A teenager who can book, attend, and report back from a medical appointment "
            "is managing one of the most important aspects of adult self-care. Many young "
            "adults avoid medical care simply because they never learnt how to access it. "
            "Start with a routine appointment (dental, vision check) before more complex ones."
        ),
        "prereqs": [],
    },
    {
        "slug": "deep-clean-space-age15",
        "title": "Deep-Clean a Room from Top to Bottom",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plan before starting** — what needs to happen? Declutter, dust surfaces "
            "(top to bottom), clean glass, vacuum or mop, clean skirting boards.\n"
            "2. **Gather supplies** — microfibre cloths, appropriate cleaner for each surface, "
            "vacuum, mop. Know which chemical to use where.\n"
            "3. **Top-to-bottom order** — always clean from highest surface to lowest "
            "so dust falls onto areas not yet cleaned.\n"
            "4. **Behind and underneath** — furniture moved, not cleaned around. "
            "This is the difference between surface-clean and genuinely clean.\n"
            "5. **Time it** — a full bedroom deep-clean takes 45–90 minutes done properly. "
            "Set aside the time before starting."
        ),
        "parent_note_md": (
            "Knowing how to properly clean a space — not just tidy it — is essential for "
            "independent living, hosting, and presenting a professional environment. "
            "Most teenagers have tidied but never deep-cleaned. This skill becomes "
            "immediately relevant when they move into shared accommodation."
        ),
        "prereqs": [],
    },
    {
        "slug": "handle-utility-bill-age15",
        "title": "Read and Pay a Utility Bill",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Get a real bill** — electricity, water, gas, or internet. "
            "Read every section together: account number, billing period, units consumed, "
            "rate per unit, total due, due date.\n"
            "2. **Understand the calculation** — units used × rate per unit = charges. "
            "Verify the maths on the bill.\n"
            "3. **Check for anomalies** — is this month's usage significantly different from "
            "last month? Why might that be?\n"
            "4. **Pay it** — online banking, app, or at a payment centre. "
            "They complete the payment themselves.\n"
            "5. **Set up a reminder** — when is the next bill due? "
            "Add it to their calendar so the due date is never missed."
        ),
        "parent_note_md": (
            "Utility bills are one of the first adult financial responsibilities. "
            "Young people who have never seen or paid one arrive at independent living "
            "without knowing what a unit of electricity costs, how to read a meter, or "
            "what happens if a bill is unpaid. These are fixable gaps — fix them now."
        ),
        "prereqs": [],
    },
]

DIGITAL_TASKS = [
    {
        "slug": "spot-phishing-scam-age15",
        "title": "Identify and Report a Phishing Attempt or Online Scam",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the red flags** — urgent language, sender email doesn't match the "
            "organisation, links that don't match the claimed site, requests for passwords "
            "or OTPs, too-good-to-be-true offers.\n"
            "2. **Inspect a suspicious email or message together** — hover over links "
            "(don't click), read the sender address carefully, look for spelling errors.\n"
            "3. **The golden rule** — no legitimate bank, government body, or company will "
            "ever ask for a password, OTP, or card number via email, SMS, or a phone call.\n"
            "4. **How to report** — forward phishing emails to the organisation being "
            "impersonated and to cybercrime.gov.in. Delete, never engage.\n"
            "5. **Simulate one** — there are safe phishing simulation tools online. "
            "Run a test email past them and see if they catch it."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never click a link in an unexpected message — go directly to the site "
            "by typing the address.\n"
            "- If you think you have been phished: change the password immediately, "
            "enable 2FA, and tell a parent."
        ),
        "parent_note_md": (
            "Phishing is the most common vector for identity theft, financial fraud, and "
            "account compromise. Teenagers are targeted specifically because they are "
            "digitally active but security-unaware. The golden rule — no legitimate "
            "organisation asks for credentials by message — is one sentence that prevents "
            "the majority of attacks."
        ),
        "prereqs": [],
    },
    {
        "slug": "build-cv-online-age15",
        "title": "Create a Basic CV or Online Profile",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Gather the content** — school, qualifications so far, any part-time work "
            "or volunteering, skills (languages, software, sports), interests.\n"
            "2. **CV structure** — contact info, personal statement (2 sentences), education, "
            "experience, skills, interests. One page maximum at this age.\n"
            "3. **Write it themselves** — parent reviews for clarity and errors but does not "
            "write any section.\n"
            "4. **Create a LinkedIn or equivalent** — set privacy settings correctly, "
            "use a professional photo (school uniform or smart clothing), complete the profile.\n"
            "5. **Update it** — add any new achievement, experience, or skill immediately. "
            "A CV is a living document."
        ),
        "parent_note_md": (
            "A CV at 15 will be sparse — and that is fine. The value is in learning the "
            "format, finding the language to describe oneself professionally, and beginning "
            "to think of life experiences as credentials. Starting early means the first "
            "job application is not the first time they have written one."
        ),
        "prereqs": [],
    },
    {
        "slug": "spreadsheet-real-use-age15",
        "title": "Use a Spreadsheet to Solve a Real Problem",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real use case** — monthly budget tracker, event expense split, "
            "exam score tracker, sports statistics, a recipe cost calculator.\n"
            "2. **Set it up** — columns, rows, labels. Think about what data goes where "
            "before entering anything.\n"
            "3. **Use formulas** — at minimum: SUM, AVERAGE, and a simple IF statement. "
            "Formulas are what make a spreadsheet powerful, not just a table.\n"
            "4. **Make it readable** — formatting: column widths, bold headers, number "
            "format (₹ for currency, % for percentages).\n"
            "5. **Use it** — the spreadsheet must answer a real question. "
            "*What is my total spending this month? What is my average exam score?*"
        ),
        "parent_note_md": (
            "Spreadsheet proficiency — basic formulas, clear layout, and data-driven "
            "answers — is one of the most universally useful workplace skills. It is "
            "required in almost every professional role. Starting with a personally "
            "meaningful problem (budget, sport, exams) makes it stick far better than "
            "a school exercise."
        ),
        "prereqs": [],
    },
    {
        "slug": "ai-tools-critically-age15",
        "title": "Use AI Tools Effectively and Critically",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use an AI assistant for a real task** — summarising a long article, "
            "explaining a concept, brainstorming ideas, drafting an email.\n"
            "2. **Verify the output** — fact-check two claims made by the AI using "
            "independent sources. Did anything need correcting?\n"
            "3. **Understand the limits** — AI can hallucinate (confidently make up facts), "
            "has a training cutoff, and reflects biases in its training data.\n"
            "4. **Good prompting** — the quality of the output depends on the clarity "
            "of the input. Practise writing specific, contextual prompts and compare results.\n"
            "5. **The line** — discuss: when is using AI assistance acceptable "
            "(brainstorming, learning, drafting) versus when does it undermine development "
            "(submitting AI work as your own thinking)?"
        ),
        "parent_note_md": (
            "AI tools are already part of the professional landscape and will only become "
            "more so. Teenagers who know how to use them effectively — and understand their "
            "limitations — have a genuine advantage. The critical skill is not avoidance "
            "but discernment: knowing when AI helps and when it replaces thinking that "
            "should be done by the person."
        ),
        "prereqs": [],
    },
    {
        "slug": "manage-screen-wellbeing-age15",
        "title": "Independently Manage Your Own Screen Time and Digital Wellbeing",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Audit current usage** — check screen time reports (Settings → Screen Time "
            "or Digital Wellbeing). Total hours per day. Top apps. Most active hours.\n"
            "2. **Honest assessment** — which usage is purposeful (learning, creating, "
            "connecting)? Which is mindless (endless scrolling, autoplay)?\n"
            "3. **Set personal limits** — they choose the limits, not the parent. "
            "Use app timers or scheduled downtime. The goal is self-governance.\n"
            "4. **Phone-free zones** — establish personal rules: phone out of the bedroom "
            "at night, no phone during meals, first 30 minutes of the day screen-free.\n"
            "5. **One-week trial** — implement the limits for one week. "
            "Review: how did it feel? What changed? Keep what worked."
        ),
        "parent_note_md": (
            "At 15, the goal is self-regulation, not parental controls. A teenager who "
            "can audit their own usage, recognise unhealthy patterns, and set limits they "
            "actually follow is developing the digital autonomy they will need as an adult "
            "— where no one sets limits for them. The parent's role is to have the "
            "conversation, not to impose the outcome."
        ),
        "prereqs": [],
    },
]

NAVIGATION_TASKS = [
    {
        "slug": "know-legal-rights-age15",
        "title": "Know Your Basic Legal Rights as a Young Person",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Age of majority** — what changes legally at 18 in India? "
            "Voting, contracts, criminal responsibility, marriage. Look these up.\n"
            "2. **Rights if stopped by police** — they do not have to answer questions "
            "without a parent or legal representative present (for minors). "
            "They have the right to know why they are being stopped.\n"
            "3. **Consumer rights** — right to a refund for faulty goods, "
            "right to a receipt, right to dispute a charge.\n"
            "4. **Online rights** — right to request deletion of personal data "
            "(DPDP Act in India), right to know what data is held.\n"
            "5. **Where to get help** — National Human Rights Commission, consumer courts, "
            "ChildLine 1098. Know the numbers."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If stopped by police as a minor, remain calm, do not argue, state you are "
            "a minor and ask for a parent to be contacted.\n"
            "- Knowing your rights reduces vulnerability — but asserting them calmly and "
            "correctly is more effective than aggressively."
        ),
        "parent_note_md": (
            "Young people who do not know their rights are more easily exploited — by "
            "employers, authorities, and commercial entities. Basic legal literacy is "
            "protective and empowering. This is also a natural conversation about civic "
            "responsibility: rights come with corresponding duties."
        ),
        "prereqs": [],
    },
    {
        "slug": "read-contract-before-signing-age15",
        "title": "Read and Understand a Simple Contract Before Agreeing",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a real contract** — a phone plan terms and conditions, a sports "
            "club membership agreement, an app's terms of service.\n"
            "2. **Read it fully** — all of it, including the small print. Note anything "
            "surprising or unclear.\n"
            "3. **Key questions** — what am I agreeing to? What are the exit conditions? "
            "What happens if I break this agreement? Are there auto-renewals?\n"
            "4. **Identify the red flags** — automatic price increases, difficulty cancelling, "
            "data sharing without clear consent.\n"
            "5. **The rule** — never sign or click *I agree* without reading. "
            "If it is too long to read, it is important enough to summarise."
        ),
        "parent_note_md": (
            "Most adults click through terms and conditions without reading them — and "
            "are routinely surprised by charges, data use, and obligations they agreed to. "
            "A teenager who has practised reading a contract before agreeing is equipped "
            "to navigate employment contracts, tenancy agreements, and financial products "
            "as an adult. Start with a short, simple one."
        ),
        "prereqs": [],
    },
    {
        "slug": "basic-first-aid-age15",
        "title": "Learn and Demonstrate Basic First Aid",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The DR ABC protocol** — Danger (is the scene safe?), Response (is the "
            "person conscious?), Airway (is it clear?), Breathing (are they breathing?), "
            "Circulation (call emergency services). Memorise in order.\n"
            "2. **Recovery position** — practise placing a conscious but unresponsive "
            "person in the recovery position. Use a family member.\n"
            "3. **CPR basics** — 30 chest compressions, 2 rescue breaths. Compressions: "
            "hard, fast, centre of the chest. Demonstrate on a cushion.\n"
            "4. **Cuts and bleeding** — apply pressure, elevate the limb, do not remove "
            "the cloth once applied. When to call an ambulance.\n"
            "5. **Enrol in a course** — the St John Ambulance or Red Cross runs youth "
            "first aid courses. A one-day certified course is the goal."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Always call emergency services (112) before or while administering first aid — "
            "do not delay the call to provide treatment.\n"
            "- Do not move a person with a suspected spinal injury unless there is "
            "immediate life-threatening danger (fire, drowning)."
        ),
        "parent_note_md": (
            "First aid knowledge saves lives. In the critical minutes before emergency "
            "services arrive, a bystander who knows the recovery position, how to apply "
            "pressure to a wound, or how to perform CPR can be the difference between "
            "life and death. A 15-year-old is old enough to retain and apply these skills "
            "under stress."
        ),
        "prereqs": [],
    },
    {
        "slug": "lost-phone-wallet-plan-age15",
        "title": "Know What to Do If You Lose Your Phone or Wallet",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Phone lost — immediate steps** — use Find My Device (Google/Apple) "
            "from another device to locate or remote-wipe. Do this before the battery dies.\n"
            "2. **Phone lost — next steps** — report to the carrier to block the SIM, "
            "report the IMEI number to police for an FIR (needed for insurance).\n"
            "3. **Wallet lost — immediate steps** — which cards are in it? "
            "Call each bank's emergency line to block the cards. Numbers should be saved "
            "somewhere other than the wallet.\n"
            "4. **Keep a backup** — memorise one parent's number. "
            "Keep a small amount of cash separate from the wallet.\n"
            "5. **Practise the scenario** — sit down now and answer: "
            "If your phone died right now, what number would you call? "
            "If your wallet was stolen, what would you do first?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Bank emergency numbers: write them on paper and keep them at home, not only in your phone.\n"
            "- Do not use remote wipe until you are certain the phone is not just misplaced — "
            "this erases all data permanently."
        ),
        "parent_note_md": (
            "Adults in their 20s routinely panic when they lose a phone or wallet because "
            "they have no plan. Having the plan in place before it happens — knowing the "
            "bank numbers, knowing how to remote-wipe, knowing who to call — turns a "
            "crisis into a procedure. Run this scenario with your teenager as a drill."
        ),
        "prereqs": [],
    },
    {
        "slug": "interview-for-opportunity-age15",
        "title": "Prepare for and Attend an Interview or Selection Process",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a real opportunity** — school council, sports team, part-time job, "
            "volunteer role, internship, scholarship. Any process with a selection step.\n"
            "2. **Research** — what does the organisation/role need? What would an ideal "
            "candidate look like? Match their language in your preparation.\n"
            "3. **Prepare answers to common questions** — *Tell me about yourself. "
            "Why do you want this? What is a challenge you have overcome?* "
            "Write bullet points, not scripts.\n"
            "4. **Mock interview** — parent or trusted adult asks questions. "
            "Full roleplay: dressed, seated, camera on if it is a video interview.\n"
            "5. **Debrief after the real thing** — what went well? What would you change? "
            "Whether selected or not, this is a skill that improves with every attempt."
        ),
        "parent_note_md": (
            "Interview performance is a learnable skill, not a personality trait. "
            "Teenagers who have been through mock interviews multiple times before their "
            "first real one are noticeably more composed. The discomfort of the mock "
            "interview is the point — exposure reduces anxiety. Start with low-stakes "
            "opportunities and build up."
        ),
        "prereqs": [],
    },
]

COGNITIVE_TASKS = [
    {
        "slug": "research-form-opinion-age15",
        "title": "Research a Complex Topic and Form an Evidence-Based Opinion",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a genuine debate** — climate policy, social media regulation, "
            "reservation systems, AI in education. Something with real complexity.\n"
            "2. **Read multiple sources** — at least three: one news article, one opinion "
            "piece from each side, one data-driven analysis.\n"
            "3. **Map the arguments** — what does each side say? What evidence do they use? "
            "Write a brief summary of each position.\n"
            "4. **Identify weak arguments** — which arguments on either side are based on "
            "emotion rather than evidence? Name them.\n"
            "5. **State your position** — *Based on the evidence, I think… because…* "
            "Be specific. Be willing to say *I'm uncertain* if the evidence is genuinely mixed."
        ),
        "parent_note_md": (
            "The ability to research, weigh evidence, and form a reasoned opinion — as "
            "distinct from adopting a group's view or reacting emotionally — is one of "
            "the defining skills of an educated adult. It protects against manipulation, "
            "improves decision-making, and is the foundation of academic and civic life."
        ),
        "prereqs": [],
    },
    {
        "slug": "manage-competing-priorities-age15",
        "title": "Manage Multiple Competing Priorities in One Week",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **List everything** — write down every commitment, task, and deadline for "
            "the coming week. School, extra-curricular, social, personal.\n"
            "2. **Prioritise** — label each item: urgent+important, important+not urgent, "
            "urgent+not important, neither. The Eisenhower matrix.\n"
            "3. **Block time** — allocate each important task a specific time slot. "
            "Protect those slots from lower-priority interruptions.\n"
            "4. **Handle the conflict** — when two things clash, practise making and "
            "communicating the trade-off: *I can't make X because I have Y. Here is my "
            "alternative.*\n"
            "5. **Friday review** — what was planned? What happened? Where did the week go "
            "off-plan? Adjust the system for next week."
        ),
        "parent_note_md": (
            "The Year 10–12 period is the first time most teenagers face genuinely competing "
            "demands on their time. Those without a system become overwhelmed and drop "
            "things — often the important ones. The Eisenhower matrix is a simple, "
            "proven tool that works at any age. Introduce it during a manageable week "
            "before a pressure period arrives."
        ),
        "prereqs": [],
    },
    {
        "slug": "exam-study-plan-age15",
        "title": "Build and Execute a Study Plan for an Exam",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Work backwards from the exam date** — how many weeks? "
            "How many topics? How many sessions per topic?\n"
            "2. **Distribute the material** — harder topics get more sessions. "
            "Revision of older material is built in. No topic is left to the last day.\n"
            "3. **Active revision only** — writing notes from memory, practice questions, "
            "teaching the topic to someone else. Not re-reading highlighted text.\n"
            "4. **Track completion** — tick off sessions as done. "
            "If behind, redistribute — do not abandon the plan.\n"
            "5. **Post-exam debrief** — when results come back: which topics were weak? "
            "Does that match where time was spent? Update the method for the next exam."
        ),
        "parent_note_md": (
            "Most teenagers revise reactively — cramming before exams rather than spacing "
            "learning over time. Spaced repetition and active recall are the most effective "
            "revision techniques according to decades of research. A teenager who knows "
            "and uses these before major exams has a significant advantage that compounds "
            "over years of study."
        ),
        "prereqs": [],
    },
    {
        "slug": "structured-decision-age15",
        "title": "Make a Major Personal Decision Using a Structured Process",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real decision** — subject choices for next year, which activity "
            "to drop, whether to take a part-time job, which opportunity to pursue.\n"
            "2. **Define the criteria** — what matters in this decision? "
            "List 4–5 factors: enjoyment, future relevance, time cost, difficulty.\n"
            "3. **List the options** — at least three. Do not skip this step — "
            "most people only consider two.\n"
            "4. **Score each option** — rate each option against each criterion (1–5). "
            "Total the scores. This is information, not the final answer.\n"
            "5. **Notice the gut reaction** — when the scores are revealed, what does "
            "their gut say? If the gut contradicts the scores, that is also information. "
            "Discuss both."
        ),
        "parent_note_md": (
            "Teenagers make consequential decisions (subject choices, social commitments, "
            "first jobs) based almost entirely on emotion or peer influence. A structured "
            "process does not remove emotion — but it surfaces the reasoning behind it. "
            "The habit of making decisions deliberately rather than impulsively is one of "
            "the most powerful transfers from adolescence to adulthood."
        ),
        "prereqs": [],
    },
    {
        "slug": "write-formal-application-age15",
        "title": "Write a Formal Application or Personal Statement",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real target** — a scholarship, a school programme, a competition, "
            "a part-time job, a volunteer role. Something they actually want.\n"
            "2. **Read the brief carefully** — what is being asked for? What are the "
            "selection criteria? Underline them before writing a word.\n"
            "3. **First draft without editing** — write freely. Say what they want to say. "
            "Do not self-censor in the first pass.\n"
            "4. **Revise against the criteria** — does every paragraph address something "
            "the selector cares about? Cut everything that doesn't.\n"
            "5. **Read aloud before submitting** — the ear catches what the eye misses. "
            "Fix anything that sounds unnatural or unclear."
        ),
        "parent_note_md": (
            "The personal statement — for a university application, a scholarship, or a "
            "job — is one of the most important pieces of writing a young adult produces. "
            "Teenagers who have practised the process of drafting, revising to criteria, "
            "and editing are significantly better at it when the stakes are real. "
            "Practise on low-stakes applications first."
        ),
        "prereqs": [],
    },
]

SOCIAL_TASKS = [
    {
        "slug": "give-constructive-feedback-age15",
        "title": "Give Constructive Feedback to a Peer",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The formula** — specific observation + impact + suggestion. "
            "Not *that was bad* — *The introduction was unclear, which made it hard to "
            "follow the argument. Starting with your main point would help.*\n"
            "2. **Separate the person from the work** — feedback is about the output, "
            "not the person. *The report has a gap* not *you left out…*\n"
            "3. **Ask permission** — *Can I share some thoughts on this?* "
            "Invited feedback lands very differently from unsolicited feedback.\n"
            "4. **Practise on something low-stakes** — a friend's essay, presentation, "
            "or project. Use the formula. Check how it was received.\n"
            "5. **Receive feedback in return** — the same session, ask for feedback on "
            "something of yours. Practise receiving it without becoming defensive."
        ),
        "parent_note_md": (
            "The ability to give honest, useful feedback without causing offence — and to "
            "receive it without shutting down — is one of the most valued skills in any "
            "workplace or team. Most adults avoid giving feedback entirely because they "
            "have never been taught the formula. Practising it at 15, on low-stakes work, "
            "makes it natural by the time it really matters."
        ),
        "prereqs": [],
    },
    {
        "slug": "lead-a-group-project-age15",
        "title": "Lead a Group or Project from Start to Finish",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Take on a real leadership role** — class project, sports event organising, "
            "family outing planning, community initiative, school club.\n"
            "2. **Define the goal and divide the work** — what needs to happen? "
            "Who is responsible for what? By when? Write it down and share it.\n"
            "3. **Run a check-in** — halfway through, review progress. "
            "Is everyone on track? Does anything need adjusting?\n"
            "4. **Handle a problem** — something will go wrong. "
            "Address it directly: communicate the issue, propose a solution, keep moving.\n"
            "5. **Debrief the group** — after the project: what went well? What was hard? "
            "What would be done differently? A leader learns from the post-mortem."
        ),
        "parent_note_md": (
            "Leadership experience at 15 — even in a small context — builds a skill set "
            "that compounds. Teenagers who have organised people, managed a timeline, "
            "and navigated a setback in a low-stakes environment are far more confident "
            "in leadership roles at university and at work. The scale does not matter — "
            "the process does."
        ),
        "prereqs": [],
    },
    {
        "slug": "difficult-conversation-adult-age15",
        "title": "Have a Difficult Conversation with an Adult",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define the conversation** — disagreeing with a teacher's decision, asking "
            "a parent for a change in a rule, addressing an unfair situation at school.\n"
            "2. **Prepare, don't wing it** — write down the key points. "
            "What is the situation? What outcome do you want? What is your strongest point?\n"
            "3. **Choose the right time** — not when either person is upset or rushed. "
            "Ask: *Can I talk to you about something when you have a moment?*\n"
            "4. **Stay calm and respectful** — state the issue without blame. "
            "*I feel… when… because…* Keep voice level and posture open.\n"
            "5. **Accept the outcome** — the goal is to be heard and understood, "
            "not necessarily to get your way. Distinguish between those two things."
        ),
        "parent_note_md": (
            "Teenagers who can raise a difficulty with an adult — calmly, clearly, and "
            "respectfully — are developing one of the most important skills for adult life. "
            "Every workplace has moments requiring this. Practise it in the safety of the "
            "family first. When your teenager comes to you with a difficult conversation, "
            "receive it as a skill demonstration — even if the content is uncomfortable."
        ),
        "prereqs": [],
    },
    {
        "slug": "introduce-professionally-age15",
        "title": "Introduce Yourself Professionally to an Adult You Don't Know",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The professional introduction** — name, context (school year or interest), "
            "one specific point of connection. Then a question. "
            "*Hi, I'm Aisha. I'm in Year 10, interested in medicine. "
            "I understand you work in healthcare — could I ask what drew you to it?*\n"
            "2. **Practise out loud** — say the full introduction three times. "
            "Vary it slightly each time.\n"
            "3. **Real application** — at a family event, open day, careers talk, or "
            "community event, introduce themselves to one adult they do not know.\n"
            "4. **The follow-up question** — after the intro, ask one genuine question "
            "about the other person's work or experience.\n"
            "5. **Debrief** — what happened? Did the conversation continue? What would "
            "they change next time?"
        ),
        "parent_note_md": (
            "Professional self-introduction is the foundation of networking — a skill that "
            "opens doors throughout adult life. Teenagers who practise this in low-pressure "
            "settings (family events, open days) are comfortable doing it in high-stakes "
            "settings (internship interviews, university fairs). The key is the question "
            "at the end — it turns a monologue into a conversation."
        ),
        "prereqs": [],
    },
    {
        "slug": "manage-online-relationships-age15",
        "title": "Manage Online Relationships and Boundaries",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Audit online contacts** — on every platform, how many people do they "
            "interact with regularly? How many do they know personally?\n"
            "2. **Define online-only relationships** — someone met only online is not "
            "a friend in the same sense as someone met in person. Discuss the distinction.\n"
            "3. **Recognise pressure patterns** — demanding immediate replies, asking for "
            "photos, making the person feel guilty for being offline. These are red flags "
            "in any relationship, online or off.\n"
            "4. **Setting limits** — it is always acceptable to mute, unfollow, block, "
            "or stop responding to anyone online. No explanation is required.\n"
            "5. **The tell-someone rule** — if any online interaction makes them feel "
            "uncomfortable, unsafe, or confused, they tell a trusted adult immediately "
            "and without fear of having their device taken away."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never meet an online-only contact alone or without a parent knowing.\n"
            "- Screenshots of concerning conversations should be saved before blocking — "
            "they may be needed for reporting.\n"
            "- Cyberstalking and online harassment can be reported to cybercrime.gov.in "
            "and to the platform directly."
        ),
        "parent_note_md": (
            "Online relationship management is one of the most significant safeguarding "
            "issues for teenagers. Unhealthy dynamics — including pressure, manipulation, "
            "and exploitation — often develop slowly through platforms teenagers use daily. "
            "The *tell-someone* rule, with an explicit promise of no device confiscation "
            "for reporting, is the most important protective factor."
        ),
        "prereqs": [],
    },
]

# ---------------------------------------------------------------------------
# Prerequisite edges: (to_slug, from_slug, is_mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    ("compare-financial-products-age15", "invest-basics-age15",              False),
    ("write-formal-application-age15",   "build-cv-online-age15",            True),
    ("exam-study-plan-age15",            "manage-competing-priorities-age15", False),
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

ALL_AGE15_TASKS = [
    (FINANCIAL_TASKS,  "Money basics"),
    (HOUSEHOLD_TASKS,  "Home care"),
    (DIGITAL_TASKS,    "Digital literacy"),
    (NAVIGATION_TASKS, "Wayfinding"),
    (COGNITIVE_TASKS,  "Reasoning"),
    (SOCIAL_TASKS,     "Social skills"),
]


class Command(BaseCommand):
    help = "Seed age-15 tasks across all six categories (idempotent)."

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
        for task_list, tag_name in ALL_AGE15_TASKS:
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

        self.stdout.write(f"Upserted {total_upserted} age-15 tasks.")

        all_slugs = [t["slug"] for task_list, _ in ALL_AGE15_TASKS for t in task_list]
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
        self.stdout.write(self.style.SUCCESS("seed_age15_catalog complete."))
