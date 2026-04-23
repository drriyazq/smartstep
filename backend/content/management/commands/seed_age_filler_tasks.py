"""Management command: seed one ladder-filler task per (category, age) cell.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_age_filler_tasks

Adds 72 approved tasks — one per category (cognitive, social, household, digital,
navigation, financial) for every age year 5–16. Each task is upserted via
update_or_create(slug=...) so re-running is idempotent and safe.

Age range convention: min_age = age, max_age = min(age + 2, 16).
Tags are set to each category's primary tag (same one used by refine_*_ladder).
Environments are assigned to all (urban, suburban, rural).
"""
from django.core.management.base import BaseCommand

from content.models import Environment, ReviewStatus, Tag, Task


# ---------------------------------------------------------------------------
# Category tag name → Tag.Category lookup
# ---------------------------------------------------------------------------

TAG_FOR_CATEGORY = {
    "cognitive":  ("Reasoning",        Tag.Category.COGNITIVE),
    "social":     ("Social skills",    Tag.Category.SOCIAL),
    "household":  ("Home care",        Tag.Category.HOUSEHOLD),
    "digital":    ("Digital literacy", Tag.Category.DIGITAL),
    "navigation": ("Wayfinding",       Tag.Category.NAVIGATION),
    "financial":  ("Money basics",     Tag.Category.FINANCIAL),
}


def _age_range(age: int) -> tuple[int, int]:
    return age, min(age + 2, 16)


# ---------------------------------------------------------------------------
# COGNITIVE — one task per age 5–16
# ---------------------------------------------------------------------------

COGNITIVE_TASKS = [
    {
        "slug": "days-of-week-order-age5",
        "title": "Name the Days of the Week in Order",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Say the seven days together** — Monday, Tuesday, Wednesday, Thursday, "
            "Friday, Saturday, Sunday. A little rhythm helps it stick.\n"
            "2. **Anchor each day to a real event** — *Monday is school again. "
            "Wednesday is swimming. Saturday we visit Nani.*\n"
            "3. **Ask what day it is** — every morning at breakfast. Build the habit.\n"
            "4. **Play the 'what comes next' game** — *After Tuesday comes...?* "
            "Then *before Friday comes...?* Harder in reverse.\n"
            "5. **Find the weekend** — which two days are the weekend? "
            "Which day is in the middle of the week?"
        ),
        "parent_note_md": (
            "Knowing the days of the week in order is the first step toward time literacy. "
            "Children who can orient to the week cope better with school routines, "
            "anticipate what's next, and handle transitions more calmly."
        ),
    },
    {
        "slug": "continue-simple-pattern-age6",
        "title": "Continue a Simple Pattern (ABAB, ABC)",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with ABAB** — red bead, blue bead, red bead, blue bead... "
            "*What comes next?* Use any two-item set you have on hand.\n"
            "2. **Move to ABC** — triangle, square, circle, triangle, square, circle... "
            "Let them finish the row.\n"
            "3. **Use sounds and actions** — clap-stomp-clap-stomp. Point at them to continue. "
            "Patterns aren't just visual.\n"
            "4. **Let them make a pattern** — set a rule and tell you what the rule is. "
            "This tests understanding, not just recognition.\n"
            "5. **Break a pattern on purpose** — *Red, blue, red, blue, GREEN!* "
            "Can they spot the mistake and fix it?"
        ),
        "parent_note_md": (
            "Pattern recognition is the seed of mathematical thinking, programming logic, "
            "and scientific reasoning. Children who can see, continue, and create patterns "
            "are building the brain machinery they'll later use for algebra and problem-solving."
        ),
    },
    {
        "slug": "recall-five-item-list-age7",
        "title": "Remember a 5-Item List from Memory",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Say five unrelated items** — *Pen, apple, socks, key, spoon.* "
            "Say each one clearly, then wait.\n"
            "2. **Ask them to repeat** — straight away. Praise any order; accuracy first.\n"
            "3. **Add a 30-second distraction** — talk about something else, then ask again. "
            "Recall after distraction is the real skill.\n"
            "4. **Teach a memory trick** — picture the items in a row, or build a silly story "
            "linking them. *The pen eats the apple while wearing socks...*\n"
            "5. **Use it for real errands** — five things to fetch from three rooms. "
            "No list, just memory."
        ),
        "parent_note_md": (
            "Working memory — holding several things in mind at once — is one of the "
            "strongest predictors of academic performance. A child who can reliably "
            "remember 5 items at 7 is building the exact mental muscle needed for "
            "following multi-step instructions at school."
        ),
    },
    {
        "slug": "read-clock-5min-age8",
        "title": "Read a Clock to the Nearest 5 Minutes",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a real analog clock** — not digital, not an app. A face with hands.\n"
            "2. **Revisit the numbers** — each number on the face is 5 minutes. "
            "12 = 0 or 60, 1 = 5, 2 = 10, 3 = 15... up to 11 = 55.\n"
            "3. **Start with the minute hand on numbers only** — *The big hand is on 6. "
            "That's 30 minutes past.*\n"
            "4. **Move through the hour** — set the clock to 3:15, 7:40, 10:55. "
            "They read each one out loud.\n"
            "5. **Quarter-past, half-past, quarter-to** — teach the short-hand expressions. "
            "*Quarter to 5* = 4:45. These are how people actually talk about time."
        ),
        "parent_note_md": (
            "Reading an analog clock is becoming a lost skill — and that matters because "
            "so much of time language (*half past, quarter to*) only makes sense on a "
            "clock face. A child fluent with an analog clock reads time visually, not "
            "by decoding digits, and handles schedules more intuitively."
        ),
    },
    {
        "slug": "predict-next-step-age9",
        "title": "Predict the Next Step in a Story or Process",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pause a story mid-scene** — book or film. *What do you think happens next? "
            "Why do you think that?*\n"
            "2. **Insist on reasoning** — not just a guess. The prediction must connect to "
            "something already in the story.\n"
            "3. **Apply it to real processes** — *We've mixed the batter and preheated the oven. "
            "What's the next step in baking a cake?*\n"
            "4. **Use it with science** — *If I drop this ball, what will happen? Why? "
            "And what will happen after that?*\n"
            "5. **Check against reality** — did the prediction come true? If not, "
            "*what did we miss?* Revising a wrong prediction is the real learning."
        ),
        "parent_note_md": (
            "Prediction is how the brain tests its model of the world. Children who are "
            "asked to predict — and to justify their prediction with reasons — develop "
            "sharper comprehension, stronger scientific thinking, and better reading "
            "comprehension. Every story and every everyday task is a chance to practise."
        ),
    },
    {
        "slug": "compare-quantities-age10",
        "title": "Compare Quantities Using >, <, and =",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Introduce the symbols** — *The hungry crocodile eats the bigger number.* "
            "8 > 5, 3 < 9. Draw the mouth around it.\n"
            "2. **Start with single digits** — they fill in the missing symbol. "
            "7 ? 4. 2 ? 6. 5 ? 5 (practise = as well).\n"
            "3. **Move to two and three digits** — 45 ? 54. 100 ? 99. "
            "*Which is bigger — and by how much?*\n"
            "4. **Use real prices or measurements** — *This book is ₹120. That one is ₹85. "
            "Which symbol goes between them?*\n"
            "5. **Include expressions** — 4 + 5 ? 3 × 3. They must calculate both sides "
            "before comparing. Use it for basic algebra-readiness."
        ),
        "parent_note_md": (
            "Fluency with comparison symbols is the gateway to inequalities, algebra, "
            "and data literacy. The skill is small but the downstream mileage is huge — "
            "every graph, every price comparison, every budget uses the same underlying idea."
        ),
    },
    {
        "slug": "build-argument-reason-example-age11",
        "title": "Build an Argument with One Reason and One Example",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a real opinion they hold** — favourite sport, best subject, "
            "a rule they'd change at school.\n"
            "2. **Teach the three-part structure** — *Claim: I think X. "
            "Reason: because Y. Example: for instance, Z.*\n"
            "3. **Make them say it out loud** — *Football is the best sport because it "
            "teaches teamwork — for example, in our last match the striker only scored "
            "because the defenders passed the ball forward.*\n"
            "4. **Challenge weak reasons** — *'It's fun' is an opinion, not a reason. "
            "Can you give me a reason someone who disagrees would still respect?*\n"
            "5. **Write it down** — three sentences, one paragraph: claim, reason, example. "
            "Re-use the shape for essay writing at school."
        ),
        "parent_note_md": (
            "Most adult arguments fail because they skip the reason or miss the example. "
            "The claim-reason-example shape is the minimum structure of persuasion — "
            "the same bones are used in debate, essay writing, professional emails, and "
            "court arguments. Drill it at 11 and it becomes automatic for life."
        ),
    },
    {
        "slug": "skim-main-idea-age12",
        "title": "Skim an Article to Find the Main Idea in 60 Seconds",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a short news article or textbook page** — 400–600 words. "
            "Set a 60-second timer.\n"
            "2. **Teach the skim path** — headline first, then first paragraph, "
            "then first sentence of every paragraph, then last paragraph. Skip the middle.\n"
            "3. **When the timer beeps, they say the main idea** — one sentence. "
            "*What is this article really saying?*\n"
            "4. **Check by reading fully** — did they catch the main point? "
            "What nuance did they miss? Where did the main idea actually live?\n"
            "5. **Repeat on different genres** — news, opinion, explainer, science. "
            "Each has a different place where the main idea hides."
        ),
        "parent_note_md": (
            "Skimming is not lazy reading — it's a distinct skill. A teenager who can "
            "scan a page in a minute and extract the core idea reads more, learns faster, "
            "and handles information overload that sinks many adults. Valuable at school, "
            "at university, and in every knowledge-work job."
        ),
    },
    {
        "slug": "mind-map-study-topic-age13",
        "title": "Make a Mind Map of a Topic You're Studying",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick an actual school topic** — something they have a test on. "
            "Large blank sheet, pens in different colours.\n"
            "2. **Write the topic in the centre** — circle it. This is the trunk.\n"
            "3. **Draw 4–6 main branches** — the big sub-topics. Each branch is one colour. "
            "Keep the label to one or two words.\n"
            "4. **Branch the branches** — each main branch breaks into 3–5 smaller ideas. "
            "Use little drawings or icons, not only text.\n"
            "5. **Redraw from memory the next day** — if they can re-create the map "
            "without looking, they know the topic. If not, the gaps show exactly where "
            "to revise."
        ),
        "parent_note_md": (
            "Mind mapping works because the brain stores information in connected networks, "
            "not linear lists. A teenager who mind-maps before a test understands the "
            "structure of the topic, not just the facts — and structure is what lets them "
            "answer questions they didn't specifically revise for."
        ),
    },
    {
        "slug": "feynman-teach-back-age14",
        "title": "Teach a Concept Back Using the Feynman Technique",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick one thing they just learned** — a maths concept, a history event, "
            "a chemical reaction. One small thing, not a whole chapter.\n"
            "2. **Explain it to you like you're 10** — no jargon. If they need a technical "
            "word, they must define it first in plain language.\n"
            "3. **Catch the stumbles** — every moment they hesitate or get vague is a gap "
            "in understanding, not communication. Mark it.\n"
            "4. **Go back to the source** — re-read the textbook or notes on just that gap. "
            "Fill it in.\n"
            "5. **Teach it again** — this time cleaner. If they can explain it simply all "
            "the way through, they own it."
        ),
        "parent_note_md": (
            "Richard Feynman's technique is the most honest test of understanding ever "
            "devised: if you can't explain it simply, you don't understand it yet. "
            "Teenagers who practise this regularly stop confusing *familiar* with *understood* — "
            "the single biggest trap in exam revision."
        ),
    },
    {
        "slug": "two-week-study-plan-age15",
        "title": "Plan a Two-Week Study Schedule for an Exam",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start from the exam date** — work backwards. Mark the exam on a calendar "
            "and count the 14 days before it.\n"
            "2. **Break the syllabus into chunks** — 10–14 chunks, one per day. "
            "Harder topics get more days, easier ones get fewer.\n"
            "3. **Reserve the last 2 days for full mock papers** — not new learning. "
            "The brain needs time to practise retrieval under exam conditions.\n"
            "4. **Block specific times on each day** — not *study maths* but *9:30–11:00 maths, "
            "trigonometry*. Vague plans fail.\n"
            "5. **Review the plan after 3 days** — is it working? Slipping behind means the "
            "plan was wrong, not that the child failed. Adjust, don't abandon."
        ),
        "parent_note_md": (
            "The ability to plan backwards from a deadline and distribute effort across "
            "time is one of the most important executive-function skills for secondary "
            "school and beyond. Students who can build a real study plan outperform those "
            "who just *study harder* — because planning is itself a form of understanding."
        ),
    },
    {
        "slug": "craap-test-source-age16",
        "title": "Evaluate a Source Using the CRAAP Test",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a source they're about to cite** — an article, a video, a website. "
            "One they were going to use without thinking.\n"
            "2. **Currency** — when was it published? Is the information still up to date? "
            "For fast-moving topics, a 10-year-old source is dangerous.\n"
            "3. **Relevance** — does it actually answer the question being asked, "
            "or just touch the topic? Reject near-misses.\n"
            "4. **Authority and Accuracy** — who wrote it? What are their credentials? "
            "Can you verify the key claims somewhere independent?\n"
            "5. **Purpose** — why was this written? To inform, persuade, sell, entertain? "
            "Purpose shapes what gets left out. Always note it."
        ),
        "parent_note_md": (
            "The CRAAP test (Currency, Relevance, Authority, Accuracy, Purpose) is a "
            "discipline of source evaluation used in universities and professional research. "
            "A teenager who applies it to every major source avoids the single biggest "
            "failure mode of modern research — treating everything Google surfaces as "
            "equally trustworthy."
        ),
    },
]


