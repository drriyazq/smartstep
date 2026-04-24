"""Management command: fill 4 content gaps identified during mastery-capability review.

Adds 25 tasks across 4 themes the catalog didn't cover well enough to support
mastery certificates:

  1. Physical fitness (7 tasks) → Active Body mastery
  2. Digital creation (6 tasks) → Young Digital Creator mastery
  3. Eco-conscious habits (6 tasks) → Eco-Conscious Kid mastery
  4. Healthcare self-management (6 tasks) → Handle Your Own Healthcare mastery

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_gap_tasks

Idempotent — upserts via update_or_create(slug=...).
"""
from django.core.management.base import BaseCommand

from content.models import Environment, ReviewStatus, Tag, Task


# ---------------------------------------------------------------------------
# Physical fitness (Active Body mastery)
# ---------------------------------------------------------------------------

FITNESS_TASKS = [
    {
        "slug": "outdoor-play-hour-age7",
        "title": "Play Outside for a Full Hour",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Agree a time and place** — a park, garden, or safe street. One hour, "
            "no screens, no interruptions.\n"
            "2. **Bring one prop, not ten** — a ball, a skipping rope, a bike. "
            "Boredom is the fuel for invention; over-packing kills it.\n"
            "3. **Go with them the first few times** — then gradually step back. "
            "Presence first, independence next.\n"
            "4. **Let the play be child-led** — no schedule, no agenda. Climbing, running, "
            "digging, inventing games — all count.\n"
            "5. **Make it the default** — every day after school, before homework. "
            "Bodies move best when the habit is built in."
        ),
        "parent_note_md": (
            "Physical play outdoors is disappearing from Indian childhoods. Children who "
            "spend a daily hour outside show sharper focus at school, sleep better, and "
            "develop the motor coordination that no indoor activity can replace."
        ),
    },
    {
        "slug": "daily-movement-habit-age8",
        "title": "Move Your Body Every Day for 30 Minutes",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick three activities they enjoy** — cycling, dancing, football, "
            "swimming, skipping. Let them choose.\n"
            "2. **Schedule a 30-minute slot** — same time each day makes it stick. "
            "Before dinner works for most families.\n"
            "3. **Track it on a visible chart** — fridge door, wall chart. Children who "
            "see streaks build streaks.\n"
            "4. **Allow variation** — one day football, another day cycling. "
            "Variety keeps the habit alive.\n"
            "5. **Count real movement** — not screen-time exercise videos passively watched. "
            "Breath should quicken, face should flush."
        ),
        "parent_note_md": (
            "The World Health Organization recommends 60 minutes of moderate activity daily "
            "for children 5–17. Building a 30-minute daily floor by age 8 creates the muscle "
            "memory of movement — essential for lifelong health and against rising childhood "
            "obesity rates."
        ),
    },
    {
        "slug": "basic-warmup-stretches-age9",
        "title": "Warm Up Properly Before Any Exercise",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the why** — cold muscles tear; warm muscles stretch. "
            "Five minutes of warmup prevents weeks of injury.\n"
            "2. **Learn three warm-up moves** — jumping jacks, arm circles, leg swings. "
            "Five of each, done before any sport.\n"
            "3. **Add three stretches** — calf stretch, hamstring stretch, shoulder stretch. "
            "Hold 15 seconds each.\n"
            "4. **Never static-stretch a cold muscle** — dynamic movement first, stretches "
            "only after warming up or after exercise.\n"
            "5. **Make it non-negotiable** — no warmup, no sport. A routine they'll keep "
            "for life."
        ),
        "parent_note_md": (
            "Warming up is one of those 'invisible' skills — no one notices when a child "
            "does it well, but everyone notices the torn muscle that follows when they don't. "
            "Instilling this habit young means it's automatic in their teenage sports years "
            "when injuries can derail months."
        ),
    },
    {
        "slug": "learn-sport-basics-age10",
        "title": "Learn the Rules and Basics of One Sport",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick one sport they're curious about** — football, cricket, badminton, "
            "basketball, table tennis. Theirs to choose.\n"
            "2. **Learn the basic rules** — how to score, how to foul, the main positions. "
            "Watch one full match together with explanations.\n"
            "3. **Practise one fundamental skill** — passing, serving, bowling, dribbling. "
            "Whatever the sport's core mechanic is.\n"
            "4. **Play at least 3 games** — with friends, siblings, or in a local club. "
            "Rules come alive only in the game.\n"
            "5. **Find a local coach or club** — even low-cost community programs teach form "
            "better than YouTube does."
        ),
        "parent_note_md": (
            "Sport teaches handling defeat, playing as a team, and following rules fairly — "
            "life lessons no classroom matches. By age 10, children can understand the rules "
            "of most sports and benefit from the social structure a club or team provides."
        ),
    },
    {
        "slug": "home-bodyweight-routine-age11",
        "title": "Complete a 15-Minute Home Workout",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn five bodyweight exercises** — squats, push-ups (knee ones are fine), "
            "lunges, plank, jumping jacks. Show correct form for each.\n"
            "2. **Do 10 reps of each, 3 rounds** — roughly 15 minutes with short rests. "
            "Form before speed; slow and correct beats fast and floppy.\n"
            "3. **Finish with stretches** — 30 seconds each: calves, quads, back. "
            "Recovery is part of the workout.\n"
            "4. **Do it twice a week minimum** — Monday and Thursday works. "
            "Consistency beats intensity at this age.\n"
            "5. **Increase reps as it gets easier** — from 10 to 12 to 15. "
            "Never skip rest days."
        ),
        "parent_note_md": (
            "Bodyweight exercise at 11+ builds real strength, bone density, and the lifelong "
            "confidence that their body is a tool they can work with. Gyms and weights come "
            "later — the discipline is what matters now."
        ),
    },
    {
        "slug": "track-fitness-progress-age12",
        "title": "Track Your Own Physical Activity for Four Weeks",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up a simple log** — notebook, phone note, or spreadsheet. Date, activity, "
            "duration, how they felt (1–10).\n"
            "2. **Set a weekly goal** — e.g. 'move for 30+ minutes, 5 days a week'. "
            "Specific and measurable.\n"
            "3. **Log every day honestly** — including the days they did nothing. "
            "Data only works if it's real.\n"
            "4. **Review weekly** — one minute, Sunday evening. Pattern spotted? "
            "Goal hit?\n"
            "5. **Adjust, don't abandon** — if 5 days felt too much, aim for 4. "
            "The system gets better, not easier."
        ),
        "parent_note_md": (
            "Tracking teaches self-measurement — the core skill behind every adult fitness, "
            "career, or financial goal. A 4-week streak proves to the child that they can "
            "own a habit, which transfers to every future pursuit."
        ),
    },
    {
        "slug": "build-exercise-habit-age13",
        "title": "Keep an Exercise Habit for 30 Days",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick the smallest viable routine** — 15 minutes, 5 days a week. "
            "Enough to matter, small enough to never skip.\n"
            "2. **Anchor it to an existing cue** — after school, before dinner, "
            "after brushing teeth. Habits need a trigger.\n"
            "3. **Mark each successful day** — calendar X, sticker chart, app streak. "
            "Visible progress is fuel.\n"
            "4. **Allow one rest day a week, guilt-free** — this is a feature, not a failure. "
            "Recovery is part of training.\n"
            "5. **On day 30, reflect** — what worked? What made you skip? "
            "What's the next 30 days?"
        ),
        "parent_note_md": (
            "Thirty days is long enough for the habit to feel automatic but short enough to "
            "stay motivating. Children who complete one 30-day streak often go on to maintain "
            "lifelong exercise — the proof of consistency is more valuable than any single "
            "workout."
        ),
    },
]


