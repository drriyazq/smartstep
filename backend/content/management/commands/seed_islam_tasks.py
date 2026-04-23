"""Management command: seed Islamic tasks for ages 5–16 (religion='islam').

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_islam_tasks

Adds 43 approved Islamic tasks — three or four per age year 5 to 16 —
covering manners (adab), teachings, daily practice, habits, and rituals.
Each task:
  * has religion='islam' so it only surfaces to profiles that opted in and
    picked Islam in the religion onboarding step;
  * is tagged with one primary category (cognitive / social / household /
    financial) so it flows through the existing per-category ladder;
  * carries an authored how_to_md and parent_note_md with grounding in
    Quran or authentic hadith (Bukhari / Muslim / Abu Dawud / Tirmidhi /
    Nasai / Ibn Majah).

Idempotent via update_or_create(slug=...).
"""
from django.core.management.base import BaseCommand

from content.models import Environment, ReviewStatus, Tag, Task


# ---------------------------------------------------------------------------
# Category tag helpers (same names used by every other seeder)
# ---------------------------------------------------------------------------

TAG_FOR_CATEGORY = {
    "cognitive": ("Reasoning",     Tag.Category.COGNITIVE),
    "social":    ("Social skills", Tag.Category.SOCIAL),
    "household": ("Home care",     Tag.Category.HOUSEHOLD),
    "financial": ("Money basics",  Tag.Category.FINANCIAL),
}


# ---------------------------------------------------------------------------
# Task catalog — grouped by age for easy review and edit
# ---------------------------------------------------------------------------