# ---------------------------------------------------------------------------
# SOCIAL — one task per age 5–16
# ---------------------------------------------------------------------------

SOCIAL_TASKS = [
    {
        "slug": "say-please-thank-you-age5",
        "title": "Say Please and Thank You Without a Reminder",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Model it relentlessly** — they hear you say *please* and *thank you* to them, "
            "to strangers, to family. Children copy what they see.\n"
            "2. **Pause and wait** — when they ask for something, don't hand it over until the "
            "word is there. Silence is a better teacher than a lecture.\n"
            "3. **Thank them visibly** — say thank you when they do something helpful. "
            "It teaches the rhythm of the word.\n"
            "4. **Notice unprompted use** — when the word appears without a reminder, say so. "
            "*I noticed you said thank you on your own.*\n"
            "5. **Do not force public performance** — shy kids freeze when pushed. "
            "Keep it low-key; habit builds over months, not days."
        ),
        "parent_note_md": (
            "Basic courtesy, used without prompting, opens doors for the rest of a child's life. "
            "Adults are disproportionately kind to children who say please and thank you — "
            "and that warmth feeds back into the child's confidence in social situations."
        ),
    },
    {
        "slug": "share-toy-no-adult-age6",
        "title": "Share a Toy Without a Grown-Up Stepping In",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up the situation** — one toy, two children, no adult hovering. "
            "Play date or sibling session.\n"
            "2. **Watch from a distance** — do not rescue instantly. Let small friction play out "
            "for a minute.\n"
            "3. **Teach the two scripts beforehand** — *Can I have a turn when you're done?* "
            "and *Yes, two more minutes.* Rehearse before the event.\n"
            "4. **Use a timer if needed** — three-minute turns. The timer is the boss, not you.\n"
            "5. **Debrief afterwards** — *How did it feel when it worked? What would you do "
            "differently next time?*"
        ),
        "parent_note_md": (
            "Learning to share without an adult umpire is the start of genuine cooperation. "
            "Children who can negotiate turns on their own develop self-regulation and "
            "empathy far faster than children whose parents referee every minor dispute."
        ),
    },
    {
        "slug": "introduce-to-classmate-age7",
        "title": "Introduce Yourself to a New Classmate",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the script** — *Hi, I'm [name]. What's your name? "
            "Do you want to play/sit together?* Three short lines.\n"
            "2. **Rehearse at home** — you play the new classmate. They practise saying it "
            "without mumbling.\n"
            "3. **Role-play the awkward cases** — what if the other child ignores them? "
            "*Say it again once, then try someone else.* No drama.\n"
            "4. **Set a real-world target** — at the next playground visit, school event, "
            "or family gathering, introduce themselves to one new person.\n"
            "5. **Celebrate the attempt, not the outcome** — whether or not the other child "
            "wanted to play, the action of introducing is what matters."
        ),
        "parent_note_md": (
            "Initiating social contact is one of the hardest skills for shy children — "
            "and one of the highest-value. A child who has practised the first line of "
            "introduction a dozen times is not relying on courage in the moment; "
            "they're relying on muscle memory."
        ),
    },
    {
        "slug": "wait-turn-speak-age8",
        "title": "Wait Your Turn to Speak in a Group",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the why** — everyone has something to say. If we all speak at once, "
            "nobody gets heard.\n"
            "2. **Teach the hand-raise or nod cue** — when they want to speak, a small signal "
            "and then wait for an opening.\n"
            "3. **Hold the thought** — a child's hardest bit is losing their idea while waiting. "
            "Teach them to mentally repeat a keyword. *Cricket. Cricket. Cricket.*\n"
            "4. **Practise at family meals** — everyone takes turns sharing one thing about "
            "their day. No interrupting, even when excited.\n"
            "5. **Acknowledge when it happens** — *You waited really well there. I noticed.*"
        ),
        "parent_note_md": (
            "The ability to wait your turn to speak is the bedrock of group learning, "
            "classroom discussion, and eventually meetings and teamwork. Children who "
            "struggle with it don't lack manners — they lack the working-memory trick "
            "of holding an idea while waiting. Practising the keyword-repeat trick fixes it."
        ),
    },
    {
        "slug": "apologise-feelings-age9",
        "title": "Apologise Properly When You Hurt Someone's Feelings",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the three-part apology** — *I'm sorry I did X. I know it hurt because Y. "
            "Next time I'll do Z.* Name the action, the impact, the repair.\n"
            "2. **Compare with a fake apology** — *Sorry you feel that way* is not an apology. "
            "Show them why it isn't.\n"
            "3. **Make them wait until calm** — apologising in a heated moment often makes it "
            "worse. Ten minutes of quiet, then approach.\n"
            "4. **Let them write it first** — for bigger situations, a short written apology, "
            "then say it in person.\n"
            "5. **Don't force immediate forgiveness** — the other person gets to decide when "
            "they're ready. The apologiser's job is to apologise, not to demand resolution."
        ),
        "parent_note_md": (
            "A proper apology is a repair skill — one of the most important in all human "
            "relationships. Children who grow up saying empty sorrys learn that the word "
            "ends the discussion; children who learn the three-part form learn that an "
            "apology opens repair. This sticks for life."
        ),
    },
    {
        "slug": "read-room-join-activity-age10",
        "title": "Read the Room Before Joining an Activity",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Stop and watch first** — before joining a game, a group conversation, "
            "or an activity, pause. Ten seconds of observing.\n"
            "2. **Ask four silent questions** — What are they doing? What's the mood? "
            "Is there a natural gap? Would I be welcome?\n"
            "3. **Look for the entry point** — between rounds, during a break, at the start "
            "of a new activity. Not mid-conversation.\n"
            "4. **Ask before inserting** — *Can I join in?* or *Mind if I listen?* beats "
            "bursting in.\n"
            "5. **Gracefully back out** — if the read says no, leave without making it "
            "awkward. *No worries, catch you later.* Dignity intact."
        ),
        "parent_note_md": (
            "Reading a room — noticing mood, energy, and unspoken rules — is one of the "
            "most socially valuable skills a child can have. Some children have it "
            "naturally; many learn it the hard way from rejection. Teaching it explicitly, "
            "with the four-question check, shortcuts years of social bruising."
        ),
    },
    {
        "slug": "say-no-keep-friend-age11",
        "title": "Say No to a Friend Without Losing the Friendship",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Separate the person from the ask** — *I love you, but I don't want to do this.* "
            "The friendship is not on trial.\n"
            "2. **Teach a soft-no script** — *Thanks for asking, but that's not for me.* or "
            "*I can't today — maybe another time.* Short, kind, firm.\n"
            "3. **Role-play the pushback** — *Come on, don't be boring.* They must hold the no "
            "without escalating. *Sorry, still no.*\n"
            "4. **Offer alternatives when possible** — *I don't want to bunk school, "
            "but let's hang out on Saturday.* Preserves the friendship.\n"
            "5. **Debrief real uses** — when it happens, talk about how it went. "
            "Was the friendship strained? Did it survive? Usually it does."
        ),
        "parent_note_md": (
            "The ability to say no while keeping a friendship is the foundation of every "
            "good adult boundary. Pre-teens who only know *yes* or *explosive no* struggle "
            "with peer pressure for years. A soft, firm, non-apologising no is a skill, "
            "not a personality trait — and it has to be practised."
        ),
    },
    {
        "slug": "resist-peer-pressure-age12",
        "title": "Recognise and Resist Peer Pressure",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the forms** — not just *everyone is doing it* but silence, "
            "mockery, exclusion, FOMO. Pressure is often subtle.\n"
            "2. **Run the *would I be okay later?* test** — if this gets back to a parent, "
            "a teacher, a coach — would I be fine with it? If not, it's a red flag.\n"
            "3. **Rehearse three exit lines** — *Not tonight.* *I told my parents I wouldn't.* "
            "*I'll catch you later.* Pre-loaded lines beat in-the-moment thinking.\n"
            "4. **Identify an ally** — who's the one friend they can text to get bailed out? "
            "A shared code word works wonders.\n"
            "5. **Tell the stories** — your own teen experiences, stories from news. "
            "Peer pressure is normal; handling it is the skill."
        ),
        "parent_note_md": (
            "Peer pressure peaks around 12–14 and is the single biggest predictor of early "
            "risky behaviour. Pre-loaded exit lines and a rehearsed ally work better than "
            "lectures on values. Practice is what converts values into action in the actual moment."
        ),
    },
    {
        "slug": "give-constructive-feedback-age13",
        "title": "Give Constructive Feedback to a Peer",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with permission** — *Do you want honest feedback, or just support?* "
            "Not everyone wants critique.\n"
            "2. **Use the sandwich only when real** — a genuine strength, a specific concern, "
            "a genuine encouragement. Fake sandwiches insult the listener.\n"
            "3. **Be specific, not global** — not *your essay is bad* but *the second paragraph "
            "lost me because the argument jumps.* Specific is useful; global is a wound.\n"
            "4. **Suggest, don't command** — *What if you tried X?* beats *You should do X.*\n"
            "5. **Ask for their response** — *Does that make sense? Is it helpful?* "
            "Feedback is a conversation, not a verdict."
        ),
        "parent_note_md": (
            "Giving constructive feedback is a skill rarely taught and hugely valued in "
            "every adult workplace. Teenagers who have practised it with peers learn that "
            "critique can be kind, specific, and actionable — and they become the kind of "
            "friend, colleague, and eventual manager whose feedback people actually want."
        ),
    },
    {
        "slug": "disagree-without-raising-voice-age14",
        "title": "Handle a Disagreement Without Raising Your Voice",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Notice the body first** — tight chest, hot face, clenched jaw. Disagreement "
            "tips into anger before the voice rises. Catch it early.\n"
            "2. **Name it out loud** — *I'm getting wound up. Give me a moment.* "
            "Calling it breaks the spiral.\n"
            "3. **Slow the rate of speech, not the volume** — speaking more slowly lowers "
            "the room's temperature faster than speaking more softly.\n"
            "4. **Use *I* statements** — *I see it differently because...* rather than "
            "*You're wrong.* Same content, very different feel.\n"
            "5. **Know when to pause** — some disagreements need 20 minutes to cool. "
            "*Let's talk again after dinner* is strength, not avoidance."
        ),
        "parent_note_md": (
            "Handling disagreement without escalating is the core skill of every stable "
            "adult relationship — romantic, family, professional. Teenagers who only "
            "have *match energy or shut down* as options grow into adults who struggle "
            "with conflict for decades. The skill is learnable; it just has to be practised."
        ),
    },
    {
        "slug": "long-distance-friendship-age15",
        "title": "Maintain a Long-Distance Friendship Over 3+ Months",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick one friend who moved or is far** — focus on quality, not on staying "
            "in touch with everyone.\n"
            "2. **Set a rhythm, not a chore** — a weekly voice note, a monthly video call, "
            "a small meme when it reminds them of the friend. Rhythm beats rules.\n"
            "3. **Share real life, not highlights** — long-distance friendships die when "
            "conversations become updates-only. The small silly details are the glue.\n"
            "4. **Remember their stuff** — exam dates, family events, birthdays. "
            "A quick message on the actual day matters a lot.\n"
            "5. **Plan one real-world meetup in the year** — a friendship without any "
            "in-person time slowly fades. Even one visit recharges it for months."
        ),
        "parent_note_md": (
            "The ability to sustain friendships across distance and time is one of the "
            "strongest predictors of adult wellbeing. Teenagers who practise it learn "
            "something most adults never figure out: that deep friendships survive on "
            "small, steady effort, not grand gestures."
        ),
    },
    {
        "slug": "network-follow-up-age16",
        "title": "Network and Follow Up with Useful Adult Contacts",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Identify a real starting list** — teachers, coaches, parents' contacts, "
            "guest speakers. Not strangers — people they've already met.\n"
            "2. **Write a first polite message** — one paragraph. *It was great meeting you at X. "
            "I'm interested in Y — could I ask you one question about it?*\n"
            "3. **Ask one specific question** — vague questions get ignored; specific questions "
            "get thoughtful replies. *What's one book you'd recommend for someone considering "
            "engineering?*\n"
            "4. **Thank them properly** — within 24 hours of any reply. Even a one-line "
            "thank-you keeps the door open.\n"
            "5. **Stay on their radar** — every 6 months, a short update. *Remember you suggested X — "
            "I did it and it went well. Thanks again.* This is how adult networks form."
        ),
        "parent_note_md": (
            "Networking at 16 is not cynical — it's how opportunities are actually "
            "distributed in the adult world. Teenagers who learn to politely reach out, "
            "ask good questions, and follow up graciously build a compounding advantage "
            "that quiet peers miss entirely."
        ),
    },
]


