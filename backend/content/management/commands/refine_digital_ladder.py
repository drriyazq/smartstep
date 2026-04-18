"""Management command: refine the Digital task ladder.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py refine_digital_ladder

Four phases, all idempotent:
  1. Delete 2 duplicate stubs
  2. Retune 18 broad age ranges into proper developmental stages
  3. Add 21 new tasks filling gaps at every tier
  4. Wire ~35 prerequisite edges connecting the ladder
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Phase 1 — Duplicates to delete (shallow stubs with better age-5/6 versions)
# ---------------------------------------------------------------------------

DELETE_SLUGS = [
    "open-close-app",       # duplicate of open-close-app-age5
    "turn-device-on-off",   # duplicate of turn-on-off-device-age6
]

# ---------------------------------------------------------------------------
# Phase 2 — Age range updates
# ---------------------------------------------------------------------------

AGE_RANGE_UPDATES = [
    ("type-own-name",                  6,  8),
    ("take-and-delete-photo",          7,  9),
    ("ask-before-downloading",         7, 10),
    ("adjust-volume-brightness",       7, 10),
    ("recognize-ad-banner",            8, 11),
    ("close-suspicious-popup",         8, 11),
    ("use-kid-safe-search",            8, 11),
    ("passwords-are-private",          8, 11),
    ("report-block-content",           8, 11),
    ("dont-share-personal-info",       9, 12),
    ("video-call-etiquette",           9, 12),
    ("respect-screen-time",            9, 12),
    ("digital-footprint-awareness",   11, 13),
    ("use-two-step-verification",     11, 13),
    ("recognize-ai-generated-media",  11, 14),
    ("create-strong-password",        10, 13),
    ("evaluate-source-credibility",   10, 13),
    ("spot-phishing-link",            10, 13),
]

# ---------------------------------------------------------------------------
# Phase 3 — New tasks (21 total)
# ---------------------------------------------------------------------------

NEW_TASKS = [
    # ── Age 5-6 (2 tasks) ───────────────────────────────────────────────
    {
        "slug": "touch-gestures-age5",
        "title": "Use Touchscreen Gestures Correctly",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Tap** — a single gentle touch. Show them: *One finger, one tap, "
            "then lift.* Not a jab or long press.\n"
            "2. **Swipe** — finger down, slide in a direction, lift. "
            "Practise swiping between home screens.\n"
            "3. **Pinch to zoom** — two fingers together, move apart (zoom in) "
            "or together (zoom out). Practise on a photo.\n"
            "4. **Long press** — hold for a second. Shows menus or lets you move apps. "
            "Different from a tap.\n"
            "5. **Gentleness matters** — screens are not buttons. Light touch works better "
            "than hard press. Practise the right pressure."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Clean hands before using a screen. Sticky fingers damage touchscreens.\n"
            "- Never use a pen, pencil, or sharp object on a touchscreen — only fingers "
            "or a proper stylus."
        ),
        "parent_note_md": (
            "Touchscreen gestures are the keyboard of this generation. Children who use "
            "them confidently navigate devices without frustration; those who don't "
            "become the child mashing the screen. Five minutes of explicit practice saves "
            "hours of wasted effort."
        ),
    },
    {
        "slug": "home-screen-navigation-age6",
        "title": "Navigate the Device Home Screen",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The home button or gesture** — how do you get back to the home screen "
            "from any app? Practise 5 times from different apps.\n"
            "2. **Find an app by name** — not by position. Show them the app drawer or search. "
            "*Where do you find the camera? YouTube Kids?*\n"
            "3. **Organise into folders** — drag one app on top of another to make a folder. "
            "*Let's put all the learning apps in one folder.*\n"
            "4. **The recent apps list** — show how to see what's been opened recently "
            "and how to close apps they're not using.\n"
            "5. **Back vs home** — back button goes to the previous screen. Home goes all "
            "the way out. Different buttons, different jobs."
        ),
        "parent_note_md": (
            "Home screen navigation is the spatial literacy of modern devices. A child "
            "who can quickly find apps, swipe between screens, and close what they're "
            "not using feels in control of the device — not overwhelmed by it. "
            "This confidence matters for every future digital skill."
        ),
    },
    # ── Age 7-8 (3 tasks) ───────────────────────────────────────────────
    {
        "slug": "online-vs-offline-age7",
        "title": "Understand What 'Online' and 'Offline' Mean",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Simple definition** — online means the device is talking to the internet. "
            "Offline means it's not.\n"
            "2. **Wi-Fi and mobile data** — these are what connect you to the internet. "
            "Show the icons on the top of the screen.\n"
            "3. **The offline test** — turn on aeroplane mode. Now try to open YouTube. "
            "What happens? Try a game they have downloaded — does it still work?\n"
            "4. **Why it matters** — when you're online, other people and computers can "
            "see what you're doing on the internet. When offline, they can't.\n"
            "5. **Where does your data go?** — when you send a message or photo online, "
            "it travels across many computers before arriving. It's not like whispering."
        ),
        "parent_note_md": (
            "The online/offline distinction is the foundational concept behind privacy, "
            "security, and every future digital literacy lesson. A child who understands "
            "that *online* means *anyone could see* is already ahead of many adults who "
            "treat the internet as private."
        ),
    },
    {
        "slug": "simple-typing-message-age7",
        "title": "Type and Send a Simple Message",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find letters on the keyboard** — not all at once. Start with their name. "
            "Can they type it on a phone or tablet?\n"
            "2. **Capital vs lowercase** — the shift key. Tap once for one capital, "
            "tap twice for all caps lock.\n"
            "3. **Simple punctuation** — full stop, question mark, exclamation mark. "
            "Practise typing a sentence with each.\n"
            "4. **Send a message to a family member** — supervised. *Hi Grandma, I love you!* "
            "They type, they send, they wait for a reply.\n"
            "5. **Check before sending** — read what they wrote. Fix a mistake. "
            "Then send. Never blast messages without checking."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Only message people a parent has approved.\n"
            "- Never send photos without a parent knowing.\n"
            "- If they receive a message from someone they don't know, come to a parent immediately."
        ),
        "parent_note_md": (
            "Typing is the writing skill of the digital era. A child who can type simple "
            "messages confidently can participate in family communication (messaging "
            "grandparents, confirming plans) and is well-prepared for school typing "
            "assignments. Practise with real recipients, not just exercises."
        ),
    },
    {
        "slug": "voice-search-safely-age7",
        "title": "Use Voice Search and Voice Commands Safely",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **How to activate** — show the voice button (microphone icon) or wake word "
            "(*Hey Google, Alexa, Siri*). Let them try.\n"
            "2. **Clear questions** — *What's the weather today? How tall is Mount Everest?* "
            "Clear questions get clear answers.\n"
            "3. **The device is listening** — whenever the mic is active, the device can hear. "
            "That's normal for voice search but worth knowing.\n"
            "4. **Never order anything by voice** — some voice assistants can buy things. "
            "Agree the rule: voice search only, never voice purchases.\n"
            "5. **Handle wrong answers** — voice search isn't perfect. If the answer seems "
            "odd, ask a parent or search the normal way."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Voice assistants can pick up conversations in the background. "
            "Be aware, especially when discussing anything private.\n"
            "- Never give a credit card, address, or password to a voice assistant.\n"
            "- If they ask for something inappropriate (like *show me scary things*), "
            "tell a parent."
        ),
        "parent_note_md": (
            "Voice interfaces are increasingly common and require a different kind of "
            "digital literacy. Children who understand that voice assistants are listening "
            "devices — useful but not private — use them responsibly and are better prepared "
            "for the voice-driven interfaces that will shape the next decade."
        ),
    },
    # ── Age 9-10 (4 tasks) ──────────────────────────────────────────────
    {
        "slug": "good-search-keywords-age9",
        "title": "Search for Information with Good Keywords",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with a question they have** — *How do dolphins sleep?*\n"
            "2. **Bad vs good search** — typing the full question works but is slow. "
            "Key words work better: *dolphins sleep*.\n"
            "3. **Be specific** — *cricket rules* is too broad. *cricket LBW rule explained* "
            "finds what you actually want.\n"
            "4. **Use quotes for exact phrases** — typing a phrase in double quotes "
            "finds pages with that exact phrase, not the words separately.\n"
            "5. **Refining the search** — if the first results aren't useful, add another "
            "keyword or try different words. Searching is a conversation with the engine."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Use Kiddle or Google SafeSearch at this age.\n"
            "- If a search result shows anything scary or inappropriate, "
            "close the tab and tell a parent.\n"
            "- Never click on a result with a URL you don't recognise."
        ),
        "parent_note_md": (
            "Search skill is a genuine academic and life skill. Children who can narrow a "
            "question into the right keywords find answers faster, do better homework, "
            "and trust their own research. Poor search skills compound over years "
            "into learned helplessness with information."
        ),
    },
    {
        "slug": "be-kind-online-age9",
        "title": "Be Kind Online and Never Send Mean Messages",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The golden rule applies online** — if you wouldn't say it to someone's "
            "face, don't type it. The keyboard doesn't remove the hurt.\n"
            "2. **Screenshots are forever** — anything you send can be kept, shown around, "
            "shown to a teacher or parent. Type as if the world could see it.\n"
            "3. **Cooling-off rule** — if angry, don't type. Wait until calm. "
            "Messages sent in anger cause the most lasting damage.\n"
            "4. **Defend, don't pile on** — if someone is being mean to another person online, "
            "don't join in. Don't laugh. Support the target privately if you can.\n"
            "5. **Report mean behaviour** — every platform has a report button. "
            "Use it when someone is repeatedly cruel. Tell a trusted adult if it's serious."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Being on the sending end of cyberbullying can have real consequences: "
            "school discipline, lost friendships, and in serious cases, legal action.\n"
            "- Being on the receiving end: screenshot evidence, block the sender, "
            "tell a parent. You will be believed."
        ),
        "parent_note_md": (
            "Online kindness is not a soft skill — it is a core safeguarding and character "
            "issue. Children who learn early that online cruelty is still real cruelty "
            "are far less likely to participate in group bullying dynamics. The "
            "cooling-off rule, practised consistently, prevents most regrettable messages."
        ),
    },
    {
        "slug": "simple-email-age9",
        "title": "Send a Simple Email",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The email structure** — To (recipient), Subject (what it's about), "
            "Body (the actual message), From (you). Understand each part.\n"
            "2. **Clear subject line** — not *hi* or blank. Something specific: "
            "*Question about the homework*, *Thank you for the birthday gift*.\n"
            "3. **Greeting and closing** — *Hi Uncle,* or *Dear Ms Sharma,* at the top. "
            "*Thanks,* or *Best wishes,* plus their name at the bottom.\n"
            "4. **Proofread before sending** — read it aloud once. Fix typos. "
            "Check the recipient is correct.\n"
            "5. **Send a real email** — to a relative, teacher, or family friend. "
            "Even if brief, the practice of actually sending one builds confidence."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never open attachments from unknown senders.\n"
            "- Never reply to emails asking for passwords, OTPs, or money.\n"
            "- If unsure whether an email is safe, show a parent before clicking anything."
        ),
        "parent_note_md": (
            "Email is the default professional communication medium for the rest of life — "
            "university, work, organisations. Children who can write a clear email at 9 "
            "arrive at real-world situations with one fewer barrier. Start by writing to "
            "known contacts so they get comfortable with the format."
        ),
    },
    {
        "slug": "organize-files-age10",
        "title": "Save, Find, and Organise Files on a Device",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Understand folders** — folders hold files, just like real folders. "
            "They can hold other folders too, nested.\n"
            "2. **Make a folder structure** — on their device or cloud: Homework, Photos, "
            "Games, Personal. A simple system beats no system.\n"
            "3. **Name files clearly** — not *untitled1.docx*. Name files so you can find "
            "them later: *history-essay-draft-2.docx*.\n"
            "4. **Search vs browse** — sometimes searching by name is faster than clicking "
            "through folders. Know both options.\n"
            "5. **Clean up regularly** — once a month, delete old files, move photos to "
            "proper folders. Digital clutter compounds fast."
        ),
        "parent_note_md": (
            "File management is a quiet but critical skill. Children who learn it at 10 "
            "never lose homework, can find photos years later, and develop the "
            "organisational habits that serve them in every project. Those who don't "
            "drown in digital clutter by their teens."
        ),
    },
    # ── Age 11-12 (5 tasks) ─────────────────────────────────────────────
    {
        "slug": "recognize-cyberbullying-age11",
        "title": "Recognise and Report Cyberbullying",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define cyberbullying** — repeated, deliberate cruelty through digital "
            "means: mean messages, public posts, exclusion from chats, rumours online.\n"
            "2. **Forms of cyberbullying** — direct messages, group chat ganging-up, "
            "fake accounts, sharing embarrassing photos, trolling, stalking.\n"
            "3. **If you're the target** — screenshot everything (with dates), block the person, "
            "tell a parent or trusted adult, don't respond, don't delete the evidence.\n"
            "4. **If you're a witness** — don't join in (not even laughing emojis). "
            "Report the content. Privately message support to the target.\n"
            "5. **If you're the one doing it** — stop immediately. Apologise. "
            "Understand that screenshots of what you sent are permanent."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Cyberbullying India helpline: Cyber Crime Cell (1930) or cybercrime.gov.in\n"
            "- Screenshots should be saved before blocking — you may need them.\n"
            "- Severe cases involving threats, blackmail, or sharing images are crimes. "
            "Report to police."
        ),
        "parent_note_md": (
            "Cyberbullying is the most common form of harm children experience online. "
            "Teenagers who know the forms, the response protocol, and that telling a "
            "parent won't result in device confiscation are far better protected. "
            "The parent's role is to make reporting safe — your reaction when they tell "
            "you matters enormously."
        ),
    },
    {
        "slug": "fact-check-simple-age11",
        "title": "Fact-Check a Piece of News or Claim",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a forwarded WhatsApp or viral claim** — there's always one. "
            "*A government minister said X. A new rule says Y.*\n"
            "2. **Check the source** — is there a named news outlet? A date? A journalist's name? "
            "Or is it just a forwarded message with no source?\n"
            "3. **Search for the claim** — search the key facts in Google. "
            "If the claim is real, a credible news outlet will have reported it.\n"
            "4. **Use fact-check sites** — altnews.in, boomlive.in, Snopes for Indian news. "
            "They investigate viral claims directly.\n"
            "5. **If it fails the check** — do not forward. Reply to the person who sent "
            "it: *This isn't true — here's the fact-check.* Gently, but do it."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Misinformation often targets fear, anger, or tribal loyalty. "
            "A strong emotional reaction is a signal to slow down, not forward.\n"
            "- Deepfake videos and AI-generated images are increasingly common — "
            "never trust a dramatic video at face value."
        ),
        "parent_note_md": (
            "Most of India's misinformation flows through WhatsApp, and teenagers are "
            "major amplifiers. A young person who routinely fact-checks before sharing "
            "is a small but real counterforce against the misinformation epidemic. "
            "Model it yourself — fact-check something in front of them."
        ),
    },
    {
        "slug": "algorithm-awareness-age11",
        "title": "Understand Why Your Feed Shows What It Does",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The feed isn't random** — YouTube recommendations, Instagram feed, "
            "TikTok For You — all are algorithmic. The platform chose what to show.\n"
            "2. **The algorithm learns from you** — every like, every second watched, "
            "every pause. It shows more of what keeps you on the app.\n"
            "3. **The filter bubble** — you see more of what you already like. "
            "Different people see different versions of the internet.\n"
            "4. **The business model** — platforms want you to stay on as long as possible. "
            "Ads pay them. Your time and attention are the product.\n"
            "5. **Take some control** — unfollow accounts that make you feel bad, "
            "mute hashtags that trap you, search actively for things you want to learn."
        ),
        "parent_note_md": (
            "Algorithmic literacy is increasingly essential. Teenagers who understand "
            "that their feed is constructed — not neutral — are less susceptible to "
            "manipulation, comparison culture, and doom-scrolling. This single mental "
            "shift changes the entire relationship with social media."
        ),
    },
    {
        "slug": "backup-important-data-age12",
        "title": "Back Up Important Files and Photos",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What needs backing up** — schoolwork, photos, personal writing, important "
            "contacts, account recovery info. Things that would genuinely hurt to lose.\n"
            "2. **The 3-2-1 rule** — 3 copies of anything important, on 2 different "
            "types of storage, with 1 copy offsite (cloud).\n"
            "3. **Cloud backup** — Google Drive, OneDrive, iCloud. Most offer free storage. "
            "Set up auto-backup for photos and documents.\n"
            "4. **A second backup** — external drive or USB. Once a month, copy important "
            "folders to it. Physical backup protects against cloud account issues.\n"
            "5. **Test the backup** — can you actually restore a file from it? "
            "A backup you can't restore is not a backup."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Strong password + 2FA on the cloud backup account — it has all your data.\n"
            "- Don't back up passwords in plain text — use a password manager.\n"
            "- External drives fail too; that's why you have cloud backup."
        ),
        "parent_note_md": (
            "Data loss — a lost phone, a crashed laptop, a ransomware attack — is among "
            "the most upsetting digital experiences. A teenager who has a working backup "
            "never feels that pain. The skill is habitual rather than intellectual: "
            "set it up once, verify it works, forget about it."
        ),
    },
    {
        "slug": "online-gaming-etiquette-age12",
        "title": "Play Online Games Respectfully",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Be a good teammate** — even if losing, don't blame others. "
            "Communicate clearly, help weaker players, praise good plays.\n"
            "2. **No rage quitting** — finishing a match you're losing is part of sportsmanship. "
            "Disconnecting hurts your team more than the score.\n"
            "3. **Voice chat rules** — no shouting, no slurs, no insulting family. "
            "Voice chat is not a private space — recordings happen.\n"
            "4. **Know when to mute** — if others are toxic, mute them. Don't match their energy. "
            "Muting ends most problems.\n"
            "5. **Keep gaming in its place** — don't skip meals, sleep, schoolwork, or family "
            "time for matches. The game will still be there tomorrow."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never share your account details, even with gaming friends.\n"
            "- Strangers who want to take the conversation off the platform (to Discord, "
            "WhatsApp) are a red flag — they may be trying to groom or scam.\n"
            "- Report players who threaten, harass, or ask for personal information."
        ),
        "parent_note_md": (
            "Online gaming is where most teenage social time now happens. It can build "
            "teamwork, friendship, and communication skills — or toxicity, rage, and "
            "exposure to strangers. Teenagers who internalise sportsmanship online are "
            "generally better-adjusted gamers and better-adjusted people."
        ),
    },
    # ── Age 13-14 (3 tasks) ─────────────────────────────────────────────
    {
        "slug": "setup-social-account-age13",
        "title": "Set Up a Social Media Account with Proper Privacy",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Age verification honestly** — most platforms require 13+. Don't lie about "
            "your age to join earlier. The rules exist for safeguarding reasons.\n"
            "2. **Choose a username carefully** — not your full name, not your school, "
            "not easily searchable. Memorable but not identifying.\n"
            "3. **Set to private immediately** — private account means only approved "
            "followers see posts. Turn this on BEFORE the first post.\n"
            "4. **Tighten every privacy setting** — who can message you (friends only), "
            "who can find you by phone (no one), who can tag you (only people you follow).\n"
            "5. **Think before the first post** — it will be there forever. "
            "What kind of account do they actually want to have?"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never post location tags in real time.\n"
            "- Never accept follow requests from people you don't know in real life.\n"
            "- If anyone asks for private photos, save the chat, block them, and tell a parent.\n"
            "- School uniforms in photos identify your school — think before posting."
        ),
        "parent_note_md": (
            "The first social media account shapes a teenager's entire online presence. "
            "Setting it up with a parent — choosing privacy settings together, "
            "agreeing on rules — establishes healthy patterns from the start. The age-13 "
            "minimum is a real legal threshold with real safeguarding reasons."
        ),
    },
    {
        "slug": "notification-hygiene-age13",
        "title": "Manage Your Notifications and Attention",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Audit your notifications** — Settings → Notifications. "
            "Go through every app. Most should be OFF.\n"
            "2. **What deserves a notification?** — messages from actual people, "
            "calendar events, critical alerts. NOT: game reminders, app updates, social feed activity.\n"
            "3. **Do Not Disturb schedule** — 10pm to 7am, no notifications except emergencies. "
            "Automate this on the phone.\n"
            "4. **Grayscale mode** — Android and iOS can turn the screen black-and-white. "
            "Apps become far less addictive. Try for a day.\n"
            "5. **Phone-free blocks** — decide on periods when the phone goes in another room: "
            "meals, homework, bedtime routine. Not negotiable."
        ),
        "parent_note_md": (
            "Attention is the most valuable resource a teenager has, and notifications are "
            "designed to steal it. Teenagers who take control of their notifications "
            "study better, sleep better, and feel less anxious. The audit takes 15 minutes "
            "and changes daily life."
        ),
    },
    {
        "slug": "read-terms-basics-age14",
        "title": "Read the Basic Parts of Terms and Conditions",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Never click *I agree* blindly again** — every *I agree* is a contract. "
            "Even if no one reads them, you're bound by them.\n"
            "2. **Find the important bits fast** — look for: *Data we collect*, "
            "*How we share your data*, *Termination*, *Payment and refunds*.\n"
            "3. **Use a summary service** — tosdr.org (Terms of Service Didn't Read) rates "
            "major services on how user-friendly their terms are.\n"
            "4. **Red flags** — perpetual rights to your content, sharing with unspecified "
            "third parties, binding arbitration clauses, automatic renewals with cancellation traps.\n"
            "5. **Decide then accept** — after 5 minutes of reading, you'll know if it's "
            "acceptable. If not, don't sign up."
        ),
        "parent_note_md": (
            "Nobody reads terms and conditions, and companies rely on that. Teenagers "
            "who even skim for red flags avoid many of the worst digital contracts of "
            "adult life. The skill isn't to read every word — it's to know where to look."
        ),
    },
    # ── Age 14-16 (2 tasks) ─────────────────────────────────────────────
    {
        "slug": "cloud-collaboration-age14",
        "title": "Collaborate Using Shared Documents",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The tools** — Google Docs, Google Sheets, Google Slides, or Microsoft equivalents. "
            "All allow multiple people to edit the same document.\n"
            "2. **Start a group project** — with classmates for a school assignment, "
            "with family for a trip plan, with friends for an event.\n"
            "3. **Share with the right permissions** — *View only* for outsiders, "
            "*Edit* for collaborators. Check who has access before sharing.\n"
            "4. **Commenting and suggesting** — for work someone else wrote, add comments "
            "or use *Suggesting* mode. Don't overwrite without agreement.\n"
            "5. **Version history** — show how to see who changed what. "
            "Nothing is ever lost — old versions can be restored."
        ),
        "parent_note_md": (
            "Cloud-based collaboration is how virtually all office work and most academic "
            "work now happens. Teenagers who use it naturally — with correct permissions, "
            "proper commenting etiquette, and version awareness — have a significant "
            "advantage in group projects and eventually in the workplace."
        ),
    },
    {
        "slug": "ethical-ai-use-age15",
        "title": "Use AI Tools Ethically and Know the Limits",
        "min_age": 15, "max_age": 17,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Disclose AI use** — if a teacher, employer, or collaborator asks if you "
            "used AI, be honest. Hiding it is a form of dishonesty.\n"
            "2. **AI is a tool, not an author** — it can help you draft, brainstorm, summarise. "
            "But submitting pure AI output as your own thinking is cheating and stunts learning.\n"
            "3. **Verify AI output** — AI hallucinates confidently. Any fact, citation, "
            "or reference from an AI tool should be verified independently.\n"
            "4. **Know the bias** — AI reflects the biases in its training data. "
            "On controversial topics or underrepresented groups, AI often gets things wrong.\n"
            "5. **Don't feed AI sensitive data** — anything you send to a public AI tool "
            "might be stored, used for training, or leaked. Keep personal and others' data out."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never share other people's private information with an AI (their messages, "
            "photos, personal details).\n"
            "- Never use AI to create content impersonating real people (deepfakes are illegal).\n"
            "- If an AI output feels wrong — it probably is. Don't use it."
        ),
        "parent_note_md": (
            "AI ethics is not a future topic — it is already here. Teenagers who use AI "
            "well: disclosing it, verifying it, not outsourcing thinking to it, and "
            "respecting others' privacy when using it — are exhibiting the judgement "
            "that defines responsible adults. Those who don't face real consequences: "
            "academic dishonesty, lost trust, legal issues around deepfakes."
        ),
    },
    # ── Age 16-18 (2 tasks) ─────────────────────────────────────────────
    {
        "slug": "know-your-data-age16",
        "title": "Find Out What Data Companies Hold About You",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Download your Google data** — takeout.google.com. Request an export. "
            "You'll receive a huge archive of everything Google has on you. "
            "Open it. Look through.\n"
            "2. **Download your Facebook/Instagram data** — Settings → Your Information. "
            "Every message, every like, every photo, tagged or posted.\n"
            "3. **Notice the patterns** — location history, search history, ad targeting data, "
            "contacts imported, devices used. It's a lot.\n"
            "4. **Request data from other services** — under the DPDP Act in India, "
            "companies must disclose what data they hold on you when you ask.\n"
            "5. **Delete what you can** — review the data, delete old content, "
            "turn off data collection features, remove permissions from apps you no longer use."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never download these archives on a public or shared computer.\n"
            "- Your data archive contains enough information for identity theft — "
            "keep it secure like a passport.\n"
            "- If you're shocked by what's there: delete accounts you don't use, "
            "not just the data."
        ),
        "parent_note_md": (
            "Most adults have no idea how much data tech companies hold on them. A "
            "teenager who does this exercise once has a different relationship with "
            "every app they sign up for afterwards. The scale is confronting but the "
            "awareness is protective. It is also the foundation for understanding "
            "data rights under law."
        ),
    },
    {
        "slug": "common-cyber-attacks-age16",
        "title": "Recognise Common Cyber Attacks",
        "min_age": 16, "max_age": 18,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Phishing** — emails/texts impersonating banks, delivery services, "
            "government. Asking for passwords, OTPs, or urgent clicks. Review a real one.\n"
            "2. **Social engineering** — phone calls pretending to be from customer service, "
            "tech support, a parent's boss. The goal is to get you to reveal something "
            "or send money. Slow down, verify.\n"
            "3. **SIM swap** — someone steals your phone number by convincing your telecom. "
            "Then they get all your OTPs and can raid your accounts. Use app-based 2FA, not SMS.\n"
            "4. **Ransomware** — malware that encrypts your files and demands payment. "
            "Prevention: backups (you've done this task) and never open suspicious attachments.\n"
            "5. **Investment/crypto scams** — *guaranteed returns*, influencer-backed tokens, "
            "pressure to invest quickly. All scams. Real investing is slow and boring."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Never share OTPs over phone. No legitimate organisation will ever ask.\n"
            "- If you think you've been scammed: change all passwords, call the bank, "
            "report at cybercrime.gov.in or call 1930.\n"
            "- Time matters — act within hours, not days."
        ),
        "parent_note_md": (
            "Cyber attacks are no longer the concern of specialists — they are an "
            "everyday risk for anyone with a phone. Teenagers who can recognise the "
            "common patterns are protected and can often warn their parents and "
            "grandparents (who are frequent targets). Knowledge of these attacks is "
            "the primary defence."
        ),
    },
]

# ---------------------------------------------------------------------------
# Phase 4 — Prerequisite edges: (to_slug, from_slug, mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    # Existing-task chains that were missing
    ("dont-share-personal-info",              "private-info-rule-age6",         True),
    ("video-call-etiquette",                  "video-call-family-age6",         True),
    ("spot-phishing-scam-age15",              "spot-phishing-link",             True),
    ("strong-password-age14",                 "create-strong-password",         True),
    ("ai-tools-critically-age15",             "identify-misinformation-age14",  True),
    ("protect-identity-online-age16",         "use-two-step-verification",      True),
    ("digital-footprint-age14",               "digital-footprint-awareness",    True),
    ("online-safety-privacy-age14",           "dont-share-personal-info",       True),
    ("identify-misinformation-age14",         "evaluate-source-credibility",    True),
    ("identify-misinformation-age14",         "recognize-ai-generated-media",   True),
    ("manage-screen-wellbeing-age15",         "respect-screen-time",            True),
    ("build-portfolio-age16",                 "build-cv-online-age15",          True),
    ("professional-digital-communication-age16", "video-call-etiquette",        True),
    ("evaluate-online-source-age16",          "evaluate-source-credibility",    True),
    ("take-and-delete-photo",                 "turn-on-off-device-age6",        True),
    ("adjust-volume-brightness",              "volume-buttons-age5",            True),
    ("passwords-are-private",                 "private-info-rule-age6",         True),
    ("ask-before-downloading",                "ask-before-screen-age6",         True),
    ("close-suspicious-popup",                "recognize-ad-banner",            True),
    ("respect-screen-time",                   "screen-time-stop-age6",          True),
    ("use-kid-safe-search",                   "open-close-app-age5",            True),
    ("build-cv-online-age15",                 "build-simple-project-age14",     True),
    ("spreadsheet-real-use-age15",            "build-simple-project-age14",     True),
    ("digital-productivity-system-age16",     "spreadsheet-real-use-age15",     True),

    # New task chains
    ("home-screen-navigation-age6",           "touch-gestures-age5",            True),
    ("simple-typing-message-age7",            "home-screen-navigation-age6",    True),
    ("voice-search-safely-age7",              "home-screen-navigation-age6",    True),
    ("online-vs-offline-age7",                "open-close-app-age5",            True),
    ("good-search-keywords-age9",             "online-vs-offline-age7",         True),
    ("good-search-keywords-age9",             "use-kid-safe-search",            True),
    ("be-kind-online-age9",                   "private-info-rule-age6",         True),
    ("simple-email-age9",                     "simple-typing-message-age7",     True),
    ("organize-files-age10",                  "take-and-delete-photo",          True),
    ("recognize-cyberbullying-age11",         "be-kind-online-age9",            True),
    ("fact-check-simple-age11",               "good-search-keywords-age9",      True),
    ("algorithm-awareness-age11",             "recognize-ad-banner",            True),
    ("backup-important-data-age12",           "organize-files-age10",           True),
    ("online-gaming-etiquette-age12",         "be-kind-online-age9",            True),
    ("setup-social-account-age13",            "digital-footprint-awareness",    True),
    ("setup-social-account-age13",            "create-strong-password",         True),
    ("notification-hygiene-age13",            "respect-screen-time",            True),
    ("read-terms-basics-age14",               "dont-share-personal-info",       True),
    ("cloud-collaboration-age14",             "simple-email-age9",              True),
    ("ethical-ai-use-age15",                  "ai-tools-critically-age15",      True),
    ("know-your-data-age16",                  "digital-footprint-age14",        True),
    ("common-cyber-attacks-age16",            "spot-phishing-scam-age15",       True),
    ("common-cyber-attacks-age16",            "backup-important-data-age12",    True),
    ("identify-misinformation-age14",         "fact-check-simple-age11",        True),
]


class Command(BaseCommand):
    help = "Refine the Digital task ladder: dedupe, retune ages, add new tasks, wire DAG."

    def handle(self, *args, **options):
        digital_tag = Tag.objects.filter(
            name="Digital literacy", category=Tag.Category.DIGITAL
        ).first()
        if not digital_tag:
            digital_tag, _ = Tag.objects.get_or_create(
                name="Digital literacy",
                defaults={"category": Tag.Category.DIGITAL},
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
            task.tags.set([digital_tag])
            task.environments.set(all_envs)
            added += 1
        self.stdout.write(f"Phase 3: upserted {added} new digital tasks.")

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

        self.stdout.write(self.style.SUCCESS("refine_digital_ladder complete."))
