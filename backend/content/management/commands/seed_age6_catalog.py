"""Management command: seed age-6 tasks across all six categories.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_age6_catalog

Idempotent — safe to re-run. Uses update_or_create throughout.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Tasks grouped by category
# ---------------------------------------------------------------------------

FINANCIAL_TASKS = [
    {
        "slug": "identify-coins-age6",
        "title": "Know Each Coin by Name and Value",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Lay out all coins** — spread every denomination on a table. "
            "Point to each one and name it together: *This is a one-rupee coin.*\n"
            "2. **Sort by value** — ask your child to arrange them from smallest to largest value. "
            "Correct gently and explain.\n"
            "3. **The grab game** — say a coin name, they pick it up from the pile as fast as they can. "
            "Repeat until instant recognition.\n"
            "4. **Match to prices** — show a price tag (₹2, ₹5) and ask them to find the exact coin.\n"
            "5. **Pocket quiz** — carry a few coins during the day and quiz them informally "
            "while waiting or walking."
        ),
        "parent_note_md": (
            "Coin recognition is the absolute first step in financial literacy. A child who "
            "cannot name coins will be anxious at any transaction involving cash. Spend one "
            "week on recognition alone before moving to counting."
        ),
        "prereqs": [],
    },
    {
        "slug": "count-small-money-age6",
        "title": "Count a Small Amount of Money",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with same coins** — place four ₹2 coins: *Each is ₹2. Count with me: 2, 4, 6, 8.*\n"
            "2. **Mix two denominations** — combine ₹1 and ₹2 coins. Sort largest first, "
            "then count up.\n"
            "3. **The shop game** — price three household items at under ₹20. "
            "Child counts out the correct coins.\n"
            "4. **Count and check** — give them a small purse with a few coins. "
            "Ask: *How much is in there?*\n"
            "5. **Real purchase** — let them count out and hand over money at a local shop. "
            "Stay nearby but let them do it."
        ),
        "parent_note_md": (
            "Counting real coins — not just numbers on paper — builds the mental arithmetic "
            "children need for every cash transaction. The hands-on action of sorting and "
            "counting locks in the skill far better than worksheets."
        ),
        "prereqs": ["identify-coins-age6"],
    },
    {
        "slug": "piggy-bank-habit-age6",
        "title": "Put Money in a Piggy Bank Every Week",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up a piggy bank** — let them choose it. Having ownership matters.\n"
            "2. **Agree a weekly amount** — even ₹5 is enough. The habit, not the amount, is the goal.\n"
            "3. **Same day every week** — link it to an existing routine (Sunday evening, "
            "pocket-money day).\n"
            "4. **Count the total together** — once a month, empty and count. "
            "Celebrate the growing total.\n"
            "5. **Name a goal** — what are they saving for? A sticker book, a toy? "
            "Draw or print a picture and stick it on the bank."
        ),
        "parent_note_md": (
            "The habit of saving before spending is one of the most powerful financial behaviours "
            "an adult can have — and it is easiest to form before age 8. The goal here is not "
            "the amount saved but the weekly ritual of choosing to save."
        ),
        "prereqs": [],
    },
    {
        "slug": "needs-vs-wants-age6",
        "title": "Tell the Difference Between a Need and a Want",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define the words** — a need is something you must have to be safe and healthy "
            "(food, clothes, shelter). A want is something nice to have.\n"
            "2. **Sorting game** — write 10 items on slips of paper (chocolate, shoes, school bag, "
            "new toy, medicine). Sort into Need / Want piles together.\n"
            "3. **Discuss grey areas** — are shoes a need or a want? It depends. Explore why.\n"
            "4. **At the shop** — when they ask for something, ask: *Is that a need or a want?* "
            "Don't use it to say no — use it to think together.\n"
            "5. **Weekly check** — look at your grocery receipt. Together identify 3 needs and 3 wants."
        ),
        "parent_note_md": (
            "This is the foundational concept behind every spending decision. Children who "
            "understand it early are less susceptible to advertising and impulse buying as "
            "teenagers. Keep discussions non-judgemental — wants are fine, they just require "
            "saving up."
        ),
        "prereqs": [],
    },
    {
        "slug": "pay-at-shop-age6",
        "title": "Hand Over Money and Wait for Change",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Roleplay at home first** — set up a pretend shop. Child buys an item, "
            "hands over coins, receives change.\n"
            "2. **Choose the coins** — before entering a real shop, help them select the right "
            "amount. Slightly more is fine — change will come back.\n"
            "3. **At the counter** — child hands over the money themselves. Coach them: "
            "*Hold it in your palm, pass it over, say thank you.*\n"
            "4. **Count the change** — when change is received, count it together. "
            "Does it match what was expected?\n"
            "5. **Repeat three times** — with different items and amounts until the sequence "
            "feels natural."
        ),
        "parent_note_md": (
            "Making a real cash transaction, even a small one, is a rite of independence. "
            "Children who do this early are confident in shops and do not panic when "
            "handling money. The act of counting change introduces subtraction in a real context."
        ),
        "prereqs": ["count-small-money-age6"],
    },
]

HOUSEHOLD_TASKS = [
    {
        "slug": "tidy-toys-age6",
        "title": "Put Toys Away After Playing",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the system** — every toy has a home (box, shelf, basket). "
            "Walk through where each thing goes.\n"
            "2. **10-minute tidy** — set a timer. The goal is to tidy before it rings. "
            "Make it feel like a game.\n"
            "3. **One-out, one-away rule** — before getting a new toy out, put the current one away.\n"
            "4. **End-of-day check** — before bedtime, check the play area together. "
            "Any toy still out gets tidied.\n"
            "5. **Praise the habit** — comment specifically: *You put the blocks away without "
            "being asked — that is really responsible.*"
        ),
        "parent_note_md": (
            "Tidying up is a foundation of self-regulation and respect for shared spaces. "
            "Children who tidy consistently feel more in control of their environment and "
            "are easier to manage as they grow. Avoid doing it for them — work alongside them instead."
        ),
        "prereqs": [],
    },
    {
        "slug": "make-bed-age6",
        "title": "Make Your Bed Every Morning",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Demonstrate once** — show the full sequence: straighten sheet, pull up duvet, "
            "place pillow. Keep expectations age-appropriate — neat enough, not hotel-perfect.\n"
            "2. **Do it together** — take one side each for a week until they are comfortable.\n"
            "3. **Link to a cue** — after they get dressed, they make the bed. Same sequence, same time.\n"
            "4. **Morning inspection** — make it a habit to glance together before school. "
            "Give a thumbs up or one small tip.\n"
            "5. **Let them own it** — once the habit is set, stop commenting unless they forget. "
            "The bed is their responsibility."
        ),
        "parent_note_md": (
            "Admiral William McRaven famously said: *If you make your bed every morning, you "
            "will have accomplished the first task of the day.* The habit builds discipline, "
            "starts the day with a win, and signals to a child that they are responsible for "
            "their own space."
        ),
        "prereqs": [],
    },
    {
        "slug": "set-table-age6",
        "title": "Lay the Dinner Table",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the layout** — plate in centre, fork on left, knife and spoon on right, "
            "glass above the knife. Keep it simple for age 6.\n"
            "2. **Count places** — ask: *How many people are eating tonight?* They count the "
            "chairs and set that many places.\n"
            "3. **Let them carry items safely** — teach two-handed carrying for plates. "
            "Glasses last, held by the base.\n"
            "4. **Make it a role** — *You are in charge of setting the table tonight.* "
            "Ownership improves follow-through.\n"
            "5. **Build up** — add napkins or condiments once the basics are consistent."
        ),
        "parent_note_md": (
            "Table setting is a gateway to family mealtime participation. It builds counting, "
            "spatial awareness, and a sense of contribution to the household. Children who "
            "help prepare meals sit better, eat better, and feel more invested in family life."
        ),
        "prereqs": [],
    },
    {
        "slug": "pour-drink-age6",
        "title": "Pour Your Own Drink Without Spilling",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a small jug first** — pour water from a child-sized jug into a cup "
            "at the sink. Spills wash away easily here.\n"
            "2. **Teach the grip** — two hands on a heavier container. Tilt slowly.\n"
            "3. **The fill line** — show them how full is enough. *Stop at halfway for now.*\n"
            "4. **Move to the table** — once they are confident at the sink, pour at the table. "
            "Have a cloth nearby.\n"
            "5. **Everyday practice** — let them pour their own water or juice at meals. "
            "Resist the urge to step in unless there is a safety risk."
        ),
        "parent_note_md": (
            "Pouring without spilling requires fine motor control, spatial judgement, and "
            "self-regulation. Children who can do it independently no longer need to ask a "
            "parent every time they are thirsty — a small but meaningful step toward "
            "day-to-day independence."
        ),
        "prereqs": [],
    },
    {
        "slug": "pack-school-bag-age6",
        "title": "Pack Your School Bag the Night Before",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Make a list together** — write or draw the items that go in every day: "
            "books, water bottle, lunch box, homework. Laminate it and stick it on the bag.\n"
            "2. **Establish the time** — after dinner or before bath, they check the list "
            "and pack the bag. Same time every night.\n"
            "3. **Parent spot-check** — for the first two weeks, check together after they have "
            "packed. Don't pack it for them — point out what's missing.\n"
            "4. **Add day-specific items** — Tuesday is PE kit day. Add this to the list.\n"
            "5. **Morning benefit** — remind them that a packed bag the night before means "
            "no rushing in the morning. Link the habit to a benefit they can feel."
        ),
        "parent_note_md": (
            "Preparing ahead is a habit that reduces morning chaos for the whole family "
            "and builds executive function in children. Children who pack their own bags "
            "develop a sense of ownership over their school life and are less dependent on "
            "parents to organise them."
        ),
        "prereqs": [],
    },
]

DIGITAL_TASKS = [
    {
        "slug": "turn-on-off-device-age6",
        "title": "Turn a Device On and Off Correctly",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the buttons** — point to the power button and explain what it does. "
            "Different devices may differ — cover the one they use.\n"
            "2. **Proper shutdown** — show that *turning off* means waiting for it to fully "
            "power down, not just putting it face-down.\n"
            "3. **Safe placement** — where does the device go when not in use? "
            "On its charger? In the drawer? Establish the rule.\n"
            "4. **Practise three times** — turn on, use briefly, turn off properly. Repeat.\n"
            "5. **Handle with care** — two hands when carrying. No food or drink nearby."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never leave a charging device under a pillow or blanket — fire risk.\n"
            "- Charge devices in a common area, not the child's bedroom.\n"
            "- If a device feels hot, put it down on a hard surface and tell an adult."
        ),
        "parent_note_md": (
            "Learning to handle a device respectfully from the start prevents future habits "
            "like leaving screens on all night, draining batteries, or dropping devices "
            "carelessly. This is the device equivalent of teaching a child to close a book."
        ),
        "prereqs": [],
    },
    {
        "slug": "private-info-rule-age6",
        "title": "Never Share Your Name or Address Online",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain why** — on the internet, we cannot see who we are talking to. "
            "Some people pretend to be children when they are not.\n"
            "2. **The private information list** — together, name things that are private: "
            "full name, address, school name, phone number, photo.\n"
            "3. **Ask before sharing** — the rule: if someone online asks for any of these, "
            "close the app and tell a parent immediately.\n"
            "4. **Roleplay** — you pretend to be someone in a game asking for their name. "
            "They practise saying *I'm not allowed to say* and closing the conversation.\n"
            "5. **Repeat regularly** — revisit this conversation every few months. "
            "As children grow, the risks change."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- No real names in online usernames or avatars.\n"
            "- If any stranger online asks personal questions, come to a parent immediately.\n"
            "- There is no such thing as a safe online stranger until a parent has verified them."
        ),
        "parent_note_md": (
            "Children start using games and apps with online components from age 5–6. "
            "The private-information rule is the single most important digital safety lesson "
            "and must be established before they are exposed to any online interaction. "
            "Keep the tone calm and matter-of-fact, not frightening."
        ),
        "prereqs": [],
    },
    {
        "slug": "ask-before-screen-age6",
        "title": "Always Ask Before Using a Screen",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **State the rule clearly** — no screen (TV, tablet, phone, game console) without "
            "asking a parent first. No exceptions.\n"
            "2. **Practise the ask** — *Can I watch something please?* Practise the phrasing. "
            "It should be calm and polite, not a demand.\n"
            "3. **Roleplay the no** — practise what to do when the answer is no: "
            "accept it, move to another activity, no arguing.\n"
            "4. **Track the week** — put a sticker on the fridge each time they ask correctly. "
            "Five stickers earns a bonus 15-minute screen session.\n"
            "5. **Explain why** — screens affect sleep, attention, and mood. "
            "Share this in simple language: *Your brain needs breaks from screens to grow.*"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- No screens in the bedroom after lights-out.\n"
            "- Minimum 1 hour gap between screen time and bedtime for children aged 6–8.\n"
            "- If they find something online that worries or confuses them, "
            "they can always show a parent without getting in trouble."
        ),
        "parent_note_md": (
            "The ask-first rule keeps parents informed about what children are watching "
            "and builds the habit of checking in before consuming content. It also "
            "prevents the default of screens as a way to fill every idle minute — "
            "one of the most important habits to shape before age 8."
        ),
        "prereqs": [],
    },
    {
        "slug": "video-call-family-age6",
        "title": "Make a Video Call to a Family Member",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose the person** — grandparent, cousin, or family friend they know well. "
            "Pre-arrange the call so the other person is expecting it.\n"
            "2. **Show how to dial** — open the app, find the contact, tap call. "
            "Let them do it with you watching.\n"
            "3. **What to say** — practise a simple opening: *Hi [name], it's me. How are you?* "
            "Roleplay at home first.\n"
            "4. **During the call** — encourage them to ask one question and listen to the answer "
            "before talking about themselves.\n"
            "5. **Ending the call** — they say goodbye themselves. "
            "*It was great talking to you. Bye!*"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Only call contacts that a parent has added and approved.\n"
            "- If someone unexpected appears on the call, hang up and tell a parent.\n"
            "- Do not show the home's rooms or street during a video call to anyone outside family."
        ),
        "parent_note_md": (
            "Video calls with known family members build communication skills, confidence "
            "on camera, and connections across distances. This is a safe introduction to "
            "digital communication before children encounter unknown contacts in games and "
            "messaging apps."
        ),
        "prereqs": ["turn-on-off-device-age6"],
    },
    {
        "slug": "screen-time-stop-age6",
        "title": "Stop Using a Screen When Asked, Without Arguing",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Give a 5-minute warning** — *Screen time ends in 5 minutes.* "
            "This reduces the shock of stopping mid-activity.\n"
            "2. **At time-up** — say clearly: *Screen off now please.* The expectation is "
            "immediate compliance, not a negotiation.\n"
            "3. **Practise the response** — the correct response is *OK* and putting it down. "
            "Roleplay this: they hold a device, you say stop, they put it down and say OK.\n"
            "4. **What if they argue?** — calmly add 10 minutes to tomorrow's screen ban "
            "each time they argue. State this in advance so it is not a surprise.\n"
            "5. **Celebrate compliance** — when they stop without arguing, name it: "
            "*Thank you for stopping straight away — that shows great self-control.*"
        ),
        "parent_note_md": (
            "The inability to stop using screens when asked is one of the most common "
            "friction points in families with young children. Building this habit at 6–7 "
            "prevents far larger battles at 10–12. Consistency is everything — the rule "
            "must apply every time or children learn that arguing works."
        ),
        "prereqs": ["ask-before-screen-age6"],
    },
]

NAVIGATION_TASKS = [
    {
        "slug": "know-home-address-age6",
        "title": "Memorise Your Home Address",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Break it into parts** — house number, street name, area/locality, city. "
            "Learn one part at a time over a week.\n"
            "2. **Say it out loud daily** — add it to the morning routine: "
            "*What is our address? 12, Sunflower Lane, Andheri, Mumbai.*\n"
            "3. **Write and draw it** — have them write or draw the address. "
            "Seeing it in their own handwriting helps memory.\n"
            "4. **Random quiz** — ask at unexpected moments: at breakfast, in the car, "
            "before bed. Keep it light.\n"
            "5. **Emergency use** — explain exactly when they would need to say it: "
            "if lost, if with a police officer, if with a stranger helping them."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Memorising your address is an emergency skill — explain it calmly as a "
            "safety tool, not something frightening.\n"
            "- Practise saying it clearly and confidently to an adult."
        ),
        "parent_note_md": (
            "Knowing their home address can save a child's life. It is also one of the "
            "first pieces of independence — a child who knows where they live is no longer "
            "entirely helpless if separated from a parent. Make it a game, not a drill."
        ),
        "prereqs": [],
    },
    {
        "slug": "trusted-adults-age6",
        "title": "Name Three Trusted Adults Who Can Help You",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define a trusted adult** — someone you know, who is an adult, and who your "
            "parents have said is safe: a teacher, a relative, a family friend.\n"
            "2. **Make a list together** — name at least three. Include someone at school, "
            "someone in the family, and one other.\n"
            "3. **Role-play asking for help** — *I'm lost. I'm going to find my teacher.* "
            "Practise walking up and saying: *Excuse me, I need help. I can't find my mum.*\n"
            "4. **Review regularly** — the list changes as the child grows or moves schools. "
            "Update it every term.\n"
            "5. **Safe adults in public** — if none of the three are around: "
            "a shop worker in a uniform, a police officer, or a mum with children."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- A trusted adult is someone YOUR PARENTS have approved, not someone who says "
            "they are safe.\n"
            "- Never go anywhere with an unknown adult even if they say your parents sent them."
        ),
        "parent_note_md": (
            "Children are significantly safer when they have a clear mental list of who to "
            "turn to in an emergency. Most children, when frightened, freeze. Having rehearsed "
            "this in advance bypasses the freeze response. The list should be revisited "
            "annually — people change."
        ),
        "prereqs": [],
    },
    {
        "slug": "traffic-light-age6",
        "title": "Understand Traffic Lights and Zebra Crossings",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the lights** — red = stop, amber = get ready, green = go. "
            "Point them out on a real journey.\n"
            "2. **At a zebra crossing** — stop at the kerb, look right, look left, look right again. "
            "Wait until all cars have stopped before stepping off.\n"
            "3. **Never assume** — green man doesn't mean every driver has stopped. "
            "Teach them to make eye contact with drivers or wait for cars to fully stop.\n"
            "4. **No phone/screen near roads** — heads up, always. Practise being alert "
            "before reaching the kerb.\n"
            "5. **Practise every crossing** — for a month, narrate the steps at every crossing "
            "together: *Stop. Look. Safe. Go.*"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Always hold a parent's hand near roads until the child can reliably demonstrate "
            "the stop-look-go sequence independently.\n"
            "- Never let a child step off a kerb ahead of you until they have passed this task.\n"
            "- Parked cars block sight lines — always stop behind them, not between them."
        ),
        "parent_note_md": (
            "Road traffic injuries are one of the leading causes of child death globally. "
            "This knowledge must be actively taught and practised, not assumed. The habit "
            "of stopping, looking, and checking — rather than just following the light — "
            "is the difference between safety and risk."
        ),
        "prereqs": [],
    },
    {
        "slug": "stay-if-lost-age6",
        "title": "Know What To Do If You Get Lost",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The rule: stop, stay, shout** — if lost, stop walking, stay where you are, "
            "and shout the parent's name loudly.\n"
            "2. **Don't walk further** — explain that moving makes it harder to be found. "
            "The spot where they last were is where parents will look first.\n"
            "3. **Find a safe adult** — if no parent comes, find a trusted adult "
            "(shop worker, police officer, mum with children) and say: "
            "*I'm lost. Can you help me find my mum/dad?*\n"
            "4. **Roleplay in a safe space** — at a park or shopping centre, practise: "
            "you walk away a short distance, they stop, stay, and wait.\n"
            "5. **Practise the address** — they should be able to say their home address "
            "clearly to any adult helping them."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never go with an unknown adult to *find your parents* — stay where you are.\n"
            "- Shout the parent's name, not *help* — this helps the specific person find them faster.\n"
            "- A safe adult in a shop or public place will not take the child away from the spot."
        ),
        "parent_note_md": (
            "The natural instinct when a child is lost is to walk around looking — which "
            "makes them harder to find. Stop, stay, shout reverses this. Practise it in "
            "a low-stakes scenario (large shop, park) so the muscle memory is there in a "
            "real situation. Keep the practice calm and game-like."
        ),
        "prereqs": ["trusted-adults-age6", "know-home-address-age6"],
    },
    {
        "slug": "walk-safely-age6",
        "title": "Walk Safely on a Pavement",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Stay on the pavement** — never walk on the road, even if the pavement is "
            "narrow. Walk in single file if the path is tight.\n"
            "2. **Walk on the inside** — the adult walks on the road side, child on the "
            "building side. Explain why.\n"
            "3. **At driveways** — pause before crossing a driveway. A car may reverse without "
            "warning. Look first.\n"
            "4. **No darting** — practise walking at a steady pace. Running ahead is only "
            "allowed when directed by the adult.\n"
            "5. **Eyes forward** — no looking at phones or devices while walking near roads."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Always hold hands near busy roads or when crossing.\n"
            "- Bright or reflective clothing in low light helps drivers see you.\n"
            "- If there is no pavement, walk facing oncoming traffic on the far right."
        ),
        "parent_note_md": (
            "Many road injuries to young children happen on pavements near driveways. "
            "Teaching pavement discipline — walking on the inside, pausing at driveways, "
            "no running ahead — reduces risk significantly. Practise on every walk until it "
            "becomes automatic."
        ),
        "prereqs": ["traffic-light-age6"],
    },
]

COGNITIVE_TASKS = [
    {
        "slug": "morning-routine-age6",
        "title": "Follow a Morning Routine Without Being Reminded",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Build the routine together** — ask: *What needs to happen every morning?* "
            "List it: wake up, toilet, wash face, brush teeth, get dressed, eat, pack bag.\n"
            "2. **Make a visual chart** — draw or print pictures for each step. "
            "Stick it on their bedroom door or bathroom mirror.\n"
            "3. **First week: do it together** — walk through each step alongside them, "
            "ticking off the chart.\n"
            "4. **Second week: they do it, you watch** — resist reminding. Let them check "
            "the chart themselves. Praise any self-correction.\n"
            "5. **Track the streak** — a tick on a calendar for each morning completed "
            "without reminders. Five ticks earns a reward they choose."
        ),
        "parent_note_md": (
            "Executive function — the ability to plan, sequence, and initiate tasks — is "
            "one of the strongest predictors of academic and life success. A morning routine "
            "is the simplest daily exercise for this skill. Parents who nag instead of "
            "letting the chart do the work accidentally delay its development."
        ),
        "prereqs": [],
    },
    {
        "slug": "take-turns-game-age6",
        "title": "Take Turns in a Game Without Cheating",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a simple game** — Snakes and Ladders, Ludo, or a card game. "
            "Explain the turn sequence before starting.\n"
            "2. **Name the rule** — *We take turns. That means waiting while the other "
            "person plays. No rushing, no skipping.*\n"
            "3. **Practise waiting** — make waiting part of the game. *While I take my turn, "
            "what can you think about for your next turn?*\n"
            "4. **Handle losing** — losing is part of the game. Practise saying "
            "*Well played* and meaning it. Roleplay it before the game.\n"
            "5. **No cheating discussion** — ask: *Why is cheating unfair?* "
            "Let them explain it. Understanding the reason is more powerful than a rule."
        ),
        "parent_note_md": (
            "Turn-taking is the foundation of cooperation, patience, and fair play. "
            "Children who can take turns without distress handle classroom group work, "
            "shared toys, and social play far better. Board games are the best low-stakes "
            "arena to build this — play them as often as you can."
        ),
        "prereqs": [],
    },
    {
        "slug": "tidy-before-leaving-age6",
        "title": "Tidy Up After Yourself Before Leaving a Room",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **State the rule** — before leaving any room, check if anything you used "
            "needs to go back. Plate to sink, book to shelf, shoes to rack.\n"
            "2. **The leaving scan** — teach a quick visual sweep before stepping out: "
            "*Do I see anything of mine? Pick it up.*\n"
            "3. **Model it yourself** — narrate as you do it: "
            "*I'm taking my mug to the kitchen before I leave the room.*\n"
            "4. **Gentle catch** — if they leave without tidying, call them back calmly: "
            "*Something of yours is still here.* Let them figure out what.\n"
            "5. **Praise the habit** — not the specific act: "
            "*You remembered to tidy before leaving — that is really considerate.*"
        ),
        "parent_note_md": (
            "This habit — leaving a space as you found it — underlies all shared living "
            "skills: being a good housemate, a good colleague, a good guest. It is the "
            "physical expression of awareness of others. Children who learn it early "
            "are noticeably easier to live and work with."
        ),
        "prereqs": ["tidy-toys-age6"],
    },
    {
        "slug": "tell-time-hour-age6",
        "title": "Read the Time to the Nearest Hour",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with an analogue clock** — the hour hand only. "
            "Cover the minute hand with tape. *This big hand points to the 3 — it is 3 o'clock.*\n"
            "2. **Walk through every hour** — move the hour hand around and name each hour together.\n"
            "3. **Daily quiz** — ask *What time is it?* at meals, before school, at bedtime. "
            "Always to the nearest hour.\n"
            "4. **Link time to events** — *School starts at 8 o'clock. Lunch is at 1 o'clock. "
            "Bedtime is at 8 o'clock.* Time becomes meaningful through routines.\n"
            "5. **Add the minute hand** — once hours are solid, introduce *half past* and "
            "*quarter past*. Do not rush this."
        ),
        "parent_note_md": (
            "An analogue clock is a spatial and mathematical tool. Children who can read one "
            "develop stronger number sense and time awareness than those who only read digital "
            "displays. Time-awareness is also essential for self-management: knowing when "
            "something starts or ends is the first step in planning around it."
        ),
        "prereqs": [],
    },
    {
        "slug": "sort-recycle-age6",
        "title": "Sort Rubbish Into the Right Bin",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the bins** — which bins or bags do you have at home? "
            "Wet waste, dry waste, recyclable. Show them each one.\n"
            "2. **Sorting game** — gather 10 household items (banana peel, plastic bottle, "
            "newspaper, food wrapper). Sort them together and explain each choice.\n"
            "3. **One rule at a time** — start with just two categories: "
            "*Wet waste (food) goes here. Everything else goes there.* Add categories as they master each.\n"
            "4. **Make them responsible** — at mealtimes, they clear their own plate "
            "and sort the waste.\n"
            "5. **Explain why** — show a short video or picture of recycling. "
            "Children who understand the reason sort more carefully than those following a rule."
        ),
        "parent_note_md": (
            "Environmental habits formed before age 8 tend to last a lifetime. Sorting waste "
            "correctly also builds categorisation skills — the same cognitive ability used in "
            "maths and science. Start with two categories and keep it simple; complexity "
            "can grow as the habit solidifies."
        ),
        "prereqs": [],
    },
]

SOCIAL_TASKS = [
    {
        "slug": "say-please-thankyou-age6",
        "title": "Always Use Please and Thank You",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the words** — *please* when asking for something, "
            "*thank you* when receiving. Explain that these show respect.\n"
            "2. **Model it constantly** — say please and thank you to your child. "
            "Children copy what they see.\n"
            "3. **Pause and wait** — if they ask for something without please, "
            "pause and look at them. Often they self-correct. If not, gently prompt.\n"
            "4. **Catch it in the wild** — notice when they use it spontaneously "
            "and name it: *You remembered your please — well done.*\n"
            "5. **Extend to others** — encourage use with grandparents, teachers, "
            "shopkeepers. The habit must work outside the home to be real."
        ),
        "parent_note_md": (
            "Please and thank you are the foundation of every social interaction. Children "
            "who use them consistently are perceived as confident, polite, and well-raised by "
            "every adult they meet. The habit forms fastest when parents use these words with "
            "their children too — it is not a one-way lesson."
        ),
        "prereqs": [],
    },
    {
        "slug": "greet-adults-age6",
        "title": "Say Hello and Goodbye to Adults",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show what it looks like** — when a familiar adult arrives, demonstrate: "
            "look up, smile, say *Hello [name]* or *Good morning*.\n"
            "2. **Practise at home** — roleplay with a parent as a visiting adult. "
            "Child greets, you respond. Swap and do it again.\n"
            "3. **Real test: relatives** — at the next family visit, prompt them before the "
            "adult arrives: *Remember to say hello when Grandma comes in.*\n"
            "4. **The goodbye** — leaving without saying goodbye is rude. "
            "Teach *Goodbye [name], see you soon* or equivalent.\n"
            "5. **No hiding behind parents** — if they cling, stay nearby but encourage "
            "the greeting rather than speaking for them."
        ),
        "parent_note_md": (
            "Greeting adults confidently is a life-long social asset. Children who greet "
            "well are remembered warmly by teachers, relatives, and eventually employers. "
            "The habit also reduces social anxiety — doing the greeting every time means "
            "it stops being scary."
        ),
        "prereqs": ["say-please-thankyou-age6"],
    },
    {
        "slug": "share-with-others-age6",
        "title": "Share a Toy or Item with Another Child",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain sharing** — sharing means letting someone else use your thing "
            "for a while. You still get it back.\n"
            "2. **Practise with a timer** — *Your turn for 5 minutes, then their turn.* "
            "Use a visible timer so the wait feels bounded.\n"
            "3. **Roleplay the hard moment** — someone wants the toy you are holding. "
            "Practise handing it over willingly and saying *Your turn.*\n"
            "4. **Handle reluctance** — if they find it very hard, start with items that "
            "are less precious. Build up to favourite toys.\n"
            "5. **Recognise the feeling** — *It feels hard to share sometimes. "
            "That is normal. The kind thing is to do it anyway.*"
        ),
        "parent_note_md": (
            "Sharing is one of the earliest cooperative skills and one of the most "
            "contested. Children who share willingly make friends more easily and are "
            "more welcome in group play. Do not force sharing every time — let children "
            "own their things — but model and practise it consistently."
        ),
        "prereqs": [],
    },
    {
        "slug": "express-feelings-words-age6",
        "title": "Say How You Feel Instead of Acting Out",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the feelings** — happy, sad, angry, scared, frustrated, lonely, proud. "
            "Use pictures or an emotion chart if helpful.\n"
            "2. **Link feeling to behaviour** — *When you threw the toy, you were feeling…?* "
            "Help them identify the feeling underneath the action.\n"
            "3. **The feeling sentence** — *I feel [word] because [reason].* "
            "Practise at calm moments: *I feel excited because we're going to the park.*\n"
            "4. **Catch it in the moment** — when they start to act out, ask: "
            "*What are you feeling right now? Can you tell me in words?*\n"
            "5. **Accept the feeling** — validate it before addressing the behaviour: "
            "*It makes sense you are angry. And we still can't throw things.*"
        ),
        "parent_note_md": (
            "Emotional vocabulary is one of the most powerful protective factors in child "
            "development. Children who can name their feelings regulate their behaviour "
            "better, have fewer tantrums past age 7, and build stronger relationships. "
            "This is not about suppressing emotions — it is about expressing them safely."
        ),
        "prereqs": [],
    },
    {
        "slug": "ask-teacher-help-age6",
        "title": "Ask Your Teacher for Help When Stuck",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Discuss the barrier** — why don't children ask? Fear of seeming slow, "
            "not wanting to bother the teacher. Reframe: teachers want to be asked.\n"
            "2. **Teach the phrase** — *Excuse me, I don't understand [specific thing]. "
            "Can you help me?* Practise saying it clearly.\n"
            "3. **Roleplay at home** — you are the teacher, they are stuck on a task. "
            "They must approach you and ask clearly.\n"
            "4. **Specific over vague** — *I don't get it* is not enough. "
            "Practise naming the exact thing: *I don't understand question 3.*\n"
            "5. **Report back** — ask in the evening: *Did you ask for help at school today? "
            "What happened?* Celebrate when they do."
        ),
        "parent_note_md": (
            "Children who ask for help get unstuck faster and perform better academically. "
            "Many children sit confused for an entire lesson rather than raise their hand. "
            "Normalising help-seeking at 6–7 prevents years of silent struggle. "
            "Make sure your reaction when they do ask is always positive — never make them "
            "feel it was a burden."
        ),
        "prereqs": ["greet-adults-age6"],
    },
]

# ---------------------------------------------------------------------------
# Prerequisite edges: (to_slug, from_slug, is_mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    ("count-small-money-age6",   "identify-coins-age6",     True),
    ("pay-at-shop-age6",         "count-small-money-age6",  True),
    ("video-call-family-age6",   "turn-on-off-device-age6", True),
    ("screen-time-stop-age6",    "ask-before-screen-age6",  True),
    ("stay-if-lost-age6",        "trusted-adults-age6",     True),
    ("stay-if-lost-age6",        "know-home-address-age6",  True),
    ("walk-safely-age6",         "traffic-light-age6",      True),
    ("tidy-before-leaving-age6", "tidy-toys-age6",          True),
    ("greet-adults-age6",        "say-please-thankyou-age6", True),
    ("ask-teacher-help-age6",    "greet-adults-age6",       True),
]

# ---------------------------------------------------------------------------
# Tag name → (display_name, category) for each category
# ---------------------------------------------------------------------------

CATEGORY_TAGS = [
    ("Money basics",     Tag.Category.FINANCIAL),
    ("Home care",        Tag.Category.HOUSEHOLD),
    ("Digital literacy", Tag.Category.DIGITAL),
    ("Wayfinding",       Tag.Category.NAVIGATION),
    ("Reasoning",        Tag.Category.COGNITIVE),
    ("Social skills",    Tag.Category.SOCIAL),
]

ALL_AGE6_TASKS = [
    (FINANCIAL_TASKS, "Money basics"),
    (HOUSEHOLD_TASKS, "Home care"),
    (DIGITAL_TASKS,   "Digital literacy"),
    (NAVIGATION_TASKS, "Wayfinding"),
    (COGNITIVE_TASKS,  "Reasoning"),
    (SOCIAL_TASKS,     "Social skills"),
]


class Command(BaseCommand):
    help = "Seed age-6 tasks across all six categories (idempotent)."

    def handle(self, *args, **options):
        # Ensure all tags exist
        tags = {}
        for display_name, category in CATEGORY_TAGS:
            tag, _ = Tag.objects.get_or_create(
                name=display_name,
                defaults={"category": category},
            )
            tags[display_name] = tag

        # Fetch all environments
        all_envs = list(Environment.objects.all())

        total_upserted = 0
        for task_list, tag_name in ALL_AGE6_TASKS:
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

        self.stdout.write(f"Upserted {total_upserted} age-6 tasks.")

        # Wire prerequisite edges
        all_slugs = [t["slug"] for task_list, _ in ALL_AGE6_TASKS for t in task_list]
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
        self.stdout.write(self.style.SUCCESS("seed_age6_catalog complete."))