# ---------------------------------------------------------------------------
# HOUSEHOLD — one task per age 5–16
# ---------------------------------------------------------------------------

HOUSEHOLD_TASKS = [
    {
        "slug": "dirty-clothes-laundry-basket-age5",
        "title": "Put Dirty Clothes in the Laundry Basket",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show where the basket lives** — bedroom? Bathroom? Make it obvious and "
            "reachable without help.\n"
            "2. **Teach the trigger moment** — taking clothes off at bath time or bedtime. "
            "*Clothes off → straight into the basket.*\n"
            "3. **Never pick up after them for a week** — let the clothes sit wherever they "
            "dropped them. When they run out of pyjamas, the point lands.\n"
            "4. **Praise the habit, not the outcome** — *You put everything in the basket "
            "yourself. That's grown-up work.*\n"
            "5. **Add socks and underwear to the rule** — these are the most-forgotten items. "
            "They count too."
        ),
        "parent_note_md": (
            "Building a simple, reliable household routine at 5 costs the parent one "
            "uncomfortable week of letting clothes lie where they fall. The payoff is a "
            "child who owns their own tidying for the next decade — and internalises "
            "that the house doesn't self-clean."
        ),
    },
    {
        "slug": "wipe-spill-age6",
        "title": "Wipe a Spill Before It Spreads",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show where the cloth lives** — a dedicated spill cloth or paper towels "
            "they can reach without help.\n"
            "2. **Teach the urgency** — small spill now = five seconds. Ignored spill = "
            "sticky puddle or stained carpet in ten minutes.\n"
            "3. **Demonstrate the technique** — blot first (press, don't rub), then wipe. "
            "Rubbing spreads the mess.\n"
            "4. **Tell, don't hide** — if they spill something they can't handle (hot tea, "
            "glass shards, oil), their job is to call an adult fast, not hide it.\n"
            "5. **Celebrate owning up** — reward honesty about accidents. Hidden spills are "
            "far worse than reported ones."
        ),
        "parent_note_md": (
            "Early ownership of small accidents prevents two bigger problems: a child who "
            "learns to hide mistakes, and a house of permanent stains. Building the *spot it, "
            "grab cloth, tell adult* habit at 6 takes weeks; the lifelong benefit is huge."
        ),
    },
    {
        "slug": "pour-drink-no-spill-age7",
        "title": "Pour a Drink Without Spilling",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with cool water and a clear glass** — they need to see the level rise.\n"
            "2. **Teach the two-hand grip** — one hand on the jug or bottle, one hand steadying "
            "the glass. Two-hand is stable; one-hand is a wobble waiting to happen.\n"
            "3. **Pour slowly, stop early** — fill to two-thirds, not the brim. Overfilling is "
            "what causes spills on the way to the table.\n"
            "4. **Practise at every meal** — let them pour their own water for a week. "
            "Mistakes will happen; don't rescue.\n"
            "5. **Move to juice, then to hot drinks under supervision** — each liquid has a "
            "different viscosity. Juice drips more; hot drinks demand extra care."
        ),
        "parent_note_md": (
            "Pouring is one of those tiny skills that secretly screens many kitchen tasks. "
            "A child who can pour their own drink gains independence at meals, "
            "builds hand steadiness for later cooking work, and takes a small but real "
            "step out of needing a parent for every glass of water."
        ),
    },
    {
        "slug": "set-dinner-table-age8",
        "title": "Set the Dinner Table Correctly",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the basic layout** — plate in the middle, fork on the left, knife on "
            "the right (blade facing the plate), spoon on the far right, glass above the knife.\n"
            "2. **Count the people first** — how many plates, cutlery sets, glasses needed? "
            "Counting before carrying prevents double trips.\n"
            "3. **Place napkins** — folded on the plate or under the fork. Small touch, "
            "big difference.\n"
            "4. **Include the shared items** — water jug, salt, condiments. Everything "
            "needed for the meal on the table before sitting.\n"
            "5. **Make it the daily job** — same child, same role, for a week. Ownership "
            "makes it a skill, not a chore."
        ),
        "parent_note_md": (
            "Setting the table teaches spatial thinking, sequence, and responsibility to "
            "the family — all in five minutes a day. A child who owns this task grows up "
            "knowing that meals are something the family creates together, not something "
            "that appears magically."
        ),
    },
    {
        "slug": "wash-dishes-hand-age9",
        "title": "Wash a Small Load of Dishes by Hand",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Scrape first** — leftover food into the bin before anything touches water. "
            "This is the single biggest mistake beginners make.\n"
            "2. **Hot water and a drop of soap** — not a stream of soap. A pea-sized drop "
            "is enough for a small sink.\n"
            "3. **Wash in order** — glasses first (cleanest water), then cutlery, then plates, "
            "then pans last. Grease saved for last.\n"
            "4. **Rinse properly** — soapy dishes taste awful and can upset stomachs. "
            "Run each piece under clean water, both sides.\n"
            "5. **Stack to dry, don't pile** — air needs to reach every surface. "
            "A proper drying rack or a clean tea towel underneath does this."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Hot water:** start warm, not scalding. Check with a hand on the outside of "
            "the sink before submerging.\n"
            "- **Glass and sharp knives:** wash one at a time. Never stack glasses in the sink.\n"
            "- **Slippery floor:** wipe up any water around the sink as you go."
        ),
        "parent_note_md": (
            "Hand-washing dishes is a basic life skill every adult needs — even with a "
            "dishwasher, glassware, knives, and pans usually stay hand-wash only. The "
            "sequence (scrape → soap → wash in order → rinse → dry) is the real lesson, "
            "and it transfers to any multi-step kitchen task."
        ),
    },
    {
        "slug": "sweep-mop-floor-age10",
        "title": "Sweep and Mop a Floor",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Move the movable** — chairs, mats, bins out of the way before starting. "
            "Sweeping around obstacles leaves dust behind.\n"
            "2. **Sweep in one direction** — corner to corner, toward the centre, then into a "
            "dustpan. Random jabs scatter dust everywhere.\n"
            "3. **Bin the sweepings** — dustpan straight to the bin, no pile-on-floor stage.\n"
            "4. **Mop in a figure-8 or S-pattern** — not back-and-forth over the same strip. "
            "Covers the floor without doubling up.\n"
            "5. **Rinse the mop as you go** — a dirty mop just moves the dirt around. "
            "Change the water when it's grey."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Wet floor sign:** tell the household the floor is wet. Slippery floors cause falls.\n"
            "- **Chemicals:** use only the cleaner in the mop bucket the parent has set up. "
            "Never mix cleaning products.\n"
            "- **Lifting furniture:** ask for help with anything heavy. Pushing, not lifting, "
            "is safer for small hands."
        ),
        "parent_note_md": (
            "Sweeping and mopping are the two most basic cleaning routines in any home, "
            "and many adults do them inefficiently. A child who learns the pattern-based "
            "method at 10 does the job faster, better, and more willingly than someone "
            "who was only ever told to *clean the floor* without technique."
        ),
    },
    {
        "slug": "kitchen-knife-chop-age11",
        "title": "Safely Use a Kitchen Knife for Chopping",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick the right knife** — a small chef's knife, sharp. Dull knives slip — "
            "they are more dangerous than sharp ones.\n"
            "2. **Teach the claw grip** — fingers of the non-cutting hand curled inward, "
            "knuckles forward. The blade tracks the knuckles.\n"
            "3. **Start with soft items** — banana, boiled potato, cucumber. Build confidence "
            "before tougher things.\n"
            "4. **Board technique** — a damp tea towel under the board stops it sliding. "
            "A sliding board under a sharp knife is the classic recipe for an accident.\n"
            "5. **Cut down, not across** — the blade rocks forward and down; it does not saw "
            "back and forth. Slow, controlled, repeatable."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Adult present, always:** the first 20+ times. Supervised practice before solo.\n"
            "- **Never catch a falling knife:** step back and let it drop. Pick it up off the floor.\n"
            "- **Handle wet or oily fingers:** dry the handle and the hand before cutting.\n"
            "- **One job at a time:** no phone, no talking over the shoulder, no distracted cutting."
        ),
        "parent_note_md": (
            "Knife handling is one of the biggest jumps in kitchen independence — and the "
            "one parents most often delay. A pre-teen who has learned the claw grip, the "
            "board-stabilising trick, and the 'never catch a dropped knife' rule has moved "
            "from kitchen bystander to genuine helper."
        ),
    },
    {
        "slug": "sew-button-age12",
        "title": "Sew a Button Back on a Shirt",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up the kit** — needle, matching thread (colour close to the shirt), "
            "scissors, the loose button.\n"
            "2. **Thread the needle and knot the end** — a double strand is stronger; "
            "a simple overhand knot holds it.\n"
            "3. **Mark the spot** — find where the button used to be. The fabric usually "
            "shows the marks. Don't guess.\n"
            "4. **Sew through each hole 4–6 times** — from underneath, up through one hole, "
            "down through the next. Keep the tension snug but not puckered.\n"
            "5. **Finish with a knot under the button** — three small stitches in place on "
            "the underside, then knot and cut. Pull to test before trusting it."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Needle safety:** stick the needle into a pincushion or folded paper "
            "between uses. Never leave a loose needle on soft furniture.\n"
            "- **Thread length:** arm's length is plenty. Very long thread tangles and "
            "can wrap fingers.\n"
            "- **Scissors:** cut away from the body, not towards."
        ),
        "parent_note_md": (
            "Sewing a button back on is a 10-minute skill that prevents discarding a good "
            "shirt. A teenager who can do it owns a small piece of repair independence that "
            "most of their peers — and many adults — can't match. The same basic technique "
            "extends to hemming, patching, and simple repairs."
        ),
    },
    {
        "slug": "unclog-drain-plunge-age13",
        "title": "Unclog a Drain or Plunge a Toilet",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Diagnose first** — slow drain = partial clog, try hot water and dish soap. "
            "Fully stopped = needs mechanical help.\n"
            "2. **Use a plunger properly** — flat-flanged plunger for toilets, cup plunger "
            "for sinks. Make a full seal; a leaky seal does nothing.\n"
            "3. **Push and pull forcefully** — 10–15 firm strokes. It's the suction pull, "
            "not the push, that dislodges the clog.\n"
            "4. **Hair is usually the culprit in bathroom drains** — remove the stopper, "
            "pull out the visible clump with a paper towel or wire hook.\n"
            "5. **Know when to stop and call** — if water is rising over the rim, if the "
            "clog persists after 10 minutes of work, or if there's sewage backflow, "
            "stop and get an adult."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Gloves and old clothes:** drain work is messy. Rubber gloves for anything "
            "bathroom-related.\n"
            "- **No chemical drain cleaners:** hazardous, often damage pipes, and mix badly "
            "with other cleaners. Plunger and patience first.\n"
            "- **Overflowing toilet:** turn off the shut-off valve behind the toilet "
            "(quarter-turn clockwise) before plunging a toilet that's close to the rim.\n"
            "- **Wash hands thoroughly** after any drain work. Soap, hot water, count to 20."
        ),
        "parent_note_md": (
            "Minor plumbing is the kind of task where a teenager can genuinely save the "
            "household a ₹500–1500 plumber call. More importantly, knowing the shut-off "
            "valve and the right first move prevents a small clog from becoming a flood. "
            "This is adulting fundamentals."
        ),
    },
    {
        "slug": "weekly-grocery-budget-age14",
        "title": "Do a Week's Grocery Shop Within a Budget",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plan the meals first** — 7 dinners, lunches, breakfasts. A meal plan is a "
            "shopping list in disguise.\n"
            "2. **Write the list by section** — produce, dairy, grains, pantry, "
            "cleaning. Matches how the shop is laid out; saves time and forgotten items.\n"
            "3. **Set the budget in advance** — if the family spends ₹3,000/week, "
            "that's the number. Everything below it is the challenge.\n"
            "4. **Track as they go** — phone calculator running. Running total after each "
            "aisle. Swap out or drop items if the total's creeping over.\n"
            "5. **Debrief at home** — what was expensive? Could a cheaper alternative work? "
            "What ran out mid-week? The next plan gets better from the review."
        ),
        "parent_note_md": (
            "Weekly shopping teaches budgeting, planning, and trade-offs in one exercise. "
            "A teenager who can plan meals, shop to a number, and review what worked is "
            "practising a grown-up version of financial competence — far more useful than "
            "abstract budgeting worksheets."
        ),
    },
    {
        "slug": "change-bulb-reset-breaker-age15",
        "title": "Change a Light Bulb and Reset a Tripped Breaker",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Match the bulb** — wattage and fitting (screw vs bayonet). Taking the "
            "old bulb to the shop is the safest way to get the right replacement.\n"
            "2. **Switch off at the wall** — never change a bulb with the switch on. "
            "For ceiling fixtures, switch off at the breaker if in doubt.\n"
            "3. **Let the bulb cool** — old bulb is hot. Two minutes to cool before touching.\n"
            "4. **Find the breaker box and learn the labels** — kitchen, bedrooms, AC, etc. "
            "Walk through each switch with a parent so they know what controls what.\n"
            "5. **Reset a tripped breaker correctly** — push it fully OFF first, then fully ON. "
            "Just jiggling it doesn't reset. If it trips again immediately, there's a fault — stop."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Electricity kills:** this is not a skill for showing off. Dry hands, dry floor, "
            "never touch both hands to metal parts at once.\n"
            "- **Breaker trips repeatedly:** do not keep flipping it. That is the breaker doing "
            "its job. Get an electrician.\n"
            "- **Smells, smoke, scorch marks:** stop. Get an adult. Do not investigate further.\n"
            "- **Water near electricity:** never reach for a breaker with wet hands or standing "
            "in water."
        ),
        "parent_note_md": (
            "Changing a bulb and resetting a breaker are the two most common home-electrical "
            "interventions an adult does. Knowing the safety rules, the breaker box layout, "
            "and when to stop and call is the real skill — not the physical action itself."
        ),
    },
    {
        "slug": "monthly-household-admin-age16",
        "title": "Manage Monthly Household Admin (Bills, Subscriptions)",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Make the list** — every recurring charge in one place. Electricity, gas, "
            "water, internet, mobiles, streaming, apps. Parent-led the first time.\n"
            "2. **Note the amount and the due date** — and which account it comes from. "
            "A simple spreadsheet or notes file is enough.\n"
            "3. **Audit every subscription** — is it still being used? Is there a cheaper "
            "plan? Is there an annual-vs-monthly saving? One hour of this typically saves "
            "₹500–2000/month.\n"
            "4. **Set calendar reminders** — 3 days before each due date. Missed bills "
            "incur late fees and damage credit records.\n"
            "5. **Review monthly** — one 20-minute slot at the start of each month. "
            "Check the total vs last month. Spot anything unusual."
        ),
        "parent_note_md": (
            "Household admin is one of the quiet skills that separates adults who feel in "
            "control of their life from those who feel chased by it. A 16-year-old who has "
            "owned even one cycle of bill-tracking, subscription auditing, and reminder-setting "
            "arrives at independent living years ahead of peers."
        ),
    },
]


