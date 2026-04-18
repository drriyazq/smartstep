"""Management command: seed the Adult task catalog (age 17+).

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_adult_catalog

Idempotent. 72 tasks — 12 per category across 6 categories — in three adult
life-stage tiers:
    Early Adult   (18-30)  — foundations: first job, first flat, money basics
    Mid Adult     (26-45)  — building: career, relationships, discipline
    Established   (35-99)  — deepening: negotiation, legacy, stewardship

Focus: street-smart, handling real life challenges effectively.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task


def _mk(slug, title, cat, tier, how_to, why, safety=None, prereqs=None):
    """Helper — returns a task dict with consistent shape."""
    tier_ranges = {
        'early': (18, 30),
        'mid': (26, 45),
        'late': (35, 99),
    }
    min_age, max_age = tier_ranges[tier]
    return {
        'slug': slug,
        'title': title,
        'category': cat,
        'min_age': min_age,
        'max_age': max_age,
        'how_to_md': how_to,
        'parent_note_md': why,
        'safety_md': safety or '',
        'prereqs': prereqs or [],
    }


# ═════════════════════════════════════════════════════════════════════
# FINANCIAL (12)
# ═════════════════════════════════════════════════════════════════════

FINANCIAL = [
    _mk('adult-read-payslip', 'Read Your Payslip Like a Pro', 'financial', 'early',
        "## How to practise\n\n"
        "1. **Find your most recent payslip** — ask HR if you don't have one saved. Open it fully.\n"
        "2. **Identify the three layers** — Gross salary, total deductions, Net (take-home). "
        "The gap is usually 15–30% for salaried Indian employees.\n"
        "3. **Understand each deduction** — PF (12%), professional tax, TDS, health premium. "
        "Google anything you don't recognise.\n"
        "4. **Match YTD to Form 16** — every April, reconcile your payslips' YTD "
        "with Form 16. Catch errors before they become tax problems.\n"
        "5. **Save it** — keep 24 months of payslips in a cloud folder. Loans, visas, "
        "job changes all ask for them.",
        "Most working adults can't explain their own payslip line by line. That's "
        "a recipe for silent mistakes — wrong tax slab, missing benefits, underclaimed "
        "deductions. 10 minutes reading yours carefully pays off for years."),

    _mk('adult-emergency-fund-6mo', 'Build a 6-Month Emergency Fund', 'financial', 'early',
        "## How to practise\n\n"
        "1. **Calculate your monthly essentials** — rent, food, transport, utilities, "
        "loans, insurance premiums. Not discretionary spending. Round up.\n"
        "2. **Multiply by 6** — that's your target. For someone with ₹40k essentials, "
        "the fund is ₹2.4 lakh.\n"
        "3. **Open a separate sweep-in savings or liquid fund** — NOT your main spending account. "
        "Out of sight, out of mind.\n"
        "4. **Automate a monthly transfer** — 20% of take-home until the fund is full. "
        "Treat it like rent — non-negotiable.\n"
        "5. **Rebuild the rule** — never dip below 3 months. Above 6 months, the extra should "
        "move into investments.",
        "A real emergency fund is the single biggest buffer between a setback and a crisis. "
        "Job loss, medical event, family emergency — without this, you borrow at 36%. "
        "With it, you just ride it out."),

    _mk('adult-start-sip-index', 'Start a Monthly SIP into a Low-Cost Index Fund', 'financial', 'early',
        "## How to practise\n\n"
        "1. **Open a demat + mutual fund account** — Zerodha Coin, Groww, or directly via AMC. "
        "Free, takes a day.\n"
        "2. **Pick a Nifty 50 or BSE Sensex index fund** — expense ratio under 0.2%. "
        "Avoid actively-managed funds for your first SIP; they underperform most indices.\n"
        "3. **Start small — ₹1,000 a month** — less than a dinner out. The habit matters more "
        "than the amount. Bump it up every year.\n"
        "4. **Automate on salary day** — first of the month, SIP debited. You never see it.\n"
        "5. **Don't check it daily** — markets move. Your SIP compounds for 20+ years. "
        "Check once a year, max.",
        "Time in the market beats timing the market. A 25-year-old starting a ₹5k SIP will "
        "retire richer than a 35-year-old doing ₹15k. The math is unforgiving — "
        "start now, however small."),

    _mk('adult-health-insurance-real', 'Buy Real Health Insurance (Not Just Employer Cover)', 'financial', 'early',
        "## How to practise\n\n"
        "1. **Understand employer cover is fragile** — it ends the day you leave the job. "
        "You need a personal policy too.\n"
        "2. **Minimum ₹10 lakh personal cover** — a single hospitalisation in a decent Indian hospital "
        "can hit ₹5-8 lakh easily. Don't underinsure.\n"
        "3. **Add a super-top-up** — cheaper way to cover ₹30L+. Choose a deductible equal to your base cover.\n"
        "4. **Read exclusions carefully** — pre-existing disease waiting periods, room rent capping, "
        "sub-limits on procedures. These are the traps.\n"
        "5. **Don't cancel when prices rise** — premium goes up with age. Lapsing means restarting the "
        "waiting period. Budget the increase.",
        "Most personal bankruptcies in India are medical. Health insurance is not a luxury — it's the "
        "wall between a hard time and financial ruin. Get it before you need it, not after.",
        "## Safety\n\n"
        "- Never buy through a random call — go direct to the insurer's website or a reputable agent.\n"
        "- Disclose all health history. Non-disclosure is the #1 reason claims are rejected.\n"
        "- Keep premium receipts and policy documents accessible to family."),

    _mk('adult-term-life-insurance', 'Buy Term Life Insurance if Anyone Depends on You', 'financial', 'mid',
        "## How to practise\n\n"
        "1. **Calculate the right cover** — 10–15× your annual income, plus any outstanding loans.\n"
        "2. **Pure term only** — no ULIPs, no endowment, no money-back. Insurance is insurance, "
        "investment is investment. Don't mix them.\n"
        "3. **Compare via aggregator** — Policybazaar, Ditto Insurance, Acko. "
        "Check claim settlement ratios (above 95% is good).\n"
        "4. **Take the medical test seriously** — inaccurate test results or missed disclosures "
        "are the most common claim rejection cause.\n"
        "5. **Nominee and witnesses** — set a clear nominee. Tell your family where the policy is stored "
        "and how to file a claim.",
        "Term insurance is the cheapest, most important thing you'll ever buy. ₹1 crore of cover "
        "for a 30-year-old non-smoker: roughly ₹8,000/year. Your family's financial stability depends on it.",
        "## Safety\n\n"
        "- Never hide smoking / drinking / medical history. You'll pay a slight premium; your family will get the claim.\n"
        "- Don't let the policy lapse. One missed premium can void everything."),

    _mk('adult-credit-card-discipline', 'Use a Credit Card with Complete Discipline', 'financial', 'early',
        "## How to practise\n\n"
        "1. **Pay the FULL bill every month** — not minimum due, not revolving. The ₹1 you carry "
        "over bills you 36–42% APR from day one.\n"
        "2. **Keep utilization under 30%** — if your limit is ₹2L, keep balance under ₹60k. "
        "Protects your credit score.\n"
        "3. **Set autopay for full amount** — never miss a due date. One late payment tanks your CIBIL for months.\n"
        "4. **Review every statement** — spot subscription charges, unauthorized transactions, "
        "fees you don't recognize.\n"
        "5. **Use the float, not the credit** — your card's 45-day grace period is free. "
        "Carrying a balance is not — it's expensive debt.",
        "Credit cards are either the best free money-management tool or the worst debt trap — "
        "and the difference is a single habit: paying the full bill every month. "
        "This one discipline separates wealth-builders from wealth-destroyers.",
        "## Safety\n\n"
        "- Never share CVV, OTP, or PIN — banks and companies will NEVER ask.\n"
        "- Report lost/stolen cards immediately. You're liable for fraud only until reported.\n"
        "- Avoid cash withdrawal on credit card — interest starts from day one, no grace period."),

    _mk('adult-negotiate-salary', 'Negotiate Your Salary Professionally', 'financial', 'mid',
        "## How to practise\n\n"
        "1. **Research market ranges** — AmbitionBox, Glassdoor, LinkedIn Salary. Talk to 3 peers in similar roles. "
        "Know the range before you sit down.\n"
        "2. **Never give the first number** — if asked in first interview, deflect: *What's the band for this role?*\n"
        "3. **State a range, not a point** — *I'm looking at ₹X–Y lakh based on market data for this role.* Upper end is your real target.\n"
        "4. **Negotiate the full package** — base, variable, ESOPs, joining bonus, notice buyout, leave encashment. "
        "All are negotiable.\n"
        "5. **Get it in writing** — nothing's final until the offer letter arrives. "
        "Verbal promises during negotiation rarely survive.",
        "The salary you negotiate at hire compounds for your entire career. Every future raise is a percentage of this number. "
        "One 15-minute uncomfortable conversation = lakhs over a decade."),

    _mk('adult-avoid-lifestyle-creep', 'Avoid Lifestyle Creep — Pay Yourself First', 'financial', 'early',
        "## How to practise\n\n"
        "1. **Fixed savings rate, not variable** — commit to saving at least 25% of every salary. "
        "When raises come, the rate stays the same so savings auto-grow.\n"
        "2. **Automate it the day salary lands** — SIPs, savings account transfer, insurance premiums. "
        "Spend what's left, not what's left over after spending.\n"
        "3. **Set a personal inflation ceiling** — when income doubles, lifestyle rises 30%, not 100%. "
        "The rest becomes wealth.\n"
        "4. **Notice the trap** — new car, new flat, new phone, every year — the classic trap. "
        "Each purchase also becomes a baseline you can't easily reverse.\n"
        "5. **Track net worth quarterly** — the only number that matters long-term. "
        "If it's rising every quarter, lifestyle is under control.",
        "The reason high earners often have no wealth is lifestyle creep. Income goes up; expenses match. "
        "A 25-year-old saving 25% of a modest income ends up richer than a 35-year-old earning 3× but saving 5%."),

    _mk('adult-home-loan-math', 'Understand Home Loan Math Before Signing', 'financial', 'mid',
        "## How to practise\n\n"
        "1. **Calculate the total paid** — ₹50L loan at 9% for 20 years = roughly ₹1.08 crore paid. "
        "Use any EMI calculator; the total can shock.\n"
        "2. **Prepay strategically** — even ₹1L prepayment in year 2 saves 3× that in total interest. "
        "Front-loaded prepayments have outsized impact.\n"
        "3. **Compare floating vs fixed** — floating is almost always cheaper long-term in India. "
        "Fixed gives predictability; floating gives lower cost.\n"
        "4. **Check processing fees, prepayment penalties** — hidden costs. ₹50k on a ₹50L loan is normal. "
        "More is negotiable.\n"
        "5. **Don't max out EMI capacity** — aim for EMI under 40% of monthly take-home. "
        "Leaving room for life means you can handle a bad quarter or job change.",
        "A home loan is the biggest financial commitment most people ever make. The difference between "
        "choosing well and choosing badly: lakhs across two decades. Read before signing.",
        "## Safety\n\n"
        "- Never sign on blank forms.\n"
        "- Get a Sale Deed, not just an Agreement to Sell. Verify title with a property lawyer.\n"
        "- Home insurance for the structure is mandatory for loans — make sure it's actually in place."),

    _mk('adult-manage-parent-finances', 'Help Your Parents Manage Their Finances', 'financial', 'late',
        "## How to practise\n\n"
        "1. **Start the conversation early** — before there's a crisis. Frame it as *I want to understand "
        "your setup so I can help if anything happens.*\n"
        "2. **Inventory assets and accounts** — bank accounts, FDs, insurance, PF, property papers, "
        "pension, will (or lack of). Document in one safe place.\n"
        "3. **Check nominees everywhere** — bank, insurance, EPF, mutual funds. Missing or outdated "
        "nominees = family court if anything happens.\n"
        "4. **Simplify and automate** — too many scattered accounts become a nightmare. Consolidate "
        "where possible. Set up standing instructions for bills.\n"
        "5. **Consider Power of Attorney** — for urgent situations when parents are ill or travelling. "
        "Speak to a family lawyer — small cost, enormous peace of mind.",
        "Aging parents usually haven't organised their paperwork. If something happens suddenly, "
        "you're left trying to reconstruct their financial life while grieving. A 2-hour conversation "
        "today saves months of stress later.",
        "## Safety\n\n"
        "- Never take control — help organise. Autonomy matters.\n"
        "- Involve siblings to avoid suspicions later.\n"
        "- Keep a copy of key documents somewhere safe that you can access in an emergency."),

    _mk('adult-tax-saving-strategy', 'Optimise Your Tax — Old vs New Regime', 'financial', 'mid',
        "## How to practise\n\n"
        "1. **Understand both regimes** — Old: more deductions, more paperwork. New: lower slabs, fewer exemptions. "
        "For most salaried folks with home loan + 80C investments, old is better.\n"
        "2. **Max out 80C (₹1.5L)** — EPF counts, ELSS, PPF, life insurance, home loan principal. "
        "Stack what you already pay.\n"
        "3. **Add 80D for health premiums** — up to ₹25k for self, ₹50k more for parents over 60.\n"
        "4. **NPS 80CCD(1B)** — extra ₹50k deduction if you invest in NPS. Only claim if you understand the lock-in.\n"
        "5. **File your own return (not via HR)** — use ClearTax or cleartax.in. Free for simple returns. "
        "You'll learn more and catch HR errors.",
        "Tax optimisation is not tax evasion. Understanding which deductions you legally qualify for can save "
        "₹50k–₹1L per year — money that would otherwise just leave your pocket. Worth a weekend of learning."),

    _mk('adult-will-succession', 'Write a Will (Even if You Think You Don\'t Need One)', 'financial', 'late',
        "## How to practise\n\n"
        "1. **List your assets** — property, bank accounts, investments, insurance, "
        "physical valuables. Everything that has a monetary or emotional value.\n"
        "2. **Decide who gets what** — specific bequests (my piano to my niece) or shares of total estate. "
        "Write down the names and relationships precisely.\n"
        "3. **Name an executor** — the person who actually distributes. Trusted, organised, and younger than you. "
        "Talk to them first.\n"
        "4. **Write, sign, witness** — in India, a will needs two witnesses. Not your spouse or beneficiaries. "
        "Keep the original in a known safe place.\n"
        "5. **Review every 3-5 years** — marriages, divorces, births, new assets all require updates. "
        "An outdated will creates more trouble than no will.",
        "Dying without a will forces your family to navigate Indian succession law — slow, stressful, "
        "and often divisive. A 2-hour will saves months or years of pain. This applies at 25, not just 65."),
]


# ═════════════════════════════════════════════════════════════════════
# HOUSEHOLD (12)
# ═════════════════════════════════════════════════════════════════════

HOUSEHOLD = [
    _mk('adult-batch-meal-prep', 'Batch Cook 3 Days of Meals in 90 Minutes', 'household', 'early',
        "## How to practise\n\n"
        "1. **Pick one Sunday afternoon** — 90 minutes committed. Music on. Phone down.\n"
        "2. **Cook 3 components** — a protein (chicken/paneer/dal), a grain (rice/roti dough), "
        "a vegetable (sabzi or salad). Each makes 3-4 meals.\n"
        "3. **Mix-and-match across the week** — dal + rice Monday, chicken + rice Tuesday, "
        "dal + roti Wednesday. Avoids food fatigue.\n"
        "4. **Store properly** — cool before refrigerating, glass containers preferred, "
        "label with date. Rice especially — fast cool, 2-3 day max.\n"
        "5. **Reheat once only** — reheating cooked food multiple times is both unsafe "
        "and unpleasant. Portion right from the start.",
        "Batch cooking on Sundays is one of the highest-leverage adult habits. It kills the daily "
        "*what's for dinner?* decision fatigue, saves money vs ordering, and genuinely improves diet. "
        "90 minutes on Sunday buys back 30 minutes a day.",
        "## Safety\n\n"
        "- Cooked rice is a salmonella / Bacillus cereus risk if cooled slowly. Spread on a tray "
        "to cool fast, then fridge within 1 hour.\n"
        "- Never reheat chicken more than once.\n"
        "- Label containers with dates — eyeball-dating food is how people get ill."),

    _mk('adult-week-meal-plan-budget', 'Plan and Shop a Week of Meals on a Budget', 'household', 'early',
        "## How to practise\n\n"
        "1. **Set the budget** — what's reasonable? ₹2000-3000 per person per week for home meals in most Indian cities.\n"
        "2. **Plan dinners first** — 7 dinners. Include variety (dal, sabzi, dry dish, one special). "
        "Breakfasts and lunches usually build off dinners.\n"
        "3. **Build the shopping list by aisle** — produce together, dairy together, grains together. "
        "Cuts shopping time in half.\n"
        "4. **Stick to the list** — no impulse buys (they're what blow budgets). One small treat is fine; "
        "a full cart of extras is the problem.\n"
        "5. **Track spend for 4 weeks** — you'll be surprised what stays in budget and what doesn't. "
        "Adjust the plan, not the budget.",
        "Meal planning is the most valuable 20 minutes you'll spend on a Sunday. Saves money, "
        "reduces waste, cuts cooking decisions to zero. It's one of the real markers between "
        "*feeding yourself* and *running a household*."),

    _mk('adult-basic-home-repair', 'Handle Basic Home Repairs Yourself', 'household', 'early',
        "## How to practise\n\n"
        "1. **Learn these four** — replace a fuse, fix a leaky tap washer, unclog a drain, re-secure a door latch.\n"
        "2. **Fuse replacement** — identify the tripped MCB in your electrical box, reset it. "
        "If it keeps tripping, something's overloaded or shorted — then call an electrician.\n"
        "3. **Leaky tap washer** — shut off under-sink valve, unscrew handle, replace rubber washer. "
        "₹10 repair vs ₹500 plumber call.\n"
        "4. **Drain unclog** — plunger first, then a simple drain snake, then caustic soda sparingly. "
        "Avoid the mystery chemical pours — they damage pipes.\n"
        "5. **Have a basic tool kit** — screwdriver set, pliers, adjustable wrench, hammer, measuring tape. "
        "₹500-1000 one-time purchase that pays for itself 10x.",
        "Calling a tradesperson for every small thing costs real money and leaves you helpless when "
        "they can't come. Four common repairs covers 80% of household issues. Learn them once; use them for decades.",
        "## Safety\n\n"
        "- ALWAYS turn off the main breaker before touching any electrical fitting.\n"
        "- Turn off water at the shut-off valve before any plumbing work.\n"
        "- If you smell gas, do not switch anything on or off. Open windows, leave, call emergency."),

    _mk('adult-tenant-rights', 'Know Your Tenant Rights Before Signing a Lease', 'household', 'early',
        "## How to practise\n\n"
        "1. **Read the rent agreement fully** — every clause. Flag anything unclear. Never sign on trust.\n"
        "2. **Security deposit** — max 2-3 months in most states. Refundable within 30-60 days. "
        "Document the flat's condition at move-in (photos + video).\n"
        "3. **Notice period** — typically 1-3 months. Understand who can terminate, under what conditions.\n"
        "4. **Maintenance and repairs** — who pays for what? Structural is usually landlord, "
        "wear-and-tear is usually tenant. Get it in writing.\n"
        "5. **Know rent control laws** — your state's Rent Control Act protects against arbitrary increases "
        "and illegal eviction. Know what applies to you.",
        "Most renters in India sign whatever agreement the landlord pushes forward. They discover the one-sided "
        "clauses only during disputes. Read before signing, negotiate, get things in writing.",
        "## Safety\n\n"
        "- Never pay deposit in cash without a signed receipt — and then register the rent agreement.\n"
        "- If the landlord demands 12 months' rent advance, walk away — that's not standard.\n"
        "- Record the meter readings on move-in day, photographed with a newspaper showing the date."),

    _mk('adult-manage-house-help', 'Hire and Manage a House Help Fairly', 'household', 'mid',
        "## How to practise\n\n"
        "1. **Agree on scope clearly** — what work, what days, what hours, what is NOT part of the job. "
        "Both parties need the same picture.\n"
        "2. **Fair wage** — research your area. Unpaid days for festivals/sickness are standard. "
        "Undercutting creates resentment and turnover.\n"
        "3. **Write a simple one-page agreement** — days, hours, tasks, wage, leave, notice period. "
        "In their language. Both sign.\n"
        "4. **Provide basics** — separate plate/cup, clean water, fan, rest break if shifts are long. "
        "Not a luxury — common decency.\n"
        "5. **Pay on time, every time** — same date every month, via bank transfer ideally. "
        "Respect in how you pay as much as how much you pay.",
        "Managing domestic workers is about respect more than efficiency. A fair, predictable, respectful "
        "relationship gets you loyalty and stability. The alternative — exploitation — is both ethically wrong "
        "and practically disastrous (constant turnover).",
        "## Safety\n\n"
        "- Verify ID — Aadhaar copy kept with you, photo on file.\n"
        "- Ensure they have a name and number for emergencies. Share yours.\n"
        "- Treat them as you would an employee — because they are."),

    _mk('adult-deep-clean-workflow', 'Deep-Clean Your Home Properly Once a Month', 'household', 'mid',
        "## How to practise\n\n"
        "1. **Set a cadence** — one Saturday a month, 2-3 hours. Music on. Block the calendar.\n"
        "2. **Room-by-room** — start top (fans, ceilings), end bottom (floors). Dust falls down, "
        "so don't vacuum before dusting.\n"
        "3. **Rotate deep tasks** — one month: kitchen deep (inside cabinets, fridge, oven). "
        "Next: bathroom deep. Next: wardrobes and bedding. One area per month.\n"
        "4. **Declutter as you clean** — anything you haven't used in 6 months goes. Storage "
        "is not free — it costs you attention.\n"
        "5. **Restock consumables** — detergent, toilet paper, soap, bulbs. Running out is a weekly "
        "annoyance; monthly top-up eliminates it.",
        "Deep cleaning beyond daily tidy is what separates a house that quietly runs from one that "
        "feels subtly stressful. The investment: 2-3 hours a month. The return: a home that's always "
        "easy to host in, easy to find things in, easy to relax in."),

    _mk('adult-cook-for-ten', 'Host and Cook for Ten People', 'household', 'late',
        "## How to practise\n\n"
        "1. **Plan 2 weeks out** — guest list, dietary restrictions (ask them), menu, seating, drinks. "
        "Everything written down.\n"
        "2. **Menu: 3-4 items, not 8** — one rice, one dal, one sabzi, one dessert. Impressive is depth, not breadth. "
        "Dishes that scale up well (sabzi, not stir fry).\n"
        "3. **Prep as much as possible the day before** — veg chopped, spices ground, dessert done. "
        "On the day, you assemble and cook — not prep from scratch.\n"
        "4. **Stagger cooking times** — things that hold hot (curry, dal) cook first. Things that don't "
        "(rice, bread) cook last. Serve hot, not tepid.\n"
        "5. **Clean as you go** — sink empty when guests arrive. End-of-night cleanup is 15 minutes, "
        "not 2 hours.",
        "Hosting 10 people is a genuine life skill — the ability to feed and welcome a crowd without panic. "
        "It builds community, strengthens relationships, and is one of the real markers of being a capable adult.",
        "## Safety\n\n"
        "- Ask about allergies (nuts, shellfish, gluten) at invite stage, not at the door.\n"
        "- Hot food stays hot (above 60°C) until served; cold food stays cold. 2-hour room temperature max.\n"
        "- Pre-cooked food reheated to piping hot all the way through — kill any bacteria that grew."),

    _mk('adult-subscription-audit', 'Audit Your Subscriptions Monthly', 'household', 'early',
        "## How to practise\n\n"
        "1. **List every recurring charge** — card statements from the last 3 months. Also app stores, "
        "SMS bills, bank standing instructions.\n"
        "2. **Categorise** — entertainment, productivity, storage, news. You probably pay for 3 services "
        "in each category; you use 1.\n"
        "3. **Calculate annual total** — monthly × 12 + annuals. A ₹200/month subscription is ₹2400/year. "
        "That number changes behaviour.\n"
        "4. **Cancel what you used less than 4 times last month** — not threatening, not *maybe*, "
        "actually cancel. You can re-subscribe if you miss it.\n"
        "5. **Set a monthly calendar reminder** — one day of the month to audit. "
        "Subscriptions regrow like weeds if not pruned.",
        "Most adults lose ₹10,000-₹50,000 a year to subscriptions they don't use. It's not about being cheap; "
        "it's about paying only for value received. The monthly audit becomes a small ritual that protects significant money."),

    _mk('adult-home-emergency-kit', 'Build a Household Emergency Kit', 'household', 'mid',
        "## How to practise\n\n"
        "1. **Agree on one cupboard or drawer** — accessible, known to every family member.\n"
        "2. **First aid essentials** — bandages, antiseptic, thermometer, paracetamol, ORS, "
        "any prescriptions + spares, pain relief.\n"
        "3. **Power backup** — torch with batteries, candles, matches, a power bank for phones.\n"
        "4. **Documents accessible** — photocopies of ID, insurance, property, medical records — "
        "in a waterproof folder.\n"
        "5. **Emergency contacts list** — printed. Family, doctor, electrician, plumber, neighbour, "
        "hospital, police. Not just in phones (phones die).",
        "Emergencies — power cut, medical, flooded street, theft — don't announce themselves. "
        "The difference between manageable and disaster is whether you have basics ready and know where they are.",
        "## Safety\n\n"
        "- Check the kit every 6 months — replace expired meds, test batteries.\n"
        "- Teach every adult in the house where it is and what's in it."),

    _mk('adult-moving-out-checklist', 'First Solo Move — Done Right', 'household', 'early',
        "## How to practise\n\n"
        "1. **Minimum 2 weeks advance** — don't scramble. Arrange transport (packers) well in advance.\n"
        "2. **Set up utilities before arrival** — electricity in your name, gas, water, internet. "
        "Arriving to a dark flat on day 1 is painful.\n"
        "3. **First-week grocery list** — rice, dal, oil, salt, sugar, tea/coffee, basic veg. "
        "You won't have energy to shop daily for the first week.\n"
        "4. **Document the flat condition** — walk-through with landlord, photos + video, "
        "email him/her the same day. Protects your deposit.\n"
        "5. **Meet at least one neighbour** — *I just moved in, my name is…* — "
        "matters the day you need something.",
        "First solo moves are where most young adults get their first taste of real independence — "
        "and also where many get ripped off by landlords, packers, or utilities. Preparing a week in "
        "advance changes everything."),

    _mk('adult-deal-with-landlord', 'Deal with Difficult Landlords Calmly', 'household', 'mid',
        "## How to practise\n\n"
        "1. **Everything in writing** — rent, deposit, repairs, extensions. Verbal agreements evaporate "
        "when inconvenient. Email or WhatsApp is fine.\n"
        "2. **Pay on time, every time** — your leverage in every dispute depends on being above reproach "
        "on your own obligations.\n"
        "3. **Report issues immediately, in writing** — not only when they get bad. A water leak that took "
        "6 months to fix becomes your fault otherwise.\n"
        "4. **Know your rights** — state's Rent Control Act, consumer court jurisdiction over rental disputes. "
        "You have more protection than you think.\n"
        "5. **For deposit return** — photograph flat at handover, present yourself for the walk-through, "
        "insist on 30-day return. Written list of any deductions with proof.",
        "The biggest renter mistake is assuming goodwill from the landlord. Assume nothing. Document everything. "
        "The calm, written, on-time tenant wins every dispute."),

    _mk('adult-aging-proof-home', 'Aging-Proof Your Parents\' Home', 'household', 'late',
        "## How to practise\n\n"
        "1. **Bathroom safety** — non-slip mats, grab rails, raised toilet seat if needed, shower seat. "
        "The #1 cause of falls is the bathroom.\n"
        "2. **Lighting** — night lights in corridors, brighter bulbs in stairs, "
        "path-lights from bed to toilet. Older eyes need 3× the light of younger ones.\n"
        "3. **Remove trip hazards** — loose rugs, low cables, kitchen mats that slide. "
        "If you've tripped on it once, your parent will too.\n"
        "4. **Tech for safety** — smart doorbell, video call-capable tablet, panic-button device. "
        "Easy-to-reach landline at the bedside.\n"
        "5. **Medication management** — weekly pill organiser, clearly-labelled, a daily check-in call.",
        "Minor home adjustments transform elderly safety. Most are one-weekend projects that prevent "
        "the fall that lands a parent in hospital for weeks. Start before it's urgent.",
        "## Safety\n\n"
        "- Test-run any new tech with your parent present. Don't install-and-leave.\n"
        "- Keep emergency numbers large and visible near every phone."),
]


# ═════════════════════════════════════════════════════════════════════
# DIGITAL (12)
# ═════════════════════════════════════════════════════════════════════

DIGITAL = [
    _mk('adult-password-manager', 'Set Up and Use a Password Manager', 'digital', 'early',
        "## How to practise\n\n"
        "1. **Install one reputable manager** — Bitwarden (free, open source), 1Password, or Dashlane. "
        "Avoid browser-native managers — they're tied to one browser.\n"
        "2. **Create a strong master password** — 5 random words joined (*correct-horse-battery-staple*). "
        "Write it down, put it in a safe, never save it digitally.\n"
        "3. **Import existing passwords** — browsers, saved accounts. Also migrate the 20 most important "
        "accounts first: email, banks, cards, social.\n"
        "4. **Generate unique passwords** — 20+ characters, random. The manager remembers; you don't.\n"
        "5. **Install the browser extension + mobile app** — auto-fill on every device. "
        "Once set up, you never type a password again.",
        "Password reuse is how most people get hacked. Unique 20-character passwords for every account is "
        "practically impossible without a manager. The manager is the single biggest upgrade to your digital "
        "security you can make in one evening.",
        "## Safety\n\n"
        "- Never store the master password digitally — it's the one key that unlocks everything.\n"
        "- Enable 2FA on the password manager itself.\n"
        "- Share vault access with spouse/trusted person (with emergency access feature) in case of an emergency."),

    _mk('adult-2fa-everywhere', 'Enable 2FA on Every Important Account', 'digital', 'early',
        "## How to practise\n\n"
        "1. **Start with email** — your email resets every other account. If it's compromised, "
        "attackers can reset your banking, social, everything. 2FA your email first.\n"
        "2. **Then banking + cards** — every bank supports 2FA/OTP. Enable any additional "
        "options (transaction limits, geography restrictions).\n"
        "3. **Then social media** — Instagram, Facebook, Twitter. All support 2FA.\n"
        "4. **Prefer app-based 2FA** — Google Authenticator, Authy. SMS 2FA is vulnerable to "
        "SIM swap attacks. Avoid SMS where possible.\n"
        "5. **Save recovery codes** — every 2FA setup gives you recovery codes. Print them, "
        "save them securely. If your phone is lost, these let you back in.",
        "2FA is the single best thing you can do after a password manager. It turns a compromised password "
        "from a crisis into a minor event. Take an evening, do it everywhere.",
        "## Safety\n\n"
        "- Never give out 2FA codes over phone, text, or email. Legitimate companies never ask.\n"
        "- If you get a 2FA code you didn't request, someone's trying to access your account — change the password."),

    _mk('adult-spot-advanced-scams', 'Recognise Advanced Scams (Phone, SIM Swap, Deepfake)', 'digital', 'mid',
        "## How to practise\n\n"
        "1. **The urgency trick** — any message creating urgency (*your account will be locked in 10 minutes*) "
        "is designed to panic you into action. Pause. Verify separately.\n"
        "2. **Phone scams** — never act on a phone call claiming to be bank/govt. Call them back "
        "on their official number from their website.\n"
        "3. **SIM swap** — if your phone suddenly loses signal for no reason, call your operator. "
        "A fraud SIM swap will let someone intercept your OTPs.\n"
        "4. **Voice deepfakes** — if a relative calls in distress asking for money, call them back on "
        "their known number. AI voice clones are now scarily convincing.\n"
        "5. **Video deepfakes** — ask questions only the real person would know. "
        "Schedule a follow-up call to confirm identity before committing anything.",
        "Scammers now use AI and social engineering at a level impossible 3 years ago. Defense is not "
        "technical — it's procedural. Slow down, verify separately, never act on urgency.",
        "## Safety\n\n"
        "- Never share OTP, CVV, PIN, or passwords — even to someone you think is from the bank.\n"
        "- Police/courts/taxmen never use WhatsApp or video calls to issue notices.\n"
        "- Report scams to cybercrime.gov.in or dial 1930."),

    _mk('adult-spreadsheet-mastery', 'Use Spreadsheets for Real Life Decisions', 'digital', 'early',
        "## How to practise\n\n"
        "1. **Pick a real problem** — compare 3 flats you're considering, plan a wedding budget, "
        "track 6 months of spending, analyse if your business idea works.\n"
        "2. **Learn SUM, AVG, IF, VLOOKUP, conditional formatting** — these 5 cover 90% of useful cases. "
        "Free on YouTube, 2 hours total.\n"
        "3. **Clear column headers, consistent formatting** — a messy spreadsheet nobody (including you) "
        "will revisit. Invest in layout.\n"
        "4. **Separate inputs from calculations** — inputs in one colour, formulas in another. "
        "When you change an assumption, you know what cascades.\n"
        "5. **Save a template** — once you've built a useful spreadsheet, strip your data, save as template. "
        "Next time is 10 minutes, not 3 hours.",
        "Spreadsheets are the most under-used super-power for adult decision-making. A 2-hour investment "
        "converts vague anxiety (*is this flat too expensive?*) into clear calculation (*yes, by 15%*)."),

    _mk('adult-linkedin-that-works', 'Build a LinkedIn Profile That Actually Works', 'digital', 'early',
        "## How to practise\n\n"
        "1. **Professional photo** — clean, smiling, business-casual. Phone selfies don't cut it. "
        "Ask a friend for 10 minutes of their time.\n"
        "2. **Headline is prime real estate** — not just *Software Engineer at X*. Use it: *Backend Engineer "
        "building payments systems | ex-Y, ex-Z | Writing about distributed systems*.\n"
        "3. **Summary is your elevator pitch** — 3 short paragraphs: what you do, what drives you, "
        "what you're looking for. Conversational tone.\n"
        "4. **Experience: outcomes, not duties** — *Scaled system from 1M to 10M requests/day* beats "
        "*Responsible for backend*. Numbers everywhere.\n"
        "5. **Post once a month** — a small learning, an opinion, a question. "
        "Stay visible without being exhausting. Engagement compounds.",
        "LinkedIn is the single best tool for career growth in modern India. Every recruiter checks it. "
        "Every new colleague looks you up. A strong profile gets you opportunities; an empty one gets skipped."),

    _mk('adult-use-ai-properly', 'Use AI Tools (ChatGPT, Claude) Properly', 'digital', 'mid',
        "## How to practise\n\n"
        "1. **Pick one tool** — ChatGPT, Claude, Gemini. Use it daily for a month. "
        "Spreading across tools teaches nothing deeply.\n"
        "2. **Give it context** — not *help me write an email*. Give it: who you're writing to, the relationship, "
        "the goal, the tone, what's already been said. Output quality = input specificity.\n"
        "3. **Verify everything factual** — AI hallucinates confidently. Any name, number, date, citation, "
        "code must be independently verified.\n"
        "4. **Use it for thinking, not replacing thought** — brainstorm, outline, critique, summarise. "
        "Don't outsource the decision itself.\n"
        "5. **Protect confidential information** — never paste in customer data, personal details, "
        "unpublished work, credentials. Assume anything you paste could be read.",
        "AI tools are a genuine multiplier for thinking, writing, coding, learning. But they're also "
        "confident fabricators. Used well, you become 2-3× more productive. Used blindly, you spread errors "
        "and sound less like yourself.",
        "## Safety\n\n"
        "- Never input customer data, financial data, personal details, proprietary code without review.\n"
        "- For anything legal/medical/financial, AI is a starting point — not a substitute for a professional."),

    _mk('adult-digital-footprint-audit', 'Audit Your Online Footprint', 'digital', 'mid',
        "## How to practise\n\n"
        "1. **Google yourself** — name, variations, city. See what the internet sees.\n"
        "2. **Archived stuff you forgot** — old Facebook posts, unused profiles, that college blog. "
        "Delete, deactivate, or set to private.\n"
        "3. **Check data breach sites** — haveibeenpwned.com. Lists every breach your email has been in. "
        "Change passwords on anything listed.\n"
        "4. **Tighten privacy settings** — every platform. Who can see your posts? Who can message you? "
        "Who can find you via phone number?\n"
        "5. **Set up monitoring** — Google Alerts for your name. You'll know the moment something new "
        "about you appears online.",
        "Every year, more decisions (hiring, lending, dating) include a quick Google search of you. "
        "The footprint you built 10 years ago is still visible. 2-3 hours once a year keeps it intentional."),

    _mk('adult-secure-online-banking', 'Practise Safe Online Banking', 'digital', 'early',
        "## How to practise\n\n"
        "1. **Separate device or browser profile** — bank only from one trusted setup. "
        "Never from shared/public computers, never over public Wi-Fi without a VPN.\n"
        "2. **Check URL every single time** — HTTPS, exact spelling. Phishing URLs often differ by one character.\n"
        "3. **Set transaction limits** — your bank lets you cap daily transfers, online purchases, international use. "
        "Set each sensibly — unusual activity gets blocked automatically.\n"
        "4. **Monitor transactions weekly** — app notifications for every transaction. "
        "Spot fraud within days, not months.\n"
        "5. **Change passwords every 6 months** — banking, email linked to banking, anywhere finance happens.",
        "Most online banking fraud is preventable with boring discipline. The devices, URLs, limits, "
        "and monitoring you set up today are the wall between you and losing everything tomorrow.",
        "## Safety\n\n"
        "- Never save card details on sites you don't trust completely.\n"
        "- If something looks even slightly off — logout URL redirect, missing branding — STOP. Login fresh.\n"
        "- Call bank on official number (card back) at the first sign of suspicion."),

    _mk('adult-identity-theft-response', 'Have an Identity Theft Response Plan', 'digital', 'mid',
        "## How to practise\n\n"
        "1. **Know the first 60 minutes** — if compromised: change email password, change banking password, "
        "freeze cards, file FIR online, report at cybercrime.gov.in.\n"
        "2. **CIBIL freeze** — you can freeze your credit report to prevent new loans being opened in your name. "
        "Critical if your Aadhaar/PAN are exposed.\n"
        "3. **Compile the paper trail** — every transaction, message, email. The sooner, the more complete. "
        "Screenshots timestamped.\n"
        "4. **Know the helplines** — 1930 (cyber crime), bank's emergency line, Aadhaar customer care. "
        "Save them in the phone now.\n"
        "5. **Tell people** — family and close contacts. A compromised account sometimes sends "
        "money-requesting messages to them.",
        "Identity theft recovery can take weeks to months. The first 24 hours determine whether you lose "
        "₹2000 or ₹2 lakh. A pre-written plan cuts panic and speeds every critical action.",
        "## Safety\n\n"
        "- Never hide the theft from family — you'll need their help and vigilance.\n"
        "- Never transfer money to *recovery experts* who call out of nowhere. They're scammers exploiting your panic."),

    _mk('adult-navigate-govt-portals', 'Master Government Portals', 'digital', 'early',
        "## How to practise\n\n"
        "1. **Income tax** — incometax.gov.in. File your own return once. You'll understand your finances "
        "10× better and catch CA errors forever.\n"
        "2. **Aadhaar** — uidai.gov.in. Biometric updates, address changes, mAadhaar app. "
        "Every adult Indian transaction uses this.\n"
        "3. **Passport** — passportindia.gov.in. Learn the online system. Appointment booking, status, renewals.\n"
        "4. **Vehicle** — parivahan.gov.in. RC transfer, NOC, hypothecation removal, fitness certificates.\n"
        "5. **E-filing grievance** — consumer complaints (consumerhelpline.gov.in), RTI applications. "
        "Your civic power online.",
        "India's government services have moved online. Those who know the portals save weeks and trips. "
        "Those who don't still pay agents. 2-3 hours of exploring these systems pays back for life."),

    _mk('adult-productivity-system', 'Set Up a Personal Productivity System', 'digital', 'mid',
        "## How to practise\n\n"
        "1. **Pick one tool** — Todoist, Notion, Google Tasks, or even paper. Stick with it 3 months.\n"
        "2. **Capture everything** — every commitment, task, idea goes in. Brain is for thinking, "
        "not remembering.\n"
        "3. **Daily plan (5 min)** — top 3 for today. Reality-check against calendar. Everything else is bonus.\n"
        "4. **Weekly review (20 min)** — every Sunday/Friday. Look at last week, plan next. "
        "Spot what slipped.\n"
        "5. **Protect deep work** — calendar blocks for focus. Notifications off during those blocks. "
        "30-45 min blocks, 2-4 per day max.",
        "The productive-seeming people aren't born more organised. They use a simple system, consistently, "
        "for years. Any system followed beats the perfect system postponed."),

    _mk('adult-digital-declutter', 'Digital Declutter — Monthly', 'digital', 'late',
        "## How to practise\n\n"
        "1. **Email inbox zero** — archive what's done, unsubscribe ruthlessly, delete old newsletters. "
        "Aim for 100 or fewer inbox items.\n"
        "2. **Photos** — delete duplicates, screenshots, blurry ones. 10,000 unreviewed photos is worse "
        "than 1,000 curated ones.\n"
        "3. **Apps** — uninstall anything you haven't opened in 30 days. Re-install if you need it back.\n"
        "4. **Cloud storage** — Drive, Dropbox, iCloud. Audit quarterly. Delete what's duplicated, archive "
        "what's rarely needed.\n"
        "5. **Close unused accounts** — old services, forums, shopping sites. Each account is a potential breach. "
        "justdelete.me is a good helper.",
        "Digital clutter is real cognitive weight. It slows your devices, spikes your stress, and creates "
        "attack surface. Monthly 30-minute cleanup keeps your digital life functional."),
]


# ═════════════════════════════════════════════════════════════════════
# NAVIGATION (12)
# ═════════════════════════════════════════════════════════════════════

NAVIGATION = [
    _mk('adult-driving-licence', 'Get Your Driving Licence (Properly)', 'navigation', 'early',
        "## How to practise\n\n"
        "1. **Apply for Learner\'s License online** — parivahan.gov.in. Docs: age/address proof, 2 photos. "
        "Fee ~₹200. Online test (easy).\n"
        "2. **Practise for real** — at least 20 hours actual driving with a licensed adult. Empty grounds "
        "for the first hours; real traffic after.\n"
        "3. **LL valid 30 days minimum before final test** — don't schedule final test before 30 days.\n"
        "4. **Book the final test** — online. Basic parking, hill start, lane discipline. Driving school helps "
        "(~₹3000 for 10 classes). Nervousness is the main failure reason.\n"
        "5. **Smart Card DL arrives by post** — 2-3 weeks. Photo + chip card. Always carry digitally "
        "(DigiLocker app) + physical.",
        "A valid driving licence is required for every road trip, flat rental, sometimes even for a bank "
        "account as ID. Getting it right the first time beats retesting under stress.",
        "## Safety\n\n"
        "- Never drive without a licence. The ₹5000 fine is the least of your worries if something goes wrong.\n"
        "- Never drive after alcohol. Zero tolerance is the safe policy. Cab fare is always cheaper than a BAC case.\n"
        "- Helmet every time on a two-wheeler. Head injuries are irreversible."),

    _mk('adult-file-fir', 'File an FIR or Online Complaint', 'navigation', 'mid',
        "## How to practise\n\n"
        "1. **When to file** — any cognisable offence (theft, assault, harassment, fraud). "
        "You have the right — police cannot refuse.\n"
        "2. **Write before going** — date, time, location, what happened, exact sequence. "
        "Read it back; file it with police.\n"
        "3. **Online FIR for minor cases** — many states support e-FIR for lost property, "
        "mobile theft, phone calls. Saves a trip.\n"
        "4. **Get a copy and FIR number** — no copy = not filed. If police refuse, write to SP/DCP "
        "or approach magistrate.\n"
        "5. **Follow up** — FIR is step 1. Investigation follows. Ask for updates; take names of officers. "
        "Don't pay anyone for *follow-up*.",
        "Most Indians feel helpless at a police station. Knowing your rights and arriving prepared flips that. "
        "A properly written FIR protects you legally and compels action.",
        "## Safety\n\n"
        "- Always get a copy of the FIR before leaving the station.\n"
        "- Note the officer's name, badge number, date, time.\n"
        "- If you're asked to pay anything — it's corruption. Report to vigilance."),

    _mk('adult-navigate-govt-offices', 'Navigate Government Offices Efficiently', 'navigation', 'early',
        "## How to practise\n\n"
        "1. **Research online first** — docs needed, fees, hours. 80% of trips are for missing documents.\n"
        "2. **Go in person, go early** — 9 AM queue vs 11 AM queue is night and day. "
        "Weekday mornings, not weekends/afternoons.\n"
        "3. **Take all originals + copies** — photocopies often needed on-site. A folder with everything "
        "saves trips.\n"
        "4. **Be polite, be persistent** — process matters more than speed. Officials respond to patience, "
        "not aggression. Never raise voice.\n"
        "5. **Never pay a bribe** — the system works without it, slower. Agents charge ₹500-₹5000 for things "
        "you can do yourself. Your time is not that cheap.",
        "Government offices reward preparation and punish impatience. Every trip you avoid is money saved and "
        "stress avoided. 30 minutes online research beats a wasted half-day."),

    _mk('adult-book-domestic-travel', 'Book Domestic Travel Like a Pro', 'navigation', 'early',
        "## How to practise\n\n"
        "1. **Book early for popular routes** — fares double 2 weeks before. Tatkal trains, "
        "weekend flights especially.\n"
        "2. **Know the airline hierarchy** — Indigo, Air India, Vistara, Spicejet. Reliability rankings "
        "change. Check on-time stats.\n"
        "3. **Train vs flight math** — under 8 hours, flight often wins including transit time. "
        "Overnight trains save a hotel.\n"
        "4. **Read cancellation policy** — flexible tickets cost more but save if plans change. "
        "Good for business travel.\n"
        "5. **Double-check IDs match tickets** — exact name, date of birth. Even a middle initial typo "
        "can block boarding.",
        "Cost-effective travel is about process, not hacks. Knowing the ecosystem — portals, policies, tricks — "
        "saves both money and stress on every trip."),

    _mk('adult-interstate-travel', 'Handle Interstate Travel Logistics', 'navigation', 'mid',
        "## How to practise\n\n"
        "1. **Know permit requirements** — some states require e-pass for entry. North-East especially, Sikkim, Lakshadweep.\n"
        "2. **Language barrier prep** — if going to a state whose language you don't speak, download Google Translate "
        "offline, learn 10 basic phrases.\n"
        "3. **Luggage rules** — domestic flights: 15kg check-in typically, 7kg cabin. Trains: 40-70kg depending "
        "on class. Cars: no limit.\n"
        "4. **State-specific taxes/tolls** — FASTag for tolls is essential. Interstate cargo: e-way bills "
        "if moving household goods.\n"
        "5. **Local transport at destination** — pre-book or know the options. Ola/Uber, local taxis, "
        "auto-rickshaws, ride-sharing apps.",
        "Interstate travel in India is actually 28 country trips. Preparing reduces friction — saves time, "
        "money, and culture shock."),

    _mk('adult-international-travel-basics', 'Travel Internationally for the First Time', 'navigation', 'mid',
        "## How to practise\n\n"
        "1. **Passport at least 6 months valid** — most countries require this, regardless of trip length. "
        "Check expiry 3 months before travel.\n"
        "2. **Visa research** — countries with Indian passport visa-free (~60), visa-on-arrival (~30), "
        "visa-required (rest). Check embassy site, not travel blogs.\n"
        "3. **Travel insurance is non-negotiable** — one medical emergency abroad = ₹10 lakh+. "
        "Basic insurance: ₹500-1000 per week.\n"
        "4. **Forex planning** — forex card + backup card + small cash. Inform your bank of travel dates "
        "(fraud blocks are common).\n"
        "5. **Register with MADAD** — madad.gov.in. The Indian embassy system. In any emergency abroad, "
        "they can intervene.",
        "First international trips are often stressful because of unfamiliar systems. 90% of problems are "
        "prevented by an hour of research. Start with simpler destinations (Dubai, Thailand) before long-haul.",
        "## Safety\n\n"
        "- Always carry two forms of ID, stored in different bags.\n"
        "- Email passport scan to yourself — recovery is easier with it.\n"
        "- Know the Indian embassy address and phone for where you're going."),

    _mk('adult-emergency-playbook', 'Have an Emergency Playbook for Real Situations', 'navigation', 'mid',
        "## How to practise\n\n"
        "1. **Accident** — first: Safety. Pull off the road, hazard lights. Check for injuries. "
        "Call 112. Photograph everything. Call insurance.\n"
        "2. **Hospital admission** — insurance cashless where possible. If emergency, pay now, claim later. "
        "Carry policy number in your wallet.\n"
        "3. **Theft** — file FIR within 24 hours ideally. Freeze cards immediately. Change passwords for "
        "compromised accounts.\n"
        "4. **Lost phone abroad** — find-my-phone first, remote wipe if unrecoverable. Block SIM, "
        "inform bank (OTPs).\n"
        "5. **Family emergency while travelling** — know connecting flight options, nearest embassy, "
        "travel insurance's concierge.",
        "Life throws emergencies randomly. Your calm preparation — what numbers, what steps, what document — "
        "converts disasters into manageable problems. Most people panic because they have no plan.",
        "## Safety\n\n"
        "- Emergency number everywhere: 112.\n"
        "- Have trusted family's number memorised, not just saved.\n"
        "- Know your blood type and any chronic conditions — tell first responders."),

    _mk('adult-find-good-doctors', 'Find Good Doctors and Specialists', 'navigation', 'mid',
        "## How to practise\n\n"
        "1. **Build the GP relationship** — one family doctor who knows you. For life. They triage, "
        "refer, save years of specialist-hopping.\n"
        "2. **Verify specialists** — MCI registration, hospital affiliations, actual specialisation "
        "(not just MD with a non-specialty exam).\n"
        "3. **Reviews + referrals** — Practo reviews are useful but crowd-sourced. Trusted friends' "
        "recommendations beat everything else.\n"
        "4. **First appointment: come prepared** — symptoms timeline, medications, allergies, previous "
        "tests. Bullet-point list. You save everyone 30 minutes.\n"
        "5. **Second opinion for anything major** — surgery, cancer, chronic meds. Ethical doctors encourage it. "
        "Bad doctors bristle.",
        "Healthcare decisions often happen under stress. Building the network — GP, trusted specialists — "
        "before emergencies means you make better decisions when urgent ones arrive.",
        "## Safety\n\n"
        "- Never take meds prescribed via WhatsApp or a brief phone call without examination.\n"
        "- Always verify prescriptions match what the doctor said, before filling.\n"
        "- Ask about side effects and interactions before starting anything new."),

    _mk('adult-handle-corrupt-officials', 'Handle Corrupt Officials Without Paying Bribes', 'navigation', 'late',
        "## How to practise\n\n"
        "1. **Never initiate** — don't ask *kya karna hai?* (what needs to be done). Stick to the official process.\n"
        "2. **Have all paperwork ready** — bribe extraction thrives on *missing documents*. "
        "Full file defeats most attempts.\n"
        "3. **Polite firmness** — *Please tell me what's missing so I can bring it.* Don't argue, don't pay, don't leave.\n"
        "4. **Know the escalation path** — every department has a grievance officer, RTI route, vigilance. "
        "Sometimes mentioning these shifts the conversation.\n"
        "5. **Record and report if asked for a bribe** — Vigilance Commission, state anti-corruption bureau. "
        "Evidence changes everything.",
        "Most corruption in India extracts ₹200-₹2000 from people who feel helpless. Patience, paperwork, and "
        "calm firmness defeat it 90% of the time. The day you stop paying is the day the system starts working.",
        "## Safety\n\n"
        "- Never pay cash without a receipt. Always demand a receipt for official fees.\n"
        "- If asked for a bribe, note the name, date, time — report to vigilance.\n"
        "- Get witnesses if possible when engaging with any official."),

    _mk('adult-spot-rental-scams', 'Spot Rental Scams and Bad Flats', 'navigation', 'early',
        "## How to practise\n\n"
        "1. **Too good to be true = scam** — flat at 50% of area rates. Asking for advance before visit. Fake.\n"
        "2. **Always view in person** — never pay a token without physical visit. Scammers thrive on urgency.\n"
        "3. **Verify owner** — Aadhaar + property papers. Match names. Sometimes 'caretaker' is the scammer.\n"
        "4. **Test everything** — taps, geysers, fans, AC, internet speed, mobile signal in every room. "
        "10 minutes of testing saves years of grief.\n"
        "5. **Walk around the locality at night** — is it safe? Well-lit? Quiet? Morning and night tell different stories.",
        "A bad flat choice costs ₹50k-₹2L in wasted deposit, moving costs, broken lease. 2 hours of careful "
        "due diligence eliminates 95% of bad flat decisions.",
        "## Safety\n\n"
        "- Never pay token to someone whose ID you haven't seen.\n"
        "- Register the rent agreement — unregistered agreements have weaker legal protection.\n"
        "- Photograph the flat condition at move-in, with you present in some shots."),

    _mk('adult-stopped-by-police', 'Know Your Rights When Stopped by Police', 'navigation', 'mid',
        "## How to practise\n\n"
        "1. **Stay calm and polite** — no sudden movements, no running, no arguing. "
        "Most stops end uneventfully.\n"
        "2. **Ask why calmly** — *Sir, can I ask what this is about?* You have the right to know. "
        "Most cops answer.\n"
        "3. **Show paperwork** — driving licence, RC, insurance, PUC. Keep digital copies in DigiLocker.\n"
        "4. **Know your rights** — they cannot arrest without reason, cannot search without warrant "
        "(except some cases), cannot detain indefinitely.\n"
        "5. **Document everything** — officer name, badge, station, vehicle number, time. "
        "If anything goes wrong, you have the record.",
        "Police encounters are statistically rare but emotionally charged. Knowing your rights calmly defuses "
        "most situations. Disrespect escalates; courtesy plus firmness de-escalates.",
        "## Safety\n\n"
        "- Never pay a bribe on the roadside — insist on a challan/ticket if there's a violation.\n"
        "- If you feel threatened, drive to the nearest police station (public, safer).\n"
        "- Keep a small dash-cam — evidence helps in disputes."),

    _mk('adult-file-consumer-complaint', 'File a Consumer Complaint That Gets Action', 'navigation', 'mid',
        "## How to practise\n\n"
        "1. **Start with the company** — written complaint (email works), give them 30 days. "
        "Most legitimate companies respond to a clear written complaint.\n"
        "2. **If they don't** — escalate to the official ombudsman. Banking: RBI Ombudsman. Insurance: IRDAI. "
        "Telecom: TRAI. Free.\n"
        "3. **Consumer Court for material disputes** — claims up to ₹1 crore can go to District Commission. "
        "Lawyer not mandatory but helps.\n"
        "4. **Online consumer helpline** — consumerhelpline.gov.in. Central portal, track by complaint number.\n"
        "5. **Keep every document** — invoice, warranty, email chain, screenshots. Evidence wins cases. "
        "Verbal claims don't.",
        "Consumer rights in India are strong but under-used. Most people give up after the company ignores them. "
        "Those who escalate systematically almost always get resolution — and compensation."),
]


# ═════════════════════════════════════════════════════════════════════
# COGNITIVE (12)
# ═════════════════════════════════════════════════════════════════════

COGNITIVE = [
    _mk('adult-decision-framework', 'Use a Decision Framework for Big Choices', 'cognitive', 'early',
        "## How to practise\n\n"
        "1. **Name the decision explicitly** — write it down. Many stuck decisions become easy when "
        "just named clearly.\n"
        "2. **Write the options** — at least 3. If you can only see 2, you haven't thought hard enough.\n"
        "3. **Name what matters** — 3-5 criteria. Weight them. Money isn't always the biggest factor.\n"
        "4. **Pre-mortem** — imagine you chose this; 1 year later, it went badly. Why? The answer reveals hidden risks.\n"
        "5. **Sleep on it** — for any reversible decision. For irreversible ones, sleep twice.",
        "Most regret comes from decisions made emotionally, poorly-framed, or under time pressure. A "
        "15-minute framework produces better results than 6 hours of rumination."),

    _mk('adult-daily-routine', 'Build a Daily Routine That Sticks', 'cognitive', 'early',
        "## How to practise\n\n"
        "1. **Start stupid-small** — wake up, 10 pushups, shower. Not a 2-hour morning routine. Consistency first, depth later.\n"
        "2. **Anchor to existing habits** — after I brush teeth, I meditate 5 min. Habit-stacking.\n"
        "3. **Evening routine matters more than morning** — set out clothes, phone off by 10 PM, "
        "read 10 min. Sleep = next morning's energy.\n"
        "4. **Don't break the chain** — miss one day, never two. One miss is a slip; two is the start of quitting.\n"
        "5. **Track visually** — paper calendar with X marks. Progress is the main motivator.",
        "Motivation is volatile; systems are durable. A small routine done daily beats ambitious plans "
        "pursued inconsistently. Build the boring scaffolding first."),

    _mk('adult-learn-new-skill', 'Learn a New Skill (Solo)', 'cognitive', 'early',
        "## How to practise\n\n"
        "1. **Pick one real skill, one real goal** — *learn Python basics* → *build a script that automates X*. "
        "Goal, not topic.\n"
        "2. **90 days, 30-45 min daily** — short, daily beats weekend marathons. Compound interest in learning is real.\n"
        "3. **Do, don't just watch** — for every 1 hour of tutorial, 2 hours of hands-on. Watching feels productive; "
        "doing actually teaches.\n"
        "4. **Teach back or ship something** — a mini project, a blog post, a talk to a friend. "
        "Forces real understanding.\n"
        "5. **Public commitment** — tell someone what you're learning and by when. Accountability doubles completion rates.",
        "Self-directed learning is the single most valuable adult skill. A new skill every 90 days "
        "compounds into extraordinary range over 10 years. The method matters more than the specific skill."),

    _mk('adult-fact-check-discipline', 'Fact-Check Before Forwarding', 'cognitive', 'mid',
        "## How to practise\n\n"
        "1. **The 30-second rule** — before sharing any claim, spend 30 seconds. Usually reveals misinformation.\n"
        "2. **Reverse image search** — suspicious photo? Google Image. Often shows the original from a decade ago.\n"
        "3. **Check fact-checker sites** — altnews.in, boomlive.in, Snopes. A lot of viral WhatsApp is there already.\n"
        "4. **Multiple reliable sources** — one source = rumor. Three reputable sources = usually true.\n"
        "5. **If you already shared misinformation** — quickly post a correction. "
        "Erasing fake news you spread takes effort but matters.",
        "In India, WhatsApp misinformation has led to lynchings, mob violence, election issues. Your "
        "forwarding habits are a civic responsibility. Slow down before hitting forward."),

    _mk('adult-read-nonfiction', 'Build a Non-Fiction Reading Habit', 'cognitive', 'early',
        "## How to practise\n\n"
        "1. **Small target, daily** — 20 pages a day. ~1 book every 2-3 weeks. 15-20 books a year. Compound gain.\n"
        "2. **Read what you\'ll actually read** — business, history, science, biographies. Not the trophy shelf.\n"
        "3. **Take notes** — highlighter + margin notes + a one-page summary at the end. "
        "Without notes, you forget 80% in a month.\n"
        "4. **Talk about what you read** — a friend, a post, a journal entry. Active recall cements learning.\n"
        "5. **DNF is OK** — not every book is for you. Drop a book that isn't working by page 50. "
        "Time is finite.",
        "Reading 15-20 non-fiction books a year separates you from 95% of adults — not because you're special, "
        "but because you've built a system. Ideas compound. Vocabulary compounds. Mental models compound."),

    _mk('adult-manage-info-overload', 'Manage Information Overload', 'cognitive', 'mid',
        "## How to practise\n\n"
        "1. **Audit your inputs** — news apps, social feeds, newsletters, group chats. Which add value? "
        "Which just fill time?\n"
        "2. **Unsubscribe aggressively** — newsletters you don't read. WhatsApp groups that add nothing. "
        "Apps you open out of habit.\n"
        "3. **Batch information consumption** — news once a day, social twice, email 3 times. "
        "Constant checking kills concentration.\n"
        "4. **Curate actively** — 5 substacks, 3 podcasts, 10 people to follow. "
        "Quality over volume of inputs.\n"
        "5. **Digital sabbath** — one day a week (or afternoon) off. Brain gets space to think, "
        "not just consume.",
        "Modern information flow exceeds human processing capacity. Curating aggressively is not being "
        "antisocial — it's preserving your attention. You literally cannot pay attention to everything, "
        "so choose what gets it."),

    _mk('adult-side-project-complete', 'Finish a Side Project', 'cognitive', 'mid',
        "## How to practise\n\n"
        "1. **Scope it small** — not *start a business*. Something shippable in 2-4 weekends.\n"
        "2. **Write down the endpoint** — *project is done when X exists*. Clear definition prevents "
        "drift and scope creep.\n"
        "3. **Time-box weekly** — 4-6 hours/week. Consistent slots beat random bursts.\n"
        "4. **Ship a v1, even embarrassing** — 80% done and shared beats 100% done and unshipped. "
        "Polish v2 based on real feedback.\n"
        "5. **Share publicly** — LinkedIn post, Twitter, Telegram. Accountability + potential opportunities.",
        "The ratio of people who *think about side projects* to those who *finish one* is enormous. "
        "A shipped v1 — even imperfect — is more valuable than dozens of unfinished ideas."),

    _mk('adult-writing-clearly', 'Write Clearly So People Actually Read It', 'cognitive', 'mid',
        "## How to practise\n\n"
        "1. **Short sentences beat long ones** — most rules break at 25 words. If a sentence has two commas, split it.\n"
        "2. **Lead with the point** — bureaucratic writing buries the request at the end. Good writing starts with it.\n"
        "3. **Cut words** — after writing, remove 20% of words on the second pass. Your point becomes clearer.\n"
        "4. **Read aloud before sending** — anything you stumble over is awkward to the reader too.\n"
        "5. **Know your audience** — a technical colleague vs a non-technical boss. "
        "One email style doesn't fit both.",
        "Clear writing is career rocket fuel. Bad writing gets ignored; great writing gets action. "
        "Most people never practise; 6 months of deliberate effort puts you ahead of 90% of professionals."),

    _mk('adult-public-speaking', 'Get Comfortable with Public Speaking', 'cognitive', 'mid',
        "## How to practise\n\n"
        "1. **Take every chance** — team meetings, family events, bank counters. Low-stakes reps "
        "build the muscle.\n"
        "2. **Structure: 3 points, always** — open with hook, make 3 points with examples, close with action. "
        "Never fails.\n"
        "3. **Breathe before you start** — 3 deep breaths. Nervous energy needs somewhere to go besides shaking voice.\n"
        "4. **Pause beats filler** — silent pause looks confident. *Umm, uhh* sounds insecure. "
        "Comfortable with 2-second silence.\n"
        "5. **Record yourself once a month** — watch cringingly. Notice verbal tics. "
        "Fix one at a time.",
        "Public speaking is the #1 fear for most adults. It's also a clear career differentiator. Regular "
        "small-scale speaking — even in meetings — compounds into comfort at a promotion or wedding speech."),

    _mk('adult-time-blocking', 'Use Time-Blocking for Real Focus', 'cognitive', 'mid',
        "## How to practise\n\n"
        "1. **Your calendar IS your to-do list** — if a task isn't scheduled, it doesn't happen. Block time.\n"
        "2. **Deep work blocks** — 90-120 minutes for important non-urgent tasks. 2-3 blocks a day max.\n"
        "3. **Protect the blocks** — phone silent, door closed (or headphones), Slack/email closed. "
        "Meeting invites declined unless fire.\n"
        "4. **Plan the next day the night before** — 5 minutes. Morning you starts with a clear plan, not anxiety.\n"
        "5. **Weekly review on Friday** — 20 min. What went well? What didn't? Adjust the system.",
        "Productivity is not doing more things. It's doing the right things deeply. Time-blocking is the "
        "simplest way to force this. Most successful people schedule their important work; rest react to inboxes."),

    _mk('adult-weekly-reflection', 'Run a 15-Minute Weekly Review', 'cognitive', 'late',
        "## How to practise\n\n"
        "1. **Same day, same time** — Friday evening or Sunday morning. Consistency beats ambition.\n"
        "2. **What worked this week?** — 3 things. Celebrate them honestly. Positivity before improvement.\n"
        "3. **What didn't work?** — 3 things. No judgement — just notice. Patterns emerge over weeks.\n"
        "4. **One change for next week** — concrete, small, trackable. Not *be more productive* but *decline "
        "meetings with no agenda*.\n"
        "5. **Long-term check-in monthly** — which weekly changes stuck? What slipped? "
        "Your operating system gets better.",
        "Unreviewed life is the same year, lived many times. A weekly 15-minute review forces deliberate choice "
        "and course correction. The most successful people run them almost religiously."),

    _mk('adult-say-no', 'Say No — Well', 'cognitive', 'mid',
        "## How to practise\n\n"
        "1. **Know what to say yes to** — clear priorities make saying no easy. Vague priorities = overcommitment.\n"
        "2. **Short, kind, firm** — *I can't take this on right now. Thanks for thinking of me.* Under 10 words.\n"
        "3. **Don't over-explain** — one sentence, not five. Long explanations invite negotiation.\n"
        "4. **Alternatives where appropriate** — *I can't, but Priya has expertise here* — helps the person, "
        "exits you.\n"
        "5. **Buy time if unsure** — *Let me check and get back in 24 hours*. Buys space to think. "
        "Much better than a panicked yes.",
        "Adults who say yes to everything burn out and deliver mediocre work across the board. Adults who "
        "can say a kind, firm no deliver excellent work on fewer things. Over a career, this difference is "
        "enormous."),
]


# ═════════════════════════════════════════════════════════════════════
# SOCIAL (12)
# ═════════════════════════════════════════════════════════════════════

SOCIAL = [
    _mk('adult-difficult-conversation', 'Have the Difficult Conversation You\'ve Been Avoiding', 'social', 'mid',
        "## How to practise\n\n"
        "1. **Name it in one sentence** — what's the conversation about? *I need to talk about the way we split "
        "household chores.* Without this, the conversation drifts.\n"
        "2. **Pick the time and space** — not in public, not when rushed, not when either is tired. "
        "Private, unrushed, face-to-face.\n"
        "3. **Open with how you feel, not what they did wrong** — *I feel overwhelmed…* beats *You never…*. "
        "Curiosity, not accusation.\n"
        "4. **Listen more than speak** — they need to feel heard first. Summarise what they said before "
        "advancing your own view.\n"
        "5. **End with a concrete next step** — not *let's try harder*. Specific: *I'll take bins on "
        "Tuesdays, you take bills on Thursdays*.",
        "The conversations we avoid define our relationships more than the ones we have. Unsaid things "
        "fester. Most difficult conversations, done well, deepen rather than damage relationships."),

    _mk('adult-set-boundaries-family', 'Set Boundaries with Family', 'social', 'mid',
        "## How to practise\n\n"
        "1. **Identify one real boundary** — unsolicited advice, late-night calls, financial demands, constant "
        "criticism. Pick the most draining one.\n"
        "2. **Short, clear, repeatable** — *I can't pick up calls after 10 PM. I'll call back in the morning.* "
        "Say it exactly the same way each time.\n"
        "3. **Brace for pushback** — especially with Indian families. First weeks are the hardest. "
        "Consistency wins eventually.\n"
        "4. **Don't over-justify** — the more you explain, the more negotiable the boundary seems. "
        "*This is what works for me* is enough.\n"
        "5. **Love is not the same as compliance** — boundaries are how healthy love works. Guilt-tripping "
        "around boundaries is how unhealthy control works.",
        "Setting boundaries with family is harder in Indian contexts than Western — collectivism makes it "
        "feel like betrayal. Done with love and consistency, it deepens rather than breaks relationships. "
        "Your mental health matters; compliance is not the same as connection.",
        "## Safety\n\n"
        "- If setting a boundary triggers serious anger or violence, prioritise safety first. Physical safety > emotional relationship.\n"
        "- If stuck, a family therapist helps. Not a luxury — a tool."),

    _mk('adult-handle-bad-boss', 'Handle a Bad Boss Without Losing Yourself', 'social', 'mid',
        "## How to practise\n\n"
        "1. **Categorise the badness** — incompetent? micromanager? bully? narcissist? Each needs a different strategy.\n"
        "2. **Document everything** — dates, conversations, emails. If it goes to HR or court, evidence "
        "is everything. Build the file quietly.\n"
        "3. **Manage upwards** — even bad bosses respond to clear communication, status updates, "
        "written summaries.\n"
        "4. **Protect yourself emotionally** — don't take it home, don't let them define you. "
        "A bad boss is a bad situation, not a judgement of you.\n"
        "5. **Know your exit options** — network actively. Having one foot out the door makes "
        "present stress bearable.",
        "At least 50% of people leave jobs because of a bad boss, not the company. Handling one well — "
        "documenting, communicating, protecting yourself, planning an exit — is a career-defining skill.",
        "## Safety\n\n"
        "- If there's harassment (sexual, caste, religious), POSH laws in India require action. Document and escalate.\n"
        "- Never confide in coworkers about your boss — it travels. Save it for friends outside work."),

    _mk('adult-make-friends', 'Make New Friends as an Adult', 'social', 'early',
        "## How to practise\n\n"
        "1. **Accept it's weird at first** — adult friendship requires effort that school friendships didn't.\n"
        "2. **Initiate, don't wait** — most people want more friends and are waiting for someone else to invite them. "
        "Be that person.\n"
        "3. **Shared regular activity** — gym buddies, book clubs, running groups, volunteer orgs. "
        "Recurring context beats one-off meetings.\n"
        "4. **Go beyond surface — 2-3 hangouts in** — ask real questions, share something real. "
        "Depth creates friendship; small talk sustains acquaintanceship.\n"
        "5. **Maintain actively** — monthly text, quarterly meeting. Friends don't sustain themselves; "
        "they need watering.",
        "Adult friendships are the #1 predictor of long-term happiness — more than money, more than career. "
        "And they're the hardest to maintain without conscious effort. Starting late is still better than not starting."),

    _mk('adult-dating-self-respect', 'Date with Self-Respect', 'social', 'early',
        "## How to practise\n\n"
        "1. **Know your standards and non-negotiables** — you can't negotiate standards you haven't set. Write them down.\n"
        "2. **Early signals matter** — how someone treats service staff, handles small disagreements, discusses exes. "
        "Watch these.\n"
        "3. **Don't accept being treated badly because you like them** — attraction and respect are separate. "
        "Both are required.\n"
        "4. **Pacing is a gift to yourself** — don't merge lives on date 3. Getting to know someone takes months, "
        "not weeks.\n"
        "5. **Break up cleanly** — kindly, clearly, once. Ghosting hurts you as much as them. "
        "Cleanliness is kindness.",
        "Dating with self-respect means you're the quality control, not just the candidate. Adults who date "
        "from a place of security (not loneliness) attract higher-quality relationships — and recognise red flags earlier.",
        "## Safety\n\n"
        "- First meet in public. Tell a friend your plans. Share your location in real-time during early dates.\n"
        "- Never send intimate photos you wouldn't want public. Even with established partners.\n"
        "- Trust your gut. If something feels off, it usually is."),

    _mk('adult-workplace-conflict', 'Resolve Workplace Conflict Without Drama', 'social', 'mid',
        "## How to practise\n\n"
        "1. **Try direct first** — colleague-to-colleague, privately. Most conflicts resolve if addressed early and calmly.\n"
        "2. **Separate people from problem** — *The approach isn't working for me* beats *You're the problem*.\n"
        "3. **Ask what they need, not just tell what you need** — understanding the other side softens positions.\n"
        "4. **Escalate only when direct fails** — write to manager with facts, not emotion. Record what you've already tried.\n"
        "5. **Be willing to compromise** — perfect resolution isn't always possible. 70% solution that ends the conflict "
        "beats 100% solution nobody agrees to.",
        "Workplace conflict avoidance doesn't solve anything — it accumulates resentment and kills teams. "
        "Handled professionally, conflict strengthens relationships and improves systems."),

    _mk('adult-give-receive-feedback', 'Give and Receive Feedback Professionally', 'social', 'mid',
        "## How to practise\n\n"
        "1. **Specific, not general** — *Your presentation on Tuesday opened too slowly* beats *You're not good at presenting*.\n"
        "2. **Behavior, not character** — *This report had several typos* not *You're careless*.\n"
        "3. **Ask for permission when giving unsolicited** — *Can I share some feedback on that?* Respects autonomy.\n"
        "4. **When receiving, say thanks first** — even if it hurts. Defensiveness closes down the feedback channel.\n"
        "5. **Separate delivery from content** — sometimes the message is valid even if poorly delivered. "
        "Extract the signal.",
        "Feedback is the single largest accelerant of growth, professional and personal. Careers plateau "
        "where feedback stops. Seeking it actively puts you in a tiny minority who keep getting better."),

    _mk('adult-mentor-someone', 'Mentor Someone Junior', 'social', 'late',
        "## How to practise\n\n"
        "1. **Listen more than advise** — mentees usually know the answer; they need to talk it out, not be told.\n"
        "2. **Ask questions that unlock** — *What would success look like?* *What's blocking you?* "
        "*What have you tried?* More useful than answers.\n"
        "3. **Be honest, especially when it's hard** — flattery isn't mentorship. Hard truth, delivered with care, is.\n"
        "4. **Regular cadence** — monthly call, 30 minutes. Beats random availability.\n"
        "5. **Open your network** — introductions, references, recommendations. The access you have is "
        "often more valuable than advice.",
        "Mentoring is how experienced adults pay forward and — importantly — how they keep learning. You "
        "understand your own craft better when you explain it to someone who's asking why. Everyone gains."),

    _mk('adult-authentic-networking', 'Network Without Being Fake', 'social', 'mid',
        "## How to practise\n\n"
        "1. **Real curiosity, not agenda** — at an event, ask genuine questions. People smell agendas a mile away.\n"
        "2. **Quality over quantity** — 3 deep conversations beat 30 business cards. Memory is triggered by depth.\n"
        "3. **Follow up within 48 hours** — brief personalised message referencing what you discussed. "
        "This puts you in the top 5%.\n"
        "4. **Give before asking** — introductions, article shares, job referrals. People remember who helped them.\n"
        "5. **Maintain the network** — quarterly check-in notes. Out of sight, out of mind is real.",
        "Networking done authentically is career rocket fuel. Done transactionally, it backfires. The secret: "
        "be curious, be generous, follow up. That's it."),

    _mk('adult-read-the-room', 'Read the Room Better', 'social', 'mid',
        "## How to practise\n\n"
        "1. **Arrive early, observe** — body language, who's dominating, group dynamics, mood. "
        "5 minutes of observation informs every move.\n"
        "2. **Match the energy** — a serious meeting isn't the place to crack jokes. A celebration isn't "
        "the place to raise concerns.\n"
        "3. **Watch faces, not just words** — tight smiles, clenched jaws, people looking away — these say more than what's spoken.\n"
        "4. **Notice who's quiet** — often the most thoughtful person. Draw them out with a direct question. "
        "You get the best insight.\n"
        "5. **Check yourself** — am I reading my own mood into the room? Emotional spillover from elsewhere is common.",
        "People who read the room well are perceived as empathetic, insightful, and effective — even when "
        "they contribute less. It's a skill of attention, not personality. Anyone can practise it."),

    _mk('adult-apologise-properly', 'Apologise Properly When You\'re Wrong', 'social', 'early',
        "## How to practise\n\n"
        "1. **Own it specifically** — *I was wrong to raise my voice in the meeting yesterday*. "
        "Vague *I'm sorry for everything* isn't an apology.\n"
        "2. **No *but*** — *I'm sorry I yelled, but you were being stubborn* cancels everything. "
        "Full stop after the apology.\n"
        "3. **Acknowledge the impact, not just the intent** — *I know that made you feel disrespected in front of the team*.\n"
        "4. **Say what you'll do differently** — change is the apology; words are just the announcement.\n"
        "5. **Don't expect instant forgiveness** — they need time to process. Your job is to apologise, not "
        "to extract absolution.",
        "A real apology repairs what's been damaged. A fake apology (*I'm sorry you feel that way*) widens "
        "the damage. Adults who can genuinely apologise maintain deeper relationships and earn trust faster after mistakes."),

    _mk('adult-repair-broken-relationship', 'Repair a Broken Relationship Worth Repairing', 'social', 'late',
        "## How to practise\n\n"
        "1. **Decide if it's worth repairing** — not all broken relationships should be. Some are wisely "
        "let go. Examine honestly.\n"
        "2. **Initiate, even if you feel you're more right** — the person who matures first often initiates. "
        "Pride shouldn't be the obstacle.\n"
        "3. **Acknowledge your part** — even if you were 30% wrong, own that 30%. Entirely your partner's fault is rare.\n"
        "4. **Give time and space** — trust rebuilds over months, not evenings. Consistent behaviour change >> grand gestures.\n"
        "5. **Accept you may fail** — some relationships cannot be repaired. Trying gives you peace regardless of outcome.",
        "Repaired relationships are often stronger than ones that never broke — because both parties chose, "
        "consciously, to be in it. But repair requires patience, humility, and the courage to reach first.",
        "## Safety\n\n"
        "- Never pursue repair with anyone abusive. Cutting off contact is healthy, not cruel.\n"
        "- Therapy for both parties speeds up repair in serious relationships."),
]


# ═════════════════════════════════════════════════════════════════════
# Minimal prereq chain — keep adult tasks mostly flat so users can start
# anywhere. Only link obvious sequels.
# ═════════════════════════════════════════════════════════════════════

PREREQ_EDGES = [
    ('adult-start-sip-index', 'adult-emergency-fund-6mo', True),
    ('adult-term-life-insurance', 'adult-health-insurance-real', True),
    ('adult-avoid-lifestyle-creep', 'adult-start-sip-index', False),
    ('adult-tax-saving-strategy', 'adult-read-payslip', True),
    ('adult-will-succession', 'adult-term-life-insurance', False),
    ('adult-week-meal-plan-budget', 'adult-batch-meal-prep', False),
    ('adult-deal-with-landlord', 'adult-tenant-rights', True),
    ('adult-2fa-everywhere', 'adult-password-manager', True),
    ('adult-identity-theft-response', 'adult-2fa-everywhere', False),
    ('adult-spot-advanced-scams', 'adult-password-manager', False),
    ('adult-driving-licence', 'adult-navigate-govt-offices', False),
    ('adult-international-travel-basics', 'adult-book-domestic-travel', False),
    ('adult-emergency-playbook', 'adult-file-fir', False),
    ('adult-fact-check-discipline', 'adult-manage-info-overload', False),
    ('adult-side-project-complete', 'adult-learn-new-skill', True),
    ('adult-time-blocking', 'adult-daily-routine', False),
    ('adult-weekly-reflection', 'adult-time-blocking', False),
    ('adult-give-receive-feedback', 'adult-difficult-conversation', False),
    ('adult-mentor-someone', 'adult-give-receive-feedback', False),
    ('adult-repair-broken-relationship', 'adult-apologise-properly', True),
    ('adult-authentic-networking', 'adult-linkedin-that-works', False),
]


ALL_TASKS = FINANCIAL + HOUSEHOLD + DIGITAL + NAVIGATION + COGNITIVE + SOCIAL


class Command(BaseCommand):
    help = "Seed the adult-tier task catalog (72 tasks, 12 per category). Idempotent."

    def handle(self, *args, **options):
        # Ensure tags exist
        tag_meta = [
            ('Money basics', Tag.Category.FINANCIAL),
            ('Home care', Tag.Category.HOUSEHOLD),
            ('Digital literacy', Tag.Category.DIGITAL),
            ('Wayfinding', Tag.Category.NAVIGATION),
            ('Reasoning', Tag.Category.COGNITIVE),
            ('Social skills', Tag.Category.SOCIAL),
        ]
        cat_to_tag = {}
        for name, cat in tag_meta:
            tag, _ = Tag.objects.get_or_create(
                name=name, defaults={'category': cat}
            )
            cat_to_tag[cat] = tag

        category_map = {
            'financial': Tag.Category.FINANCIAL,
            'household': Tag.Category.HOUSEHOLD,
            'digital': Tag.Category.DIGITAL,
            'navigation': Tag.Category.NAVIGATION,
            'cognitive': Tag.Category.COGNITIVE,
            'social': Tag.Category.SOCIAL,
        }

        all_envs = list(Environment.objects.all())

        added = 0
        for t in ALL_TASKS:
            task, _ = Task.objects.update_or_create(
                slug=t['slug'],
                defaults={
                    'title': t['title'],
                    'how_to_md': t['how_to_md'],
                    'parent_note_md': t.get('parent_note_md', ''),
                    'safety_md': t.get('safety_md', ''),
                    'min_age': t['min_age'],
                    'max_age': t['max_age'],
                    'sex_filter': 'any',
                    'status': ReviewStatus.APPROVED,
                },
            )
            tag = cat_to_tag[category_map[t['category']]]
            task.tags.set([tag])
            task.environments.set(all_envs)
            added += 1
        self.stdout.write(f"Upserted {added} adult tasks.")

        # Wire prerequisite edges
        edges = 0
        for to_slug, from_slug, mandatory in PREREQ_EDGES:
            to_task = Task.objects.filter(slug=to_slug).first()
            from_task = Task.objects.filter(slug=from_slug).first()
            if not to_task or not from_task:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Edge {from_slug} → {to_slug}: task not found"
                    )
                )
                continue
            _, created = PrerequisiteEdge.objects.get_or_create(
                from_task=from_task,
                to_task=to_task,
                defaults={'is_mandatory': mandatory},
            )
            if created:
                edges += 1
        self.stdout.write(f"Added {edges} new prereq edges.")
        self.stdout.write(self.style.SUCCESS("seed_adult_catalog complete."))