# ---------------------------------------------------------------------------
# Digital creation (Young Digital Creator mastery)
# ---------------------------------------------------------------------------

CREATOR_TASKS = [
    {
        "slug": "take-good-photo-age8",
        "title": "Take a Well-Composed Photo",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the rule of thirds** — imagine the frame split into 3x3 grid. "
            "Put the subject where lines cross, not dead centre.\n"
            "2. **Find the light** — face the subject toward a window or the sun. "
            "Never shoot into bright light behind them.\n"
            "3. **Get close** — one step closer than feels natural. Most beginner photos are "
            "too far away.\n"
            "4. **Hold steady** — elbows tucked in, breath held, press gently. "
            "Shaky = blurry.\n"
            "5. **Take three versions** — same scene, different angles. "
            "Pick the best one, delete the others."
        ),
        "parent_note_md": (
            "Photography teaches seeing — noticing light, composition, and moment. "
            "A child with a camera in hand looks at the world differently. "
            "Start on any phone; no fancy gear needed."
        ),
    },
    {
        "slug": "record-clear-video-age9",
        "title": "Record a Clear Short Video",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Hold horizontally** — landscape, not portrait. "
            "Videos look better wide; stories can be cropped vertical later.\n"
            "2. **Keep it short** — 30 seconds max for their first videos. "
            "Short is always better than long.\n"
            "3. **Good audio matters more than good video** — record in a quiet room, "
            "speak close to the mic, avoid wind and echo.\n"
            "4. **One idea per video** — a demo, a how-to, a review. "
            "Not a rambling everything-about-everything.\n"
            "5. **Watch it back before sharing** — ask: does it make sense? "
            "Is there anything embarrassing? Private info on screen?"
        ),
        "parent_note_md": (
            "Video is the literacy of their generation. Teaching them to record "
            "purposefully — with audio, framing, and an idea — is as important as teaching "
            "them to write. The skill carries into presentations, interviews, and creative work."
        ),
    },
    {
        "slug": "edit-photo-basics-age10",
        "title": "Edit a Photo: Crop, Brighten, Adjust",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a free built-in editor** — Google Photos, Apple Photos, or any free app. "
            "No need for expensive software.\n"
            "2. **Crop first** — remove anything not adding to the subject. "
            "A tight crop often saves a mediocre shot.\n"
            "3. **Adjust brightness and contrast** — most phone photos are a touch dark. "
            "A small bump lifts them noticeably.\n"
            "4. **Use filters sparingly** — one subtle filter, not a heavy one. "
            "Know when to stop.\n"
            "5. **Compare before/after** — the 'undo' button teaches better than any tutorial. "
            "See the difference each change made."
        ),
        "parent_note_md": (
            "Editing teaches judgement — what to keep, what to cut, when it's finished. "
            "The same instinct applies to writing, planning, and decision-making. A child "
            "who edits their photos well is training a transferable skill."
        ),
    },
    {
        "slug": "make-slideshow-age10",
        "title": "Make a Simple Slideshow Presentation",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a topic they care about** — their pet, a trip, a hobby. "
            "Personal topics are easier to explain.\n"
            "2. **Plan 5–7 slides before opening the tool** — one idea per slide on paper. "
            "Structure before software.\n"
            "3. **One big idea per slide** — headline, one image, one sentence. "
            "Not walls of text.\n"
            "4. **Use Google Slides or Keynote** — free tools are perfectly fine. "
            "Presentation quality isn't the point; clarity is.\n"
            "5. **Present it aloud** — to family, in class, or to camera. "
            "Speaking to slides is its own skill."
        ),
        "parent_note_md": (
            "Slide-making is the foundational skill of communicating ideas — used in "
            "every school project, pitch, and career presentation. Children who practise "
            "structuring their thoughts into slides at 10 speak with more clarity at 15."
        ),
    },
    {
        "slug": "edit-video-basics-age11",
        "title": "Edit a Short Video (Trim, Titles, Transitions)",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a free editor** — CapCut, iMovie, or phone built-in editor. "
            "All powerful enough for anything at this stage.\n"
            "2. **Trim the boring bits first** — the silence at the start, the tail-off at the end, "
            "any um-ahs in between. Half of good editing is cutting.\n"
            "3. **Add a title card** — 2 seconds, big text, plain background. "
            "Tells the viewer what they're about to see.\n"
            "4. **Use one transition, not five** — a simple cut is usually best. "
            "Flashy transitions age badly.\n"
            "5. **Add background music if appropriate** — at low volume, not over speech. "
            "Use copyright-free sources only (e.g. YouTube Audio Library)."
        ),
        "parent_note_md": (
            "Video editing teaches pacing, storytelling, and self-critique. A 60-second edited "
            "video is harder than it looks — children learn to cut their own work, a skill they'll "
            "use in essays, emails, and life decisions."
        ),
    },
    {
        "slug": "publish-first-creation-age12",
        "title": "Publish or Share Your First Digital Creation",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Decide who the audience is** — family WhatsApp, a small class group, "
            "a private YouTube link. Never public-by-default for a first publish.\n"
            "2. **Check privacy before sharing** — no address, school uniform, full names, "
            "or identifiable locations visible.\n"
            "3. **Get one genuine reaction** — ask a trusted viewer: what worked? "
            "what was confusing? Actionable, specific feedback.\n"
            "4. **Improve version 2 based on feedback** — not every comment, but the "
            "repeat-offender ones. 'Too long' is worth listening to.\n"
            "5. **Celebrate the ship, not the likes** — the act of finishing and sharing is "
            "the achievement. Engagement is noise."
        ),
        "parent_note_md": (
            "Most people never ship. Getting a child comfortable with publishing their "
            "own work — even a one-minute video to a WhatsApp family group — breaks the "
            "perfectionism that stops adults from ever sharing their ideas. "
            "This habit, built young, pays dividends for life."
        ),
    },
]


