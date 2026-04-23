"""Management command: add 46 new Islamic tasks (ages 5–16), bringing total to ~85.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_islam_tasks_2

Covers duas, aqeedah (belief/tawhid), sunnah acts, seerah, akhlaq (character),
Ramadan practices, ghusl, social-media ethics, halal awareness, and modesty.
Focuses on practical/behavioural tasks with Quran/hadith grounding.

Idempotent via update_or_create(slug=...).
"""
from django.core.management.base import BaseCommand

from content.models import Environment, ReviewStatus, Tag, Task


TAG_FOR_CATEGORY = {
    "cognitive": ("Reasoning",     Tag.Category.COGNITIVE),
    "social":    ("Social skills", Tag.Category.SOCIAL),
    "household": ("Home care",     Tag.Category.HOUSEHOLD),
    "financial": ("Money basics",  Tag.Category.FINANCIAL),
}

ISLAM_TASKS_2 = [
    # ══════════════════════════════════════════════════════════════════════
    # AGE 5
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-dua-sleep-wake-age5",
        "title": "Say the Dua for Sleeping and Waking Up",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Before sleeping**, say together: *Allahumma bismika amutu wa ahya* "
            "(*O Allah, in Your name I die and I live*).\n"
            "2. **On waking up**, say: *Alhamdulillahil-ladhi ahyana ba'da ma amatana "
            "wa ilayhin-nushur* (*All praise is for Allah who gave us life after having taken it from us, "
            "and unto Him is the resurrection*).\n"
            "3. **Keep a small card** on the bedside table with the Arabic and the meaning until memorised.\n"
            "4. **Make it a nightly ritual** — lights off only after the sleeping dua is said."
        ),
        "parent_note_md": (
            "These duas are authentic sunnah. The sleeping dua is reported in Sahih Bukhari (6312) "
            "and Sahih Muslim (2711). The waking dua is in Sahih Bukhari (6324). Teaching children "
            "to begin and end each day with Allah's name instils God-consciousness (taqwa) naturally."
        ),
    },
    {
        "slug": "islam-tawhid-basic-age5",
        "title": "Understand That Allah Is One (Tawhid Basics)",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Surah Al-Ikhlas** together: *Qul huwa Allahu ahad…* — three short ayahs that "
            "summarise tawhid. Memorise and understand the meaning.\n"
            "2. **Ask 'Who created the sky, trees, and rain?'** — let the child answer: *Allah*.\n"
            "3. **Teach three names of Allah** this month: *Al-Khaliq* (the Creator), *Ar-Rahman* "
            "(the Most Merciful), *Al-'Alim* (the All-Knowing).\n"
            "4. **Connect to daily life** — 'Why do we say Bismillah? Because everything belongs to Allah.'"
        ),
        "parent_note_md": (
            "Tawhid (the oneness of Allah) is the foundation of Islam. The Prophet ﷺ told his cousin "
            "Ibn Abbas: *'The first thing you should call them to is the testimony that there is no god "
            "worthy of worship but Allah'* (Sahih Bukhari 1395, Sahih Muslim 19). Surah Al-Ikhlas is "
            "equivalent to one-third of the Quran in meaning (Sahih Bukhari 5013). Starting early "
            "plants the roots before the branches grow."
        ),
    },
    {
        "slug": "islam-entering-home-sunnah-age5",
        "title": "Say Bismillah and Salam When Entering Home",
        "category": "social",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **At the door**, pause before entering. Say *Bismillah* while stepping in with the **right foot**.\n"
            "2. **Give salam to family** immediately: *As-salamu alaykum wa rahmatullahi wa barakatuh*.\n"
            "3. **Make it a game** — who says salam first when getting home?\n"
            "4. **When leaving**, step out with the **left foot** and say: "
            "*Bismillah, tawakkaltu 'alallah, wa la hawla wa la quwwata illa billah*.\n"
            "5. **Remind gently** when they forget — no scolding, just a soft prompt."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'When a man enters his house and mentions Allah when he enters and "
            "when he eats, the Shaytan says: you have no place to stay and no food tonight. "
            "But if he enters without mentioning Allah, Shaytan says: you have found a place to stay'* "
            "(Sahih Muslim 2018). Salam is a greeting of peace and a dua — spreading it spreads blessings "
            "between family members (Sahih Muslim 54)."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 6
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-dua-after-wudu-age6",
        "title": "Recite the Dua After Making Wudu",
        "category": "cognitive",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **After completing wudu**, look up at the sky and say: "
            "*Ash-hadu an la ilaha illallahu wahdahu la sharika lah, wa ash-hadu anna Muhammadan "
            "abduhu wa rasuluh. Allahumm-aj'alni minat-tawwabin, waj'alni minal-mutatahhirin.*\n"
            "2. **Learn the meaning**: 'I testify there is no god but Allah alone… O Allah make me "
            "of those who repent and of those who purify themselves.'\n"
            "3. **Post a small card** next to the sink until it is memorised.\n"
            "4. **Practise every wudu** — consistency is the goal, not perfection."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Whoever performs ablution and says this dua, "
            "the eight gates of Paradise will be opened for him and he may enter by whichever gate he wishes'* "
            "(Sahih Muslim 234, Tirmidhi 55). This dua combines shahada (testimony of faith) with a "
            "request for continuous repentance and purity — a perfect pairing with the physical act of wudu."
        ),
    },
    {
        "slug": "islam-memorise-kafirun-age6",
        "title": "Memorise Surah Al-Kafirun and Know Its Meaning",
        "category": "cognitive",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Listen** to a clear recitation of Surah Al-Kafirun (6 verses) every day for a week.\n"
            "2. **Repeat verse by verse** after the recording or parent.\n"
            "3. **Learn the meaning**: 'Say: O disbelievers, I do not worship what you worship… "
            "For you is your religion and for me is mine.' — a declaration of clarity and respect.\n"
            "4. **Recite it in Fajr and Maghrib** sunnah rakats — the Prophet ﷺ often recited it there.\n"
            "5. **Test understanding**: ask 'What is this surah telling us about our religion?'"
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Recite Surah Al-Kafirun before sleeping — it is a declaration of "
            "freedom from shirk'* (Abu Dawud 5055, authenticated by Al-Albani). The surah teaches "
            "both clarity of belief and respectful coexistence — a balance children need early. "
            "Short surahs learnt young are remembered for life."
        ),
    },
    {
        "slug": "islam-allah-watching-age6",
        "title": "Understand That Allah Sees Everything (Muraqabah)",
        "category": "cognitive",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with a story**: tell the hadith of Jibreel asking the Prophet ﷺ about ihsan "
            "(*'Worship Allah as though you see Him; if you cannot, know that He sees you'*).\n"
            "2. **Apply it daily**: when the child is about to do something wrong, gently ask — "
            "'Does Allah see what you are about to do?'\n"
            "3. **Also apply to goodness**: 'Allah saw you being kind just now — He never misses it.'\n"
            "4. **Avoid fear-only framing** — muraqabah is about love and awareness, not just punishment."
        ),
        "parent_note_md": (
            "The concept of ihsan — worshipping Allah as if you see Him — is from the Hadith of Jibreel "
            "(Sahih Muslim 8), one of the most comprehensive hadith in Islam. Allah says: "
            "*'He knows the treachery of the eyes and what the breasts conceal'* (Quran 40:19). "
            "Teaching this awareness early builds internal moral regulation rather than external compliance."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 7
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-kalima-tayyibah-age7",
        "title": "Understand the Full Meaning of La ilaha illallah",
        "category": "cognitive",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Break it down word by word** with the child: *La* (no) + *ilaha* (god worthy of worship) "
            "+ *illallah* (except Allah). Full meaning: 'There is no god worthy of worship except Allah.'\n"
            "2. **Discuss what 'worship' means**: it is not just prayer — love, fear, hope, obedience, trust.\n"
            "3. **What does it negate?** — wealth, status, people, desires as the ultimate authority.\n"
            "4. **Memorise the full first kalima** including Muhammad Rasulullah.\n"
            "5. **Recite it 10 times** after Fajr and after Maghrib as a daily habit."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'The best remembrance is La ilaha illallah'* (Tirmidhi 3383, hasan). "
            "This kalima is not just a verbal formula — it is a statement of loyalty and liberation. "
            "Understanding it deeply (not just reciting it) is what gives it weight. "
            "Ibn Al-Qayyim wrote that this word requires knowledge, certainty, acceptance, compliance, "
            "truthfulness, sincerity, and love — all character qualities worth cultivating."
        ),
    },
    {
        "slug": "islam-dua-bathroom-age7",
        "title": "Say the Dua When Entering and Leaving the Bathroom",
        "category": "cognitive",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Before entering**: step in with the **left foot** and say quietly: "
            "*Allahumma inni a'udhu bika minal khubuthi wal khaba'ith* (O Allah, I seek refuge in You from "
            "male and female evil spirits).\n"
            "2. **On leaving**: step out with the **right foot** and say: *Ghufranaka* (I seek Your forgiveness).\n"
            "3. **Remind consistently** until it is a reflex.\n"
            "4. **Explain why**: the bathroom is a place where shaytan likes to linger — the dua is protection."
        ),
        "parent_note_md": (
            "The entering dua is from Sahih Bukhari (142) and Sahih Muslim (375). "
            "The exiting dua *Ghufranaka* is from Abu Dawud (30), Tirmidhi (7), and Ibn Majah (300) — "
            "all authenticated. This small habit teaches children that Islamic etiquette covers every moment "
            "of life, and that seeking forgiveness is a constant disposition, not just for big sins."
        ),
    },
    {
        "slug": "islam-truthful-always-age7",
        "title": "Practice Telling the Truth Even When It Is Hard",
        "category": "social",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Role-play scenarios**: you broke something, you forgot your homework, you took a biscuit "
            "without asking. Practise saying the truth calmly.\n"
            "2. **Praise truth-telling** — even when the news is bad. Never punish a child more severely "
            "for telling the truth than for the original mistake.\n"
            "3. **Discuss the Prophet ﷺ's title** — *Al-Amin* (the Trustworthy) — before prophethood.\n"
            "4. **Teach the chain**: truth → trust → good character → Allah's love."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Truthfulness leads to righteousness, and righteousness leads to "
            "Paradise. A man keeps telling the truth until he is recorded with Allah as a Siddiq (truthful). "
            "Lying leads to wickedness, and wickedness leads to Hellfire'* (Sahih Bukhari 6094, Muslim 2607). "
            "Age 7 is when the aql (rational faculty) begins to develop — an ideal time to internalise this virtue."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 8
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-angels-belief-age8",
        "title": "Learn About the Angels (Belief in Mala'ikah)",
        "category": "cognitive",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain belief in angels** as the second pillar of iman: they are created from light, "
            "do not disobey Allah, and carry out His commands.\n"
            "2. **Learn 10 named angels** and their roles: Jibreel (revelation), Mikaeel (rain and provision), "
            "Israfeel (blowing the trumpet), Izra'eel (taking souls), "
            "Munkar and Nakeer (questioning in the grave), Kiraman Katibin (recording deeds), "
            "Ridwan (guardian of Paradise), Malik (guardian of Hellfire), Raqeeb and Ateed (two recorders).\n"
            "3. **Discuss the Kiraman Katibin** — they are always with us. Ask: 'What would you want "
            "them to record today?'\n"
            "4. **Use a worksheet** to draw and label each angel's role."
        ),
        "parent_note_md": (
            "Belief in angels is explicitly listed in the Quran: *'The Messenger has believed in what "
            "was revealed to him from his Lord, and so have the believers. All of them have believed in "
            "Allah, His angels, His books, and His messengers'* (Quran 2:285). The Hadith of Jibreel "
            "(Sahih Muslim 8) also lists it as a pillar of iman. Children who understand the unseen "
            "world develop a more complete spiritual awareness."
        ),
    },
    {
        "slug": "islam-sunnah-acts-daily-age8",
        "title": "Adopt 5 Daily Sunnah Acts of the Prophet ﷺ",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose 5 sunnah acts** from this list and practise all 5 for one month:\n"
            "   - Using a miswak (or brushing teeth) before prayer\n"
            "   - Drinking water in three sips seated\n"
            "   - Eating with the right hand from the near side of the plate\n"
            "   - Sleeping on the right side\n"
            "   - Smiling at family members as an act of sadaqah\n"
            "   - Saying *Yarhamukallah* when someone sneezes and says Alhamdulillah\n"
            "2. **Make a tracker chart** — tick each sunnah daily.\n"
            "3. **Discuss why** the Prophet ﷺ did these things — they are beneficial for health and character."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Whoever revives my sunnah loves me, and whoever loves me will be "
            "with me in Paradise'* (Tirmidhi 2678). Daily sunnah acts are accessible entry points — "
            "they do not require a specific event and build constant mindfulness. "
            "Allah says: *'In the Messenger of Allah you have an excellent example for whoever hopes "
            "in Allah and the Last Day'* (Quran 33:21)."
        ),
    },
    {
        "slug": "islam-avoid-backbiting-age8",
        "title": "Understand Why Backbiting (Gheebah) Is Haram",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the definition**: backbiting (*gheebah*) means mentioning your brother or sister "
            "in a way they would dislike, even if it is true.\n"
            "2. **Role-play** — tell a short story where a child says something negative about a classmate. "
            "Ask: 'Was that backbiting? How did the absent person feel?'\n"
            "3. **Teach the self-check**: before speaking about someone, ask — 'Would they mind if they "
            "could hear me right now?'\n"
            "4. **Practise changing the subject** when backbiting starts in a group.\n"
            "5. **Discuss the Quran verse** — eating the flesh of your dead brother (metaphor for gheebah)."
        ),
        "parent_note_md": (
            "Allah says: *'Do not backbite one another. Would one of you like to eat the flesh of his "
            "dead brother? You would hate it'* (Quran 49:12). The Prophet ﷺ defined it clearly: "
            "*'Do you know what backbiting is? It is to mention your brother in a way he would dislike'* "
            "(Sahih Muslim 2589). Age 8 is when peer conversations begin and the habit of gossip can "
            "start — an excellent time to build this awareness."
        ),
    },
    {
        "slug": "islam-dua-leave-enter-home-age8",
        "title": "Memorise the Dua for Leaving the House",
        "category": "cognitive",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Memorise the dua**: *Bismillah, tawakkaltu 'alallahi, wa la hawla wa la quwwata "
            "illa billah* (In the name of Allah, I place my trust in Allah, and there is no might "
            "nor power except with Allah).\n"
            "2. **Say it every morning** before leaving for school — left foot first, door still open.\n"
            "3. **Learn the promised benefit**: the Prophet ﷺ said whoever says it, Allah tells "
            "the shaytan 'You have no authority over this person today.'\n"
            "4. **Pair it** with the entering-home sunnah (Bismillah, right foot, salam to family)."
        ),
        "parent_note_md": (
            "Abu Dawud (5095) and Tirmidhi (3426) report: *'Whoever says this dua when leaving home, "
            "it will be said: your needs are met, your enemy is repelled, and you are protected. "
            "The shaytan withdraws from him'* (authenticated by Al-Albani). "
            "Teaching this dua gives children a practical tool for tawakkul (reliance on Allah) "
            "before facing the day."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 9
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-dua-for-parents-age9",
        "title": "Make Dua for Your Parents Every Day",
        "category": "social",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the Quranic dua**: *Rabbir-hamhuma kama rabbayani saghira* "
            "(My Lord, have mercy on them both as they raised me when I was small).\n"
            "2. **Make it a daily habit** — say it after each salah or at bedtime.\n"
            "3. **Personalise it**: add specific duas, e.g., 'O Allah, keep my mother healthy and "
            "my father in your protection.'\n"
            "4. **Discuss why**: parents have the greatest right over us; their duas for us are "
            "answered and so are ours for them.\n"
            "5. **If a parent is deceased**, explain that dua continues and reaches them — "
            "this is among the deeds that benefit the dead."
        ),
        "parent_note_md": (
            "The dua is from Quran 17:24 — the same verse that commands not even saying 'uff' to parents. "
            "The Prophet ﷺ said: *'Three duas are answered without doubt: the dua of the oppressed, "
            "the traveller, and the parent for their child'* (Tirmidhi 1905). "
            "Teaching children to make dua for parents builds gratitude, love, and an understanding "
            "of their rights simultaneously."
        ),
    },
    {
        "slug": "islam-all-prophets-belief-age9",
        "title": "Learn the Names of 25 Prophets Mentioned in the Quran",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **List the 25 prophets** mentioned by name in the Quran (Adam, Idrees, Nuh, Hud, "
            "Saleh, Ibrahim, Lut, Ismail, Ishaq, Yaqub, Yusuf, Shu'ayb, Ayyub, Dhul-Kifl, Musa, "
            "Harun, Dawud, Sulayman, Ilyas, Al-Yasa', Yunus, Zakariyya, Yahya, Isa, Muhammad ﷺ).\n"
            "2. **Learn 5 names per week** until all 25 are known.\n"
            "3. **Match each to their nation** — Nuh to his flood, Yunus to the whale, Musa to Pharaoh.\n"
            "4. **Test using a blank table** — fill in names from memory."
        ),
        "parent_note_md": (
            "Belief in all the prophets is a pillar of iman. The Quran says: *'We make no distinction "
            "between any of His messengers'* (Quran 2:285). The Prophet ﷺ said: *'Allah sent 124,000 "
            "prophets, 315 of whom were messengers'* (Ahmad, authenticated by Ibn Hibban). "
            "Knowing these 25 by name connects children to the full chain of divine guidance and builds "
            "reverence for the prophetic tradition."
        ),
    },
    {
        "slug": "islam-kind-to-neighbors-age9",
        "title": "Show Regular Kindness to Neighbours",
        "category": "social",
        "min_age": 9, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know your neighbours** — learn the names and faces of at least 3 nearby families.\n"
            "2. **Do one kind act per week**: say salam when you see them, hold the door, share food "
            "from home cooking, ask if they need help carrying groceries.\n"
            "3. **Do not cause disturbance** — lowering noise, not blocking their driveway, being "
            "considerate of their space is also a right of the neighbour.\n"
            "4. **Discuss the Quran verse** about neighbours — their rights are extensive in Islam."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Jibreel kept advising me about the neighbour until I thought he "
            "would make him an heir'* (Sahih Bukhari 6014, Sahih Muslim 2625). Allah says: "
            "*'Worship Allah… and do good to parents, relatives, orphans, the poor, the near neighbour, "
            "the distant neighbour…'* (Quran 4:36). Children who learn neighbourly kindness early "
            "grow into citizens who strengthen communities."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 10
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-dhikr-after-salah-age10",
        "title": "Recite the Three Tasbihs After Every Salah",
        "category": "cognitive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **After the salam** ending each salah, recite:\n"
            "   - *Subhanallah* 33 times (Glory be to Allah)\n"
            "   - *Alhamdulillah* 33 times (All praise is for Allah)\n"
            "   - *Allahu Akbar* 34 times (Allah is the Greatest)\n"
            "2. **Use fingers** to count — right hand, starting from the index finger.\n"
            "3. **Add Ayatul Kursi** (Quran 2:255) before the tasbihs — the Prophet ﷺ recommended it.\n"
            "4. **Do not rush** — the tasbihs take about 90 seconds. Make them conscious, not mechanical."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Whoever says SubhanAllah 33 times, Alhamdulillah 33 times, "
            "Allahu Akbar 34 times after every salah, all his sins will be forgiven even if they are "
            "like the foam of the sea'* (Sahih Muslim 597). Ayatul Kursi after salah is from "
            "Nasa'i (9928) and is graded sahih by Al-Albani. These post-salah adhkar turn five "
            "daily prayers into ten daily pauses for gratitude and remembrance."
        ),
    },
    {
        "slug": "islam-tarawih-ramadan-age10",
        "title": "Attend or Pray Tarawih During Ramadan",
        "category": "cognitive",
        "min_age": 10, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain tarawih**: optional night prayer in Ramadan, 8 or 20 rakats, performed in "
            "the masjid or at home after Isha.\n"
            "2. **Start with 8 rakats at home** if the masjid is not accessible.\n"
            "3. **Go to the masjid** when possible — the communal experience has special merit.\n"
            "4. **Encourage listening** to the Quran recitation carefully, even without understanding "
            "every word.\n"
            "5. **Let the child track** how many nights of tarawih they complete in Ramadan."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Whoever prays qiyam in Ramadan with faith and hoping for reward, "
            "his past sins will be forgiven'* (Sahih Bukhari 37, Sahih Muslim 760). "
            "Tarawih is the primary extra act of worship in Ramadan — attending with family from age 10 "
            "builds a lifelong Ramadan identity. The reward is linked to faith and intention, not "
            "just physical attendance."
        ),
    },
    {
        "slug": "islam-akhira-belief-age10",
        "title": "Understand the Stages of the Afterlife (Akhira)",
        "category": "cognitive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Map the stages** in order: death → questioning in the grave (munkar and nakeer) → "
            "barzakh → the Trumpet (soor) → resurrection → the weighing of deeds (mizan) → "
            "the bridge (sirat) → Paradise or Hellfire.\n"
            "2. **Learn two descriptions of Paradise** from the Quran or hadith that the child finds "
            "beautiful.\n"
            "3. **Discuss**: 'How does thinking about the akhira change how you behave today?'\n"
            "4. **Remind during decisions**: 'Is this something you'd be happy having on your record?'"
        ),
        "parent_note_md": (
            "Belief in the Last Day (yawm al-qiyama) is a pillar of iman (Hadith of Jibreel, Sahih Muslim 8). "
            "The Prophet ﷺ said: *'The intelligent person is one who restrains his soul and works for "
            "what is after death'* (Tirmidhi 2459). Children who have a concrete, positive picture of the "
            "akhira are more motivated to do good — and the detailed Quranic descriptions make it "
            "a powerful teaching tool."
        ),
    },
    {
        "slug": "islam-silat-ar-rahm-age10",
        "title": "Maintain Ties With Extended Family (Silat Ar-Rahm)",
        "category": "social",
        "min_age": 10, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **List five extended relatives**: grandparents, aunts, uncles, cousins.\n"
            "2. **Take action monthly**: call, visit, or send a gift or message of goodwill to one "
            "of them.\n"
            "3. **Accompany parents** on family visits instead of staying on devices.\n"
            "4. **Greet relatives warmly** by name — remember their names, ask about their lives.\n"
            "5. **Discuss the hadith**: silat ar-rahm extends lifespan and increases rizq — "
            "connect this to daily motivation."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Whoever wishes to have his provision expanded and his lifespan "
            "extended, let him maintain ties of kinship'* (Sahih Bukhari 5986, Sahih Muslim 2557). "
            "Allah warns: *'Would you then, if you were given authority, cause corruption on earth "
            "and sever your ties of kinship? Such are the ones whom Allah has cursed'* (Quran 47:22-23). "
            "Family ties are not optional in Islam — they are a form of worship."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 11
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-rawatib-sunnah-age11",
        "title": "Pray the 12 Rawatib Sunnah Prayers Daily",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the 12 rawatib rakats** confirmed by hadith:\n"
            "   - 2 before Fajr\n"
            "   - 4 before Dhuhr + 2 after Dhuhr\n"
            "   - 2 after Maghrib\n"
            "   - 2 after Isha\n"
            "2. **Start with 2 before Fajr** — the most emphasised (the Prophet ﷺ never missed these).\n"
            "3. **Add one more pair** each week until all 12 are consistent.\n"
            "4. **Pray at home** — the Prophet ﷺ preferred sunnah prayers at home."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Whoever prays 12 rakats of sunnah per day, Allah will build a house "
            "for him in Paradise'* (Sahih Muslim 728). The 2 rakats before Fajr are especially emphasised: "
            "*'The two rakats of Fajr are better than this world and everything in it'* (Sahih Muslim 725). "
            "At age 11, children can establish a full daily prayer routine including sunnah — "
            "these 12 rakats take under 15 minutes total."
        ),
    },
    {
        "slug": "islam-anger-control-age11",
        "title": "Use Islamic Tools to Control Anger",
        "category": "social",
        "min_age": 11, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Memorise the hadith**: *'The strong person is not the one who can wrestle. "
            "The strong person is the one who controls himself when angry.'*\n"
            "2. **Learn the three steps** when angry:\n"
            "   - Say *A'udhu billahi minash-shaytan ir-rajim* (the anger comes from shaytan)\n"
            "   - If standing, sit down; if sitting, lie down\n"
            "   - Make wudu — cold water calms the inner fire\n"
            "3. **Role-play** a frustrating scenario and practise all three steps.\n"
            "4. **Track it** — notice what triggered anger this week. Awareness is step one."
        ),
        "parent_note_md": (
            "The wrestling hadith is from Sahih Bukhari (6114) and Sahih Muslim (2609). "
            "The remedy of sitting is from Abu Dawud (4782), and of wudu from Ahmad (17985). "
            "The request 'give me advice' — the Prophet ﷺ replied three times: *'Do not be angry'* "
            "(Sahih Bukhari 6116). Adolescence is a peak window for anger management — "
            "teaching these tools before emotions intensify is strategic parenting."
        ),
    },
    {
        "slug": "islam-qadar-belief-age11",
        "title": "Understand Belief in Qadar (Divine Decree)",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the four levels of qadar**: Allah's knowledge of all things, "
            "His writing of all in Al-Lawh Al-Mahfoodh, His will (nothing happens outside it), "
            "and His creation of all things.\n"
            "2. **Address the common confusion**: 'If everything is decreed, why make effort?' "
            "Answer: the effort is part of the decree; Allah commands the means, not just the end.\n"
            "3. **Discuss grief and trial**: when something bad happens, *'Qaddarallahu wa ma sha'a "
            "fa'al'* — this is sunnah to say and it brings peace.\n"
            "4. **Relate it to gratitude**: good things came by Allah's decree — so thank Him, not luck."
        ),
        "parent_note_md": (
            "Belief in qadar, both good and bad, is the sixth and final pillar of iman (Hadith of Jibreel, "
            "Sahih Muslim 8). The Prophet ﷺ said: *'Know that what has missed you was never going to hit "
            "you, and what has hit you was never going to miss you'* (Abu Dawud 4699, authenticated). "
            "Correct understanding of qadar prevents both arrogance in success and despair in hardship — "
            "two of the most important psychological tools an adolescent needs."
        ),
    },
    {
        "slug": "islam-last-10-nights-age11",
        "title": "Worship Intensely in the Last 10 Nights of Ramadan",
        "category": "cognitive",
        "min_age": 11, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain laylatul qadr**: better than 1000 months — equal to 83+ years of worship in "
            "one night. It falls in the odd nights of the last 10 of Ramadan (21, 23, 25, 27, 29).\n"
            "2. **Make a plan**: wake up for tahajjud on the odd nights; recite extra Quran; "
            "make long personal duas.\n"
            "3. **Learn the dua of laylatul qadr**: *Allahumma innaka 'afuwwun tuhibbul-'afwa "
            "fa'fu 'anni* (O Allah, You are Pardoning and love pardon, so pardon me).\n"
            "4. **Do i'tikaf** (seclusion in the masjid) if possible — even for one night.\n"
            "5. **Track each night** — a simple checklist of what was done."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Search for Laylatul Qadr in the odd nights of the last ten "
            "nights of Ramadan'* (Sahih Bukhari 2017). The dua was taught by the Prophet ﷺ to "
            "Aisha (Tirmidhi 3513, sahih). He would intensify worship, wake his family, and "
            "tighten his belt in these nights (Sahih Bukhari 2024). Teaching children to "
            "invest in these nights early creates a lifelong Ramadan anchor."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 12
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-ghusl-proper-age12",
        "title": "Learn How to Perform Ghusl (Ritual Bath) Correctly",
        "category": "household",
        "min_age": 12, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn when ghusl is obligatory**: after sexual dreams (ihtilam), menstruation (for girls), "
            "janabah, and on death (done by others). Ghusl is also recommended before Jumu'ah and on Eid.\n"
            "2. **Learn the obligatory steps** (the minimum for ghusl to be valid):\n"
            "   - Intention (niyyah)\n"
            "   - Rinse the mouth\n"
            "   - Rinse the nose\n"
            "   - Pour water over the entire body so no hair or skin is left dry\n"
            "3. **Learn the full sunnah method**: wash hands first, wash private parts, "
            "make full wudu, then wash body three times starting from right.\n"
            "4. **Discuss with a same-sex parent** or trusted adult in private."
        ),
        "parent_note_md": (
            "Ghusl becomes practically relevant at puberty — teaching it just before is ideal. "
            "The obligatory elements are consensus (ijma') among the four madhabs. "
            "The sunnah method is from Sahih Bukhari (248) and Sahih Muslim (316) via Aisha's description. "
            "Neglecting ghusl invalidates salah — children reaching puberty need practical fiqh, "
            "not just theoretical knowledge. Discuss it calmly and with correct fiqh terminology."
        ),
    },
    {
        "slug": "islam-seerah-madinah-age12",
        "title": "Learn the Key Events of the Madinah Period of Seerah",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Study the hijra** — why it happened, the journey, arrival in Madinah.\n"
            "2. **Learn the key events in order**: building the masjid, the Constitution of Madinah, "
            "Battle of Badr, Battle of Uhud, Battle of Khandaq (Trench), Treaty of Hudaybiyyah, "
            "Conquest of Makkah, Farewell Hajj and sermon.\n"
            "3. **Discuss the lessons** from each event — leadership, patience, strategy, justice.\n"
            "4. **Use a timeline** drawn on paper or a seerah book chart.\n"
            "5. **Discuss the Prophet ﷺ's character** throughout — forgiving those who hurt him."
        ),
        "parent_note_md": (
            "The Madinah period covers the final 10 years of the Prophet's ﷺ life and contains the "
            "full model of Islamic governance, community, conflict resolution, and mercy. "
            "The Prophet ﷺ said: *'Learn the events of my people as you learn the Quran'* "
            "(reported by Ibn Hibban). Seerah at age 12 gives adolescents a role model grounded "
            "in real history rather than abstract ideals — directly relevant to identity formation."
        ),
    },
    {
        "slug": "islam-control-tongue-age12",
        "title": "Guard the Tongue — Practise 24-Hour Speech Audit",
        "category": "social",
        "min_age": 12, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the five categories** of speech in Islam: obligatory (testimony of truth), "
            "recommended (dhikr, teaching), neutral, disliked (pointless chatter), and forbidden "
            "(lying, backbiting, cursing).\n"
            "2. **Do a 24-hour speech audit**: for one full day, mentally note every time you say "
            "something in each category.\n"
            "3. **Identify patterns**: Is there a lot of neutral/pointless talk? Social media messages count.\n"
            "4. **Apply the rule of three**: before speaking, ask — Is it true? Is it kind? Is it necessary?\n"
            "5. **Replace idle talk** with dhikr during quiet moments — *Subhanallah, Alhamdulillah, etc.*"
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Whoever believes in Allah and the Last Day, let him speak good or "
            "remain silent'* (Sahih Bukhari 6018, Sahih Muslim 47). He also said: *'A person may utter "
            "a word without thinking that it will cause him to fall into the Fire deeper than the distance "
            "between east and west'* (Sahih Bukhari 6477, Muslim 2988). At age 12, speech becomes social "
            "currency — this audit helps children develop self-awareness before it becomes a habit."
        ),
    },
    {
        "slug": "islam-tawbah-practice-age12",
        "title": "Learn How to Make Sincere Tawbah (Repentance)",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the three conditions** for valid tawbah:\n"
            "   - Stop the sin immediately\n"
            "   - Feel genuine regret\n"
            "   - Resolve not to return to it\n"
            "2. **Add a fourth** if the sin involved another person: make amends or seek forgiveness.\n"
            "3. **Learn Sayyid al-Istighfar** — the master dua of seeking forgiveness (Sahih Bukhari 6306).\n"
            "4. **Teach**: tawbah wipes the sin completely — Allah loves those who repent constantly.\n"
            "5. **Practise it weekly** — make tawbah a habitual act, not just reserved for big mistakes."
        ),
        "parent_note_md": (
            "Allah says: *'Indeed, Allah loves those who are constantly repentant and loves those who "
            "purify themselves'* (Quran 2:222). The Prophet ﷺ said: *'By Allah, I seek Allah's "
            "forgiveness and repent to Him more than 70 times a day'* (Sahih Bukhari 6307). "
            "Teaching tawbah at puberty — when guilt and shame are heightened — is psychologically "
            "essential. It gives adolescents a path back from mistakes without despair."
        ),
    },
    {
        "slug": "islam-laylatul-qadr-age12",
        "title": "Understand the Significance of Laylatul Qadr",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Surah Al-Qadr** (chapter 97) with tafsir — understand each ayah.\n"
            "2. **Calculate 1000 months**: approximately 83 years and 4 months — "
            "worship in one night = more than a lifetime.\n"
            "3. **Learn what happens**: the angels and Ruh (Jibreel) descend; peace prevails until "
            "the break of dawn.\n"
            "4. **Make a personal worship plan** for the odd nights — Quran, dua, dhikr, salah.\n"
            "5. **Discuss why Allah hid the exact night**: so we would worship all odd nights, "
            "not just one."
        ),
        "parent_note_md": (
            "Surah Al-Qadr states: *'The Night of Decree is better than a thousand months'* (Quran 97:3). "
            "The Prophet ﷺ said: *'Whoever stands in prayer on Laylatul Qadr with faith and hoping "
            "for reward, his past sins are forgiven'* (Sahih Bukhari 1901). Understanding the *why* "
            "behind Ramadan peaks at this age — children who understand significance are more likely "
            "to invest their later adolescent Ramadans deeply."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 13
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-four-caliphs-age13",
        "title": "Study the Lives of the Four Rightly-Guided Caliphs",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Study each Caliph** over four weeks: Abu Bakr (1 week), Umar (1 week), "
            "Uthman (1 week), Ali (1 week).\n"
            "2. **For each, identify**: their unique quality, their greatest achievement, "
            "the challenge they faced, and one hadith about them from the Prophet ﷺ.\n"
            "3. **Discuss leadership lessons** — how do their styles differ? What can you apply today?\n"
            "4. **Abu Bakr**: unshakeable loyalty. **Umar**: justice and governance. "
            "**Uthman**: generosity and compilation of the Quran. **Ali**: knowledge and wisdom."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Follow my sunnah and the sunnah of the rightly-guided caliphs after me'* "
            "(Abu Dawud 4607, authenticated). He named Abu Bakr and Umar by name as guides (Tirmidhi 3662). "
            "The four caliphs are not just history — they are models of how Islam is to be applied in "
            "leadership, governance, and personal life. Studying them at 13 gives adolescents concrete "
            "Muslim role models who were real people facing real challenges."
        ),
    },
    {
        "slug": "islam-halal-food-labels-age13",
        "title": "Read Food Labels and Identify Halal/Haram Ingredients",
        "category": "household",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the haram categories**: pork and pork derivatives, alcohol, "
            "non-zabiha animal products (gelatine, lard, rennet).\n"
            "2. **Learn the suspicious E-numbers**: E120 (carmine, from insects), "
            "E441 (gelatine), E470/E471 (may be animal-derived).\n"
            "3. **Pick up 5 food items at home** and read the ingredients together. "
            "Look up any unfamiliar items.\n"
            "4. **Check for halal certification** logos — know which logos are trusted in your country.\n"
            "5. **Discuss the principle**: when in doubt, leave it out (*ihtiyat*) — "
            "and ask someone who knows."
        ),
        "parent_note_md": (
            "Allah says: *'O you who have believed, eat from the good things which We have provided "
            "for you and be grateful to Allah if it is indeed Him that you worship'* (Quran 2:172). "
            "Halal eating at home is maintained by parents — but at 13, children start buying food "
            "independently (school canteens, shops). Equipping them to read labels is practical fiqh "
            "for real-world independence."
        ),
    },
    {
        "slug": "islam-social-media-ethics-age13",
        "title": "Apply Islamic Ethics to Social Media Use",
        "category": "social",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Apply the tongue rules to text**: everything said online is recorded — "
            "the Kiraman Katibin do not only record spoken words.\n"
            "2. **Identify prohibited online acts**: mocking, cyberbullying, sharing unverified news, "
            "exposing others' private matters, following haram content.\n"
            "3. **Learn the news rule** — Quran 49:6: verify before sharing. Default: do not share "
            "what you cannot verify as true.\n"
            "4. **Audit your feed**: does it increase knowledge, inspiration, or heedlessness? "
            "Unfollow accounts that weaken your iman.\n"
            "5. **Set a daily screen-time limit** and make niyyah before opening social media."
        ),
        "parent_note_md": (
            "Allah says: *'O you who have believed, if there comes to you a disobedient one with "
            "information, investigate, lest you harm a people out of ignorance'* (Quran 49:6). "
            "The Prophet ﷺ said: *'It is enough of a lie for a man to repeat everything he hears'* "
            "(Sahih Muslim, introduction, authentic). Islam's speech ethics predate social media "
            "by 1400 years — they apply identically. At 13, social media is entering the child's "
            "life and Islamic frameworks need to arrive first."
        ),
    },
    {
        "slug": "islam-niyyah-intention-age13",
        "title": "Develop the Habit of Making Niyyah Before Every Action",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start each day** with an intention: 'I intend to please Allah in everything I do today.'\n"
            "2. **Before each act**, make a conscious intention to do it for Allah: studying, "
            "helping at home, being kind — all can be ibadah with the right niyyah.\n"
            "3. **Practise converting neutral acts** to ibadah: sleeping to rest the body for worship, "
            "eating to have strength to obey Allah, working to provide halal earnings.\n"
            "4. **Discuss the hadith**: the entire reward of an action can hang on the intention.\n"
            "5. **Check intentions** at the end of the day — how many actions were genuinely for Allah?"
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Actions are only by intentions, and every person will have only "
            "what they intended'* (Sahih Bukhari 1, Sahih Muslim 1907) — this is the first hadith "
            "in Sahih Bukhari for a reason. Niyyah transforms the entire moral value of an action. "
            "At 13, adolescents are building a self-concept — teaching them to be deliberate in "
            "intention gives their actions direction and spiritual weight beyond external compliance."
        ),
    },
    {
        "slug": "islam-friday-sunnah-age13",
        "title": "Follow the Full Sunnah of Jumu'ah (Friday)",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the sunnah acts of Jumu'ah** in order:\n"
            "   - Ghusl (bath) before Jumu'ah\n"
            "   - Wear clean, best clothing\n"
            "   - Apply pleasant scent if available\n"
            "   - Go early to the masjid\n"
            "   - Recite Surah Al-Kahf (or as much as possible)\n"
            "   - Increase salawat on the Prophet ﷺ\n"
            "   - Make dua in the last hour before Maghrib\n"
            "2. **Implement all 7 acts** on Friday for one month.\n"
            "3. **Explain the expiation**: Jumu'ah to Jumu'ah wipes minor sins in between."
        ),
        "parent_note_md": (
            "Jumu'ah ghusl: Sahih Bukhari 877. Best clothing: Ibn Majah 1097. Surah Al-Kahf: "
            "authenticated by Al-Albani (Silsilah As-Sahihah 651). Salawat on Friday: Abu Dawud 1047. "
            "The hidden hour of accepted dua: Sahih Muslim 852. The Prophet ﷺ said: "
            "*'The five daily prayers, and Jumu'ah to Jumu'ah, are expiations for what is between them, "
            "as long as major sins are avoided'* (Sahih Muslim 233). Friday is Islam's weekly spiritual "
            "reset — teaching children to maximise it builds a weekly rhythm of renewal."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 14
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-duha-prayer-age14",
        "title": "Pray Salat Ad-Duha (Forenoon Prayer) Regularly",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the time**: Duha begins 20 minutes after sunrise and ends 10–15 minutes before "
            "Dhuhr. Minimum 2 rakats, maximum 8 or 12 according to different reports.\n"
            "2. **Start with 2 rakats** on school holidays or weekends.\n"
            "3. **Build toward 4 rakats** as a consistent habit.\n"
            "4. **Learn the benefit**: equivalent to giving sadaqah on behalf of every joint in the body.\n"
            "5. **Set an alarm** labelled 'Duha time' for weekends until it becomes habitual."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Every day a sadaqah is due on every joint of the body of each of you. "
            "Two rakats of Duha prayer is sufficient for all of that'* (Sahih Muslim 720). "
            "Aisha said: *'The Messenger of Allah used to pray Duha four rakats and would sometimes "
            "pray more'* (Sahih Muslim 719). At 14, young people have enough routine control "
            "to add a voluntary act — Duha on weekends is an accessible, high-reward starting point."
        ),
    },
    {
        "slug": "islam-sahabi-biography-age14",
        "title": "Study the Biography of One Sahabah in Depth",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose one Sahabah** (suggest: Bilal ibn Rabah, Mus'ab ibn Umayr, "
            "Khadijah bint Khuwaylid, Abu Dharr Al-Ghifari, or Salman Al-Farisi).\n"
            "2. **Read a dedicated biography** (many short books available for young readers).\n"
            "3. **Extract 5 character lessons** — list them.\n"
            "4. **Discuss**: how does their story relate to challenges you face today?\n"
            "5. **Share** what you learnt — explain it to a sibling or write 3 paragraphs."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'My companions are like stars — whichever of them you follow, "
            "you will be guided'* (Al-Bazzar, authenticated by many scholars). The Sahaba's lives "
            "demonstrate every virtue — courage, sacrifice, loyalty, learning, activism — in historical "
            "detail. At 14, young people need narrative role models who are both inspiring and imperfect "
            "humans. Mus'ab ibn Umayr is particularly relatable — young, wealthy, who gave it all up."
        ),
    },
    {
        "slug": "islam-hajj-knowledge-age14",
        "title": "Learn the Full Rites of Hajj and Its Spiritual Meaning",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the rites in sequence**: ihram and talbiyah → Tawaf Al-Qudum → Sa'i → "
            "stay in Mina → standing at Arafah → Muzdalifah → stoning of the jamarat → "
            "slaughter → shaving → Tawaf Al-Ifadah → farewell tawaf.\n"
            "2. **Learn the story behind each rite** (Ibrahim ﷺ, Hajar, and Ismail ﷺ).\n"
            "3. **Memorise the key dua of Arafah**: *'The best dua is the dua on the Day of Arafah'* "
            "(Tirmidhi 3585).\n"
            "4. **Understand Hajj as a journey of the soul** — beyond the physical steps."
        ),
        "parent_note_md": (
            "Hajj is the fifth pillar of Islam, obligatory once in a lifetime for those who are able. "
            "Allah says: *'And proclaim the Hajj to people — they will come to you on foot and on every "
            "lean camel, from every distant mountain path'* (Quran 22:27). Learning the rites at 14 "
            "prepares children for their first Hajj (which many families aim for when children reach "
            "adulthood) and deepens their connection to the story of Ibrahim ﷺ — the foundation of Islamic monotheism."
        ),
    },
    {
        "slug": "islam-modest-dress-age14",
        "title": "Understand and Practise Islamic Modesty in Dress",
        "category": "social",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the basic awrah rules** for your sex (discuss with same-sex parent or trusted adult).\n"
            "2. **For boys**: the awrah is from navel to knee; general guideline is loose, modest clothing.\n"
            "3. **For girls**: covering all except face and hands in front of non-mahram men is the "
            "scholarly consensus for when outside or in public.\n"
            "4. **Discuss modesty as a value** — not just a rule. It reflects self-respect, "
            "dignity, and God-consciousness.\n"
            "5. **Audit the wardrobe**: which items align with Islamic modesty? Make gradual adjustments."
        ),
        "parent_note_md": (
            "Allah says: *'O Prophet, tell your wives and daughters and the women of the believers "
            "to draw their outer garments close around them'* (Quran 33:59). The Quran addresses men "
            "first: *'Tell the believing men to lower their gaze and guard their private parts'* "
            "(Quran 24:30). Modesty is for both sexes. At 14, adolescents are forming their identity "
            "and wardrobe choices. Framing modesty positively — as dignity and God-consciousness "
            "rather than shame — makes it sustainable."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 15
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-tahajjud-habit-age15",
        "title": "Establish a Regular Tahajjud (Night Prayer) Habit",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the time**: Tahajjud (Qiyam Al-Layl) is prayed in the last third of the night, "
            "after waking from sleep. Minimum 2 rakats.\n"
            "2. **Start small**: set an alarm 20 minutes before Fajr adhan on weekends. Pray 2 rakats.\n"
            "3. **Make long dua** after the prayer — this is the most special time for personal conversation "
            "with Allah.\n"
            "4. **Learn Surah Al-Muzammil** (chapter 73) — revealed specifically about the night prayer.\n"
            "5. **Build to 8 rakats** over several months. Witr should conclude the night prayer."
        ),
        "parent_note_md": (
            "Allah says: *'And from part of the night, pray with it as additional worship for you; "
            "it may be that your Lord will raise you to a praised station'* (Quran 17:79). "
            "The Prophet ﷺ said: *'The best prayer after the obligatory prayers is the night prayer'* "
            "(Sahih Muslim 1163). He also said Allah descends to the lowest heaven in the last third of "
            "the night and calls: *'Who is supplicating that I may respond?'* (Sahih Bukhari 1145). "
            "At 15, teenagers have the capacity to build this habit independently — it transforms faith "
            "from inherited to personally chosen."
        ),
    },
    {
        "slug": "islam-amr-bil-maruf-age15",
        "title": "Learn How to Encourage Good and Discourage Wrong (Wisely)",
        "category": "social",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the obligation and its levels**: *'Whoever sees a wrong, let him change it "
            "with his hand; if he cannot, then with his tongue; if he cannot, then with his heart — "
            "and that is the weakest of faith'* (Sahih Muslim 49).\n"
            "2. **Apply the wisdom rules**: amr bil ma'ruf must be done with knowledge "
            "(is it truly wrong?), with gentleness, and without causing greater harm.\n"
            "3. **Start with yourself** — the scholars said one cannot enjoin others before enjoining "
            "themselves.\n"
            "4. **Practise with family**: gently mention when something haram is happening at home, "
            "with respect and love, not lecturing."
        ),
        "parent_note_md": (
            "The Hadith of changing wrong with the hand/tongue/heart is in Sahih Muslim (49) — "
            "it is a foundational civic-religious obligation. The Prophet ﷺ also said: "
            "*'The people who know good but do not practice it, and forbid evil but do not abandon it — "
            "beware of them'* (Shu'ab Al-Iman). At 15, teenagers begin to have opinions and influence "
            "over peers — teaching them to use that influence correctly is essential before they enter "
            "the social pressure of late adolescence."
        ),
    },
    {
        "slug": "islam-shirk-awareness-age15",
        "title": "Understand the Major and Minor Forms of Shirk to Avoid Them",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define major shirk**: directing any act of worship — dua, sacrifice, tawaf — "
            "to other than Allah. This nullifies iman.\n"
            "2. **Define minor shirk**: the most feared is riya (showing off in worship). "
            "The Prophet ﷺ called it the hidden shirk.\n"
            "3. **Self-audit**: Do you pray to be seen? Do you dress modestly only in front of others? "
            "Do you give charity so people think well of you?\n"
            "4. **Learn the dua against riya**: *Allahumma inni a'udhu bika an ushrika bika shay'an "
            "a'lamuhu, wa astaghfiruka lima la a'lam* (O Allah, I seek refuge in You from knowingly "
            "associating anything with You, and I ask forgiveness for what I do not know).\n"
            "5. **Discuss the Quran verse**: Allah will not forgive shirk but may forgive anything below it."
        ),
        "parent_note_md": (
            "Allah says: *'Indeed, Allah does not forgive association with Him, but He forgives what is "
            "less than that for whom He wills'* (Quran 4:48). The Prophet ﷺ said: "
            "*'The thing I fear most for you is the minor shirk — riya (showing off)'* (Ahmad 23630, "
            "authenticated). At 15, adolescents are highly susceptible to peer performance and "
            "social media validation — teaching the concept of riya at this exact stage is "
            "psychologically timed correctly."
        ),
    },
    {
        "slug": "islam-good-friends-age15",
        "title": "Choose Friends Based on Islamic Criteria",
        "category": "social",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the hadith on companionship**: 'A person is on the religion of his friend, "
            "so look carefully at who you befriend.'\n"
            "2. **Identify the qualities of a good friend in Islam**: reminds you of Allah, "
            "is honest with you even when uncomfortable, does not pull you toward haram, "
            "is present when you are in difficulty.\n"
            "3. **Evaluate current friendships** honestly: do they make you better or worse?\n"
            "4. **Do not abandon current friends abruptly** — but consciously invest more in those "
            "who strengthen your deen.\n"
            "5. **Seek friendship in Islamic spaces**: masjid, halaqas, Islamic youth groups."
        ),
        "parent_note_md": (
            "The companionship hadith is in Abu Dawud (4833) and Tirmidhi (2378), authenticated. "
            "The Prophet ﷺ gave the blacksmith analogy: *'The example of a good and bad companion "
            "is like a carrier of musk and a blacksmith's bellows — the musk carrier may give you "
            "some, or you may buy from him, or you at least enjoy the scent. The bellows will either "
            "burn your clothes or you will get a foul smell'* (Sahih Bukhari 5534, Muslim 2628). "
            "Peer influence peaks at 15 — this task arrives at exactly the right time."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 16
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "islam-zakat-calculation-age16",
        "title": "Learn How to Calculate Zakat on Savings",
        "category": "financial",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the nisab**: the minimum threshold — the gold nisab is 85 grams of gold "
            "(check current price). If your savings exceed this value for a full lunar year, "
            "zakat is due.\n"
            "2. **Calculate 2.5%**: e.g., if savings = £5,000 and nisab is met, "
            "zakat = £5,000 × 0.025 = £125.\n"
            "3. **Learn which assets are zakatable**: cash, gold and silver, trade goods, investments.\n"
            "4. **Practise on a hypothetical amount**: if you have £500, do you owe zakat? "
            "(Compare to nisab, check if held for a year, then calculate.)\n"
            "5. **Discuss who receives zakat** — the eight categories in Quran 9:60."
        ),
        "parent_note_md": (
            "Zakat is the third pillar of Islam. Allah says: *'Take from their wealth a charity "
            "by which you purify them'* (Quran 9:103). The calculation methodology (nisab based "
            "on 85g gold, 2.5% of zakatable wealth held for one year) is the dominant scholarly "
            "view (Hanafi, Maliki, Shafi'i, Hanbali with minor variations). At 16, young people "
            "may have savings from part-time work or gifts — teaching them to calculate their own "
            "zakat prepares them to fulfil this pillar as adults."
        ),
    },
    {
        "slug": "islam-teach-others-age16",
        "title": "Teach One Islamic Concept to Someone Else This Month",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose one topic** you have already learnt: a dua, a concept of aqeedah, "
            "a seerah story, a fiqh ruling, a Quran tafsir.\n"
            "2. **Prepare briefly**: know the daleel (evidence), the key points, and one example.\n"
            "3. **Teach it** — to a younger sibling, a friend, in an Islamic youth group, or by "
            "writing a social media post with proper references.\n"
            "4. **Reflect**: what questions were asked? What did you not know? Look up the answers.\n"
            "5. **Repeat monthly** — teaching is the deepest form of learning."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Convey from me even if it is one verse'* (Sahih Bukhari 3461). "
            "He also said: *'The best of you are those who learn the Quran and teach it'* "
            "(Sahih Bukhari 5027). Teaching reinforces learning and creates a chain — "
            "the teacher is rewarded for the good deeds of everyone they have guided. "
            "At 16, young people have the vocabulary and confidence to teach — "
            "this task activates them as agents of da'wah, not just passive recipients."
        ),
    },
    {
        "slug": "islam-seerah-complete-age16",
        "title": "Complete a Full Reading of the Prophet's ﷺ Life (Seerah)",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a complete seerah book** appropriate for teenagers: "
            "'When the Moon Split' by Safiur Rahman Mubarakpuri, or 'The Sealed Nectar', "
            "or 'Muhammad: His Life Based on the Earliest Sources' by Martin Lings.\n"
            "2. **Set a reading schedule**: 20–30 pages per week to complete in 2–3 months.\n"
            "3. **Note 10 character lessons** from the Prophet's ﷺ life as you read.\n"
            "4. **Discuss with a parent or study group** — at least 3 sessions of 30 minutes each.\n"
            "5. **Finish with salawat**: *Allahumma salli 'ala Muhammad wa 'ala ali Muhammad...*"
        ),
        "parent_note_md": (
            "The Prophet ﷺ is described as *'an excellent example for whoever hopes in Allah and "
            "the Last Day'* (Quran 33:21). Allah says: *'And We have not sent you except as a mercy "
            "to the worlds'* (Quran 21:107). A complete seerah reading at 16 — not a children's "
            "summary but a full account — connects a young Muslim's maturing intellect to the "
            "complete human story of their Prophet ﷺ. This single reading often transforms faith "
            "from childhood inheritance to adult conviction."
        ),
    },
    {
        "slug": "islam-personal-dua-habit-age16",
        "title": "Develop a Personal Dua List and Review It Weekly",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Create a personal dua list** with categories: deen (faith), dunya "
            "(this life — study, health, relationships), akhira (forgiveness, Paradise, protection from Hell), "
            "family, community, and the ummah.\n"
            "2. **Write at least 5 duas in each category** — be specific. Not just 'good marks' but "
            "'O Allah, grant me the ability to understand and retain what I study.'\n"
            "3. **Pray these duas** during sujud (prostration), after salah, and in the last hour of Jumu'ah.\n"
            "4. **Review the list weekly**: note which have been answered (write it down as a reminder of "
            "Allah's mercy); update the list as life changes.\n"
            "5. **Understand**: dua is not asking and forgetting — it is an ongoing conversation with Allah."
        ),
        "parent_note_md": (
            "The Prophet ﷺ said: *'Dua is worship'* (Abu Dawud 1479, Tirmidhi 2969). Allah says: "
            "*'Call upon Me; I will respond to you'* (Quran 40:60). He also says: "
            "*'And when My servants ask you concerning Me — indeed I am near. I respond to the "
            "invocation of the supplicant when he calls upon Me'* (Quran 2:186). "
            "At 16, a young person stands at the threshold of adult life — deen, studies, future, "
            "relationships. Building a structured dua practice now gives them a direct channel "
            "to Allah for every challenge ahead."
        ),
    },
]