# ---------------------------------------------------------------------------
# DIGITAL — one task per age 5–16 (all include safety_md)
# ---------------------------------------------------------------------------

DIGITAL_TASKS = [
    {
        "slug": "ask-before-pressing-button-age5",
        "title": "Ask a Grown-Up Before Pressing a Button You Don't Know",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Make the rule simple** — *If you don't know what it does, ask first.*\n"
            "2. **Show them the safe buttons** — power, volume, the remote basics. "
            "Green means go; red means stop and ask.\n"
            "3. **Reward the ask** — every time they come to check before pressing, "
            "say well done. The ask is the skill, not the button.\n"
            "4. **Never shame the mistake** — if they press something wrong, fix it "
            "calmly. Shame teaches hiding; calm teaches checking.\n"
            "5. **Extend it to keyboard shortcuts** — laptop keys that look blank or "
            "symbol-only are exactly the ones to ask about."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Unknown prompt on screen:** do not tap *OK*, *Yes*, or *Install*. "
            "Fetch an adult.\n"
            "- **App asking to be downloaded:** always ask first. Never install without "
            "a grown-up.\n"
            "- **Pop-ups and ads that look urgent:** they are designed to trick kids. "
            "Close the window or ask an adult."
        ),
        "parent_note_md": (
            "The *ask before pressing* habit at 5 is the seed of digital caution that "
            "protects a child from accidental purchases, malware installs, and dangerous "
            "settings for years. The rule is tiny; the lifelong dividend is large."
        ),
    },
    {
        "slug": "power-button-shutdown-age6",
        "title": "Find the Power Button and Shut the Device Down Properly",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find the button on each device** — tablet, laptop, TV, game console. "
            "Point to each one together.\n"
            "2. **Teach the two modes** — short press = sleep, long press = shutdown. "
            "Different devices behave differently; let them try both.\n"
            "3. **Use the proper menu option** — on a laptop or tablet, the proper way to "
            "shut down is through the menu, not by holding the power button. "
            "Practise both routes.\n"
            "4. **Save before shutdown** — any work, game save, drawing. Shutting down without "
            "saving loses it. Build the habit of checking.\n"
            "5. **Know when to force off** — if a device is truly frozen (screen not responding "
            "for over a minute), hold the power button 10 seconds. Last resort only."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Do not yank the charger or pull plugs while the device is running** — "
            "you can corrupt files or damage the battery.\n"
            "- **Hot device:** if a laptop or tablet is unusually hot, shut down properly and "
            "tell an adult. Don't keep using it.\n"
            "- **Water near electronics:** if there's any liquid nearby, power off first, "
            "move the device, then clean the liquid."
        ),
        "parent_note_md": (
            "Proper shutdown is the single most-missed digital habit in children. Force-off "
            "becomes a lifelong habit that damages devices and loses work. Ten minutes of "
            "teaching proper shutdown saves years of *why is this so slow?* frustration."
        ),
    },
    {
        "slug": "take-save-screenshot-age7",
        "title": "Take and Save a Screenshot",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the shortcut for each device** — phone (power + volume down), "
            "Windows (Win + PrtScn), Mac (Cmd + Shift + 3). Write them on a card by the computer.\n"
            "2. **Try it on something fun** — a game score, a drawing, a funny meme. "
            "Screenshots stick when they feel useful.\n"
            "3. **Find where it saved** — Pictures folder, Screenshots album, Photos app. "
            "The screenshot isn't done until they can find it.\n"
            "4. **Crop and rename it** — any basic tool works. Renaming makes it findable later; "
            "*IMG_20260418_1245.png* tells you nothing.\n"
            "5. **Send it somewhere** — email to themselves, send in a chat, paste into a doc. "
            "A screenshot unused is a screenshot wasted."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Never screenshot private information without permission** — passwords, "
            "credit cards, a friend's phone number. Screenshots are easy to forward.\n"
            "- **Think before sharing** — once a screenshot is sent, it can be forwarded "
            "anywhere. *Would I be fine with this being public?*\n"
            "- **Screenshots of chats:** the other person didn't consent. Think twice before "
            "sharing their words."
        ),
        "parent_note_md": (
            "Screenshots are the most basic document skill of the digital world. A 7-year-old "
            "who can take, find, rename, and share a screenshot is genuinely computer-literate "
            "in a way many adults aren't — and the privacy warnings go in at the same time "
            "as the shortcut."
        ),
    },
    {
        "slug": "type-name-sentence-age8",
        "title": "Type Your Name and a Short Sentence on a Keyboard",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the home row** — left hand on A-S-D-F, right hand on J-K-L-;. "
            "F and J have the little bumps. Finger placement is a real thing, not a rule made up to be annoying.\n"
            "2. **Start with name and sentence** — *My name is [name]. I am [age] years old.* "
            "Short, meaningful, repeated.\n"
            "3. **Teach shift for capitals** — hold with the pinky on the opposite hand while "
            "the other hand types. Not caps lock for a single letter.\n"
            "4. **Use a free typing game** — the first fluency comes from games, not drills. "
            "15 minutes three times a week.\n"
            "5. **No looking at the hands** — the leap from hunt-and-peck to touch typing is "
            "just *stop looking down*. Hard at first, fast after two weeks."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Posture:** back straight, feet flat, screen at eye level. Bad posture now "
            "turns into neck and wrist pain later.\n"
            "- **Take a break every 20 minutes** — look at something far away for 20 seconds. "
            "Eye strain is real.\n"
            "- **Typing on shared devices:** always log out of your accounts when done — "
            "especially in schools and libraries."
        ),
        "parent_note_md": (
            "Touch typing is one of the highest-ROI skills a child can learn — it compounds "
            "every day of school, college, and work life. Children who learn it by 10 "
            "write faster, edit more, and think differently about writing because the "
            "keyboard stops being friction."
        ),
    },
    {
        "slug": "photos-shared-beyond-sender-age9",
        "title": "Understand That Photos Can Be Shared Beyond the Sender",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Ask the grandma test** — before sending any photo, *Would I be okay if Grandma "
            "and my teacher both saw this?* If not, don't send.\n"
            "2. **Show how screenshots work** — any photo sent can be captured by the receiver. "
            "*Disappearing* photos aren't really disappearing.\n"
            "3. **Talk about group chats** — a photo sent to one friend can be forwarded to 50 "
            "people in an hour. Demonstrate with a harmless photo and permission.\n"
            "4. **Never photograph someone without asking** — even funny candids. Their face, "
            "their choice.\n"
            "5. **Know the undo limits** — once it's sent, you cannot un-send. The only "
            "control is *don't send*."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Never share photos in underwear or swimwear** — not even with friends. "
            "Not even in private. Full stop.\n"
            "- **Do not send photos to strangers** — no matter what they promise or ask.\n"
            "- **If someone asks for a photo that feels wrong, tell a trusted adult.** "
            "Immediately. No trouble for the child; the adult handles it.\n"
            "- **Location in photos:** some phones embed GPS in photos. Check the camera "
            "settings with a parent; turn off location tagging for shared photos."
        ),
        "parent_note_md": (
            "The *photos can travel* lesson at 9 is the foundation of every later online-safety "
            "conversation. Children who internalise the grandma test early make safer choices "
            "as teens, when the stakes rise sharply. This is one of the most important "
            "digital-safety conversations a parent will have."
        ),
    },
    {
        "slug": "compose-polite-email-age10",
        "title": "Compose and Send a Polite Email",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set the subject line** — specific, not blank. *Question about Thursday's homework* "
            "beats *Hi*. Teachers read by subject line; so does everyone else.\n"
            "2. **Use a greeting** — *Dear Ms. Kaur,* or *Hi Ravi,* depending on who. "
            "Never start with just the message.\n"
            "3. **Say why you're writing in the first line** — *I'm writing to ask about X.* "
            "Respect the reader's time.\n"
            "4. **Sign off properly** — *Thanks, [Name]* or *Kind regards, [Name].* "
            "Blank end is rude; so is just a first name with no thanks.\n"
            "5. **Re-read once before sending** — for typos, tone, and missing attachments. "
            "The 10-second re-read saves most embarrassments."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Check the recipient:** a misaddressed email can leak private information. "
            "Look before hitting send.\n"
            "- **Never email sensitive details** — home address, passwords, ID numbers. "
            "Email is not private.\n"
            "- **Spam and phishing:** emails asking for logins, money, or urgent action are "
            "almost always scams. Don't click; show an adult.\n"
            "- **Reply-all is not always your friend** — a personal reply to *the whole class* "
            "can be embarrassing. Check before clicking."
        ),
        "parent_note_md": (
            "Email is the single most-used business communication tool and still dominant "
            "in schools, colleges, and jobs. A 10-year-old who can write a clear, polite, "
            "subject-lined email stands out to teachers — and has a head start on one of "
            "the most enduring professional skills."
        ),
    },
    {
        "slug": "turn-on-2fa-age11",
        "title": "Turn On Two-Factor Authentication for One Account",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick an important account** — email first. Email is the key to every other "
            "account's password reset; protect it.\n"
            "2. **Find the security settings** — every major service has them. *Settings → "
            "Security → 2-Step Verification.*\n"
            "3. **Prefer an authenticator app** — Google Authenticator or similar — over SMS. "
            "SMS can be intercepted; apps can't.\n"
            "4. **Save the backup codes** — every 2FA setup gives you recovery codes. "
            "Write them on paper and store them somewhere a parent knows.\n"
            "5. **Test it by logging out and back in** — does it work? Can you find the code "
            "quickly? Smooth now saves panic later."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Never share a 2FA code** — not even with *support staff*. Real support never asks.\n"
            "- **Lose your phone?** backup codes are your way in. Store them somewhere physical, "
            "not just on the phone you might lose.\n"
            "- **Authenticator app itself needs protection** — set a passcode or face unlock "
            "on the phone.\n"
            "- **Pair it with a strong password** — 2FA is a second layer, not a replacement "
            "for a good password."
        ),
        "parent_note_md": (
            "Two-factor authentication is the single biggest reduction in account hijacking "
            "risk a person can make. An 11-year-old who turns it on for their email has "
            "immunised themselves against ~99% of casual account takeovers — a huge protection "
            "for essentially zero daily friction."
        ),
    },
    {
        "slug": "spot-phishing-age12",
        "title": "Spot a Phishing Message",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the urgency tell** — *Your account will be deleted in 24 hours!* is "
            "almost always a scam. Real organisations don't work like that.\n"
            "2. **Check the sender address** — *netflix-support@unknownsite.xyz* is not Netflix. "
            "Hover (or long-press) to see the real address.\n"
            "3. **Never click links in suspicious emails** — type the URL directly into the "
            "browser yourself. Scammers fake the visible text, not the destination.\n"
            "4. **Spot the grammar and spelling** — small errors in an apparently-official "
            "message are a flag. Real corporate comms are proofread.\n"
            "5. **When in doubt, ask** — forward to a parent or an adult. Thirty seconds of "
            "asking saves a compromised account."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Don't reply or engage** — even *unsubscribe* on a scam email tells them the "
            "address is live. Delete; block.\n"
            "- **Report it in your email client** — most have a *Report phishing* option. Use it.\n"
            "- **Already clicked?** — change the password immediately from a different device. "
            "Then tell an adult. Quick action limits damage.\n"
            "- **Never send money or gift cards** based on an urgent email or message. Scams "
            "always route through untraceable payment methods."
        ),
        "parent_note_md": (
            "Phishing is the single most common cyber-attack and the one children encounter "
            "regularly through email, SMS, and game-platform messages. A 12-year-old who has "
            "internalised the urgency-tell, sender-check, and don't-click rules is protected "
            "against the majority of scams they'll meet."
        ),
    },
    {
        "slug": "set-screen-time-limits-age13",
        "title": "Set Up and Respect Your Own Screen-Time Limits",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Audit first** — every phone has a screen-time dashboard. *Settings → Digital "
            "Wellbeing* (Android) or *Screen Time* (iOS). Look at the last week honestly.\n"
            "2. **Pick one app to limit** — the one that shocked them. 60 min/day to start.\n"
            "3. **Set a wind-down for sleep** — phone on black-and-white or do-not-disturb "
            "from 9pm. Sleep is where screens do the most silent damage.\n"
            "4. **Plan screen-free windows** — meal times, first 30 min after waking, last 60 min "
            "before bed. Not *no screens ever* — targeted boundaries.\n"
            "5. **Review weekly** — did the limits hold? Did they feel good or irritating? "
            "Adjust. Good limits are the ones they keep."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Screens and sleep:** the single worst screen habit is scrolling in bed. "
            "It predicts mood and school performance better than any other variable.\n"
            "- **Set notifications to summary mode** — getting pinged every few minutes "
            "destroys focus.\n"
            "- **Overriding your own limits** is the warning sign. If *just five more minutes* "
            "happens every day, the app probably needs uninstalling, not limiting.\n"
            "- **Private browsing doesn't hide screen time** — the dashboard sees it. Don't rely "
            "on it as a workaround."
        ),
        "parent_note_md": (
            "Self-regulated screen time at 13 is one of the highest-impact habits a teenager "
            "can build. Research links late-night screen use to anxiety, poor sleep, and lower "
            "school performance. A teen who owns the habit — not has it imposed — is learning "
            "self-regulation, not rebellion."
        ),
    },
    {
        "slug": "ai-assistant-verify-age14",
        "title": "Use an AI Assistant Responsibly — Verify Before Trusting",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know what AI does** — it produces plausible-sounding text based on patterns. "
            "It is not a search engine; it does not check facts.\n"
            "2. **Never copy directly into homework** — most schools detect it, and it doesn't "
            "teach anything. Use AI as a tutor, not an answer machine.\n"
            "3. **Always verify facts elsewhere** — any name, date, statistic, or quote the AI "
            "gives. AIs confidently make things up (this is called *hallucination*).\n"
            "4. **Use it for brainstorming and explanations** — *Explain this concept in 3 "
            "different ways* is a great use. *Write my essay* is a terrible one.\n"
            "5. **Keep private info out** — don't paste in real names, addresses, passwords, or "
            "family details. AI services log conversations."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **AI is wrong a lot** — confidently. Medical, legal, or safety advice from AI "
            "must be verified against real sources before acting on it.\n"
            "- **AI image generation:** never make fake images of real people without consent. "
            "In many places it's illegal, and always it's unkind.\n"
            "- **Don't believe it about you** — if an AI describes a person by name, "
            "it may be hallucinating. Especially for real people, it invents plausible details.\n"
            "- **Signs of overreliance:** feeling unable to write, think, or solve without AI. "
            "Take regular AI-free days."
        ),
        "parent_note_md": (
            "AI assistants are going to be a lifelong tool, and responsible use is a distinct "
            "skill — much like responsible search or responsible calculator use in past "
            "generations. Teenagers who learn verification and boundaries now enter adult "
            "work ahead of peers who either avoid AI or surrender to it."
        ),
    },
    {
        "slug": "lock-down-app-privacy-age15",
        "title": "Lock Down Privacy Settings on Every App You Use",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Make the list** — every app on the phone. All of them. Social media, games, "
            "shopping, messaging.\n"
            "2. **For each one, find the privacy settings** — usually *Settings → Privacy* or "
            "*Account → Privacy*. 5–10 minutes per app.\n"
            "3. **Default to *friends only* or *private*** — profile, posts, location, activity "
            "status. Public is only for things they actively want public.\n"
            "4. **Turn off location sharing globally** — except maps while actually navigating. "
            "Most apps don't need it, and many sell it.\n"
            "5. **Review app permissions** — microphone, camera, contacts, location. Revoke "
            "anything that doesn't need what it's asking for."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Location leaks are dangerous** — stalkers, scammers, and even predictable "
            "advertising all use location data. Turn it off wherever possible.\n"
            "- **Friend requests from strangers** — block without guilt. Real friends don't "
            "need to friend-request you on an app you've never used.\n"
            "- **Old accounts you don't use** — delete them, don't just log out. Breaches of "
            "forgotten accounts are a leading cause of identity theft.\n"
            "- **Search engines:** your activity is logged. Incognito mode hides it from the "
            "browser, not from the search engine."
        ),
        "parent_note_md": (
            "A 15-year-old who has manually locked down their app privacy has done something "
            "95% of adults have never done — and they're protecting themselves from the main "
            "risks of the social-media era: stalking, doxing, data sale, and targeted "
            "manipulation. One slow afternoon; lifelong benefit."
        ),
    },
    {
        "slug": "audit-online-presence-age16",
        "title": "Audit Your Online Presence and Clean Up Old Content",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Google yourself** — *Name*, *name + school*, *name + city*. See what "
            "strangers see. Include image search.\n"
            "2. **Review every old post** — on every platform. Anything cringe, harsh, or "
            "private from a younger self, delete.\n"
            "3. **Lock down or delete old accounts** — the one from when they were 11, "
            "the abandoned one, the forgotten one. Each is a leak waiting to happen.\n"
            "4. **Curate a professional version** — a clean profile photo, a simple bio, "
            "private settings. Future employers and universities will look.\n"
            "5. **Set a reminder to re-audit every 6 months** — the internet doesn't rest. "
            "Small, regular clean-ups beat panic sweeps later."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Images spread fast** — deleting a post doesn't delete the screenshots others "
            "have taken. Think about what went up before you worry about what comes down.\n"
            "- **Old email addresses in data breaches** — check haveibeenpwned.com (with a "
            "parent) to see if any password has leaked. Change those passwords.\n"
            "- **Photos of others** — if you post a photo with friends in it, they have a "
            "say. Ask before posting anything recognisable.\n"
            "- **Right to be forgotten:** in some countries you can legally request search "
            "engines to remove specific results. Know this is an option."
        ),
        "parent_note_md": (
            "A conscious online presence is no longer optional. University admissions, "
            "employers, scholarship committees, and even some landlords now run basic "
            "web searches on names. A 16-year-old who has audited and cleaned up their "
            "presence before it matters — rather than after — is thinking like an adult."
        ),
    },
]