# ---------------------------------------------------------------------------
# Eco-conscious habits (Eco-Conscious Kid mastery)
# ---------------------------------------------------------------------------

ECO_TASKS = [
    {
        "slug": "turn-off-lights-age6",
        "title": "Turn Off Lights When Leaving a Room",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the switch at child height** — if they can't reach, the habit can't form. "
            "Use a stool or stool-up the switch.\n"
            "2. **Name the rule** — last person out turns off the light. "
            "Applies in their room, bathroom, playroom.\n"
            "3. **Point it out for two weeks** — 'did you turn off the fan?' each time. "
            "After two weeks, step back.\n"
            "4. **Link it to cost and planet** — 'every light we leave on is a rupee wasted "
            "and a bit more carbon into the air.' Concrete stakes.\n"
            "5. **Praise the spot-check** — catch them doing it unprompted. Those moments "
            "cement the habit."
        ),
        "parent_note_md": (
            "Micro-habits like switching off lights compound over a lifetime — both for the "
            "planet and for teaching accountability. Children who own small wastefulness "
            "as a problem grow up with a cleaner sense of agency over their footprint."
        ),
    },
    {
        "slug": "save-water-tap-age7",
        "title": "Turn Off the Tap to Save Water",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **While brushing teeth** — tap on to wet the brush, off while brushing, "
            "on to rinse. Not a running tap for two minutes.\n"
            "2. **While soaping hands** — off during the 20-second soap-scrub, back on to rinse. "
            "Easy win.\n"
            "3. **Half-fill the bucket, not full** — for buckets and mugs, learn to judge "
            "'enough'.\n"
            "4. **Report leaks** — teach them to spot a dripping tap or leaking flush, "
            "and tell you. Small leaks waste thousands of litres a year.\n"
            "5. **Know why water matters** — much of India faces water shortage every summer. "
            "Their choices ripple outward."
        ),
        "parent_note_md": (
            "Water literacy matters more every year as urban India's supply tightens. "
            "A child who automatically shuts the tap while brushing saves ~15 litres a day — "
            "and more importantly, builds the instinct that resources aren't infinite."
        ),
    },
    {
        "slug": "reuse-before-throw-age8",
        "title": "Find a Reuse Before Throwing Away",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pause at the bin** — before throwing anything away, ask: "
            "is there a second use here?\n"
            "2. **Keep a reuse box** — glass jars become storage, boxes become craft material, "
            "scrap paper becomes shopping lists.\n"
            "3. **One-time vs many-time packaging** — single-use plastic is the worst; "
            "reusable is best. Train the eye to spot the difference.\n"
            "4. **Repurpose one thing a week** — a shoebox becomes a drawer divider, "
            "an old t-shirt becomes a dusting cloth.\n"
            "5. **Donate instead of discard** — outgrown clothes, old toys, unused stationery. "
            "One person's bin is another's treasure."
        ),
        "parent_note_md": (
            "The 'reuse instinct' is most easily built at 8–10, when children are creatively "
            "curious and less brand-conscious. Children who grow up with the reuse-first habit "
            "become adults who naturally avoid waste — saving money and the planet."
        ),
    },
    {
        "slug": "carry-reusable-age9",
        "title": "Carry a Reusable Water Bottle and Bag",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick their own bottle and bag** — ownership drives the habit. "
            "Let them choose colour, size, brand.\n"
            "2. **Refill, don't buy** — no bottled water purchases except in "
            "genuine emergencies. Refill at home, school, public fountains.\n"
            "3. **Cloth bag in the school bag permanently** — any trip may need one. "
            "Pocket-sized foldable ones are cheap.\n"
            "4. **Track one month of plastic avoided** — roughly a plastic bottle a day, "
            "30 bottles a month. A real count.\n"
            "5. **Set the example outside the house** — on picnics, trips, malls. "
            "Everywhere plastic is offered, they have their own."
        ),
        "parent_note_md": (
            "A single reusable bottle replaces ~300 single-use plastic bottles a year. "
            "Beyond the planetary impact, children who carry their own kit develop "
            "preparedness and self-sufficiency — a habit that extends far beyond water."
        ),
    },
    {
        "slug": "compost-kitchen-waste-age10",
        "title": "Help Compost Kitchen Scraps",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up a compost bin** — a terracotta pot, a balcony bucket, or a community "
            "compost heap. Many housing societies now have collective composting.\n"
            "2. **Learn what composts** — fruit peels, vegetable scraps, tea leaves, eggshells. "
            "NO meat, dairy, oil, or cooked food at this level.\n"
            "3. **Add the brown layer** — dry leaves, newspaper, cardboard pieces. "
            "Kitchen waste alone smells; brown matter balances it.\n"
            "4. **Turn it weekly** — aerating the pile speeds decomposition. "
            "Kids actually enjoy this — it's hands-on science.\n"
            "5. **Harvest and use the compost** — for plants at home. "
            "Closing the loop from scrap to soil is the whole point."
        ),
        "parent_note_md": (
            "Composting teaches that waste and resource are the same thing in a different "
            "state. Children who compost understand soil, microbes, and organic cycles — "
            "and see up close that responsible living is practical, not theoretical."
        ),
    },
    {
        "slug": "repair-before-replace-age11",
        "title": "Try to Repair Before Replacing",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Identify one broken item** — a torn bag, loose button, hanging shoe sole, "
            "stiff zipper. Start small.\n"
            "2. **Research the fix** — a quick YouTube search shows nine out of ten simple "
            "repairs. Learn to use this resource.\n"
            "3. **Find the tool or glue** — needle and thread, super glue, tape, "
            "a screwdriver. Every household has a basic repair kit or can build one.\n"
            "4. **Attempt the repair** — imperfectly is fine. 'Good enough to use for another year' "
            "beats 'thrown away perfectly'.\n"
            "5. **Track items saved** — over a year, keep a list of things repaired. "
            "Celebrate the cost and carbon avoided."
        ),
        "parent_note_md": (
            "We live in a throwaway age. A child who learns to repair before replacing "
            "fights two massive modern problems at once — consumer waste and learned "
            "helplessness. They develop practical skills and a confident, capable relationship "
            "with the physical world."
        ),
    },
]