ISLAM_TASKS = [
    # ══════════════════════════════════════════════════════════════════════
    # AGE 5 — foundational manners and first surah
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-bismillah-before-eating-age5",
        "title": "Say Bismillah Before Eating, Alhamdulillah After",
        "category": "social",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Before the first bite**, say aloud together: *Bismillah* "
            "(*In the name of Allah*).\n"
            "2. **If they forget and start eating**, teach the makeup phrase: "
            "*Bismillahi awwalahu wa akhirahu* (*In the name of Allah at its beginning and end*).\n"
            "3. **Use the right hand** for eating and drinking, the sunnah way.\n"
            "4. **After finishing**, say *Alhamdulillah* (*All praise is for Allah*) aloud.\n"
            "5. **Practise at every meal** — not just special ones. This is a habit, not a performance."
        ),
        "parent_note_md": (
            "Saying Bismillah before eating is a direct sunnah. The Prophet ﷺ said to Umar ibn Abi Salama: "
            "*Say Bismillah, eat with your right hand, and eat from what is close to you* "
            "(Sahih Bukhari 5376, Sahih Muslim 2022). Saying Alhamdulillah after eating is "
            "also an established sunnah (Abu Dawud 3850). These two small habits anchor "
            "gratitude into the rhythm of every day."
        ),
    },
    {
        "slug": "islam-return-salam-age5",
        "title": "Return the Greeting As-salamu alaykum",
        "category": "social",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the greeting in full** — *As-salamu alaykum* (*Peace be upon you*).\n"
            "2. **Teach the reply** — *Wa alaykumu-salam* (*And upon you be peace*). "
            "A better reply adds *wa rahmatullahi wa barakatuh*.\n"
            "3. **Use it at home first** — greet them with salam when you enter a room; "
            "expect salam back.\n"
            "4. **Practise with relatives** — on phone calls, at the door, at the masjid.\n"
            "5. **Explain the meaning simply** — *We're wishing peace on each other. "
            "It's a small gift we give without spending anything.*"
        ),
        "parent_note_md": (
            "Returning a greeting is not optional in Islam — Allah commands in the Quran: "
            "*When you are greeted, return it with something better or at least like it* (4:86). "
            "The Prophet ﷺ said: *You will not enter Paradise until you believe, and you will "
            "not believe until you love one another. Shall I tell you of something that, if you "
            "do it, you will love one another? Spread salam among yourselves* (Sahih Muslim 54)."
        ),
    },
    {
        "slug": "islam-memorise-fatiha-age5",
        "title": "Memorise Surah Al-Fatiha",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Listen daily** — play a slow, clear recitation of Surah Al-Fatiha during "
            "a quiet time each day. Repetition is everything.\n"
            "2. **One ayah at a time** — learn the first ayah for a day or two, then add the next. "
            "Don't rush.\n"
            "3. **Say it together during your own salah** — when they hear you, they learn the rhythm.\n"
            "4. **Explain it simply** — *This is what we say to Allah at the start of every prayer.*\n"
            "5. **Celebrate when they complete it** — memorising Al-Fatiha is a milestone; "
            "this is the surah recited in every rak'ah for the rest of their life."
        ),
        "parent_note_md": (
            "Surah Al-Fatiha is *Umm al-Kitab* — the Mother of the Book. It is the only surah "
            "recited in every rak'ah of salah, so learning it early gives the child direct "
            "access to every prayer they'll pray for the rest of their life. The Prophet ﷺ "
            "said: *There is no prayer for the one who does not recite Al-Fatiha* (Sahih Bukhari 756)."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 6 — first short surah, InshaAllah habit, watching salah
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-memorise-ikhlas-age6",
        "title": "Memorise Surah Al-Ikhlas",
        "category": "cognitive",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Listen to the surah daily** — only four short ayahs. Ten listens and "
            "they'll start repeating it.\n"
            "2. **Recite it yourself in their presence** — during salah, at bedtime, after Fajr.\n"
            "3. **Ayah by ayah** — they repeat after you. Don't worry about perfect tajweed yet.\n"
            "4. **Use it at bedtime** — sunnah is to recite Al-Ikhlas, Al-Falaq, and An-Nas "
            "three times each and blow on the hands (Sahih Bukhari 5017).\n"
            "5. **Test without help** — once they can say it on their own, they've memorised it."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said Surah Al-Ikhlas equals *one-third of the Quran* "
            "(Sahih Bukhari 5013, Sahih Muslim 811). It is the clearest declaration of "
            "tawheed in the Quran, and memorising it at 6 gives a child the core creedal "
            "statement of their faith in exact Quranic words."
        ),
    },
    {
        "slug": "islam-say-inshaallah-age6",
        "title": "Say InshaAllah When Talking About the Future",
        "category": "social",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Model it yourself** — any time *you* speak about a future plan, add *InshaAllah*. "
            "Children copy speech patterns before they copy habits.\n"
            "2. **Catch their future statements** — *I'll play tomorrow*. Prompt gently: *InshaAllah.*\n"
            "3. **Explain the why** — *Nothing happens unless Allah wills it. We say InshaAllah "
            "to remember that.*\n"
            "4. **Make it natural, not performative** — don't force it mid-sentence. A gentle "
            "reminder is enough; habit comes from hearing you say it.\n"
            "5. **Same for wishes** — *May Allah protect us* and *MashaAllah* when admiring "
            "something also belong to this family of habits."
        ),
        "parent_note_md": (
            "Saying InshaAllah when speaking of the future is commanded in the Quran: "
            "*And never say of anything, 'Indeed, I will do that tomorrow,' except [with the caveat], "
            "'If Allah wills'* (18:23-24). This is not a superstition but a daily acknowledgement "
            "that outcomes belong to Allah. A child who grows up with this habit carries humility "
            "about plans into adulthood."
        ),
    },
    {
        "slug": "islam-pray-with-parent-age6",
        "title": "Stand with a Parent During Part of Salah",
        "category": "household",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Let them watch from close by** — stand beside you, not behind a wall. They "
            "need to see what prayer looks like from the inside.\n"
            "2. **No pressure to complete** — if they sit halfway through, that's fine. "
            "The goal is exposure, not performance.\n"
            "3. **Explain what each part means** — when you go into ruku: *Now I'm bowing "
            "to glorify Allah.* When you do sujood: *This is the closest a person gets to Allah.*\n"
            "4. **Encourage them to copy the movements** — takbir, standing, ruku, sujood. "
            "The movements stick before the words.\n"
            "5. **Praise the attempt** — don't correct mistakes. Enthusiasm first; correctness comes naturally with time."
        ),
        "parent_note_md": (
            "Children who stand beside parents at salah are absorbing the practice visually "
            "long before they are ready to pray alone. The Prophet ﷺ would allow his grandchildren "
            "to climb on him during sujood and wait for them to get down before rising — a clear "
            "sign that children were welcome in the space of prayer (Sunan An-Nasa'i 1141). "
            "Formal teaching starts at seven; exposure should start earlier."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 7 — the formal age to begin praying per hadith
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-learn-wudu-age7",
        "title": "Learn and Perform Wudu with Adult Supervision",
        "category": "household",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with the intention** — teach them *Bismillah* at the start of wudu.\n"
            "2. **Wash the hands** three times up to the wrists.\n"
            "3. **Rinse the mouth** three times, then **sniff water into the nose** and blow out three times.\n"
            "4. **Wash the face** three times, then the **right arm to the elbow** three times, "
            "then the **left arm** three times.\n"
            "5. **Wipe the head once** with wet hands, then the **ears inside and out**, "
            "then **wash both feet up to the ankles**, right first. End with *Ashhadu an la ilaha illallah, "
            "wa ashhadu anna Muhammadan abduhu wa rasuluh.*"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- **Water temperature:** warm but not hot. Cold is acceptable; scalding is not.\n"
            "- **Don't rush** on slippery floors — foot-washing needs a stable stance.\n"
            "- **Supervise the first ~20 times** — wudu has a fixed order; small mistakes "
            "invalidate it, and they should learn the correct form from the start."
        ),
        "parent_note_md": (
            "The method of wudu is described in detail in hadith narrated by Uthman ibn Affan (Bukhari 159) "
            "and others. The Prophet ﷺ said: *Purification is half of faith* (Sahih Muslim 223). A child "
            "who has learned wudu correctly at 7 is ready to begin prayer meaningfully — this is the "
            "ritual gateway to salah."
        ),
    },
    {
        "slug": "islam-start-praying-age7",
        "title": "Start Praying At Least One Salah Each Day",
        "category": "household",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick one prayer to start with** — Maghrib is shortest (3 rak'ah) and comes "
            "at a natural family time.\n"
            "2. **Pray together** — they follow your lead, standing on your right in a two-person line.\n"
            "3. **Teach the structure** — takbir, recite Fatiha, a short surah (e.g. Al-Ikhlas), "
            "ruku, sujood twice, tashahhud, salam.\n"
            "4. **Build up gradually** — one prayer for a week, then add a second, over months.\n"
            "5. **Never scold for missing a prayer at this age** — encouragement builds habit; "
            "scolding builds resentment. Discipline comes at ten, not seven."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Command your children to pray when they are seven years old, "
            "and discipline them for it when they are ten* (Abu Dawud 495, graded sahih). "
            "Age seven is the start of teaching — warm, consistent, no harshness. Children "
            "who begin now pray naturally by ten. Children who start at ten begin under pressure."
        ),
    },
    {
        "slug": "islam-memorise-mu-awwidhatayn-age7",
        "title": "Memorise Surah An-Nas and Al-Falaq",
        "category": "cognitive",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Both are short** — five ayahs and six ayahs. Start with An-Nas since it is "
            "slightly shorter and simpler.\n"
            "2. **Use them nightly** — the sunnah is to recite Al-Ikhlas, Al-Falaq, and An-Nas "
            "three times each before sleep.\n"
            "3. **One ayah a day** — cumulative. Don't rush; memorised well is memorised forever.\n"
            "4. **Explain the meaning** — *We are asking Allah to protect us from harm and bad "
            "thoughts. These surahs are like a shield.*\n"
            "5. **Test with gaps** — say most of an ayah and pause. They fill in the blank. "
            "This tests true memorisation."
        ),
        "parent_note_md": (
            "Al-Falaq (113) and An-Nas (114) are the *Mu'awwidhatayn* — the two surahs of seeking "
            "refuge. Aisha narrated that every night before sleep, the Prophet ﷺ would recite these "
            "two along with Al-Ikhlas, blow into his hands, and wipe his body (Sahih Bukhari 5017). "
            "A child who knows these has a nightly protection recitation for life."
        ),
    },
    {
        "slug": "islam-obey-parents-age7",
        "title": "Obey and Help Your Parents Without Being Asked Twice",
        "category": "social",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the Quranic verse** — Al-Isra 17:23-24. *Do not say to them a word of "
            "disrespect, nor shout at them — but address them with kind words.*\n"
            "2. **Respond on the first ask** — not the third. This is the habit being built.\n"
            "3. **Volunteer before being asked** — carrying bags, bringing water, helping with "
            "small chores. Unsolicited help is the real level.\n"
            "4. **Never roll eyes, sigh, or mumble** — those are the modern forms of *uff* "
            "that Allah prohibited.\n"
            "5. **Make dua for parents daily** — *Rabbi irhamhuma kama rabbayani saghira* "
            "(*O Lord, have mercy on them as they raised me when small* — Quran 17:24)."
        ),
        "parent_note_md": (
            "Kindness to parents is mentioned in the Quran right after the command to worship "
            "Allah alone (17:23, 31:14). When a man asked the Prophet ﷺ *Who is most deserving "
            "of my good company?* he said *Your mother* — three times — then *your father* "
            "(Sahih Bukhari 5971). Obedience to parents is among the most emphasised social "
            "duties in Islam; teaching it at 7 shapes a lifetime."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 8 — building up salah, memorising Ayatul Kursi, eating etiquette
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-pray-multiple-salah-age8",
        "title": "Pray Two or Three of the Five Daily Prayers On Time",
        "category": "household",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Expand from one to three** — add Maghrib first, then Isha (both at home "
            "with family), then Fajr.\n"
            "2. **Pray at the prayer time, not later** — teach the principle of *waqt* (on time).\n"
            "3. **Use the adhan app or nearby masjid** — the ear learns to recognise prayer times.\n"
            "4. **Pray together when possible** — in jama'ah (congregation) at home if not at the masjid.\n"
            "5. **Debrief occasionally** — *How did your salah feel today? Did you think about what you were saying?* "
            "Quality begins to matter, not just quantity."
        ),
        "parent_note_md": (
            "The Prophet ﷺ was asked: *Which deed is most beloved to Allah?* He said: *Prayer "
            "at its appointed time* (Sahih Bukhari 527, Sahih Muslim 85). At age 8, the child "
            "is still in the teaching phase — consistency without harshness. Three prayers "
            "daily by 8 is a strong foundation for the five by 10."
        ),
    },
    {
        "slug": "islam-memorise-ayatul-kursi-age8",
        "title": "Memorise Ayatul Kursi (Quran 2:255)",
        "category": "cognitive",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Listen to it daily** — slow, clear recitation. It is one of the longest "
            "single ayahs in the Quran; expect 2–4 weeks of practice.\n"
            "2. **Break it into natural phrases** — stop at *wa la nawm*, *ma fi-s-samawati wa-ma fi-l-ardh*, "
            "*illa bi-idhnih*, etc. Phrase by phrase sticks far better than trying to learn it all at once.\n"
            "3. **Recite after every salah** — the sunnah practice. The sooner it becomes a habit, "
            "the sooner it becomes memorised automatically.\n"
            "4. **Recite at bedtime** — along with Al-Ikhlas, Al-Falaq, and An-Nas.\n"
            "5. **Explain the content** — *This ayah describes Allah: He is alive, He doesn't sleep, "
            "He knows everything, and nothing is too much for Him.*"
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Whoever recites Ayatul Kursi after every obligatory prayer, "
            "nothing stands between him and entering Paradise except death* (Sunan An-Nasa'i, "
            "graded sahih by Al-Albani). A child who has Ayatul Kursi memorised has one of the "
            "greatest ayahs of the Quran ready on their tongue for every post-prayer dhikr and "
            "every bedtime, for life."
        ),
    },
    {
        "slug": "islam-eating-etiquette-age8",
        "title": "Eat with the Right Hand, Bismillah, and from What is Close",
        "category": "social",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Always right hand** — for eating and drinking. Left hand is only a helper.\n"
            "2. **Say Bismillah before starting** — aloud at home, quietly at restaurants.\n"
            "3. **Eat from what is in front of you** — don't reach across the plate or take "
            "the best piece from someone else's side.\n"
            "4. **Sit to eat** — the Prophet ﷺ forbade drinking while standing except in specific cases. "
            "Sit, slow down, chew properly.\n"
            "5. **Don't criticise food** — if you don't like it, eat something else or leave it; "
            "never complain. This is a direct sunnah."
        ),
        "parent_note_md": (
            "The Prophet ﷺ taught Umar ibn Abi Salama: *O boy, say Bismillah, eat with your right hand, "
            "and eat from what is close to you* (Sahih Bukhari 5376, Sahih Muslim 2022). Abu Hurairah "
            "also reported: *The Prophet ﷺ never criticised any food; if he liked it he ate it, "
            "if he did not, he left it* (Sahih Bukhari 3563). These small table adab shape character "
            "more than their size suggests."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 9 — all five prayers (trying), short surahs, first fasting + sadaqa
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-pray-five-daily-age9",
        "title": "Attempt All Five Daily Prayers",
        "category": "household",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Map the day to the five prayers** — Fajr, Dhuhr, Asr, Maghrib, Isha. Know the "
            "time windows for each.\n"
            "2. **Dhuhr and Asr at school** — find a quiet spot. Prayer doesn't need a mosque.\n"
            "3. **Don't combine or skip lightly** — each prayer at its own time builds the discipline "
            "the next year requires.\n"
            "4. **Keep a small prayer mat or clean cloth in the bag** — readiness reduces excuses.\n"
            "5. **Missed one? Pray it as qada** — as soon as you remember, don't skip it entirely. "
            "The Prophet ﷺ: *Whoever sleeps through a prayer or forgets it, let him pray it when "
            "he remembers* (Sahih Muslim 684)."
        ),
        "parent_note_md": (
            "At age 9, the child is a year from the hadith's discipline age. Trying all five "
            "prayers now, with parental support and without punishment for lapses, means the "
            "transition at 10 is smooth, not abrupt. The Prophet ﷺ said the difference between "
            "belief and disbelief is prayer (Sahih Muslim 82) — this is the most emphasised "
            "practical obligation in Islam."
        ),
    },
    {
        "slug": "islam-memorise-kawthar-asr-age9",
        "title": "Memorise Surah Al-Kawthar and Al-Asr",
        "category": "cognitive",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Al-Kawthar first** — it is the shortest surah in the Quran (three ayahs). "
            "One day's practice may be enough.\n"
            "2. **Al-Asr next** — also very short (three ayahs). Its meaning is a life blueprint.\n"
            "3. **Use them in salah immediately** — recite them after Al-Fatiha in the rak'ahs where "
            "a short surah is recited.\n"
            "4. **Learn the translation of Al-Asr** — *By time, mankind is in loss, except those "
            "who believe, do righteous deeds, counsel each other to truth, and counsel each other "
            "to patience.*\n"
            "5. **Reflect once** — after memorising, discuss what Al-Asr teaches. What are the four "
            "things that save a person? This is the first step into understanding meaning, not just memorising sound."
        ),
        "parent_note_md": (
            "Imam Ash-Shafi'i said: *If people only reflected on Surah Al-Asr, it would be enough for them.* "
            "In three ayahs it lists the four things that save a person from loss: belief, righteous "
            "action, enjoining truth, and enjoining patience. Every child who memorises it carries "
            "a summary of Islamic life in their memory."
        ),
    },
    {
        "slug": "islam-weekly-sadaqa-age9",
        "title": "Give a Small Sadaqa Every Week",
        "category": "financial",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set aside a small amount from pocket money** — even ₹5 or ₹10. The amount doesn't matter; "
            "the habit does.\n"
            "2. **Pick a consistent day** — every Friday works well (Jumu'ah is a day of blessings).\n"
            "3. **Give to different causes** — one week a donation box at the masjid, one week food "
            "for someone in need, one week something given anonymously.\n"
            "4. **Give with the right hand** — sunnah adab for giving.\n"
            "5. **Don't announce it** — the Quran praises those who give so that *the left hand does "
            "not know what the right hand has given* (implied by Quran 2:271)."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Charity does not decrease wealth* (Sahih Muslim 2588). He also said: "
            "*Protect yourself from the fire even with half a date* (Sahih Bukhari 1417). A child "
            "who gives weekly learns that giving is not about having a lot — it's about knowing "
            "that everything you have came from Allah, and a share of it belongs to those in need."
        ),
    },
    {
        "slug": "islam-practice-fasting-age9",
        "title": "Practise Fasting for Part of the Day in Ramadan",
        "category": "household",
        "min_age": 9, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with half-day fasts** — from suhoor until Dhuhr, or until Asr. Don't push "
            "a child to full fasts before they're physically ready.\n"
            "2. **Do suhoor together** — even a small meal. The sunnah is to eat something, even "
            "if only a date.\n"
            "3. **Pick a day** — maybe the weekend. Build up to more days across Ramadan.\n"
            "4. **Keep busy and cool** — fasting is easier with structured activity, not endless "
            "thinking about food.\n"
            "5. **Celebrate the iftar** — whether they fasted 4 hours or 14, opening the fast with "
            "the family is the reward that makes it stick."
        ),
        "parent_note_md": (
            "The companions would get their young children used to fasting on Ashura by giving them "
            "a toy made of wool when they cried from hunger (Sahih Bukhari 1960, Sahih Muslim 1136) — "
            "evidence that children were eased into fasting gradually. Building up fasts before "
            "puberty is normal and healthy. The Prophet ﷺ said: *Whoever fasts Ramadan out of faith "
            "and hope of reward will have his past sins forgiven* (Sahih Bukhari 38)."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 10 — discipline age per hadith, five pillars, truthfulness
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-consistent-five-prayers-age10",
        "title": "Pray All Five Daily Prayers Consistently",
        "category": "household",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **All five, every day, on time** — this is now the expectation, not the goal.\n"
            "2. **Make wudu properly before each** — one wudu lasts until broken, but fresh wudu "
            "between prayers is sunnah.\n"
            "3. **Pray at the first part of the time window** — the earlier within the window, the better.\n"
            "4. **Never leave a prayer** — if missed, make it up the moment you remember.\n"
            "5. **Use a checklist for a month if needed** — tick off each prayer. External structure "
            "makes internal discipline easier to build."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Command your children to pray when they are seven, and discipline "
            "them for it when they are ten, and separate their beds at that time* (Abu Dawud 495). "
            "Age ten marks the shift from encouragement to expectation. This is the age where salah "
            "becomes a personal obligation under parental guidance — not out of fear, but because "
            "the Messenger of Allah ﷺ said so."
        ),
    },
    {
        "slug": "islam-memorise-short-surahs-age10",
        "title": "Memorise Five More Short Surahs",
        "category": "cognitive",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Al-Fil (105)** — five ayahs. The story of the elephant.\n"
            "2. **Quraysh (106)** — four ayahs.\n"
            "3. **Al-Ma'un (107)** — seven ayahs. Critical lessons on neglect of the orphan and the needy.\n"
            "4. **Al-Kafirun (109)** — six ayahs. Clear separation of faith.\n"
            "5. **An-Nasr (110)** — three ayahs. Recite one new surah a week; cycle through the "
            "existing ones during salah to keep them fresh."
        ),
        "parent_note_md": (
            "Juz Amma (the 30th juz) contains short, memorable surahs that cover creed, history, "
            "ethics, and prayer. A child who finishes Juz Amma by age 12 has memorised material "
            "they will use in every salah for the rest of their life. The Prophet ﷺ said: "
            "*The best of you are those who learn the Quran and teach it* (Sahih Bukhari 5027)."
        ),
    },
    {
        "slug": "islam-five-pillars-age10",
        "title": "Know the Five Pillars of Islam by Name and Meaning",
        "category": "cognitive",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Shahada** — *La ilaha illa Allah, Muhammadun rasulullah.* Testimony of faith. "
            "Memorise, understand, repeat.\n"
            "2. **Salah** — five daily prayers. Already being practised; now name it as a pillar.\n"
            "3. **Zakat** — giving 2.5% of savings above a threshold yearly to the poor. "
            "Explain simply; the details come later.\n"
            "4. **Sawm** — fasting the month of Ramadan. Connect to their own fasting practice.\n"
            "5. **Hajj** — pilgrimage to Makkah at least once if physically and financially able. "
            "Show pictures of the Ka'bah; explain where it is and why."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Islam is built on five: to testify that there is no god but Allah "
            "and that Muhammad is the Messenger of Allah, to establish the prayer, to give zakat, "
            "to fast Ramadan, and to perform Hajj if one is able* (Sahih Bukhari 8, Sahih Muslim 16). "
            "This is the structural framework of Islamic practice. A child who knows the five pillars "
            "can place every ibadah they learn later into its proper place."
        ),
    },
    {
        "slug": "islam-avoid-lying-age10",
        "title": "Always Tell the Truth, Even When It's Hard",
        "category": "social",
        "min_age": 10, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set the baseline** — no lying, ever. Not 'white lies', not jokes that deceive, "
            "not exaggerations that mislead.\n"
            "2. **When caught in a mistake, admit it immediately** — owning up honestly is a massive "
            "habit. Never punish honest admission the way you would punish denial.\n"
            "3. **Catch small lies** — *How was school?* *Good* (when it wasn't). Teach them to say "
            "*Hard* instead. Small honesty builds big honesty.\n"
            "4. **Don't lie in front of them yourself** — including the *tell them I'm not home* kind. "
            "They learn hypocrisy just as fast as they learn the rule.\n"
            "5. **Praise the truth when it costs something** — when they tell you a hard truth that "
            "gets them in trouble, note that the truth-telling was right even though the action was wrong."
        ),
        "parent_note_md": (
            "Allah commands in the Quran: *O you who believe! Have taqwa of Allah and be with the "
            "truthful* (9:119). The Prophet ﷺ said: *Truthfulness leads to righteousness and "
            "righteousness leads to Paradise. A man keeps speaking the truth until he is recorded "
            "with Allah as truthful* (Sahih Bukhari 6094, Sahih Muslim 2607). Truthfulness is not "
            "a trait in Islam; it is the ground on which character stands."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 11 — full Ramadan, Juz Amma, daily Quran habit
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-full-ramadan-fast-age11",
        "title": "Fast Full Days During Ramadan",
        "category": "household",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Be medically honest** — if physically able, aim for the full month. If weaker, "
            "build up through the month (one day on, one off at first).\n"
            "2. **Eat suhoor** — the pre-dawn meal is a sunnah and makes the fast far easier. "
            "Even a glass of water is the minimum.\n"
            "3. **Hydrate at iftar, don't overeat** — the classic mistake. Start with dates and "
            "water, then eat slowly.\n"
            "4. **Pace the day** — no intense sport during fasting hours; read, study, rest.\n"
            "5. **Don't just abstain from food** — the Prophet ﷺ said: *Whoever does not abandon false "
            "speech and acting upon it, Allah has no need that he leaves his food and drink* (Bukhari 6057). "
            "Fasting is from lies, anger, backbiting as well."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- **Listen to the body** — if genuinely unwell (fever, severe headache, faintness), "
            "break the fast. Health matters, and Allah is merciful.\n"
            "- **Menstruating or ill girls** — do not fast; make up the days later. This is Islamic rule.\n"
            "- **Diabetes or other conditions** — consult a doctor and a trusted scholar. Fasting with "
            "a chronic condition may require a modified approach."
        ),
        "parent_note_md": (
            "Ramadan is the fourth pillar of Islam. The Prophet ﷺ said: *Whoever fasts Ramadan out of "
            "faith and hope of reward will have his past sins forgiven* (Sahih Bukhari 38). "
            "Full fasting typically begins around puberty (age 11–13 for most) but can start earlier "
            "for eager, healthy children. The goal is a healthy, well-paced fast, not a proud one."
        ),
    },
    {
        "slug": "islam-memorise-juz-amma-age11",
        "title": "Memorise Ten Surahs from Juz Amma",
        "category": "cognitive",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick the shortest ten first** — An-Nas, Al-Falaq, Al-Ikhlas, Al-Masad, An-Nasr, "
            "Al-Kafirun, Al-Kawthar, Al-Ma'un, Quraysh, Al-Fil. Many already memorised.\n"
            "2. **One surah per week** — new material. Review every previous surah daily.\n"
            "3. **Recite during salah** — rotate through them so each stays fresh.\n"
            "4. **Recite to a teacher or parent monthly** — someone who can correct tajweed mistakes. "
            "Wrong sound learned is hard to unlearn.\n"
            "5. **Write them down from memory** — for Arabic-literate children, writing from memory "
            "deepens retention beyond just reciting."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *The best among you are those who learn the Quran and teach it* "
            "(Sahih Bukhari 5027). Ten memorised surahs is a meaningful milestone: it covers most "
            "surahs that can be recited in nafl (optional) prayers and builds the scaffolding for "
            "memorising the full Juz Amma."
        ),
    },
    {
        "slug": "islam-daily-quran-age11",
        "title": "Recite Quran Daily for 10–15 Minutes",
        "category": "cognitive",
        "min_age": 11, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a fixed time** — after Fajr is ideal (*when dawn reads the Quran*) — or after Maghrib.\n"
            "2. **Read, don't just listen** — open a physical mushaf or app, follow the Arabic "
            "even if reading it slowly.\n"
            "3. **Start from Juz Amma, work forwards** — or tackle Surah Al-Baqarah slowly. "
            "Consistency beats volume.\n"
            "4. **Use tajweed rules learned in class** — if enrolled in a Quran class. If not, "
            "this is a sign to enrol in one.\n"
            "5. **Reflect on one ayah each day** — pick one verse, read a short translation "
            "commentary, think about it during the day."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Whoever reads a letter from the Book of Allah, he will have a "
            "reward, and that reward will be multiplied by ten. I am not saying Alif-Lam-Mim is "
            "one letter; rather, Alif is a letter, Lam is a letter, and Mim is a letter* (Tirmidhi 2910). "
            "Fifteen minutes a day, done for a decade, builds a Quranic relationship that lasts."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 12 — deeper study of meanings, seerah, promises
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-learn-surah-meanings-age12",
        "title": "Learn the Meaning of the Surahs You've Memorised",
        "category": "cognitive",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick one memorised surah** — start with Al-Ikhlas or Al-Asr.\n"
            "2. **Read a translation** — Saheeh International, Pickthall, or Mufti Taqi Usmani's "
            "*The Meanings of the Noble Quran*. Pick a trusted, clear translation.\n"
            "3. **Read a short tafsir** — Tafsir as-Sa'di and Tafsir Ibn Kathir (abridged) are "
            "student-accessible.\n"
            "4. **Summarise in their own words** — *What is this surah teaching?* One paragraph.\n"
            "5. **Move to the next surah only when the first is understood** — not just memorised, but understood."
        ),
        "parent_note_md": (
            "Allah commanded reflection on the Quran: *Do they not ponder over the Quran, or are "
            "there locks upon their hearts?* (47:24). Memorisation without understanding is an "
            "incomplete relationship with the Book. A 12-year-old who understands the surahs they "
            "recite in prayer has prayer with depth, not prayer as recitation."
        ),
    },
    {
        "slug": "islam-study-seerah-makkan-age12",
        "title": "Learn the Makkan Period of the Prophet's Life",
        "category": "cognitive",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a child-level seerah book** — Ar-Raheeq al-Makhtum (Sealed Nectar, abridged "
            "editions exist), or an illustrated seerah.\n"
            "2. **Learn the events in order** — birth, childhood, marriage to Khadijah, revelation "
            "at 40, first converts, public da'wah, boycott, death of Khadijah and Abu Talib, Isra and Mi'raj, Hijra.\n"
            "3. **Memorise key names** — Khadijah, Abu Bakr, Umar, Uthman, Ali, Bilal, Sumayyah, Yasir.\n"
            "4. **Discuss lessons** — how did the Prophet ﷺ deal with persecution? With rejection? "
            "With loss? These become life lessons for the child.\n"
            "5. **Watch a reputable seerah series** — many are available from trusted Islamic institutions."
        ),
        "parent_note_md": (
            "Allah commanded: *In the Messenger of Allah you have an excellent example for whoever "
            "hopes in Allah and the Last Day* (33:21). A child cannot follow the best example without "
            "knowing his life. The Makkan period especially is the story of patience under persecution — "
            "directly applicable to any time a child feels alone in doing the right thing."
        ),
    },
    {
        "slug": "islam-keep-promises-age12",
        "title": "Keep Every Promise You Make",
        "category": "social",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Think before promising** — *Am I sure I can do this?* Don't promise casually.\n"
            "2. **Use InshaAllah** — if it's about the future, always. It's both a religious habit "
            "and a safety net.\n"
            "3. **Write down promises** — small ones too. *I'll help you with maths on Saturday.*\n"
            "4. **If you can't keep it, explain in advance** — not after. Apologise early; reschedule honestly.\n"
            "5. **Never say something you won't do to end a conversation** — that's both a lie and a broken promise."
        ),
        "parent_note_md": (
            "Allah says in the Quran: *And fulfill every engagement, for every engagement will be "
            "enquired into* (17:34). The Prophet ﷺ said: *The signs of a hypocrite are three: when "
            "he speaks, he lies; when he promises, he breaks it; and when he is trusted, he betrays* "
            "(Sahih Bukhari 33, Sahih Muslim 59). Breaking promises is not just a social failing — "
            "in Islam it is a trait of nifaq (hypocrisy). Keeping them is a trait of the believer."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 13 — baligh, halal/haram, prayer without prompt
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-baligh-responsibility-age13",
        "title": "Understand the Responsibility of Baligh",
        "category": "cognitive",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Have the conversation honestly** — puberty marks the start of Islamic legal "
            "accountability. Every deed is now recorded.\n"
            "2. **Know the signs of baligh** — age 15 by lunar calendar at the latest (if signs "
            "haven't appeared); or earlier if the physical signs appear.\n"
            "3. **All five obligatory prayers are now fully obligatory** — missing one is now a sin, "
            "not just a lapse in habit.\n"
            "4. **Ramadan fasting is now fully obligatory** — same standard as adults.\n"
            "5. **Take responsibility for what they see and say** — accountability has begun. "
            "This is empowering, not scary."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *The pen is lifted from three: from the one who sleeps until he "
            "wakes, from the child until he reaches puberty, and from the insane until he regains "
            "his reason* (Abu Dawud 4398, graded sahih). Once puberty arrives, a person is "
            "accountable before Allah for every act — a milestone worth marking with honesty, warmth, "
            "and clarity. A teenager who understands their own accountability has pride in it, not anxiety."
        ),
    },
    {
        "slug": "islam-salah-without-prompt-age13",
        "title": "Pray All Five Daily Prayers Without Being Prompted",
        "category": "household",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set personal reminders** — phone adhan apps, an alarm. External reminder is the bridge; "
            "internal discipline is the goal.\n"
            "2. **Pray at the masjid for Maghrib and Isha** — at least on weekends. Builds the masjid habit.\n"
            "3. **Own making up missed prayers** — no parent should need to ask *did you pray?*\n"
            "4. **Bring salah to school and outings** — find a corner, face qibla, pray. Don't skip "
            "because it's inconvenient.\n"
            "5. **Reflect monthly** — which prayers are easiest? Which hardest? Fajr is the one "
            "most struggle with. Plan for it."
        ),
        "parent_note_md": (
            "At age 13, the parental role shifts from commanding prayer to supporting it. The teenager "
            "is now baligh (most boys and girls by this point) and personally accountable. The Prophet ﷺ "
            "said: *The covenant between us and them is prayer; whoever abandons it has disbelieved* "
            "(Tirmidhi 2621, graded sahih). Owning one's own five prayers is a serious milestone "
            "of Islamic maturity."
        ),
    },
    {
        "slug": "islam-halal-haram-basics-age13",
        "title": "Learn the Basics of Halal and Haram",
        "category": "cognitive",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Food basics** — halal meat, no pork, no alcohol, no carrion or blood. "
            "Gelatine and some flavourings: check.\n"
            "2. **Earning basics** — no riba (interest), no gambling, no cheating in trade. "
            "Fairness and honesty in transactions.\n"
            "3. **Relationship basics** — no premarital physical relationships, modesty in interaction "
            "with the opposite sex, respect for others' privacy and honour.\n"
            "4. **Speech basics** — no backbiting (*ghiba*), no slander (*buhtan*), no mocking, no lying.\n"
            "5. **When in doubt, ask or leave it** — the Prophet ﷺ said: *Leave what causes you "
            "to doubt for what does not* (Tirmidhi 2518, graded sahih)."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *The halal is clear and the haram is clear, and between them are "
            "doubtful matters many people do not know. Whoever avoids the doubtful has protected "
            "his religion and his honour* (Sahih Bukhari 52, Sahih Muslim 1599). At 13, the child "
            "encounters real-world choices: what to eat at a friend's house, what websites to visit, "
            "what conversations to join. Knowing the basic categories helps them navigate without "
            "constant parental consultation."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 14 — names of Allah, Jumu'ah, regular charity
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-names-of-allah-age14",
        "title": "Memorise and Reflect on the 99 Names of Allah (Start with 20)",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with the most familiar** — Ar-Rahman, Ar-Raheem, Al-Malik, Al-Quddus, "
            "As-Salam, Al-Mu'min, Al-Muhaymin, Al-Aziz, Al-Jabbar, Al-Mutakabbir.\n"
            "2. **One name a day** — memorise the Arabic, learn the meaning, read a short reflection.\n"
            "3. **Use them in dua** — *Ya Razzaq, provide for me* when asking for sustenance. "
            "*Ya Ghafur, forgive me* when asking forgiveness. This is a sunnah of dua.\n"
            "4. **Pair each name with a quality to practise** — if Ar-Rahman is the All-Merciful, "
            "am I being merciful today?\n"
            "5. **Build up over a year** — 20 the first month, 40 by six months, all 99 by year's end."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Allah has 99 names, one hundred less one; whoever memorises them "
            "will enter Paradise* (Sahih Bukhari 2736, Sahih Muslim 2677). But memorisation is not "
            "the goal — understanding and living by them is. Each name is an attribute of Allah that "
            "shapes how the believer relates to Him and how they behave in the world."
        ),
    },
    {
        "slug": "islam-jumah-attend-age14",
        "title": "Attend Friday Jumu'ah Prayer Consistently",
        "category": "household",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **For males: Jumu'ah is fard on the baligh Muslim** — plan the week around it, not the other way around.\n"
            "2. **Arrive early** — the sunnah is to come at the first hour; blessings diminish "
            "the later you come (Sahih Bukhari 881).\n"
            "3. **Do the pre-Jumu'ah prep** — ghusl (full bath), clean clothes, perfume/miswak, "
            "walk to the masjid. Each is a sunnah.\n"
            "4. **Listen silently to the khutba** — don't talk, scroll, or even tell someone to be quiet. "
            "The Prophet ﷺ said speaking during the khutba nullifies the reward.\n"
            "5. **Read Surah Al-Kahf on Fridays** — a weekly habit with explicit sunnah grounding."
        ),
        "parent_note_md": (
            "Jumu'ah is the weekly congregation of Muslims, commanded in the Quran: *O you who "
            "believe! When the call is proclaimed to prayer on Friday, hasten earnestly to the "
            "Remembrance of Allah, and leave off business* (62:9). For an adolescent boy, consistent "
            "Jumu'ah is a rite of passage and a weekly reset. The Prophet ﷺ said: *Whoever misses "
            "three Jumu'ahs out of negligence, Allah puts a seal on his heart* (Abu Dawud 1052, "
            "graded sahih)."
        ),
    },
    {
        "slug": "islam-regular-sadaqa-age14",
        "title": "Establish a Regular, Structured Sadaqa Habit",
        "category": "financial",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set a percentage** — even 2–5% of pocket money or earnings. Proportional giving "
            "is more sustainable than a fixed amount.\n"
            "2. **Give at a fixed time** — every Friday, or the 1st of the month. Structure "
            "prevents forgetting.\n"
            "3. **Rotate causes** — local masjid, food for the needy, orphan sponsorship, disaster relief. "
            "Broaden the heart, not just the habit.\n"
            "4. **Give from your own earnings when possible** — not only from pocket money. "
            "Sadaqa from one's own effort teaches the connection between work and giving.\n"
            "5. **Keep it private** — no announcing, no social media posts. Sadaqa loses reward "
            "when it becomes a performance."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *Charity extinguishes sin as water extinguishes fire* (Tirmidhi 614, "
            "graded sahih). Regular giving — especially small and consistent — is more beloved to "
            "Allah than occasional large amounts, as the Prophet ﷺ said: *The most beloved deeds to "
            "Allah are those done consistently, even if small* (Sahih Bukhari 6464, Sahih Muslim 783). "
            "A teenager who has a structured giving habit at 14 carries it for life."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 15 — tafsir, 6 pillars of iman, morning/evening adhkar
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-tafsir-study-age15",
        "title": "Study the Tafsir of Important Surahs",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with Al-Fatiha** — the foundational surah. A full tafsir session on seven "
            "ayahs. Shouldn't be rushed.\n"
            "2. **Then Surah Yasin** — *heart of the Quran* per hadith (Tirmidhi 2887, with weakness in chain). "
            "Its content on resurrection, tawheed, and history is foundational.\n"
            "3. **Then Surah Al-Kahf** — Friday recitation; four major stories (People of the Cave, "
            "the rich man and his garden, Musa and Khidr, Dhul-Qarnayn) each with deep lessons.\n"
            "4. **Use Ibn Kathir or As-Sa'di** — reliable scholars, available in English. Read the "
            "tafsir ayah by ayah, not as a novel.\n"
            "5. **Keep a notebook** — one line per session capturing the main lesson. Over a year, "
            "this is a personal tafsir journal."
        ),
        "parent_note_md": (
            "Allah commands reflection: *This is a Book We have sent down to you, full of blessing, "
            "that they may reflect on its ayahs* (38:29). Tafsir is the bridge between recitation "
            "and life. A 15-year-old reading tafsir regularly develops Islamic thinking — not just "
            "Islamic knowledge — and grounds their worldview in the actual text of the Quran, "
            "not just cultural impressions."
        ),
    },
    {
        "slug": "islam-six-pillars-iman-age15",
        "title": "Learn the Six Pillars of Iman",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Belief in Allah** — His existence, His oneness, His names and attributes without "
            "likening or denial (*la tashbeeh, la ta'teel*).\n"
            "2. **Belief in the angels** — unseen creatures of light, doing Allah's commands. "
            "Learn names: Jibreel, Mika'eel, Israfeel, Malak al-Mawt.\n"
            "3. **Belief in the Divine Books** — Torah, Zabur, Injil (in their original form), Quran "
            "(preserved). Quran is the final and protected revelation.\n"
            "4. **Belief in the Messengers** — from Adam to Muhammad ﷺ. Know the five 'Ulul Azm' "
            "(great messengers): Nuh, Ibraheem, Musa, Isa, Muhammad ﷺ.\n"
            "5. **Belief in the Last Day** — death, grave, resurrection, judgment, hell, paradise. "
            "**And Belief in Qadar** — Allah's decree, both the good and the apparent bad."
        ),
        "parent_note_md": (
            "In the hadith of Jibreel (Sahih Muslim 8), the angel asked the Prophet ﷺ: *What is iman?* "
            "He replied by listing the six pillars. These are the creedal foundation of Islam — "
            "everything a Muslim believes at the level of aqeedah fits into one of these six. "
            "A teenager who knows them explicitly has the mental scaffolding to organise every "
            "religious concept they encounter afterwards."
        ),
    },
    {
        "slug": "islam-morning-evening-adhkar-age15",
        "title": "Build a Morning and Evening Adhkar Habit",
        "category": "household",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use Hisnul Muslim** (*Fortress of the Muslim*) — compact, authenticated, widely available.\n"
            "2. **After Fajr** — Ayatul Kursi, the three *Muawwidhat* (Ikhlas, Falaq, Nas x3), "
            "*Allahumma bika asbahna...* (the morning dua), the dua of Bilal (*Hasbi-Allahu...*).\n"
            "3. **After Asr or before Maghrib** — the evening counterparts of the above.\n"
            "4. **10 minutes max** — enough time to do it sincerely without rushing. Not a chore; a protection.\n"
            "5. **Never skip on busy days** — especially on busy days. These are the adhkar of the Prophet ﷺ "
            "and they guard the day."
        ),
        "parent_note_md": (
            "The adhkar of morning and evening are collected in authenticated hadith across multiple "
            "collections. The Prophet ﷺ said the person who recites *Ayatul Kursi* in the morning "
            "has protection until evening, and the person who recites it in the evening has protection "
            "until morning (Al-Hakim, classed sahih). Ten minutes of adhkar twice a day is a lifetime "
            "habit of spiritual armour."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 16 — community engagement, Islamic finance, 40 Hadith Nawawi
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-community-engagement-age16",
        "title": "Engage With the Muslim Community Through the Masjid",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick the local masjid** — pray at least one congregational prayer there daily "
            "or every other day.\n"
            "2. **Volunteer for at least one role** — Ramadan iftar organising, Saturday school "
            "assistance, new-Muslim mentoring, clean-up.\n"
            "3. **Attend one halaqa (study circle) weekly** — Quran tafsir, seerah, or fiqh. "
            "Community learning beats solo learning for accountability.\n"
            "4. **Know the imam and community elders** — shake their hands, exchange salams, "
            "ask thoughtful questions.\n"
            "5. **Help with Eid, Ramadan, and janazah logistics** — these are high-value moments "
            "where the community pulls together. A willing teenager is remembered."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *The example of the believers in their mutual love, mercy, and "
            "compassion is like that of a body: if one limb complains, the rest of the body responds "
            "with sleeplessness and fever* (Sahih Muslim 2586). A 16-year-old is old enough to become "
            "a contributing member of the ummah, not just a recipient. Community ties built now "
            "hold for life."
        ),
    },
    {
        "slug": "islam-finance-basics-age16",
        "title": "Learn the Basics of Islamic Finance",
        "category": "financial",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Riba (interest) is forbidden** — both paying and receiving. Quran 2:275-279. "
            "This rules out conventional loans, credit card interest, and interest-bearing savings.\n"
            "2. **Halal earning** — honest trade, fair wages, no cheating in weights or quality. "
            "*Whoever cheats us is not of us* (Sahih Muslim 102).\n"
            "3. **Zakat calculation** — 2.5% of wealth above the nisab threshold, held for one lunar year. "
            "Learn the calculation even before you have the wealth.\n"
            "4. **Gharar (uncertainty)** — avoid contracts with major unknowns. Insurance in some forms, "
            "speculative gambling-like trades, are classical examples. Learn the principle.\n"
            "5. **Seek halal alternatives** — Islamic banking, halal investment funds, "
            "profit-and-loss partnerships (*mudarabah*, *musharakah*). The alternatives exist; finding them is part of the adulting."
        ),
        "parent_note_md": (
            "Allah declares in the Quran: *Allah has permitted trade and forbidden riba* (2:275). "
            "The Prophet ﷺ said riba has 73 categories, the least of which is like a man committing "
            "zina with his own mother (Ibn Majah 2274, graded sahih). Islamic finance is not a "
            "niche topic — it shapes how a Muslim chooses a bank, a credit card, a home loan, "
            "a job. Entering adult financial life with knowledge of these rules prevents a lifetime "
            "of unknowingly tangled contracts."
        ),
    },
    {
        "slug": "islam-40-hadith-nawawi-age16",
        "title": "Study the 40 Hadith of Imam An-Nawawi",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Get a trusted translation with commentary** — Dar-us-Salam's edition, or Jamal Zarabozo's "
            "deep three-volume commentary.\n"
            "2. **One hadith a week** — memorise the Arabic text and the translation.\n"
            "3. **Write a one-paragraph reflection per hadith** — what did the Prophet ﷺ mean? "
            "How does it apply today? What is one action point?\n"
            "4. **Complete the set in a year** — 40 weeks. Ten weeks leftover for review.\n"
            "5. **Teach one hadith to a younger sibling or peer** — the Prophet ﷺ said: "
            "*The best of you are those who learn and teach the Quran*; teaching hadith is of the same spirit."
        ),
        "parent_note_md": (
            "Imam An-Nawawi selected 42 ahadith he considered pillars of Islamic practice and "
            "foundational to understanding the religion. They cover intention, worship, manners, "
            "halal and haram, and character. A 16-year-old who has studied all 40 has a compact "
            "library of the Prophet's ﷺ most central teachings ready in their memory for life — "
            "a scholarly foundation in one year's disciplined work."
        ),
    },
]


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = (
        "Seed Islamic tasks across ages 5–16 (religion='islam'). "
        "Grounded in Quran and authentic hadith. Idempotent."
    )

    def handle(self, *args, **options):
        all_envs = list(Environment.objects.all())

        tag_by_category: dict[str, Tag] = {}
        for cat_key, (tag_name, tag_cat) in TAG_FOR_CATEGORY.items():
            tag, _ = Tag.objects.get_or_create(
                name=tag_name, defaults={"category": tag_cat}
            )
            tag_by_category[cat_key] = tag

        added = 0
        updated = 0
        for t in ISLAM_TASKS:
            cat_key = t["category"]
            if cat_key not in tag_by_category:
                self.stdout.write(
                    self.style.ERROR(
                        f"  {t['slug']}: unknown category '{cat_key}', skipping"
                    )
                )
                continue
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
                    "religion": "islam",
                },
            )
            task.tags.set([tag_by_category[cat_key]])
            task.environments.set(all_envs)
            if created:
                added += 1
            else:
                updated += 1

        self.stdout.write(
            f"seed_islam_tasks: {added} new, {updated} updated, "
            f"{added + updated} total."
        )

        # Per-age breakdown
        from collections import Counter
        per_age = Counter(t["min_age"] for t in ISLAM_TASKS)
        self.stdout.write("\nPer-age counts:")
        for age in sorted(per_age):
            self.stdout.write(f"  age {age:>2}: {per_age[age]}")

        self.stdout.write(self.style.SUCCESS("Complete."))