# ---------------------------------------------------------------------------
# NAVIGATION — one task per age 5–16 (all include safety_md)
# ---------------------------------------------------------------------------

NAVIGATION_TASKS = [
    {
        "slug": "point-front-door-age5",
        "title": "Point to the Front Door From Inside the Home",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Stand in every room together** — bedroom, kitchen, bathroom. "
            "*Point to the front door.* Do they get it right?\n"
            "2. **Talk about walls** — *The front door is that way, on the other side of this wall.*\n"
            "3. **Close their eyes, turn them around** — *Point to the door.* "
            "Harder without visual cues. Build mental map.\n"
            "4. **From the neighbour's house or the garden** — *Which of these houses is ours? "
            "Where is the door?*\n"
            "5. **Play *how would a fire escape go?*** — *If we had to leave the house now, "
            "which way would we go?* Foundational safety thinking."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Fire route:** agree a family escape route. The child should know it from "
            "every room.\n"
            "- **Meeting point outside:** choose a safe spot the family meets if there's an "
            "emergency evacuation — the front gate, the tree across the road.\n"
            "- **Never go back in:** once outside in an emergency, never go back for anything. "
            "Not a toy, not a pet, not a favourite book."
        ),
        "parent_note_md": (
            "Spatial awareness of the home is the first layer of real-world navigation — "
            "and it doubles as foundational fire safety. A 5-year-old who can point to the "
            "front door from every room has a mental map of their home, not just a memorised "
            "list of rooms."
        ),
    },
    {
        "slug": "tell-adult-stranger-age6",
        "title": "Tell a Trusted Adult if a Stranger Approaches",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name trusted adults** — parents, grandparents, teacher, named neighbour. "
            "Be specific; *adults* is too vague.\n"
            "2. **Rehearse the response** — *Stop, don't go with them, walk to a trusted adult, "
            "tell.* Walk through it physically.\n"
            "3. **Practise the *what if*** — *What if they say Mummy sent them? What if they "
            "offer a sweet?* The correct answer is always: tell a trusted adult first.\n"
            "4. **Teach the code word** — a family password. Only a real emergency pickup "
            "would know it.\n"
            "5. **Celebrate telling** — any time they come to you with *someone I didn't know "
            "talked to me*, thank them. Positive reinforcement prevents hiding."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Nobody legitimate needs a child to keep a secret from parents.** That is "
            "the single biggest red flag.\n"
            "- **Loud and public is safer** — if a stranger won't let them go, *shout* is a "
            "better instinct than *run silently.*\n"
            "- **Safe places:** shops, restaurants, offices, uniformed adults (police, shop "
            "staff). Teach them to walk into these if scared.\n"
            "- **Mummy/Daddy sent me** without the code word = it's a lie. Walk away."
        ),
        "parent_note_md": (
            "Stranger awareness needs to be handled without scaring the child — "
            "statistically, strangers are a rare threat. The real skill is *tell a trusted "
            "adult*, which covers everything from stranger encounters to being hurt by "
            "someone they know. Practising the code word and the *tell* habit is the goal."
        ),
    },
    {
        "slug": "walk-correct-side-pavement-age7",
        "title": "Walk on the Correct Side of the Pavement",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the basic rule** — walk on the inside (wall side) of the pavement, "
            "not the edge. The traffic-side edge is the danger zone.\n"
            "2. **Walk toward oncoming traffic** — on roads without pavements, face the "
            "traffic so you can see cars coming and step aside.\n"
            "3. **Let faster walkers pass** — step slightly to one side when you hear footsteps "
            "behind. Basic pavement etiquette.\n"
            "4. **Hold hands near busy roads** — under 8, always. Not a negotiation.\n"
            "5. **Check before stepping off a curb** — look both ways, even on a one-way street. "
            "Cyclists and e-bikes don't follow arrows."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Headphones and distraction:** cars are very quiet from behind. Take one "
            "earbud out when near traffic.\n"
            "- **Parked cars are a threat** — they can open doors or pull out suddenly. "
            "Walk at least one pace away from the car row.\n"
            "- **Weather:** rain makes roads and pavements slippery and reduces driver visibility. "
            "Bright or reflective clothing helps.\n"
            "- **Crossing:** always at a designated crossing where possible. Eye contact with "
            "drivers before stepping off."
        ),
        "parent_note_md": (
            "Pavement awareness is the first real road-safety skill. A 7-year-old who walks "
            "on the inside of the pavement, faces traffic on roads without pavements, and "
            "makes eye contact with drivers before crossing is significantly safer than "
            "peers who have never been explicitly taught. Accidents drop with skill."
        ),
    },
    {
        "slug": "read-bus-metro-map-age8",
        "title": "Read a Simple Bus or Metro Map",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a real map** — local bus or metro. Print it or use a phone.\n"
            "2. **Find home and school** — can they locate both stations? "
            "Use finger-tracing to travel the route.\n"
            "3. **Teach colours = lines** — each line is a different colour. Changes happen at "
            "stations where lines cross.\n"
            "4. **Plan a pretend journey** — *We want to go from the market to the zoo. "
            "Which line? Where do we change? How many stations?*\n"
            "5. **Count the stations** — from A to B. Knowing how many stops to listen for "
            "is a real navigation skill."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Platform edge:** stand behind the yellow line. Always. Trains create a strong "
            "wind-pull as they arrive.\n"
            "- **Mind the gap** — stepping between the train and the platform. Watch every time.\n"
            "- **Lost:** stay in one safe place. Tell a staff member in uniform (not a stranger). "
            "Most stations have information desks.\n"
            "- **Crowded carriages:** stay close to the adult; no wandering. Hands on the rail "
            "or adult."
        ),
        "parent_note_md": (
            "Reading a transit map is a rite of passage for urban independence. An 8-year-old "
            "who can find home, school, and a destination on a metro map understands their "
            "city in a new way — and is ready for the next steps toward travelling alone."
        ),
    },
    {
        "slug": "find-building-by-signage-age9",
        "title": "Find a Named Building by Reading Signage",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a destination** — a shop, library, clinic, post office. Something "
            "they haven't been to 100 times.\n"
            "2. **Give the name only** — no directions, no pointing. They have to find it.\n"
            "3. **Read signs systematically** — building names, house numbers, shop signs, "
            "direction signs with arrows.\n"
            "4. **Use landmarks to confirm** — *the bakery is next to the green-gated temple.* "
            "Real-world cross-referencing.\n"
            "5. **Ask if stuck** — part of the skill is knowing who to ask. A shop assistant, "
            "a uniformed guard, an older person waiting at the bus stop. Not a random person "
            "walking past."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Stay on main streets** — not through alleys or parking lots, even as shortcuts.\n"
            "- **Ask safe people:** uniformed staff, shop owners, clearly-working adults. "
            "Not someone already paying them attention.\n"
            "- **Phone charged, location enabled** — this is the one time location sharing "
            "with a parent is appropriate. Makes *lost* into *findable*.\n"
            "- **Agreed check-in time** — if not at the destination by a set time, they call. "
            "Parent knows to check too."
        ),
        "parent_note_md": (
            "Navigating to a named building is one of the first real solo-navigation skills. "
            "A 9-year-old who can do it competently — reading signs, using landmarks, asking "
            "the right people — is ready for slightly bigger independent journeys."
        ),
    },
    {
        "slug": "use-compass-find-north-age10",
        "title": "Use a Compass to Find North",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a real compass** — a cheap base-plate compass. Phone compasses work but "
            "aren't as satisfying for learning.\n"
            "2. **Let the needle settle** — hold flat, away from metal and phones. The red "
            "end points to magnetic north.\n"
            "3. **Orient the map** — when the compass is placed on a map and north-aligned, "
            "the map now matches the real world around you.\n"
            "4. **Find the four directions from where they stand** — *Point north. Now east. "
            "Now south-west.* Build intuition, not just rote.\n"
            "5. **Walk a bearing** — parent picks a landmark, reads its bearing on the compass, "
            "child walks to it without looking at the landmark, only the needle."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Compasses lie near metal** — cars, fences, steel rebar. Step clear before "
            "taking a reading.\n"
            "- **Compass plus map plus phone:** three layers is safer than one. Don't "
            "depend entirely on the phone.\n"
            "- **Know the local north:** urban landmarks can anchor direction — *the river is "
            "south, the hills are north.* Local geography + compass is the combination."
        ),
        "parent_note_md": (
            "Compass literacy is quietly underrated — it's rarely life-critical in a city, "
            "but it builds spatial reasoning and a deep understanding of orientation that "
            "transfers to reading maps, navigating unfamiliar places, and thinking geographically."
        ),
    },
    {
        "slug": "one-transit-stop-alone-age11",
        "title": "Travel One Transit Stop Alone (With Check-In)",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a safe, short route** — one bus stop or one metro station. Familiar "
            "line, daytime, low-crowd time.\n"
            "2. **Full dry run together** — ride it together the day before. They lead; "
            "you follow and observe.\n"
            "3. **Phone fully charged, maps open** — and a parent's number on a locked-screen "
            "contact card.\n"
            "4. **Check-in calls agreed** — *Call me when you board. Call me when you arrive.* "
            "Two touchpoints, parent stays ready.\n"
            "5. **Debrief honestly afterwards** — what felt scary? What went well? "
            "What to do differently next time? This is the real growth."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Never leave with anyone who wasn't pre-agreed** — even if someone says *Mum "
            "called me to pick you up.* Code word or no.\n"
            "- **Missed the stop?** stay calm, get off at the next one, call a parent, wait in "
            "the station. Don't try to fix it alone.\n"
            "- **Talking to strangers on transit:** polite but brief. No sharing where they "
            "live or where they're going alone.\n"
            "- **Feel unsafe:** move to a busier carriage, sit near the driver, or get off and "
            "call. Trust the instinct."
        ),
        "parent_note_md": (
            "The first solo transit ride is a huge milestone — and if it's one stop with a "
            "dry run and phone check-ins, it's a safe and confidence-building one. Pre-teens "
            "who have done it once stop being afraid of public transport; the fear was "
            "always of the unknown."
        ),
    },
    {
        "slug": "multi-transfer-transit-age12",
        "title": "Navigate a Multi-Transfer Transit Journey",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plan together first** — a journey with one or two transfers. Use a real "
            "route planner.\n"
            "2. **Write the steps as a list** — *Take Line 1 to Station X, transfer to Line 3, "
            "get off at Station Y.* Paper or phone; the list is the plan.\n"
            "3. **Time each leg** — add 5 minutes per transfer for buffer. Real journeys run late; "
            "buffers save missed connections.\n"
            "4. **Identify fallback options** — *If we miss the transfer, the next train is in "
            "15 min.* Knowing the fallback is the real confidence.\n"
            "5. **Run it solo with a parent tracking via phone** — the safety net is invisible "
            "but real. Debrief at the other end."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Transfer stations are crowded** — stay aware, keep bags in front, phone in pocket.\n"
            "- **Wrong train or wrong platform** — get off at the next safe station, check the "
            "map, re-route. Don't panic-improvise.\n"
            "- **Late night avoid** — plan trips to finish before dark or before off-peak hours "
            "when stations empty out.\n"
            "- **Pickpockets target the distracted** — no phone out while walking between lines. "
            "Check routes before entering the crowd."
        ),
        "parent_note_md": (
            "Multi-transfer navigation is where a teenager genuinely starts to own their "
            "city. It combines planning, time estimation, stress management, and problem-solving "
            "into one compact task. A pre-teen who has done it three times is ready for "
            "unfamiliar cities as a teen."
        ),
    },
    {
        "slug": "cycle-safely-public-road-age13",
        "title": "Cycle Safely on a Public Road",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Helmet fit first** — two fingers above eyebrows, straps V'd under each ear, "
            "chin strap firm but breathable. A loose helmet is no helmet.\n"
            "2. **Bike check** — brakes firm, tyres pumped, lights working, chain clean. "
            "Every ride starts with a 30-second check.\n"
            "3. **Quiet roads first** — residential streets, daytime, dry weather. Confidence "
            "before traffic.\n"
            "4. **Hand signals** — right turn, left turn, stopping. Practise them until "
            "automatic; you lose balance if signalling is unfamiliar.\n"
            "5. **Ride defensively** — assume drivers haven't seen you. Make eye contact at "
            "junctions. Bright clothes, lights on even in daytime if dull."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Helmet, always, every ride** — even for 5 minutes. Most cycling deaths involve "
            "no helmet.\n"
            "- **Lights at dawn, dusk, and after dark** — white front, red rear. Non-negotiable.\n"
            "- **No headphones while cycling** — ears are the second-most-important navigation "
            "tool after eyes.\n"
            "- **Left side of the road in India / UK; right side in USA / EU** — learn your "
            "country's rules, including junctions and roundabouts.\n"
            "- **Avoid lorries and buses** — give them huge space. Their blind spots are enormous.\n"
            "- **Phone away while cycling** — never check messages. Pull over completely to use it."
        ),
        "parent_note_md": (
            "Cycling on public roads is one of the biggest independence leaps a teenager takes — "
            "and statistically one of the riskier ones if done badly. Proper gear, defensive "
            "riding, and eye contact with drivers reduce accident rates massively. Teach the "
            "skill; don't forbid the activity."
        ),
    },
    {
        "slug": "day-trip-unfamiliar-area-age14",
        "title": "Plan and Take a Day Trip to an Unfamiliar Area",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a destination with 1–2 friends** — a park, museum, market, town "
            "they haven't been to. Parental approval first.\n"
            "2. **Plan the full journey** — departure time, transit routes, arrival time, "
            "lunch spot, return time. On paper or phone — *the plan*.\n"
            "3. **Budget the day** — transit, food, any entry fees. Carry a small buffer for "
            "emergencies.\n"
            "4. **Agree check-ins with parents** — departure, arrival, lunch, return-journey-started. "
            "Four touchpoints.\n"
            "5. **Debrief** — what went to plan, what didn't, what would they change? "
            "Every trip is a mini-project they run."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Phone charged; powerbank or charger in bag** — a dead phone on a day trip is "
            "a serious problem.\n"
            "- **Meeting points:** agreed places where the group meets if separated. Station "
            "gates work well.\n"
            "- **Emergency money on the person** — not in a bag that could be stolen.\n"
            "- **Trust the gut** — if a situation feels off (strange offer, unsafe alley, person "
            "who won't leave them alone), leave immediately. Call a parent.\n"
            "- **Know the return window** — last train home, closing of last bus, etc. "
            "Being stranded is avoidable; plan for it."
        ),
        "parent_note_md": (
            "A planned day trip with friends is one of the biggest leaps in teenage "
            "independence — and if it's planned properly, one of the safest. The planning "
            "process is the real skill: breaking a goal into journey legs, managing time, "
            "anticipating problems. This generalises to every adult project."
        ),
    },
    {
        "slug": "intercity-train-bus-alone-age15",
        "title": "Book and Take an Intercity Train or Bus Alone",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Research options** — which operator, which times, cost, journey duration. "
            "Compare 2–3 options.\n"
            "2. **Book online** — account setup, payment, seat selection. Screenshot the "
            "confirmation. Note the PNR/booking reference.\n"
            "3. **Arrival buffer** — for trains, 30–45 min before departure; for buses, 20 min. "
            "Rushing an intercity journey means missing it entirely.\n"
            "4. **Know the platform or bay** — check the boards on arrival; ask staff if unclear. "
            "Don't guess and hope.\n"
            "5. **Contact the person at the other end** — confirm pickup, agree plan B if "
            "anything changes. Intercity journeys often run late; stay in touch."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Luggage:** one hand on it at all times at stations. Never leave it unattended, "
            "even *for a second*.\n"
            "- **Long journeys:** food, water, phone charger, some cash. A bad situation "
            "without these is worse than one with.\n"
            "- **Stranger conversations:** polite, short, don't share the destination or who's "
            "waiting. Travelling alone is not something to advertise.\n"
            "- **Late-night arrivals:** pre-arrange pickup — don't wait alone in a deserted "
            "station at midnight.\n"
            "- **Ticket, ID, boarding pass:** keep together in one zipped inner pocket. "
            "Losing one of them makes the journey much harder."
        ),
        "parent_note_md": (
            "The first solo intercity journey is a genuine adult skill — booking, timing, "
            "managing luggage, handling delays. A 15-year-old who has done it once, with "
            "parental support in the background, arrives at university or work travel already "
            "confident instead of anxious."
        ),
    },
    {
        "slug": "navigate-airport-age16",
        "title": "Navigate an Airport from Check-in to Boarding",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Online check-in** — 24 hours before. Download the boarding pass to the "
            "phone wallet. Saves check-in queue time.\n"
            "2. **Arrive early** — international: 3 hours before; domestic: 2 hours. "
            "Airports punish lateness brutally.\n"
            "3. **Security flow** — liquids under 100ml in a clear bag, laptop out, shoes and "
            "belts depending on airport. Know before the queue, not in it.\n"
            "4. **Find the gate** — gate number on departure board. Walking distance to some "
            "gates is 20+ minutes. Factor it in.\n"
            "5. **Boarding** — listen for announcements by seat row or zone. "
            "Don't queue too early; the plane won't leave without you."
        ),
        "safety_md": (
            "## Safety first\n\n"
            "- **Never leave bags unattended** — airports have strict security rules. "
            "Unattended bags get destroyed.\n"
            "- **Watch the phone and passport** — the two most lost items in airports. "
            "Zipped inner pocket, check every 30 minutes.\n"
            "- **No joking about security** — any mention of *bomb*, *weapon*, etc., even "
            "as a joke, will have them removed from the flight.\n"
            "- **Stay with group in crowds** — busy airports separate families easily. "
            "Agree a meeting point (e.g. departure gate) if anyone gets separated.\n"
            "- **Unknown substance offered:** never accept food, drinks, or parcels from "
            "strangers. Do not carry anything for someone else through security."
        ),
        "parent_note_md": (
            "Airports are a surprising test of independence — a mix of bureaucracy, "
            "time management, crowd navigation, and rule-following. A 16-year-old who has "
            "navigated one confidently is ready for international travel, exchange programmes, "
            "and university abroad."
        ),
    },
]