class Command(BaseCommand):
    help = "Add 46 new Islamic tasks (ages 5–16), bringing total to ~85."

    def handle(self, *args, **options):
        all_envs = list(Environment.objects.all())
        if not all_envs:
            self.stdout.write(self.style.ERROR(
                "No Environment rows found. Run seed_demo first."
            ))
            return

        created_count = 0
        updated_count = 0

        for data in ISLAM_TASKS_2:
            cat_key = data["category"]
            tag_name, tag_cat = TAG_FOR_CATEGORY[cat_key]
            tag, _ = Tag.objects.get_or_create(
                name=tag_name,
                defaults={"category": tag_cat},
            )

            task, created = Task.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title":          data["title"],
                    "how_to_md":      data.get("how_to_md", ""),
                    "parent_note_md": data.get("parent_note_md", ""),
                    "safety_md":      data.get("safety_md", ""),
                    "min_age":        data["min_age"],
                    "max_age":        data["max_age"],
                    "sex_filter":     "any",
                    "religion":       "islam",
                    "status":         ReviewStatus.APPROVED,
                },
            )
            task.environments.set(all_envs)
            task.tags.set([tag])
            task.save()

            if created:
                created_count += 1
                self.stdout.write(f"  CREATED  {data['slug']}")
            else:
                updated_count += 1
                self.stdout.write(f"  UPDATED  {data['slug']}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone — {created_count} created, {updated_count} updated."
        ))
