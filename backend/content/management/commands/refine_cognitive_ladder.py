"""Management command: refine the Cognitive task ladder.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py refine_cognitive_ladder

Four phases, all idempotent:
  1. Reclassify: remove cognitive tag from tasks that belong under Social
  2. Retune: tighten broad 7-13 / 8-13 age ranges to developmental stages
  3. Add 30 new tasks filling the ladder gaps at ages 5, 6, 7, 8-9, 10-11, 12-13
  4. Wire the prerequisite DAG — 30+ edges connecting the ladder properly
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Phase 1 — Reclassification: these tasks belong to Social, not Cognitive
# ---------------------------------------------------------------------------

RECLASSIFY_FROM_COGNITIVE = [
    "write-a-thank-you-note",
    "self-advocacy-asking-for-help",
]

# ---------------------------------------------------------------------------
# Phase 2 — Age range updates (slug, new_min, new_max)
# ---------------------------------------------------------------------------

AGE_RANGE_UPDATES = [
    ("follow-three-step-instruction", 7, 9),
    ("sort-by-invented-rule",         7, 9),
    ("tell-time-analog-clock",        7, 9),
    ("use-calendar-find-date",        7, 10),
    ("summarize-short-story",         8, 11),
    ("spot-pattern-in-sequence",      8, 10),
    ("explain-process-in-order",      8, 10),
    ("ask-why-research-answer",       7, 10),
    ("home-alone-safely",            11, 14),
    ("menstrual-health-basics",       9, 13),
]

# ---------------------------------------------------------------------------
# Phase 3 — New tasks (30 total, 5 per tier)
# ---------------------------------------------------------------------------

NEW_TASKS = [
    # ── Age 5 (5 tasks) ──────────────────────────────────────────────────
    {
        "slug": "count-to-20-age5",
        "title": "Count to 20 and Recognise Written Numbers",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Count aloud together** — 1 to 20 slowly. Tap each number as you say it.\n"
            "2. **Count real things** — steps, grapes on a plate, toy cars. "
            "Touching each item anchors the count.\n"
            "3. **Recognise the numerals** — write 1–20 on cards. Hold one up, they name it.\n"
            "4. **Find the missing number** — lay cards in order with one missing. "
            "Which number is gone?\n"
            "5. **Count backwards from 10** — a much harder skill. Start at 10, "
            "count down to 1 together. Repeat until confident."
        ),
        "parent_note_md": (
            "Reliable counting to 20 is the bridge between rote reciting and genuine "
            "number sense. Children who can count real objects (not just sing the "
            "numbers) are ready for early addition and everyday quantity awareness."
        ),
    },
    {
        "slug": "name-basic-shapes-age5",
        "title": "Name Eight Common Shapes",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Introduce the shapes** — circle, square, triangle, rectangle, oval, "
            "star, diamond, heart. Draw each one on paper.\n"
            "2. **Shape hunt around the home** — *Find me a circle! A rectangle!* "
            "Clocks, books, plates, windows, door.\n"
            "3. **Sort by shape** — cut out mixed shapes from magazines or paper. "
            "Pile them by shape together.\n"
            "4. **Describe what they see** — *The pizza is round (circle). "
            "The door is tall (rectangle).*\n"
            "5. **Draw the shapes** — they copy each one onto paper. "
            "Neatness is not the goal — recognition is."
        ),
        "parent_note_md": (
            "Shape recognition builds spatial awareness and is foundational to geometry, "
            "reading letter forms, and later architectural and design thinking. "
            "Naming shapes in daily life anchors the concept in the real world."
        ),
    },
    {
        "slug": "remember-three-items-age5",
        "title": "Remember Three Things from a Short List",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Say three related items** — *Apple, banana, milk.* "
            "Ask them to repeat immediately.\n"
            "2. **Wait and ask again** — after 30 seconds of chat about something else, "
            "*What were the three things I said?*\n"
            "3. **Use a real errand** — give a tray to carry three items from the kitchen. "
            "No writing — just memory.\n"
            "4. **Mix the categories** — not just fruit. *Pen, towel, spoon.* "
            "Harder to remember because there's no theme.\n"
            "5. **Build up to four** — once three is reliable, try four. "
            "Building working memory is a daily practice."
        ),
        "parent_note_md": (
            "Working memory — holding a few things in mind while doing something else — "
            "is one of the strongest predictors of academic success. It can be trained "
            "from a young age with simple, playful exercises. Three items at 5, four at 6, "
            "five at 7 is a reasonable progression."
        ),
    },
    {
        "slug": "sort-by-one-property-age5",
        "title": "Sort Objects by One Property",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose one property** — colour, size, or shape. Only one at a time.\n"
            "2. **Give them a mixed pile** — buttons, coins, Lego bricks, cut paper. "
            "*Put all the red ones here, all the others there.*\n"
            "3. **Switch the rule** — now sort the same pile by size. "
            "Same objects, different groupings.\n"
            "4. **Let them invent a rule** — *Sort these however you want, then tell me the rule.* "
            "This is a big step — their own category.\n"
            "5. **Odd one out** — give four items, three alike. "
            "Which is different and why?"
        ),
        "parent_note_md": (
            "Sorting is the earliest form of classification — a thinking skill used in "
            "every subject from biology to law. Children who can sort, resort, and "
            "explain the rule are developing flexible thinking, not just observation."
        ),
    },
    {
        "slug": "what-happens-next-age5",
        "title": "Answer What Happens Next in a Story",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pause mid-story** — while reading a picture book, stop at a key moment. "
            "*What do you think happens next?*\n"
            "2. **Accept all guesses** — there is no wrong answer. "
            "Reward the act of thinking ahead, not correctness.\n"
            "3. **Predict from pictures** — look at the next page's illustration together. "
            "*What is happening here? How do you know?*\n"
            "4. **Real-life predictions** — *The kettle is boiling. What happens next?* "
            "*The sky is dark and cloudy. What happens next?*\n"
            "5. **Link cause and effect** — *Because it rained, what happened to the garden?*"
        ),
        "parent_note_md": (
            "Prediction is the foundation of comprehension — of stories, of science, "
            "of social situations. Children who practise thinking ahead become better "
            "readers, better decision-makers, and more attuned to their surroundings. "
            "Bedtime stories are the perfect training ground."
        ),
    },
    # ── Age 6 (5 tasks) ──────────────────────────────────────────────────
    {
        "slug": "count-to-100-age6",
        "title": "Count to 100 in Ones and Tens",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Daily countdown** — count to 100 out loud once a day for a week.\n"
            "2. **Count in tens** — 10, 20, 30… 100. Much faster. "
            "Helps them see the pattern of the decades.\n"
            "3. **Start from anywhere** — *Start at 56. Keep counting.* "
            "Harder than starting from 1.\n"
            "4. **The 100 chart** — print or draw a 10×10 grid of numbers 1–100. "
            "Point to patterns: all ones end in 1, all the tens column is 10, 20, 30…\n"
            "5. **Count backwards from 20** — real control of number order. "
            "Extend to backwards from 30, then 50."
        ),
        "parent_note_md": (
            "Counting to 100 is not just memorisation — done well, it's pattern "
            "recognition. A child who sees that every row on the hundred chart works "
            "the same way is developing abstract thinking. Forwards is easy; backwards "
            "and starting-from-anywhere is where real mastery is tested."
        ),
    },
    {
        "slug": "because-so-age6",
        "title": "Use Because and So to Explain",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Model the words** — *I'm putting on a jacket because it's cold. "
            "It's cold, so I need a jacket.*\n"
            "2. **Ask them to complete the sentence** — *I was hungry, so…* "
            "*I went to sleep because…*\n"
            "3. **Turn it around** — give a fact, ask for the cause. "
            "*The plant is wilting. Why?*\n"
            "4. **Play a because/so swap** — they say a sentence using 'because', "
            "then rephrase with 'so'. Practise both directions.\n"
            "5. **Catch them using it** — when they spontaneously use because or so, "
            "praise it: *Good reasoning — you said because.*"
        ),
        "parent_note_md": (
            "Cause-and-effect language is where real reasoning begins. Children who "
            "use because and so are building logical structure into their thinking — "
            "which later becomes the ability to construct arguments, solve problems, "
            "and explain reasoning to others."
        ),
    },
    {
        "slug": "recall-four-events-age6",
        "title": "Recall Four Events in the Right Order",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use their day** — at bedtime, ask: *What did we do today, "
            "in order?* Prompt with *What was first? What was next?*\n"
            "2. **Use a story** — after reading, ask them to retell four things "
            "that happened in the right order.\n"
            "3. **Sequence cards** — draw or print 4 pictures showing a simple process "
            "(planting a seed, making toast). They arrange them in order.\n"
            "4. **Reverse the order** — once the forward order is easy, ask for "
            "reverse. *Tell me the day backwards, from bedtime to waking up.*\n"
            "5. **Build up to six events** — once four is solid, go to five then six. "
            "Sequencing is a lifelong skill."
        ),
        "parent_note_md": (
            "Sequencing events correctly is the foundation of narrative writing, "
            "logical reasoning, and following multi-step instructions. Retelling the "
            "day in order is also emotionally valuable — children who can recall and "
            "name what happened process their experiences better."
        ),
    },
    {
        "slug": "memory-pairs-age6",
        "title": "Play and Win a Memory Pairs Game",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up 12 cards** — 6 matching pairs, face down, shuffled. "
            "A deck of playing cards or a memory card set works.\n"
            "2. **Take turns** — flip two cards. If they match, keep the pair and go again. "
            "If not, turn them back over. Next player's turn.\n"
            "3. **Talk through the strategy** — *I saw the red horse earlier. "
            "Where was it?* Remembering positions is the whole skill.\n"
            "4. **Extend the game** — once 6 pairs is easy, go to 8 then 10 pairs.\n"
            "5. **Play daily for a week** — tracking improvement is motivating. "
            "How many pairs found on the first day vs the seventh?"
        ),
        "parent_note_md": (
            "Memory games train working memory in a fun, competitive format. Children "
            "who play them regularly improve measurably at remembering positions, "
            "sequences, and spatial arrangements — skills that transfer directly to "
            "classroom learning."
        ),
    },
    {
        "slug": "answer-why-with-reason-age6",
        "title": "Answer Why Questions with a Real Reason",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Accept any answer initially** — *Why do birds fly?* Even silly "
            "answers show they're thinking. Build from there.\n"
            "2. **Push for a real reason** — after their first answer, ask: "
            "*Why do you think that?* No accepting *just because*.\n"
            "3. **Ask about their own choices** — *Why did you pick that shirt? "
            "Why do you like this book?* Reasons about themselves are easier.\n"
            "4. **Look up the real answer together** — if they don't know, "
            "find out. *Let's see why lakes freeze but oceans don't.*\n"
            "5. **Celebrate good reasoning** — when they give a thoughtful reason, "
            "name it: *That's a really good reason — you thought about it carefully.*"
        ),
        "parent_note_md": (
            "The habit of having and giving real reasons — rather than accepting "
            "*just because* — is the root of critical thinking. Children who are "
            "expected to explain their thinking produce better answers throughout "
            "their schooling. Never punish a question; always welcome a reason."
        ),
    },
    # ── Age 7 (5 tasks — NEW TIER) ──────────────────────────────────────
    {
        "slug": "follow-simple-recipe-age7",
        "title": "Follow a Simple 3-Step Recipe",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a no-cook recipe first** — sandwich, fruit salad, cereal, yoghurt parfait. "
            "Read it through together first.\n"
            "2. **Gather everything before starting** — ingredients and tools laid out. "
            "Professional cooks call this *mise en place*.\n"
            "3. **Read-then-do** — read step 1, do step 1. Read step 2, do step 2. "
            "Don't skim ahead.\n"
            "4. **Measure exactly** — if the recipe says 2 spoons, measure 2 spoons. "
            "Following instructions precisely is the lesson.\n"
            "5. **Serve and eat what they made** — the reward is tasting their own work. "
            "Progress to a simple cooked recipe (scrambled eggs, pasta) once confident."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- No-cook recipes only until knife and stove skills are established.\n"
            "- Wash hands before starting.\n"
            "- Any cutting should be done with adult guidance using a child-safe knife."
        ),
        "parent_note_md": (
            "A recipe is a formal set of sequential instructions — the closest a "
            "child comes to reading a procedure before they encounter one in school. "
            "Cooking builds reading comprehension, measurement, and the discipline "
            "of doing things in order."
        ),
    },
    {
        "slug": "categorise-objects-age7",
        "title": "Sort a Mixed Group into Clear Categories",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Give a mixed pile** — animals, foods, tools, clothes on cards or pictures.\n"
            "2. **Sort into their natural groups** — animals in one pile, foods in another. "
            "Say each category name aloud.\n"
            "3. **Then sort differently** — split animals into *lives in water / on land / flies*. "
            "Same objects, finer categories.\n"
            "4. **Invent their own categories** — *How would YOU group these?* "
            "Accept unusual answers if the rule is consistent.\n"
            "5. **Multi-level sorting** — foods → fruits → citrus fruits. "
            "Show how categories nest inside each other."
        ),
        "parent_note_md": (
            "Hierarchical categorisation — nested groups, multiple sorting rules — "
            "is the thinking behind biology, library systems, computer files, and "
            "almost all formal knowledge. Starting at 7 with simple groups builds "
            "the mental framework used for the rest of school."
        ),
    },
    {
        "slug": "find-odd-one-out-age7",
        "title": "Find the Odd One Out and Explain Why",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start visually** — four pictures, three related, one different. "
            "*Apple, banana, carrot, orange.*\n"
            "2. **Explain the reasoning** — they must say *why* the odd one is odd. "
            "*Carrot is a vegetable; the others are fruits.*\n"
            "3. **Accept alternate answers** — *Orange is odd because the others start with A or B.* "
            "Any consistent reason is valid.\n"
            "4. **Harder sets** — *Dog, cat, goldfish, eagle.* "
            "Multiple possible answers. Discuss.\n"
            "5. **Abstract sets** — numbers or words. "
            "*2, 4, 7, 8 — which doesn't belong?* Build toward mathematical reasoning."
        ),
        "parent_note_md": (
            "The odd-one-out puzzle is the simplest form of reasoning: *these are "
            "alike in some way, this one isn't.* Children who can articulate the "
            "rule are building the foundation of analytical thinking, which will "
            "show up in maths, science, and literature comprehension."
        ),
    },
    {
        "slug": "solve-a-riddle-age7",
        "title": "Solve Simple Riddles and 'Who Am I' Puzzles",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with easy ones** — *I have four legs and a tail and I say woof. "
            "What am I?* Build confidence.\n"
            "2. **Move to multi-clue riddles** — *I am yellow. I grow on trees. "
            "Monkeys love me. What am I?*\n"
            "3. **Teach the listen-then-think pattern** — hear all clues first, "
            "then think, then answer. Not blurting after the first clue.\n"
            "4. **Let them invent riddles** — they pick something, give you 3 clues. "
            "Harder than solving — they must pick distinguishing features.\n"
            "5. **Daily riddle** — one riddle a day at breakfast or bedtime. "
            "A small, consistent practice builds real skill."
        ),
        "parent_note_md": (
            "Riddles require children to hold multiple clues in mind and combine them — "
            "exactly the cognitive move needed for maths word problems, scientific "
            "reasoning, and detective-style thinking. They're also fun, which is why "
            "the habit sticks."
        ),
    },
    {
        "slug": "estimate-by-looking-age7",
        "title": "Estimate a Quantity Just by Looking",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Put 10 objects in a bowl** — marbles, buttons, coins. "
            "Ask: *How many do you think are in there?*\n"
            "2. **Count to check** — together. Were they close? "
            "No blame if off — estimation improves with practice.\n"
            "3. **Estimate bigger numbers** — jar of sweets, pages in a book, "
            "people in a room.\n"
            "4. **Estimate time and distance** — *How many minutes is it to the shop? "
            "How many steps across the room?*\n"
            "5. **Use anchor estimates** — *This cup holds about 20 raisins. "
            "How many do you think are in this bigger jar?*"
        ),
        "parent_note_md": (
            "Estimation is the maths skill most used in everyday life — yet most "
            "schools don't teach it directly. Children who can estimate reliably "
            "check their own answers in maths, spot wrong calculations, and handle "
            "real-world measurement problems confidently."
        ),
    },
    # ── Age 8-9 (5 tasks) ───────────────────────────────────────────────
    {
        "slug": "mental-arithmetic-age8",
        "title": "Do Simple Mental Arithmetic",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Daily 5-question drill** — addition and subtraction within 20, "
            "done in their head. 2 minutes maximum.\n"
            "2. **Bridge through 10** — 7 + 5 = 7 + 3 + 2. Teach this strategy "
            "explicitly. It's faster than counting on fingers.\n"
            "3. **Times tables** — start with 2s, 5s, 10s. Sing or chant them. "
            "Add 3s and 4s once foundation is solid.\n"
            "4. **Real-world sums** — *You have ₹20. The snack costs ₹12. "
            "How much change?* Every transaction is a mental maths opportunity.\n"
            "5. **Speed and accuracy, not just accuracy** — aim for fast recall. "
            "Slow-but-correct leaves children struggling in timed settings later."
        ),
        "parent_note_md": (
            "Mental maths fluency is one of the strongest predictors of later "
            "mathematical confidence. Children who can do simple arithmetic "
            "automatically have cognitive bandwidth for the harder concepts. "
            "Those who count on fingers at 10 often struggle with fractions at 12."
        ),
    },
    {
        "slug": "note-key-points-age8",
        "title": "Note Down the Key Points from a Short Talk",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Watch a 5-minute video together** — educational content: a BBC Bitesize "
            "clip, a CrashCourse Kids episode, a short documentary segment.\n"
            "2. **Write 3 key points** — not full sentences. Just words or short phrases "
            "that capture the main ideas.\n"
            "3. **Compare your notes** — what did each of you write? Why did you each "
            "pick those points?\n"
            "4. **Rewatch and check** — did they miss something important? "
            "What would they add now?\n"
            "5. **Practise weekly** — same format, different topics. "
            "Note-taking is a muscle; it builds with consistent use."
        ),
        "parent_note_md": (
            "Note-taking from a talk is a foundation skill for the rest of formal "
            "education. Children who can extract key points from a lecture or video "
            "are learning actively, not passively. Starting at 8 — with short, "
            "engaging content — builds the habit before it's needed under pressure."
        ),
    },
    {
        "slug": "find-info-in-book-age8",
        "title": "Find Information in a Book or Trusted Website",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pose a real question** — *How long do elephants live? Why is the sky blue?* "
            "Something they genuinely want to know.\n"
            "2. **Start with a book** — use an encyclopaedia or a topic-specific book at home. "
            "Teach the table of contents and the index.\n"
            "3. **Online search** — use a child-safe search engine (Kiddle) or supervised Google. "
            "Teach good keywords: not *the big grey African animal*, but *elephant lifespan*.\n"
            "4. **Evaluate the source** — is this a trustworthy site? A children's museum, "
            "a university, a known encyclopaedia — yes. A random blog — check.\n"
            "5. **Summarise the answer** — once they find it, they tell you the answer in "
            "their own words, not by reading it out."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- All online research at this age should be with parent supervision or "
            "on a child-safe search engine.\n"
            "- Never enter personal information while researching."
        ),
        "parent_note_md": (
            "The ability to find information when you need it is more important than "
            "knowing facts in advance. Children who learn to research — with books "
            "and with careful online searches — become self-teaching adults. "
            "This is the foundation of lifelong learning."
        ),
    },
    {
        "slug": "make-weekly-plan-age9",
        "title": "Make a Simple Weekly Plan",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Draw a 7-day grid** — one column per day of the week.\n"
            "2. **Fill in fixed commitments** — school hours, extra-curriculars, "
            "family meals, sleep time. These are non-negotiable.\n"
            "3. **Add homework and study** — each assignment gets a specific day "
            "to be done. Not *sometime this week* — a named day.\n"
            "4. **Add free time and fun** — play, reading, screen time. "
            "A good plan includes rest, not just work.\n"
            "5. **Review on Sunday** — what worked this week? What didn't? "
            "Adjust the plan for next week."
        ),
        "parent_note_md": (
            "Planning a week ahead — rather than reacting day by day — is the "
            "executive function skill behind every well-managed adult life. Starting "
            "at 9 with a visual plan teaches the habit before the stakes rise at "
            "secondary school. Resist building the plan for them — they must own it."
        ),
    },
    {
        "slug": "teach-back-age9",
        "title": "Teach Back What You Just Learned",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick something they just learned** — in class, in a book, "
            "in a documentary.\n"
            "2. **The teach-back** — they explain it to you as if you know nothing. "
            "Use a whiteboard or paper. Draw diagrams.\n"
            "3. **Ask pretend-dumb questions** — *Why does that happen? "
            "What does this word mean?* Force them to clarify.\n"
            "4. **Spot the gaps** — where did they get stuck? Those are the gaps "
            "in their own understanding — the most valuable thing to know.\n"
            "5. **Go back and fill the gaps** — re-read, re-watch, or ask a "
            "teacher. Then teach back again."
        ),
        "parent_note_md": (
            "The Feynman Technique — learning by teaching — is one of the most "
            "effective study strategies ever identified. A child who can explain "
            "a concept to someone else genuinely understands it. Those who can only "
            "repeat it do not. Use this weekly for any subject they're struggling with."
        ),
    },
    # ── Age 10-11 (5 tasks) ─────────────────────────────────────────────
    {
        "slug": "mind-map-topic-age10",
        "title": "Create a Mind Map of a Topic",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a topic they know well** — their favourite sport, game, "
            "book, subject. Write it in the centre of a large sheet.\n"
            "2. **Draw main branches** — 4–6 main aspects of the topic. "
            "For cricket: rules, positions, famous players, history, equipment, formats.\n"
            "3. **Add sub-branches** — break each main branch into smaller ideas. "
            "Keep branching until the topic is mapped.\n"
            "4. **Use colours and pictures** — visual mind maps are remembered far "
            "better than plain text.\n"
            "5. **Apply it to a school topic** — next time they revise, mind-map the "
            "topic first. Compare learning speed with and without the map."
        ),
        "parent_note_md": (
            "Mind mapping is one of the most effective study and thinking techniques "
            "ever developed. It matches how the brain stores information — in "
            "connected networks, not lists. A child who can mind-map a topic is "
            "absorbing and organising it at the same time."
        ),
    },
    {
        "slug": "research-and-present-age10",
        "title": "Research a Topic and Present It in 3 Minutes",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a topic they care about** — an animal, a historical figure, "
            "a country, a scientific phenomenon.\n"
            "2. **Research from 2–3 sources** — books, trusted websites. "
            "Take notes in their own words, not copied text.\n"
            "3. **Structure the talk** — introduction (what it is), main points (3 key facts), "
            "conclusion (what's most interesting about it).\n"
            "4. **Practise out loud** — before presenting. Time it. 3 minutes is harder "
            "than it sounds.\n"
            "5. **Present to the family** — real audience, eye contact, clear voice. "
            "Take questions at the end."
        ),
        "parent_note_md": (
            "The research-and-present format is how most knowledge work is shared in "
            "the adult world — school presentations, work briefings, lectures. "
            "A child who has practised this many times arrives at school presentations "
            "confident. Every family meal is a potential audience."
        ),
    },
    {
        "slug": "fractions-real-context-age10",
        "title": "Use Fractions to Solve Everyday Problems",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Cooking measurements** — *The recipe calls for 1/4 cup of oil. Measure it.* "
            "*We need half of 3/4 cup. How much is that?*\n"
            "2. **Splitting things fairly** — *There are 12 biscuits. Four people. "
            "How many each? That's what 12/4 means.*\n"
            "3. **Time and fractions** — *Quarter past, half past, quarter to* — "
            "these are all fractions of an hour.\n"
            "4. **Pizza problems** — *A pizza cut into 8 slices. You ate 3. "
            "What fraction did you eat? What's left?*\n"
            "5. **Equivalent fractions** — 1/2 = 2/4 = 4/8. Use real objects "
            "(chocolate bar, clock face) to show they're the same."
        ),
        "parent_note_md": (
            "Fractions is where many children start to struggle with maths — not "
            "because they're hard, but because they're taught abstractly. A child "
            "who has measured half a cup, split 12 biscuits four ways, and eaten "
            "3/8 of a pizza understands fractions viscerally. Do the maths in the kitchen."
        ),
    },
    {
        "slug": "compare-options-systematic-age11",
        "title": "Compare Two Options Systematically",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a real decision** — two schools, two activities, two phones, "
            "two holiday destinations. Something they actually care about.\n"
            "2. **List the criteria** — what matters? Cost, fun, difficulty, time, "
            "quality, friends involved. 4–6 criteria.\n"
            "3. **Build a comparison table** — options as columns, criteria as rows. "
            "Fill in each cell honestly.\n"
            "4. **Weight the criteria** — are all criteria equally important? "
            "If not, which matter most? Star them.\n"
            "5. **Make and explain the decision** — based on the table, which option "
            "wins? Can they explain why to someone who disagrees?"
        ),
        "parent_note_md": (
            "Structured comparison — building a table, weighting criteria — is how "
            "adults make good decisions in work and life. Most people make decisions "
            "emotionally and only justify them with reasoning later. Teaching the "
            "structure at 11 builds a lifelong habit of deliberate choice."
        ),
    },
    {
        "slug": "hypothesis-and-test-age11",
        "title": "Make a Hypothesis and Test It",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Observation** — notice something in daily life. *The plants by the window "
            "grow faster than the ones in the corner.*\n"
            "2. **Form a hypothesis** — a specific, testable prediction. "
            "*Plants grow faster with more light.*\n"
            "3. **Design a simple test** — two identical plants, different light levels, "
            "same water and care. Predict which will grow faster.\n"
            "4. **Run the test** — for 2–3 weeks. Measure weekly. "
            "Write down results, even when unexpected.\n"
            "5. **Conclusion** — was the hypothesis right? What would you do differently? "
            "What's the next question to test?"
        ),
        "parent_note_md": (
            "The scientific method — observe, predict, test, conclude — is the most "
            "powerful thinking tool ever developed. Children who apply it even to "
            "simple questions (does water freeze faster in a metal or plastic container?) "
            "are learning to think like scientists. This is the heart of rational inquiry."
        ),
    },
    # ── Age 12-13 (5 tasks — NEW TIER) ──────────────────────────────────
    {
        "slug": "structured-class-notes-age12",
        "title": "Take Structured Notes in Class",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the Cornell method** — page divided into three sections: "
            "main notes (right), cues/questions (left), summary (bottom).\n"
            "2. **Use headings and indentation** — main topic, sub-points indented, "
            "examples indented further. Structure mirrors content.\n"
            "3. **Abbreviations and symbols** — develop personal shorthand. "
            "→ (leads to), ≠ (not equal), eg, ie. Faster than full words.\n"
            "4. **Within 24 hours** — reread the notes, fill in the cue column with "
            "questions that match each section, write the summary at the bottom.\n"
            "5. **Test without looking** — cover the main notes, look only at the cues, "
            "try to answer. This is active revision, not re-reading."
        ),
        "parent_note_md": (
            "Note-taking is the single biggest differentiator between students who "
            "pass and students who excel in secondary school. Most children just "
            "write what the teacher says verbatim — or stop writing when they lose track. "
            "Structured systems like Cornell turn note-taking into an active learning "
            "exercise."
        ),
    },
    {
        "slug": "summarise-long-text-age12",
        "title": "Summarise a Chapter or Long Article in One Paragraph",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read once fully** — no notes, no highlighting. Just understand it.\n"
            "2. **Identify the main argument** — in one sentence, what is the author saying?\n"
            "3. **List the 3 strongest supporting points** — from memory if possible. "
            "Re-skim only to verify.\n"
            "4. **Write the summary** — 4–6 sentences. Main argument, supporting points, "
            "conclusion. No direct quotations.\n"
            "5. **Test the summary** — could someone who hasn't read the original get "
            "the main idea from your summary? If not, revise."
        ),
        "parent_note_md": (
            "The ability to distil a long text into its core argument is one of the "
            "highest-value academic skills. It requires genuine comprehension, not just "
            "reading. Students who can summarise well read more efficiently, revise more "
            "quickly, and write more persuasively. It's also how research works — "
            "compressing large bodies of information into actionable insight."
        ),
    },
    {
        "slug": "use-library-database-age12",
        "title": "Use a Library or Academic Database to Find Sources",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start in a physical library** — learn the classification system "
            "(Dewey Decimal or similar). Ask the librarian to walk through it.\n"
            "2. **Use the catalogue** — search for a topic, find 3 relevant books, "
            "locate them on the shelves.\n"
            "3. **Explore digital catalogues** — many libraries have online catalogues. "
            "Learn to search by subject, author, and year.\n"
            "4. **Academic databases** — Google Scholar, JSTOR (many public libraries "
            "offer free access), Khan Academy library. Search a topic.\n"
            "5. **Evaluate a source** — who wrote it? When? Who published it? "
            "A textbook, an academic article, and a blog post are not equal sources."
        ),
        "parent_note_md": (
            "The library — physical and digital — is the richest research resource "
            "available to anyone, and most students never learn to use it beyond the "
            "most basic searches. A child who can navigate a library catalogue and "
            "an academic database has a massive academic advantage over peers who "
            "rely entirely on random Google searches."
        ),
    },
    {
        "slug": "structured-debate-age13",
        "title": "Participate in a Structured Debate",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a motion** — *This house believes homework should be abolished.* "
            "Something they have views on.\n"
            "2. **Assign sides** — sometimes force them to argue the side they disagree with. "
            "That's the real skill.\n"
            "3. **Prepare three arguments per side** — each with evidence or examples, "
            "not just opinion.\n"
            "4. **Debate format** — opening statement (2 min), rebuttal (1 min), closing (1 min). "
            "Time it strictly.\n"
            "5. **Debrief** — which arguments were strongest? Did anyone change their mind? "
            "What did they learn about the other side?"
        ),
        "parent_note_md": (
            "Structured debate trains precisely the skills most lacking in modern "
            "discourse: arguing for a position with evidence, genuinely considering "
            "the other side, and engaging respectfully with disagreement. Teenagers "
            "who have debated formally — even at a kitchen table — are measurably "
            "better at writing persuasive essays and navigating real-world arguments."
        ),
    },
    {
        "slug": "scientific-method-age13",
        "title": "Apply the Full Scientific Method to a Real Question",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pose a researchable question** — *Does background music affect focus? "
            "Does temperature affect plant growth?* Specific and testable.\n"
            "2. **Literature review** — look up what's already known about this. "
            "Summarise existing research in 3–4 sentences.\n"
            "3. **Hypothesis with reasoning** — what's their prediction and *why*? "
            "Grounded in the prior research.\n"
            "4. **Designed experiment** — control variables, independent variable, "
            "dependent variable. Multiple trials, not just one.\n"
            "5. **Analyse and write up** — graph the results if possible. "
            "Discuss whether the hypothesis was supported, what limitations existed, "
            "what the next experiment should be."
        ),
        "parent_note_md": (
            "By 13, a child should have done at least one proper experiment "
            "independently — from question to write-up. This is qualitatively different "
            "from a school experiment following a recipe. It is the genuine practice "
            "of science — the same method used in every research field from medicine "
            "to social policy."
        ),
    },
]

# ---------------------------------------------------------------------------
# Phase 4 — Prerequisite edges: (to_slug, from_slug, mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    # Cross-age cognitive ladder — existing tasks
    ("follow-three-step-instruction",      "follow-two-step-instruction-age5", True),
    ("tell-time-analog-clock",             "tell-time-hour-age6",              True),
    ("summarize-short-story",              "listen-till-finished-age5",        True),
    ("accept-feedback-calmly",             "manage-emotions-calm-down",        True),
    ("reflect-handle-failure-age14",       "accept-feedback-calmly",           True),
    ("critical-thinking-argument-age14",   "detect-biased-argument",           True),
    ("research-form-opinion-age15",        "detect-biased-argument",           True),
    ("research-form-opinion-age15",        "spot-basic-logical-fallacy",       True),
    ("analyse-media-bias-age16",           "research-form-opinion-age15",      True),
    ("manage-competing-priorities-age15",  "manage-homework-schedule",         True),
    ("structured-decision-age15",          "decide-with-incomplete-info",      True),
    ("write-structured-essay-age16",       "write-formal-application-age15",   True),
    ("long-term-goal-plan-age16",          "set-achieve-personal-goal-age14",  True),

    # New task chains
    ("count-to-100-age6",                  "count-to-20-age5",                 True),
    ("recall-four-events-age6",            "remember-three-items-age5",        True),
    ("answer-why-with-reason-age6",        "because-so-age6",                  True),
    ("categorise-objects-age7",            "sort-by-one-property-age5",        True),
    ("find-odd-one-out-age7",              "categorise-objects-age7",          True),
    ("sort-by-invented-rule",              "categorise-objects-age7",          True),
    ("spot-pattern-in-sequence",           "sort-by-invented-rule",            True),
    ("mental-arithmetic-age8",             "count-to-100-age6",                True),
    ("note-key-points-age8",               "summarize-short-story",            True),
    ("find-info-in-book-age8",             "ask-why-research-answer",          True),
    ("make-weekly-plan-age9",              "use-calendar-find-date",           True),
    ("teach-back-age9",                    "explain-process-in-order",         True),
    ("mind-map-topic-age10",               "explain-process-in-order",         True),
    ("research-and-present-age10",         "find-info-in-book-age8",           True),
    ("compare-options-systematic-age11",   "make-pros-cons-list",              True),
    ("hypothesis-and-test-age11",          "spot-pattern-in-sequence",         True),
    ("structured-class-notes-age12",       "note-key-points-age8",             True),
    ("summarise-long-text-age12",          "summarize-short-story",            True),
    ("use-library-database-age12",         "find-info-in-book-age8",           True),
    ("structured-debate-age13",            "detect-biased-argument",           True),
    ("scientific-method-age13",            "hypothesis-and-test-age11",        True),
]


class Command(BaseCommand):
    help = "Refine the Cognitive task ladder: reclassify, retune ages, add new tasks, wire DAG."

    def handle(self, *args, **options):
        reasoning_tag = Tag.objects.filter(
            name="Reasoning", category=Tag.Category.COGNITIVE
        ).first()
        social_tag = Tag.objects.filter(
            name="Social skills", category=Tag.Category.SOCIAL
        ).first()

        if not reasoning_tag:
            reasoning_tag, _ = Tag.objects.get_or_create(
                name="Reasoning",
                defaults={"category": Tag.Category.COGNITIVE},
            )
        if not social_tag:
            social_tag, _ = Tag.objects.get_or_create(
                name="Social skills",
                defaults={"category": Tag.Category.SOCIAL},
            )

        all_envs = list(Environment.objects.all())

        # ── Phase 1 — Reclassify ────────────────────────────────────────
        reclassified = 0
        for slug in RECLASSIFY_FROM_COGNITIVE:
            task = Task.objects.filter(slug=slug).first()
            if not task:
                self.stdout.write(
                    self.style.WARNING(f"  Phase 1: task {slug} not found, skipping")
                )
                continue
            task.tags.remove(reasoning_tag)
            if not task.tags.filter(category=Tag.Category.SOCIAL).exists():
                task.tags.add(social_tag)
            reclassified += 1
        self.stdout.write(f"Phase 1: reclassified {reclassified} tasks from cognitive to social.")

        # ── Phase 2 — Age range updates ─────────────────────────────────
        retuned = 0
        for slug, new_min, new_max in AGE_RANGE_UPDATES:
            updated = Task.objects.filter(slug=slug).update(
                min_age=new_min, max_age=new_max
            )
            if updated:
                retuned += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"  Phase 2: task {slug} not found, skipping")
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
            task.tags.set([reasoning_tag])
            task.environments.set(all_envs)
            added += 1
        self.stdout.write(f"Phase 3: upserted {added} new cognitive tasks.")

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

        self.stdout.write(self.style.SUCCESS("refine_cognitive_ladder complete."))