# ---------------------------------------------------------------------------
# FINANCIAL — one task per age 5–16
# ---------------------------------------------------------------------------

FINANCIAL_TASKS = [
    {
        "slug": "coins-vs-notes-age5",
        "title": "Recognise the Difference Between Coins and Notes",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Lay out real money** — a mix of coins and small notes. Not toy money; "
            "real is more memorable.\n"
            "2. **Sort them into two piles** — coins here, notes there. Let them do the sorting.\n"
            "3. **Name each denomination** — *This is a ₹10 coin. This is a ₹20 note.* "
            "Introduce two at a time, don't overwhelm.\n"
            "4. **Coin vs note test** — put one face-down. *Is it a coin or a note?* "
            "Feel, weight, shape give it away.\n"
            "5. **Big number doesn't mean big money** — a ₹10 coin is worth less than a ₹500 note. "
            "This is a subtle but important early lesson."
        ),
        "parent_note_md": (
            "Money recognition is the foundational financial literacy skill. A 5-year-old "
            "who can sort coins from notes, name the denominations, and understand that size "
            "doesn't equal value has taken the first real step toward understanding money "
            "as a system."
        ),
    },
    {
        "slug": "count-change-to-10-age6",
        "title": "Count Small Change Up to 10",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use small coins only** — ₹1, ₹2, ₹5. Enough to make combinations under 10.\n"
            "2. **Start with same-denomination stacks** — *Five one-rupee coins. How much?* "
            "Counting identical coins is easier than mixing.\n"
            "3. **Mix two denominations** — *Two ₹2 coins and three ₹1 coins. How much?* "
            "They count by ₹2s, then add the ₹1s.\n"
            "4. **Make change the goal** — *I give you a ₹10 note; you give me a ₹5 bar of "
            "chocolate. What's my change?* Subtraction in context.\n"
            "5. **Let them pay** — at a small shop. Count the coins into the cashier's hand. "
            "Receive change. Verify it's correct."
        ),
        "parent_note_md": (
            "Counting small change involves addition, subtraction, and place-value in one "
            "real-world package. A 6-year-old who can do it at a shop has graduated from "
            "abstract arithmetic to lived mathematics — the transition that makes or breaks "
            "later maths confidence."
        ),
    },
    {
        "slug": "pay-at-till-count-change-age7",
        "title": "Pay at a Till and Count Your Change",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Let them hold the money** — their own small budget (₹20–50) for one shop visit.\n"
            "2. **Read the price tag** — before going to the till. *This is ₹35.* Know the "
            "number before paying.\n"
            "3. **Hand over money and wait** — don't rush the cashier. Receive the change in "
            "their own hand.\n"
            "4. **Count the change carefully** — before leaving the till. *I gave ₹50, the item "
            "was ₹35, so I should get ₹15 back.* Verify.\n"
            "5. **Keep the receipt** — show the parent at home. Double-check the arithmetic. "
            "Cashiers make mistakes too."
        ),
        "parent_note_md": (
            "Paying at a till and counting change is a rite of passage in financial "
            "independence. A 7-year-old who has done it 20 times is not intimidated by money "
            "transactions — a confidence that carries into adult banking, negotiations, "
            "and commerce."
        ),
    },
    {
        "slug": "save-piggy-bank-goal-age8",
        "title": "Save for a Small Goal in a Piggy Bank",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a real goal** — something they want, priced between ₹200–500. "
            "Too expensive is discouraging; too cheap is meaningless.\n"
            "2. **Calculate the timeline** — weekly pocket money divided into the goal. "
            "*₹30 a week; ₹300 needed; about 10 weeks.*\n"
            "3. **Use a visible container** — clear jar beats opaque piggy bank. Seeing the "
            "money grow is part of the reward.\n"
            "4. **Track on paper** — every deposit in a small notebook. Running total. "
            "Teaches record-keeping.\n"
            "5. **Resist the spend** — the real lesson is walking past something cheaper and "
            "saying *no, I'm saving for X*. Name the feeling: this is delayed gratification."
        ),
        "parent_note_md": (
            "Saving for a specific goal is where financial discipline begins. An 8-year-old "
            "who has completed one full save-and-buy cycle has experienced delayed "
            "gratification — one of the single strongest predictors of lifelong financial "
            "and personal success."
        ),
    },
    {
        "slug": "wants-vs-needs-age9",
        "title": "Tell the Difference Between a Want and a Need",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define the two** — need = something that keeps you alive, healthy, or "
            "meeting obligations. Want = everything else, however nice.\n"
            "2. **Sort 10 items together** — food, new video game, school shoes, fancy backpack, "
            "medicine, latest phone, water, cinema ticket. Pile them as need / want.\n"
            "3. **Catch the tricky ones** — phone can be either. Shoes are a need; branded "
            "shoes are a want. The principle is more important than the label.\n"
            "4. **Apply to their own wishlist** — go through the things they've been asking for. "
            "Which are needs? Which are wants? Honest only.\n"
            "5. **Discuss family spending** — not all wants are bad. Families need some joy "
            "spending. But being able to see the difference is the skill."
        ),
        "parent_note_md": (
            "The want/need distinction is the single most important concept in personal "
            "finance. Adults who never learned it end up over-borrowing for wants they "
            "mistake for needs. A 9-year-old who can sort honestly has started a framework "
            "that pays for the rest of their life."
        ),
    },
    {
        "slug": "compare-unit-prices-age10",
        "title": "Compare Unit Prices to Find the Better Deal",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find two versions of the same product** — different sizes. Toothpaste, "
            "washing powder, rice. Bigger isn't always cheaper per unit.\n"
            "2. **Teach unit price** — price divided by quantity. *₹240 for 600g = ₹0.40 per gram. "
            "₹150 for 300g = ₹0.50 per gram.* Smaller number wins per unit.\n"
            "3. **Check the label** — many products show per-100g or per-kg price. "
            "Point it out; it saves the arithmetic.\n"
            "4. **Factor in the consumption** — the bigger pack is only a saving if you "
            "actually use it before it expires. Cheap bulk that spoils is expensive.\n"
            "5. **Apply it on a real shop** — three items compared per visit. Note down "
            "savings found. Feel the real money."
        ),
        "parent_note_md": (
            "Unit-price literacy is one of the most practical adult money skills — and one "
            "most people never formally learn. A 10-year-old who checks per-gram pricing "
            "saves money for the rest of their shopping life, and learns to resist "
            "marketing tricks built around misleading pack sizes."
        ),
    },
    {
        "slug": "spending-diary-week-age11",
        "title": "Keep a Spending Diary for One Week",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up a notebook or phone note** — single column: date, item, amount.\n"
            "2. **Record every rupee spent** — for 7 days. Not skipped because it was a small "
            "snack or a bus fare. Honesty is the whole point.\n"
            "3. **Categorise at the end of the week** — food, snacks, entertainment, transport, "
            "gifts. Simple 5-category split.\n"
            "4. **Add up each category** — which one was the biggest? Is that where they "
            "thought their money was going?\n"
            "5. **Discuss the surprises** — *I didn't realise I spent ₹200 on snacks in a week.* "
            "That realisation is the point of the exercise."
        ),
        "parent_note_md": (
            "A one-week spending diary reveals the gap between what we think we spend money on "
            "and what we actually spend it on. For an 11-year-old this gap is usually small — "
            "and that makes it the perfect age to build the habit before the numbers get larger."
        ),
    },
    {
        "slug": "monthly-allowance-budget-age12",
        "title": "Create and Stick to a Monthly Allowance Budget",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know the total** — monthly pocket money. Let's say ₹500.\n"
            "2. **Three buckets: Spend, Save, Give** — 50% spend, 40% save, 10% give. "
            "(Exact split is flexible; having three buckets is not.)\n"
            "3. **Write it on paper** — ₹250 spend, ₹200 save, ₹50 give. Then break down "
            "the spend bucket into categories.\n"
            "4. **Track during the month** — a simple tally. When the spend bucket is empty, "
            "no more spending until next month. The save bucket is sacred.\n"
            "5. **Review at month end** — did the plan hold? What was the weak point? "
            "Next month's budget is informed, not guessed."
        ),
        "parent_note_md": (
            "A three-bucket budget is the simplest form of adult personal finance. A "
            "12-year-old who has run one — honestly, with real constraints — understands "
            "the machinery that most adults only stumble into in their 20s or 30s."
        ),
    },
    {
        "slug": "compound-interest-basics-age13",
        "title": "Understand How Compound Interest Grows Over Time",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the principle** — interest on interest. If ₹100 grows 10% a year, "
            "year 1 = ₹110, year 2 = ₹121 (not ₹120), year 3 = ₹133.\n"
            "2. **Show the rule of 72** — 72 ÷ interest rate = years to double. 10% = 7.2 years. "
            "6% = 12 years. It's a gift of mental maths.\n"
            "3. **Try the extreme** — ₹1000 at 10% for 30 years = ~₹17,500. For 40 years = ~₹45,000. "
            "The last decade matters the most.\n"
            "4. **Flip it to debt** — credit cards charge 30–40% a year. A ₹10,000 unpaid balance "
            "becomes ₹13,000 next year, ₹17,000 the year after. Compound works against you too.\n"
            "5. **Open a simple spreadsheet** — let them plug in numbers and see the curve. "
            "Seeing exponential growth is different from hearing about it."
        ),
        "parent_note_md": (
            "Compound interest is the single most important concept in personal finance — "
            "and the one most adults never really feel. A 13-year-old who has built their "
            "own spreadsheet and seen ₹1000 grow for 40 years will not start saving at 35. "
            "They'll start at 18. That's the whole game."
        ),
    },
    {
        "slug": "open-savings-account-age14",
        "title": "Open and Operate a Basic Savings Account",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Research 2–3 banks** — interest rate, minimum balance, fees, ease of use. "
            "Not all accounts are equal; comparing matters.\n"
            "2. **Go to the branch with a parent** — fill in the forms, provide ID, photograph, "
            "address proof. Understand what's being signed.\n"
            "3. **Collect the passbook, debit card, net-banking credentials** — separately. "
            "Learn how each is used.\n"
            "4. **Make a first deposit and a first withdrawal** — even ₹100. See the transaction "
            "land in the passbook or app.\n"
            "5. **Review statements monthly** — for any charge they don't recognise, any "
            "interest credited, any mistakes. Active account ownership from the start."
        ),
        "parent_note_md": (
            "Opening your own savings account is a meaningful adult rite of passage. "
            "A 14-year-old who has personally walked through the paperwork, understands "
            "the charges, and reviews their statement understands banking as a system — "
            "not as a mystery controlled by adults."
        ),
    },
    {
        "slug": "read-payslip-age15",
        "title": "Read and Understand a Payslip",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Borrow a real payslip** — a parent's or an older sibling's. Names can be "
            "blanked out; structure is the lesson.\n"
            "2. **Identify gross vs net** — gross = total earned. Net = what lands in the bank. "
            "The difference is deductions.\n"
            "3. **Learn the main deductions** — income tax, provident fund, professional tax, "
            "health insurance. Each is a line item on the slip.\n"
            "4. **Calculate the effective tax rate** — tax divided by gross. Usually lower than "
            "the marginal rate because of exemptions.\n"
            "5. **Understand annual CTC vs monthly take-home** — CTC is what the company spends. "
            "Take-home is what the employee receives. They can differ by 20–30%."
        ),
        "parent_note_md": (
            "Most adults sign their first employment contract without really understanding "
            "a payslip. A 15-year-old who has read three payslips and can explain gross, "
            "net, CTC, and deductions is starting their working life with a massive advantage "
            "over peers who will learn the hard way."
        ),
    },
    {
        "slug": "simple-tax-declaration-age16",
        "title": "File a Simple Tax Declaration Under Guidance",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Shadow a parent's filing** — one full cycle. Forms, supporting documents, "
            "investment proofs, submission.\n"
            "2. **Understand the main concepts** — income, deductions, exemptions, tax slabs, "
            "tax paid vs tax due. Vocabulary first.\n"
            "3. **Work through a dummy filing** — if they have scholarship income, freelance "
            "earnings, or any income, try a real filing. Otherwise use a worked example.\n"
            "4. **Understand refund and due dates** — late filing penalties, refund timelines. "
            "Tax rules are unforgiving of lateness.\n"
            "5. **Keep the records** — ITR acknowledgement, Form 16, investment proofs. "
            "Organised files saves hours in future years."
        ),
        "parent_note_md": (
            "Tax literacy is a core adult skill that most people pick up painfully in their "
            "20s. A 16-year-old who has shadowed one full filing cycle is several years "
            "ahead — they understand what they're earning toward, what they're owed, "
            "and how to stay on the right side of the law."
        ),
    },
]


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

