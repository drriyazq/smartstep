"""Management command: refine the Household task ladder.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py refine_household_ladder

Four phases, all idempotent:
  1. Delete 3 duplicates
  2. Retune 20 broad age ranges into proper developmental stages
  3. Add 20 new tasks filling gaps at every tier
  4. Wire ~35 prerequisite edges connecting the ladder
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Phase 1 — Duplicates to delete
# ---------------------------------------------------------------------------

DELETE_SLUGS = [
    "make-bed",            # duplicate of make-bed-age6
    "water-plants",        # duplicate of water-plant-age5
    "make-simple-meal",    # overlaps with cook-full-meal
]

# ---------------------------------------------------------------------------
# Phase 2 — Age range updates
# ---------------------------------------------------------------------------

AGE_RANGE_UPDATES = [
    ("clear-table",                   7,  9),
    ("pack-lunchbox",                 7, 10),
    ("fold-tshirt",                   7, 10),
    ("sweep-small-area",              7, 10),
    ("wipe-kitchen-counters",         7, 10),
    ("sort-laundry-by-color",         8, 10),
    ("wash-dishes",                   8, 11),
    ("crack-egg",                     8, 10),
    ("make-cold-sandwich",            8, 10),
    ("take-out-trash-sort-recycle",   8, 10),
    ("boil-water",                    9, 11),
    ("use-microwave-safely",          9, 11),
    ("use-stove-knob",                9, 11),
    ("load-dishwasher",               9, 12),
    ("pack-travel-bag",               9, 12),
    ("cook-egg",                     10, 12),
    ("cook-pasta",                   10, 12),
    ("cook-full-meal",               11, 13),
    ("iron-clothing",                12, 14),
    ("shaving-basics",               13, 15),
]

# ---------------------------------------------------------------------------
# Phase 3 — New tasks (20 total)
# ---------------------------------------------------------------------------

NEW_TASKS = [
    # ── Age 5-6 (3 tasks) ───────────────────────────────────────────────
    {
        "slug": "wash-hands-age5",
        "title": "Wash Your Hands Properly",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The 20-second rule** — wet hands, apply soap, rub for 20 seconds "
            "(about singing *Happy Birthday* twice). Then rinse.\n"
            "2. **All the places** — palms, backs of hands, between fingers, thumbs, "
            "wrists, under nails. Practise each explicitly.\n"
            "3. **When to wash** — before eating, after the toilet, after playing outside, "
            "after touching pets, when visibly dirty.\n"
            "4. **Dry properly** — a towel or air dry. Wet hands pick up germs faster.\n"
            "5. **Check-up quiz** — *When do we wash hands? How long? "
            "Which parts must we rub?* Weekly refresher."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Warm water is more comfortable but not essential for killing germs — "
            "soap + time is what matters.\n"
            "- Hand sanitiser is OK when no water is available but doesn't remove dirt."
        ),
        "parent_note_md": (
            "Proper hand washing is the single most effective personal hygiene "
            "habit — it prevents more illness than any other daily action. "
            "Children who learn the 20-second rule at 5 carry it for life. "
            "Make it visible: sing along, watch them do it, never rush."
        ),
    },
    {
        "slug": "brush-teeth-age5",
        "title": "Brush Your Teeth Twice a Day",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Twice a day, every day** — morning and night. Non-negotiable. "
            "Link it to fixed events: after breakfast, before bed.\n"
            "2. **Technique** — small circles on every tooth surface: outside, inside, "
            "chewing. Don't forget back molars or the tongue.\n"
            "3. **Two minutes** — use a timer or a song. Most children brush for 30 seconds "
            "and stop. Two full minutes is the real target.\n"
            "4. **Small amount of toothpaste** — pea-sized for children. More foam isn't better.\n"
            "5. **Spit, don't rinse much** — a bit of water, don't rinse thoroughly — "
            "leaves a protective film of toothpaste."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Supervised brushing until 7-8 — children under 7 rarely brush thoroughly "
            "enough alone.\n"
            "- Never swallow toothpaste — it contains fluoride which is fine in "
            "recommended doses only.\n"
            "- Replace the toothbrush every 3 months or when bristles splay."
        ),
        "parent_note_md": (
            "Dental health in childhood determines dental health for life. Children "
            "who brush properly twice daily from age 5 have dramatically fewer cavities "
            "than those who are inconsistent. The habit is what matters — technique "
            "can refine later. Don't skip nights, even tired ones."
        ),
    },
    {
        "slug": "dress-self-fully-age6",
        "title": "Dress Yourself Including Buttons and Zips",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The full sequence** — underwear, socks, trousers/skirt, shirt, jumper if needed, "
            "shoes. Learn the order.\n"
            "2. **Buttons** — practise with a shirt or jacket. Start from the bottom, "
            "line up holes, push button through. Slow at first.\n"
            "3. **Zips** — hold the bottom of the zip, insert the slider onto the track, "
            "pull up firmly. Practise on a jacket.\n"
            "4. **Laces if shoes have them** — bunny ears or cross-over loop method. "
            "Practise dozens of times — it clicks eventually.\n"
            "5. **Morning timing** — once mastered, they dress themselves every morning. "
            "No parent help unless truly stuck."
        ),
        "parent_note_md": (
            "Dressing independently is a foundational autonomy milestone. Children "
            "who can manage all their own clothing fasteners by age 7 are less "
            "dependent on parents during the rushed morning routine and develop "
            "earlier confidence in physical skill acquisition."
        ),
    },
    # ── Age 7-8 (3 tasks) ───────────────────────────────────────────────
    {
        "slug": "shower-self-age7",
        "title": "Shower or Bathe Yourself Thoroughly",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Check water temperature first** — not too hot, not too cold. "
            "Turn the tap slowly.\n"
            "2. **Wet whole body, then soap** — shampoo hair first (if washing), "
            "then soap starting from the neck down. Rinse well.\n"
            "3. **Don't miss areas** — behind ears, under arms, feet (especially between toes), "
            "private parts, back of neck.\n"
            "4. **Finish with a rinse** — all soap off. Soap left on skin causes itching.\n"
            "5. **Dry properly** — pat, don't rub. Especially between toes and ears — "
            "damp warm places grow fungus."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Test water temperature with the back of the hand first, not the face.\n"
            "- Use a non-slip mat in the shower.\n"
            "- Never leave the shower running unattended — hot water can scald "
            "and wastes water."
        ),
        "parent_note_md": (
            "Self-bathing is a quiet milestone that marks genuine hygiene independence. "
            "Children who shower thoroughly without supervision have learned both "
            "self-care and modesty at the right age. Verify for the first few weeks "
            "that no areas are being skipped."
        ),
    },
    {
        "slug": "help-prep-veg-age7",
        "title": "Help Prepare Fruits and Vegetables",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Wash first** — run fruits and vegetables under water. Scrub potatoes/carrots "
            "with a soft brush if muddy.\n"
            "2. **Peel with a peeler** — safer than a knife. Show them: away from the body, "
            "firm grip. Practise on a carrot.\n"
            "3. **Tear instead of cut** — for lettuce, spinach, coriander. "
            "Tearing builds confidence in food handling.\n"
            "4. **Sort ripe from unripe** — help them see when a tomato is ready, "
            "when a banana has gone too far. Practical food awareness.\n"
            "5. **Be their sous-chef** — when cooking, let them prepare the vegetables "
            "while you handle the knife work and stove."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Peelers can cut — always peel with the stroke moving away from the body.\n"
            "- Always wash hands before and after handling food.\n"
            "- Any cuts or scrapes covered with a plaster before food prep."
        ),
        "parent_note_md": (
            "Food prep alongside a parent is a gentle entry into cooking. Children who "
            "are regularly involved eat more vegetables, understand where food comes "
            "from, and are ready for real cooking at 9-10. Treat them as genuine helpers, "
            "not as an audience."
        ),
    },
    {
        "slug": "hang-laundry-age7",
        "title": "Hang Clean Laundry to Dry",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pegs and lines** — show how to peg a shirt by the hem, trousers by the waist. "
            "Not by the shoulder (stretches fabric) or middle (slow drying).\n"
            "2. **Don't crowd the line** — leave space between items for air. "
            "Crowded washing dries slower and smells damp.\n"
            "3. **Shake before hanging** — reduces creases and speeds drying.\n"
            "4. **Know the weather** — if rain is likely, hang inside. "
            "If sunny, outside. Check before starting.\n"
            "5. **Bring it in dry** — don't leave clothes on the line overnight. "
            "Damp returns, birds, insects, theft."
        ),
        "parent_note_md": (
            "In India, line-drying is still the norm — even where machines exist, "
            "clothes lines are common. A child who can hang laundry properly is "
            "contributing real work to the household and gaining a practical skill "
            "they'll use every week for life."
        ),
    },
    # ── Age 9-10 (4 tasks) ──────────────────────────────────────────────
    {
        "slug": "safe-knife-use-age9",
        "title": "Use a Kitchen Knife Safely for Simple Cutting",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with the right knife** — a small paring knife, sharp "
            "(counter-intuitive: sharp is safer than blunt — less slipping).\n"
            "2. **The claw grip** — curl the fingers of the holding hand so knuckles "
            "face the blade, not fingertips. Demonstrate explicitly.\n"
            "3. **Stable cutting board** — place a damp cloth underneath so it doesn't slide.\n"
            "4. **Simple cuts first** — soft fruits (banana, strawberry), then cooked "
            "vegetables, then raw vegetables. Build up.\n"
            "5. **Knife down while not using** — lay flat on the board, never let it "
            "overhang the counter edge, never leave it in a sink of water."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If a knife falls, do NOT try to catch it. Step back, let it land.\n"
            "- Never walk around the kitchen with a knife — set it down first.\n"
            "- Always cut on a stable board, never in the hand.\n"
            "- Sharp knives cut through distraction — focus on the knife, not the TV."
        ),
        "parent_note_md": (
            "Knife skills are central to cooking and notoriously under-taught. A "
            "child who learns proper grip, claw hand, and stable board at 9 cuts "
            "safely for life. Most knife injuries come from dull knives, rushed cuts, "
            "or unstable boards — address all three."
        ),
    },
    {
        "slug": "read-simple-recipe-age9",
        "title": "Read and Follow a Simple Recipe",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read it all first** — before touching ingredients, read the full recipe. "
            "Know the whole journey before starting.\n"
            "2. **Check you have everything** — ingredients and tools. Writing down what's "
            "missing beats discovering mid-cook.\n"
            "3. **Measurements matter** — teaspoon vs tablespoon vs cup. One line of "
            "mistaken measurement changes the whole dish. Set out measuring spoons.\n"
            "4. **Follow the order exactly** — recipes list steps in order for a reason. "
            "Don't skip ahead.\n"
            "5. **Clean as you go** — wipe the counter between steps, wash bowls while "
            "things cook. Half the stress of cooking is the cleanup at the end."
        ),
        "parent_note_md": (
            "Recipe literacy is the entry point to real cooking. Children who can read, "
            "prepare, and follow a simple recipe have a universe of meals open to them. "
            "The *clean as you go* habit is particularly valuable — it's what separates "
            "those who enjoy cooking from those who hate it."
        ),
    },
    {
        "slug": "make-breakfast-age9",
        "title": "Make a Simple Breakfast Independently",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with no-cook options** — cereal with milk, fruit with yoghurt, "
            "toast with jam. No stove needed.\n"
            "2. **Move to toaster and microwave** — boiled milk, warm parathas, toasted bread. "
            "Master these before progressing.\n"
            "3. **A single-egg dish** — once they can crack eggs and use the stove, "
            "scrambled or boiled. A simple omelette after that.\n"
            "4. **The full breakfast** — a drink (juice or milk), a main (cereal or toast or egg), "
            "a fruit. Make it balanced.\n"
            "5. **On school mornings** — for a week, they make their own breakfast "
            "every day. See if they can stick to it."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Toasters: never stick a knife in to dig out bread. Unplug first.\n"
            "- Microwaves: no metal, steam can scald — open lids away from face.\n"
            "- Stove work only with adult awareness nearby."
        ),
        "parent_note_md": (
            "Making your own breakfast is the first fully independent meal a child "
            "prepares. It also solves one of the biggest weekday friction points — "
            "getting fed in the morning. A 9-year-old who can reliably make their own "
            "breakfast is genuinely helpful to the whole household."
        ),
    },
    {
        "slug": "help-grocery-age10",
        "title": "Help with Grocery Shopping from a List",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plan the list together** — what's needed for the week? "
            "Organise by shop section: produce, dairy, dry goods.\n"
            "2. **Read the list as you go** — don't rely on memory. Tick off items as "
            "they go into the basket.\n"
            "3. **Compare sizes and brands** — same item, different prices. Why? "
            "Is bigger cheaper per kg? (Introduction to unit pricing.)\n"
            "4. **Check dates on perishables** — milk, bread, vegetables. "
            "Closer-to-expiry items go further back on the shelf for a reason.\n"
            "5. **At the checkout** — watch the scan, notice the total. "
            "Is it close to what you expected? Check the receipt."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Hold the trolley near the parent at busy times — getting lost in a supermarket "
            "is common at this age.\n"
            "- Never accept anything from a stranger who approaches in a shop."
        ),
        "parent_note_md": (
            "Grocery shopping with a child teaches planning, reading (the list), numeracy "
            "(prices and totals), decision-making (choices between products), and "
            "organisation. It's one of the richest life-skills exercises available, and "
            "most households do it weekly anyway."
        ),
    },
    # ── Age 11-12 (4 tasks) ─────────────────────────────────────────────
    {
        "slug": "clean-bathroom-age11",
        "title": "Clean a Bathroom Thoroughly",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Gather supplies** — toilet brush, bathroom cleaner, glass cleaner, "
            "cloths, rubber gloves. All in one place before starting.\n"
            "2. **Top to bottom** — mirror and high surfaces first. Then sink. "
            "Then toilet. Then floor. Dust and dirt fall downward.\n"
            "3. **The toilet routine** — cleaner inside, leave 5 minutes, scrub. "
            "Wipe outside including seat, lid, handle, base.\n"
            "4. **Don't mix cleaners** — bleach and ammonia produce toxic fumes. "
            "One cleaner at a time.\n"
            "5. **Floor last** — after everything else. Sweep, mop, let dry before walking."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Always wear rubber gloves when using chemical cleaners.\n"
            "- Never mix cleaning products — some combinations produce toxic gas.\n"
            "- Ventilate the bathroom while cleaning (open window or fan)."
        ),
        "parent_note_md": (
            "Proper bathroom cleaning is a skill most young adults leave home without. "
            "Teaching it at 11-12 — with the gloves-on, top-to-bottom, don't-mix-cleaners "
            "rules — establishes cleanliness standards and safety habits that transfer "
            "directly to hostel life and future homes."
        ),
    },
    {
        "slug": "change-bed-sheet-age11",
        "title": "Change a Bed Sheet Properly",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Strip the old sheets** — remove fitted sheet, flat sheet, pillowcases. "
            "Check the mattress for anything underneath.\n"
            "2. **Fitted sheet first** — elastic corners go on the mattress corners. "
            "Work around — top-left, top-right, bottom-right, bottom-left.\n"
            "3. **Flat sheet on top** — pattern-side down (so it shows right-side-up when folded back). "
            "Tuck in the bottom and sides.\n"
            "4. **Pillowcases** — pillow in, corners pushed into corners. "
            "Shake the case so the pillow fills it properly.\n"
            "5. **Old sheets to laundry** — directly, not left on the floor."
        ),
        "parent_note_md": (
            "Changing bed sheets is a weekly hygiene task most children never learn until "
            "they move out. A child who can do it at 11 maintains their own bed, "
            "contributes to the household, and understands the rhythms of clean-linen "
            "living. Frequency: at least once a week."
        ),
    },
    {
        "slug": "understand-food-storage-age11",
        "title": "Understand Expiry Dates and Food Storage",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read dates on packets** — *Use by* (must eat before), "
            "*Best before* (safe after, just lower quality), *Manufactured* (when made).\n"
            "2. **Fridge, freezer, or shelf** — each food has a correct storage spot. "
            "Milk, eggs, leftovers → fridge. Meat long-term → freezer. Rice, flour → shelf.\n"
            "3. **Fridge organisation** — raw meat on bottom shelf (no drips on other food). "
            "Dairy in the middle. Vegetables in drawers.\n"
            "4. **Leftovers** — cover, cool before putting in fridge, use within 2-3 days. "
            "Label with date if possible.\n"
            "5. **Trust your senses** — a food past its date that smells fine may still be OK. "
            "A food within date that smells bad is not. Always check."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Raw chicken is the highest food-safety risk — wash hands immediately after "
            "handling, use separate chopping boards.\n"
            "- Reheated rice is a common source of food poisoning (*Bacillus cereus*) — "
            "cool rice quickly after cooking and store in the fridge.\n"
            "- When in doubt, throw it out. Cheaper than food poisoning."
        ),
        "parent_note_md": (
            "Food storage literacy prevents illness, waste, and wasted money. Children "
            "who understand dates and proper storage do not get food poisoning as often, "
            "and manage a kitchen more confidently when they live alone."
        ),
    },
    {
        "slug": "home-first-aid-age12",
        "title": "Apply Basic First Aid at Home",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know where the kit is** — every home should have a first aid kit. "
            "Show them exactly where, and what's inside.\n"
            "2. **Small cuts and scrapes** — wash with water, apply antiseptic, cover with a plaster.\n"
            "3. **Burns** — cool running water for 10 minutes. Never butter, ice, or toothpaste. "
            "A blister means don't pop — cover with loose gauze.\n"
            "4. **Nosebleeds** — lean FORWARD (not back), pinch soft part of nose for 10 minutes, "
            "breathe through mouth. If not stopping, doctor.\n"
            "5. **When to call for real help** — lost consciousness, breathing difficulty, "
            "severe bleeding, suspected broken bone, head injury with vomiting → 112 immediately."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Learn CPR basics separately — recovery position and rescue breaths can save lives.\n"
            "- Keep the first aid kit stocked — check expiry on medicines quarterly.\n"
            "- A first aid course (St John Ambulance, Red Cross) is more valuable than any amount of reading."
        ),
        "parent_note_md": (
            "First aid at home gives a 12-year-old genuine capability — they can help "
            "a younger sibling, a grandparent, or themselves in a minor emergency. It "
            "also builds confidence to handle rather than panic. Walk them through your "
            "home first aid kit explicitly."
        ),
    },
    # ── Age 13-14 (3 tasks) ─────────────────────────────────────────────
    {
        "slug": "plan-meals-few-days-age13",
        "title": "Plan Meals for Two to Three Days",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick 2-3 days** — weekend or school holidays. Plan breakfast, lunch, dinner "
            "for each day.\n"
            "2. **Consider balance** — a protein, a carbohydrate, a vegetable in each meal. "
            "Not every meal perfectly balanced — across the 3 days, yes.\n"
            "3. **Use what you have** — open the fridge and pantry first. "
            "What's already there? Plan around it to avoid waste.\n"
            "4. **Shopping list for what's missing** — derive from the plan. "
            "Specific quantities, not just *eggs* but *12 eggs*.\n"
            "5. **Execute one of the meals** — they plan AND cook it. "
            "Closing the loop is the learning."
        ),
        "parent_note_md": (
            "Multi-day meal planning is the bridge between cooking individual dishes and "
            "running a kitchen. It integrates nutrition awareness, inventory checking, "
            "shopping, and actual cooking — the full cycle. This skill is rare even in "
            "adults; starting at 13 is a substantial head start."
        ),
    },
    {
        "slug": "basic-grooming-age13",
        "title": "Manage Basic Hair Care and Grooming",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Hair washing routine** — how often depends on hair type and activity. "
            "Shampoo, rinse, condition if needed. Don't over-wash.\n"
            "2. **Hair styling basics** — for them, appropriate for their hair type. "
            "Combing, drying, simple style.\n"
            "3. **Nail care** — trim every 2-3 weeks. Straight across for toes to avoid ingrown nails. "
            "Keep clean underneath.\n"
            "4. **Skin care** — teenage skin produces more oil. Simple face wash morning and night. "
            "Don't pick spots.\n"
            "5. **Body odour management** — daily shower, deodorant, fresh clothes. "
            "Puberty brings new odour — no embarrassment, just good habits."
        ),
        "parent_note_md": (
            "Puberty brings new grooming requirements. Teenagers who are taught explicitly "
            "(not left to figure it out from peers or media) develop healthy, sustainable "
            "grooming habits without either neglect or obsession. The conversation should "
            "be matter-of-fact — this is maintenance, not vanity."
        ),
    },
    {
        "slug": "manage-own-health-routine-age13",
        "title": "Manage Your Own Medicine and Health Routine",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Daily medication** — if on any regular medicine (asthma, allergies, etc), "
            "they take it themselves at the right time. Set a phone reminder.\n"
            "2. **Know what they're taking and why** — not just *the blue pill*. "
            "Name, purpose, dose. Important for any doctor visit.\n"
            "3. **Sleep, water, exercise** — the non-medicine health basics. "
            "Track for one week: sleep hours, water intake, physical activity minutes.\n"
            "4. **Recognise when to see a doctor** — fever over 3 days, pain that worsens, "
            "any new lump, mental health concerns. Not everything self-resolves.\n"
            "5. **Vaccination and check-up records** — know where their records are. "
            "What booster is due? When was the last dental check?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never share prescription medicine with friends.\n"
            "- Never take more than the prescribed dose of any medicine, "
            "even painkillers (paracetamol overdose can cause liver failure).\n"
            "- Always tell a parent about any medicine they're taking, "
            "even from a pharmacy."
        ),
        "parent_note_md": (
            "Teenagers who manage their own health routine — medicine, sleep, basic "
            "awareness — arrive at adulthood as active participants in their health, "
            "not passive patients. The prescription awareness (name, purpose, dose) is "
            "particularly important and often neglected."
        ),
    },
    # ── Age 14-16 (2 tasks) ─────────────────────────────────────────────
    {
        "slug": "manage-leftovers-age14",
        "title": "Manage Food Leftovers and Avoid Waste",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Cool then refrigerate** — cooked food out within 2 hours. "
            "Cover, label with date, put away.\n"
            "2. **Use within 2-3 days** — leftovers aren't infinite. "
            "Eat sooner rather than throwing away later.\n"
            "3. **Reinvent the meal** — leftover dal → dal paratha. Leftover rice → fried rice. "
            "Leftover roast veg → wrap with sauce. Same meal twice is boring; reinvention isn't.\n"
            "4. **Reheat properly** — to piping hot all the way through. "
            "Stir midway if microwave. Never reheat more than once.\n"
            "5. **Freeze when in doubt** — if you won't eat it in 2 days, freeze it the first day. "
            "Freezers are forgiving; fridges are not."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Rice is especially risky — cool fast (within 1 hour), store cold, reheat once.\n"
            "- Never reheat chicken more than once.\n"
            "- If it smells off, it is off. Compost or discard — never *eat to save it*."
        ),
        "parent_note_md": (
            "Food waste is environmentally and financially significant. A teenager who "
            "manages leftovers well — cooling, storing, creatively reinventing, freezing "
            "decisively — contributes real value to the household and develops habits "
            "that carry into their own kitchen."
        ),
    },
    {
        "slug": "care-for-sibling-age15",
        "title": "Care for a Younger Sibling for a Few Hours",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know the plan before parents leave** — meal times, bedtime, any medications, "
            "emergency contacts, what to do if X happens.\n"
            "2. **Keep the sibling engaged** — simple activities: cooking together (age-appropriate), "
            "a game, a craft, a shared show. Avoid non-stop screens.\n"
            "3. **Manage meals** — warm a prepared meal, or make something simple they can "
            "both eat. Monitor for allergies.\n"
            "4. **Handle small challenges calmly** — tantrums, refusal to sleep, minor injuries. "
            "Model the calm the child needs.\n"
            "5. **Know when to escalate** — any real injury, any concern about behaviour, "
            "anything unusual → call a parent immediately."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Parents must be reachable by phone at all times.\n"
            "- Kitchen and bathroom are the main injury risks — supervise closely near both.\n"
            "- Never leave a younger child alone in a bath, even briefly.\n"
            "- Have the paediatrician's number and 112 written where you can see them."
        ),
        "parent_note_md": (
            "Caring for a younger sibling alone is a significant responsibility — "
            "start with short periods (1-2 hours) and build up. It develops responsibility, "
            "empathy, practical parenting skills, and genuine contribution to the family. "
            "Only when both your teenager and younger child are ready."
        ),
    },
    # ── Age 16-18 (1 task) ──────────────────────────────────────────────
    {
        "slug": "moving-out-setup-age16",
        "title": "Plan the Practical Basics of Moving Out",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The essentials checklist** — bedding, towels, basic cookware, cutlery, "
            "plates, cups, cleaning supplies, first aid kit, toilet paper. "
            "Without these, a new flat is unliveable.\n"
            "2. **Utilities to set up** — electricity, gas, water, internet, phone. "
            "Who provides each in the new location? Budget for deposits and setup fees.\n"
            "3. **Groceries for the first week** — you won't have time or energy to shop daily. "
            "Stock staples: rice, oil, salt, pasta, some vegetables, eggs.\n"
            "4. **Documents to bring** — ID, proof of address, rental agreement copy, "
            "medical records, important contacts.\n"
            "5. **The first-30-days plan** — register with a local GP, find the nearest shop, "
            "meet the neighbours, check emergency exits. Don't just inhabit — settle."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Change any entry locks or codes if you're moving into a property where others "
            "may have had keys.\n"
            "- Test smoke alarms, know where the gas shut-off and electrical box are.\n"
            "- Share the new address and emergency contacts with parents before moving."
        ),
        "parent_note_md": (
            "The practical logistics of moving out — not just the emotional milestone — "
            "are enormous. A teenager who has walked through the essentials, utilities, "
            "groceries, documents, and first-month plan before the actual move handles "
            "it with far less stress. This builds on *manage-home-solo* and every "
            "household skill before it."
        ),
    },
]

# ---------------------------------------------------------------------------
# Phase 4 — Prerequisite edges: (to_slug, from_slug, mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    # Missing chains in existing ladder
    ("clear-table",                     "carry-plate-sink-age5",     True),
    ("wash-dishes",                     "clear-table",               True),
    ("set-table-age6",                  "pour-drink-age6",           True),
    ("pack-lunchbox",                   "pack-school-bag-age6",      True),
    ("sweep-small-area",                "tidy-toys-age6",            True),
    ("wipe-kitchen-counters",           "wipe-spill-age5",           True),
    ("boil-water",                      "pour-drink-age6",           True),
    ("make-cold-sandwich",              "wash-dishes",               True),
    ("load-dishwasher",                 "wash-dishes",               True),
    ("pack-travel-bag",                 "pack-school-bag-age6",      True),
    ("sew-on-button",                   "fold-tshirt",               True),
    ("do-own-laundry-age14",            "operate-washing-machine",   True),
    ("do-own-laundry-age14",            "fold-tshirt",               True),
    ("cook-full-meal-age14",            "cook-full-meal",            True),
    ("manage-own-schedule-age14",       "pack-school-bag-age6",      True),
    ("deep-clean-space-age15",          "sweep-small-area",          True),
    ("deep-clean-space-age15",          "wipe-kitchen-counters",     True),
    ("plan-week-meals-budget-age15",    "cook-full-meal-age14",      True),
    ("host-a-meal-age16",               "cook-full-meal-age14",      True),
    ("manage-home-solo-age16",          "cook-full-meal-age14",      True),
    ("manage-home-solo-age16",          "do-own-laundry-age14",      True),
    ("medical-appointment-solo-age15",  "manage-own-schedule-age14", True),

    # New task chains
    ("shower-self-age7",                "wash-hands-age5",           True),
    ("help-prep-veg-age7",              "wash-hands-age5",           True),
    ("hang-laundry-age7",               "sort-laundry-by-color",     True),
    ("safe-knife-use-age9",             "help-prep-veg-age7",        True),
    ("read-simple-recipe-age9",         "help-prep-veg-age7",        True),
    ("make-breakfast-age9",             "read-simple-recipe-age9",   True),
    ("make-breakfast-age9",             "safe-knife-use-age9",       True),
    ("help-grocery-age10",              "pay-at-shop-age6",          False),
    ("clean-bathroom-age11",            "wipe-kitchen-counters",     True),
    ("change-bed-sheet-age11",          "make-bed-age6",             True),
    ("understand-food-storage-age11",   "read-simple-recipe-age9",   True),
    ("home-first-aid-age12",            "wash-hands-age5",           True),
    ("plan-meals-few-days-age13",       "read-simple-recipe-age9",   True),
    ("basic-grooming-age13",            "shower-self-age7",          True),
    ("manage-own-health-routine-age13", "home-first-aid-age12",      True),
    ("manage-leftovers-age14",          "understand-food-storage-age11", True),
    ("care-for-sibling-age15",          "home-first-aid-age12",      True),
    ("moving-out-setup-age16",          "manage-home-solo-age16",    True),
    ("moving-out-setup-age16",          "handle-home-emergency-age16", True),
]


class Command(BaseCommand):
    help = "Refine the Household task ladder: dedupe, retune ages, add new tasks, wire DAG."

    def handle(self, *args, **options):
        household_tag = Tag.objects.filter(
            category=Tag.Category.HOUSEHOLD
        ).first()
        if not household_tag:
            household_tag, _ = Tag.objects.get_or_create(
                name="Home care",
                defaults={"category": Tag.Category.HOUSEHOLD},
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
            task.tags.set([household_tag])
            task.environments.set(all_envs)
            added += 1
        self.stdout.write(f"Phase 3: upserted {added} new household tasks.")

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

        self.stdout.write(self.style.SUCCESS("refine_household_ladder complete."))
