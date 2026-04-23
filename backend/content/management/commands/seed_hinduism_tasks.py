"""Management command: seed Hinduism tasks for ages 5–16 (religion='hinduism').

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_hinduism_tasks

Broadly pan-Hindu — practical tasks any practicing Hindu family would recognise
regardless of tradition (Vaishnava, Shaiva, Shakta, Smarta). Each task includes
Sanskrit shloka in Devanagari + IAST transliteration + English meaning where
applicable. Grounded in Bhagavad Gita, Upanishads, Ramayana, and core Hindu practice.

Idempotent via update_or_create(slug=...).
"""
from django.core.management.base import BaseCommand

from content.models import Environment, ReviewStatus, Tag, Task


TAG_FOR_CATEGORY = {
    "cognitive": ("Reasoning",     Tag.Category.COGNITIVE),
    "social":    ("Social skills", Tag.Category.SOCIAL),
    "household": ("Home care",     Tag.Category.HOUSEHOLD),
    "financial": ("Money basics",  Tag.Category.FINANCIAL),
    "digital":   ("Digital life",  Tag.Category.DIGITAL),
    "navigation":("Finding the way", Tag.Category.NAVIGATION),
}

HINDUISM_TASKS = [
    # ══════════════════════════════════════════════════════════════════════
    # AGE 5
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-namaste-meaning",
        "title": "Namaste — Greet Others with Divine Awareness",
        "category": "social",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the gesture**: press both palms together at the heart (Anjali mudra), "
            "bow the head slightly, and say *Namaste* or *Namaskar*.\n"
            "2. **Explain the meaning**: *Namaste* comes from Sanskrit — *namas* (I bow) + *te* (to you). "
            "The full phrase is: **नमस्ते — Namaste** — 'The divine in me bows to the divine in you.'\n"
            "3. **Practise greeting** every family member this way at the start of each day.\n"
            "4. **Use it at the mandir** when greeting the deity and the pandit.\n"
            "5. **Ask the child**: 'If God lives in everyone, how should we treat everyone?' "
            "Discuss unkindness, exclusion, and respect."
        ),
        "parent_note_md": (
            "The Bhagavad Gita teaches: *'The humble sages, by virtue of true knowledge, see with "
            "equal vision a learned Brahmin, a cow, an elephant, a dog and a dog-eater'* (BG 5:18). "
            "Namaste is the physical expression of this equality — it reminds children that every "
            "person carries a spark of the divine (Atman). Teaching this greeting early plants the "
            "root of ahimsa, respect, and non-judgement that Hindu ethics is built on."
        ),
    },
    {
        "slug": "hindu-om-sound",
        "title": "OM — Chant the Sacred Sound of Creation Daily",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the symbol**: write **ॐ** (Om) and explain it is the most sacred symbol "
            "in Hinduism — representing Brahman, the source of all existence.\n"
            "2. **Teach the three sounds**: A (creation) — U (preservation) — M (dissolution). "
            "The silence after is the fourth state, Turiya.\n"
            "3. **Chant together**: sit still, close eyes, take a deep breath, and chant *'Oooooom'* "
            "slowly three times, feeling the vibration in the chest.\n"
            "4. **Do it every morning** before puja and every night before sleep — even 3 chants "
            "takes only 30 seconds.\n"
            "5. **Practice drawing ॐ** — let the child trace and colour it as an art activity."
        ),
        "parent_note_md": (
            "The Mandukya Upanishad (verse 1) teaches: *'Om — this syllable is all this. "
            "All that is past, present and future — all of it is Om. And whatever else there is "
            "beyond the three times, that too is Om.'* The Chandogya Upanishad calls OM the "
            "*udgitha* — the highest song. Children who start their day with Om develop a habit "
            "of stillness, focus, and connection to something greater than themselves — a foundation "
            "for all future prayer and meditation practice."
        ),
    },
    {
        "slug": "hindu-brahmarpanam-shloka",
        "title": "Brahmarpanam — Shloka of Grace Before Meals",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the shloka** together (from Bhagavad Gita 4:24):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > ब्रह्मार्पणं ब्रह्म हविः ब्रह्माग्नौ ब्रह्मणा हुतम् ।\n"
            "   > ब्रह्मैव तेन गन्तव्यं ब्रह्मकर्मसमाधिना ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Brahmārpaṇaṃ brahma haviḥ brahmāgnau brahmaṇā hutam |*\n"
            "   > *Brahmaiva tena gantavyaṃ brahmakarmasamādhinā ||*\n\n"
            "   **Meaning:** 'The act of offering is Brahman, the offering itself is Brahman, "
            "   offered by Brahman into the fire of Brahman — whoever sees Brahman in all action "
            "   reaches Brahman.'\n\n"
            "2. **Say it before every meal**, hands joined, eyes closed.\n"
            "3. **Explain in simple terms**: 'We are thanking God for the food and saying "
            "   everything comes from God and returns to God.'\n"
            "4. **Make it a non-negotiable family habit** — no meal begins without it."
        ),
        "parent_note_md": (
            "This shloka is from the Bhagavad Gita 4:24, where Krishna teaches Arjuna about "
            "Brahma Yajna — the sacrifice of all action to the divine. Saying it before meals "
            "transforms eating from a physical act into an act of worship (yajna). The Taittiriya "
            "Upanishad (3.2) declares: *'Annam Brahma'* — food is Brahman. Children who grow up "
            "pausing to acknowledge God before eating develop gratitude, mindfulness, and the "
            "understanding that all of life is sacred."
        ),
    },
    {
        "slug": "hindu-light-diya",
        "title": "Light the Diya — Daily Home Ritual of Light",
        "category": "household",
        "min_age": 5, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up a small altar space** — even a shelf with a deity image, a diya "
            "(clay lamp), and a small flower works.\n"
            "2. **Teach the child to fill the diya** with ghee or sesame oil and place the "
            "cotton wick correctly.\n"
            "3. **Light it at sunrise and/or sunset** — the two sandhya (twilight) times are "
            "traditionally auspicious.\n"
            "4. **Explain the symbolism**: the flame represents Agni (the divine fire), "
            "knowledge dispelling darkness, and the Atman (inner light) within us.\n"
            "5. **Say a simple prayer** while the diya is lit: *'O God, let your light "
            "illuminate my mind and heart today.'*\n"
            "6. **Safety rule**: the child lights it with adult supervision until age 8."
        ),
        "parent_note_md": (
            "The diya is central to Hindu worship across all traditions. The Rig Veda (1.1.1) "
            "opens with *'Agnim Īḷe'* — 'I praise Agni' — the sacred fire that connects the "
            "human to the divine. Deepotsava (festival of lights) at Diwali is the grand "
            "expression of this daily practice. The daily diya teaches children that God is "
            "light, that worship is a daily act (not just for festivals), and that even small "
            "rituals done consistently build a profound inner life."
        ),
    },
    {
        "slug": "hindu-morning-hand-shloka",
        "title": "Karagre Vasate Lakshmi — Morning Hand Shloka on Waking",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The moment the child wakes**, before getting out of bed, teach them to look "
            "at their open palms and recite:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > कराग्रे वसते लक्ष्मीः करमध्ये सरस्वती ।\n"
            "   > करमूले तु गोविन्दः प्रभाते करदर्शनम् ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Karāgre vasate Lakṣmīḥ karamadhye Sarasvatī |*\n"
            "   > *Karamūle tu Govindaḥ prabhāte karadarśanam ||*\n\n"
            "   **Meaning:** 'At the fingertips dwells Lakshmi (prosperity); in the middle of "
            "   the palm dwells Saraswati (knowledge); at the base of the palm dwells Govinda "
            "   (God). I view my hands in the morning.'\n\n"
            "2. **Then touch the floor** before getting out of bed — asking forgiveness of "
            "   Bhumi Mata (Mother Earth) for stepping on her.\n"
            "3. **Practise until the child can say it from memory** within one week."
        ),
        "parent_note_md": (
            "This is one of Hinduism's most widely practised prabhata shlokas (morning verses). "
            "By looking at one's own hands and seeing the three great deities — Lakshmi, Saraswati, "
            "and Vishnu — the child is taught that the divine is not distant but present within "
            "them. Starting the day with this shloka creates a habit of beginning with God before "
            "screens, food, or noise. It also plants the seeds of understanding the Hindu trinity "
            "of deities and their domains: prosperity, knowledge, and divine protection."
        ),
    },
    {
        "slug": "hindu-ishwar-everywhere",
        "title": "God is Everywhere — Understanding Ishwar in All",
        "category": "cognitive",
        "min_age": 5, "max_age": 6,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Tell the story of young Prahlada** (from the Bhagavata Purana): "
            "Hiranyakashipu asked 'Where is your God?' and Prahlada said 'Everywhere — even "
            "in this pillar.' God appeared from the pillar as Narasimha to protect him.\n"
            "2. **Do a 'Where is God?' walk**: go around the home or garden and ask the child "
            "'Is God in this flower? In this water? In this cat?' Answer: yes, God is in "
            "everything as Brahman.\n"
            "3. **Teach the key idea**: Hinduism teaches that God (Brahman) is both the "
            "creator of the universe AND present within it — in every living thing.\n"
            "4. **Draw it**: draw a sun with rays spreading to a tree, an animal, a person, "
            "and the sky — Brahman is the sun, all things are rays.\n"
            "5. **Connect to Namaste**: 'That's why we bow to everyone — God is inside them too.'"
        ),
        "parent_note_md": (
            "The Bhagavad Gita (10:20) teaches: *'I am the Atman seated in the heart of all "
            "creatures. I am the beginning, the middle, and the end of all beings.'* This is "
            "the foundational concept of Hinduism — Brahman is both transcendent (Paramatman) "
            "and immanent (Atman in all). Children who understand this early treat nature, "
            "animals, and other people with reverence — because they see God in all. This is "
            "the experiential root of ahimsa and universal compassion."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 6
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-ganesh-mantra-new-task",
        "title": "Ganesh Mantra — Invoke Blessings Before Anything New",
        "category": "cognitive",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the Vakratunda Ganesha shloka**:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > वक्रतुण्ड महाकाय सूर्यकोटिसमप्रभ ।\n"
            "   > निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Vakratuṇḍa mahākāya sūryakoṭisamaprabha |*\n"
            "   > *Nirvighnaṃ kuru me deva sarvakāryeṣu sarvadā ||*\n\n"
            "   **Meaning:** 'O Ganesha of the curved trunk and large body, with the "
            "   radiance of a million suns — please remove all obstacles from my work, always.'\n\n"
            "2. **Say it before**: starting a school project, an exam, a journey, a new school "
            "   year, or any important task.\n"
            "3. **Explain Ganesha's role**: Vighnaharta (remover of obstacles) and Prathamapujya "
            "   (first to be worshipped before all deities).\n"
            "4. **Draw Ganesha together** — his elephant head, four arms, modak, and mouse "
            "   vehicle — and label what each symbolises."
        ),
        "parent_note_md": (
            "Ganesha is invoked first in all Hindu rituals because He removes obstacles (Vighna) "
            "and blesses beginnings. This is why Hindu weddings, new businesses, exam halls, "
            "and temple consecrations all begin with Ganesh puja. The Ganesha Purana and the "
            "Mudgala Purana both establish his primacy. Teaching children to pause and seek "
            "divine blessing before important tasks — rather than rushing in with ego — "
            "builds humility, focus, and the understanding that effort plus grace together "
            "lead to success."
        ),
    },
    {
        "slug": "hindu-bal-leela-krishna",
        "title": "Stories of Baby Krishna — Bal Leela",
        "category": "cognitive",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read or tell three key stories** from the Bhagavata Purana (Canto 10):\n"
            "   - **The butter thief**: Krishna stealing butter — the joy of God playing with "
            "     His devotees.\n"
            "   - **Putana's defeat**: baby Krishna protected by God — evil cannot touch the "
            "     devoted.\n"
            "   - **Lifting Govardhan**: Krishna protecting the village from Indra's rain — "
            "     God protects those who trust Him over blind tradition.\n"
            "2. **Ask questions after each story**: 'What did Krishna teach us here? What "
            "   would you have done?'\n"
            "3. **Act it out**: let the child play-act the butter-thief scene or the lifting "
            "   of Govardhan with toy blocks.\n"
            "4. **Connect to Janmashtami**: 'This is why we celebrate His birthday every year.'"
        ),
        "parent_note_md": (
            "The Bhagavata Purana (Srimad Bhagavatam, Canto 10) is the most beloved text of "
            "Vaishnavas and deeply resonant across all Hindu traditions. Krishna's childhood "
            "leelas (divine play) teach that God is not distant and fearsome but intimate, "
            "playful, and deeply loving — accessible to a child's heart. Stories are the most "
            "powerful vehicle for value formation at age 6–8. Each Bal Leela encodes a theological "
            "truth: God's omnipotence, His protection of devotees, and the superiority of bhakti "
            "over ritual alone."
        ),
    },
    {
        "slug": "hindu-temple-visit-etiquette",
        "title": "Visiting the Mandir — Etiquette, Reverence, and Meaning",
        "category": "social",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Before entering**: remove shoes, wash hands, and explain why — the mandir "
            "   is the home of God; we enter clean and humble.\n"
            "2. **At the entrance**: ring the bell (ghanta) and explain — the sound OM "
            "   resonates the space and announces our presence to God.\n"
            "3. **Before the deity**: do Anjali (palms joined), do a simple pranam (forehead "
            "   to floor), and stand quietly for 30 seconds with eyes closed.\n"
            "4. **Pradakshina (circumambulation)**: walk clockwise around the deity once — "
            "   God is at the centre of our lives.\n"
            "5. **Receive prasad** with both hands, showing respect.\n"
            "6. **Speak quietly and keep the phone away** — explain that this is God's home, "
            "   not a tourist attraction.\n"
            "7. **After the visit**: ask the child what they prayed for and what they felt."
        ),
        "parent_note_md": (
            "The mandir is a sacred space designed on Agama Shastra principles — its architecture, "
            "layout, and rituals are all designed to facilitate the meeting of the devotee with "
            "the divine. The Vishnu Purana teaches that darshan (seeing the deity) itself is an "
            "act of grace. Children who learn temple etiquette early develop reverence, the "
            "ability to be still, and a sense of the sacred — skills increasingly rare in the "
            "age of constant stimulation. Regular temple visits ground Hindu identity across generations."
        ),
    },
    {
        "slug": "hindu-bedtime-prayer",
        "title": "Bedtime Shloka — Karacharana Kritam Forgiveness Prayer",
        "category": "cognitive",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the shloka** together:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > कायेन वाचा मनसेन्द्रियैर्वा बुद्ध्यात्मना वा प्रकृतिस्वभावात् ।\n"
            "   > करोमि यद्यत् सकलं परस्मै नारायणायेति समर्पयामि ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Kāyena vācā manasendriyairvā buddhyātmanā vā prakṛtisvabhāvāt |*\n"
            "   > *Karomi yad yat sakalaṃ parasmai Nārāyaṇāyeti samarpayāmi ||*\n\n"
            "   **Meaning:** 'Whatever I have done today through body, speech, mind, senses, "
            "   intellect, or simply by my nature — I offer it all to Narayana (God).'\n\n"
            "2. **Say it every night** before sleep, with eyes closed and hands joined.\n"
            "3. **Explain the meaning**: at the end of the day we give all our actions — "
            "   good and bad — back to God. This is how we let go and rest.\n"
            "4. **Add a moment of reflection**: 'What is one good thing you did today? "
            "   One thing you could do better tomorrow?'"
        ),
        "parent_note_md": (
            "This closing shloka is widely used across Vaishnava and Smarta traditions as a "
            "daily surrender of all actions to God — the essence of Karma Yoga (BG 9:27: "
            "*'Whatever you do, eat, offer, give away — do it as an offering to Me'*). "
            "Ending the day with prayer and brief self-examination is a practice common to "
            "all great spiritual traditions. For children it builds accountability, gratitude, "
            "and the habit of ending each day with God — rather than with a screen."
        ),
    },
    {
        "slug": "hindu-diwali-story",
        "title": "Diwali — The Story, Meaning, and Celebration",
        "category": "social",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Tell the story**: on Diwali eve, read the return of Ram, Sita, and Lakshman "
            "   to Ayodhya from the Ramayana — the people lit thousands of diyas to welcome "
            "   them home. This is why we light lights.\n"
            "2. **Other stories to share**: Lakshmi's arrival (for prosperity), Naraka Chaturdashi "
            "   (Krishna's defeat of the demon Narakasura), King Bali and Vamana avatar.\n"
            "3. **Rituals to do together**: clean the house (invite Lakshmi in), light diyas "
            "   at every door and window, do Lakshmi-Ganesha puja as a family.\n"
            "4. **Make rangoli together** at the entrance — geometric patterns welcoming "
            "   divine energy.\n"
            "5. **Discuss the meaning**: Diwali = triumph of light over darkness, of knowledge "
            "   over ignorance, of dharma over adharma."
        ),
        "parent_note_md": (
            "Diwali is the most universally celebrated Hindu festival — observed across Vaishnava, "
            "Shaiva, and Shakta traditions, as well as by Jains and Sikhs in related forms. "
            "The Valmiki Ramayana (Yuddha Kanda) records Ram's triumphant return to Ayodhya. "
            "The Skanda Purana connects Diwali to Lakshmi's emergence from the cosmic ocean. "
            "Teaching the full story — not just the fireworks — ensures children understand that "
            "festivals are theology expressed as celebration, and that every light they place "
            "is an act of devotion."
        ),
    },
    {
        "slug": "hindu-ahimsa-basics",
        "title": "Ahimsa — Non-Violence in Daily Life with Others and Animals",
        "category": "social",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the word**: Ahimsa = a (non) + himsa (harm). It means not harming "
            "   any living being through thought, word, or action.\n"
            "2. **Discuss examples**: 'Have you ever hurt someone with words? That is himsa. "
            "   Have you ever stepped on an ant? That is himsa. Have you been unkind? That is himsa.'\n"
            "3. **The animal connection**: talk about why many Hindus are vegetarian — because "
            "   animals also have Atman (soul) and feel pain. Even non-vegetarian families can "
            "   practise ahimsa by treating animals with care and not wasting food.\n"
            "4. **Practise for one week**: the child tracks every time they almost said something "
            "   unkind — did they stop themselves?\n"
            "5. **Connect to Gandhi**: Mahatma Gandhi called ahimsa the greatest force in the "
            "   world — stronger than weapons."
        ),
        "parent_note_md": (
            "Ahimsa is the first Yama in Patanjali's Yoga Sutras (2:30) and the foundation "
            "of Hindu ethics. The Mahabharata states: *'Ahimsa paramo dharmaḥ'* — non-violence "
            "is the highest dharma. Mahatma Gandhi built India's independence movement on this "
            "single principle. For children, learning ahimsa early — starting with how they "
            "speak to siblings and treat insects — builds the moral foundation for empathy, "
            "compassion, and ethical action throughout their entire lives."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 7
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-gayatri-mantra",
        "title": "Gayatri Mantra — Memorise, Chant at Sunrise, Understand",
        "category": "cognitive",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the full mantra** (Rigveda 3.62.10):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > ॐ भूर्भुवः स्वः ।\n"
            "   > तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि ।\n"
            "   > धियो यो नः प्रचोदयात् ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Oṃ bhūr bhuvaḥ svaḥ |*\n"
            "   > *Tatsaviturvareṇyaṃ bhargo devasya dhīmahi |*\n"
            "   > *Dhiyo yo naḥ pracodayāt ||*\n\n"
            "   **Meaning:** 'Om — We meditate upon the divine light of the effulgent Sun "
            "   (Savitri/God). May that divine light illuminate and guide our intellect.'\n\n"
            "2. **Chant it 3, 11, or 21 times** at sunrise, facing east with eyes closed.\n"
            "3. **Memorise line by line** over two weeks: first line week 1, second week 2, "
            "   third week 3.\n"
            "4. **Explain the three worlds**: Bhur (earth), Bhuvah (sky), Svah (heaven) — "
            "   we chant it for the entire universe, not just ourselves."
        ),
        "parent_note_md": (
            "The Gayatri Mantra from Rigveda 3.62.10 is the most revered mantra in all of "
            "Hinduism — called the mother of all Vedas. Traditionally given during Upanayana "
            "(sacred thread ceremony), it is now widely chanted by all genders and ages. "
            "Swami Vivekananda said: 'If I were asked to give one mantra to a child, it would "
            "be the Gayatri.' Scientists have found the specific sound vibrations of this mantra "
            "to have measurable effects on concentration and calmness. A child who chants it "
            "daily from age 7 will carry this lifelong anchor through all of life's storms."
        ),
    },
    {
        "slug": "hindu-morning-puja",
        "title": "Morning Puja — Set Up and Perform Home Worship",
        "category": "household",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up the puja space**: clean altar cloth, deity images or murti, "
            "   diya, incense (agarbatti), flowers, small bell, water vessel, and prasad.\n"
            "2. **The five elements of puja (Panchopachara)**:\n"
            "   - Gandha (sandalwood paste or flower) — Earth\n"
            "   - Pushpa (flowers offered) — Water element\n"
            "   - Dhupa (incense) — Fire\n"
            "   - Dipa (lamp/diya) — Air\n"
            "   - Naivedya (food offering) — Ether/Space\n"
            "3. **Ring the bell** to begin — calling the divine to witness.\n"
            "4. **Offer each item** with both hands to the deity, saying 'Om Namah Shivaya' "
            "   or 'Om Namo Narayanaya' or the family's chosen mantra.\n"
            "5. **Close with Aarti** and prostration (Sashtanga pranam or simple pranam).\n"
            "6. **Duration**: 5–10 minutes daily is sufficient."
        ),
        "parent_note_md": (
            "Home puja (grha puja) is the daily sadhana that sustains Hindu family life between "
            "temple visits. The Agama Shastras describe puja as the devotee offering their five "
            "senses — through each of the five elements — back to God. This is the experiential "
            "equivalent of BG 9:27: *'Whatever you do, eat, offer, or give away — do it as an "
            "offering to Me.'* Children who learn puja procedure early understand that the home "
            "itself is a sacred space, and that every day begins with God before it begins with "
            "the world."
        ),
    },
    {
        "slug": "hindu-aarti-practice",
        "title": "Aarti — How to Perform and Understand Its Meaning",
        "category": "household",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the circular motion**: hold the aarti thali (plate with lit diya) "
            "   in both hands and rotate it clockwise in circles before the deity — 7 "
            "   circles at the feet, 4 at the navel, 2 at the face, 7 around the whole form.\n"
            "2. **Ring the bell** with one hand while rotating with the other.\n"
            "3. **Sing an aarti**: begin with *'Om Jai Jagdish Hare'* — the most universal "
            "   Hindi aarti, sung in every tradition. Memorise the first two verses.\n"
            "4. **Explain the meaning of aarti**: we offer light (knowledge, the Atman's "
            "   nature) back to the source of all light — God.\n"
            "5. **After aarti**: receive the flame by cupping palms over the diya and "
            "   bringing hands to closed eyes — receiving blessings.\n"
            "6. **Perform it at every festival** and at the close of every family puja."
        ),
        "parent_note_md": (
            "Aarti is derived from the Sanskrit *Arati* — waving of light. It is the most "
            "universally practised act of Hindu worship, performed in every tradition from "
            "Kashmir to Kanyakumari. The act of circling light before the deity represents "
            "our offering of everything — intellect (light), ego (the circular motion of "
            "surrender), and devotion. The Skanda Purana states that those who perform aarti "
            "with devotion accumulate great merit. Teaching children to perform aarti rather "
            "than merely watch builds active participation in worship, embodying devotion "
            "rather than just observing it."
        ),
    },
    {
        "slug": "hindu-satya-truthfulness",
        "title": "Satya — Truthfulness as a Daily Practice",
        "category": "social",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Tell the story of Harishchandra** — the king who gave up his kingdom, "
            "   his wife, and everything he owned rather than speak a single untruth. "
            "   God rewarded his truthfulness in the end.\n"
            "2. **Explain Satya**: one of the five Yamas of Patanjali's Yoga Sutras (2:36). "
            "   Mahatma Gandhi called truth (Satya) his God — *'Satya is Ishvar'*.\n"
            "3. **Discuss the difference**: white lies, full lies, half-truths, and silence "
            "   when you should speak. Which are himsa? All of them.\n"
            "4. **The week's challenge**: the child commits to one week without any lie, "
            "   even small ones. If they slip, they note it honestly.\n"
            "5. **The mantra**: *'Satyam vada, dharmam chara'* — 'Speak truth, walk the "
            "   righteous path' (Taittiriya Upanishad 1.11.1)."
        ),
        "parent_note_md": (
            "The Taittiriya Upanishad (1.11.1) opens its instruction to graduating students "
            "with: *'Satyam vada, dharmam chara'* — speak truth, walk dharma. The Mahabharata "
            "states: *'There is no higher dharma than truth, no greater sin than falsehood.'* "
            "The Yoga Sutras (2:36) teach that when a person is firmly established in truth, "
            "all their words become effective — the universe aligns with the truth-teller. "
            "Children who internalise Satya as a non-negotiable value — not just a rule — "
            "build the character foundation for everything else in their spiritual life."
        ),
    },
    {
        "slug": "hindu-ramayana-stories",
        "title": "Ramayana — Key Episodes and Lessons for Life",
        "category": "cognitive",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read or tell five key episodes** over five weeks:\n"
            "   - Ram's exile: obeying parents even at great personal cost (Ayodhya Kanda)\n"
            "   - Hanuman's devotion: complete selfless service to God (Sundara Kanda)\n"
            "   - Sita's abduction and patience: staying righteous even in suffering\n"
            "   - Lanka war: good eventually defeats evil through courage and dharma\n"
            "   - Ram's return to Ayodhya: Diwali — every ending is a new beginning\n"
            "2. **After each episode**: 'What did Ram/Sita/Hanuman choose? What would you "
            "   choose? What does this teach us?'\n"
            "3. **Use a children's illustrated Ramayana** for ages 7–9 — Amar Chitra Katha "
            "   comics work excellently.\n"
            "4. **Watch a family-friendly Ramayana** (Doordarshan 1987 version remains the most "
            "   complete) alongside the reading."
        ),
        "parent_note_md": (
            "Valmiki's Ramayana — one of the two great Itihasas — is not merely mythology "
            "but a mahakavya (great epic) encoding the ideals of Hindu civilisation: Ram as the "
            "ideal king (maryada purushottama), Sita as steadfast virtue, Hanuman as perfect "
            "devotion, and Lakshman as fraternal loyalty. The Adhyatma Ramayana and Tulsidas's "
            "Ramcharitmanas extend its reach across every Hindu tradition. Children who grow "
            "up knowing the Ramayana have a ready vocabulary for every moral dilemma they will "
            "face — these archetypes live in the Hindu psyche for life."
        ),
    },
    {
        "slug": "hindu-tulsi-plant-care",
        "title": "Tulsi Plant — Daily Care and Sacred Significance",
        "category": "household",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Plant a Tulsi (Holy Basil)** in a traditional tulsi vrindavan (elevated pot) "
            "   at the home entrance or courtyard.\n"
            "2. **Daily care**: water it every morning at sunrise, circumambulate it once "
            "   clockwise (pradakshina), light a diya beside it in the evening.\n"
            "3. **Teach why Tulsi is sacred**: she is considered an avatar of Lakshmi and "
            "   the most beloved plant of Vishnu. The Padma Purana says a home with Tulsi "
            "   is always protected.\n"
            "4. **Medicinal knowledge**: Tulsi leaves in hot water or tea help immunity and "
            "   colds — science confirms its anti-bacterial and anti-viral properties.\n"
            "5. **Never uproot Tulsi** — only gently pluck leaves that are offered for puja.\n"
            "6. **Tulsi Vivah** (in Kartik month): observe the festival of Tulsi's symbolic "
            "   marriage to Vishnu."
        ),
        "parent_note_md": (
            "The Padma Purana declares: *'Where there is Tulsi, there is no disease; where "
            "there is Tulsi, there is no poverty; where there is Tulsi, Vishnu is present.'* "
            "Tulsi (Ocimum tenuiflorum) is among the most studied medicinal plants in Ayurveda "
            "and modern pharmacology — anti-bacterial, anti-viral, adaptogenic. Teaching children "
            "to care for the Tulsi plant connects daily responsibility (watering, tending) with "
            "devotion, ecological consciousness, and the understanding that all of nature is "
            "sacred in the Hindu worldview."
        ),
    },
    {
        "slug": "hindu-seva-at-home",
        "title": "Seva at Home — Selfless Service Without Being Asked",
        "category": "social",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define Seva**: selfless service done with no expectation of reward, "
            "   as an offering to God. The Bhagavad Gita calls this Nishkama Karma "
            "   (action without attachment to results).\n"
            "2. **Choose 3 daily home sevas**: e.g., sweeping the entrance, washing one dish, "
            "   helping a younger sibling, fetching water for an elder, watering plants.\n"
            "3. **The rule**: do it before being asked. This is the key — seva is given "
            "   freely, not as a response to a command.\n"
            "4. **Teach the idea**: 'When you serve your parents and family, you are serving "
            "   God — because God lives in them.' (BG 5:18)\n"
            "5. **Track it**: at night, the child tells one act of seva they did that day. "
            "   Parents acknowledge it with 'Shubham karoti' — 'You have done a good deed.'"
        ),
        "parent_note_md": (
            "The Bhagavad Gita (3:19) teaches: *'Therefore always perform the duty that "
            "should be done without attachment — for by performing action without attachment "
            "one reaches the Supreme.'* Seva is the direct practical expression of this — "
            "action as worship. Swami Vivekananda's famous call was *'Daridra Narayana seva'* "
            "— serve the poor as God. Starting at home, with family, teaches children that "
            "every act of genuine help is a spiritual act. Children who practise seva become "
            "adults who contribute to family, community, and society without keeping score."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 8
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-harvest-festival",
        "title": "Makar Sankranti / Pongal / Onam — Harvest Festival Gratitude",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Know your regional festival**: Makar Sankranti (North/West India, 14 Jan), "
            "   Pongal (Tamil Nadu, 4 days), Onam (Kerala, 10 days in August). All are harvest "
            "   festivals — thanking God and nature for the year's food.\n"
            "2. **For Makar Sankranti**: make til-gur (sesame-jaggery sweets), fly kites, "
            "   take a sunrise dip, and offer sesame-water to the Sun (Surya).\n"
            "3. **For Pongal**: boil rice with milk and jaggery in a new pot, let it overflow "
            "   (abundance overflows!), decorate with kolam and sugarcane.\n"
            "4. **Core meaning across all versions**: gratitude to Surya (the Sun), to farmers, "
            "   to the earth, and to the community — Loka Sangraha (collective wellbeing).\n"
            "5. **Do one act of daan (giving)** on this day: donate food, sweets, or clothing "
            "   to someone in need."
        ),
        "parent_note_md": (
            "India's harvest festivals mark the Sun's transition into Makara (Capricorn) — "
            "the astronomical event called Uttarayana, when the days lengthen again. The "
            "Mahabharata (Bhishma Parva) records that Bhishma chose this auspicious Uttarayana "
            "period to leave his body. The Surya (Sun) connection teaches children that Hindu "
            "festivals are not merely cultural customs but are rooted in astronomy, ecology, "
            "and gratitude to natural forces. Celebrating with daan (giving) ensures the "
            "festival also nourishes compassion, not just festivity."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 8 (continued)
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-prahlada-story",
        "title": "Story of Prahlada — Devotion That Cannot Be Broken",
        "category": "cognitive",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Tell the full story** from the Bhagavata Purana (Canto 7):\n"
            "   - Prahlada's father Hiranyakashipu hated Vishnu and demanded to be "
            "     worshipped as God. Prahlada, his own son, refused — he worshipped "
            "     only Vishnu.\n"
            "   - Hiranyakashipu tried every punishment: poison, fire, trampling by "
            "     elephants, throwing from cliffs. Vishnu protected Prahlada every time.\n"
            "   - Finally, from a stone pillar, Narasimha (man-lion avatar) emerged "
            "     and destroyed the demon — not inside, not outside; not by day, not "
            "     by night; not by human nor animal.\n"
            "2. **Ask the child**: 'Prahlada's own father was against him. He still "
            "   chose God. What does that tell us about inner conviction?'\n"
            "3. **Key teaching**: God protects the devoted. No power — not even a "
            "   parent, a bully, or a crowd — can overcome true bhakti.\n"
            "4. **Connect to peer pressure**: 'If everyone around you does something "
            "   wrong, does that make it right? What would Prahlada do?'"
        ),
        "parent_note_md": (
            "The Prahlada narrative in Bhagavata Purana (Canto 7, Chapters 5–10) is "
            "one of Hinduism's most beloved devotional stories. Philosophically, it "
            "affirms that Brahman (God as Vishnu/Narayana) is truly omnipresent — "
            "'Is your God in this pillar?' asked Hiranyakashipu. 'Yes,' said Prahlada. "
            "And God appeared. This story speaks directly to children facing situations "
            "where doing the right thing makes them unpopular. It also introduces "
            "the concept of Narasimha — the fourth avatar of Vishnu — and the idea "
            "that God takes forms specifically suited to each challenge."
        ),
    },
    {
        "slug": "hindu-saraswati-vandana",
        "title": "Saraswati Vandana — Dedicate All Learning to the Goddess",
        "category": "cognitive",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the Saraswati Vandana shloka**:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > या कुन्देन्दुतुषारहारधवला या शुभ्रवस्त्रावृता ।\n"
            "   > या वीणावरदण्डमण्डितकरा या श्वेतपद्मासना ।\n"
            "   > या ब्रह्माच्युतशङ्करप्रभृतिभिर्देवैः सदा वन्दिता ।\n"
            "   > सा मां पातु सरस्वती भगवती निःशेषजाड्यापहा ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Yā kundendutusārahāradhavalā yā śubhravstrāvṛtā |*\n"
            "   > *Yā vīṇāvaradaṇḍamaṇḍitakarā yā śvetapadmāsanā |*\n"
            "   > *Yā brahmācyutaśaṅkaraprabhṛtibhirdevaiḥ sadā vanditā |*\n"
            "   > *Sā māṃ pātu Sarasvatī Bhagavatī niḥśeṣajāḍyāpahā ||*\n\n"
            "   **Meaning:** 'She who is white as jasmine, the moon, and snow — "
            "   holding the veena — seated on a white lotus — always worshipped by "
            "   Brahma, Vishnu, and Shiva — may that Goddess Saraswati protect me "
            "   and remove all my dullness.'\n\n"
            "2. **Say it before opening books** — at the start of study time.\n"
            "3. **On Saraswati Puja (Vasant Panchami)**: place books and pens before "
            "   the deity and do a formal puja.\n"
            "4. **Explain Saraswati**: goddess of knowledge, music, speech, and arts — "
            "   the one who makes learning possible."
        ),
        "parent_note_md": (
            "Saraswati is the presiding deity of Vidya (knowledge) in all its forms — "
            "including modern academics, music, and language. Her four arms hold a veena "
            "(arts), a book (knowledge), a rosary (meditation), and the gesture of blessing. "
            "Teaching children to invoke Saraswati before study transforms learning from "
            "a chore into a sacred act. The Rig Veda (6.61) praises Saraswati as the "
            "river of inspiration. Students who develop this pre-study ritual also "
            "develop concentration and a growth mindset — believing that knowledge "
            "comes through effort plus divine grace."
        ),
    },
    {
        "slug": "hindu-holi-meaning",
        "title": "Holi — The Story, Colours, and Triumph of Devotion",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Tell the story of Holika and Prahlada** (the Holi legend):\n"
            "   Hiranyakashipu asked his sister Holika (immune to fire) to burn Prahlada. "
            "   She sat in a bonfire with Prahlada on her lap. Vishnu's grace protected "
            "   Prahlada — Holika burned instead. Evil destroyed itself.\n"
            "2. **Holika Dahan (night before Holi)**: watch or participate in the bonfire "
            "   ritual — symbolically burning away our own ego, anger, and negativity.\n"
            "3. **Holi of colours**: play with natural colours (gulal). Explain the "
            "   Braj tradition — Krishna played Holi with Radha and the gopis. "
            "   On this day all social barriers dissolve — rich/poor, old/young are equal.\n"
            "4. **Core message**: adharma (unrighteousness) destroys itself. Bhakti "
            "   (devotion) and innocence are indestructible.\n"
            "5. **Practical**: use only natural, skin-safe colours. Clean up properly "
            "   — respecting nature is also dharma."
        ),
        "parent_note_md": (
            "Holi has two layers: the theological (Holika's defeat, Prahlada's protection) "
            "and the devotional (Krishna's Vrindavan Holi with the gopis). The Bhagavata "
            "Purana and the Narada Purana both document these narratives. Spiritually, Holi "
            "represents the burning of vasanas (deep-rooted desires and ego — Holika) so "
            "that the pure devotional self (Prahlada) can emerge. Children who understand "
            "the theology behind the festival see it as a renewal ritual, not just a day "
            "of play — though the joyful play itself is a form of worship in the Holi tradition."
        ),
    },
    {
        "slug": "hindu-raksha-bandhan",
        "title": "Raksha Bandhan — The Sacred Bond of Sibling Protection",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The ceremony**: the sister ties a rakhi (sacred thread) on the brother's "
            "   wrist, does aarti, applies tilak, and offers mithai (sweets). The brother "
            "   gives a gift and pledges to protect her always.\n"
            "2. **Discuss the meaning**: raksha (protection) + bandhan (bond). This is not "
            "   just a physical thread — it is a promise. A bond of mutual care.\n"
            "3. **The mythological roots**: Draupadi tore her sari to bandage Krishna's "
            "   wounded finger — he called her 'sister' and later protected her in her "
            "   greatest hour of need (Mahabharata, Sabha Parva).\n"
            "4. **Extend the concept**: in many families, girls tie rakhi to any friend or "
            "   cousin they consider a protective brother-figure.\n"
            "5. **The lesson**: relationships carry duties (dharma). A brother's duty is "
            "   protection; a sister's duty is blessing. Both are sacred."
        ),
        "parent_note_md": (
            "Raksha Bandhan is observed across India and the Hindu diaspora on Shravana "
            "Purnima (full moon of Shravana month). The Bhagavata Purana records Goddess "
            "Lakshmi tying a rakhi to King Bali, making him her brother — and thereby "
            "securing Vishnu's freedom. The festival encodes one of Hinduism's core "
            "values: that relationships create obligations (dharma), and that care, "
            "protection, and mutual responsibility are sacred duties — not optional acts "
            "of sentiment. Teaching children to honour their siblings forms the foundation "
            "for honouring all relationships throughout life."
        ),
    },
    {
        "slug": "hindu-kids-yoga-asanas",
        "title": "Yoga Asanas for Children — Build a Daily Practice",
        "category": "cognitive",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with five foundational asanas** (10–15 minutes daily):\n"
            "   - **Tadasana** (Mountain Pose) — stillness, rootedness\n"
            "   - **Vrikshasana** (Tree Pose) — balance, focus, one-pointedness\n"
            "   - **Balasana** (Child's Pose) — surrender, rest, humility\n"
            "   - **Bhujangasana** (Cobra Pose) — strength, spine health\n"
            "   - **Shavasana** (Corpse Pose) — complete relaxation, stillness of mind\n"
            "2. **Link each asana to nature**: tree, mountain, child, cobra, corpse — "
            "   yoga honours all forms of life.\n"
            "3. **Add to Surya Namaskar** (age 10) once the basic asanas are stable.\n"
            "4. **Breath awareness**: in each asana, close eyes and notice the breath. "
            "   This is the first step toward pratyahara (withdrawal of senses).\n"
            "5. **Consistency over duration**: 10 minutes every day beats 1 hour once a week."
        ),
        "parent_note_md": (
            "Patanjali's Yoga Sutras (2:46) define asana as *'sthira sukham āsanam'* — "
            "'a posture that is steady and comfortable.' The purpose of asana in classical "
            "yoga is not fitness but preparation of the body and nervous system for "
            "meditation. Children who build a yoga practice early gain body awareness, "
            "emotional regulation, and concentration — skills that transfer directly to "
            "academic performance and social behaviour. The physical benefits (flexibility, "
            "strength, posture) are secondary to the inner training. The Ministry of AYUSH "
            "has documented measurable improvements in children's focus through school yoga."
        ),
    },
    {
        "slug": "hindu-caring-for-animals",
        "title": "Caring for Animals — Ahimsa Towards All Living Beings",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach that all beings have Atman**: not just humans but animals, birds, "
            "   insects — all carry the divine spark. This is why Hindu dharma "
            "   protects life at every level.\n"
            "2. **Daily acts of care**: place a small bowl of water for birds every "
            "   morning, sprinkle a few grains of rice for ants, offer leftover roti "
            "   to a cow or stray dog.\n"
            "3. **The cow connection**: explain why the cow is sacred — she gives milk "
            "   (life), labours without complaint, and never harms. She represents "
            "   the principle of selfless giving (Go Mata).\n"
            "4. **Discuss food choices**: many Hindus are vegetarian because of ahimsa. "
            "   Even for non-vegetarian families, discuss reducing waste and not "
            "   causing unnecessary suffering.\n"
            "5. **Spider / ant rule**: if you find an insect indoors, take it outside "
            "   rather than killing it — this is ahimsa in the smallest daily action."
        ),
        "parent_note_md": (
            "The Manusmriti and the Mahabharata both state: *'Ahimsa paramo dharmaḥ'* — "
            "non-violence is the highest dharma. Hinduism's reverence for life extends "
            "to every being with a soul (jiva) — the Jain concept of jiva-daya (compassion "
            "for all souls) deeply overlaps with Hindu ahimsa. Mahatma Gandhi wrote: "
            "'The greatness of a nation and its moral progress can be judged by the way "
            "its animals are treated.' Children who practise small daily acts of animal "
            "care develop empathy, responsibility, and the lived experience that all life "
            "is interconnected — the experiential basis of ecological and social compassion."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 9
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-hanuman-chalisa",
        "title": "Hanuman Chalisa — Memorise All 40 Verses",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Introduction**: the Hanuman Chalisa (40 verses in praise of Hanuman) "
            "   was composed by Tulsidas in Awadhi. It is the most widely recited Hindu "
            "   prayer after the Gayatri Mantra.\n"
            "2. **First two lines** (Doha 1) — learn first:\n\n"
            "   **Sanskrit/Awadhi (Devanagari):**\n"
            "   > श्रीगुरु चरन सरोज रज निज मनु मुकुरु सुधारि ।\n"
            "   > बरनउँ रघुबर बिमल जसु जो दायकु फल चारि ।।\n\n"
            "   **Transliteration:**\n"
            "   > *Śrīguru carana saroja raja nija manu mukuru sudhāri |*\n"
            "   > *Baranauṃ Raghubara bimala jasu jo dāyaku phala cāri ||*\n\n"
            "   **Meaning:** 'Cleansing the mirror of my heart with the dust of the "
            "   Guru's lotus feet, I narrate the pure glory of Rama, who bestows the "
            "   four fruits of life.'\n\n"
            "3. **Memorise 2 verses per week** — fully memorised in 20 weeks (one school term).\n"
            "4. **Chant daily**: ideally on Tuesday and Saturday (Hanuman's days), and "
            "   whenever facing difficulty or fear.\n"
            "5. **Explain Hanuman**: the ideal of bhakti, strength, humility, and service. "
            "   He is the bridge between Ram and the devotee."
        ),
        "parent_note_md": (
            "The Hanuman Chalisa, composed by Tulsidas in the 16th century, is one of the "
            "most memorised texts in the world. It extols Hanuman — the ideal devotee — "
            "as the embodiment of strength (bala), wisdom (buddhi), virtue (guna), and "
            "devotion (bhakti). The Ramcharitmanas (Sundara Kanda) shows Hanuman as the "
            "one who leaps across the ocean alone, carrying the flame of Ram's name within "
            "him. Children who memorise the Chalisa build both memory capacity and a "
            "powerful internal resource: when afraid, anxious, or tested, the instinct "
            "to recite it provides genuine psychological comfort rooted in spiritual identity."
        ),
    },
    {
        "slug": "hindu-navratri-durga",
        "title": "Navratri — Nine Nights of the Goddess, Meaning and Practice",
        "category": "social",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the nine forms of Devi**: Shailaputri, Brahmacharini, Chandraghanta, "
            "   Kushmanda, Skandamata, Katyayani, Kalaratri, Mahagauri, Siddhidatri. "
            "   Each represents a different power and virtue.\n"
            "2. **The story**: the demon Mahishasura could not be killed by any male "
            "   being. The Gods combined all their powers to create Durga — the mother "
            "   who destroyed evil. This is why she has ten arms — each holding a "
            "   weapon gifted by a different god.\n"
            "3. **Fasting**: observe partial fast (fruits and milk only) for at least "
            "   1–3 days of Navratri as an introduction to disciplined practice.\n"
            "4. **Garba/Dandiya** (Gujarat tradition): dance in circles around the Devi's "
            "   image — the circle represents the cycle of creation around the divine centre.\n"
            "5. **Ashtami/Navami**: participate in Kanya Puja — feeding nine young girls "
            "   as manifestations of the nine forms of Devi. This teaches that divinity "
            "   lives in the feminine, in every girl."
        ),
        "parent_note_md": (
            "Navratri (literally 'nine nights') is observed twice a year — Chaitra (spring) "
            "and Sharada (autumn). The Devi Mahatmya (Durga Saptashati), part of the Markandeya "
            "Purana, is the primary text — 700 verses describing Devi's victory over darkness. "
            "The Shakti tradition sees the divine not as masculine alone but as Shakti — "
            "the dynamic power that underlies all creation. Kanya Puja, where girls are "
            "worshipped as the Goddess, is among Hinduism's most powerful statements that "
            "the feminine is sacred. Children who participate in Navratri absorb this "
            "theology through experience — far more powerfully than through instruction."
        ),
    },
    {
        "slug": "hindu-dashavatar",
        "title": "Dashavatar — The Ten Avatars of Vishnu and Their Meaning",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn all ten avatars in order**:\n"
            "   1. Matsya (fish) — saved the Vedas from the great flood\n"
            "   2. Kurma (tortoise) — supported the cosmic churning (Samudra Manthan)\n"
            "   3. Varaha (boar) — rescued the earth from the cosmic ocean\n"
            "   4. Narasimha (man-lion) — protected Prahlada, destroyed Hiranyakashipu\n"
            "   5. Vamana (dwarf) — measured the three worlds in three steps\n"
            "   6. Parashurama — removed adharma from the warrior class\n"
            "   7. Rama — the ideal king; dharmic ruler\n"
            "   8. Krishna — the divine teacher; Bhagavad Gita\n"
            "   9. Buddha — compassion and non-violence\n"
            "   10. Kalki — the future avatar who will end the Kali Yuga\n"
            "2. **Connect to evolution**: many scholars note the avatars trace a pattern "
            "   from water creatures → amphibian → land animal → man-animal → human — "
            "   paralleling biological evolution. Discuss this.\n"
            "3. **Make a chart or drawing** of all ten avatars with their names.\n"
            "4. **Learn the Dashavatar shloka** if available in your family tradition."
        ),
        "parent_note_md": (
            "The doctrine of Avatar (divine descent) is articulated in the Bhagavad Gita "
            "(4:7–8): *'Whenever dharma declines and adharma rises, I manifest myself… "
            "to protect the good, to destroy evil, and to re-establish dharma — I am "
            "born age after age.'* The ten avatars are documented in the Srimad Bhagavatam "
            "(Canto 1, Chapter 3). The Dashavatar narrative teaches children that God is "
            "not passive — He intervenes in history. It also teaches adaptability: God "
            "takes different forms to meet different ages. B.G. Tilak and Sri Aurobindo "
            "both noted the evolutionary symbolism embedded in the avatar sequence."
        ),
    },
    {
        "slug": "hindu-mahabharata-stories",
        "title": "Mahabharata — Key Stories and Dharmic Dilemmas",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read or tell five key episodes** over five weeks:\n"
            "   - **Draupadi's vastraharan**: injustice happens when good people stay "
            "     silent. Surrendering to Krishna brought divine protection.\n"
            "   - **Arjuna's dilemma at Kurukshetra**: when duty (dharma) conflicts "
            "     with emotion — and why Krishna said 'fight.'\n"
            "   - **Karna's loyalty**: a good person on the wrong side — the tragedy "
            "     of misplaced loyalty.\n"
            "   - **Yudhishthira and the Yaksha**: wisdom in answering hard questions "
            "     is more powerful than strength.\n"
            "   - **Bhishma's death bed**: a great man's final teaching — non-violence, "
            "     dharma, and the nature of the self.\n"
            "2. **After each episode**: 'Who made the right choice? Who didn't? Why?'\n"
            "3. **Use an illustrated Mahabharata** for this age — Amar Chitra Katha "
            "   or Devdutt Pattanaik's children's versions."
        ),
        "parent_note_md": (
            "The Mahabharata is ten times the length of the Iliad and Odyssey combined — "
            "the longest poem ever written. It contains the Bhagavad Gita, the Vishnu "
            "Sahasranama, and the Shanti Parva (treatise on statecraft and ethics). "
            "Its central teaching is expressed in the Anushasana Parva: "
            "*'Do not do to others what you do not want done to yourself — this is the "
            "essence of dharma.'* Unlike morality tales with clear heroes and villains, "
            "the Mahabharata deliberately presents moral grey — Karna is noble but on "
            "the wrong side; Yudhishthira is righteous but gambles his wife. This "
            "complexity is exactly what adolescents need to develop ethical reasoning."
        ),
    },
    {
        "slug": "hindu-janmashtami",
        "title": "Janmashtami — Celebrating the Birth of Krishna",
        "category": "social",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The story**: Krishna was born at midnight in a prison cell — to Devaki "
            "   and Vasudeva, imprisoned by the tyrant Kamsa. Despite all obstacles, "
            "   God was born. Vasudeva carried the baby across a flooded river to safety.\n"
            "2. **The fast**: observe nirjala (water-only) or partial fast on Janmashtami "
            "   day until midnight — the birth hour.\n"
            "3. **At midnight**: do Krishna puja with the family — bathe the baby Krishna "
            "   murti with panchamrit (milk, honey, curd, ghee, sugar), dress him, "
            "   and place him in a decorated cradle (jhula). Rock the cradle and sing.\n"
            "4. **Dahi Handi** (especially Maharashtra): celebrate the next day with "
            "   a pot of curd suspended high — recreating Krishna's childhood mischief.\n"
            "5. **Reflect**: 'Krishna was born in a prison, in the dark, at midnight — "
            "   yet nothing could stop his arrival. What does this teach about hope?'"
        ),
        "parent_note_md": (
            "Janmashtami marks the birth of Sri Krishna on the Ashtami (eighth day) of "
            "the dark fortnight of Shravana — documented in Bhagavata Purana, Canto 10. "
            "The midnight birth symbolises that divine light emerges in the deepest "
            "darkness — a message of hope that resonates across every tradition. "
            "Krishna's life as presented in the Bhagavatam is multi-layered: child "
            "(Bal Leela), lover (Vrindavan), king (Dwarka), and divine teacher (Gita). "
            "Janmashtami anchors children's relationship with Krishna as a living, "
            "joyful, personal deity — not an abstract concept — making the Bhagavad "
            "Gita more accessible when they encounter it at ages 11–13."
        ),
    },
    {
        "slug": "hindu-bhajan-kirtan",
        "title": "Bhajan and Kirtan — Learn and Sing Devotional Songs",
        "category": "social",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn three bhajans** over three months — one per month:\n"
            "   - **'Raghupati Raghava Raja Ram'** — Gandhi's favourite; asks God to "
            "     let us see the divine in all people regardless of religion.\n"
            "   - **'Om Jai Jagdish Hare'** — the most widely sung aarti across traditions.\n"
            "   - **'Hare Krishna Hare Rama'** (Maha Mantra) — the great mantra of the "
            "     Kali Yuga, according to the Kali-Santarana Upanishad.\n"
            "2. **Sing with the family** at every puja, aarti, and festival.\n"
            "3. **Attend a local bhajan satsang** — community singing at a mandir or "
            "   devotional group. This is kirtan: call-and-response group singing.\n"
            "4. **Explain Nada Yoga**: sound is divine — the universe was created from "
            "   OM (Nada Brahman). Singing God's name is a form of meditation.\n"
            "5. **If musically inclined**: learn harmonium, tabla, or tanpura to "
            "   accompany family bhajans."
        ),
        "parent_note_md": (
            "The Bhagavata Purana (7.5.23) lists Shravanam (hearing), Kirtanam (singing), "
            "and Smaranam (remembering God's name) as the first three of the nine "
            "forms of bhakti (Navavidha Bhakti). Kirtan — congregational singing of "
            "God's names — was the central practice of all Bhakti movement saints: "
            "Mirabai, Tukaram, Kabir, Chaitanya Mahaprabhu. Neuroscience confirms that "
            "group singing releases oxytocin, reduces cortisol, and builds social bonding. "
            "Children who grow up singing bhajans carry devotional music into adulthood "
            "as an always-available form of prayer — one that bypasses the intellect "
            "and reaches the heart directly."
        ),
    },
    {
        "slug": "hindu-daan-giving",
        "title": "Daan — The Sacred Practice of Charitable Giving",
        "category": "financial",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the three levels of daan**:\n"
            "   - **Sattvic daan** (highest): given to the right person, at the right "
            "     time, in the right place, expecting nothing in return (BG 17:20).\n"
            "   - **Rajasic daan**: given expecting a return, recognition, or reward.\n"
            "   - **Tamasic daan**: given with contempt or to the wrong person at "
            "     the wrong time.\n"
            "2. **Set up a daan box**: a small box at home. Each week the child "
            "   puts in 10% of any pocket money — recreating the ancient concept "
            "   of dasvandh (tenth part).\n"
            "3. **Monthly action**: collectively decide where the collected amount "
            "   goes — a local temple food project, a child's education fund, or "
            "   a stray animal shelter.\n"
            "4. **Annadaan**: at least once a month, the family donates food — "
            "   cooked meals, rice, or groceries to someone in need.\n"
            "5. **The key rule**: give without telling others. Anonymous giving is "
            "   the purest form."
        ),
        "parent_note_md": (
            "The Bhagavad Gita (17:20) defines sattvic daan: *'That gift which is given "
            "to one who does nothing in return, with the feeling that it is one's duty "
            "to give — and which is given at the right place and time, to a worthy person "
            "— that is considered to be in the mode of goodness.'* The Taittiriya Upanishad "
            "(1.11.3) instructs: *'Dātavyam iti'* — 'Give!' The concept of dasvandh "
            "(giving a tenth) predates modern tithing. Children who practise regular giving "
            "develop generosity as a character trait — not a response to guilt but as an "
            "expression of the understanding that wealth flows through us, not to us."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 10
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-surya-namaskar",
        "title": "Surya Namaskar — 12-Step Sun Salutation Daily Practice",
        "category": "cognitive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the 12 positions** in order:\n"
            "   Pranamasana → Hasta Uttanasana → Hasta Padasana → Ashwa Sanchalanasana "
            "   → Dandasana → Ashtanga Namaskara → Bhujangasana → Adho Mukha Svanasana "
            "   → Ashwa Sanchalanasana → Hasta Padasana → Hasta Uttanasana → Pranamasana\n"
            "2. **Say the 12 Surya mantras** with each position — one for each of the "
            "   Sun's 12 names: Om Mitraya, Om Ravaye, Om Suryaya, Om Bhanave, "
            "   Om Khagaya, Om Pushne, Om Hiranyagarbhaya, Om Marichaye, Om Adityaya, "
            "   Om Savitre, Om Arkaya, Om Bhaskaraya — followed by Namah.\n"
            "3. **Start with 3 rounds** (morning, facing east), build to 12 over time.\n"
            "4. **Explain the purpose**: Surya Namaskar is both physical exercise and "
            "   worship — thanking the Sun (Surya) who sustains all life on earth.\n"
            "5. **Coordinate with breath**: inhale on extensions, exhale on folds."
        ),
        "parent_note_md": (
            "Surya Namaskar is documented in the ancient Aditya Hridayam (from Valmiki "
            "Ramayana, Yuddha Kanda) — the prayer to the Sun taught to Rama before "
            "his battle with Ravana. Each of the 12 positions corresponds to one of "
            "Surya's 12 names and one sign of the zodiac. A complete round stretches "
            "every major muscle group, stimulates all internal organs, and synchronises "
            "the body with the breath. Research published in the International Journal of "
            "Yoga shows 12 rounds of Surya Namaskar equals 288 yoga poses and burns "
            "approximately 13.9 calories — comparable to other forms of moderate exercise. "
            "It is one of the most complete physical and spiritual practices ever developed."
        ),
    },
    {
        "slug": "hindu-anulom-vilom",
        "title": "Anulom-Vilom Pranayama — Daily Alternate Nostril Breathing",
        "category": "cognitive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The technique**:\n"
            "   - Sit in Sukhasana (cross-legged) with spine erect.\n"
            "   - Right hand in Vishnu mudra: fold index and middle fingers; use thumb "
            "     to close right nostril, ring finger to close left.\n"
            "   - Close right nostril with thumb; inhale slowly through left nostril (4 counts).\n"
            "   - Close both nostrils; hold breath (4 counts) — Kumbhaka.\n"
            "   - Release right nostril; exhale slowly through right (8 counts).\n"
            "   - Inhale through right (4 counts). Hold (4 counts). Exhale through left (8 counts).\n"
            "   - This is one complete cycle. Do 5–10 cycles daily.\n"
            "2. **Best time**: morning on an empty stomach, after Surya Namaskar.\n"
            "3. **Explain the Nadis**: Ida (left/lunar/cooling) and Pingala "
            "   (right/solar/energising) — alternate nostril breathing balances both.\n"
            "4. **Build to**: 10 minutes daily within a month."
        ),
        "parent_note_md": (
            "Anulom-Vilom (Nadi Shodhana Pranayama) is described in the Hatha Yoga Pradipika "
            "(Chapter 2) and the Gheranda Samhita. It purifies the 72,000 nadis (energy "
            "channels) of the subtle body, balancing the sympathetic and parasympathetic "
            "nervous systems. A 2013 study in the Journal of Clinical and Diagnostic Research "
            "found significant improvement in cardiorespiratory endurance and stress "
            "reduction in school children who practised it for 12 weeks. Patanjali's Yoga "
            "Sutras (2:49–51) identify pranayama as the fourth limb of yoga — the bridge "
            "between the body (asana) and the mind (pratyahara). Children who establish "
            "this practice before puberty have a powerful tool for stress regulation."
        ),
    },
    {
        "slug": "hindu-panchatantra-lessons",
        "title": "Panchatantra — Read Stories to Understand Dharma and Wisdom",
        "category": "cognitive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Background**: the Panchatantra (Five Principles) was composed by "
            "   Vishnu Sharma around 200 BCE to teach statecraft, wisdom, and dharma "
            "   to princes through animal fables. It is the source of Aesop's Fables "
            "   and One Thousand and One Nights.\n"
            "2. **Read 10 stories over 10 weeks** — one per week from the five books:\n"
            "   - Book 1 (Mitra Bheda): The Lion and the Bull — on trust and false friends\n"
            "   - Book 2 (Mitra Samprapti): The Crow, Mouse, Deer, and Turtle — on friendship\n"
            "   - Book 3 (Kakolukiyam): Crows and Owls — on strategy in conflict\n"
            "   - Book 4 (Labdhapranasham): The Monkey and the Crocodile — on wisdom and deceit\n"
            "   - Book 5 (Aparikshitakaraka): The Brahmin and the Mongoose — on hasty judgement\n"
            "3. **After each story**: identify the dharma principle — what should the "
            "   characters have done? What did their choices cost them?\n"
            "4. **Apply to real life**: 'When have you faced a situation like this?'"
        ),
        "parent_note_md": (
            "The Panchatantra is one of the most widely translated books in human history — "
            "appearing in over 50 languages. Vishnu Sharma wrote it to teach practical "
            "wisdom (niti shastra) through stories, because stories bypass resistance "
            "and reach the heart. The five books cover: splitting alliances, building "
            "alliances, war and peace, losing what is gained, and acting without thinking. "
            "These are exactly the situations children face — in friendships, in social "
            "dynamics, in peer pressure, and in decision-making. The Panchatantra is "
            "Hinduism's most practical ethical education system, designed specifically "
            "for 10–14 year olds."
        ),
    },
    {
        "slug": "hindu-matru-pitru-devo-bhava",
        "title": "Matru / Pitru Devo Bhava — Honour Parents as the First God",
        "category": "social",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The teaching** from Taittiriya Upanishad (1.11.2):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > मातृदेवो भव । पितृदेवो भव । आचार्यदेवो भव । अतिथिदेवो भव ।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Mātṛdevo bhava | Pitṛdevo bhava | Ācāryadevo bhava | Atithidevo bhava |*\n\n"
            "   **Meaning:** 'May your mother be your god. May your father be your god. "
            "   May your teacher be your god. May your guest be your god.'\n\n"
            "2. **Daily practice**: before leaving the house each morning, touch the "
            "   feet of both parents and receive their blessing.\n"
            "3. **Weekly act of service**: do one thing for parents without being asked — "
            "   cook tea, massage tired feet, clean their room.\n"
            "4. **Explain why**: parents gave us life, raised us, sacrificed for us. "
            "   In doing so, they acted as God's instruments. Honouring them is "
            "   honouring the divine itself.\n"
            "5. **The limit**: this applies when parents act dharmatically — the teaching "
            "   also includes the story of Prahlada, who loved his father but did not "
            "   obey adharma."
        ),
        "parent_note_md": (
            "The Taittiriya Upanishad's convocation address (1.11) is Hinduism's most "
            "complete instruction to young people entering adult life. It begins with "
            "the famous fourfold teaching: honour mother, father, teacher, and guest as "
            "God. Shankara's commentary notes that this is not blind obedience but "
            "recognition of the divine working through those who have shaped us. The "
            "Ramayana's most powerful ethical moment is Ram's acceptance of 14 years of "
            "exile rather than dishonour his father's word — Pitru dharma elevated to "
            "cosmic principle. Children who practise touching parents' feet daily develop "
            "humility, gratitude, and a living connection to their ancestral lineage."
        ),
    },
    {
        "slug": "hindu-ekadashi-fast",
        "title": "Ekadashi Fasting — Practice and Meaning of the Fortnightly Fast",
        "category": "household",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is Ekadashi**: the 11th day (Ekadashi = 11) of each lunar fortnight "
            "   — there are 24 Ekadashis per year. It is the most widely observed fast "
            "   in Vaishnavism and broadly across Hinduism.\n"
            "2. **How to fast**: abstain from grains and lentils (the main restriction). "
            "   Permitted: fruits, milk, nuts, root vegetables (like potato, sweet potato). "
            "   Full nirjala (no water) fast is for advanced practitioners.\n"
            "3. **Why no grains on Ekadashi**: the Padma Purana states that on this day, "
            "   sinful energies reside in grains — avoiding them is a purification.\n"
            "4. **What to do instead of eating**: spend extra time in prayer, reading "
            "   scripture, or seva. The fast creates space for the divine.\n"
            "5. **Break the fast the next day** (Dwadashi) with light food after morning "
            "   puja — this is called Parana.\n"
            "6. **Start with one Ekadashi per month** for children — build to both."
        ),
        "parent_note_md": (
            "Ekadashi fasting is prescribed in the Bhagavata Purana and extensively in "
            "the Padma Purana (Uttara Khanda). It is observed across Vaishnava, Shaiva, "
            "and Smarta traditions. Physiologically, twice-monthly fasting aligns with "
            "modern intermittent fasting research — the body's autophagy (cellular repair) "
            "processes activate significantly after 16–24 hours of grain restriction. "
            "Spiritually, fasting is the clearest embodied practice of the teaching that "
            "we are not the body — we can choose to override physical hunger for a higher "
            "purpose. Children who learn voluntary fasting before adolescence develop "
            "impulse control, willpower, and the lived experience of mind over body."
        ),
    },
    {
        "slug": "hindu-rangoli-art",
        "title": "Rangoli — Traditional Sacred Art and Its Spiritual Meaning",
        "category": "household",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is Rangoli**: geometric patterns made at the entrance of the home "
            "   with coloured powder, rice flour, or flower petals — welcoming the divine "
            "   and auspicious energies into the home.\n"
            "2. **Learn 5 basic patterns** progressively:\n"
            "   - Simple dots-and-lines grid (kolam style)\n"
            "   - Flower pattern (lotus — symbol of purity)\n"
            "   - Swastika (ancient auspicious symbol — meaning 'good being')\n"
            "   - Diya pattern (for Diwali)\n"
            "   - Peacock (symbol of Krishna)\n"
            "3. **When to make it**: every morning at the entrance (daily kolam in "
            "   South India), on festival days, and for guests.\n"
            "4. **Use rice flour when possible**: it feeds ants and insects — "
            "   another act of ahimsa embedded in daily ritual.\n"
            "5. **Explain the geometry**: rangoli patterns are based on sacred geometry — "
            "   the same mathematical ratios found in temple architecture (Vastu Shastra)."
        ),
        "parent_note_md": (
            "Rangoli (kolam in South India, alpana in Bengal, aripana in Bihar) is one "
            "of the oldest continuous art traditions in the world — examples dating to "
            "the Indus Valley Civilisation. The Griha Sutras (household ritual texts) "
            "prescribe daily kolam as a form of sthapana — establishing sacred order at "
            "the threshold. The lotus pattern represents Lakshmi; the swastika (svastika "
            "= good being, prosperity) is Hinduism's most ancient auspicious symbol, "
            "predating its misuse by millennia. Children who learn rangoli develop fine "
            "motor skills, spatial reasoning, patience, and a living connection to the "
            "sacred art tradition of their ancestors."
        ),
    },
    {
        "slug": "hindu-ganesh-chaturthi",
        "title": "Ganesh Chaturthi — Story, Puja, and Eco-Friendly Immersion",
        "category": "social",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The story**: Shiva and Parvati's son received an elephant head after "
            "   Shiva, in anger, beheaded him — then restored him with the head of "
            "   the first creature found, and declared him Prathama Pujya (first to "
            "   be worshipped). Parvati's grief turned to joy.\n"
            "2. **Install the murti**: on Chaturthi (4th day of Bhadrapada month), "
            "   bring a clay Ganesha murti home. Perform Prana Pratishtha (inviting "
            "   Ganesha's presence into the murti) with the family pandit or from "
            "   a printed ritual guide.\n"
            "3. **Daily puja for 1.5, 5, 7, or 11 days**: offer modak (his favourite "
            "   sweet), durva grass, red flowers, and coconut.\n"
            "4. **Visarjan (immersion)**: on the final day, carry Ganesha in procession "
            "   to a body of water (or a bucket of water at home) and immerse the murti — "
            "   symbolising his return to the cosmic source.\n"
            "5. **Eco-friendly**: use only natural clay murtis with natural colours "
            "   (no plaster of Paris or chemical paints) — dharma includes environmental "
            "   responsibility."
        ),
        "parent_note_md": (
            "Ganesh Chaturthi as a public festival was revived by Bal Gangadhar Tilak in "
            "1893 as a platform for community gathering during the independence movement — "
            "using devotion as social cohesion. The theological root is in the Ganesha "
            "Purana and Mudgala Purana. The immersion (visarjan) ritual teaches a profound "
            "truth: we welcome, love, and then release — even the most beloved things "
            "return to the source. This is the Hindu teaching on impermanence (anitya) "
            "expressed as joyful festival rather than mournful philosophy. Children who "
            "participate in Ganesh Chaturthi's full 10-day cycle — from installation to "
            "immersion — experience this teaching bodily, not abstractly."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 11
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-gita-introduction",
        "title": "Bhagavad Gita — Introduction and the Heart of Karma Yoga (Ch 1–2)",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Context of the Gita**: set the scene — Arjuna stands between two armies "
            "   on the battlefield of Kurukshetra. His relatives are on both sides. He "
            "   drops his bow and refuses to fight. Krishna — his charioteer and God — "
            "   responds. The entire Bhagavad Gita is this conversation.\n"
            "2. **Chapter 1**: Arjuna's grief (Vishada Yoga) — read it together and discuss: "
            "   'Have you ever faced a situation where doing the right thing felt impossible?'\n"
            "3. **Chapter 2**: the turning point — Krishna's first great teaching. Learn "
            "   the key shloka:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > कर्मण्येवाधिकारस्ते मा फलेषु कदाचन ।\n"
            "   > मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Karmaṇyevādhikāraste mā phaleṣu kadācana |*\n"
            "   > *Mā karmaphalaheturbhūrmā te saṅgo'stvakarmaṇi ||*\n\n"
            "   **Meaning (BG 2:47):** 'You have the right to perform your action, but "
            "   never to its fruits. Let not the fruits of action be your motive, nor "
            "   let your attachment be to inaction.'\n\n"
            "4. **Discuss for 10 minutes**: 'What does this verse mean for exams? For "
            "   sport? For how we treat others?'\n"
            "5. **Begin a Gita journal**: write one key verse per week with personal reflection."
        ),
        "parent_note_md": (
            "The Bhagavad Gita, embedded in the Mahabharata's Bhishma Parva, is Hinduism's "
            "most revered philosophical text — 700 verses across 18 chapters. BG 2:47 is "
            "the verse most cited by leaders from Gandhi to Tilak to Steve Jobs: do your "
            "best work without being attached to the outcome. This teaching cuts directly "
            "against the anxiety and result-obsession that defines modern adolescent life. "
            "Introducing the Gita at age 11 — through narrative (Arjuna's crisis) before "
            "philosophy — makes it emotionally accessible. Children who begin here will "
            "return to the Gita at every major life transition."
        ),
    },
    {
        "slug": "hindu-karma-law",
        "title": "Karma — Understanding the Universal Law of Cause and Effect",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define Karma precisely**: Karma (कर्म) simply means 'action.' The law "
            "   of karma is: every action has a consequence — good actions generate "
            "   good results (Punya), harmful actions generate suffering (Papa).\n"
            "2. **Three types of karma** (from the Yoga Sutras and Vedanta):\n"
            "   - **Sanchita karma**: accumulated karma from all past actions\n"
            "   - **Prarabdha karma**: the portion bearing fruit right now (current life)\n"
            "   - **Agami / Kriyamana karma**: karma being created by current actions\n"
            "3. **The Gita's deeper teaching** (BG 4:17): karma is not just physical action — "
            "   it includes speech and thought. Even thinking harmful thoughts is karma.\n"
            "4. **Practical reflection**: ask the child — 'Think of three situations where "
            "   your action had an unexpected consequence — good or bad. What does this tell "
            "   you about how to act now?'\n"
            "5. **Debunk misuse**: karma does not mean 'suffering is deserved' — it means "
            "   'choices have consequences.' It is a call to act better, not a reason to "
            "   ignore others' suffering."
        ),
        "parent_note_md": (
            "BG 4:17 states: *'The nature of action is hard to understand — one must know "
            "the nature of action, the nature of wrong action, and the nature of inaction.'* "
            "The Brihadaranyaka Upanishad (4.4.5) teaches: *'You are what your deep, driving "
            "desire is. As your desire is, so is your will. As your will is, so is your deed. "
            "As your deed is, so is your destiny.'* Understanding karma as a moral physics — "
            "not fatalism — gives adolescents a profound sense of agency: every choice is "
            "building the person they are becoming. This counters both victimhood thinking "
            "and passive resignation."
        ),
    },
    {
        "slug": "hindu-dharma-duty",
        "title": "Dharma — Understanding Your Duty at Every Stage of Life",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define Dharma**: from the root *dhr* (to hold, sustain). Dharma is "
            "   the principle that holds everything together — cosmic order, moral duty, "
            "   and right conduct. It is what sustains individuals, families, and society.\n"
            "2. **Four levels of Dharma**:\n"
            "   - **Sanatana Dharma** (eternal duty): truth, non-violence, purity — for all\n"
            "   - **Varna Dharma**: duties according to one's role in society\n"
            "   - **Ashrama Dharma**: duties according to stage of life\n"
            "   - **Svadharma**: one's own specific duty (BG 18:47 — 'Better is one's own "
            "     dharma imperfectly performed than the dharma of another perfectly performed')\n"
            "3. **The key question**: 'What is my dharma right now, as a student?' — "
            "   study, respect for teachers, care for family, self-development.\n"
            "4. **Debate**: 'What is harder — doing what you're told or figuring out what "
            "   is truly right? When might they be different?'\n"
            "5. **Connect to current life**: apply dharma to a real dilemma the child faces "
            "   this week — a friendship conflict, a school decision, a family situation."
        ),
        "parent_note_md": (
            "BG 18:47: *'Better is one's own dharma, though imperfectly performed, than the "
            "dharma of another well performed.'* The Mahabharata's entire drama is built on "
            "dharmic dilemmas — characters who face impossible choices between competing "
            "duties. Dharma is not a simple rulebook; it is a dynamic, contextual, evolving "
            "understanding of right action. Teaching dharma at 11 gives adolescents a "
            "framework for ethical reasoning that goes far beyond rule-following — it builds "
            "the capacity for moral judgment, which is exactly what the teenage years demand."
        ),
    },
    {
        "slug": "hindu-temple-seva",
        "title": "Temple Seva — Volunteering at the Mandir as Spiritual Practice",
        "category": "social",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a local mandir** and speak to the pujari or trust committee "
            "   about volunteering once or twice a month.\n"
            "2. **Types of seva available to children and youth**:\n"
            "   - Flower arrangement (pushpa seva) — offering fresh flowers before the deity\n"
            "   - Sweeping and cleaning the temple floor (sammajana seva)\n"
            "   - Welcoming visitors and guiding new devotees\n"
            "   - Assisting with prasad distribution\n"
            "   - Helping with festival preparations\n"
            "3. **The inner attitude**: seva at the mandir is not volunteering — it is "
            "   direct service to God. Do it silently, with full attention, no phone.\n"
            "4. **After seva**: sit quietly in the garbhagriha (sanctum) for 5 minutes "
            "   in silence — this is the gift the mandir gives back.\n"
            "5. **Build consistency**: monthly is a minimum; weekly is transformative."
        ),
        "parent_note_md": (
            "Temple seva embodies BG 9:27: *'Whatever you do, eat, offer, or give away, "
            "whatever austerity you practise — do it as an offering to Me.'* Serving in "
            "the temple community also connects children to their extended Hindu sangha "
            "(community) — the elders, the pandit, the other families. Research on "
            "adolescent wellbeing consistently shows that community belonging and "
            "contribution are among the strongest protective factors against depression, "
            "substance use, and antisocial behaviour. Temple seva delivers both the "
            "spiritual benefit (serving God) and the social benefit (belonging) simultaneously."
        ),
    },
    {
        "slug": "hindu-sattvic-diet",
        "title": "Sattvic Diet — Principles and Why Food Affects the Mind",
        "category": "household",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The three food categories** from BG 17:8–10:\n"
            "   - **Sattvic** (pure, clarity-promoting): fresh fruits and vegetables, "
            "     whole grains, milk, ghee, honey, nuts — promotes calmness, clarity, "
            "     health, and longevity.\n"
            "   - **Rajasic** (stimulating): very spicy, sour, salty, or pungent foods, "
            "     strong tea/coffee — promotes restlessness and desire.\n"
            "   - **Tamasic** (dulling): stale, overprocessed, fermented, heavily fried "
            "     foods — promotes lethargy, dullness, and heaviness.\n"
            "2. **Practical audit**: for one week, the child labels every meal as sattvic, "
            "   rajasic, or tamasic and notices how they feel after.\n"
            "3. **The key shift**: add one sattvic meal per day — a fresh fruit breakfast, "
            "   a dal-rice lunch, a warm milk and honey before bed.\n"
            "4. **The mind-food link**: explain that yogis have taught for centuries that "
            "   food directly shapes consciousness — the Chandogya Upanishad (6.5.4) "
            "   teaches: *'Annamayam hi manah'* — 'The mind is made of food.'"
        ),
        "parent_note_md": (
            "BG 17:8: *'Foods that promote longevity, virtue, strength, health, happiness, "
            "and joy — juicy, smooth, substantial, and agreeable — are dear to those in "
            "the mode of goodness (sattva).'* The Chandogya Upanishad (6.5.4) is even more "
            "direct: *'The food that is eaten is divided into three parts. The grossest "
            "becomes faeces. The middle becomes flesh. The subtlest becomes the mind.'* "
            "Modern nutritional psychiatry now confirms what the Upanishads stated 3,000 "
            "years ago — diet directly affects mental health, concentration, and emotional "
            "regulation. Teaching sattvic eating to adolescents gives them a framework for "
            "food choices rooted in understanding, not restriction."
        ),
    },
    {
        "slug": "hindu-atman-concept",
        "title": "Atman — Understanding the Eternal Self Within",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The central teaching of BG 2:20** — learn it by heart:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > न जायते म्रियते वा कदाचिन्नायं भूत्वा भविता वा न भूयः ।\n"
            "   > अजो नित्यः शाश्वतोऽयं पुराणो न हन्यते हन्यमाने शरीरे ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Na jāyate mriyate vā kadācinNāyaṃ bhūtvā bhavitā vā na bhūyaḥ |*\n"
            "   > *Ajo nityaḥ śāśvato'yaṃ purāṇo na hanyate hanyamāne śarīre ||*\n\n"
            "   **Meaning:** 'The soul is never born, nor does it die. It has not come "
            "   into being, nor will it cease to be. Unborn, eternal, ever-existing, "
            "   primeval — it is not slain when the body is slain.'\n\n"
            "2. **The mirror exercise**: sit before a mirror and ask — 'Who is looking? "
            "   Your eyes are looking — but who is aware of your eyes? That witness "
            "   awareness is the Atman.'\n"
            "3. **The snake and rope analogy** (from Adi Shankara): in dim light, a rope "
            "   looks like a snake. We mistake the body (rope) for the self (snake). "
            "   Knowledge removes the mistake.\n"
            "4. **Discuss grief and loss**: 'When a grandparent dies, where do they go? "
            "   The Atman is never lost — it takes a new form.'"
        ),
        "parent_note_md": (
            "BG 2:20 is the Gita's foundational statement on the Atman — the eternal, "
            "unchanging self that inhabits the body but is not the body. The Katha Upanishad "
            "(1.2.18–19) presents the same teaching through Nachiketa's dialogue with Yama "
            "(Death) himself. Understanding Atman resolves one of adolescence's deepest "
            "anxieties: 'Who am I? Am I this body? Am I my grades? My looks? My popularity?' "
            "The answer the Gita gives is radical: you are none of those — you are "
            "the unchanging witness behind all of them. This is the most powerful "
            "antidote to the identity fragility that makes the teenage years so turbulent."
        ),
    },
    {
        "slug": "hindu-study-as-worship",
        "title": "Vidya as Sadhana — Dedicating All Learning to the Divine",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The teaching from BG 4:33**:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > श्रेयान्द्रव्यमयाद्यज्ञाज्ज्ञानयज्ञः परन्तप ।\n"
            "   > सर्वं कर्माखिलं पार्थ ज्ञाने परिसमाप्यते ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Śreyāndravyamayādyajñājjñānayajñaḥ parantapa |*\n"
            "   > *Sarvaṃ karmākhilaṃ Pārtha jñāne parisamāpyate ||*\n\n"
            "   **Meaning:** 'The sacrifice of wisdom (jnana yajna) is superior to any "
            "   material sacrifice, O Arjuna — for all actions in their entirety "
            "   culminate in wisdom.'\n\n"
            "2. **Pre-study ritual**: before sitting to study, say the Saraswati Vandana "
            "   (learned at age 8), light a small diya if possible, and set an intention: "
            "   'I study not for grades alone, but as an offering to Saraswati.'\n"
            "3. **Post-study**: close with gratitude — 'Thank you for the understanding "
            "   I received today.'\n"
            "4. **Examine motivation**: 'Am I studying because I am curious? Because I "
            "   want to serve others with this knowledge? Or only for the exam mark?'\n"
            "5. **Discuss**: what would school feel like if learning itself were the goal?"
        ),
        "parent_note_md": (
            "The Taittiriya Upanishad's instruction to graduates (1.11.1) begins with "
            "*'Satyam vada, dharmam chara'* and continues: *'May learning and teaching "
            "never be neglected by you.'* Hinduism considers Vidya (knowledge) the "
            "highest form of wealth — *'Na chor hary vidya'* (no thief can steal "
            "learning). The concept of jnana yajna (sacrifice of knowledge) transforms "
            "study from instrumental (for grades, career) to intrinsic (for understanding, "
            "for service). Adolescents who experience learning as sacred — rather than as "
            "a performance — are far more resilient to academic setbacks and develop "
            "genuine intellectual curiosity."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 12
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-saints-stories",
        "title": "Lives of Great Saints — Mirabai, Tukaram, Kabir, Ramakrishna",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read one saint's life per month** over four months:\n"
            "   - **Mirabai** (1498–1547): Rajput princess who gave up royal life for "
            "     Krishna. Poisoned by enemies — the poison turned to nectar. Her bhajans "
            "     are sung across India today. *Key teaching*: bhakti transcends all "
            "     social barriers — even gender and caste.\n"
            "   - **Tukaram** (1608–1650): Marathi weaver-saint. Lost his family in "
            "     famine, found God in sorrow. His abhangas (devotional poems) are "
            "     Maharashtra's spiritual heritage. *Key teaching*: God is closer in "
            "     suffering than in comfort.\n"
            "   - **Kabir** (1440–1518): weaver, mystic, poet. Neither Hindu nor Muslim — "
            "     worshipped at both temples. His dohas (couplets) cut through all "
            "     religious hypocrisy. *Key teaching*: God is found within, not in "
            "     pilgrimage or ritual alone.\n"
            "   - **Ramakrishna** (1836–1886): priest of Kali who experienced samadhi and "
            "     practised all major religions. *Key teaching*: all paths lead to the "
            "     same divine — Sarva Dharma Sambhava.\n"
            "2. **After each**: 'What obstacle did this saint face? How did they respond? "
            "   What would you do?'"
        ),
        "parent_note_md": (
            "India's Bhakti movement saints (12th–17th centuries) are Hinduism's most "
            "accessible teachers for teenagers — they were themselves rebels, questioners, "
            "and people who felt deeply. Mirabai defied patriarchy; Kabir defied religious "
            "orthodoxy; Tukaram defied social hierarchy. Their poetry is viscerally alive "
            "today because it speaks from direct experience of God, not theological theory. "
            "Swami Vivekananda wrote of Ramakrishna: 'He was the very embodiment of "
            "everything I have been trying to teach.' Children who know their saints "
            "have role models for principled non-conformity — courage in devotion that "
            "does not bend to social pressure."
        ),
    },
    {
        "slug": "hindu-annadaan",
        "title": "Annadaan — Donating Food as the Highest Form of Daan",
        "category": "financial",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The teaching** from Taittiriya Upanishad (3.2.1):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > अन्नं न निन्द्यात् तद् व्रतम् ।\n"
            "   > अन्नं न परिचक्षीत तद् व्रतम् ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Annaṃ na nindyāt tad vratam | Annaṃ na paricakṣīta tad vratam ||*\n\n"
            "   **Meaning:** 'Do not disrespect food — that is your vow. Do not reject "
            "   food — that is your vow.' (Annam Brahma — food is Brahman.)\n\n"
            "2. **Monthly action**: once a month, the family cooks extra food and "
            "   distributes it to the poor, to workers, or through a temple langar "
            "   (community kitchen).\n"
            "3. **Waste audit**: for one week, track how much food is thrown away at "
            "   home. Calculate. Discuss — wasting food is wasting Brahman.\n"
            "4. **Join a temple annadaan program**: many mandirs run daily or weekly "
            "   free meals (mahaprasad). Volunteer to serve — ladle out food "
            "   with both hands, with the attitude of serving Narayana.\n"
            "5. **The discipline**: never criticise food that is prepared and offered."
        ),
        "parent_note_md": (
            "The Taittiriya Upanishad (3.2) contains one of Hinduism's most extraordinary "
            "declarations: *'Annam Brahma'* — food IS God. The passage continues with a "
            "graduated sequence: from food comes life, from life comes mind, from mind "
            "comes intellect, from intellect comes bliss. Annadaan is therefore the most "
            "tangible form of serving the divine in others. ISKCON's midday meal program "
            "feeds over 1.2 million school children across India daily — the world's "
            "largest vegetarian food relief program, built on this single Upanishadic "
            "principle. Teaching annadaan at 12 ensures children understand that "
            "generosity with food is not charity — it is sacrament."
        ),
    },
    {
        "slug": "hindu-gratitude-kritajna",
        "title": "Kritajna — Daily Gratitude Practice as Spiritual Discipline",
        "category": "social",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The word**: Kritajna (कृतज्ञ) = krita (what has been done/given) + "
            "   jña (one who knows/remembers). A grateful person remembers what they "
            "   have received and from whom.\n"
            "2. **The daily practice**: every night before the bedtime shloka, the child "
            "   writes three things:\n"
            "   - One gift from God or nature today (sunlight, health, food)\n"
            "   - One act of kindness received from a person today\n"
            "   - One capacity or talent they used well today\n"
            "3. **The Vedic root**: the Rig Veda (10.117.1) teaches: *'The gods favour "
            "   the generous.'* Gratitude is the recognition that nothing we have came "
            "   solely from our own effort.\n"
            "4. **Express it**: at least once a week, the child verbally thanks one "
            "   person they usually take for granted — a parent, a teacher, a classmate.\n"
            "5. **Connect to puja**: the entire ritual of puja is an act of gratitude — "
            "   offering back to God what God has given us."
        ),
        "parent_note_md": (
            "Gratitude (Kritajnata) is explicitly listed among the divine qualities in "
            "BG 16:1–3: *'Fearlessness, purity of heart, steadfastness in knowledge and "
            "yoga, charity, control of the senses, sacrifice, study of scripture, "
            "austerity, uprightness…'* Ingratitude is listed among the demonic qualities. "
            "Positive psychology research (Emmons & McCullough, 2003) shows that a "
            "daily gratitude journal reduces depressive symptoms by 25% and increases "
            "subjective wellbeing significantly. Adolescence is when negativity bias "
            "peaks — the brain is wired to notice threats more than gifts. Gratitude "
            "practice is a direct counter-training, and it is recommended by both "
            "modern neuroscience and 3,000 years of Hindu spiritual tradition."
        ),
    },
    {
        "slug": "hindu-body-as-temple",
        "title": "Body as Temple — Health and Lifestyle Through a Dharmic Lens",
        "category": "household",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The teaching**: the Chandogya Upanishad (6.8.6) teaches "
            "*'Tat tvam asi'* — 'Thou art That.' The body is the temporary vehicle "
            "of the Atman — the temple of God within. How we treat the body is how "
            "we treat the divine guest residing within it.\n"
            "2. **Five Saucha (purity) practices** from Patanjali's Niyamas:\n"
            "   - **External purity**: daily bathing, clean clothes, clean eating space\n"
            "   - **Internal purity**: sattvic food, limiting junk food and intoxicants\n"
            "   - **Sleep discipline**: fixed sleep and wake times (8 hours for this age)\n"
            "   - **Exercise**: 30 minutes daily — yoga, walking, or sport\n"
            "   - **Screen boundary**: no screens 1 hour before bed\n"
            "3. **Reflect weekly**: 'Am I maintaining the body God gave me? Is it "
            "   getting stronger, cleaner, and more energised this week?'\n"
            "4. **Ayurveda basics**: introduce the three doshas (Vata, Pitta, Kapha) "
            "   and help the child identify their dominant type — this is Hinduism's "
            "   personalised health system, 5,000 years old."
        ),
        "parent_note_md": (
            "BG 17:8–10 classifies foods by their effect on the three gunas. The Yoga "
            "Sutras (2:40) state that Saucha (purity) leads to *'dispassion for one's "
            "own body'* — meaning we care for it without being enslaved by its "
            "appearance or cravings. Ayurveda — the Vedic science of life — is rooted "
            "in the same framework: the body is a vehicle for dharma, artha, kama, and "
            "ultimately moksha. It must be maintained accordingly. Teaching adolescents "
            "to see health choices through a spiritual framework — rather than purely "
            "aesthetic or social ones — gives them a more stable and principled "
            "foundation for making good choices about food, sleep, and exercise."
        ),
    },
    {
        "slug": "hindu-maya-concept",
        "title": "Maya — Understanding Illusion and What Is Truly Real",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define Maya** (माया): from the root *ma* (to measure, to create). "
            "   Maya is the cosmic power of illusion — the force that makes the "
            "   temporary appear permanent and the relative appear absolute.\n"
            "2. **The classic analogy** (Adi Shankara, Vivekachudamani): in dim light, "
            "   a rope appears to be a snake. The fear is real — the snake is not. "
            "   Maya is like that light — it distorts how we see Brahman (pure reality) "
            "   as the world of names and forms.\n"
            "3. **Maya in daily life** — identify three examples together:\n"
            "   - Thinking popularity on social media is real happiness\n"
            "   - Believing that if we get 'that thing' we will be permanently happy\n"
            "   - Identifying so strongly with our body that we forget we are the Atman\n"
            "4. **The Gita's teaching** (BG 7:14): *'This divine energy of Mine — "
            "   consisting of the three modes of nature — is difficult to overcome. "
            "   But those who have surrendered to Me can easily cross beyond it.'\n"
            "5. **The practical takeaway**: question your cravings. Ask — 'Is this "
            "   real need or Maya's illusion?'"
        ),
        "parent_note_md": (
            "Maya is one of the most misunderstood concepts in Hindu philosophy. It does "
            "not mean 'the world is not real' — it means the world as we ordinarily "
            "perceive it (as separate, permanent, and the source of lasting happiness) "
            "is not accurately perceived. Shankara's Advaita Vedanta and Ramanuja's "
            "Vishishtadvaita both engage with Maya, though they interpret it differently. "
            "For adolescents, the concept of Maya is immediately applicable: the social "
            "media performance of life (perfect photos, likes, followers) is a contemporary "
            "Maya — appearances mistaken for substance. Children who grasp Maya develop "
            "healthy scepticism about surface appearances and a deeper search for what "
            "is genuinely true and lasting."
        ),
    },
    {
        "slug": "hindu-kshama-forgiveness",
        "title": "Kshama — The Practice of Forgiveness as Spiritual Power",
        "category": "social",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The teaching** from the Mahabharata (Udyoga Parva 33.68):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > क्षमा बलमशक्तानां शक्तानां भूषणं क्षमा ।\n"
            "   > क्षमा वशीकृते लोके क्षमया किं न साध्यते ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Kṣamā balamaśaktānāṃ śaktānāṃ bhūṣaṇaṃ kṣamā |*\n"
            "   > *Kṣamā vaśīkṛte loke kṣamayā kiṃ na sādhyate ||*\n\n"
            "   **Meaning:** 'Forgiveness is the strength of the weak; forgiveness is "
            "   the ornament of the strong. The world is conquered through forgiveness — "
            "   what cannot be achieved through forgiveness?'\n\n"
            "2. **Distinguish forgiveness from approval**: forgiving someone does not "
            "   mean what they did was acceptable. It means you are releasing the "
            "   poison from your own mind — not writing off the wrong.\n"
            "3. **The 5-step practice**:\n"
            "   - Name what hurt you (privately, in a journal)\n"
            "   - Name the impact it had on you\n"
            "   - Decide to release the resentment — not for their sake, for yours\n"
            "   - Say or write: 'I release [name] from my judgement'\n"
            "   - Do not bring it up again — this is the measure of real forgiveness"
        ),
        "parent_note_md": (
            "The Mahabharata dedicates an entire section to Kshanti (patient forgiveness). "
            "BG 16:3 lists kshanti (forbearance) among the divine qualities. Adi Shankara's "
            "Vivekachudamani also places kshama as essential for the spiritual aspirant. "
            "Neuroscientific research at Stanford's Forgiveness Project shows that "
            "practising forgiveness reduces cardiovascular stress markers, depression, "
            "and anxiety — and increases empathy and life satisfaction. For adolescents "
            "navigating intense social dynamics — exclusion, betrayal, gossip, bullying — "
            "the capacity to forgive without either suppressing or stewing is one of the "
            "most practically important skills they can develop."
        ),
    },
    {
        "slug": "hindu-anger-control",
        "title": "Controlling Anger — The Gita's Chain of Destruction and Its Remedy",
        "category": "social",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn BG 2:62–63** — the chain of destruction:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > ध्यायतो विषयान्पुंसः सङ्गस्तेषूपजायते ।\n"
            "   > सङ्गात्सञ्जायते कामः कामात्क्रोधोऽभिजायते ।।\n"
            "   > क्रोधाद्भवति सम्मोहः सम्मोहात्स्मृतिविभ्रमः ।\n"
            "   > स्मृतिभ्रंशाद्बुद्धिनाशो बुद्धिनाशात्प्रणश्यति ।।\n\n"
            "   **Meaning (BG 2:62–63):** 'Thinking about objects of sense, attachment "
            "   forms. From attachment, desire is born. From desire comes anger. From "
            "   anger comes delusion. From delusion, memory fails. From memory failure, "
            "   the intellect perishes. When the intellect perishes, the person is lost.'\n\n"
            "2. **Map the chain in a real situation**: recall a recent moment of anger. "
            "   Trace it back — what was the desire? What was the attachment underneath?\n"
            "3. **The STOP technique with Hindu grounding**:\n"
            "   - **S**top — do not act immediately\n"
            "   - **T**ake a breath — 4 counts in, 8 counts out (Anulom-Vilom)\n"
            "   - **O**bserve — what am I feeling? What is the underlying desire?\n"
            "   - **P**roceed with dharma — not with impulse\n"
            "4. **Chant 'Om' three times** when anger rises — the vibration breaks the chain."
        ),
        "parent_note_md": (
            "BG 2:62–63 is possibly the most psychologically precise description of how "
            "human beings destroy themselves — nearly 2,000 years before Freud. The chain "
            "runs: sense-contact → attachment → desire → anger → delusion → memory loss → "
            "intellectual failure → total self-destruction. Krishna gives the solution "
            "in BG 2:64–65: the person who has regulated their senses moves freely in "
            "the world without being mastered by it — and in that steadiness, all sorrow "
            "ends. Adolescence is the peak period for anger dysregulation — the prefrontal "
            "cortex is still developing. Teaching this Gita framework gives teenagers "
            "a Sanskrit-backed neuroscience of their own emotional states."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 13
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-four-purusharthas",
        "title": "Four Purusharthas — The Four Goals of a Well-Lived Hindu Life",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the four Purusharthas** (goals of human existence):\n"
            "   - **Dharma** (धर्म): righteousness, duty, moral order — the foundation\n"
            "   - **Artha** (अर्थ): wealth, prosperity, career, material wellbeing — "
            "     pursued within the bounds of dharma\n"
            "   - **Kama** (काम): pleasure, love, beauty, enjoyment — enjoyed "
            "     within dharma and without harming others\n"
            "   - **Moksha** (मोक्ष): liberation, freedom from the cycle of birth and "
            "     death — the ultimate goal\n"
            "2. **The key insight**: all four are legitimate goals. Hinduism does not "
            "   reject wealth or pleasure — it insists they be pursued in the right "
            "   order and within dharma.\n"
            "3. **Life planning exercise**: ask the child — 'What is your Artha goal "
            "   for this year? What is your Dharma goal? What Kama (simple pleasures) "
            "   do you want to preserve? What does Moksha mean to you at this age?'\n"
            "4. **Discuss trade-offs**: when Artha conflicts with Dharma — what do "
            "   you choose? Give real examples (cheating to win, lying to get a job).\n"
            "5. **Source**: Manusmriti, Arthashastra, and BG 18:46 all address the "
            "   relationship between the four Purusharthas."
        ),
        "parent_note_md": (
            "The Purusharthas are the organising framework of Hindu life — providing a "
            "comprehensive answer to the question 'What should I aim for?' Unlike "
            "traditions that prioritise only spiritual goals, or cultures that prioritise "
            "only material ones, Hinduism holds all four in dynamic balance. The "
            "Arthashastra of Kautilya is an entire treatise on Artha. The Kamasutra "
            "of Vatsyayana is an entire treatise on Kama. Both are considered legitimate "
            "Hindu knowledge — within the overarching frame of Dharma. Teaching the "
            "Purusharthas at 13 gives adolescents a life-philosophy wide enough to hold "
            "ambition, pleasure, duty, and spiritual aspiration — without sacrificing any."
        ),
    },
    {
        "slug": "hindu-three-gunas",
        "title": "Three Gunas — Sattva, Rajas, Tamas in Daily Life",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the three Gunas** (qualities of Prakriti/Nature, from BG 14):\n"
            "   - **Tamas** (inertia, darkness): heaviness, laziness, confusion, "
            "     dullness, sleep, ignorance, procrastination\n"
            "   - **Rajas** (energy, passion): activity, desire, restlessness, "
            "     ambition, excitement, anger, attachment to results\n"
            "   - **Sattva** (clarity, goodness): lightness, knowledge, harmony, "
            "     contentment, wisdom, selflessness\n"
            "2. **Apply to daily experiences** — classify each below as S, R, or T:\n"
            "   - Eating chips and watching Netflix for 3 hours (T)\n"
            "   - Competing fiercely to win at any cost (R)\n"
            "   - Waking at 6am, doing yoga, eating fruit, studying (S)\n"
            "   - Volunteering at the temple out of genuine care (S)\n"
            "3. **The goal**: move from Tamas → Rajas → Sattva. Then transcend all "
            "   three — BG 14:26 teaches that devotion (bhakti) transcends the gunas.\n"
            "4. **Weekly check-in**: rate the past week — predominantly S, R, or T? "
            "   What would you change?"
        ),
        "parent_note_md": (
            "The Guna framework (BG Chapters 14, 17, 18) is one of the most practically "
            "applicable models in all of philosophy. Unlike moral frameworks that only say "
            "'do this, don't do that,' the Gunas explain WHY we do what we do — and "
            "give a map for transformation. BG 14:6: *'Sattva, being pure, is "
            "illuminating and free from disease — it binds through attachment to "
            "happiness and knowledge.'* Even Sattva is a guna to be transcended — "
            "the Gunatita (one who has gone beyond the gunas) is the ideal. Teaching "
            "the Gunas at 13 gives teenagers a self-assessment framework they can use "
            "every day — far more nuanced than 'good vs bad' binary thinking."
        ),
    },
    {
        "slug": "hindu-gita-chapters-key",
        "title": "Bhagavad Gita — Chapters 3, 4, and 12 (Karma, Jnana, Bhakti Yoga)",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Chapter 3 — Karma Yoga** (the yoga of selfless action):\n"
            "   - BG 3:19: *'Therefore always perform your duty without attachment — "
            "     by doing so a person attains the Supreme.'\n"
            "   - Key concept: Nishkama Karma — act without craving the fruit.\n"
            "   - Practise: this week, do one act of service with zero expectation.\n\n"
            "2. **Chapter 4 — Jnana Yoga** (the yoga of knowledge):\n"
            "   - BG 4:7–8: 'Whenever dharma declines, I descend — to protect the "
            "     good and destroy evil and to re-establish dharma, age after age.'\n"
            "   - Key concept: yajna (sacrifice) of all actions to God.\n"
            "   - Practise: identify one action this week you can do as a yajna — "
            "     fully, without distraction, as an offering.\n\n"
            "3. **Chapter 12 — Bhakti Yoga** (the yoga of devotion):\n"
            "   - BG 12:13–14: the characteristics of the ideal devotee — "
            "     *'One who hates no creature, who is friendly and compassionate "
            "     to all, free from attachment and ego, equal in pleasure and pain, "
            "     patient, always content, self-controlled — such a devotee is "
            "     dear to Me.'\n"
            "   - Practise: for one day, try to be this person. At night, assess."
        ),
        "parent_note_md": (
            "Chapters 3, 4, and 12 form the practical heart of the Bhagavad Gita. "
            "Chapter 3 answers: what should I do? (Act without attachment.) Chapter 4 "
            "answers: how should I understand action? (As yajna — sacrifice to God.) "
            "Chapter 12 answers: who is the ideal person? (The steady devotee, "
            "friendly to all, free from ego.) Together they give a teenager a complete "
            "daily ethics: what to do, how to do it, and who to become. BG 12:13–19 "
            "is a portrait of the ideal human being — a checklist that can be revisited "
            "daily as a mirror of self-improvement rather than a standard to feel guilty about."
        ),
    },
    {
        "slug": "hindu-brahmacharya-student",
        "title": "Brahmacharya — Self-Discipline and Energy Management for Students",
        "category": "social",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The meaning**: Brahmacharya = Brahman + charya (moving toward). "
            "   It is the movement of one's life energy (prana/ojas) toward Brahman. "
            "   At the student stage (Brahmacharya Ashrama), this means channelling "
            "   vital energy into learning, growth, and self-development.\n"
            "2. **Practical Brahmacharya for students (not monasticism)**:\n"
            "   - Waking before 6am — the Brahma Muhurta (3am–6am) is the ideal "
            "     study and meditation window.\n"
            "   - Avoiding excessive entertainment, social media, and idle talk.\n"
            "   - Maintaining modesty in dress and conduct.\n"
            "   - Controlling the impulse to gossip, to react impulsively, or to "
            "     seek constant sensory stimulation.\n"
            "   - Directing creative energy into studies, service, and skill-building.\n"
            "3. **The ojas concept**: Ayurveda teaches that conserved vital energy "
            "   (ojas) builds intelligence, radiance, and spiritual strength. "
            "   Dispersed energy (through overindulgence in any direction) diminishes it.\n"
            "4. **One-week experiment**: wake at 6am every day. Record what changes."
        ),
        "parent_note_md": (
            "Brahmacharya is the first Ashrama — the student stage — prescribed in "
            "the Dharmashastra texts (Manusmriti, Yajnavalkya Smriti). The student "
            "was expected to live in the guru's house, serve, study, and practice "
            "complete self-regulation. In modern life, the principle applies without "
            "the monastic setting: a teenager's core dharma is learning — academic, "
            "moral, and spiritual. Brahmacharya means directing life energy toward "
            "that purpose. Patanjali's Yoga Sutras (2:38) state: *'From Brahmacharya, "
            "great vitality is obtained.'* This is the Hindu answer to the modern "
            "problem of adolescent energy dissipated through screens and distraction."
        ),
    },
    {
        "slug": "hindu-guru-purnima",
        "title": "Guru Purnima — Honouring the Lineage of Teachers",
        "category": "social",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is Guru Purnima**: the full moon of Ashadha (June–July). "
            "   Named for Vyasa — the sage who compiled the Vedas, wrote the "
            "   Mahabharata, and the 18 Puranas. It is the day to honour all "
            "   teachers across all traditions.\n"
            "2. **The meaning of Guru** (गुरु):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > गुरुर्ब्रह्मा गुरुर्विष्णुर्गुरुर्देवो महेश्वरः ।\n"
            "   > गुरुः साक्षात् परब्रह्म तस्मै श्री गुरवे नमः ।।\n\n"
            "   **Meaning:** 'The Guru is Brahma, Vishnu, and Shiva — the Guru is "
            "   the very supreme Brahman. To that Guru I bow.'\n"
            "   *Gu* = darkness, *Ru* = remover — the Guru removes the darkness of ignorance.\n\n"
            "3. **The practice on Guru Purnima**:\n"
            "   - Visit or write to one teacher who changed your life and express genuine gratitude.\n"
            "   - Do pada puja (washing the feet) for parents or a respected elder.\n"
            "   - Commit to one new learning practice for the year ahead.\n"
            "4. **Reflect**: 'Who are the three most important teachers in my life? "
            "   Have I thanked them?'"
        ),
        "parent_note_md": (
            "The Guru-Shishya (teacher-student) relationship is the backbone of the "
            "entire Hindu knowledge tradition — the Vedas were transmitted orally for "
            "5,000 years from Guru to Shishya without being written. The Taittiriya "
            "Upanishad (1.11.2) declares: *'Ācāryadevo bhava'* — 'Let your teacher be "
            "your God.' The Katha Upanishad's very first verse shows Nachiketa refusing "
            "to accept a lazy answer from Yama — because a true shishya demands genuine "
            "knowledge. Guru Purnima teaches adolescents that knowledge is not a "
            "commodity to be downloaded — it is a sacred transmission that requires "
            "humility, relationship, and gratitude. In an age of Google, this is "
            "precisely the lesson most needed."
        ),
    },
    {
        "slug": "hindu-mahamrityunjaya-mantra",
        "title": "Mahamrityunjaya Mantra — Full Text, Meaning, and Daily Practice",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the full mantra** (Rigveda 7.59.12):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम् ।\n"
            "   > उर्वारुकमिव बन्धनान् मृत्योर्मुक्षीय माऽमृतात् ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Oṃ tryambakaṃ yajāmahe sugandhiṃ puṣṭivardhanam |*\n"
            "   > *Urvārukamiva bandhanān mṛtyormukṣīya māmṛtāt ||*\n\n"
            "   **Meaning:** 'We worship the three-eyed one (Shiva/Tryambaka) who is "
            "   fragrant and nourishes all beings. May He liberate us from the bondage "
            "   of death just as a ripened cucumber is severed from its vine — "
            "   granting immortality, not death.'\n\n"
            "2. **Chant 108 times** (one full mala) on Mondays (Shiva's day) and "
            "   during illness, fear, or crisis.\n"
            "3. **The meaning unpacked**: the cucumber analogy — we are not cut "
            "   violently; we fall away naturally when ripe. Death is liberation, "
            "   not tragedy, for the one who has prepared.\n"
            "4. **Use it for others**: chant it for a family member who is ill — "
            "   the Mahamrityunjaya is Hinduism's universal prayer of healing."
        ),
        "parent_note_md": (
            "The Mahamrityunjaya Mantra is from the Rigveda (7.59.12) and is one of "
            "the most ancient mantras still in active daily use. It appears also in "
            "the Yajurveda (3.60) and the Shiva Purana. 'Maha' = great, 'Mrityu' = "
            "death, 'Jaya' = victory — the great mantra that conquers death. "
            "Mrityunjaya is one of Shiva's names — the one who has defeated death. "
            "For adolescents who may face illness in loved ones, their own mortality "
            "questions, or existential anxiety, this mantra offers a complete theological "
            "response: death is not the enemy — attachment to the temporary is. The "
            "mantra asks not for endless life but for liberation (muksha) — the ripened "
            "soul released naturally from the vine of embodiment."
        ),
    },
    {
        "slug": "hindu-daily-meditation",
        "title": "Meditation — Establish a Daily Silent Practice (Dhyana)",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with 10 minutes daily** — same time, same place, every day. "
            "   Morning (Brahma Muhurta, 5–6am) is ideal; after school works too.\n"
            "2. **The technique — Trataka (candle gazing)**:\n"
            "   - Place a lit diya at eye level, 60–90 cm away.\n"
            "   - Gaze at the flame without blinking for as long as comfortable.\n"
            "   - When eyes water, close them and visualise the flame at the point "
            "     between the eyebrows (Ajna chakra).\n"
            "   - This develops single-pointed concentration (Dharana) — the sixth "
            "     limb of Patanjali's Ashtanga Yoga.\n"
            "3. **The mantra method (Japa Dhyana)**:\n"
            "   - Sit still, close eyes, and silently repeat your chosen mantra "
            "     (Gayatri, OM, Mahamrityunjaya, or any name of God).\n"
            "   - When the mind wanders — note it, do not judge it — and gently "
            "     return to the mantra.\n"
            "4. **Build over 90 days**: 10 min → 15 min → 20 min.\n"
            "5. **Track**: after each session note one word describing the quality "
            "   of mind — restless, dull, clear, peaceful, distracted."
        ),
        "parent_note_md": (
            "Patanjali defines meditation (Dhyana) in Yoga Sutras 3:2: "
            "*'Tatra pratyayaikatānatā dhyānam'* — "
            "'A continuous flow of the same cognition toward the object of focus — "
            "that is meditation.' It is the seventh of the eight limbs, following "
            "Dharana (concentration) and preceding Samadhi (absorption). "
            "The Mandukya Upanishad teaches that the true Self is discovered in "
            "the silent space beyond thought. Neuroscience confirms: regular "
            "meditation measurably thickens the prefrontal cortex, reduces amygdala "
            "reactivity, and improves focus — benefits that are particularly powerful "
            "when established before age 16. Adolescents who meditate navigate stress, "
            "social pressure, and identity formation with significantly greater stability."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 14
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-ashtanga-yoga",
        "title": "Patanjali's Ashtanga Yoga — The Eight Limbs of the Yoga Path",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn all eight limbs in Sanskrit and meaning**:\n"
            "   - **Yama** (restraints): Ahimsa, Satya, Asteya, Brahmacharya, Aparigraha\n"
            "   - **Niyama** (observances): Saucha, Santosha, Tapas, Svadhyaya, Ishvara Pranidhana\n"
            "   - **Asana**: steady, comfortable posture\n"
            "   - **Pranayama**: breath regulation\n"
            "   - **Pratyahara**: withdrawal of senses from external objects\n"
            "   - **Dharana**: concentration — fixing the mind on one point\n"
            "   - **Dhyana**: meditation — sustained flow of attention\n"
            "   - **Samadhi**: absorption — the mind merges with its object\n"
            "2. **Assess your current practice**: which limbs are you already living? "
            "   Which are weakest? Make a personal map.\n"
            "3. **Pick one Yama and one Niyama** to actively develop this month.\n"
            "4. **Key shloka** (Yoga Sutras 2:29):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > यमनियमासनप्राणायामप्रत्याहारधारणाध्यानसमाधयोऽष्टावङ्गानि ।\n\n"
            "   **Meaning:** 'The eight limbs are: Yama, Niyama, Asana, Pranayama, "
            "   Pratyahara, Dharana, Dhyana, Samadhi.'"
        ),
        "parent_note_md": (
            "Patanjali's Yoga Sutras (compiled c. 400 CE) are the systematic codification "
            "of yoga philosophy — 196 aphorisms organising the entire spiritual path. "
            "The first two limbs (Yama and Niyama) are the ethical foundation: without "
            "them, the inner limbs cannot function properly — like trying to build a "
            "house without a foundation. The Yoga Sutras make clear that yoga is not "
            "primarily a physical practice (Asana is only three of 196 sutras). "
            "Adolescents who understand the full eight-limb framework understand that "
            "the yoga class they may attend is only one-eighth of the path — and that "
            "how they speak, what they eat, and how they treat others are also yoga."
        ),
    },
    {
        "slug": "hindu-upanishads-intro",
        "title": "Upanishads — Introduction to the Philosophical Heart of Hinduism",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What are the Upanishads**: 108 philosophical texts at the end of "
            "   the Vedas (Vedanta = end of the Vedas). They contain the direct "
            "   transmission of the deepest truths from Guru to Shishya.\n"
            "2. **The four Mahavakyas** (Great Sayings) — one from each Veda:\n\n"
            "   | Mahavakya | Meaning | Source |\n"
            "   |-----------|---------|--------|\n"
            "   | *Prajnanam Brahma* | Consciousness is Brahman | Aitareya Upanishad |\n"
            "   | *Aham Brahmasmi* | I am Brahman | Brihadaranyaka Upanishad |\n"
            "   | *Tat tvam asi* | Thou art That | Chandogya Upanishad |\n"
            "   | *Ayam Atma Brahma* | This Self is Brahman | Mandukya Upanishad |\n\n"
            "3. **Read the Kena Upanishad** (only 34 verses) — the opening question: "
            "*'By whom is the mind directed? By whom is breath impelled? Who directs "
            "the eye and ear?'* — and the surprising answer: not an external God, but "
            "the pure awareness that makes all experience possible.\n"
            "4. **One-week practice**: each morning, spend 5 minutes asking 'Neti neti' "
            "   (not this, not this) — I am not my body, not my thoughts, not my emotions. "
            "   What remains?"
        ),
        "parent_note_md": (
            "The Upanishads are the crown of the Vedic tradition — their teachings "
            "form the basis of Vedanta, which Swami Vivekananda brought to the world "
            "stage in 1893. The four Mahavakyas are their distilled essence: the "
            "individual self (Atman) and the universal Self (Brahman) are not two "
            "different things — they are one. Adi Shankara's Advaita Vedanta, Ramanuja's "
            "Vishishtadvaita, and Madhva's Dvaita all rest on Upanishadic foundations — "
            "they differ only in *how* they interpret the relationship between Atman "
            "and Brahman. For a 14-year-old asking 'Who am I?', there is no more "
            "profound answer anywhere in the world's philosophical literature."
        ),
    },
    {
        "slug": "hindu-social-media-ethics",
        "title": "Social Media Through Hindu Values — Ahimsa, Satya, and Maya Online",
        "category": "digital",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Apply the five Yamas to online behaviour**:\n"
            "   - **Ahimsa**: do my words online cause harm? Even passive likes of "
            "     cruel content are a form of himsa.\n"
            "   - **Satya**: am I presenting a true version of myself? Or a curated "
            "     performance?\n"
            "   - **Asteya**: am I giving proper credit? Am I taking others' content "
            "     without acknowledgement?\n"
            "   - **Brahmacharya**: how many hours does my phone drain from study, "
            "     sleep, and real relationships?\n"
            "   - **Aparigraha**: am I addicted to accumulating followers, likes, "
            "     and notifications? This is a subtle form of greed.\n"
            "2. **The Maya test**: before posting anything, ask — 'Is this real or "
            "   am I feeding the illusion? Is this sattvic or rajasic or tamasic?'\n"
            "3. **The 24-hour test**: before sending an angry message, wait 24 hours. "
            "   BG 2:63 — anger leads to delusion leads to destruction.\n"
            "4. **Digital fasting**: practise one screen-free day per week — "
            "   apply the Ekadashi principle to digital consumption."
        ),
        "parent_note_md": (
            "The Yamas of Patanjali's Yoga Sutras (2:30) are defined as 'universal "
            "great vows' — applicable at all times, in all places, to all beings. "
            "They were articulated 2,000 years before social media but describe its "
            "ethical challenges with uncanny precision. The BG 2:63 chain of "
            "desire → anger → delusion → destruction plays out in viral social media "
            "pile-ons daily. Researchers have documented that social media use in "
            "adolescents correlates with increased anxiety and comparison-based "
            "unhappiness — exactly what the Gita predicts from constant sense-stimulation "
            "and attachment to results (likes). Teaching the Yamas as a social media "
            "framework gives teenagers a principled, proactive ethics — not just rules."
        ),
    },
    {
        "slug": "hindu-asteya-aparigraha-modern",
        "title": "Asteya and Aparigraha — Non-Stealing and Non-Greed in Modern Life",
        "category": "financial",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Asteya** (अस्तेय) = non-stealing. From Yoga Sutras 2:37:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > अस्तेयप्रतिष्ठायां सर्वरत्नोपस्थानम् ।\n\n"
            "   **Meaning:** 'When one is firmly established in non-stealing, "
            "   all jewels present themselves.'\n\n"
            "   **Modern forms of stealing to examine**:\n"
            "   - Plagiarising in schoolwork\n"
            "   - Using pirated software, music, or films\n"
            "   - Taking credit for others' ideas\n"
            "   - Wasting others' time (time is their most precious resource)\n\n"
            "2. **Aparigraha** (अपरिग्रह) = non-possessiveness. From Yoga Sutras 2:39:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > अपरिग्रहस्थैर्ये जन्मकथन्तासम्बोधः ।\n\n"
            "   **Meaning:** 'When established in non-possessiveness, knowledge of "
            "   one's past and future lives arises.'\n\n"
            "   **Practical application**: own fewer things, but chosen well. "
            "   Give away something unused every month.\n"
            "3. **Reflection**: make a list of 10 things you own that you don't need. "
            "   Who could benefit from them?"
        ),
        "parent_note_md": (
            "Asteya and Aparigraha are two of the five Yamas — the ethical foundation "
            "of the yoga path. In a consumer culture designed around manufactured "
            "desire, both are radical counter-values. The Yoga Sutras' promise for "
            "Asteya is extraordinary: when you stop taking what isn't yours (in all "
            "its subtle forms), abundance flows to you — because the universe trusts "
            "you with more. Aparigraha was the principle that Gandhi used to reduce "
            "his worldly possessions to a spinning wheel, a bowl, and a pair of sandals "
            "— and found that the less he owned, the freer and more powerful he became. "
            "Teaching this to 14-year-olds in consumer culture is one of the most "
            "counter-cultural and valuable things a Hindu parent can do."
        ),
    },
    {
        "slug": "hindu-pilgrimage-concept",
        "title": "Pilgrimage — The Char Dham Concept and the Inner Yatra",
        "category": "navigation",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the four Char Dham** (sacred to all Hindus):\n"
            "   - **Badrinath** (North, Uttarakhand) — Vishnu; at the source of the Ganga\n"
            "   - **Dwarka** (West, Gujarat) — Krishna's ancient kingdom\n"
            "   - **Puri** (East, Odisha) — Jagannath (Vishnu); the Rath Yatra chariot\n"
            "   - **Rameswaram** (South, Tamil Nadu) — Shiva; where Ram built the bridge\n"
            "2. **Why pilgrimage?** Pilgrimage (Tirtha Yatra) is physically going to a "
            "   place where the divine has been especially present — the concentrated "
            "   spiritual energy (shakti) of a sacred site is real and palpable.\n"
            "3. **Attend one local pilgrimage or yatra this year** — a nearby mandir's "
            "   annual chariot festival, a temple fair, or a day trip to a nearby "
            "   sacred site. Experience it fully — no phones, full presence.\n"
            "4. **The inner pilgrimage**: Adi Shankara taught that the greatest Tirtha "
            "   is within — the pure Atman is the most sacred of all places. "
            "   Pilgrimage prepares us to find that inner sanctum.\n"
            "5. **Plan a Char Dham yatra** as a family life goal — even if 10 years away."
        ),
        "parent_note_md": (
            "The concept of Tirtha (sacred crossing) is foundational to Hindu geography — "
            "India's entire landscape is a map of the divine. Adi Shankara (8th century) "
            "established the four Char Dham at the four cardinal points of India, "
            "unifying all Hindu traditions in a single pilgrimage circuit. The Mahabharata's "
            "Tirtha Yatra Parva (Vana Parva) lists hundreds of sacred sites and their "
            "benefits. Modern research on pilgrimage finds that the combination of "
            "physical hardship, communal purpose, and sacred intention produces "
            "measurable psychological transformation — exactly what rites of passage "
            "are designed to do. For adolescents, a pilgrimage is one of the few "
            "remaining genuine initiation experiences."
        ),
    },
    {
        "slug": "hindu-vivekananda-youth",
        "title": "Swami Vivekananda — His Life and Message for Young Hindus",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read a short biography** of Vivekananda — particularly:\n"
            "   - His troubled youth and questions about God (he went to Sri Ramakrishna "
            "     and asked: 'Have you seen God?')\n"
            "   - His transformation under Ramakrishna's guidance\n"
            "   - The Chicago Address (1893) — the speech that introduced Hinduism "
            "     to the Western world: *'Sisters and brothers of America…'*\n"
            "2. **Study five key teachings**:\n"
            "   - *'Arise, awake, stop not till the goal is reached'* (Katha Upanishad)\n"
            "   - *'You are not sinners — you are children of immortal bliss!'*\n"
            "   - *'Strength is life; weakness is death'*\n"
            "   - *'The goal of mankind is knowledge — not enjoyment'*\n"
            "   - *'Serve the poor as Narayana — Daridra Narayana seva'*\n"
            "3. **Apply one teaching this week**: pick one of the five — write one "
            "   paragraph on how it applies to your life right now.\n"
            "4. **Celebrate National Youth Day**: January 12 — Vivekananda's birthday "
            "   — as a day of reading, reflection, and renewed commitment."
        ),
        "parent_note_md": (
            "Swami Vivekananda (1863–1902) is arguably Hinduism's most effective "
            "communicator for the modern age. He took the Advaita Vedanta of his "
            "guru Ramakrishna and expressed it in a language that spoke equally to "
            "Western audiences and Indian youth. His core message was radical "
            "self-belief rooted in the Atman: you are not sinners needing salvation — "
            "you are already divine, needing only to realise it. The Government of "
            "India observes January 12 as National Youth Day in his honour. "
            "For adolescents struggling with self-image, Vivekananda's lion-roar — "
            "'You are children of immortal bliss!' — is one of the most empowering "
            "messages in the entire Hindu tradition."
        ),
    },
    {
        "slug": "hindu-ishta-devata",
        "title": "Ishta Devata — Choosing Your Personal Deity and Deepening Bhakti",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is Ishta Devata**: 'the chosen deity' — the one form of God "
            "   that speaks most directly to your heart and temperament. Different "
            "   deities represent different paths to the same ultimate reality.\n"
            "2. **Explore the major deities** and their gifts:\n"
            "   - **Ganesha**: wisdom, removing obstacles — for those who value "
            "     intellect and new beginnings\n"
            "   - **Saraswati**: knowledge, arts — for students and creative souls\n"
            "   - **Lakshmi**: abundance and grace — for those seeking prosperity with "
            "     gratitude\n"
            "   - **Krishna**: love, joy, playfulness, the Gita — for devotional hearts\n"
            "   - **Rama**: integrity, duty, sacrifice — for those drawn to dharmic living\n"
            "   - **Shiva**: transformation, stillness, destruction of ego — for "
            "     meditators and seekers\n"
            "   - **Durga/Kali**: fierce protection, fearlessness — for those who need "
            "     strength and courage\n"
            "3. **Choose one** not by tradition but by genuine resonance. Spend a week "
            "   reading their stories, learning their mantra, placing their image at "
            "   your personal altar.\n"
            "4. **Deepen**: learn one shloka and one quality of your Ishta Devata and "
            "   embody that quality this month."
        ),
        "parent_note_md": (
            "The Ishta Devata concept is one of Hinduism's greatest gifts to spiritual "
            "development — it recognises that people are different and need different "
            "forms of the divine to enter the path. The Gita (7:21) says: *'Whatever "
            "form any devotee desires to worship with faith — I make that very faith "
            "of his unwavering.'* Sri Ramakrishna worshipped Kali and reached samadhi; "
            "he also had deep experiences of Rama, Krishna, and Christ — all through "
            "their specific forms. The choice of Ishta Devata at 14 is not final — "
            "it is a beginning. But having a personal deity one speaks to, whose "
            "stories one knows, and whose qualities one aspires to develop, gives the "
            "adolescent's spiritual life a concrete, intimate, and emotionally resonant "
            "centre."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 15
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-vedanta-advaita",
        "title": "Vedanta — Advaita: Brahman, Atman, Maya, and Liberation",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The core teaching of Advaita Vedanta** (Adi Shankara, 8th century):\n"
            "   - There is only ONE reality — **Brahman** (pure consciousness, infinite, "
            "     formless, unchanging)\n"
            "   - The individual self (**Atman**) appears separate but is identical "
            "     with Brahman: *Aham Brahmasmi* — 'I am Brahman'\n"
            "   - The appearance of multiplicity is **Maya** (the power of illusion)\n"
            "   - **Moksha** (liberation) = realising this identity — the drop "
            "     merging back into the ocean\n"
            "2. **Three schools to compare** (spend one week on each):\n"
            "   - **Advaita** (Shankara): Atman and Brahman are one; the world is Maya\n"
            "   - **Vishishtadvaita** (Ramanuja): Atman is real but part of Brahman, "
            "     like a body's cells to the body\n"
            "   - **Dvaita** (Madhva): Atman and Brahman are eternally distinct; "
            "     devotion to God bridges them\n"
            "3. **Read Vivekachudamani** (Crest Jewel of Discrimination) "
            "   by Shankara — just the first 20 verses to start.\n"
            "4. **The practical question**: 'If my true nature is Brahman — why do I "
            "   still feel small, afraid, and limited? What would it mean to live "
            "   from that truth today?'"
        ),
        "parent_note_md": (
            "Advaita Vedanta is India's most influential philosophical system — Shankara "
            "synthesised the entire Upanishadic tradition into a coherent non-dualistic "
            "framework that has shaped Hindu thought for 1,200 years. The Mandukya "
            "Upanishad (verse 2) states: *'Sarvam hyetad brahma'* — 'All of this is "
            "indeed Brahman.' The Chandogya Upanishad (6.8.7) repeats nine times: "
            "*'Tat tvam asi'* — 'Thou art That.' For a 15-year-old grappling with "
            "identity, the Vedantic answer is transformative: your deepest identity is "
            "not your name, body, culture, or achievements — it is the infinite, "
            "unchanging awareness that witnesses all of those. This is the most "
            "radical and liberating idea in human philosophical history."
        ),
    },
    {
        "slug": "hindu-four-yoga-paths",
        "title": "Four Yoga Paths — Bhakti, Karma, Jnana, Raja: Find Your Way",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the four paths** — each suited to a different temperament:\n"
            "   - **Bhakti Yoga** (path of devotion): for the emotional, loving "
            "     heart — puja, bhajan, kirtan, prayer, surrender to God. "
            "     *Key text: Bhagavata Purana, BG Chapter 12*\n"
            "   - **Karma Yoga** (path of action): for the active, practical person — "
            "     selfless service, work as worship, nishkama karma. "
            "     *Key text: BG Chapters 3–5*\n"
            "   - **Jnana Yoga** (path of knowledge): for the intellectual, inquiring "
            "     mind — inquiry into the nature of self and reality, Vedanta study. "
            "     *Key text: Upanishads, BG Chapter 4*\n"
            "   - **Raja Yoga** (path of meditation): for the disciplined, introspective "
            "     person — Patanjali's eight-limb path, meditation, samadhi. "
            "     *Key text: Yoga Sutras of Patanjali*\n"
            "2. **Self-assessment**: which path resonates most with you right now? "
            "   Which do you find most difficult? Both answers are important.\n"
            "3. **The key insight**: all four paths lead to the same summit — "
            "   union with Brahman/Ishvara. You may enter from any gate.\n"
            "4. **This week**: practise one act from each of the four paths and "
            "   compare how each one felt in your body and mind."
        ),
        "parent_note_md": (
            "Swami Vivekananda's four-volume commentary (Raja Yoga, Jnana Yoga, "
            "Karma Yoga, Bhakti Yoga) is the definitive modern exposition of these "
            "four paths. The BG itself presents all four — Chapters 3–5 for Karma, "
            "Chapter 4 for Jnana, Chapter 12 for Bhakti, and Chapters 6 and 18 for "
            "Raja. Sri Ramakrishna said: 'All rivers lead to the same ocean.' The "
            "genius of Hinduism is that it provides multiple valid entry points — "
            "one person's path through devotional singing (Bhakti) is as valid as "
            "another's through philosophical inquiry (Jnana). At 15, adolescents can "
            "begin to understand their own spiritual temperament and choose the path "
            "that will carry them deepest."
        ),
    },
    {
        "slug": "hindu-gita-complete-reading",
        "title": "Bhagavad Gita — Complete Reading of All 18 Chapters With Reflection",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read one chapter per day** over 18 days — or 2 chapters per week "
            "   over 9 weeks, with discussion.\n"
            "2. **Keep a Gita journal**: after each chapter, write:\n"
            "   - The one verse that struck you most\n"
            "   - What it means to you in your current life\n"
            "   - One action you will take this week based on it\n"
            "3. **Chapter summary map** to guide discussion:\n"
            "   - Ch 1–2: Arjuna's crisis; Atman teaching; BG 2:47\n"
            "   - Ch 3–5: Karma Yoga; nishkama karma; yajna\n"
            "   - Ch 6: Dhyana Yoga; meditation\n"
            "   - Ch 7–9: Knowledge of God; devotion; BG 9:22\n"
            "   - Ch 10–11: God's manifestations; Vishvarupa (cosmic form)\n"
            "   - Ch 12: Bhakti Yoga; qualities of a devotee\n"
            "   - Ch 13–15: Kshetra-Kshetrajna; three Gunas; the Ashvattha tree\n"
            "   - Ch 16–17: Divine vs demonic qualities; three types of faith\n"
            "   - Ch 18: Synthesis — surrender and liberation; BG 18:66\n"
            "4. **Closing shloka** (BG 18:66):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज ।\n"
            "   > अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः ।।\n\n"
            "   **Meaning:** 'Abandon all varieties of dharma and simply surrender "
            "   unto Me alone. I shall liberate you from all sinful reactions — "
            "   do not fear.'"
        ),
        "parent_note_md": (
            "The Bhagavad Gita has been called 'the crown of Hindu scripture' and "
            "'the greatest spiritual document the world has known' (Aldous Huxley). "
            "Reading it in full at 15 — after years of encountering its individual "
            "verses through practice — is like seeing the full painting after years "
            "of studying brushstrokes. BG 18:66 is the Gita's ultimate verse: "
            "all the dharmas, all the paths, all the practices ultimately arrive "
            "at one thing — surrender to the divine. Not passive resignation but "
            "active trust: 'I have done my best. I offer the rest to You.' "
            "Adolescents who complete a full Gita reading have a philosophical "
            "foundation that most adults never acquire."
        ),
    },
    {
        "slug": "hindu-bhumi-mata-environment",
        "title": "Bhumi Mata — Environmental Dharma and Earth as Sacred Mother",
        "category": "social",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The foundational shloka** from Atharva Veda (12.1.12):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > माता भूमिः पुत्रोऽहं पृथिव्याः ।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Mātā bhūmiḥ putro'haṃ pṛthivyāḥ |*\n\n"
            "   **Meaning:** 'The Earth is my mother; I am her son/daughter.'\n\n"
            "2. **Apply in daily life**:\n"
            "   - Walk barefoot on earth or grass once a week — this is "
            "     Bhumi Pranam (bowing to Mother Earth)\n"
            "   - Plant at least one tree or plant this year\n"
            "   - Reduce single-use plastic — this is a modern form of himsa "
            "     against Bhumi Mata\n"
            "   - Celebrate Pongal/Makar Sankranti as a thanksgiving to the Earth\n"
            "3. **Discuss**: Hindu temples, rivers (Ganga, Yamuna, Saraswati), "
            "   mountains (Himavan), forests — all were personified and worshipped "
            "   because they were seen as manifestations of the divine. "
            "   What would our relationship with nature look like if we genuinely "
            "   believed this today?\n"
            "4. **Community action**: join or organise one local environmental "
            "   clean-up, tree-planting, or river-care initiative."
        ),
        "parent_note_md": (
            "The Atharva Veda's Bhumi Sukta (Earth Hymn, 12.1) is the world's oldest "
            "environmental declaration — 63 verses addressed to the Earth as a living, "
            "sacred being. The Rig Veda opens with Agni (Fire) and contains hymns to "
            "Vayu (Wind), Varuna (Ocean), Indra (Rain), Surya (Sun) — all natural "
            "forces treated as divine persons. Hinduism's theological framework is "
            "inherently ecological: if God pervades all of nature, destroying nature "
            "is destroying God. This is the deepest philosophical foundation for "
            "environmental activism — not legal obligation or scientific fear but "
            "sacred duty. Adolescents who internalise this understanding become "
            "lifelong stewards of the planet."
        ),
    },
    {
        "slug": "hindu-four-ashrams",
        "title": "Four Ashrams — The Stages of a Complete Hindu Life",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the four Ashrams** (stages of life) from the Dharmashastra:\n"
            "   - **Brahmacharya** (student, birth–25): study, self-discipline, "
            "     serving the teacher, building character\n"
            "   - **Grihastha** (householder, 25–50): marriage, family, career, "
            "     wealth, raising children in dharma — considered the most important "
            "     stage (sustains the other three)\n"
            "   - **Vanaprastha** (forest-dweller, 50–75): gradual withdrawal from "
            "     worldly duties; passing responsibilities to children; more time "
            "     for spiritual practice\n"
            "   - **Sannyasa** (renunciation, 75+): complete withdrawal from worldly "
            "     identity; full focus on Moksha\n"
            "2. **Where you are**: at 15, you are in Brahmacharya Ashrama — the "
            "   stage of building the foundation for everything that follows. "
            "   What you develop now you carry into Grihastha.\n"
            "3. **Interview a grandparent or elder**: 'What do you regret from "
            "   your Brahmacharya stage? What do you wish you had done differently?'\n"
            "4. **Plan your Brahmacharya exit goal**: what kind of person do you "
            "   want to be by age 25?"
        ),
        "parent_note_md": (
            "The Ashrama system is described in the Manusmriti, Yajnavalkya Smriti, "
            "and Vasistha Dharmasutra. It provides a complete life-map — one of "
            "Hinduism's most sophisticated contributions to human self-understanding. "
            "The system recognises that different stages of life have different "
            "legitimate priorities: the student must focus on learning, not wealth; "
            "the householder must create wealth and family, not wander; the elder "
            "must hand over and prepare for liberation. Many modern people live their "
            "entire lives in a confused version of Grihastha, never having fully "
            "completed Brahmacharya and never intentionally preparing for the later "
            "stages. Teaching the Ashrama framework at 15 gives adolescents a "
            "perspective that transforms how they understand their current stage."
        ),
    },
    {
        "slug": "hindu-isha-katha-upanishad",
        "title": "Isha and Katha Upanishad — Study the Most Accessible Upanishads",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Isha Upanishad** (18 verses — the shortest and most complete):\n"
            "   - Opening verse: *'Īśāvāsyam idam sarvaṃ'* — "
            "     'All this — whatever moves in this universe — is pervaded by God.'\n"
            "   - Its teaching: inhabit the world fully AND renounce it — "
            "     not one or the other but both simultaneously.\n"
            "   - Read all 18 verses over one week with translation and commentary.\n"
            "2. **Katha Upanishad** — the dialogue between young Nachiketa and Yama (Death):\n"
            "   - Nachiketa refuses three boons and asks Yama: 'What happens after death?'\n"
            "   - Yama's teaching is the entire Vedanta: the Atman cannot be killed — "
            "     *'Na jāyate mriyate vā kadācit'* (BG 2:20 draws directly from here)\n"
            "   - Read Katha Upanishad Part 1 (Chapters 1–3) in two weeks.\n"
            "3. **Discussion questions**:\n"
            "   - Nachiketa chose the knowledge of death over all riches. What does "
            "     that tell us about what truly matters?\n"
            "   - The Isha Upanishad says live fully AND hold nothing — how?\n"
            "4. **Memorise** Isha Upanishad verse 1 — it takes 5 minutes."
        ),
        "parent_note_md": (
            "The Isha Upanishad opens every printed collection of Upanishads for a "
            "reason — its 18 verses contain the essence of Vedanta in the most "
            "balanced form. Gandhi called it: 'If all the Upanishads were destroyed "
            "and only the Isha Upanishad remained, Hinduism would survive.' "
            "The Katha Upanishad's story of Nachiketa is the purest narrative "
            "expression of Vedanta: a young person (adolescent age!) who refuses "
            "material gifts and demands knowledge of what is truly real. Yama — "
            "Death itself — teaches that the one who knows the Atman fears neither "
            "life nor death. These two texts together give a 15-year-old the "
            "philosophical core of Hinduism in accessible narrative and verse form."
        ),
    },
    {
        "slug": "hindu-grief-impermanence",
        "title": "Grief and Impermanence — The Gita's Teaching on the Immortal Soul",
        "category": "social",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The Gita's central teaching on death** (BG 2:22):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > वासांसि जीर्णानि यथा विहाय नवानि गृह्णाति नरोऽपराणि ।\n"
            "   > तथा शरीराणि विहाय जीर्णान्यन्यानि संयाति नवानि देही ।।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Vāsāṃsi jīrṇāni yathā vihāya navāni gṛhṇāti naro'parāṇi |*\n"
            "   > *Tathā śarīrāṇi vihāya jīrṇānyanyāni saṃyāti navāni dehī ||*\n\n"
            "   **Meaning:** 'Just as a person puts on new garments after discarding "
            "   the worn-out ones, so the soul accepts new material bodies after "
            "   discarding the old and useless ones.'\n\n"
            "2. **Discuss honestly**: 'Have you experienced the death of someone you "
            "   loved? What did you feel? What does the Gita say about what happened "
            "   to their Atman?'\n"
            "3. **The Hindu framework for grief**: grief for the body is natural; "
            "   grief for the Atman is misplaced — the Atman is eternal. We mourn "
            "   the separation, not the destruction of the person.\n"
            "4. **Ritual meaning**: the Antyesti (last rites) and Shraddha ceremonies "
            "   are not superstition — they are the family's final act of seva for "
            "   the departing soul and the survivors' way of processing and honouring."
        ),
        "parent_note_md": (
            "BG 2:22 is the Gita's answer to what every human being fears most: "
            "death, loss, and the suffering of those we love. Krishna does not "
            "minimise Arjuna's grief — he acknowledges it and then gives it a "
            "larger frame. The Katha Upanishad (1.2.19) teaches: *'The wise one "
            "who knows the Self as bodiless within bodies, as unchanging among "
            "changing things — this wise one grieves no more.'* Introducing the "
            "Hindu understanding of death and the Atman at 15 — before a personal "
            "crisis forces the question — gives adolescents an inner resource that "
            "no amount of secular counselling can replicate. It does not remove "
            "grief but transforms its quality — from terror of annihilation to "
            "trust in continuity."
        ),
    },
    # ══════════════════════════════════════════════════════════════════════
    # AGE 16
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "hindu-sarva-dharma-sambhava",
        "title": "Sarva Dharma Sambhava — Honouring All Paths to the Divine",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The principle**: *Sarva Dharma Sambhava* — 'all religions are equally "
            "   valid paths.' This is not relativism — it is the Vedantic insight that "
            "   all sincere paths lead to the same ultimate reality.\n"
            "2. **The Rig Veda foundation** (1.164.46):\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > एकं सद्विप्रा बहुधा वदन्ति ।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Ekaṃ sad viprā bahudhā vadanti |*\n\n"
            "   **Meaning:** 'Truth is one; the wise describe it in many ways.'\n\n"
            "3. **Study one other tradition**: spend two weeks reading about the "
            "   teachings of one other religion (Islam, Christianity, Buddhism, "
            "   Sikhism, Judaism). Find where it overlaps with Hindu teaching.\n"
            "4. **Interfaith dialogue**: if possible, visit a mosque, church, "
            "   gurudwara, or monastery with an adult family member — with genuine "
            "   curiosity, not comparison or criticism.\n"
            "5. **The difference from indifference**: Sarva Dharma does not mean "
            "   'all practices are equal regardless of ethics.' It means sincere "
            "   seeking of truth in any tradition is honoured by God."
        ),
        "parent_note_md": (
            "The Rig Vedic declaration *'Ekaṃ sad viprā bahudhā vadanti'* (1.164.46) "
            "is perhaps the world's oldest statement of religious pluralism — composed "
            "before most of the world's major religions existed. Sri Ramakrishna's "
            "direct spiritual experiments with Christianity and Islam — and his "
            "declaration that he reached samadhi through each — gave this ancient "
            "principle a modern, lived demonstration. Gandhi embodied it politically. "
            "Swami Vivekananda brought it to Chicago. In a world of rising religious "
            "conflict, this distinctively Hindu principle of *Sarva Dharma Sambhava* "
            "is one of humanity's most urgently needed contributions — and its "
            "next generation must carry it with understanding, not merely as a "
            "slogan."
        ),
    },
    {
        "slug": "hindu-loka-sangraha",
        "title": "Loka Sangraha — Service to Society as the Highest Spiritual Practice",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The teaching from BG 3:20**:\n\n"
            "   **Sanskrit (Devanagari):**\n"
            "   > लोकसंग्रहमेवापि सम्पश्यन्कर्तुमर्हसि ।\n\n"
            "   **IAST transliteration:**\n"
            "   > *Lokasaṃgrahamevāpi sampaśyankartumarhasi |*\n\n"
            "   **Meaning:** 'You should perform action — even for the welfare and "
            "   holding together of the world (*loka sangraha*).' Krishna says this "
            "   to Arjuna — even the wise must act to set an example and hold "
            "   society together.\n\n"
            "2. **Identify a real community need** near you: a struggling school, "
            "   an elderly neighbour, a polluted stream, underfed children. "
            "   This is your Karma Yoga field.\n"
            "3. **Commit to 4 hours per month of seva** outside your family — at a "
            "   temple kitchen, tutoring younger students, or environmental work.\n"
            "4. **Leadership through service**: at 16, begin contributing to the "
            "   Hindu community as a leader, not just a participant — lead a bhajan, "
            "   organise a cleanup, teach younger children the Gayatri Mantra.\n"
            "5. **Vivekananda's charge**: 'So long as the millions live in hunger "
            "   and ignorance, I hold every person a traitor who, having been "
            "   educated at their expense, pays not the least attention to them.'"
        ),
        "parent_note_md": (
            "BG 3:20–21 presents Loka Sangraha as the highest motivation for action "
            "after one has transcended personal desire: even the wise must continue "
            "to act for the welfare of the world, because their example sets the "
            "standard. *'Whatever a great person does, others follow — whatever "
            "standard they set, the world follows it'* (BG 3:21). This is why "
            "Swami Vivekananda — who could have remained in peaceful Vedantic "
            "contemplation — instead spent himself completely in service: founding "
            "the Ramakrishna Mission, feeding the poor, establishing hospitals and "
            "schools. At 16, a young Hindu should begin to see themselves as a "
            "potential leader of Loka Sangraha — responsible for the world they "
            "are inheriting."
        ),
    },
    {
        "slug": "hindu-personal-dharma-statement",
        "title": "Personal Dharma Statement — Life Purpose From Hindu Values",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Reflection questions** — journal answers over one week:\n"
            "   - What am I genuinely good at? (This is a gift from God — a hint "
            "     about your Svadharma.)\n"
            "   - What injustice or suffering in the world bothers me most? "
            "     (This is likely your Karma Yoga field.)\n"
            "   - Which of the four Purusharthas most calls to me now — "
            "     Dharma, Artha, Kama, or Moksha?\n"
            "   - What kind of Grihastha (householder) do I want to be?\n"
            "   - What legacy — what change — do I want to leave when I am gone?\n"
            "2. **Draft a personal dharma statement** — a single paragraph "
            "   (max 150 words) that answers: 'Who am I, what am I here to do, "
            "   and how will I do it with dharma?'\n"
            "3. **Ground it in scripture**: include one Gita or Upanishad verse "
            "   that serves as your personal anchor.\n"
            "4. **Review annually**: on your birthday, read it — refine it. "
            "   Dharma evolves as you grow.\n"
            "5. **Share it** with one trusted adult and ask for honest feedback."
        ),
        "parent_note_md": (
            "BG 18:47 states: *'Better is one's own dharma, though imperfectly "
            "performed, than the dharma of another well performed.'* The task of "
            "adolescence is to discover Svadharma — one's own unique dharma — "
            "distinct from one's parents' path, one's culture's expectations, and "
            "one's peers' choices. The Mahabharata's Yaksha asks Yudhishthira: "
            "'What is the greatest wonder?' and he answers: 'Day after day, "
            "countless people die — and those who remain live as though they were "
            "immortal. That is the greatest wonder.' Writing a personal dharma "
            "statement at 16 is the conscious decision to not be that person — to "
            "live with purpose and awareness. This is the culmination of the "
            "entire Brahmacharya Ashrama."
        ),
    },
    {
        "slug": "hindu-gita-chapter-18",
        "title": "Bhagavad Gita Chapter 18 — The Complete Synthesis and Final Surrender",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Chapter 18 carefully** — it is the Gita's grand conclusion, "
            "   weaving together all the previous threads.\n"
            "2. **Five key sections**:\n"
            "   - BG 18:1–12: Renunciation vs. abandonment — the difference between "
            "     leaving action and performing it without attachment\n"
            "   - BG 18:13–18: Five causes of action — body, ego, senses, effort, "
            "     and the divine will\n"
            "   - BG 18:41–44: The Gunas in different vocations — all work is sacred "
            "     when done with dharma\n"
            "   - BG 18:61–66: God in the heart of all beings — the final teaching "
            "     of surrender (BG 18:66)\n"
            "   - BG 18:70–71: The power of hearing the Gita — whoever hears it "
            "     with faith is freed\n"
            "3. **Memorise BG 18:66** (learned earlier in full reading task).\n"
            "4. **The final question**: after all the paths, all the teachings, all "
            "   the philosophy — Krishna's final word is *'surrender to Me alone.'* "
            "   What does surrender mean to you? Is it weakness or ultimate strength?\n"
            "5. **Write a letter to your 30-year-old self** about what the Gita "
            "   means to you today."
        ),
        "parent_note_md": (
            "Chapter 18 of the Bhagavad Gita — Moksha Sannyasa Yoga — is the synthesis "
            "of all 17 preceding chapters. Its final verses are among the most "
            "concentrated in all of Hindu literature. BG 18:65: *'Fix your mind on "
            "Me, be devoted to Me, worship Me, bow to Me — you shall come to Me alone. "
            "I promise you truly — you are dear to Me.'* And BG 18:66 follows: "
            "the complete surrender that releases all other obligations. Adi Shankara, "
            "Ramanuja, and Madhva all wrote their most important commentaries on "
            "this chapter. A 16-year-old who has read all 18 chapters, understood "
            "the framework, and sat with the final teaching has accomplished something "
            "that most adults never do — and carries it for life."
        ),
    },
    {
        "slug": "hindu-japa-meditation",
        "title": "Japa Meditation — Daily Mala Practice With Your Chosen Mantra",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **What is Japa**: the repetitive silent or whispered recitation of "
            "   God's name or a mantra. Japa is the most universal Hindu sadhana — "
            "   practised by saints of every tradition.\n"
            "2. **Get a mala** (rosary): 108 beads — Rudraksha (for Shiva mantras) "
            "   or Tulsi (for Vishnu/Krishna mantras). The 109th bead (Meru) "
            "   marks the start/end — never cross it; reverse direction.\n"
            "3. **Choose your mantra**:\n"
            "   - OM Namah Shivaya (Shiva — for transformation and stillness)\n"
            "   - OM Namo Narayanaya (Vishnu — for preservation and grace)\n"
            "   - OM Namo Bhagavate Vasudevaya (Krishna — for love and wisdom)\n"
            "   - Hare Krishna Hare Rama (Maha Mantra — for Kali Yuga, any tradition)\n"
            "   - Gayatri Mantra (universal — for knowledge and clarity)\n"
            "4. **Daily practice**: one mala (108 repetitions) takes 5–10 minutes. "
            "   Do it at the same time daily — before bed or after morning puja.\n"
            "5. **Build over time**: one mala → three malas → a morning sitting. "
            "   Swami Vivekananda said: 'All power is within you — repeat God's name "
            "   and it will reveal itself.'"
        ),
        "parent_note_md": (
            "Japa is recommended in virtually every Hindu scripture as the most "
            "accessible sadhana for the Kali Yuga. The Vishnu Purana states: "
            "*'In the Kali age the mere utterance of the name of Hari is sufficient "
            "for liberation.'* The Yoga Sutras (1:28–29) teach: *'Its repetition "
            "and meditating on its meaning (Japa and Bhavana) — from this comes "
            "knowledge of the inner consciousness and removal of obstacles.'* "
            "Neurologically, repetitive mantra recitation induces theta brainwave "
            "states associated with deep meditation — even in beginners. The mala "
            "adds a proprioceptive (physical) anchor that helps the wandering mind "
            "return. A 16-year-old who establishes daily Japa has a portable, "
            "always-available meditation practice they can sustain anywhere, forever."
        ),
    },
    {
        "slug": "hindu-philosophical-schools",
        "title": "Six Schools of Hindu Philosophy — Understanding the Darshanas",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the six Darshanas** (philosophical schools) — the six "
            "   authoritative systems of Hindu philosophy (Astika — accepting the Vedas):\n"
            "   - **Samkhya** (Kapila): dualism — Purusha (consciousness) and "
            "     Prakriti (matter) are eternally distinct. The Gunas emerge from Prakriti.\n"
            "   - **Yoga** (Patanjali): methodology for union with Purusha through "
            "     the 8 limbs. Practical application of Samkhya metaphysics.\n"
            "   - **Nyaya** (Gautama): logic and epistemology — how do we know what "
            "     we know? Proof, inference, and valid cognition.\n"
            "   - **Vaisheshika** (Kanada): atomism — the universe is made of atoms "
            "     (anu) of different qualities. India's atomic theory, 6th century BCE.\n"
            "   - **Mimamsa** (Jaimini): examination of Vedic ritual duty — what does "
            "     right action require?\n"
            "   - **Vedanta** (Badarayana): the culmination — the nature of Brahman, "
            "     Atman, and their relationship. The Upanishads as primary source.\n"
            "2. **Spend one week on Vedanta** — compare Advaita, Vishishtadvaita, Dvaita.\n"
            "3. **Key question**: 'Which school best describes how I already think "
            "   about reality?'"
        ),
        "parent_note_md": (
            "The six Darshanas represent one of history's most systematic and rigorous "
            "intellectual achievements — six complete philosophical systems developed "
            "in dialogue with each other over 2,500 years. India's philosophers debated "
            "epistemology (Nyaya), physics (Vaisheshika), metaphysics (Samkhya), "
            "ethics (Mimamsa), practice (Yoga), and ultimate reality (Vedanta) — "
            "centuries before Greek philosophy reached its peak. Will Durant wrote: "
            "'India was the motherland of our race and Sanskrit the mother of Europe's "
            "languages — she was the mother of our philosophy, mother of our mathematics "
            "and ideals.' A 16-year-old who understands even the outline of the six "
            "Darshanas has a philosophical vocabulary richer than most university "
            "humanities graduates."
        ),
    },
    {
        "slug": "hindu-sharing-dharma",
        "title": "Sharing Hindu Wisdom — Explaining Your Faith Clearly and Confidently",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Prepare answers** to the five questions most commonly asked "
            "   about Hinduism:\n"
            "   - 'Do Hindus worship many Gods?' (Answer: One Brahman, many names and "
            "     forms — like one sun seen through different windows)\n"
            "   - 'What do Hindus believe about after death?' (Atman, karma, rebirth, "
            "     and moksha)\n"
            "   - 'What is yoga really?' (The complete path of the Yoga Sutras — "
            "     not just asanas)\n"
            "   - 'Is Hinduism a religion or a philosophy?' (Sanatana Dharma — the "
            "     eternal way — encompasses both and more)\n"
            "   - 'Why do Hindus have so many rituals?' (Rituals are embodied "
            "     philosophy — theology practiced through the body)\n"
            "2. **Practice with a trusted friend or family member** — explain each "
            "   answer in under 2 minutes, without jargon.\n"
            "3. **The Vivekananda model**: confident, warm, rooted in philosophy, "
            "   never defensive or apologetic, deeply respectful of others' paths.\n"
            "4. **Write your personal testimony**: one page — what Hinduism means to "
            "   you personally, what it has given you, and how it shapes your life."
        ),
        "parent_note_md": (
            "Swami Vivekananda's opening words at the 1893 Parliament of the World's "
            "Religions in Chicago — *'Sisters and brothers of America'* — brought the "
            "entire hall to a standing ovation before he had said a single substantive "
            "word. He then presented Hinduism's core — Advaita Vedanta, Sarva Dharma, "
            "the universality of the Atman — in language that was simultaneously "
            "ancient and entirely modern. Every generation of Hindus must be equipped "
            "to do what Vivekananda did: present their tradition with pride, clarity, "
            "intellectual rigour, and profound respect for all other paths. Adolescents "
            "who can articulate their faith — to curious classmates, to antagonistic "
            "questioners, to genuine seekers — carry that tradition forward. Those who "
            "cannot are one generation from losing it."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed Hinduism tasks — all batches: Ages 5–16 (~82 tasks)"

    def handle(self, *args, **options):
        all_envs = list(Environment.objects.all())
        created = updated = 0

        for data in HINDUISM_TASKS:
            tag_name, tag_cat = TAG_FOR_CATEGORY[data["category"]]
            tag, _ = Tag.objects.get_or_create(
                name=tag_name, category=tag_cat
            )

            task, is_new = Task.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title":          data["title"],
                    "how_to_md":      data["how_to_md"],
                    "parent_note_md": data.get("parent_note_md", ""),
                    "safety_md":      data.get("safety_md", ""),
                    "min_age":        data["min_age"],
                    "max_age":        data["max_age"],
                    "religion":       "hinduism",
                    "status":         ReviewStatus.APPROVED,
                },
            )
            task.environments.set(all_envs)
            task.tags.set([tag])

            if is_new:
                created += 1
                self.stdout.write(f"  CREATED  {task.slug}")
            else:
                updated += 1
                self.stdout.write(f"  UPDATED  {task.slug}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone — {created} created, {updated} updated."
            )
        )