CATEGORY_TASKS = {
    "cognitive":  COGNITIVE_TASKS,
    "social":     SOCIAL_TASKS,
    "household":  HOUSEHOLD_TASKS,
    "digital":    DIGITAL_TASKS,
    "navigation": NAVIGATION_TASKS,
    "financial":  FINANCIAL_TASKS,
}


class Command(BaseCommand):
    help = "Seed 72 ladder-filler tasks — one per (category, age) cell for ages 5-16."

    def handle(self, *args, **options):
        all_envs = list(Environment.objects.all())

        # Resolve (or create) the primary tag for each category
        tag_by_category: dict[str, Tag] = {}
        for cat_key, (tag_name, tag_category) in TAG_FOR_CATEGORY.items():
            tag, _ = Tag.objects.get_or_create(
                name=tag_name, defaults={"category": tag_category}
            )
            tag_by_category[cat_key] = tag

        total_added = 0
        total_updated = 0
        for cat_key, tasks in CATEGORY_TASKS.items():
            tag = tag_by_category[cat_key]
            cat_added = 0
            cat_updated = 0
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
                    cat_added += 1
                else:
                    cat_updated += 1
            total_added += cat_added
            total_updated += cat_updated
            self.stdout.write(
                f"{cat_key:10}: {cat_added} new, {cat_updated} updated."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_age_filler_tasks complete — "
                f"{total_added} new, {total_updated} updated, "
                f"{total_added + total_updated} total."
            )
        )
