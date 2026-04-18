"""Management command: refine the Navigation task ladder.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py refine_navigation_ladder

Four phases, all idempotent:
  1. Delete 2 duplicates + remove 1 illogical prereq edge
  2. Retune 18 age ranges into proper developmental stages
  3. Add 19 new tasks filling gaps at every tier
  4. Wire ~35 prerequisite edges connecting the ladder
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Phase 1a — Duplicates to delete
# ---------------------------------------------------------------------------

DELETE_SLUGS = [
    "know-parent-phone-memorized",   # subset of know-full-name-address-phone
    "identify-home-school-shop",     # covered by know-where-home-is-age5 + identify-landmarks-near-home
]

# ---------------------------------------------------------------------------
# Phase 1b — Illogical prereq edges to delete
# ---------------------------------------------------------------------------

DELETE_EDGES = [
    # (to_slug, from_slug) — overnight trip does not logically require a job app
    ("overnight-trip-solo-age16", "full-job-application-age16"),
]

# ---------------------------------------------------------------------------
# Phase 2 — Age range updates
# ---------------------------------------------------------------------------

AGE_RANGE_UPDATES = [
    ("look-both-ways",                 7,  8),
    ("cross-crosswalk-with-parent",    7,  9),
    ("stranger-safety-basics",         7, 10),
    ("walk-to-mailbox-and-back",       7, 10),
    ("identify-landmarks-near-home",   7, 10),
    ("dial-emergency-number",          7, 10),
    ("use-pedestrian-signal",          8, 10),
    ("follow-simple-sketch-map",       8, 10),
    ("read-street-transit-signs",      9, 11),
    ("navigate-public-library",        9, 11),
    ("ride-bike-with-helmet",          9, 12),
    ("take-bus-with-parent",           9, 11),
    ("buy-transit-ticket",            10, 12),
    ("use-phone-maps-app",            10, 12),
    ("walk-to-friend-house-solo",     10, 12),
    ("cross-busy-intersection-solo",  11, 13),
    ("plan-route-with-stops",         11, 13),
    ("ride-transit-independently",    11, 13),
]

# ---------------------------------------------------------------------------
# Phase 3 — New tasks (19 total)
# ---------------------------------------------------------------------------

NEW_TASKS = [
    # ── Age 5-6 (2 tasks) ───────────────────────────────────────────────
    {
        "slug": "recognise-safety-symbols-age5",
        "title": "Recognise Common Safety Symbols",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Introduce core symbols** — STOP sign (red octagon), EXIT sign (green), "
            "fire extinguisher, no-entry, toilets, disabled access. Show pictures of each.\n"
            "2. **Name them together** — *What does this one mean? Why is it important?*\n"
            "3. **Spot them in the wild** — on walks, in shops, at the mall. "
            "*Quick, find a STOP sign! Find an EXIT!*\n"
            "4. **Action with the symbol** — STOP means stop. EXIT means way out in emergency. "
            "Don't just recognise — know what to do.\n"
            "5. **Build the library** — add more symbols over time: pedestrian crossing, "
            "school zone, hospital sign, fire alarm."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- In any building, make it a habit to look for the EXIT sign.\n"
            "- A STOP sign applies to you as a pedestrian too — never walk past one without "
            "checking the road."
        ),
        "parent_note_md": (
            "Safety symbols are the universal visual language that keeps children safe "
            "in public spaces. A child who recognises them can navigate independently "
            "and act correctly in an emergency. Start with 4-5 symbols and build up."
        ),
    },
    {
        "slug": "what-counts-as-emergency-age6",
        "title": "Know What Counts as an Emergency",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define emergency** — something serious where someone could get hurt or die "
            "if no one helps quickly. Fire, someone collapsing, someone drowning, a bad accident.\n"
            "2. **What's NOT an emergency** — scraping a knee, sibling taking your toy, "
            "being hungry. These are problems, not emergencies.\n"
            "3. **Sort scenarios** — go through 8 scenarios together. Emergency or not? Why?\n"
            "4. **What to do in an emergency** — stay calm, tell an adult immediately, "
            "call for help (112 in India).\n"
            "5. **What to do in a non-emergency** — handle it yourself or ask for help calmly."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- India national emergency number: 112 (covers police, fire, ambulance).\n"
            "- Never call an emergency number as a joke — it can prevent real help reaching "
            "someone who needs it."
        ),
        "parent_note_md": (
            "Children confuse *serious* with *emergency* — and vice versa. Teaching the "
            "distinction at 6 means they don't panic over small things and DO act quickly "
            "on real emergencies. This conversation prepares them for the dial-emergency "
            "task that follows."
        ),
    },
    # ── Age 7-8 (3 tasks) ───────────────────────────────────────────────
    {
        "slug": "signal-for-help-age7",
        "title": "Signal for Help Without Speaking",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **When it's useful** — across a busy road, from a window, in a shop where "
            "they can't speak loudly, or if they are with someone who is pressuring them.\n"
            "2. **Wave with urgency** — both arms up, waving. Very different from a casual wave.\n"
            "3. **Eye contact + distressed face** — a known trusted adult will often notice "
            "something is wrong just from the look.\n"
            "4. **The help signal** — internationally, palm out with thumb folded in and "
            "fingers closed over the thumb. Used by people in distress.\n"
            "5. **Practise in safe settings** — make it a game at home. Parent is *the helper*; "
            "child signals from across a room."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If someone is near them who might stop them calling for help (a bad stranger, "
            "a coercive adult), silent signals can be lifesaving.\n"
            "- The Universal Help Signal (closed fist with thumb tucked under fingers) is "
            "recognised globally — worth teaching specifically."
        ),
        "parent_note_md": (
            "Children in dangerous situations often can't speak, either because of shock "
            "or because speaking would escalate the danger. A child who knows how to signal "
            "silently has a crucial extra safety tool. Teach it without alarming them."
        ),
    },
    {
        "slug": "stranger-approaches-age7",
        "title": "Know What to Do If a Stranger Approaches or Follows You",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The rule: don't engage** — if an unknown adult approaches offering sweets, "
            "a ride, help, or wanting to find a lost puppy, the answer is *no thank you* and "
            "walk away quickly.\n"
            "2. **Go towards people, not away** — if they feel unsafe, move towards a group "
            "of people or a shop, not down an empty street.\n"
            "3. **The loud no** — if a stranger tries to grab or pressure them, "
            "shout loudly: *NO! I don't know you! HELP!*\n"
            "4. **Tell a parent afterwards** — even if nothing happened. Parents need to know.\n"
            "5. **Roleplay scenarios** — you pretend to be a friendly stranger offering "
            "sweets. They practise saying no and walking away."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- *Stranger danger* nuance: most strangers are safe people. The risk is "
            "strangers who approach, offer, or ask — not strangers walking past.\n"
            "- Adults who need real help do not ask children. If an adult asks for help, "
            "it is a red flag.\n"
            "- Never, ever get into a vehicle with someone you don't know, no matter what "
            "they say (including *your parents sent me*)."
        ),
        "parent_note_md": (
            "Teaching stranger response without creating phobia is delicate. The goal is "
            "a child who is comfortable around normal strangers but knows exactly what to "
            "do if someone approaches with intent. Practise the response so it's automatic, "
            "not frightened."
        ),
    },
    {
        "slug": "navigate-inside-building-age7",
        "title": "Find Your Way Inside a Familiar Building",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Map the school** — in their school or a regular venue (community hall, mall), "
            "can they get from the entrance to the toilet? To the canteen? To the main office?\n"
            "2. **Use signs** — look for directional signs. *Toilets →* , *Exit ↓*.\n"
            "3. **Ask for directions** — when they don't know, they walk up to a staff member "
            "or security guard and ask clearly: *Excuse me, where is the…*\n"
            "4. **The home base** — agree on a meeting spot if separated (main entrance, "
            "a specific counter). They always know where to return to.\n"
            "5. **Practise solo** — in a safe building, send them on a small errand "
            "(fetch something from a specific spot). Watch from a distance."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Always ask building staff (uniformed), not random adults.\n"
            "- If they get lost, stand still at a distinctive spot and wait — "
            "don't wander further.\n"
            "- Know where the nearest exit is in any building."
        ),
        "parent_note_md": (
            "Children who can navigate inside familiar buildings — school, mall, library — "
            "are ready to be slightly separated from parents briefly and to manage small "
            "errands. This prepares them for the solo outdoor navigation tasks that follow."
        ),
    },
    # ── Age 9-10 (3 tasks) ──────────────────────────────────────────────
    {
        "slug": "cardinal-directions-age9",
        "title": "Use North, South, East, and West",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find north at home** — use a phone compass app. Which direction is North "
            "from your front door? Mark it mentally.\n"
            "2. **The sun rule** — the sun rises in the east and sets in the west. "
            "At morning or evening, you always know east/west from the sun.\n"
            "3. **Landmark directions** — *The park is north of our house. School is to the east.* "
            "Build a mental map of the area with directions.\n"
            "4. **Use directions to give instructions** — *Go north for two blocks, then east.* "
            "Much clearer than *go there, then turn.*\n"
            "5. **On a map** — every map has north at the top by convention. "
            "Practise reading maps with this in mind."
        ),
        "parent_note_md": (
            "Cardinal directions are the foundation of spatial reasoning. Children who "
            "internalise north/south/east/west navigate maps, understand geography, "
            "and give precise directions — skills that transfer everywhere from hiking "
            "to Uber locations. The sun rule is the most memorable anchor."
        ),
    },
    {
        "slug": "road-signs-basics-age9",
        "title": "Understand Common Road Signs",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The three shapes** — triangles (warning), circles (orders), "
            "rectangles (information). A quick way to read any sign.\n"
            "2. **The core pedestrian signs** — pedestrian crossing, school zone, "
            "no-entry, one-way, stop, give-way.\n"
            "3. **Sign hunt on walks** — on the way home or to school, name every sign you pass. "
            "How many can they spot and name?\n"
            "4. **What they mean for pedestrians** — a school zone means slow traffic but "
            "also kids crossing. One-way streets mean look the other way too.\n"
            "5. **What they mean for drivers** — learning from the driver's view helps "
            "them understand road behaviour around them."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Even at a pedestrian crossing, cars may not stop. Always verify before stepping off.\n"
            "- One-way streets are particularly dangerous for pedestrians — a car can come "
            "from a direction you didn't check."
        ),
        "parent_note_md": (
            "Road sign literacy protects pedestrians, future cyclists, and future drivers. "
            "Children who can read signs understand road environments, anticipate driver "
            "behaviour, and make safer decisions about when and where to cross."
        ),
    },
    {
        "slug": "elevator-safety-age10",
        "title": "Use a Lift/Elevator Safely",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Call buttons** — up arrow for going up, down arrow for going down. "
            "Press only the one you need.\n"
            "2. **Wait behind the door** — stand back until the door fully opens. "
            "Let people out before going in.\n"
            "3. **Inside the lift** — press the floor button once. Hold the door open button "
            "if someone is rushing in. Step towards the back to let others in.\n"
            "4. **If it gets stuck** — stay calm. Press the alarm or emergency button. "
            "Never try to force the door open. Don't climb out.\n"
            "5. **Fire rule** — in a fire, never use the lift. Always use stairs. "
            "Lifts can get stuck or fill with smoke."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If a lift stops between floors, DON'T panic. Press emergency button, "
            "wait for help, breathe slowly.\n"
            "- Never ride a lift alone with an adult you don't know — wait for the next one.\n"
            "- In a fire or earthquake, use stairs only."
        ),
        "parent_note_md": (
            "Lift use is a daily urban skill and carries real safety considerations. "
            "A child who knows lift etiquette and emergency protocol is both well-mannered "
            "and safer. The never-alone-with-a-stranger rule is particularly important."
        ),
    },
    # ── Age 11-12 (3 tasks) ─────────────────────────────────────────────
    {
        "slug": "walk-home-from-school-age11",
        "title": "Walk Home from School Safely on Your Own",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Agree the route** — the exact path, agreed with parents. "
            "No shortcuts unless pre-approved.\n"
            "2. **Walk it together first** — do the route with them 3-4 times. "
            "Point out safe crossings, the one or two tricky spots.\n"
            "3. **Phone protocol** — no earbuds near roads. Phone in bag, not hand. "
            "Text *home safe* on arrival.\n"
            "4. **The unexpected** — what if it starts raining? If someone they know offers "
            "a lift? If the usual way is blocked? Plan for each.\n"
            "5. **Progressive independence** — first time you follow at a distance. "
            "Next time they go fully alone. Build up over 2-3 weeks."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Stay on the agreed route. No deviations without calling first.\n"
            "- Walk with another kid if possible — safer and more fun.\n"
            "- If followed, go into a shop, restaurant, or towards a group. Call a parent."
        ),
        "parent_note_md": (
            "Walking home from school solo is a major step. It requires route awareness, "
            "time management, stranger-safety, and self-reliance. Parents who practise "
            "the route, agree the protocols, and then let go steadily raise more confident "
            "children. Indians tend to delay this; there is real developmental value in "
            "doing it at 11-12 where local context allows."
        ),
    },
    {
        "slug": "handle-transit-disruption-age11",
        "title": "Handle a Missed Stop or Wrong Train",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Missed stop** — don't panic. Get off at the next stop. "
            "Check the maps app for the best way back.\n"
            "2. **Wrong train/bus** — similarly get off at the next stop. "
            "Check which route does go to your destination.\n"
            "3. **Ask someone** — a uniformed staff member, the driver, another passenger. "
            "*Excuse me, does this go to [destination]?*\n"
            "4. **Call a parent early** — not at the last minute when panicked. "
            "Early call means more options.\n"
            "5. **Emergency fund** — always carry a bit more money than the planned journey, "
            "for unexpected detours."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If you end up somewhere unfamiliar, stay in well-lit populated areas. "
            "Don't start walking randomly.\n"
            "- Have your parent's number memorised, not just saved.\n"
            "- Phone charge matters. Keep it charged before every solo journey."
        ),
        "parent_note_md": (
            "Transit disruptions will happen. A teenager who can handle them calmly — "
            "without panic, without catastrophising — becomes a genuinely independent "
            "traveller. The skills learned here transfer to flights, foreign travel, "
            "and work commuting for decades."
        ),
    },
    {
        "slug": "navigate-transport-hub-age12",
        "title": "Navigate a Railway or Bus Station",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read the display boards** — departure and arrival times, platform numbers, "
            "delays. Understand the format before you need it.\n"
            "2. **Find the platform** — signs, overhead displays, staff for directions. "
            "Walk there with time to spare — never at the last minute.\n"
            "3. **Ticket and ID** — always with you, not in checked luggage. "
            "Ready to show when asked.\n"
            "4. **Public facilities** — toilets, drinking water, waiting area, food stalls. "
            "Know where they are in case of a delay.\n"
            "5. **Station safety** — stay behind the yellow line. Never run across platforms. "
            "Watch your belongings — stations are pickpocket territory."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Bags at your feet or in your lap, never on the ground next to you.\n"
            "- Never accept food or drink from strangers on a train — spiking happens.\n"
            "- If a suspicious package is left unattended, tell security immediately."
        ),
        "parent_note_md": (
            "Indian railway and bus stations are complex, crowded, and require specific "
            "navigation skills. A teenager who has practised reading boards, finding "
            "platforms, and managing belongings is ready for longer travel — and safer "
            "as a solo traveller."
        ),
    },
    # ── Age 13-14 (3 tasks) ─────────────────────────────────────────────
    {
        "slug": "use-rideshare-safely-age13",
        "title": "Use a Rideshare or Auto-Rickshaw Safely",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use the app, not the street** — Uber, Ola, Rapido. Known driver, tracked route, "
            "fare agreed in advance, rating visible.\n"
            "2. **Verify before getting in** — number plate matches the app. "
            "Driver's name matches. Their photo matches.\n"
            "3. **Share live location** — every rideshare app has this feature. "
            "Share with a parent for the whole journey.\n"
            "4. **Back seat rule** — as a young person, always in the back seat, never next to "
            "the driver. Door-handle side.\n"
            "5. **If something feels wrong** — stop the ride at a safe busy location. "
            "Get out. Report via the app."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- For auto-rickshaws flagged on the street: confirm the fare before getting in, "
            "insist on the meter, tell a parent the plate number before the ride.\n"
            "- If a rideshare driver deviates from the app route, ask why immediately. "
            "If the answer is unsatisfactory, get out at the next safe stop.\n"
            "- Women and young teens: consider female-driver options (some apps offer this) "
            "for longer or late-night rides."
        ),
        "parent_note_md": (
            "Rideshare and auto-rickshaw use is an everyday Indian reality. Teenagers who "
            "use them safely — tracked, app-based, verified — are substantially less at "
            "risk than those who flag random vehicles. Establishing the protocol at 13 "
            "builds life-long safer travel habits."
        ),
    },
    {
        "slug": "find-local-services-age13",
        "title": "Find the Nearest Hospital, Police Station, or Help",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know your local services** — draw a mental or actual map. Where is the "
            "nearest hospital? Police station? Fire station? Pharmacy (24-hour)?\n"
            "2. **Use maps tools** — search *hospital near me* or *pharmacy 24x7*. "
            "Know how to filter by what's open now.\n"
            "3. **Google the local emergency** — every locality has specific emergency numbers "
            "(local police, local ambulance). Save them.\n"
            "4. **Landmark method** — if they're in an unfamiliar area and something goes wrong, "
            "find a major landmark (metro station, temple, large mall) as a meeting point.\n"
            "5. **Practise unfamiliar areas** — when visiting a new part of the city or "
            "another city, first thing: identify the nearest services. Habit, not drill."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- India emergency: 112 (general), 100 (police), 108/102 (ambulance), "
            "101 (fire), 1091 (women), 1098 (children).\n"
            "- In a major city, hospitals in private networks (Apollo, Fortis, Max) are "
            "often easier to find and access than public hospitals.\n"
            "- A police station's general diary (GD) can file an emergency contact even "
            "if it's not a serious crime — useful if someone is missing."
        ),
        "parent_note_md": (
            "Knowing where to get help when something goes wrong is the difference between "
            "crisis and managed problem. Teenagers who automatically orient themselves in "
            "any new location — *where are the nearest services?* — are safer and more "
            "resilient. This is practical preparation for adult life, college in a new "
            "city, or working abroad."
        ),
    },
    {
        "slug": "navigate-new-city-age14",
        "title": "Navigate a City You've Never Been To Before",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plan before arrival** — where are you going? What transport? "
            "Download the offline map of the city.\n"
            "2. **Get oriented on arrival** — at the station or airport, find the map. "
            "Identify where you are, which direction your destination is.\n"
            "3. **Choose transport** — metro, bus, app-based cab, prepaid taxi. "
            "Research before choosing — prepaid taxis from airports avoid tourist surcharges.\n"
            "4. **Know the safe neighbourhoods** — before wandering, ask a hotel staff or "
            "local: *Is this area safe to walk in the evening?*\n"
            "5. **The fall-back** — if genuinely lost, find a metro station or major hotel. "
            "They're usually safe hubs with staff who can help."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Save your hotel address in the local language (Hindi, Tamil, whatever).\n"
            "- Download the city's metro map offline.\n"
            "- Carry two forms of ID. Hide one.\n"
            "- Inform a parent of your itinerary before arriving."
        ),
        "parent_note_md": (
            "Navigating a new city independently is a major growth milestone. Teenagers "
            "who do this well — with preparation, orientation, and safe fallbacks — are "
            "ready for college in new cities and eventually for international travel. "
            "Start with a visit to a friend or relative in another city, where there's a "
            "local anchor."
        ),
    },
    # ── Age 14-16 (1 task) ──────────────────────────────────────────────
    {
        "slug": "online-travel-booking-age14",
        "title": "Book a Train, Bus, or Hotel Online",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with a real booking** — a family trip where you do the research and "
            "present options. Train: IRCTC or RedBus. Hotel: MakeMyTrip, Booking.com, or direct.\n"
            "2. **Compare multiple sites** — same journey on different platforms. "
            "Which is cheaper? Which has better timing? Note the differences.\n"
            "3. **Read the fine print** — cancellation policy, refund timelines, tax inclusions, "
            "convenience fees. These often determine the true cheapest option.\n"
            "4. **Check reviews** — for hotels in particular, recent reviews matter more than "
            "star ratings. Look at photos from guests, not just the hotel.\n"
            "5. **Confirm and record** — PNR numbers, booking references, check-in details. "
            "Email or screenshot. Accessible without network if possible."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Only book on trusted, known sites. Scam travel sites exist.\n"
            "- Use a credit card (with fraud protection), not a debit card, for travel bookings.\n"
            "- Never share OTP or card CVV with anyone claiming to be *helping* with a booking."
        ),
        "parent_note_md": (
            "Online travel booking is a universal adult skill. Teenagers who have done a "
            "real booking — researched, compared, read the fine print, completed the "
            "transaction — are far more confident arranging their own travel in college "
            "and as young adults."
        ),
    },
    # ── Age 15-17 (1 task) ──────────────────────────────────────────────
    {
        "slug": "if-stopped-by-police-age15",
        "title": "Know What to Do If Stopped by Police",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Stay calm and polite** — no arguing, no sudden movements, no running. "
            "Even if it feels unjust, the spot to argue is not there.\n"
            "2. **Ask why they are stopping you** — politely, once. *Sir/Madam, can I ask "
            "what this is about?* You have the right to know.\n"
            "3. **Show ID if asked** — carry some form of ID when out. "
            "If it's at home, calmly say so.\n"
            "4. **Minor rights** — as someone under 18, you can ask for a parent or "
            "guardian to be contacted. For anything beyond a brief stop, this is important.\n"
            "5. **Remember and report** — after any police interaction, write down the date, "
            "time, location, officer name/number. Tell a parent. If rights were violated, "
            "this is the record needed to act later."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never try to flee. Even innocent flight creates legal trouble.\n"
            "- Don't consent to searches unnecessarily, but don't physically resist if "
            "they proceed — object verbally.\n"
            "- If something feels very wrong (unmarked vehicle, plainclothes only, no ID "
            "shown), it may not be real police — insist on going to a police station, "
            "not with them.\n"
            "- Free legal aid: call the National Legal Services Authority (NALSA) helpline "
            "at 15100."
        ),
        "parent_note_md": (
            "Teenagers — especially those who look older than their age — are increasingly "
            "likely to be stopped in traffic checks, at festivals, or during periodic "
            "police drives. Knowing how to handle this calmly protects them from "
            "escalation and gives you (the parent) the information you need to raise "
            "genuine concerns afterwards."
        ),
    },
    # ── Age 16-18 (3 tasks) ─────────────────────────────────────────────
    {
        "slug": "get-learner-licence-age16",
        "title": "Get a Learner's Licence for a Scooter or Car",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know what's legal** — in India, 16 minimum for 50cc gearless scooter "
            "(learner's licence), 18 for motorcycles and cars. Check your state's current rules.\n"
            "2. **Study the basics** — traffic signs, rules of the road, vehicle safety. "
            "Free online test practice on parivahan.gov.in.\n"
            "3. **Complete the application** — online via parivahan.gov.in or at the local RTO. "
            "Documents: age proof, address proof, passport photos, medical certificate if required.\n"
            "4. **Take the theory test** — at the RTO, on a computer. Multiple choice. "
            "Pass rate is high if you've prepared. If you fail, you can retake.\n"
            "5. **Practise with a licensed adult** — learner's licence allows driving with "
            "a supervising adult. Practise in empty parking lots before roads."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never ride without a helmet, even for a two-minute trip. "
            "Head injuries are the #1 motor vehicle death cause for young riders.\n"
            "- Never ride under the influence of anything, prescription or otherwise.\n"
            "- Three people on a scooter, or any vehicle beyond legal capacity, "
            "is illegal AND dangerous."
        ),
        "parent_note_md": (
            "Getting a learner's licence is a practical rite of passage. Teenagers who go "
            "through the process themselves — not have parents handle it — gain the "
            "document-navigation skills they'll use for passports, insurance, and every "
            "other government-related adult task."
        ),
    },
    {
        "slug": "navigate-college-admission-age16",
        "title": "Navigate the College Admission Process",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Map your options** — research 5-10 colleges/universities that match their "
            "interests and eligibility. Different courses have very different entry paths.\n"
            "2. **Understand the entrance exams** — JEE, NEET, CUET, CLAT, state-level, "
            "university-specific. Know which ones apply to the courses they want.\n"
            "3. **Track deadlines religiously** — a calendar with every exam, application, "
            "and document submission deadline. Missing a deadline can cost a year.\n"
            "4. **Prepare documents in advance** — passport photo, ID, marks certificates, "
            "caste certificate if applicable. Scan and keep multiple digital copies.\n"
            "5. **The backup plan** — always have a realistic second and third choice. "
            "Dream schools are a bet; realistic schools are the safety net."
        ),
        "parent_note_md": (
            "The Indian college admissions process is notoriously complex, with multiple "
            "exams, councils, and timelines. Teenagers who take ownership of the process "
            "— tracking deadlines, preparing documents, researching options — make better "
            "choices and arrive at college more invested in being there. Parents who do "
            "it all for them create dependent students."
        ),
    },
    {
        "slug": "travel-abroad-basics-age16",
        "title": "Understand the Basics of Travelling Abroad",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Passport process** — how to apply (passport seva portal), documents needed, "
            "timeline (usually 2-4 weeks normal, faster for tatkal). Know your passport "
            "expiry — many countries require 6+ months validity.\n"
            "2. **Visa types** — tourist, student, work, transit. Not every country needs a visa "
            "(Indian passport has visa-free access to ~60 countries). Know the rules for where "
            "they plan to go.\n"
            "3. **International airport basics** — check-in, security, immigration, boarding. "
            "Arrive 3 hours before international flights. Keep passport accessible.\n"
            "4. **Currency and cards** — forex card, international debit card, or cash? "
            "Which is best for which country? Notify the bank before travel.\n"
            "5. **The safety basics** — register with the Indian embassy if staying long-term, "
            "know the local emergency number, keep a photocopy of passport separately, "
            "travel insurance is not optional."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never hand over your passport to anyone except official immigration.\n"
            "- Keep digital AND paper copies of important documents, stored separately.\n"
            "- Register your travel with MADAD (madad.gov.in) — the Indian government's "
            "consular service platform.\n"
            "- Travel insurance covering medical evacuation is essential, not optional."
        ),
        "parent_note_md": (
            "International travel — for higher studies, exchanges, work, or tourism — is "
            "increasingly part of young Indian adults' lives. A teenager who understands "
            "passport, visa, airport, and currency basics handles their first international "
            "trip with confidence. The alternative is panic at every new checkpoint."
        ),
    },
]

# ---------------------------------------------------------------------------
# Phase 4 — Prerequisite edges: (to_slug, from_slug, mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    # Missing chains in existing ladder
    ("know-home-address-age6",                "know-where-home-is-age5",         True),
    ("know-full-name-address-phone",          "know-home-address-age6",          True),
    ("dial-emergency-number",                 "trusted-adults-age6",             True),
    ("look-both-ways",                        "traffic-light-age6",              True),
    ("walk-to-mailbox-and-back",              "walk-safely-age6",                True),
    ("stranger-safety-basics",                "trusted-adults-age6",             True),
    ("follow-simple-sketch-map",              "know-where-home-is-age5",         True),
    ("ride-bike-with-helmet",                 "walk-safely-age6",                True),
    ("walk-to-friend-house-solo",             "walk-to-mailbox-and-back",        True),
    ("travel-independently-age14",            "ride-transit-independently",      True),
    ("plan-trip-independently-age14",         "use-phone-maps-app",              True),
    ("read-map-navigate-age14",               "use-phone-maps-app",              True),
    ("read-map-navigate-age14",               "follow-simple-sketch-map",        True),
    ("handle-emergency-alone-age14",          "dial-emergency-number",           True),
    ("basic-first-aid-age15",                 "handle-emergency-alone-age14",    True),
    ("lost-phone-wallet-plan-age15",          "handle-emergency-alone-age14",    True),
    ("overnight-trip-solo-age16",             "travel-independently-age14",      True),
    ("overnight-trip-solo-age16",             "plan-trip-independently-age14",   True),
    ("read-contract-before-signing-age15",    "read-official-document-age14",    True),
    ("understand-renting-age16",              "read-contract-before-signing-age15", True),
    ("understand-civic-participation-age16",  "know-legal-rights-age15",         True),
    ("full-job-application-age16",            "interview-for-opportunity-age15", True),

    # New task chains
    ("what-counts-as-emergency-age6",         "trusted-adults-age6",             True),
    ("signal-for-help-age7",                  "what-counts-as-emergency-age6",   True),
    ("stranger-approaches-age7",              "stay-if-lost-age6",               True),
    ("navigate-inside-building-age7",         "know-where-home-is-age5",         True),
    ("cardinal-directions-age9",              "identify-landmarks-near-home",    True),
    ("road-signs-basics-age9",                "traffic-light-age6",              True),
    ("elevator-safety-age10",                 "navigate-inside-building-age7",   True),
    ("walk-home-from-school-age11",           "walk-to-friend-house-solo",       True),
    ("handle-transit-disruption-age11",       "ride-transit-independently",      True),
    ("navigate-transport-hub-age12",          "handle-transit-disruption-age11", True),
    ("use-rideshare-safely-age13",            "navigate-transport-hub-age12",    True),
    ("find-local-services-age13",             "dial-emergency-number",           True),
    ("navigate-new-city-age14",               "read-map-navigate-age14",         True),
    ("online-travel-booking-age14",           "use-phone-maps-app",              True),
    ("if-stopped-by-police-age15",            "know-legal-rights-age15",         True),
    ("get-learner-licence-age16",             "ride-bike-with-helmet",           True),
    ("navigate-college-admission-age16",      "read-official-document-age14",    True),
    ("travel-abroad-basics-age16",            "navigate-new-city-age14",         True),
]


class Command(BaseCommand):
    help = "Refine the Navigation task ladder: dedupe, fix bad edge, retune ages, add tasks, wire DAG."

    def handle(self, *args, **options):
        nav_tag = Tag.objects.filter(
            name="Wayfinding", category=Tag.Category.NAVIGATION
        ).first()
        if not nav_tag:
            nav_tag, _ = Tag.objects.get_or_create(
                name="Wayfinding",
                defaults={"category": Tag.Category.NAVIGATION},
            )

        all_envs = list(Environment.objects.all())

        # ── Phase 1a — Delete duplicates ────────────────────────────────
        deleted = 0
        for slug in DELETE_SLUGS:
            qs = Task.objects.filter(slug=slug)
            if qs.exists():
                qs.delete()
                deleted += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"  Phase 1a: {slug} already gone, skipping")
                )
        self.stdout.write(f"Phase 1a: deleted {deleted} duplicate tasks.")

        # ── Phase 1b — Delete bad prereq edges ──────────────────────────
        edge_deleted = 0
        for to_slug, from_slug in DELETE_EDGES:
            to_task = Task.objects.filter(slug=to_slug).first()
            from_task = Task.objects.filter(slug=from_slug).first()
            if to_task and from_task:
                qs = PrerequisiteEdge.objects.filter(from_task=from_task, to_task=to_task)
                if qs.exists():
                    qs.delete()
                    edge_deleted += 1
        self.stdout.write(f"Phase 1b: deleted {edge_deleted} illogical prereq edges.")

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
            task.tags.set([nav_tag])
            task.environments.set(all_envs)
            added += 1
        self.stdout.write(f"Phase 3: upserted {added} new navigation tasks.")

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

        self.stdout.write(self.style.SUCCESS("refine_navigation_ladder complete."))
