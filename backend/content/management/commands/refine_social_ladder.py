"""Management command: refine the Social task ladder.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py refine_social_ladder

Four phases, all idempotent:
  1. De-duplicate: remove 2 tasks that duplicate existing skills
  2. Retune: stage age ranges cleanly so age-5/6 tasks hand off to 7-9 tasks
  3. Add 22 new tasks filling gaps at ages 5-6, 7-9, 9-11, 11-13, 13-15
  4. Wire the prerequisite DAG — 30+ edges connecting the ladder properly
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Phase 1 — Duplicates to delete
# ---------------------------------------------------------------------------

DELETE_SLUGS = [
    "self-advocacy-asking-for-help",  # triplicate of social-ask-help-adult + ask-teacher-help-age6
    "write-a-thank-you-note",         # duplicate of social-write-thank-you
]

# ---------------------------------------------------------------------------
# Phase 2 — Age range updates
# ---------------------------------------------------------------------------

AGE_RANGE_UPDATES = [
    ("manage-online-relationships-age15", 13, 16),
    ("mentor-younger-child-age14",        12, 15),
    ("social-make-phone-call",             9, 12),
    # Stage age-5/6 tasks so they hand off cleanly to the 7-9 tier
    ("say-please-thankyou-age6",           6, 7),
    ("say-sorry-mean-it-age5",             5, 6),
    ("greet-adults-age6",                  6, 7),
    ("wait-to-speak-age5",                 5, 6),
    ("ask-teacher-help-age6",              6, 7),
]

# ---------------------------------------------------------------------------
# Phase 3 — New tasks (22 total)
# ---------------------------------------------------------------------------

NEW_TASKS = [
    # ── Age 5-6 (4 tasks) ───────────────────────────────────────────────
    {
        "slug": "make-eye-contact-age5",
        "title": "Look at the Person Who Is Talking to You",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain why eye contact matters** — *When you look at someone, "
            "they know you are listening. It's polite and makes people feel heard.*\n"
            "2. **Demonstrate both ways** — look them in the eye while talking, "
            "then look at the floor while talking. Ask which felt better.\n"
            "3. **The 'count to three' trick** — when someone talks to them, "
            "look at the person's eyes while silently counting to three. Then reply.\n"
            "4. **Practise at mealtimes** — each person at the table takes a turn "
            "speaking. The others must look at the speaker.\n"
            "5. **Gentle reminders** — if they drift off, a light touch on the arm "
            "or saying their name brings the eyes back. No shame, just practice."
        ),
        "parent_note_md": (
            "Eye contact is the quietest, most important social signal — it tells "
            "the other person you are present. Children who struggle with it are "
            "perceived as uninterested or shy, even when they are neither. "
            "For children who find eye contact very uncomfortable, aim for the "
            "forehead or nose area — it looks the same from the speaker's side."
        ),
    },
    {
        "slug": "comfort-someone-sad-age5",
        "title": "Comfort Someone Who Looks Sad",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Notice the feeling** — *Look at Appa's face. How do you think "
            "he's feeling right now?* Practise reading feelings from faces.\n"
            "2. **Teach the simple words** — *Are you OK? Do you want a hug? "
            "Can I help?* Practise saying them out loud.\n"
            "3. **A kind action** — a hug, a drawing, bringing them their favourite "
            "toy, sitting next to them quietly. All are forms of comfort.\n"
            "4. **Don't fix, just be there** — explain that you don't have to make "
            "the sadness go away. Sometimes being there is enough.\n"
            "5. **Practise with a puppet or toy** — the toy is sad. What does your "
            "child do or say? Roleplay builds the instinct for when it's real."
        ),
        "parent_note_md": (
            "Empathy — noticing and responding to another person's feelings — is "
            "the foundation of every caring relationship. Children who learn to "
            "comfort at 5 carry that instinct into adulthood. When your child is "
            "sad, model exactly the behaviour you want them to learn: notice, ask, "
            "offer comfort."
        ),
    },
    {
        "slug": "say-goodbye-properly-age5",
        "title": "Say Goodbye Before You Leave",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **State the rule** — *When we leave, we say goodbye. We don't just walk away. "
            "That is the polite thing to do.*\n"
            "2. **Demonstrate a warm goodbye** — look at the person, smile, "
            "say *Goodbye [name]! See you soon.*\n"
            "3. **Practise at home** — roleplay leaving a friend's house. "
            "They walk to the door, turn, and say goodbye. Practise 3 times.\n"
            "4. **Real situations** — before leaving relatives or friends, "
            "prompt them: *How do we leave?* Let them lead.\n"
            "5. **The wave and smile** — if they're shy, even a wave and smile "
            "with no words is a start. Build from there."
        ),
        "parent_note_md": (
            "The way a child leaves is often remembered more than how they arrived. "
            "A warm goodbye makes the other person want to see them again. "
            "Children who slip away silently can come across as rude even when "
            "they're simply shy — teaching this reframes leaving as a social act, "
            "not a disappearance."
        ),
    },
    {
        "slug": "ask-before-taking-age5",
        "title": "Ask Before Taking Something That Isn't Yours",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define the rule simply** — *If it's not yours, ask first.* "
            "Even if it's a family thing like a phone or the remote.\n"
            "2. **Teach the ask** — *Can I please use this? Can I have some?* "
            "Practise saying it calmly.\n"
            "3. **Handle a no** — sometimes the answer is no. "
            "Practise the calm response: *OK* and walking away.\n"
            "4. **At a friend's house** — remind them before going: *If you want "
            "to play with any of their toys, ask first. Don't just take.*\n"
            "5. **Notice and praise it** — when they ask instead of grabbing, "
            "say so: *You asked before taking — that was really good manners.*"
        ),
        "parent_note_md": (
            "The habit of asking before taking protects friendships, prevents "
            "theft accusations later in school, and builds the concept of "
            "consent and boundaries. Children who grab without asking are often "
            "not malicious — they just haven't been taught. The fix is simple "
            "and powerful."
        ),
    },
    # ── Age 7-9 (4 tasks) ───────────────────────────────────────────────
    {
        "slug": "start-play-new-child-age7",
        "title": "Start Playing with a Child You Don't Know",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The approach** — walk up, smile, say *Hi, I'm [name]. "
            "What are you playing?*\n"
            "2. **Ask to join** — *Can I play too?* or *That looks fun — "
            "can I join in?* Simple, direct.\n"
            "3. **Handle a no gracefully** — sometimes children say no. "
            "That's OK. *No worries!* and walk away. No showing hurt.\n"
            "4. **Practise in low-stakes settings** — park, community event, "
            "family gathering where there are unknown kids.\n"
            "5. **Reflect after** — how did it go? What felt easy or hard? "
            "Getting braver at this takes repetitions."
        ),
        "parent_note_md": (
            "The ability to walk up to a stranger child and start playing is one "
            "of the most freeing social skills a child can have. It means they're "
            "never stuck alone at a park, a party, or a new school. Most children "
            "need encouragement and modelling — few figure this out unprompted."
        ),
    },
    {
        "slug": "gracious-winner-loser-age7",
        "title": "Be a Good Winner and a Good Loser",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set the rules before the game** — *We play to have fun. "
            "No gloating if we win, no tantrums if we lose.*\n"
            "2. **Model it yourself** — when you win a game with them, say: "
            "*Good game!* When you lose: *You played really well.*\n"
            "3. **What to say when winning** — *Good game!* or *That was close!* "
            "Never *I told you I'd win* or a victory dance.\n"
            "4. **What to say when losing** — *Well played* or *Good game — "
            "can we play again?* Tears and flipping the board are not options.\n"
            "5. **Walk away if needed** — if they feel very upset, it's OK to "
            "leave the game for a minute and come back calm. Learn self-regulation."
        ),
        "parent_note_md": (
            "How a child handles winning and losing shapes their character — and "
            "other children's willingness to play with them. Gracious winners are "
            "admired; poor losers are excluded. This is best taught at home where "
            "losing regularly is safe. Let them lose; don't let them win."
        ),
    },
    {
        "slug": "include-someone-alone-age7",
        "title": "Include Someone Who Is on Their Own",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Notice who is alone** — at the park, in class, at a party. "
            "A child on the side, not playing. That is the one to include.\n"
            "2. **The simple invite** — *Hey, do you want to play with us?* "
            "That's all. No long speech.\n"
            "3. **Make them feel welcome** — introduce them to others, "
            "tell them the rules of the game, give them a turn.\n"
            "4. **Handle shyness** — if they say no or look unsure, try once more: "
            "*We'd like you to.* If still no, that's OK.\n"
            "5. **Reflect on the feeling** — how did it feel to include someone? "
            "How do you think they felt?"
        ),
        "parent_note_md": (
            "Being the kid who notices someone alone and invites them in changes "
            "the whole social temperature of a group. These children become "
            "genuine leaders — not by dominating, but by making space. "
            "This act, practised early and often, shapes a lifelong habit of "
            "generosity."
        ),
    },
    {
        "slug": "small-talk-basics-age8",
        "title": "Have a Short Small-Talk Conversation",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is small talk** — a short, friendly chat that's not about "
            "anything deep. *How are you? How was your weekend? Nice weather.*\n"
            "2. **The open-question rule** — *How was your day?* invites a real "
            "answer. *Did you have a good day?* gets only yes/no.\n"
            "3. **Follow up on what they say** — they say *I went to my grandma's.* "
            "You say *Oh nice! Did you do anything fun there?*\n"
            "4. **Practise with 2 adults they know** — uncle, neighbour, friend's parent. "
            "A 2-minute chat. Ask one question, listen, ask a follow-up.\n"
            "5. **Debrief** — how did it feel? Did the person smile and respond? "
            "Small talk is a warm-up, not a performance."
        ),
        "parent_note_md": (
            "Small talk is genuinely undervalued. It's how we show up warmly in "
            "lifts, waiting rooms, parties, and checkout queues — the "
            "micro-interactions that make up most social life. Children who can "
            "do small talk comfortably are never awkwardly silent in shared spaces."
        ),
    },
    # ── Age 9-11 (4 tasks) ──────────────────────────────────────────────
    {
        "slug": "keep-positive-secret-age9",
        "title": "Keep a Positive Secret",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the difference** — a positive secret is a surprise that "
            "will end with someone feeling happy. A birthday gift, a surprise party.\n"
            "2. **Contrast with unsafe secrets** — if an adult ever says *don't tell "
            "your parents*, that is NOT a positive secret — tell a parent immediately.\n"
            "3. **Practise holding the secret** — a parent tells the child something "
            "small (a gift they bought for the other parent). Can they keep it for 3 days?\n"
            "4. **The test of temptation** — sometimes people hint or ask. "
            "Practise the response: *It's a surprise — you'll have to wait!*\n"
            "5. **Celebrate when revealed** — when the secret is finally shared, "
            "acknowledge the effort: *You kept that secret really well.*"
        ),
        "parent_note_md": (
            "Being able to keep a positive secret is a sign of self-control and "
            "trustworthiness — qualities friends and family rely on. The more "
            "important lesson is the distinction: positive secrets end in joy; "
            "secrets that feel heavy or involve adults telling them to hide things "
            "are never OK."
        ),
    },
    {
        "slug": "respect-privacy-age9",
        "title": "Respect Other People's Privacy",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the rule** — *Knock before entering a closed door. "
            "Don't read other people's messages. Don't open other people's drawers.*\n"
            "2. **Their own privacy too** — they also deserve privacy. "
            "Agree together on what is private in the family.\n"
            "3. **The knock-and-wait** — at a closed door, knock and wait for "
            "*come in.* Don't push through.\n"
            "4. **Digital privacy** — don't read a sibling's or parent's messages "
            "on an unlocked phone. Even if you could, you don't.\n"
            "5. **What to do if you see something by accident** — don't share it. "
            "Pretend you didn't see it. Privacy is about restraint."
        ),
        "parent_note_md": (
            "Respecting privacy at 9 lays the groundwork for respecting consent, "
            "digital boundaries, and adult relationships. It is also a marker of "
            "maturity — children who can restrain natural curiosity about siblings' "
            "things are demonstrating exactly the self-control they'll need "
            "elsewhere in life."
        ),
    },
    {
        "slug": "own-up-to-mistake-age9",
        "title": "Admit a Mistake Without Being Asked",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Reframe mistakes** — everyone makes them. The shame is in hiding, "
            "not in making them.\n"
            "2. **The sooner the better** — admit it quickly, not after being caught. "
            "Admitting first dramatically reduces consequences.\n"
            "3. **The formula** — *I did X. I shouldn't have. I'm sorry. Next time, "
            "I'll do Y.* Four short sentences.\n"
            "4. **No blame-shifting** — even if someone else was involved, own your part. "
            "*We all did it* is not an apology.\n"
            "5. **Trust it** — as a parent, consistently respond calmly to "
            "self-admitted mistakes. Over-reacting teaches children to hide them."
        ),
        "parent_note_md": (
            "Self-admission of mistakes is one of the surest signs of integrity. "
            "Children who can do this are trusted more, by teachers, employers, "
            "and future partners. The parent's role here is critical: punishing "
            "a self-admitted mistake severely teaches children to hide next time. "
            "Reward the honesty, address the behaviour."
        ),
    },
    {
        "slug": "recognise-bullying-age10",
        "title": "Recognise When Someone Is Being Bullied",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define bullying clearly** — repeated, deliberate unkindness that "
            "has a power imbalance. One person picking on another, not a one-off argument.\n"
            "2. **Types of bullying** — physical (hitting, pushing), verbal (name-calling, "
            "teasing), social (excluding, spreading rumours), online (mean messages, "
            "leaving out of group chats).\n"
            "3. **Warning signs in the victim** — avoiding school, not eating, "
            "losing things, saying they don't want to go somewhere they used to enjoy.\n"
            "4. **Roleplay scenarios** — discuss 3 situations. Is this bullying or "
            "friendly teasing? What's the difference?\n"
            "5. **What to do if they see it** — don't join in (even by laughing). "
            "Tell a trusted adult. If it's safe, speak up in the moment."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Telling an adult about bullying is never *snitching*. "
            "It is the right thing to do.\n"
            "- If the bullying involves threats of violence, weapons, or self-harm, "
            "tell a parent or teacher IMMEDIATELY, not later."
        ),
        "parent_note_md": (
            "Most children witness bullying before they ever experience it themselves. "
            "Recognising it — knowing what counts and what doesn't — is the first step. "
            "Children who can identify bullying are better positioned to help friends, "
            "tell adults, and protect themselves."
        ),
    },
    # ── Age 11-13 (5 tasks) ─────────────────────────────────────────────
    {
        "slug": "support-sad-friend-age11",
        "title": "Support a Friend Who Is Sad or Upset",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Notice before asking** — when a friend seems off, notice it. "
            "*You seem quiet today. Are you OK?* is often enough to open a conversation.\n"
            "2. **Listen first, advise never** — most people who are sad don't "
            "want solutions. They want to feel heard. Let them talk.\n"
            "3. **Don't minimise** — don't say *it's not that bad* or *at least…* "
            "Those comments, even kindly meant, dismiss the feeling.\n"
            "4. **Offer something specific** — *Want to walk home together? "
            "Want to come over after school?* Specific beats vague *let me know*.\n"
            "5. **Check in later** — a day or two after, ask how they are doing. "
            "Showing you remembered matters enormously."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If a friend mentions hurting themselves, hurting someone else, "
            "or not wanting to be alive, tell a parent or trusted adult immediately. "
            "A kept confidence that risks a life is never the right choice."
        ),
        "parent_note_md": (
            "Being the friend who shows up when things are hard is one of the most "
            "valuable things a person can be. Most adults never learn this — they "
            "try to fix, minimise, or disappear. Children who learn it at 11 have "
            "stronger friendships for life and are more protected themselves when "
            "they need support."
        ),
    },
    {
        "slug": "online-stranger-safety-age11",
        "title": "Stay Safe When Strangers Contact You Online",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define an online stranger** — someone you have not met in person. "
            "It doesn't matter how long you've chatted — if you haven't met, they're a stranger.\n"
            "2. **Red flags** — asking your age, your school, where you live, "
            "asking for photos, asking to keep the conversation secret, "
            "being unusually complimentary.\n"
            "3. **The rule: never meet in person** — no matter what. "
            "Strangers who ask to meet are strangers to be reported, always.\n"
            "4. **Block and report** — teach how to use the block button on every "
            "platform they use. Use it without guilt.\n"
            "5. **Tell a parent, no trouble** — promise them in advance: "
            "reporting anything concerning will never get their device taken away. "
            "They must trust you to keep them safe, not punish them."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Online grooming often begins with flattery, gifts (even virtual — "
            "game items, currency), and gradually moving to private chat.\n"
            "- Any request for a photo should be refused and reported.\n"
            "- The *secret friend* framing is always a red flag."
        ),
        "parent_note_md": (
            "Online grooming is the single biggest safeguarding threat to children "
            "aged 10–15. Conversations that start in gaming chat and move to private "
            "messaging apps follow a predictable pattern. Children who know the red "
            "flags — and who trust they can come to you without losing their device — "
            "are significantly safer."
        ),
    },
    {
        "slug": "handle-friendship-drift-age12",
        "title": "Handle a Friendship That is Changing",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Normalise it** — friendships change as people grow. This is normal "
            "and does not mean anything is wrong with either person.\n"
            "2. **Notice the pattern** — are we hanging out less? "
            "Are conversations shorter? Is there a specific reason?\n"
            "3. **Talk about it if you can** — *I feel like we're not spending as "
            "much time together. Is everything OK?* Sometimes this reconnects you.\n"
            "4. **Accept what you can't control** — if the other person has moved on, "
            "forcing it doesn't work. Let it be what it is.\n"
            "5. **Invest in other connections** — grief about one friendship is less "
            "crushing when you have others. Actively spend time with people who make you feel good."
        ),
        "parent_note_md": (
            "Friendships shift dramatically between ages 11–14 as interests, schools, "
            "and social groups change. This is painful and normal. Children who "
            "understand that drift is not failure — and who know how to invest in "
            "new connections rather than cling — navigate the middle years far better."
        ),
    },
    {
        "slug": "recognise-toxic-friendship-age12",
        "title": "Recognise an Unhealthy Friendship",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Warning signs** — a friend who puts you down, makes you feel "
            "anxious, pressures you into things, gets jealous when you hang out "
            "with others, or makes everything about them.\n"
            "2. **The 'after-effect' test** — how do you feel after spending time "
            "with this person? Energised or drained? Happy or anxious? The feeling tells you.\n"
            "3. **Distinguish bad days from patterns** — everyone has off days. "
            "A toxic pattern is consistent, not occasional.\n"
            "4. **Options** — address it directly (*When you do X, I feel Y*), "
            "reduce contact, or end the friendship. All are valid.\n"
            "5. **Talk to a trusted adult** — when a friendship feels unhealthy, "
            "a parent or counsellor can help you see it more clearly."
        ),
        "parent_note_md": (
            "Learning to recognise toxic patterns in friendships at 12 is the "
            "foundation of recognising them in romantic relationships at 16 and in "
            "workplaces at 22. Children who can name what makes a friendship "
            "unhealthy are better equipped to choose their circles throughout life. "
            "The after-effect test is particularly powerful."
        ),
    },
    {
        "slug": "group-chat-etiquette-age12",
        "title": "Navigate a Group Chat Respectfully",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The gossip rule** — if you wouldn't say it to the person's face, "
            "don't type it in a group chat. Screenshots travel.\n"
            "2. **Don't pile on** — when one person is being picked on, don't join in. "
            "Even a laugh emoji counts as piling on.\n"
            "3. **The 24-hour rule** — if angry or upset, wait before typing. "
            "Messages you send in a rage live forever.\n"
            "4. **Exit gracefully** — if a chat becomes unkind, it's OK to leave "
            "or mute it. You don't have to be in every group.\n"
            "5. **Don't screenshot private chats** — keeping private messages private "
            "is a basic trust rule. Breaking it damages relationships permanently."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If you are in a group chat where someone is being bullied, "
            "tell an adult. Don't just leave.\n"
            "- Never send or forward inappropriate images — it is illegal "
            "and harmful, even if sent as a joke."
        ),
        "parent_note_md": (
            "Group chats are where most teenage social conflict now plays out. "
            "The same social rules apply — don't gossip, don't pile on, don't "
            "share private content — but they're often forgotten in the immediacy "
            "of typing. A clear set of principles, discussed openly, helps children "
            "navigate the medium without losing their values."
        ),
    },
    # ── Age 13-15 (5 tasks) ─────────────────────────────────────────────
    {
        "slug": "body-autonomy-consent-age13",
        "title": "Understand Body Autonomy and Consent",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The core principle** — your body belongs to you. No one has the "
            "right to touch you in any way you don't want — not friends, family, partners.\n"
            "2. **Consent is specific and active** — silence is not consent. "
            "Saying yes once doesn't mean yes forever. Consent can be withdrawn at any point.\n"
            "3. **The same applies to others** — you must respect other people's "
            "bodies too. Never assume. Always ask.\n"
            "4. **Pressure is not consent** — if someone agrees after being pressured, "
            "that is not real agreement. Never pressure anyone, physically or emotionally.\n"
            "5. **Who to tell if something happens** — a parent, a school counsellor, "
            "a helpline (Childline 1098). Violations of consent are never your fault, regardless of circumstances."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- If anyone touches you in a way you don't want — even a relative or friend — "
            "tell a trusted adult immediately. You will be believed.\n"
            "- Childline India: 1098 (free, 24-hour helpline for children).\n"
            "- Online harassment, unwanted images, or pressure are also violations "
            "of body autonomy — same rules apply."
        ),
        "parent_note_md": (
            "Body autonomy and consent are foundational safeguarding concepts. "
            "They apply to friends, relatives, romantic partners, and strangers. "
            "Having this conversation openly at 13 — before dating and sexual "
            "development complicate it — gives children the vocabulary and "
            "framework to recognise and respond to violations. Keep the tone "
            "matter-of-fact and non-judgemental."
        ),
    },
    {
        "slug": "handle-first-crush-age13",
        "title": "Handle a Crush or Romantic Feelings Respectfully",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Normalise the feeling** — crushes are normal and healthy. "
            "They don't have to be acted on. They don't have to be hidden.\n"
            "2. **No pressure on the other person** — never assume the other person "
            "feels the same. Don't push, don't expect, don't make them feel awkward.\n"
            "3. **Be prepared for rejection** — sometimes feelings aren't mutual. "
            "That is not a failure — it is information. Handle it with grace.\n"
            "4. **Respect their choice completely** — if someone says no, that is final. "
            "No continuing to pursue, no asking friends to lobby, no anger.\n"
            "5. **Talk to someone trusted** — a parent, an older sibling, a close friend. "
            "First crushes feel huge; talking helps keep them in perspective."
        ),
        "parent_note_md": (
            "First crushes shape the pattern of how a young person handles romantic "
            "feelings for years to come. Teenagers who learn early that crushes "
            "don't entitle them to anything — and that rejection is not a wound — "
            "avoid much of the drama that surrounds adolescent relationships. "
            "Keep communication open; children who can discuss crushes with parents "
            "are safer and less confused."
        ),
    },
    {
        "slug": "act-on-bullying-witness-age13",
        "title": "Act When You Witness Bullying",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The three safe options** — (a) interrupt directly if safe to do so, "
            "(b) support the victim privately afterwards, (c) tell a trusted adult. "
            "Any of these are real action.\n"
            "2. **Direct interruption** — if safe: *That's not cool, stop.* "
            "Or distract: *Hey, come look at this over here.* Breaking the dynamic often ends it.\n"
            "3. **Support privately** — if you can't speak up in the moment, "
            "find the victim afterwards. *I saw what happened. That was wrong. Are you OK?*\n"
            "4. **Tell an adult** — reporting is not snitching. If it is repeated or serious, "
            "an adult needs to know. Anonymously if necessary.\n"
            "5. **Don't be the bystander** — walking away silently makes bullying worse. "
            "Choose one of the three options every time."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never intervene if there is physical danger. Get an adult immediately.\n"
            "- Cyberbullying evidence should be screenshotted before telling an adult — "
            "it may be deleted by the time you tell.\n"
            "- Your safety matters too. Choose the action that is safe for you."
        ),
        "parent_note_md": (
            "Bystanders are the deciding factor in most bullying situations. "
            "A bullying incident that gets a laugh from onlookers escalates; "
            "one that gets silence or interruption often ends. Teenagers who know "
            "they have three safe options — and that any of them is real help — "
            "are much more likely to act. Not acting is a choice with consequences too."
        ),
    },
    {
        "slug": "ask-for-what-you-need-age13",
        "title": "Ask for What You Need in a Relationship",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Identify what you need** — often people are upset without knowing "
            "why. Practise naming it: *I need more time with you. I need you to listen "
            "without fixing. I need space right now.*\n"
            "2. **Ask calmly, not as a demand** — *Could you…* or *I'd really appreciate "
            "if…* rather than *You never…* or *Why can't you just…*\n"
            "3. **Pick the right moment** — not when you or they are angry or busy. "
            "A calm moment with time to talk.\n"
            "4. **Accept it may take a few tries** — people don't always change on "
            "the first ask. Repeat calmly. If it never happens, that's also information.\n"
            "5. **Also ask what they need** — relationships are two-way. "
            "Ask in return. A conversation, not a monologue."
        ),
        "parent_note_md": (
            "Most relationship problems — with friends, family, future partners — "
            "stem from unspoken needs. Teenagers who learn to ask for what they "
            "need, calmly and directly, have dramatically healthier relationships "
            "throughout life. This is especially important for children who tend "
            "to sulk, shut down, or expect others to guess."
        ),
    },
    {
        "slug": "find-place-new-group-age14",
        "title": "Find Your Place in a New Social Group",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Observe first** — in any new group, spend the first few sessions "
            "noticing: who are the leaders? What's the group humour? "
            "How do people talk to each other?\n"
            "2. **Contribute early, but not too much** — say something the first or "
            "second session. Don't wait weeks. But also don't try to dominate.\n"
            "3. **Find your natural role** — are you the joker, the organiser, the "
            "quiet one with good ideas, the listener? Being yourself works better than performing.\n"
            "4. **Invest in one person first** — make one real connection rather than "
            "try to befriend everyone. That person will then bring you into the rest.\n"
            "5. **Give it time** — three to five sessions minimum before judging whether "
            "the group works for you. First impressions mislead."
        ),
        "parent_note_md": (
            "Finding your place in a new group — a new school, a new club, a new "
            "workplace — is a skill that transfers across a lifetime. Teenagers "
            "who can do this calmly settle into new environments faster, "
            "have more options, and suffer less from the isolation that comes "
            "with change. The *observe first* step is what most people get wrong — "
            "they either hide or try too hard."
        ),
    },
]

# ---------------------------------------------------------------------------
# Phase 4 — Prerequisite edges: (to_slug, from_slug, mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    # Missing chains in existing ladder
    ("resolve-conflict-peer-age14",           "social-resolve-conflict",       True),
    ("empathy-perspective-age14",             "social-read-body-language",     True),
    ("active-listening-age14",                "social-listen-no-interrupt",    True),
    ("give-constructive-feedback-age15",      "social-disagree-respectfully",  True),
    ("set-communicate-boundaries-age16",      "social-say-no-confidently",     True),
    ("support-peer-difficulty-age16",         "active-listening-age14",        True),
    ("introduce-professionally-age15",        "social-introduce-yourself",     True),
    ("maintain-professional-relationship-age16", "introduce-professionally-age15", True),
    ("navigate-peer-pressure-age14",          "social-say-no-confidently",     True),
    ("social-resolve-conflict",               "social-disagree-respectfully",  True),
    ("lead-a-group-project-age15",            "social-take-turns-talk",        True),

    # New task chains
    ("say-goodbye-properly-age5",             "say-hello-back-age5",           True),
    ("include-someone-alone-age7",            "make-eye-contact-age5",         True),
    ("start-play-new-child-age7",             "say-hello-back-age5",           True),
    ("small-talk-basics-age8",                "start-play-new-child-age7",     True),
    ("own-up-to-mistake-age9",                "say-sorry-mean-it-age5",        True),
    ("recognise-bullying-age10",              "social-handle-teasing",         True),
    ("support-sad-friend-age11",              "comfort-someone-sad-age5",      True),
    ("online-stranger-safety-age11",          "social-safety-secret",          True),
    ("handle-friendship-drift-age12",         "express-feelings-words-age6",   True),
    ("recognise-toxic-friendship-age12",      "handle-friendship-drift-age12", True),
    ("group-chat-etiquette-age12",            "social-listen-no-interrupt",    True),
    ("act-on-bullying-witness-age13",         "recognise-bullying-age10",      True),
    ("body-autonomy-consent-age13",           "social-say-no-confidently",     True),
    ("handle-first-crush-age13",              "social-disagree-respectfully",  True),
    ("ask-for-what-you-need-age13",           "social-disagree-respectfully",  True),
    ("find-place-new-group-age14",            "social-introduce-yourself",     True),
    ("support-peer-difficulty-age16",         "support-sad-friend-age11",      True),
    ("gracious-winner-loser-age7",            "take-turns-game-age6",          True),
]


class Command(BaseCommand):
    help = "Refine the Social task ladder: dedupe, retune ages, add new tasks, wire DAG."

    def handle(self, *args, **options):
        social_tag = Tag.objects.filter(
            name="Social skills", category=Tag.Category.SOCIAL
        ).first()
        if not social_tag:
            social_tag, _ = Tag.objects.get_or_create(
                name="Social skills",
                defaults={"category": Tag.Category.SOCIAL},
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
            task.tags.set([social_tag])
            task.environments.set(all_envs)
            added += 1
        self.stdout.write(f"Phase 3: upserted {added} new social tasks.")

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

        self.stdout.write(self.style.SUCCESS("refine_social_ladder complete."))
