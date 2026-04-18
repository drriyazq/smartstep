"""Management command: seed the Social & Communication task category.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_social_catalog

Idempotent — safe to re-run. Uses update_or_create throughout.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

SOCIAL_TASKS = [
    # ── Foundation (no prerequisites, age 7-9) ────────────────────────────
    {
        "slug": "social-courtesy-words",
        "title": "Use Courtesy Words Every Time",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the three magic words** — *please*, *thank you*, and *excuse me*. "
            "Ask your child when they think each one is used.\n"
            "2. **Morning drill** — at breakfast, ask them to request something (cereal, juice) "
            "using please. Praise immediately when they do.\n"
            "3. **Roleplay a shop** — you are the shopkeeper. They must say please when asking "
            "for items and thank you when receiving them.\n"
            "4. **Spot it in the wild** — when out, gently point out when others use (or forget) "
            "courtesy words. Keep it light, not judgmental.\n"
            "5. **End-of-day check** — ask: *Did you use any courtesy words today? When?* "
            "Celebrate any example they can recall."
        ),
        "parent_note_md": (
            "Courtesy words are the foundation of every social interaction. Children who use "
            "them consistently are perceived as more confident and likeable by teachers, "
            "family, and peers. The habit forms fastest when parents model it themselves — "
            "say please and thank you to your child too."
        ),
        "prereqs": [],
    },
    {
        "slug": "social-greet-adult",
        "title": "Greet an Adult Properly",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show what good looks like** — demonstrate: stand straight, make eye contact, "
            "smile, say *Good morning / Good afternoon*, and offer a handshake.\n"
            "2. **Practise at home** — roleplay with a parent as a visiting adult. Child knocks, "
            "you answer, they greet. Repeat 3 times.\n"
            "3. **Real test: a familiar adult** — greet a relative, neighbour, or teacher using "
            "the technique. Coach gently afterwards.\n"
            "4. **Discuss what was hard** — did they forget eye contact? Go limp on the "
            "handshake? Practise just that part again.\n"
            "5. **Raise the bar** — add *Nice to meet you* or *How are you?* once the basics "
            "are solid."
        ),
        "parent_note_md": (
            "A confident greeting sets the tone for every interaction. Children who greet "
            "adults well are remembered positively by teachers and future employers alike. "
            "Eye contact in particular signals confidence and respect — it is worth practising "
            "separately if your child finds it uncomfortable."
        ),
        "prereqs": [],
    },
    {
        "slug": "social-listen-no-interrupt",
        "title": "Listen Without Interrupting",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the habit** — explain that interrupting makes the other person feel "
            "unimportant. Listening is a gift.\n"
            "2. **The talking stick** — use any object. Only the person holding it may speak. "
            "Have a short family conversation using the stick.\n"
            "3. **Pause practice** — tell a story for 2 minutes. Child must wait until you "
            "pause before adding anything. Swap roles.\n"
            "4. **Hold the thought** — if they want to say something, teach them to hold up one "
            "finger (a silent signal) rather than blurting it out.\n"
            "5. **Review** — after a family meal, ask: *Did you interrupt anyone? Did anyone "
            "interrupt you? How did it feel?*"
        ),
        "parent_note_md": (
            "Listening is the most underrated communication skill. Children who listen well "
            "build deeper friendships and perform better in group settings. Interrupting is "
            "usually not rudeness — it is excitement or anxiety. Teach the finger-hold trick "
            "as a physical anchor that lets them keep the thought without breaking the flow."
        ),
        "prereqs": [],
    },
    {
        "slug": "social-apologise-sincerely",
        "title": "Apologise Sincerely",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the formula** — a real apology has three parts: *what you did wrong*, "
            "*that you are sorry*, *what you will do differently*.\n"
            "2. **Show a bad apology** — roleplay a forced, mumbled *sorry* and ask how that "
            "felt. Contrast with a genuine one.\n"
            "3. **Practise on a small thing** — find a recent moment where they could have "
            "apologised better. Roleplay it properly now.\n"
            "4. **No 'sorry but…'** — explain that adding *but* cancels the apology. Practise "
            "stopping after the sorry and the fix.\n"
            "5. **Repair something real** — if there is an outstanding situation, encourage "
            "them to apologise to the person today."
        ),
        "parent_note_md": (
            "A genuine apology requires humility and courage. Children who master this skill "
            "repair relationships faster, suffer less social exclusion, and grow into adults "
            "who take accountability. Avoid forcing a robotic apology in the heat of the "
            "moment — practise when calm so the template is available when emotions are high."
        ),
        "prereqs": [],
    },
    {
        "slug": "social-speak-up-when-wrong",
        "title": "Speak Up When Something Feels Wrong",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Normalise it** — explain that speaking up is brave, not troublemaking. "
            "Adults want to know when something is wrong.\n"
            "2. **Identify trusted adults** — together, list 3 adults they could tell: a "
            "parent, a teacher, a relative.\n"
            "3. **Roleplay scenarios** — *Someone takes your lunch. What do you say and to "
            "whom?* Work through 3-4 situations.\n"
            "4. **Practise the words** — *I need to tell you something important.* "
            "Have them say this to you clearly and calmly.\n"
            "5. **Confirm the safe-to-tell rule** — they will never get in trouble for telling "
            "a trusted adult about something that felt wrong."
        ),
        "parent_note_md": (
            "Children who can speak up protect themselves from bullying, unsafe situations, "
            "and injustice. Many children stay silent because they fear not being believed or "
            "being seen as weak. Reinforce consistently: telling is strength. Make sure your "
            "reaction when they do tell you something is calm and grateful, not alarmed — "
            "otherwise they will stop coming to you."
        ),
        "prereqs": [],
    },
    {
        "slug": "social-safety-secret",
        "title": "Know the Difference: Surprise vs Unsafe Secret",
        "min_age": 7, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define a surprise** — a surprise ends happily and is told eventually "
            "(birthday gift, party plan). Everyone feels good.\n"
            "2. **Define an unsafe secret** — something that makes you feel scared, "
            "uncomfortable, or confused, and an adult says not to tell.\n"
            "3. **Sort examples together** — give 5 scenarios and decide: surprise or unsafe "
            "secret? Discuss each one.\n"
            "4. **The no-secret-from-parents rule** — explain: no adult should ever ask you "
            "to keep a secret from your parents. If they do, tell a parent immediately.\n"
            "5. **Practise the phrase** — *I can't keep that secret. I need to tell my mum/dad.* "
            "Say it out loud three times."
        ),
        "parent_note_md": (
            "This is a child safety essential. Children who understand this distinction are "
            "significantly better protected against grooming. Keep the tone calm and matter-of-fact "
            "— you are giving them a tool, not frightening them. Revisit this conversation "
            "annually as they grow."
        ),
        "prereqs": [],
    },
    # ── Level 2 (age 8-11, simple prerequisites) ─────────────────────────
    {
        "slug": "social-accept-compliment",
        "title": "Accept a Compliment Gracefully",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the two wrong ways** — dismissing (*Oh it's nothing*) and boasting "
            "(*I know, I'm amazing*). Act both out and discuss why neither works.\n"
            "2. **Teach the right response** — make eye contact, smile, say *Thank you, that "
            "means a lot* or just *Thank you!*\n"
            "3. **Roleplay: give compliments, receive them** — take turns giving and accepting "
            "3 compliments each.\n"
            "4. **Add a bonus** — once comfortable, add something back: *Thank you — I worked "
            "hard on it.*\n"
            "5. **Real life test** — the next time someone gives them a genuine compliment, "
            "notice and discuss how they responded."
        ),
        "parent_note_md": (
            "Many children deflect compliments out of false modesty or discomfort with "
            "attention. Learning to accept praise graciously builds self-worth and encourages "
            "others to keep recognising their efforts. It is a small skill with outsized "
            "social impact."
        ),
        "prereqs": ["social-courtesy-words"],
    },
    {
        "slug": "social-give-compliment",
        "title": "Give a Genuine Compliment",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Distinguish genuine from flattery** — a genuine compliment is specific and "
            "true. Flattery is vague and just to please someone.\n"
            "2. **Good vs weak examples** — *Your drawing of the horse is really detailed* "
            "vs *You're so talented*. Discuss the difference.\n"
            "3. **Observation exercise** — look at something a family member did or made. "
            "Find one specific thing to compliment.\n"
            "4. **Delivery matters** — make eye contact, speak clearly, don't mumble.\n"
            "5. **Compliment someone outside the family** — a classmate, a teacher. Report "
            "back on how it was received."
        ),
        "parent_note_md": (
            "Children who give sincere, specific compliments are better liked and form "
            "stronger friendships. This skill also trains them to notice positive details "
            "about others — a habit that builds empathy and reduces social comparison."
        ),
        "prereqs": ["social-accept-compliment"],
    },
    {
        "slug": "social-write-thank-you",
        "title": "Write a Handwritten Thank You Note",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain why handwritten matters** — it takes more effort than a text and "
            "the recipient keeps it. It signals you truly care.\n"
            "2. **The three-sentence structure** — (1) Thank them for the specific thing. "
            "(2) Say what it means to you or how you will use it. (3) Warm closing.\n"
            "3. **Write a draft together** — pick a real situation: a gift, a kind act, a "
            "favour. Draft it on scrap paper first.\n"
            "4. **Write the final version** — neatly, on a card or folded paper. No crossings-out.\n"
            "5. **Deliver or post it** — hand it to the person or put it in the post. "
            "Discuss how it feels to send."
        ),
        "parent_note_md": (
            "Handwritten thank you notes are rare enough to be memorable. A child who sends "
            "them stands out positively to relatives, teachers, and eventually employers. "
            "This task also practices gratitude — one of the strongest predictors of "
            "wellbeing in children and adults."
        ),
        "prereqs": ["social-courtesy-words"],
    },
    {
        "slug": "social-ask-help-adult",
        "title": "Ask an Adult for Help Clearly",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Why children don't ask** — discuss the reasons: fear of seeming stupid, "
            "not wanting to bother anyone. Reframe: asking is smart.\n"
            "2. **The approach sequence** — walk up, wait for a pause, make eye contact, "
            "say *Excuse me, could you help me with something?*\n"
            "3. **State the problem clearly** — not *I don't get it* but *I don't understand "
            "step 3 of the maths problem. Can you show me?*\n"
            "4. **Roleplay with parent as teacher** — child approaches, asks for help with "
            "a specific thing. Practise 3 times.\n"
            "5. **Real test** — ask a teacher, librarian, or shop assistant for help with "
            "something real this week."
        ),
        "parent_note_md": (
            "Children who ask for help get unstuck faster and perform better academically. "
            "Many children suffer in silence because asking feels risky. Normalising "
            "help-seeking now prevents years of unnecessary struggle later. Celebrate every "
            "time they ask — never make them feel it was a burden."
        ),
        "prereqs": ["social-greet-adult"],
    },
    {
        "slug": "social-ask-follow-up",
        "title": "Ask Follow-Up Questions in a Conversation",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is a follow-up question?** — a question about what the other person "
            "just said. It shows you were listening.\n"
            "2. **Bad vs good** — they say *I went to the beach*. Bad follow-up: *I went to "
            "the beach once too.* Good: *What was the water like?*\n"
            "3. **Practise with a story** — tell a 1-minute story. Child must ask at least "
            "two follow-up questions before sharing anything about themselves.\n"
            "4. **The interest game** — pick any topic. Child must keep the conversation "
            "going with only questions for 2 minutes.\n"
            "5. **Real-life challenge** — in the next conversation with a friend or relative, "
            "ask at least one follow-up question. Report back."
        ),
        "parent_note_md": (
            "The ability to ask good questions is one of the rarest and most valued social "
            "skills. People who ask follow-up questions are universally described as great "
            "conversationalists and deep listeners. This habit also builds curiosity — "
            "a key driver of academic and lifelong success."
        ),
        "prereqs": ["social-listen-no-interrupt"],
    },
    {
        "slug": "social-order-restaurant",
        "title": "Order Food at a Restaurant Independently",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Before you arrive** — read the menu online or when seated. Decide what "
            "they want before the waiter comes.\n"
            "2. **The exchange** — when the waiter comes, they (not the parent) make eye "
            "contact and say what they would like. Clearly. With please.\n"
            "3. **Handle a question** — roleplay: waiter asks *What size? Any allergies?* "
            "Practise answering calmly.\n"
            "4. **Say thank you** — when food arrives and when the plate is cleared.\n"
            "5. **One step further** — ask the waiter a question themselves: *What do you "
            "recommend?* or *Is this spicy?*"
        ),
        "parent_note_md": (
            "Ordering at a restaurant seems small but involves making a decision, speaking "
            "clearly to a stranger, and handling the unexpected — all in a low-stakes "
            "environment. Children who do this regularly gain independence and lose the "
            "habit of hiding behind parents in unfamiliar social situations."
        ),
        "prereqs": ["social-greet-adult"],
    },
    {
        "slug": "social-handle-teasing",
        "title": "Handle Teasing Calmly",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Distinguish teasing from bullying** — friendly teasing is mutual and "
            "stops when you say stop. Bullying is repeated and one-sided.\n"
            "2. **Why reacting big makes it worse** — if teasing gets a big emotional "
            "reaction, it becomes more fun for the teaser.\n"
            "3. **Three tools** — (a) ignore and walk away, (b) agree with a smile (*Yeah, "
            "I know!*), (c) use humour (*Thanks for noticing!*).\n"
            "4. **Roleplay** — parent teases mildly, child practises the three tools. "
            "Debrief which felt easiest.\n"
            "5. **Know when to tell** — if teasing happens repeatedly or feels mean, that "
            "is when to tell a trusted adult."
        ),
        "parent_note_md": (
            "Children who can deflect teasing without overreacting are far less likely to "
            "become bullying targets. The key insight is that emotional reactions are fuel — "
            "removing the fuel removes the fun. The agree-and-deflect technique in particular "
            "is surprisingly powerful and disarms most teasers quickly."
        ),
        "prereqs": ["social-speak-up-when-wrong"],
    },
    {
        "slug": "social-leave-politely",
        "title": "End a Conversation and Leave Politely",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Why endings matter** — how you leave is the last impression. A good exit "
            "makes people want to talk to you again.\n"
            "2. **The formula** — (1) natural pause, (2) wrap-up phrase (*It was really "
            "nice talking to you*), (3) reason (*I need to go find my mum*), (4) farewell.\n"
            "3. **Avoid the awkward fade** — practise NOT just walking away mid-conversation.\n"
            "4. **Roleplay** — have a short conversation, then practise ending it three "
            "different ways.\n"
            "5. **Real test** — next time they are at a social event, notice how conversations "
            "end and try the formula at least once."
        ),
        "parent_note_md": (
            "Most children are taught how to start conversations but not how to end them. "
            "An awkward exit can undo a good interaction. This skill is particularly useful "
            "at family gatherings, social events, and school — anywhere children need to "
            "manage multiple social interactions in one session."
        ),
        "prereqs": ["social-greet-adult"],
    },
    # ── Level 3 (age 10-13, deeper skills) ───────────────────────────────
    {
        "slug": "social-introduce-yourself",
        "title": "Introduce Yourself to Someone New",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The three-part intro** — name, one relevant fact, one question back. "
            "Example: *Hi, I'm Aisha. I'm in Year 5. What about you?*\n"
            "2. **Keep it brief** — an introduction is an opener, not a speech. 2-3 "
            "sentences maximum.\n"
            "3. **Roleplay with parent** — swap roles several times. Parent models different "
            "reactions (shy, friendly, distracted).\n"
            "4. **Practise the uncomfortable bit** — walking up to someone you don't know. "
            "Role-play approaching from across the room.\n"
            "5. **Real test** — introduce themselves to one new person this week: a new "
            "classmate, a friend's sibling, a relative they rarely see."
        ),
        "parent_note_md": (
            "Self-introduction is the gateway to every new relationship. Children who can do "
            "this comfortably build social networks more easily and suffer less from the "
            "isolation that comes with shyness. The question at the end of the intro is the "
            "key — it shifts focus from them to the other person immediately."
        ),
        "prereqs": ["social-greet-adult"],
    },
    {
        "slug": "social-join-group-chat",
        "title": "Join a Group Conversation Already in Progress",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read the room** — watch for a moment when the group pauses or someone "
            "glances around. That is the opening.\n"
            "2. **Don't force entry** — hovering near the group and making eye contact is "
            "enough to signal you want to join. Wait for an acknowledgement.\n"
            "3. **First contribution** — add to what was just said rather than changing "
            "the subject. *Yeah, and another thing about that…*\n"
            "4. **Roleplay at home** — two family members chat. Child must find the right "
            "moment to join without interrupting.\n"
            "5. **Debrief** — after trying in real life, discuss: *How did you find the "
            "opening? What did you say first?*"
        ),
        "parent_note_md": (
            "Joining a group mid-conversation is one of the trickiest social moves for "
            "children and adults alike. Children who can do it confidently are far less "
            "likely to feel excluded. The key skill is patience — reading the conversation "
            "before diving in."
        ),
        "prereqs": ["social-introduce-yourself"],
    },
    {
        "slug": "social-take-turns-talk",
        "title": "Take Turns in a Conversation",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The conversation ball** — think of conversation like a ball being thrown. "
            "A good conversationalist throws it back every time.\n"
            "2. **Notice who is holding the ball** — after sharing something, consciously "
            "throw it back with a question or *What about you?*\n"
            "3. **Timed exercise** — set a 3-minute conversation timer. Each person must "
            "speak roughly equally. Count turns afterwards.\n"
            "4. **Spot the dominator** — watch a conversation (TV, family meal) and notice "
            "who dominates. Discuss why it feels uncomfortable.\n"
            "5. **Real challenge** — in the next group conversation, count how many times "
            "they throw the ball to someone else."
        ),
        "parent_note_md": (
            "Children who monopolise conversations push friends away without realising it. "
            "Learning to balance sharing and listening is one of the most important "
            "friendship skills. This exercise works best after a real-life example — "
            "reflect on a conversation they were part of where someone held the ball "
            "too long."
        ),
        "prereqs": ["social-ask-follow-up"],
    },
    {
        "slug": "social-say-no-confidently",
        "title": "Say No Confidently Without Over-Explaining",
        "min_age": 9, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **No is a complete sentence** — explain that they do not owe a reason for "
            "every refusal. A polite no is enough.\n"
            "2. **Practise saying no clearly** — *No thank you*, *I'd rather not*, "
            "*That's not for me*. Say each one out loud, confidently.\n"
            "3. **Handle the pushback** — roleplay: you keep pressing after they say no. "
            "They repeat calmly: *I said no. I mean it.*\n"
            "4. **Peer pressure scenarios** — work through 4 situations: skipping class, "
            "trying something they don't want to, leaving somewhere without telling parents.\n"
            "5. **Celebrate no** — when they say no to something appropriately, acknowledge "
            "how difficult that can feel and how proud you are."
        ),
        "parent_note_md": (
            "Children who cannot say no are vulnerable to peer pressure, boundary violations, "
            "and being taken advantage of. This skill protects them in adolescence more than "
            "almost any other. Practise in low-stakes situations so the muscle is strong "
            "when it really matters."
        ),
        "prereqs": ["social-speak-up-when-wrong"],
    },
    {
        "slug": "social-disagree-respectfully",
        "title": "Disagree Respectfully",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Separate idea from person** — disagreeing with what someone said is fine. "
            "Attacking them is not. The idea is wrong; the person is not stupid.\n"
            "2. **The formula** — *I see it differently… / I'm not sure I agree because… / "
            "Have you considered…?*\n"
            "3. **Never say 'you're wrong'** — practise replacing that phrase with *I think "
            "it might be…* or *What about…?*\n"
            "4. **Roleplay a friendly debate** — pick a low-stakes topic (best sport, "
            "best film). Each person takes a side and disagrees respectfully for 3 minutes.\n"
            "5. **Real test** — the next time they disagree with a teacher or parent, use "
            "the formula instead of sulking or arguing."
        ),
        "parent_note_md": (
            "Children who can disagree respectfully become adults who thrive in workplaces, "
            "partnerships, and civic life. This skill requires them to hold two things at "
            "once: confidence in their own view and genuine respect for the other person. "
            "Model it yourself — disagree with your child respectfully and name what you "
            "are doing."
        ),
        "prereqs": ["social-apologise-sincerely"],
    },
    {
        "slug": "social-resolve-conflict",
        "title": "Resolve a Conflict with a Friend",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Cool down first** — never try to resolve conflict when angry. "
            "Agree to talk when both people are calm.\n"
            "2. **I-statements only** — *I felt hurt when…* not *You always…* "
            "Practice turning you-statements into I-statements.\n"
            "3. **Listen to understand** — the other person gets to finish fully before "
            "responding. No interrupting.\n"
            "4. **Find common ground** — what does each person actually want? Usually "
            "it is the same thing (to feel respected, to feel heard).\n"
            "5. **Agree on next steps** — end with a specific commitment: *Next time I'll "
            "tell you before I'm upset.* Shake on it."
        ),
        "parent_note_md": (
            "The ability to resolve conflict without adult intervention is one of the "
            "strongest predictors of social success in adolescence. Children who learn this "
            "have longer, more stable friendships and handle difficult people better as "
            "adults. Resist the urge to fix conflicts for them — coach from the sideline instead."
        ),
        "prereqs": ["social-apologise-sincerely"],
    },
    {
        "slug": "social-receive-criticism",
        "title": "Receive Criticism Without Getting Defensive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Reframe criticism** — useful criticism is information, not an attack. "
            "The person offering it usually wants you to improve.\n"
            "2. **The pause** — train the instinct to pause before responding. Take a breath. "
            "Do not react immediately.\n"
            "3. **Acknowledge and clarify** — *Thanks for telling me. Can you say more about "
            "what you mean?* shows maturity and gets better information.\n"
            "4. **Roleplay: hard feedback** — parent gives critical feedback on something "
            "real (tidiness, attitude, schoolwork). Child practises not getting defensive.\n"
            "5. **The test** — next time a teacher returns marked work, respond with "
            "*What could I do better?* Report back."
        ),
        "parent_note_md": (
            "Defensiveness in response to criticism is the single biggest obstacle to growth. "
            "Children who can hear feedback calmly improve faster in every area — "
            "academic, sporting, social. This skill is particularly hard for children "
            "with perfectionist tendencies. Be patient and model it yourself: ask your "
            "child for feedback on your parenting and respond graciously."
        ),
        "prereqs": ["social-disagree-respectfully"],
    },
    {
        "slug": "social-read-body-language",
        "title": "Read Basic Body Language",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The basics** — arms crossed (defensive/cold), eye contact (engaged), "
            "phone out while talking (disinterested), leaning in (interested).\n"
            "2. **TV observation** — mute a show. Watch two characters interact. What is "
            "each person feeling? Un-mute and check.\n"
            "3. **Real life scan** — at the dinner table or on a bus, quietly observe one "
            "person. What emotion or state do their body and face signal?\n"
            "4. **Practise signalling yourself** — demonstrate interested body language: "
            "lean slightly forward, make eye contact, nod.\n"
            "5. **In conversation** — notice one thing about the other person's body "
            "language and adjust accordingly (slow down if they seem bored, etc.)."
        ),
        "parent_note_md": (
            "Over 50% of communication is non-verbal. Children who can read body language "
            "are more empathetic, better at conflict prevention, and more socially attuned. "
            "This skill is particularly valuable for children who struggle with social cues "
            "or have been described as oblivious to others' feelings."
        ),
        "prereqs": ["social-ask-follow-up"],
    },
    {
        "slug": "social-handle-left-out",
        "title": "Handle Being Left Out",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the feeling** — being left out hurts. That is normal and does not "
            "mean something is wrong with you.\n"
            "2. **Distinguish accident from intention** — sometimes it is oversight, "
            "sometimes it is exclusion. They need different responses.\n"
            "3. **The three options** — (a) ask to join, (b) find something else to do, "
            "(c) talk to a trusted adult if it is repeated.\n"
            "4. **Practise asking to join** — *Hey, can I play too?* Simple, direct, "
            "without embarrassment. Roleplay it.\n"
            "5. **Build another relationship** — identify one other person they could spend "
            "time with. Feeling left out hurts less with more than one friend."
        ),
        "parent_note_md": (
            "Social exclusion is one of the most painful experiences in childhood. Children "
            "who have strategies for handling it cope better and recover faster. The biggest "
            "gift you can give them is helping them see that being left out occasionally is "
            "universal — not a verdict on their worth."
        ),
        "prereqs": ["social-handle-teasing"],
    },
    {
        "slug": "social-make-phone-call",
        "title": "Make a Phone Call to a Business or Adult",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Prepare before calling** — know the name of the person or place, the "
            "purpose of the call, and any information you might need to give.\n"
            "2. **Opening line** — *Hello, my name is [name]. I'm calling about [reason]. "
            "Is this a good time?*\n"
            "3. **Speak slowly and clearly** — phone calls remove body language. "
            "Pace and clarity matter more than usual.\n"
            "4. **Roleplay first** — parent plays a receptionist or adult. Child calls "
            "with a real purpose (booking, enquiry, leaving a message).\n"
            "5. **Real call** — place a real low-stakes call: ask a relative a question, "
            "enquire about opening hours, book an appointment."
        ),
        "parent_note_md": (
            "Young people increasingly avoid phone calls due to anxiety — they prefer texts "
            "and messages. But phone calls are unavoidable in adult life: GPs, employers, "
            "banks, schools. Building comfort with this now prevents significant anxiety "
            "later. Start with a friendly call to a relative, then build up to a business."
        ),
        "prereqs": ["social-introduce-yourself"],
    },
    {
        "slug": "social-write-formal-email",
        "title": "Write a Clear Formal Email or Letter",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The structure** — Subject line, greeting (*Dear Mr/Ms [name],*), "
            "clear opening sentence stating purpose, body, polite closing, name.\n"
            "2. **Subject line matters** — it must be specific. *Question* is bad. "
            "*Year 6 trip permission — question about date* is good.\n"
            "3. **One purpose per email** — do not cram multiple requests. One thing, "
            "clearly stated.\n"
            "4. **Proofread** — read it aloud before sending. Fix anything that sounds odd.\n"
            "5. **Real email** — write and send (with your supervision) an email to a "
            "teacher, club organiser, or librarian about something real."
        ),
        "parent_note_md": (
            "Formal written communication is a life skill that is increasingly rare. "
            "Children who can write a clear, professional email stand out dramatically in "
            "school, university applications, and the workplace. Start with email since "
            "it is the most common format — handwritten letters can follow once the "
            "structure is mastered."
        ),
        "prereqs": ["social-write-thank-you"],
    },
]

# slug → is_mandatory prerequisite slugs
PREREQ_EDGES = [
    # slug, prereq_slug, mandatory
    ("social-accept-compliment",  "social-courtesy-words",       True),
    ("social-give-compliment",    "social-accept-compliment",    True),
    ("social-write-thank-you",    "social-courtesy-words",       True),
    ("social-ask-help-adult",     "social-greet-adult",          True),
    ("social-ask-follow-up",      "social-listen-no-interrupt",  True),
    ("social-order-restaurant",   "social-greet-adult",          True),
    ("social-handle-teasing",     "social-speak-up-when-wrong",  True),
    ("social-leave-politely",     "social-greet-adult",          True),
    ("social-introduce-yourself", "social-greet-adult",          True),
    ("social-join-group-chat",    "social-introduce-yourself",   True),
    ("social-take-turns-talk",    "social-ask-follow-up",        True),
    ("social-say-no-confidently", "social-speak-up-when-wrong",  True),
    ("social-disagree-respectfully", "social-apologise-sincerely", True),
    ("social-resolve-conflict",   "social-apologise-sincerely",  True),
    ("social-receive-criticism",  "social-disagree-respectfully", True),
    ("social-read-body-language", "social-ask-follow-up",        True),
    ("social-handle-left-out",    "social-handle-teasing",       True),
    ("social-make-phone-call",    "social-introduce-yourself",   True),
    ("social-write-formal-email", "social-write-thank-you",      True),
]


class Command(BaseCommand):
    help = "Seed the Social & Communication task category (idempotent)."

    def handle(self, *args, **options):
        # Create tag
        tag, created = Tag.objects.get_or_create(
            name="Social skills",
            defaults={"category": Tag.Category.SOCIAL},
        )
        if not created and tag.category != Tag.Category.SOCIAL:
            tag.category = Tag.Category.SOCIAL
            tag.save()

        # Fetch all environments
        envs = {e.kind: e for e in Environment.objects.all()}
        all_envs = list(envs.values())

        # Create / update tasks
        for t in SOCIAL_TASKS:
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

        self.stdout.write(f"Upserted {len(SOCIAL_TASKS)} social tasks.")

        # Wire prerequisite edges
        task_map = {t.slug: t for t in Task.objects.filter(
            slug__in=[t["slug"] for t in SOCIAL_TASKS]
        )}
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
        self.stdout.write(self.style.SUCCESS("seed_social_catalog complete."))