# ---------------------------------------------------------------------------
# Healthcare self-management (Handle Your Own Healthcare mastery)
# ---------------------------------------------------------------------------

HEALTH_TASKS = [
    {
        "slug": "know-own-medicines-age11",
        "title": "Know What Medicines You Take and Why",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **List everything they take regularly** — even multivitamins count. "
            "Write name, dose, and reason.\n"
            "2. **Learn the real name, not just the nickname** — 'paracetamol' not just "
            "'fever medicine'. The real name is what doctors and chemists understand.\n"
            "3. **Know the reason** — what is each medicine treating? What would happen without it?\n"
            "4. **Learn allergy history** — anything they've ever reacted badly to. "
            "This may save their life in a future emergency.\n"
            "5. **Keep the list where it's accessible** — a note on their phone, "
            "a card in their wallet. Updated when anything changes."
        ),
        "parent_note_md": (
            "Most adults can't accurately name their own medications — a gap that causes "
            "real harm during emergencies. A child who knows their own medicines and "
            "allergies by age 11 carries this knowledge forward as a core self-care "
            "competence into adult life."
        ),
    },
    {
        "slug": "medicine-dosage-safety-age12",
        "title": "Read Medicine Labels and Dose Safely",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read the label on every medicine** — dose, timing, "
            "with/without food, warnings. Not the brand name, the actual instructions.\n"
            "2. **Understand 'as needed' vs 'regularly'** — paracetamol 'as needed' means "
            "only when needed; BP medicine 'regularly' means every day without fail.\n"
            "3. **Check the expiry date** — never take expired medicine. "
            "Even if it looks fine, effectiveness drops and some become unsafe.\n"
            "4. **Know the max dose and the spacing** — e.g. paracetamol every 4–6 hours, "
            "max 4 times a day. Overdose is dangerous.\n"
            "5. **Store medicines right** — cool, dry, away from young children. "
            "Never kept in the bathroom (humid)."
        ),
        "parent_note_md": (
            "Medication errors are one of the most common preventable causes of harm "
            "at home. A 12-year-old who can confidently read a label and dose themselves "
            "responsibly doesn't need an adult to hand out every tablet — and is "
            "prepared for occasional unsupervised moments."
        ),
    },
    {
        "slug": "when-to-see-doctor-age12",
        "title": "Know When to See a Doctor",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the 'watch and wait' list** — common cold, mild headache, small cuts, "
            "low fever under 48 hours. Rest, fluids, paracetamol — usually self-resolves.\n"
            "2. **Learn the 'same-day doctor' list** — fever over 39°C, severe pain, "
            "vomiting > 24 hours, rash with fever, breathing difficulty.\n"
            "3. **Learn the 'emergency now' list** — chest pain, fainting, severe bleeding, "
            "head injury with confusion, sudden weakness on one side. Hospital, not clinic.\n"
            "4. **Never Google-diagnose alone** — the internet will scare you into the worst "
            "case. Check symptoms with a parent or qualified adult.\n"
            "5. **Write it down for reference** — simple one-page list at home. "
            "Read it through together once a year."
        ),
        "parent_note_md": (
            "Knowing when to escalate and when to wait is a life skill most adults only learn "
            "through panic trips to A&E. A child with this knowledge makes better decisions "
            "about their own health and eventually their own children's."
        ),
    },
    {
        "slug": "keep-health-record-age13",
        "title": "Keep Your Own Basic Health Record",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start a health file** — a physical folder or a phone note. "
            "One place for everything.\n"
            "2. **Record key data points** — blood group, allergies, long-term conditions, "
            "height and weight (updated yearly), vision prescription if any.\n"
            "3. **Log doctor visits** — date, doctor, reason, what was done, follow-ups needed. "
            "One line each is enough.\n"
            "4. **Save prescriptions and test reports** — digital photos or PDFs. "
            "Organised by date.\n"
            "5. **Update after every visit** — right away, before it's forgotten. "
            "A 30-second habit that saves hours later."
        ),
        "parent_note_md": (
            "Indian healthcare doesn't have unified patient records. A child who keeps "
            "their own record grows into an adult who can answer any doctor's questions "
            "confidently — and avoid repeat tests, wrong prescriptions, and lost history "
            "when switching providers."
        ),
    },
    {
        "slug": "book-doctor-appt-age14",
        "title": "Book Your Own Doctor's Appointment",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know the clinic name, doctor name, and phone number** — before calling. "
            "Look up if unsure.\n"
            "2. **Prepare before you call** — why you need the appointment, how urgent, "
            "preferred day/time. Rehearse if needed.\n"
            "3. **Open the call well** — 'Hello, this is [name], I'd like to book an "
            "appointment with Dr X.' Direct and polite.\n"
            "4. **Note down the confirmed time** — in their calendar, phone alarm, "
            "or diary. Never rely on memory alone.\n"
            "5. **Confirm a day before if needed** — some clinics require it; "
            "many appreciate it. Shows maturity."
        ),
        "parent_note_md": (
            "Phone anxiety is real for this generation — the dominant medium is text. "
            "But medical appointments, bookings, and business calls still happen by phone. "
            "A teen who can confidently book a doctor's appointment by phone is practising "
            "a skill they'll need throughout adult life."
        ),
    },
    {
        "slug": "know-family-medical-history-age14",
        "title": "Know Your Family's Medical History",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Sit with parents or grandparents** — 30 minutes, no distractions. "
            "This is one of those conversations that matters.\n"
            "2. **Ask about the big five** — heart disease, diabetes, cancer, stroke, "
            "mental health. In both parents' families, going back to grandparents.\n"
            "3. **Ask about age of onset** — 'at what age was Dadi diagnosed with diabetes?' "
            "Earlier onset = higher genetic risk.\n"
            "4. **Write it down in their health file** — a simple family tree with conditions "
            "and ages. A doctor can use this directly.\n"
            "5. **Update when new diagnoses happen** — extended family illnesses added "
            "as they become known. Living document."
        ),
        "parent_note_md": (
            "Family medical history is the single most predictive piece of information "
            "a doctor can use for preventive care. Asking these questions while grandparents "
            "are alive and remember clearly is a gift to the child's future self — and "
            "to their children."
        ),
    },
]


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

# (tag_name, Tag.Category) — all gap tasks fit into existing categories
TAG_BY_GROUP = {
    "fitness":  ("Home care",        Tag.Category.HOUSEHOLD),
    "creator":  ("Digital literacy", Tag.Category.DIGITAL),
    "eco":      ("Home care",        Tag.Category.HOUSEHOLD),
    "health":   ("Home care",        Tag.Category.HOUSEHOLD),
}

GROUP_TASKS = {
    "fitness":  FITNESS_TASKS,
    "creator":  CREATOR_TASKS,
    "eco":      ECO_TASKS,
    "health":   HEALTH_TASKS,
}


class Command(BaseCommand):
    help = "Seed 25 gap-filler tasks — fitness, digital creation, eco, healthcare self-management."

    def handle(self, *args, **options):
        all_envs = list(Environment.objects.all())

        tag_by_group: dict[str, Tag] = {}
        for group, (tag_name, tag_category) in TAG_BY_GROUP.items():
            tag, _ = Tag.objects.get_or_create(
                name=tag_name, defaults={"category": tag_category}
            )
            tag_by_group[group] = tag

        total_added = 0
        total_updated = 0
        for group, tasks in GROUP_TASKS.items():
            tag = tag_by_group[group]
            g_added = 0
            g_updated = 0
            for t in tasks:
                task, created = Task.objects.update_or_create(
                    slug=t["slug"],
                    defaults={
                        "title": t["title"],
                        "how_to_md": t["how_to_md"],
                        "safety_md": t.get("safety_md", ""),
                        "parent_note_md": t.get("parent_note_md", ""),
                        "min_age": t["min_age"],
                        "max_age": t["max_age"],
                        "sex_filter": t.get("sex_filter", "any"),
                        "status": ReviewStatus.APPROVED,
                    },
                )
                task.tags.set([tag])
                task.environments.set(all_envs)
                if created:
                    g_added += 1
                else:
                    g_updated += 1
            total_added += g_added
            total_updated += g_updated
            self.stdout.write(
                f"{group:10}: {g_added} new, {g_updated} updated."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_gap_tasks complete — "
                f"{total_added} new, {total_updated} updated, "
                f"{total_added + total_updated} total."
            )
        )
