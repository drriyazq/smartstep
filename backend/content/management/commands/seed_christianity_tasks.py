"""Management command: seed Christianity tasks for ages 5–16 (religion='christianity').

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_christianity_tasks

Broadly ecumenical — practical tasks any practicing Christian family (Catholic,
Protestant, Evangelical, Orthodox) would recognise. Each task is grounded in
a specific scripture reference and focuses on practical/behavioural formation.

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

CHRISTIANITY_TASKS = [
    # ══════════════════════════════════════════════════════════════════════
    # AGE 5
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-lords-prayer-age5",
        "title": "Learn the Lord's Prayer by Heart",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read it together** from Matthew 6:9–13 every evening for one week — "
            "slowly, one line at a time.\n"
            "2. **Teach the meaning of each line**: 'Our Father in heaven' — we speak to God "
            "as a loving Father. 'Thy kingdom come' — we ask for God's rule in our lives. "
            "'Give us today our daily bread' — we trust Him for what we need.\n"
            "3. **Say it every night** before bed until fully memorised.\n"
            "4. **Explain that this is Jesus teaching us** — He gave us these exact words when "
            "His disciples asked 'Lord, teach us to pray.'\n"
            "5. **Test gently**: can they say it on their own from memory this week?"
        ),
        "parent_note_md": (
            "Jesus taught this prayer directly to His disciples: *'This, then, is how you should pray: "
            "Our Father in heaven, hallowed be your name…'* (Matthew 6:9, NIV). It is the model prayer "
            "of Christianity — covering worship, trust, petition, forgiveness, and protection in seven lines. "
            "Children who learn it young carry it their whole lives. It is prayed in every Christian "
            "tradition worldwide, making it the most universal starting point for Christian formation."
        ),
    },
    {
        "slug": "christ-grace-before-meals-age5",
        "title": "Say Grace Before Every Meal",
        "category": "social",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pause before every meal** — even snacks. Hold hands as a family if possible.\n"
            "2. **Start with a simple grace**: *'Thank you God for this food. Amen.'* — "
            "build up to a fuller prayer.\n"
            "3. **Take turns leading grace** at the table — the child leads on weekends.\n"
            "4. **Add one thing to be thankful for** beyond the food: 'Thank you for our family, "
            "for school, for sunshine today.'\n"
            "5. **Explain why**: everything we have is a gift from God — saying grace is "
            "acknowledging that."
        ),
        "parent_note_md": (
            "Paul writes: *'For everything God created is good, and nothing is to be rejected if "
            "it is received with thanksgiving, because it is consecrated by the word of God and prayer'* "
            "(1 Timothy 4:4–5, NIV). Jesus Himself gave thanks before meals — before feeding the five "
            "thousand (Matthew 14:19) and at the Last Supper (Matthew 26:26–27). This simple habit "
            "teaches children that gratitude is a Christian posture, not just a mealtime formality."
        ),
    },
    {
        "slug": "christ-god-loves-you-age5",
        "title": "Understand That God Loves You Unconditionally",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read John 3:16 together**: *'For God so loved the world that he gave his one and "
            "only Son, that whoever believes in him shall not perish but have eternal life.'*\n"
            "2. **Replace 'the world' with their name**: 'For God so loved [child's name]…' — "
            "make it personal.\n"
            "3. **Ask**: 'Does God stop loving you when you do something wrong?' — No. His love "
            "is unconditional. Romans 8:38–39 says nothing can separate us from His love.\n"
            "4. **Draw or paint** a picture of what God's love feels like to them.\n"
            "5. **Repeat the verse daily** until memorised — it is the most important verse in "
            "the Bible."
        ),
        "parent_note_md": (
            "John 3:16 is called 'the Gospel in miniature' — it contains the entire message of "
            "Christianity in one sentence. Paul reinforces this: *'Neither death nor life, neither "
            "angels nor demons… nor anything else in all creation will be able to separate us from "
            "the love of God that is in Christ Jesus our Lord'* (Romans 8:38–39, NIV). A child who "
            "knows God's love as a foundational fact has the security to build every other virtue on "
            "top of it. Teach this first."
        ),
    },
    {
        "slug": "christ-say-sorry-forgive-age5",
        "title": "Say Sorry When You're Wrong and Forgive Others",
        "category": "social",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Model saying sorry** yourself as a parent — children learn forgiveness "
            "by watching adults practise it.\n"
            "2. **Teach the three-part apology**: 'I'm sorry for ___. It was wrong because ___. "
            "I will try to ___.'  — not just 'sorry.'\n"
            "3. **Teach forgiving**: when someone says sorry, practise saying 'I forgive you' "
            "out loud — not just 'it's okay.'\n"
            "4. **Role-play** sibling or friend conflict scenarios and practise both sides.\n"
            "5. **Connect to God**: 'When we forgive others, we do what God does for us.'"
        ),
        "parent_note_md": (
            "Paul writes: *'Be kind and compassionate to one another, forgiving each other, "
            "just as in Christ God forgave you'* (Ephesians 4:32, NIV). Jesus links forgiveness "
            "directly to our relationship with God in the Lord's Prayer: *'Forgive us our debts, "
            "as we also have forgiven our debtors'* (Matthew 6:12). Teaching both asking for and "
            "granting forgiveness from age 5 builds the relational foundation of Christian ethics. "
            "It is both a moral habit and a theological reality."
        ),
    },
    {
        "slug": "christ-prayer-posture-age5",
        "title": "Learn to Pray with Focus — Still Body, Quiet Heart",
        "category": "household",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a prayer spot** at home — a corner, a chair, beside the bed. "
            "This becomes 'their prayer place.'\n"
            "2. **Teach stillness**: before praying, take three slow breaths and be still for "
            "10 seconds. 'Be still and know that I am God.'\n"
            "3. **Try different postures**: hands folded, kneeling, eyes closed. Explain that "
            "these help us focus — God hears all prayer.\n"
            "4. **Keep prayers short and honest**: 'Thank you God for… Please help me with… "
            "I'm sorry for…'\n"
            "5. **Pray together daily** — morning or night. Consistency matters more than length."
        ),
        "parent_note_md": (
            "Psalm 46:10 says: *'Be still, and know that I am God.'* Jesus regularly withdrew to "
            "pray alone (Luke 5:16) and taught private, sincere prayer over public performance "
            "(Matthew 6:6). Teaching children that prayer is a real conversation with a real God — "
            "not a performance — is foundational. A consistent prayer habit formed at age 5 is one "
            "of the strongest predictors of adult faith retention."
        ),
    },
    {
        "slug": "christ-jesus-always-with-you-age5",
        "title": "Know That Jesus Is Always With You",
        "category": "cognitive",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Memorise Matthew 28:20**: *'And surely I am with you always, to the very end "
            "of the age.'*\n"
            "2. **Apply it to scary moments**: at night, first day of school, when they feel "
            "alone — remind them of this promise.\n"
            "3. **Teach them to talk to Jesus** in moments of fear or loneliness — not just in "
            "formal prayer but in simple, natural words.\n"
            "4. **Discuss**: Jesus came, died, rose again, and sent the Holy Spirit to be with "
            "us always. We are never alone.\n"
            "5. **Draw a picture**: 'Me and Jesus in my favourite place.'"
        ),
        "parent_note_md": (
            "Matthew 28:20 is the closing promise of the Great Commission — the last recorded words "
            "of Jesus before the ascension. The Psalmist echoes this: *'Where can I go from your "
            "Spirit? Where can I flee from your presence?'* (Psalm 139:7). Children who internalise "
            "God's presence early are less prone to anxiety and more resilient under pressure. "
            "This is not just comfort — it is a doctrinal reality: the Holy Spirit dwells with "
            "and in believers (John 14:17)."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 6
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-psalm23-age6",
        "title": "Memorise Psalm 23 and Know Its Meaning",
        "category": "cognitive",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Psalm 23 aloud together** every day for two weeks.\n"
            "2. **Learn verse by verse** — one verse per day, adding to what was learnt before.\n"
            "3. **Explain each image**: The Lord as Shepherd means He guides, protects, and "
            "provides. 'Green pastures' — rest and nourishment. 'Valley of the shadow of death' "
            "— the most frightening places. 'Your rod and staff comfort me' — His discipline "
            "and guidance are comforting, not scary.\n"
            "4. **Discuss when to use it**: when scared, when sad, when worried — say Psalm 23.\n"
            "5. **Recite it without help** by end of the month."
        ),
        "parent_note_md": (
            "Psalm 23 is arguably the most memorised passage in the Bible — treasured across "
            "every Christian tradition. It teaches children that God is not a distant judge "
            "but a personal shepherd who actively cares for them. It also introduces the concept "
            "of God's presence in suffering: *'Even though I walk through the darkest valley, "
            "I will fear no evil, for you are with me'* (Psalm 23:4, NIV). Children who know "
            "this psalm by heart carry a lifelong resource for every difficult moment."
        ),
    },
    {
        "slug": "christ-ten-commandments-age6",
        "title": "Learn the Ten Commandments and What They Mean",
        "category": "cognitive",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Exodus 20:1–17** together and list the ten commandments simply.\n"
            "2. **Group them**: Commandments 1–4 are about our relationship with God. "
            "Commandments 5–10 are about our relationship with people.\n"
            "3. **Memorise 2 per week** until all ten are known by name.\n"
            "4. **Apply each to daily life**: 'Honour your father and mother' — what does that "
            "look like at breakfast? When asked to do chores?\n"
            "5. **Discuss**: Jesus summarised all ten in two commands — love God, love people "
            "(Matthew 22:37–40)."
        ),
        "parent_note_md": (
            "The Ten Commandments are the moral foundation of both Judaism and Christianity. "
            "Jesus said He came not to abolish but to fulfil the Law (Matthew 5:17). Paul writes "
            "that the commandments are *'summed up in this one command: Love your neighbour as "
            "yourself'* (Romans 13:9, NIV). Teaching children the Decalogue gives them a "
            "concrete moral framework before peer pressure and cultural relativism become "
            "dominant influences. Most major catechisms (Catholic, Lutheran, Reformed) place "
            "the Ten Commandments at the centre of moral formation."
        ),
    },
    {
        "slug": "christ-morning-bedtime-prayer-age6",
        "title": "Pray Every Morning and Before Bed",
        "category": "household",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Morning prayer (2 minutes)**: give thanks for the new day, ask for God's help "
            "and protection. 'Lord, this is Your day. Help me to honour You in everything.'\n"
            "2. **Bedtime prayer (2 minutes)**: review the day — what went well, what went "
            "wrong, anything to say sorry for. Give thanks. Ask God to watch over the family.\n"
            "3. **Use a simple structure**: Thanks → Sorry → Please (TSP).\n"
            "4. **Keep a prayer notebook**: write one prayer request per week and track answers.\n"
            "5. **Pray with them** — don't just supervise. Let them hear your prayers too."
        ),
        "parent_note_md": (
            "David writes: *'In the morning, Lord, you hear my voice; in the morning I lay my "
            "requests before you and wait expectantly'* (Psalm 5:3, NIV). Paul instructs: "
            "*'Pray continually'* (1 Thessalonians 5:17). Bracketing the day with prayer — "
            "morning and night — builds the habit of turning to God first rather than last. "
            "Research on faith transmission consistently shows that parents who pray with their "
            "children (not just for them) are the single strongest factor in adult faith retention."
        ),
    },
    {
        "slug": "christ-be-honest-age6",
        "title": "Always Tell the Truth — Practice Radical Honesty",
        "category": "social",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Proverbs 12:22**: *'The Lord detests lying lips, but he delights in people "
            "who are trustworthy.'*\n"
            "2. **Role-play hard honesty situations**: you broke something, you didn't finish your "
            "homework, you took a biscuit without asking. Practise telling the truth calmly.\n"
            "3. **Reward truth-telling** even when the truth is inconvenient. Never make the "
            "consequence of honesty worse than the consequence of the mistake.\n"
            "4. **Discuss white lies**: even small lies erode trust. 'I'm fine' when you're not "
            "is a habit — practise saying the real thing kindly.\n"
            "5. **Connect to Jesus**: He called Himself 'the Truth' (John 14:6). We follow Him "
            "by living truthfully."
        ),
        "parent_note_md": (
            "Proverbs 12:22 is direct about God's view of lying. Jesus declared: *'I am the way, "
            "the truth, and the life'* (John 14:6) — truth is not just a virtue but a person. "
            "Paul instructs: *'Therefore each of you must put off falsehood and speak truthfully "
            "to your neighbour'* (Ephesians 4:25, NIV). Age 6 is when social lying often begins "
            "— an ideal time to build the honesty habit before it becomes entrenched. "
            "A child who is known as honest is trusted by peers, teachers, and future employers."
        ),
    },
    {
        "slug": "christ-christmas-story-age6",
        "title": "Know the Christmas Story — Why Jesus Came",
        "category": "cognitive",
        "min_age": 6, "max_age": 8,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Luke 2:1–20** together — the full nativity story as Luke records it.\n"
            "2. **Act it out**: assign roles (Mary, Joseph, shepherds, angels) and retell it.\n"
            "3. **Connect to Isaiah 9:6**: God promised a Saviour centuries before — Jesus "
            "was the fulfilment of that promise.\n"
            "4. **Discuss why He came as a baby**: not as a king in a palace — He came humbly, "
            "for ordinary people.\n"
            "5. **Separate the gifts from the meaning**: gifts are fine, but what is Christmas "
            "actually about? Test their understanding."
        ),
        "parent_note_md": (
            "Luke 2 is the most complete account of Jesus's birth. The angel's announcement "
            "states the purpose clearly: *'Today in the town of David a Saviour has been born "
            "to you; he is the Messiah, the Lord'* (Luke 2:11, NIV). Isaiah prophesied this "
            "700 years earlier: *'For to us a child is born, to us a son is given… And he will "
            "be called Wonderful Counsellor, Mighty God, Everlasting Father, Prince of Peace'* "
            "(Isaiah 9:6). Grounding the Christmas story in scripture from age 6 ensures it "
            "remains theological, not just cultural."
        ),
    },
    {
        "slug": "christ-serve-at-home-age6",
        "title": "Serve at Home as Serving God",
        "category": "household",
        "min_age": 6, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Assign regular household tasks**: clearing the table, tidying their room, "
            "helping with laundry, feeding a pet.\n"
            "2. **Before doing them, say together**: *'Whatever you do, do it with all your "
            "heart, as working for the Lord.'* (Colossians 3:23)\n"
            "3. **Reframe service**: sweeping is not a chore — it is an act of worship when "
            "done for God and the family.\n"
            "4. **Help others unprompted**: notice when a parent needs help and do it without "
            "being asked — one such act per week.\n"
            "5. **Discuss Jesus washing feet** (John 13:1–17) — the Son of God served others. "
            "We follow His example."
        ),
        "parent_note_md": (
            "Colossians 3:23–24 says: *'Whatever you do, work at it with all your heart, as "
            "working for the Lord, not for human masters'*. Jesus Himself modelled servant "
            "leadership: *'The Son of Man did not come to be served, but to serve'* (Matthew "
            "20:28, NIV). Teaching children that ordinary household tasks are acts of worship "
            "when done with the right heart reframes the entire concept of service and builds "
            "the character that sustains vocations, marriages, and communities."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 7
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-beatitudes-age7",
        "title": "Memorise the Beatitudes (Matthew 5:3–12)",
        "category": "cognitive",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 5:3–12** — the opening of the Sermon on the Mount — aloud "
            "together.\n"
            "2. **Memorise one beatitude per day** for eight days, building on each previous one.\n"
            "3. **Understand each one** simply: 'Blessed are the poor in spirit' — those who "
            "know they need God. 'Blessed are the meek' — those who don't push themselves "
            "forward. 'Blessed are the merciful' — those who forgive.\n"
            "4. **Discuss**: these are opposite to what the world values — power, wealth, "
            "popularity. Jesus calls these the truly happy people.\n"
            "5. **Pick one beatitude per week** to focus on living out."
        ),
        "parent_note_md": (
            "The Beatitudes open the Sermon on the Mount — Jesus's most extended moral teaching. "
            "They describe the character of Kingdom citizens and consistently invert worldly values. "
            "C.S. Lewis described them as *'the most radical ethical teaching in history.'* "
            "Memorising them at age 7 gives children a moral grid that stands in contrast to "
            "what culture teaches about success, happiness, and power. "
            "They function as a Christian character manifesto — every virtue in the Beatitudes "
            "is directly countercultural."
        ),
    },
    {
        "slug": "christ-bible-stories-daily-age7",
        "title": "Read One Bible Story Every Day",
        "category": "cognitive",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a children's Bible or age-appropriate Bible** — aim for the actual text "
            "with some explanation, not just picture books.\n"
            "2. **Same time every day**: after dinner, before bed — consistency matters.\n"
            "3. **After reading, ask three questions**: What happened? What does it tell us about "
            "God? What should we do differently because of this?\n"
            "4. **Cover both Testaments**: Old Testament stories give context; New Testament "
            "stories show Jesus fulfilling them.\n"
            "5. **Keep a simple journal**: one sentence per story — 'Today I read about… and "
            "I learnt…'"
        ),
        "parent_note_md": (
            "Paul writes: *'All Scripture is God-breathed and is useful for teaching, rebuking, "
            "correcting and training in righteousness'* (2 Timothy 3:16, NIV). Psalm 119:105 "
            "says: *'Your word is a lamp for my feet, a light on my path.'* Daily Bible "
            "engagement at age 7 — even brief — is one of the most robust predictors of adult "
            "spiritual resilience. The Barna Group and similar studies consistently show that "
            "daily Bible habits established in childhood are the single strongest indicator of "
            "life-long faith."
        ),
    },
    {
        "slug": "christ-forgive-daily-age7",
        "title": "Practice Forgiving Others — Even When It Is Hard",
        "category": "social",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **At the end of each day**, ask: 'Is there anyone you need to forgive today? "
            "Anyone who hurt your feelings, was unkind, or treated you unfairly?'\n"
            "2. **Pray for that person by name** — not to change them, but to release the hurt.\n"
            "3. **Explain the difference**: forgiving is not saying what they did was okay. "
            "It is choosing not to let it live in your heart.\n"
            "4. **Read the Parable of the Unmerciful Servant** (Matthew 18:21–35) together "
            "and discuss what happens when we refuse to forgive.\n"
            "5. **Practise reconciliation** where possible — if safe, go and make peace."
        ),
        "parent_note_md": (
            "When Peter asked how many times to forgive — seven times? — Jesus answered: "
            "*'Not seven times, but seventy-seven times'* (Matthew 18:22, NIV). Jesus links "
            "our forgiveness from God directly to our forgiving others (Matthew 6:14–15). "
            "Forgiveness is one of the most countercultural and most repeated commands in the "
            "New Testament. Teaching it daily from age 7 prevents bitterness from taking root — "
            "one of the most destructive spiritual conditions the Bible warns against "
            "(Hebrews 12:15)."
        ),
    },
    {
        "slug": "christ-attend-church-age7",
        "title": "Attend Sunday Worship Every Week",
        "category": "household",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Make Sunday worship non-negotiable** — not dependent on mood, sports, or "
            "social plans.\n"
            "2. **Prepare on Saturday**: lay out clothes, sleep early, wake up without a rush.\n"
            "3. **During the service**: give the child a notepad — write or draw one thing "
            "from the sermon each week.\n"
            "4. **Discuss on the way home**: 'What did you learn? What was one thing the "
            "preacher said?'\n"
            "5. **Help them connect with other children** in the congregation — faith community "
            "is not just about the service."
        ),
        "parent_note_md": (
            "Hebrews 10:25 says: *'Not giving up meeting together, as some are in the habit of "
            "doing, but encouraging one another — and all the more as you see the Day approaching.'* "
            "Weekly church attendance provides four things children cannot get elsewhere: "
            "multigenerational community, corporate worship, regular biblical teaching, and "
            "the Eucharist/Communion. Studies by Harvard's Tyler VanderWeele show that "
            "children raised attending religious services weekly have significantly better "
            "life outcomes across mental health, relationships, and social cohesion."
        ),
    },
    {
        "slug": "christ-creation-story-age7",
        "title": "Understand the Story of Creation and What It Teaches",
        "category": "cognitive",
        "min_age": 7, "max_age": 9,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Genesis 1–2** together — both creation accounts.\n"
            "2. **Discuss the key truths** (not just the events): God made everything from "
            "nothing. Everything He made is good. Humans are made in His image (*imago Dei*). "
            "We are called to care for creation.\n"
            "3. **Discuss what 'made in God's image' means**: we can think, create, love, make "
            "moral choices — we reflect God in the world.\n"
            "4. **Address common questions honestly**: science and faith can coexist — the "
            "'how' and the 'why' are different questions.\n"
            "5. **Apply stewardship**: God put humans in charge of creation as caretakers "
            "(Genesis 2:15) — how do we care for it?"
        ),
        "parent_note_md": (
            "Genesis 1:27 states: *'So God created mankind in his own image, in the image of "
            "God he created them; male and female he created them.'* This doctrine of *imago Dei* "
            "is the foundation of human dignity, equality, and purpose. It answers the deepest "
            "question a child will ask: 'Why am I here?' John 1:3 confirms the New Testament "
            "view: *'Through him all things were made; without him nothing was made that has "
            "been made.'* A child who understands their identity as an image-bearer of God "
            "has a foundation for self-worth that no culture can take away."
        ),
    },
    {
        "slug": "christ-tithing-pocket-money-age7",
        "title": "Give a Tenth of Your Pocket Money to God",
        "category": "financial",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **When they receive any money**, immediately set aside 10% in a dedicated "
            "'giving jar' or envelope.\n"
            "2. **Let them choose** where to give it — the church offering, a charity, someone "
            "in need — making the decision real and meaningful.\n"
            "3. **Explain why**: everything belongs to God. Giving 10% is an act of trust "
            "that says 'God, I acknowledge You own it all.'\n"
            "4. **Celebrate the giving** — not the amount, but the act of cheerful generosity.\n"
            "5. **Track it**: keep a simple log of what was given and where. Review it together."
        ),
        "parent_note_md": (
            "Malachi 3:10 says: *'Bring the whole tithe into the storehouse… Test me in this, "
            "says the Lord Almighty, and see if I will not throw open the floodgates of heaven.'* "
            "Jesus affirmed tithing (Matthew 23:23) while noting its heart mattered. Paul says: "
            "*'Each of you should give what you have decided in your heart to give, not reluctantly "
            "or under compulsion, for God loves a cheerful giver'* (2 Corinthians 9:7). "
            "Teaching tithing from pocket money at age 7 forms a lifelong posture of generosity "
            "before earning a salary makes it feel costly."
        ),
    },
    {
        "slug": "christ-kind-acts-daily-age7",
        "title": "Do One Act of Kindness for Someone Every Day",
        "category": "social",
        "min_age": 7, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Each morning, set an intention**: 'Who will I be kind to today and how?'\n"
            "2. **Ideas for acts of kindness**: hold the door, share your snack, help a "
            "classmate who is struggling, write an encouraging note, sit with someone eating "
            "alone.\n"
            "3. **Each evening, report back**: 'What kind thing did you do today? How did "
            "it make the other person feel? How did it make you feel?'\n"
            "4. **Keep a kindness journal**: one sentence per day for a month.\n"
            "5. **Connect to Jesus**: *'Let your light shine before others, that they may see "
            "your good deeds and glorify your Father in heaven'* (Matthew 5:16)."
        ),
        "parent_note_md": (
            "Matthew 5:16 calls Christians to visible, active goodness. Paul writes: *'Therefore, "
            "as we have opportunity, let us do good to all people, especially to those who belong "
            "to the family of believers'* (Galatians 6:10, NIV). The parable of the Good Samaritan "
            "(Luke 10:25–37) defines 'neighbour' as anyone in need, regardless of background. "
            "Daily intentional kindness at age 7 forms the habit of noticing others — the "
            "practical core of Christian love that Jesus called the second greatest commandment."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 8
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-fruits-spirit-age8",
        "title": "Learn and Live the Fruits of the Spirit",
        "category": "cognitive",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Galatians 5:22–23**: *'The fruit of the Spirit is love, joy, peace, "
            "forbearance, kindness, goodness, faithfulness, gentleness and self-control.'*\n"
            "2. **Memorise all nine** — use the acronym LJPPKGFGS or a simple song.\n"
            "3. **Focus on one fruit per week**: learn its meaning and look for opportunities "
            "to practise it. Week 1: Love — do one loving act for someone who is difficult "
            "to love.\n"
            "4. **Self-audit at bedtime**: 'Which fruit did I show today? Which one did I "
            "struggle with?'\n"
            "5. **Discuss**: fruit grows naturally on a healthy tree — these qualities grow "
            "naturally in a person who stays close to God."
        ),
        "parent_note_md": (
            "Paul contrasts the fruits of the Spirit with the works of the flesh (Galatians "
            "5:19–21), showing that Christian character is not self-achieved but Spirit-produced. "
            "Jesus taught the same: *'I am the vine; you are the branches… apart from me you "
            "can do nothing'* (John 15:5, NIV). Teaching all nine fruits as a complete set "
            "at age 8 gives children a vocabulary for character and a daily self-assessment "
            "tool that is entirely scripturally grounded. These nine qualities together describe "
            "the full character of Jesus."
        ),
    },
    {
        "slug": "christ-baptism-meaning-age8",
        "title": "Understand What Baptism Means",
        "category": "cognitive",
        "min_age": 8, "max_age": 10,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 28:19** — baptism is commanded by Jesus as part of the "
            "Great Commission.\n"
            "2. **Explain the meaning**: baptism is a public declaration of faith in Jesus. "
            "It symbolises dying to the old self and rising to new life in Christ "
            "(Romans 6:3–4).\n"
            "3. **If the child was baptised as an infant**, explain what happened and what "
            "it means for how they live now — the promises made at their baptism.\n"
            "4. **Watch a baptism video or attend one** — seeing it makes the symbolism real.\n"
            "5. **Discuss the difference between the sign and the reality**: baptism points "
            "to inner transformation — it is not a magic act but a meaningful commitment."
        ),
        "parent_note_md": (
            "Paul writes: *'We were therefore buried with him through baptism into death in "
            "order that, just as Christ was raised from the dead through the glory of the "
            "Father, we too may live a new life'* (Romans 6:4, NIV). Jesus was baptised "
            "by John to 'fulfil all righteousness' (Matthew 3:15), modelling it for us. "
            "Across all traditions — Catholic, Orthodox, Protestant — baptism is a "
            "foundational sacrament/ordinance. Age 8 is when children begin to form their "
            "own faith identity; understanding their baptism anchors that identity in "
            "God's action on their behalf."
        ),
    },
    {
        "slug": "christ-pray-for-others-age8",
        "title": "Pray for Others by Name Every Day (Intercession)",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Make a prayer list** of 5 people to pray for: family members, a friend, "
            "a teacher, someone going through difficulty, a world situation.\n"
            "2. **Pray for each person by name** every day — not vague 'bless everyone' but "
            "specific requests: 'Lord, please help my friend with her exams.'\n"
            "3. **Update the list weekly**: add new people, note when prayers are answered.\n"
            "4. **Tell people you're praying for them** — it is an act of love and often "
            "brings great encouragement.\n"
            "5. **Track answers**: when a prayer is answered, write it down — it builds faith "
            "for the next request."
        ),
        "parent_note_md": (
            "Paul writes: *'I urge, then, first of all, that petitions, prayers, intercession "
            "and thanksgiving be made for all people'* (1 Timothy 2:1, NIV). Jesus Himself "
            "interceded for His disciples and for all future believers (John 17). James writes: "
            "*'The prayer of a righteous person is powerful and effective'* (James 5:16). "
            "Intercessory prayer teaches children three things simultaneously: compassion "
            "(noticing others' needs), faith (trusting God to act), and humility (recognising "
            "we cannot fix everything ourselves)."
        ),
    },
    {
        "slug": "christ-jesus-miracles-age8",
        "title": "Learn 10 Miracles of Jesus and Their Meaning",
        "category": "cognitive",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Study one miracle per week** from this list: Feeding 5,000 (John 6:1–14), "
            "Walking on water (Matthew 14:22–33), Healing a blind man (John 9), "
            "Raising Lazarus (John 11), Calming the storm (Mark 4:35–41), "
            "Healing ten lepers (Luke 17:11–19), Water into wine (John 2:1–11), "
            "Healing a paralysed man (Mark 2:1–12), Casting out demons (Mark 5:1–20), "
            "The Resurrection (Luke 24).\n"
            "2. **For each miracle, ask**: What problem was there? What did Jesus do? "
            "What did it reveal about who He is?\n"
            "3. **Understand miracles as signs** (John 20:30–31) — they point to Jesus's "
            "identity, not just His power.\n"
            "4. **Memorise one key verse** from each story."
        ),
        "parent_note_md": (
            "John explains his purpose: *'Jesus performed many other signs in the presence "
            "of his disciples, which are not recorded in this book. But these are written "
            "that you may believe that Jesus is the Messiah, the Son of God, and that by "
            "believing you may have life in his name'* (John 20:30–31, NIV). Each miracle "
            "reveals a different aspect of Jesus's nature and authority — over nature, "
            "disease, death, and the spiritual world. Children who know these stories have "
            "a concrete basis for faith in Jesus as Lord, not merely a moral teacher."
        ),
    },
    {
        "slug": "christ-holy-spirit-age8",
        "title": "Understand the Holy Spirit and His Role in Your Life",
        "category": "cognitive",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read John 14:15–27** — Jesus promises the Holy Spirit as Helper, "
            "Counsellor, and Spirit of Truth.\n"
            "2. **Learn His roles**: He convicts of sin (John 16:8), teaches and reminds "
            "(John 14:26), guides into truth (John 16:13), gives spiritual gifts "
            "(1 Corinthians 12), produces fruit (Galatians 5:22–23).\n"
            "3. **Discuss what 'living in the Spirit' means in practical terms**: letting "
            "Him guide decisions, being sensitive to His prompting, not grieving Him "
            "with sin (Ephesians 4:30).\n"
            "4. **Pray consciously for the Holy Spirit's help** before tasks: 'Holy Spirit, "
            "help me in this.'\n"
            "5. **Read Acts 2** together — the Day of Pentecost, when the Spirit was poured out."
        ),
        "parent_note_md": (
            "Jesus called the Holy Spirit the *Paraclete* — the Helper/Comforter/Advocate "
            "(John 14:16). Paul writes: *'Do you not know that your bodies are temples of "
            "the Holy Spirit, who is in you, whom you have received from God?'* "
            "(1 Corinthians 6:19, NIV). Understanding the Holy Spirit is essential to "
            "Christian living — He is the source of power for change, not willpower alone. "
            "Children who understand the Spirit's role have an internal resource rather than "
            "relying purely on external rules."
        ),
    },
    {
        "slug": "christ-honour-parents-age8",
        "title": "Honour and Obey Your Parents as unto the Lord",
        "category": "social",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Ephesians 6:1–3**: *'Children, obey your parents in the Lord, for "
            "this is right. Honour your father and mother — which is the first commandment "
            "with a promise.'*\n"
            "2. **Distinguish honour from blind obedience**: honour means treating parents "
            "with respect, listening attentively, not answering back dismissively, "
            "appreciating what they do.\n"
            "3. **Practise one active honour act per day**: say thank you unprompted, do a "
            "task before being asked, say something kind to a parent.\n"
            "4. **Discuss the promise**: long life and things going well — God links honouring "
            "parents to flourishing.\n"
            "5. **When you disagree**, express it respectfully — 'Mum/Dad, may I explain why "
            "I see it differently?' not sulking or arguing."
        ),
        "parent_note_md": (
            "This is the Fifth Commandment (Exodus 20:12) and the only one with an explicit "
            "promise attached: *'that it may go well with you and that you may enjoy long "
            "life on the earth'* (Ephesians 6:3, NIV). Paul places it in the context of "
            "mutual submission — parents are also charged: *'Do not exasperate your children'* "
            "(Ephesians 6:4). At age 8, children are beginning to push against authority — "
            "grounding honour in scripture rather than in parental preference gives it moral "
            "weight that outlasts parental authority itself."
        ),
    },
    {
        "slug": "christ-generosity-sharing-age8",
        "title": "Practice Generosity — Share What You Have",
        "category": "financial",
        "min_age": 8, "max_age": 11,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read the story of the widow's offering** (Luke 21:1–4) — she gave "
            "everything she had. God values generosity over amount.\n"
            "2. **Find one thing to give away this week**: a toy, food, time, help. "
            "Give it to someone who needs it more than you.\n"
            "3. **Practise sharing in small daily moments**: the last biscuit, the front seat, "
            "the remote control — treat these as generosity training.\n"
            "4. **Collect items for a local food bank or charity** once a month.\n"
            "5. **Discuss**: holding onto things tightly makes us anxious; giving freely "
            "makes us joyful. This is one of Jesus's most repeated teachings."
        ),
        "parent_note_md": (
            "Jesus said: *'Give, and it will be given to you. A good measure, pressed down, "
            "shaken together and running over, will be poured into your lap'* (Luke 6:38, NIV). "
            "The early church was marked by extraordinary generosity: *'They sold property and "
            "possessions to give to anyone who had need'* (Acts 2:45). The widow's offering "
            "(Luke 21:1–4) shows that God measures generosity by sacrifice, not by amount. "
            "Teaching generosity at age 8 — before materialism becomes deeply ingrained — "
            "shapes how children relate to money and possessions for life."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 9
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-read-four-gospels-age9",
        "title": "Read All Four Gospels (Matthew, Mark, Luke, John)",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with Mark** — the shortest Gospel (16 chapters), fast-paced "
            "and action-focused. Read 1–2 chapters per day.\n"
            "2. **Move to Luke** — the most detailed account, with the most parables and "
            "focus on the poor and women.\n"
            "3. **Then Matthew** — the most Jewish Gospel, with the Sermon on the Mount "
            "and five major teaching blocks.\n"
            "4. **Finally John** — the most theological. Slower reading, focus on the "
            "'I am' statements.\n"
            "5. **Keep a simple notebook**: one insight per chapter — 'What did I learn "
            "about Jesus from this?'"
        ),
        "parent_note_md": (
            "The four Gospels give four complementary portraits of Jesus: Matthew (King/Messiah), "
            "Mark (Servant/Son of God), Luke (Son of Man/universal Saviour), John (Word/God). "
            "Reading all four at age 9 gives children a full and rich picture of Jesus's life, "
            "teaching, death, and resurrection. John states his purpose explicitly: "
            "*'These are written that you may believe that Jesus is the Messiah, the Son of "
            "God, and that by believing you may have life in his name'* (John 20:31, NIV). "
            "Knowing the Gospels is the irreplaceable foundation of Christian faith."
        ),
    },
    {
        "slug": "christ-holy-communion-age9",
        "title": "Understand Holy Communion — The Lord's Supper",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Luke 22:14–20** — the Last Supper — and 1 Corinthians 11:23–26 "
            "(Paul's account and its meaning).\n"
            "2. **Explain the two elements**: bread = the body of Christ broken for us. "
            "Cup = the blood of Christ poured out for us. We do this in remembrance.\n"
            "3. **Discuss across traditions**: Catholics/Orthodox believe in real presence; "
            "Protestants see it as a memorial and proclamation. All traditions take it "
            "seriously as a central act of worship.\n"
            "4. **Explain the self-examination** Paul mentions (1 Corinthians 11:28) — "
            "we approach Communion with honesty and repentance.\n"
            "5. **Next time they receive Communion**, encourage deliberate, conscious "
            "participation — not routine."
        ),
        "parent_note_md": (
            "Jesus said: *'Do this in remembrance of me'* (Luke 22:19, NIV). Paul writes: "
            "*'For whenever you eat this bread and drink this cup, you proclaim the Lord's "
            "death until he comes'* (1 Corinthians 11:26). Communion is the most universally "
            "observed act in Christian worship across all denominations. A child who "
            "understands what they are doing — and why — participates with faith, not "
            "mere ritual. Age 9 is typically when first communion preparation begins "
            "in Catholic and some Protestant traditions, making this task timely."
        ),
    },
    {
        "slug": "christ-memorise-10-verses-age9",
        "title": "Memorise 10 Key Bible Verses by Heart",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose 10 foundational verses** — one per week:\n"
            "   - John 3:16 · Romans 3:23 · Romans 6:23 · Romans 10:9 · John 14:6\n"
            "   - Philippians 4:13 · Jeremiah 29:11 · Psalm 23:1 · Matthew 6:33 · "
            "Proverbs 3:5–6\n"
            "2. **Write the verse** on a card and put it on the bathroom mirror or "
            "bedside table.\n"
            "3. **Say it aloud 5 times every morning** until memorised — then test "
            "without the card.\n"
            "4. **Learn the reference** (book, chapter, verse) — not just the words.\n"
            "5. **Use the verse in conversation or prayer** that week — applying it "
            "makes it stick."
        ),
        "parent_note_md": (
            "Psalm 119:11 says: *'I have hidden your word in my heart that I might not "
            "sin against you.'* Scripture memorisation is one of the most practically "
            "powerful spiritual disciplines — the Holy Spirit brings it to mind in "
            "moments of temptation, decision, or fear (John 14:26). The verses listed "
            "form a basic gospel framework (the Roman Road), a devotional foundation "
            "(Psalms, Proverbs), and a life orientation (Jeremiah 29:11, Matthew 6:33). "
            "A child who knows these ten verses has the core of the gospel in their heart."
        ),
    },
    {
        "slug": "christ-easter-resurrection-age9",
        "title": "Understand Easter — The Resurrection and What It Means",
        "category": "cognitive",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 Corinthians 15:1–8** — Paul's summary of the resurrection as "
            "the core of the gospel.\n"
            "2. **Walk through Holy Week**: Palm Sunday → Last Supper → Arrest → Trial "
            "→ Crucifixion → Burial → Resurrection → Appearances → Ascension.\n"
            "3. **Discuss why the resurrection matters**: if Jesus did not rise, our faith "
            "is useless (1 Corinthians 15:17). If He did rise, everything changes.\n"
            "4. **Address common questions**: What evidence is there? Why did He have to "
            "die? What does it mean for us?\n"
            "5. **Celebrate Easter more intentionally than Christmas** — it is the central "
            "event of the entire Christian faith."
        ),
        "parent_note_md": (
            "Paul is unambiguous: *'If Christ has not been raised, your faith is futile; "
            "you are still in your sins'* (1 Corinthians 15:17, NIV). The resurrection "
            "is not peripheral — it is the entire foundation. N.T. Wright, one of the "
            "world's leading New Testament scholars, calls it *'the best-attested fact "
            "of ancient history.'* Children who understand why Easter matters — not just "
            "as a holiday but as a historical and theological claim — have the intellectual "
            "and spiritual roots to withstand the secular challenges they will face in school."
        ),
    },
    {
        "slug": "christ-serve-in-church-age9",
        "title": "Serve in Church or Your Community",
        "category": "household",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find one regular service role** in church: helping set up chairs, "
            "serving in children's ministry, welcoming people at the door, collecting "
            "food donations, helping clean up after services.\n"
            "2. **Show up consistently** — serving once is an act, serving weekly builds "
            "character and community.\n"
            "3. **In the community**: one service act per month — volunteer at a food bank, "
            "help an elderly neighbour, collect for a charity.\n"
            "4. **Reflect**: Jesus came to serve, not to be served. We follow Him by doing "
            "the same.\n"
            "5. **Ask the church leader** what the child could practically do — don't wait "
            "for an invitation."
        ),
        "parent_note_md": (
            "Paul writes: *'You, my brothers and sisters, were called to be free. But do "
            "not use your freedom to indulge the flesh; rather, serve one another humbly "
            "in love'* (Galatians 5:13, NIV). Jesus declared: *'Whoever wants to become "
            "great among you must be your servant'* (Matthew 20:26). Children who serve "
            "in church from a young age are significantly more likely to remain in "
            "active faith as adults (Barna Research). Service also builds empathy, "
            "reduces entitlement, and forms community bonds that sustain faith through "
            "adolescence."
        ),
    },
    {
        "slug": "christ-give-to-poor-age9",
        "title": "Give to Those in Need — Regular Charitable Giving",
        "category": "financial",
        "min_age": 9, "max_age": 12,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up a 'giving fund'**: a portion of any money received goes into "
            "a giving jar specifically for those in need.\n"
            "2. **Choose a cause together**: a local food bank, a child sponsorship "
            "programme, a disaster relief fund, a homeless shelter.\n"
            "3. **Learn about the cause**: who are we helping? What is their life like? "
            "Making it concrete builds compassion.\n"
            "4. **Give regularly, not just at Christmas** — need does not take holidays.\n"
            "5. **Practise anonymous giving** when possible — give without announcing it, "
            "following Jesus's teaching in Matthew 6:3."
        ),
        "parent_note_md": (
            "Paul writes: *'Each of you should give what you have decided in your heart "
            "to give, not reluctantly or under compulsion, for God loves a cheerful giver'* "
            "(2 Corinthians 9:7, NIV). Jesus says: *'Truly I tell you, whatever you did "
            "for one of the least of these brothers and sisters of mine, you did for me'* "
            "(Matthew 25:40). Proverbs 19:17 adds: *'Whoever is kind to the poor lends to "
            "the Lord, and he will reward them.'* Age 9 is when children begin to understand "
            "global inequality — compassion guided by scripture is the antidote to indifference."
        ),
    },
    {
        "slug": "christ-deep-forgiveness-age9",
        "title": "Forgive Someone Who Has Deeply Hurt You",
        "category": "social",
        "min_age": 9, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 18:21–35** — the Parable of the Unmerciful Servant. "
            "Discuss: we have been forgiven an unpayable debt by God. How much more "
            "should we forgive others?\n"
            "2. **Identify someone they genuinely struggle to forgive** — a bully, a "
            "friend who betrayed them, a relative who hurt them.\n"
            "3. **Pray for that person daily for two weeks** — even if it feels impossible. "
            "Prayer changes the one praying.\n"
            "4. **Clarify the distinction**: forgiving is not pretending the hurt didn't "
            "happen. It is releasing them from your debt — releasing yourself from bitterness.\n"
            "5. **If reconciliation is safe and appropriate**, take a small step toward it "
            "with an adult's guidance."
        ),
        "parent_note_md": (
            "Paul writes: *'Bear with each other and forgive one another if any of you has "
            "a grievance against someone. Forgive as the Lord forgave you'* (Colossians "
            "3:13, NIV). Hebrews 12:15 warns: *'See to it that no one falls short of the "
            "grace of God and that no bitter root grows up to cause trouble.'* Deep "
            "forgiveness is different from casual forgiveness — it requires a decision of "
            "the will, often sustained by prayer. Age 9 is when social wounds can begin "
            "to run deep. Teaching the process of real forgiveness at this age is one of "
            "the most protective things a Christian parent can do."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 10
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-apostles-creed-age10",
        "title": "Learn the Apostles' Creed and Understand Every Line",
        "category": "cognitive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Memorise the full Apostles' Creed** — recite it together daily for "
            "two weeks.\n"
            "2. **Break it into three sections**: belief in God the Father (Creator), "
            "belief in Jesus Christ (Saviour), belief in the Holy Spirit and the Church.\n"
            "3. **For each line, explain the meaning** — 'born of the Virgin Mary' "
            "(Jesus was fully human), 'descended into hell' (He went to the realm of "
            "the dead), 'the communion of saints' (the global, cross-time family of "
            "believers).\n"
            "4. **Identify any lines that raise questions** — engage them seriously.\n"
            "5. **Discuss**: this creed has united Christians across denominations for "
            "1,700 years — reciting it connects us to every believer in history."
        ),
        "parent_note_md": (
            "The Apostles' Creed (c. 2nd century) summarises the core beliefs of "
            "Christianity in twelve articles and is used in Catholic, Orthodox, Anglican, "
            "Lutheran, Reformed, and many other traditions. It is not Scripture, but it "
            "is a faithful summary of Scripture. Learning it at age 10 gives children "
            "doctrinal literacy — they know what they believe, why, and how it connects "
            "to the Biblical narrative. Doctrine is not dry; it is the skeleton that "
            "gives Christian life its shape."
        ),
    },
    {
        "slug": "christ-trinity-age10",
        "title": "Understand the Trinity — One God, Three Persons",
        "category": "cognitive",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 28:19** (baptise in the name of Father, Son, and Spirit) "
            "and 2 Corinthians 13:14 (the Trinitarian blessing).\n"
            "2. **Explain the doctrine clearly**: One God — not three gods. Three distinct "
            "persons — Father, Son, Holy Spirit — each fully God, not three parts.\n"
            "3. **Discuss common illustrations and their limits**: the egg (three parts), "
            "water (three states), a man with three roles — all illustrations break down. "
            "The Trinity is a mystery, not an impossibility.\n"
            "4. **Discuss why it matters**: God is relational within Himself. We are "
            "created for relationship because our Creator is relational. Love is at the "
            "heart of God's nature (1 John 4:8).\n"
            "5. **Engage their questions seriously** — the Trinity is worth wrestling with."
        ),
        "parent_note_md": (
            "The Trinity is the distinctively Christian understanding of God — present in "
            "Jesus's baptism (Matthew 3:16–17), His teaching (John 14–16), and Paul's "
            "letters (Ephesians 1). It was formally articulated at the Council of Nicaea "
            "(325 AD) in response to heresy. C.S. Lewis wrote: *'If Christianity was "
            "something we were making up, of course we could make it easier. But it is "
            "not… God is not a static thing — not even a person — but a dynamic, pulsating "
            "activity, a life, almost a kind of drama.'* Age 10 is when children can begin "
            "to handle theological nuance — this is the right time."
        ),
    },
    {
        "slug": "christ-fasting-age10",
        "title": "Learn and Practice Christian Fasting",
        "category": "household",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 6:16–18** — Jesus assumes His followers will fast ("
            "'when you fast,' not 'if you fast').\n"
            "2. **Start small**: skip one meal, replacing it with prayer and Bible "
            "reading. Begin with one day per month.\n"
            "3. **Explain the purpose**: fasting is not dieting. It is deliberately "
            "choosing hunger to create space for God — the physical discomfort reminds "
            "us to pray.\n"
            "4. **Do it privately** (Matthew 6:18) — not for social credit.\n"
            "5. **Observe Lenten fasting** or Fridays (common across Catholic, Orthodox, "
            "Anglican, and many Protestant traditions) as a shared community discipline.\n"
            "6. **Discuss substitution**: fasting is not only food — it can be "
            "fasting from screens, entertainment, or social media."
        ),
        "parent_note_md": (
            "Jesus fasted for 40 days before beginning His ministry (Matthew 4:2) and "
            "taught fasting as a normal spiritual discipline alongside prayer and giving "
            "(Matthew 6:1–18). Isaiah 58:6–7 reveals the fast God chooses: *'to loose "
            "the chains of injustice… to share your food with the hungry.'* Fasting "
            "at age 10 teaches children that the body's appetites are not in charge — "
            "the Spirit is. This is countercultural formation of the most practical kind. "
            "Most major Christian traditions have a fasting calendar: Lent (Catholic/Orthodox/"
            "Anglican), quarterly fasts (Reformed), individual disciplines (Evangelical)."
        ),
    },
    {
        "slug": "christ-sabbath-rest-age10",
        "title": "Keep Sunday as a Day of Rest, Worship, and Family",
        "category": "household",
        "min_age": 10, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Guard Sunday**: no homework (plan ahead), limited screens, no "
            "sport commitments if possible. Make it noticeably different from other days.\n"
            "2. **Start with worship**: Sunday service is the anchor, not an option.\n"
            "3. **Do something restorative as a family**: a walk, a meal together, "
            "a board game, visiting grandparents.\n"
            "4. **Read or reflect**: use Sunday afternoon for spiritual reading, "
            "journaling, or a longer prayer time.\n"
            "5. **Discuss the purpose**: we rest because God rested (Genesis 2:2–3). "
            "We worship because we were made for it. Rest is not laziness — it is "
            "an act of trust that God runs the world, not us."
        ),
        "parent_note_md": (
            "The Fourth Commandment: *'Remember the Sabbath day by keeping it holy'* "
            "(Exodus 20:8, NIV). Jesus said: *'The Sabbath was made for man, not man "
            "for the Sabbath'* (Mark 2:27) — it is a gift, not a burden. In an age of "
            "constant productivity pressure and over-scheduled children, keeping Sunday "
            "different is a radical counter-cultural act. Children who grow up with a "
            "weekly rhythm of rest and worship are less anxious, more grounded, and more "
            "likely to retain faith as adults — Sunday is not just a religious obligation "
            "but a psychological and spiritual anchor."
        ),
    },
    {
        "slug": "christ-repentance-age10",
        "title": "Understand and Practice Repentance — Turning Back to God",
        "category": "household",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 John 1:9**: *'If we confess our sins, he is faithful and just "
            "and will forgive us our sins and purify us from all unrighteousness.'*\n"
            "2. **Learn the meaning of repentance**: not just feeling sorry — "
            "*metanoia* (Greek) means a change of mind and direction. Turn away "
            "from the wrong, turn toward God.\n"
            "3. **Build a daily examination of conscience**: at bedtime, quietly review "
            "the day — where did I fall short? Bring it honestly to God.\n"
            "4. **Practise the three steps**: confess specifically (not vaguely), "
            "receive forgiveness (don't wallow in guilt), resolve to change.\n"
            "5. **For Catholics/Anglicans/Orthodox**: explore the sacrament of "
            "Confession as an additional expression of this."
        ),
        "parent_note_md": (
            "John's opening message in 1 John establishes that even believers sin, "
            "and the response is confession, not pretence: *'If we claim to be without "
            "sin, we deceive ourselves'* (1 John 1:8). Jesus began His ministry with "
            "*'Repent, for the kingdom of heaven has come near'* (Matthew 4:17). "
            "Paul writes that *'godly sorrow brings repentance that leads to salvation "
            "and leaves no regret, but worldly sorrow brings death'* (2 Corinthians "
            "7:10). Teaching children the discipline of repentance at age 10 prevents "
            "both the extremes of callous indifference to sin and crushing guilt — "
            "it is the ongoing maintenance of a living relationship with God."
        ),
    },
    {
        "slug": "christ-golden-rule-age10",
        "title": "Live the Golden Rule Every Day",
        "category": "social",
        "min_age": 10, "max_age": 13,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Memorise Matthew 7:12**: *'So in everything, do to others what you "
            "would have them do to you, for this sums up the Law and the Prophets.'*\n"
            "2. **Apply it before every interaction**: before speaking, before acting, "
            "ask — 'How would I want to be treated in this situation?'\n"
            "3. **Apply it to difficult situations**: the person who is excluded, the "
            "unpopular classmate, the person who annoys you — how would you want to "
            "be treated if you were them?\n"
            "4. **Track Golden Rule moments**: one per day for a week — 'I chose to "
            "treat someone the way I'd want to be treated when…'\n"
            "5. **Discuss**: Jesus says this summarises the whole moral law. It is "
            "the foundation of justice, kindness, and love."
        ),
        "parent_note_md": (
            "Matthew 7:12 concludes the Sermon on the Mount's ethical teaching with "
            "one universal principle. Jesus links it explicitly to the entire Old "
            "Testament moral tradition ('the Law and the Prophets'). Paul echoes: "
            "*'Love your neighbour as yourself'* (Galatians 5:14). The Golden Rule "
            "is found in nearly every world religion, but Jesus's formulation is "
            "uniquely positive — not 'don't do harm' but 'actively do good.' "
            "At age 10, children are navigating complex social dynamics — "
            "this rule gives them a simple, powerful, and scriptural decision-making tool."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 11
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-parables-of-jesus-age11",
        "title": "Study the Parables of Jesus and Their Meaning",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Study one parable per week** — start with these ten:\n"
            "   The Prodigal Son (Luke 15:11–32), The Good Samaritan (Luke 10:25–37), "
            "The Sower (Mark 4:1–20), The Lost Sheep (Luke 15:3–7), The Talents "
            "(Matthew 25:14–30), The Pharisee and the Tax Collector (Luke 18:9–14), "
            "The Ten Virgins (Matthew 25:1–13), The Pearl of Great Price (Matthew 13:45–46), "
            "The Unmerciful Servant (Matthew 18:21–35), The Rich Fool (Luke 12:16–21).\n"
            "2. **For each parable, answer three questions**: What is the story? "
            "What is Jesus teaching? How does it apply to my life right now?\n"
            "3. **Memorise one key verse** from each parable.\n"
            "4. **Discuss why Jesus used stories**: they reveal truth to those who seek "
            "it and conceal it from those who don't (Matthew 13:10–13)."
        ),
        "parent_note_md": (
            "Jesus used parables as His primary teaching method — one-third of His recorded "
            "teaching is in parable form. They are deceptively simple on the surface and "
            "inexhaustibly deep on reflection. The Prodigal Son alone has been called 'the "
            "greatest short story ever told' (Charles Dickens). Each parable reveals something "
            "specific about the Kingdom of God, human nature, or God's character. At age 11, "
            "children can grasp the layered meanings. Knowing the parables well gives them "
            "a theological imagination — the ability to think in stories as Jesus did."
        ),
    },
    {
        "slug": "christ-acts-apostles-age11",
        "title": "Read the Acts of the Apostles — The Birth of the Church",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Acts over 4–6 weeks** — 2–3 chapters per sitting.\n"
            "2. **Track the key moments**: Pentecost (Acts 2), Peter's boldness (Acts 3–4), "
            "Ananias and Sapphira (Acts 5), Stephen's martyrdom (Acts 7), "
            "Paul's conversion (Acts 9), the first Gentile believers (Acts 10), "
            "Paul's missionary journeys (Acts 13–28).\n"
            "3. **Ask with each chapter**: What did the Holy Spirit do here? How did "
            "the early Christians respond to hardship?\n"
            "4. **Compare to today**: in what ways is our church like the early church? "
            "In what ways is it different?\n"
            "5. **Note the repeated pattern**: proclamation → response → opposition → "
            "growth. The church grew through suffering, not despite it."
        ),
        "parent_note_md": (
            "Acts is the bridge between the Gospels and the Epistles — it shows how the "
            "message of Jesus spread from Jerusalem to Rome in one generation. The early "
            "church was marked by four things: *'They devoted themselves to the apostles' "
            "teaching and to fellowship, to the breaking of bread and to prayer'* (Acts "
            "2:42, NIV). Reading Acts at age 11 gives children a model of what authentic "
            "Christian community looks like — bold, Spirit-filled, generous, and willing "
            "to suffer for truth. It also shows that Christianity is a historical movement, "
            "not a private belief system."
        ),
    },
    {
        "slug": "christ-stewardship-age11",
        "title": "Understand Christian Stewardship — Time, Money, and Gifts",
        "category": "financial",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 2 Corinthians 9:6–7** and the Parable of the Talents "
            "(Matthew 25:14–30).\n"
            "2. **Apply the three areas of stewardship**:\n"
            "   - *Money*: Am I giving generously? Saving wisely? Spending carefully?\n"
            "   - *Time*: How much time goes to God, family, study, screen time? "
            "Is the balance right?\n"
            "   - *Gifts/Talents*: What am I good at? Am I using it for God and others?\n"
            "3. **Do a weekly review**: spend 5 minutes each Sunday reflecting on how "
            "well you stewarded these three areas that week.\n"
            "4. **Set one concrete stewardship goal** in each area for the next month.\n"
            "5. **Discuss**: we own nothing — we manage what God has given us."
        ),
        "parent_note_md": (
            "The Parable of the Talents makes stewardship explicit: God entrusts resources "
            "and expects returns (Matthew 25:14–30). Peter writes: *'Each of you should use "
            "whatever gift you have received to serve others, as faithful stewards of God's "
            "grace in its various forms'* (1 Peter 4:10, NIV). Paul adds: *'Whoever sows "
            "sparingly will also reap sparingly, and whoever sows generously will also reap "
            "generously'* (2 Corinthians 9:6). At age 11, children begin to have real "
            "discretionary time and money — teaching stewardship now shapes how they handle "
            "much larger resources as adults."
        ),
    },
    {
        "slug": "christ-anger-control-age11",
        "title": "Control Anger with Prayer and Scripture",
        "category": "social",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read James 1:19–20**: *'Everyone should be quick to listen, slow to speak "
            "and slow to become angry, because human anger does not produce the "
            "righteousness that God desires.'*\n"
            "2. **Identify your anger triggers**: list the top 3 situations that reliably "
            "make you angry. Awareness is the first step.\n"
            "3. **Practise the pause**: when anger rises, pause for 5 seconds before "
            "speaking or acting. In that pause — breathe, pray one word: 'Help.'\n"
            "4. **Memorise Ephesians 4:26**: *'In your anger do not sin: do not let the "
            "sun go down while you are still angry.'* — resolve conflict before bed.\n"
            "5. **Distinguish righteous from selfish anger**: Jesus showed righteous anger "
            "at injustice (John 2:13–17). Not all anger is wrong — how we express it matters."
        ),
        "parent_note_md": (
            "James 1:19–20 sets the standard clearly. Paul adds: *'Do not be quickly "
            "provoked in your spirit, for anger resides in the lap of fools'* (Ecclesiastes "
            "7:9). Proverbs 15:1 says: *'A gentle answer turns away wrath, but a harsh "
            "word stirs up anger.'* Adolescence is a peak window for anger — hormonal "
            "changes intensify emotional reactions exactly when social stakes are rising. "
            "Teaching biblical anger management at age 11 — before the peak of "
            "adolescence — equips children with tools before they are overwhelmed."
        ),
    },
    {
        "slug": "christ-psalms-emotions-age11",
        "title": "Use the Psalms for Emotional and Spiritual Guidance",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Match psalms to emotions** — keep this list accessible:\n"
            "   - Anxious/afraid: Psalm 23, 46, 91\n"
            "   - Sad/depressed: Psalm 34, 42, 88\n"
            "   - Thankful/joyful: Psalm 100, 103, 150\n"
            "   - Confused/doubting: Psalm 73, 77\n"
            "   - Guilty/ashamed: Psalm 51\n"
            "   - Overwhelmed: Psalm 61, 62\n"
            "2. **Read the matching psalm** when that emotion arises — before turning "
            "to a friend, phone, or social media.\n"
            "3. **Memorise one psalm in full** — Psalm 23, 100, or 121.\n"
            "4. **Journal**: write a short psalm of your own using the same honest style — "
            "address God directly, say what you actually feel."
        ),
        "parent_note_md": (
            "The Psalms are the prayer book of the Bible — 150 prayers covering every "
            "human emotion with radical honesty. Psalm 22 begins with the cry of desolation "
            "(*'My God, my God, why have you forsaken me?'*) — the same words Jesus cried "
            "from the cross (Matthew 27:46). The Psalms validate emotional honesty before "
            "God rather than performing spiritual happiness. Psalm 34:18 says: *'The Lord "
            "is close to the broken-hearted and saves those who are crushed in spirit.'* "
            "At age 11, emotional intelligence and faith fluency need to develop together — "
            "the Psalms are the perfect resource."
        ),
    },
    {
        "slug": "christ-youth-group-age11",
        "title": "Join and Commit to a Christian Youth Group or Community",
        "category": "social",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Find a youth group** — church-based, parachurch (Scripture Union, "
            "YWAM, Boys/Girls Brigade), or school Christian Union.\n"
            "2. **Commit to attending consistently** — not just when convenient.\n"
            "3. **Invest in relationships**: don't just attend, connect. Learn the names "
            "of at least 5 peers in the group.\n"
            "4. **Take a leadership step**: volunteer to help set up, lead a discussion, "
            "or welcome new members.\n"
            "5. **Discuss honestly**: does this group make you a better Christian? "
            "Do you leave more encouraged and challenged, or unchanged?"
        ),
        "parent_note_md": (
            "Proverbs 13:20 says: *'Walk with the wise and become wise, for a companion "
            "of fools suffers harm.'* Research consistently shows that peer Christian "
            "community is the strongest external protective factor for adolescent faith. "
            "Hebrews 10:25 instructs against abandoning gathering together, *'but "
            "encouraging one another — and all the more as you see the Day approaching.'* "
            "A child with Christian friends navigates adolescence with a fundamentally "
            "different set of social reference points — peers who share values are "
            "irreplaceable during the years when parental influence naturally decreases."
        ),
    },
    {
        "slug": "christ-lent-practices-age11",
        "title": "Observe the Season of Lent — Fasting, Prayer, and Giving",
        "category": "household",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain Lent**: 40 days before Easter, mirroring Jesus's 40 days in "
            "the wilderness. Begins on Ash Wednesday.\n"
            "2. **Choose one thing to fast from**: social media, sweets, gaming, "
            "meat on Fridays — something genuinely sacrificial.\n"
            "3. **Add something positive**: read one extra chapter of Scripture per day, "
            "pray an extra 5 minutes, do one act of service per week.\n"
            "4. **Give alms**: redirect money saved from fasting to someone in need.\n"
            "5. **Read one Gospel during Lent** as a whole — Matthew, Mark, Luke, or "
            "John — arriving at Easter with the full story fresh in mind.\n"
            "6. **Attend Holy Week services** if available: Maundy Thursday, Good "
            "Friday, Easter Vigil."
        ),
        "parent_note_md": (
            "Joel 2:12 calls: *'Return to me with all your heart, with fasting and weeping "
            "and mourning.'* Lent is the most widely observed Christian season across "
            "Catholic, Orthodox, Anglican, Lutheran, and many Evangelical traditions. "
            "Its three disciplines — fasting, prayer, and almsgiving — are exactly the "
            "three Jesus assumed His followers would practise in Matthew 6:1–18. "
            "Observing Lent at age 11 gives children a liturgical calendar that structures "
            "spiritual growth through the year, not just individual effort."
        ),
    },
    {
        "slug": "christ-works-of-mercy-age11",
        "title": "Practice the Works of Mercy — Serve the Least",
        "category": "household",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 25:35–40** — Jesus identifies Himself with the hungry, "
            "thirsty, stranger, naked, sick, and imprisoned.\n"
            "2. **Pick two works of mercy to practise this month**:\n"
            "   - Feed the hungry: donate to a food bank or help prepare meals for others\n"
            "   - Welcome the stranger: befriend a new student or isolated classmate\n"
            "   - Clothe the naked: donate good clothes to a charity shop\n"
            "   - Visit the sick: write a card or visit someone who is ill\n"
            "   - Comfort the sorrowful: spend time with someone who is grieving\n"
            "3. **Do it without announcing it** (Matthew 6:3) — no social media posts.\n"
            "4. **Reflect after**: how did it feel? What did you notice about the person?"
        ),
        "parent_note_md": (
            "Matthew 25:40 is one of the most sobering verses in the New Testament: "
            "*'Truly I tell you, whatever you did for one of the least of these brothers "
            "and sisters of mine, you did for me.'* The Works of Mercy have been a "
            "cornerstone of Christian practice since the early church. They are not "
            "optional extras — they are the lived expression of faith. James writes: "
            "*'Faith without deeds is dead'* (James 2:26). Teaching children to serve "
            "the most vulnerable connects faith directly to action and dismantles "
            "the Christianity-as-comfortable-lifestyle tendency of contemporary culture."
        ),
    },
    {
        "slug": "christ-overcome-worry-age11",
        "title": "Overcome Worry and Anxiety Through Prayer and Scripture",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Memorise Philippians 4:6–7**: *'Do not be anxious about anything, but "
            "in every situation, by prayer and petition, with thanksgiving, present your "
            "requests to God. And the peace of God, which transcends all understanding, "
            "will guard your hearts and minds in Christ Jesus.'*\n"
            "2. **Apply the four-step process when worry strikes**: "
            "Stop → identify the worry specifically → pray about it using Phil 4:6 → "
            "replace the worry with a truth from scripture.\n"
            "3. **Keep a 'worry list'**: write down worries and then pray over each one, "
            "symbolically handing them to God.\n"
            "4. **Read Matthew 6:25–34** — Jesus's direct teaching on anxiety: 'Can worry "
            "add a single hour to your life?' Seek the Kingdom first.\n"
            "5. **Track answered prayers** — building an evidence base that God is faithful."
        ),
        "parent_note_md": (
            "Anxiety disorders in children have risen sharply — the average onset age is "
            "now 11. Scripture addresses anxiety directly: *'Cast all your anxiety on him "
            "because he cares for you'* (1 Peter 5:7). Jesus asked: *'Can any one of you "
            "by worrying add a single hour to your life?'* (Matthew 6:27). Philippians "
            "4:6–7 gives a concrete practice — prayer plus thanksgiving — and promises "
            "a specific result: 'the peace of God which transcends all understanding.' "
            "This is not suppression of anxiety but its biblical treatment: bring it to "
            "God, replace it with trust, receive peace. A profoundly practical tool."
        ),
    },
    {
        "slug": "christ-new-testament-reading-age11",
        "title": "Read Through the New Testament Systematically",
        "category": "cognitive",
        "min_age": 11, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set a pace**: 2 chapters per day completes the New Testament in about "
            "130 days — roughly 4 months.\n"
            "2. **Use a reading plan**: Matthew → Mark → Luke → John → Acts → Romans → "
            "1&2 Corinthians → Galatians → Ephesians → Philippians → Colossians → "
            "1&2 Thessalonians → 1&2 Timothy → Titus → Philemon → Hebrews → James → "
            "1&2 Peter → 1,2,3 John → Jude → Revelation.\n"
            "3. **After each book**, write 3 things: what surprised you, what challenged "
            "you, what you will apply.\n"
            "4. **Don't skip the Epistles**: Paul's letters are the theological backbone "
            "of Christian living — they explain how to live in light of what Jesus did.\n"
            "5. **Finish with Revelation**: read it as a message of hope, not fear."
        ),
        "parent_note_md": (
            "Paul writes: *'All Scripture is God-breathed and is useful for teaching, "
            "rebuking, correcting and training in righteousness, so that the servant of "
            "God may be thoroughly equipped for every good work'* (2 Timothy 3:16–17, "
            "NIV). Reading the full New Testament by age 11 gives children direct "
            "access to the primary source of Christian teaching — not summaries, not "
            "children's versions, but the actual text. Children who read the Bible "
            "for themselves are significantly more resistant to both legalism and "
            "liberalism, because they know what it actually says."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 12
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-plan-of-salvation-age12",
        "title": "Understand and Be Able to Explain the Gospel",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Learn the four key truths** (the Roman Road):\n"
            "   - All have sinned (Romans 3:23)\n"
            "   - The wages of sin is death (Romans 6:23)\n"
            "   - God demonstrates His love through Christ's death (Romans 5:8)\n"
            "   - Confess and believe and you will be saved (Romans 10:9)\n"
            "2. **Practise explaining it** to a family member in under 2 minutes.\n"
            "3. **Understand the atonement**: why did Jesus have to die? "
            "Substitutionary atonement — He took our penalty so we don't have to.\n"
            "4. **Understand grace**: salvation is a gift, not earned. "
            "Ephesians 2:8–9: *'For it is by grace you have been saved, through faith — "
            "and this is not from yourselves, it is the gift of God.'*\n"
            "5. **Reflect personally**: do you believe this? Have you responded to it?"
        ),
        "parent_note_md": (
            "Paul summarises the gospel in 1 Corinthians 15:3–4: *'Christ died for our "
            "sins according to the Scriptures, that he was buried, that he was raised "
            "on the third day.'* This is the non-negotiable core of Christianity — "
            "remove it and what remains is only a moral code. Age 12 is the age of "
            "reason — children can now engage the gospel not only emotionally but "
            "intellectually. Understanding it clearly enough to explain it is a sign "
            "of genuine personal ownership. Many Christian traditions hold confirmation "
            "or first communion at this age precisely because they recognise this "
            "developmental threshold."
        ),
    },
    {
        "slug": "christ-quiet-time-age12",
        "title": "Build a Daily Quiet Time — Bible Reading and Personal Prayer",
        "category": "household",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Fix a time and place**: 15 minutes every morning before school, "
            "or before bed. Same time, same place builds the habit.\n"
            "2. **Structure the 15 minutes**: 5 min Bible reading → 5 min reflection "
            "(what does this show me about God? about myself? what will I do?) → "
            "5 min prayer (thanks, sorry, please).\n"
            "3. **Keep a journal**: one insight and one prayer per day. Looking back "
            "after 3 months shows spiritual growth concretely.\n"
            "4. **Use a simple devotional plan** if needed — YouVersion Bible app "
            "has age-appropriate plans, or a printed daily reading plan.\n"
            "5. **Guard it**: this is a non-negotiable appointment with God. "
            "Protect it from screens and other distractions."
        ),
        "parent_note_md": (
            "Mark 1:35 records: *'Very early in the morning, while it was still dark, "
            "Jesus got up, left the house and went off to a solitary place, where he "
            "prayed.'* If Jesus — who was God — needed regular time alone with the "
            "Father, how much more do we? The discipline of daily quiet time is the "
            "single habit most consistently cited by Christian adults as the foundation "
            "of their spiritual life. Establishing it at age 12 — before full adolescent "
            "busyness takes over — means they enter the hardest years with a daily "
            "anchor already in place."
        ),
    },
    {
        "slug": "christ-social-media-ethics-age12",
        "title": "Apply Christian Ethics to Your Social Media Life",
        "category": "social",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Apply the Philippians 4:8 filter to your feed**: *'Whatever is true, "
            "whatever is noble, whatever is right, whatever is pure, whatever is lovely, "
            "whatever is admirable — think about such things.'* Does your feed pass "
            "this test? Audit it.\n"
            "2. **Before posting, ask four questions**: Is it true? Is it kind? "
            "Is it necessary? Would I say this to the person's face?\n"
            "3. **Identify prohibited online behaviours**: mocking, spreading rumours, "
            "sharing unverified news, following content that weakens your faith or purity.\n"
            "4. **Set a daily time limit** for social media — and keep it.\n"
            "5. **Use it for good**: encourage someone, share something life-giving, "
            "check on a friend who seems lonely."
        ),
        "parent_note_md": (
            "Philippians 4:8 is the most applicable scripture to digital life — written "
            "2,000 years before the internet, it describes exactly the mental diet that "
            "social media violates. Paul also warns: *'Do not be misled: bad company "
            "corrupts good character'* (1 Corinthians 15:33) — and digital company is "
            "still company. The average 12-year-old now spends 5+ hours per day on "
            "screens. Christian ethics are not an add-on to digital life — they are the "
            "lens through which every post, follow, and message should be evaluated. "
            "Age 12 is when most children enter social media — this task should come first."
        ),
    },
    {
        "slug": "christ-christian-hero-age12",
        "title": "Study the Life of a Christian Hero or Saint",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose one person** to study — suggestions by tradition:\n"
            "   - Catholic/Orthodox: St Francis of Assisi, St Teresa of Calcutta, "
            "St Thérèse of Lisieux\n"
            "   - Protestant: William Wilberforce, Dietrich Bonhoeffer, "
            "Corrie ten Boom, C.S. Lewis\n"
            "   - Evangelical/missionary: Hudson Taylor, Amy Carmichael, Jim Elliot\n"
            "2. **Read a biography** — not a summary, but a full account.\n"
            "3. **Extract 5 character lessons**: what did they do that cost them? "
            "What does their life say about faith, sacrifice, and calling?\n"
            "4. **Discuss**: how does their life challenge your comfortable Christianity?\n"
            "5. **Share what you learnt** — write a paragraph or explain to the family."
        ),
        "parent_note_md": (
            "Hebrews 12:1 says: *'Therefore, since we are surrounded by such a great "
            "cloud of witnesses, let us throw off everything that hinders and the sin "
            "that so easily entangles.'* The 'cloud of witnesses' is the communion of "
            "saints — Christians who have gone before us and whose lives testify to "
            "the faithfulness of God. At age 12, young people need concrete, historical "
            "role models who were real Christians facing real choices — not abstract "
            "ideals. Bonhoeffer stood against Hitler. Wilberforce spent 20 years "
            "fighting slavery. These lives make faith tangible and costly."
        ),
    },
    {
        "slug": "christ-guard-speech-age12",
        "title": "Guard Your Speech — Only Words That Build Up",
        "category": "social",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Ephesians 4:29**: *'Do not let any unwholesome talk come out of "
            "your mouths, but only what is helpful for building others up according to "
            "their needs, that it may benefit those who listen.'*\n"
            "2. **Do a 24-hour speech audit**: for one day, mentally note every time you "
            "say something hurtful, sarcastic, false, or unnecessary.\n"
            "3. **Identify patterns**: gossip? Complaining? Putting others down for laughs? "
            "Exaggerating? These are all speech sins.\n"
            "4. **Apply the three gates**: before speaking — Is it true? Is it kind? "
            "Is it necessary? If it fails two out of three, don't say it.\n"
            "5. **Replace negative speech with affirmation**: say one genuine "
            "encouraging thing to someone every day."
        ),
        "parent_note_md": (
            "James dedicates an entire chapter to the tongue: *'The tongue is a small "
            "part of the body, but it makes great boasts. Consider what a great forest "
            "is set on fire by a small spark'* (James 3:5, NIV). Proverbs 18:21: "
            "*'The tongue has the power of life and death.'* At age 12, children's "
            "social lives are increasingly built through language — group chats, "
            "banter, and social positioning through speech. Gossip, exclusion, and "
            "mockery peak in early adolescence. Grounding speech ethics in scripture "
            "at this age gives children a clear standard before the social pressures "
            "of secondary school intensify."
        ),
    },
    {
        "slug": "christ-exam-conscience-age12",
        "title": "Practice the Daily Examination of Conscience",
        "category": "household",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Before bed, spend 5 minutes** reviewing the day honestly with God.\n"
            "2. **Use five simple questions**:\n"
            "   - What am I most grateful for today?\n"
            "   - Where did I feel God's presence?\n"
            "   - Where did I fail to love — God, others, myself?\n"
            "   - What do I need to ask forgiveness for?\n"
            "   - What will I ask God's help with tomorrow?\n"
            "3. **Be specific** — not 'I was a bit unkind' but 'I mocked James in "
            "front of his friends and it was wrong.'\n"
            "4. **Receive forgiveness** — don't wallow, don't dismiss. "
            "1 John 1:9: confess, receive, move forward.\n"
            "5. **Write one line in a journal** each night — a single honest sentence."
        ),
        "parent_note_md": (
            "Lamentations 3:40 says: *'Let us examine our ways and test them, and let "
            "us return to the Lord.'* Paul writes: *'Examine yourselves to see whether "
            "you are in the faith; test yourselves'* (2 Corinthians 13:5). The Daily "
            "Examen (practised by Ignatius of Loyola and many other traditions) is one "
            "of the most ancient and effective tools of Christian spiritual formation. "
            "It builds self-awareness, gratitude, and accountability before God. "
            "At age 12, developing emotional self-awareness and moral honesty are "
            "equally important — this practice serves both simultaneously."
        ),
    },
    {
        "slug": "christ-care-poor-age12",
        "title": "Actively Care for the Poor and Vulnerable in Your Community",
        "category": "financial",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Identify one person or group** who is poor or vulnerable in your "
            "immediate community — not abstractly, but someone real.\n"
            "2. **Take concrete action this month**: volunteer at a food bank, collect "
            "clothing, help an elderly neighbour with shopping, fundraise for a "
            "family in need.\n"
            "3. **Give sacrificially**: not from surplus, but from what you were "
            "going to spend on yourself. Make it feel like something.\n"
            "4. **Read James 2:14–17**: faith without action for the poor is dead faith.\n"
            "5. **Discuss systemic poverty**: why are people poor? What does the Bible "
            "say about justice, not just charity? (Micah 6:8, Amos 5:24)"
        ),
        "parent_note_md": (
            "Proverbs 19:17: *'Whoever is kind to the poor lends to the Lord, and he "
            "will reward them for what they have done.'* James is direct: *'Suppose a "
            "brother or a sister is without clothes and daily food. If one of you says "
            "to them, 'Go in peace; keep warm and well fed,' but does nothing about "
            "their physical needs, what good is it?'* (James 2:15–16). Isaiah 58:7 "
            "defines the true fast as sharing food with the hungry. Active care for "
            "the poor is not a social justice option — it is a consistent command "
            "throughout both Testaments. Teaching it practically at age 12 forms "
            "a lifelong posture of justice."
        ),
    },
    {
        "slug": "christ-body-temple-age12",
        "title": "Understand Your Body as a Temple of the Holy Spirit",
        "category": "cognitive",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 Corinthians 6:19–20**: *'Do you not know that your bodies are "
            "temples of the Holy Spirit, who is in you, whom you have received from God? "
            "You are not your own; you were bought at a price. Therefore honour God "
            "with your bodies.'*\n"
            "2. **Apply it practically — the body is a temple means**:\n"
            "   - Sleep: 8–9 hours is stewardship, not laziness\n"
            "   - Food: eating well is an act of worship\n"
            "   - Substance avoidance: drugs, alcohol, tobacco harm the temple\n"
            "   - Sexual purity: the body is not for casual use\n"
            "   - Exercise: physical health serves spiritual purpose\n"
            "3. **Discuss the cost**: *'You were bought at a price'* — Jesus's death "
            "gives your body infinite value. It is not yours to misuse.\n"
            "4. **Set one body-stewardship goal** this month."
        ),
        "parent_note_md": (
            "1 Corinthians 6:19–20 is the theological foundation for Christian ethics "
            "of the body — covering sexuality, substance use, health, and physical care. "
            "Romans 12:1 extends this: *'Offer your bodies as a living sacrifice, holy "
            "and pleasing to God — this is your true and proper worship.'* At age 12, "
            "children are entering puberty — the age when questions about the body, "
            "sexuality, substances, and peer pressure become live issues. Grounding "
            "bodily ethics in theology ('you are a temple') rather than mere rules "
            "gives them a foundation that lasts because it is rooted in identity, "
            "not just prohibition."
        ),
    },
    {
        "slug": "christ-good-neighbour-age12",
        "title": "Be a Good Samaritan — Neighbour Love in Real Life",
        "category": "social",
        "min_age": 12, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Luke 10:25–37** — the Parable of the Good Samaritan in full.\n"
            "2. **Note the three responses**: the priest passed by, the Levite passed by, "
            "the Samaritan stopped and helped — at personal cost and inconvenience.\n"
            "3. **Identify your 'wounded man'**: who in your life is struggling and being "
            "overlooked? The new student? The isolated classmate? The neighbour nobody "
            "visits?\n"
            "4. **Take action this week** — not a vague intention but a concrete act: "
            "sit with them, invite them, help them, visit them.\n"
            "5. **Discuss the cost**: the Samaritan gave time, money, and inconvenience. "
            "Jesus is asking if we will do the same."
        ),
        "parent_note_md": (
            "When a lawyer asked *'Who is my neighbour?'*, Jesus answered with a story "
            "rather than a definition (Luke 10:29–37). The answer was radical: your "
            "neighbour is anyone in need, regardless of their background, race, or "
            "religion — and the man who hated Samaritans had to hear that from a "
            "Samaritan. Jesus closed the parable with a command, not a suggestion: "
            "*'Go and do likewise'* (Luke 10:37). At age 12, the social dynamics of "
            "secondary school create constant opportunities to either pass by or stop — "
            "this parable is the most practical guide to those decisions."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 13
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-sermon-on-mount-age13",
        "title": "Study the Sermon on the Mount (Matthew 5–7) in Depth",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 5–7 in one sitting** first — get the whole sweep before "
            "breaking it down.\n"
            "2. **Study it section by section over 4 weeks**:\n"
            "   - Week 1: The Beatitudes (5:3–12) — the character of Kingdom people\n"
            "   - Week 2: Salt, light, the Law fulfilled, anger, lust, divorce, oaths "
            "(5:13–48) — Jesus raises the bar\n"
            "   - Week 3: Giving, prayer, fasting, money, worry (6:1–34) — "
            "the hidden life of faith\n"
            "   - Week 4: Judging, prayer, the narrow gate, false prophets, "
            "two builders (7:1–29) — discernment and decision\n"
            "3. **Identify one verse per section** that most challenges you and write "
            "it down.\n"
            "4. **Pick one teaching** and apply it deliberately for one week."
        ),
        "parent_note_md": (
            "Matthew 7:28–29 records the crowd's reaction: *'When Jesus had finished "
            "saying these things, the crowds were amazed at his teaching, because he "
            "taught as one who had authority, and not as their teachers of the law.'* "
            "The Sermon on the Mount is the most concentrated block of Jesus's moral "
            "and spiritual teaching in the Gospels. It systematically inverts cultural "
            "values — on anger, lust, retaliation, money, worry, and judgement. "
            "At age 13, young people are forming their own moral worldview — studying "
            "the Sermon on the Mount gives them a comprehensive counter-cultural "
            "framework rooted in Jesus's own words."
        ),
    },
    {
        "slug": "christ-personal-faith-commitment-age13",
        "title": "Make a Personal, Conscious Commitment of Faith",
        "category": "cognitive",
        "min_age": 13, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Discuss the difference** between inherited faith (believing because "
            "your parents do) and personal faith (believing because you have examined "
            "it and chosen it yourself).\n"
            "2. **Read Romans 10:9–10**: *'If you declare with your mouth, 'Jesus is "
            "Lord,' and believe in your heart that God raised him from the dead, you "
            "will be saved.'*\n"
            "3. **Reflect honestly**: Do I actually believe this? Have I ever personally "
            "responded to the gospel — not just attended church?\n"
            "4. **For those in traditions with Confirmation**: engage the preparation "
            "seriously as a genuine act of faith, not a rite of passage.\n"
            "5. **For all**: write a personal statement of faith — what you believe "
            "and why — in your own words."
        ),
        "parent_note_md": (
            "Faith cannot be inherited — it must be personally appropriated. John "
            "says: *'Yet to all who did receive him, to those who believed in his name, "
            "he gave the right to become children of God'* (John 1:12, NIV). "
            "Confirmation in Catholic, Anglican, Lutheran, and Methodist traditions "
            "is designed to be exactly this — the personal ownership of baptismal "
            "promises. For Evangelical traditions, this is the moment of personal "
            "conversion or recommitment. Age 13 is the average age of genuine "
            "faith questioning — engaging it honestly at this point is far more "
            "valuable than suppressing the questions."
        ),
    },
    {
        "slug": "christ-proverbs-wisdom-age13",
        "title": "Read and Apply the Book of Proverbs for Daily Wisdom",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read one chapter per day**: Proverbs has 31 chapters — one per day "
            "maps to any month of the year.\n"
            "2. **Proverbs 1:7 is the key**: *'The fear of the Lord is the beginning "
            "of wisdom'* — read everything else in light of this.\n"
            "3. **Identify the themes**: wisdom vs folly, speech, money, friendship, "
            "work, relationships, integrity, pride, and humility.\n"
            "4. **Write down one proverb per week** that speaks directly to a "
            "current situation in your life.\n"
            "5. **Apply it specifically**: 'This week I will apply Proverbs 15:1 — "
            "'a gentle answer turns away wrath' — in my response to my brother/sister.'"
        ),
        "parent_note_md": (
            "Proverbs was written largely by Solomon, described as the wisest man who "
            "ever lived (1 Kings 4:29–30), as a guide for young people: *'for gaining "
            "wisdom and instruction; for understanding words of insight; for receiving "
            "instruction in prudent behaviour'* (Proverbs 1:2–3, NIV). At age 13, "
            "adolescents face daily decisions about friendship, speech, money, work "
            "habits, and relationships — Proverbs addresses all of these with "
            "concentrated practical wisdom. Reading one chapter per day means it "
            "can be completed monthly, repeatedly, building a deep reservoir "
            "of biblical common sense."
        ),
    },
    {
        "slug": "christ-modesty-dignity-age13",
        "title": "Understand Christian Modesty — Dressing and Behaving with Dignity",
        "category": "social",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Understand modesty as an inward value** first — it is about "
            "dignity, respect, and not drawing attention to the wrong things, "
            "not just rules about hemlines.\n"
            "2. **Read 1 Timothy 2:9–10**: modesty in dress connected to good deeds — "
            "your actions should be what stands out, not your appearance.\n"
            "3. **Audit your wardrobe honestly**: does your clothing honour your "
            "body as a temple? Does it invite the right kind of attention?\n"
            "4. **Discuss modesty for both sexes**: it is not only a female issue — "
            "boys have equal responsibility (Matthew 5:28 addresses the male gaze).\n"
            "5. **Apply to behaviour**: modesty also means not boasting, not "
            "dominating conversations, not making everything about yourself."
        ),
        "parent_note_md": (
            "1 Timothy 2:9 addresses outward dress; 1 Peter 3:3–4 points to "
            "inward character: *'Your beauty should not come from outward adornment… "
            "Rather, it should be that of your inner self, the unfading beauty of "
            "a gentle and quiet spirit, which is of great worth in God's sight.'* "
            "Matthew 5:28 addresses the male responsibility for their thought life. "
            "Modesty is not about covering up out of shame — the body is good "
            "(Genesis 1:31). It is about communicating dignity and directing "
            "attention appropriately. At 13, peer pressure around appearance "
            "and social media presentation peaks — a positive, dignified "
            "theology of the body is the best antidote."
        ),
    },
    {
        "slug": "christ-peer-pressure-age13",
        "title": "Stand Firm Under Peer Pressure with Christian Values",
        "category": "social",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Romans 12:2**: *'Do not conform to the pattern of this world, "
            "but be transformed by the renewing of your mind.'* — memorise it.\n"
            "2. **Identify your three biggest pressure points**: areas where you are "
            "most tempted to compromise your faith to fit in.\n"
            "3. **Prepare responses in advance**: if someone offers drugs — 'No thanks, "
            "that's not for me.' Rehearsed responses reduce in-the-moment panic.\n"
            "4. **Build a support person**: identify one friend who shares your values "
            "and agree to hold each other accountable.\n"
            "5. **Discuss the difference** between fitting in (changing who you are) "
            "and belonging (being accepted for who you are). "
            "Jesus offers the latter — the world offers only the former."
        ),
        "parent_note_md": (
            "Romans 12:2 is Paul's foundational statement on counter-cultural living. "
            "Peter adds: *'Dear friends, I urge you, as foreigners and exiles, to "
            "abstain from sinful desires, which wage war against your soul'* "
            "(1 Peter 2:11, NIV). The teenage years are the peak window for peer "
            "conformity pressure — neurologically, the adolescent brain is highly "
            "sensitive to social acceptance and rejection. Children who have a clear "
            "sense of identity in Christ ('I am a child of God — that defines me, "
            "not what my peers think') navigate this pressure with fundamentally "
            "different resources than those whose identity is entirely peer-derived."
        ),
    },
    {
        "slug": "christ-prayer-journal-age13",
        "title": "Keep a Personal Prayer Journal",
        "category": "household",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Buy a dedicated notebook** — physical, not digital. Something "
            "that feels worth writing in.\n"
            "2. **Structure each entry**:\n"
            "   - Date and one-line 'where I am today'\n"
            "   - Thanksgiving: 3 specific things I'm grateful for\n"
            "   - Confession: one honest thing to bring to God\n"
            "   - Intercession: 3 people I'm praying for today\n"
            "   - Personal request: what I need\n"
            "   - Scripture: one verse I'm sitting with\n"
            "3. **Write to God** — not about prayer but to Him, as a letter.\n"
            "4. **Review monthly**: look back at what you prayed for. Mark answered "
            "prayers. Build a record of God's faithfulness.\n"
            "5. **Keep it private**: this is between you and God."
        ),
        "parent_note_md": (
            "Paul writes: *'Do not be anxious about anything, but in every situation, "
            "by prayer and petition, with thanksgiving, present your requests to God'* "
            "(Philippians 4:6, NIV). The Psalms are themselves a prayer journal — "
            "David wrote with raw emotional honesty, bringing everything to God. "
            "A prayer journal serves three purposes simultaneously: it deepens prayer "
            "(writing forces clarity), it builds faith (answered prayers are recorded), "
            "and it develops emotional and spiritual self-awareness. At 13, adolescents "
            "are forming their inner life — a prayer journal gives that inner life "
            "a God-directed channel."
        ),
    },
    {
        "slug": "christ-community-service-age13",
        "title": "Volunteer Regularly to Serve Your Community",
        "category": "household",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a regular volunteering commitment** — not a one-off but "
            "monthly or weekly: food bank, homeless shelter, elderly care home, "
            "church children's ministry, hospital visiting, environmental project.\n"
            "2. **Commit to it for at least 3 months** — long enough to build "
            "relationships, not just complete a task.\n"
            "3. **Go beyond giving things** — give time and presence. The person "
            "you serve needs to be seen and known, not just fed.\n"
            "4. **Reflect after each session**: what did I notice? What was hard? "
            "What did I learn about myself? What did I see of God?\n"
            "5. **Bring a friend** — shared service deepens both relationships "
            "and impact."
        ),
        "parent_note_md": (
            "Matthew 25:40: *'Whatever you did for one of the least of these brothers "
            "and sisters of mine, you did for me.'* Galatians 5:13: *'Serve one another "
            "humbly in love.'* Research by Christian Smith (University of Notre Dame) "
            "shows that teenagers who regularly serve others have significantly higher "
            "faith retention, lower depression rates, and stronger social skills. "
            "Service at age 13 is particularly powerful because it happens at the "
            "exact developmental moment when identity is being formed — it answers "
            "the question 'Who am I?' with 'Someone who gives, not just takes.'"
        ),
    },
    {
        "slug": "christ-faith-and-works-age13",
        "title": "Understand That Faith Without Works Is Dead",
        "category": "cognitive",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read James 2:14–26** — the clearest statement on faith and works.\n"
            "2. **Resolve the apparent tension with Paul**: Paul says we are saved by "
            "faith alone (Ephesians 2:8–9); James says faith without works is dead. "
            "Both are true — Paul addresses how we are saved; James addresses how "
            "we know saving faith is real. True faith produces works naturally.\n"
            "3. **Apply the test**: if you say you have faith but nothing in your life "
            "has changed — your time, money, relationships, priorities — is it real?\n"
            "4. **List three areas** where your faith should be producing visible "
            "fruit and isn't.\n"
            "5. **Discuss the difference** between earning salvation (impossible) "
            "and demonstrating it (inevitable if genuine)."
        ),
        "parent_note_md": (
            "James 2:17 is unambiguous: *'Faith by itself, if it is not accompanied "
            "by action, is dead.'* This does not contradict Paul — Luther famously "
            "called James 'an epistle of straw' but later came to see that James "
            "and Paul address different questions. Paul says works don't save; "
            "James says real saving faith always produces works. At age 13, "
            "children are capable of engaging this theological nuance. "
            "Understanding it prevents both legalism (earning God's favour through "
            "works) and antinomianism (believing faith permits any behaviour). "
            "It is one of the most practically important theological distinctions "
            "a Christian teenager can grasp."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 14
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-apologetics-age14",
        "title": "Learn to Explain and Defend Your Faith (Basic Apologetics)",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 Peter 3:15**: *'Always be prepared to give an answer to "
            "everyone who asks you to give the reason for the hope that you have. "
            "But do this with gentleness and respect.'*\n"
            "2. **Master five basic questions** with a thoughtful answer for each:\n"
            "   - Why do you believe God exists?\n"
            "   - How do you know the Bible is reliable?\n"
            "   - Didn't Jesus just exist as a good teacher?\n"
            "   - If God is good, why does suffering exist?\n"
            "   - Aren't all religions the same?\n"
            "3. **Read one apologetics book** at an accessible level — e.g. C.S. Lewis's "
            "*Mere Christianity* or *The Case for Christ* by Lee Strobel.\n"
            "4. **Practise with a trusted adult** playing the sceptic.\n"
            "5. **Remember the posture**: gentleness and respect always, not argument "
            "and superiority."
        ),
        "parent_note_md": (
            "1 Peter 3:15 commands readiness to explain — *apologia* in Greek means "
            "a prepared defence. This does not mean hostile debate but thoughtful, "
            "gentle, reasoned engagement. Paul reasoned in the synagogues and the "
            "marketplace (Acts 17:17). C.S. Lewis said: *'Christianity, if false, is "
            "of no importance, and if true, of infinite importance. The only thing "
            "it cannot be is moderately important.'* At age 14, teenagers face "
            "direct challenges to their faith from peers, teachers, and media. "
            "Children who cannot articulate why they believe often quietly abandon "
            "faith not because they stopped believing but because they couldn't "
            "answer the questions."
        ),
    },
    {
        "slug": "christ-christian-martyrs-age14",
        "title": "Study the Lives of Christian Martyrs and Their Witness",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Study three martyrs in depth** — one from each era:\n"
            "   - Early church: Polycarp (burned at the stake, 155 AD) or "
            "Stephen (Acts 7)\n"
            "   - Reformation: William Tyndale (strangled for translating the Bible) "
            "or Thomas More\n"
            "   - Modern: Dietrich Bonhoeffer (killed by Nazis), Jim Elliot "
            "(killed by Auca tribe, 1956), or Perpetua (2nd century)\n"
            "2. **For each, note**: what did they believe so strongly they died for it? "
            "What does their death say about the truth of Christianity?\n"
            "3. **Read Jim Elliot's journal entry**: *'He is no fool who gives what "
            "he cannot keep to gain what he cannot lose.'*\n"
            "4. **Discuss costly faith**: what would you be willing to sacrifice "
            "for your faith?"
        ),
        "parent_note_md": (
            "Hebrews 11 — the 'Hall of Faith' — lists those who *'were put to death "
            "by the sword… they went about in sheepskins and goatskins, destitute, "
            "persecuted and mistreated'* (Hebrews 11:37, NIV). Revelation 12:11: "
            "*'They triumphed over him by the blood of the Lamb and by the word of "
            "their testimony; they did not love their lives so much as to shrink "
            "from death.'* Martyrs are the strongest apologetic for the truth of "
            "Christianity — people do not die for what they know to be a lie. "
            "At 14, studying costly faith confronts comfortable Christianity and "
            "raises the question every young Christian must eventually answer: "
            "Is this worth everything?"
        ),
    },
    {
        "slug": "christ-bible-reading-plan-age14",
        "title": "Build and Maintain a Structured Daily Bible Reading Plan",
        "category": "household",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a reading plan** with a fixed daily portion:\n"
            "   - McCheyne's plan: OT + NT daily, whole Bible in a year\n"
            "   - Chronological Bible plan: events in historical order\n"
            "   - SOAP method: Scripture → Observe → Apply → Pray\n"
            "2. **Fix a time**: 15–20 minutes every morning before school. "
            "Before breakfast if possible — it sets the tone for the day.\n"
            "3. **Don't catch up**: if you miss a day, skip it and continue — "
            "guilt about gaps kills the habit faster than the gaps do.\n"
            "4. **Use a journal alongside**: one insight, one application, "
            "one prayer per reading session.\n"
            "5. **Track completion**: a simple tick per day builds momentum. "
            "Aim for 300 out of 365 days in a year — not perfection."
        ),
        "parent_note_md": (
            "Joshua 1:8: *'Keep this Book of the Law always on your lips; meditate "
            "on it day and night, so that you may be careful to do everything written "
            "in it. Then you will be prosperous and successful.'* Psalm 119:105: "
            "*'Your word is a lamp for my feet, a light on my path.'* A structured "
            "Bible reading plan is different from casual reading — it ensures the "
            "whole counsel of Scripture is encountered, not just favourite passages. "
            "At age 14, teenagers can sustain adult-level spiritual disciplines. "
            "Establishing a reading plan now means they enter university and "
            "independent life with a self-sufficient faith practice already in place."
        ),
    },
    {
        "slug": "christ-relationships-values-age14",
        "title": "Understand Christian Values in Friendships and Relationships",
        "category": "social",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 2 Corinthians 6:14**: *'Do not be yoked together with "
            "unbelievers. For what do righteousness and wickedness have in common?'* "
            "— discuss what this means practically (it does not mean avoid all "
            "non-Christians, but close partnerships need shared values).\n"
            "2. **Identify the qualities of a God-honouring friendship**: honest, "
            "encouraging, accountable, faith-building — not just fun.\n"
            "3. **Evaluate current close friendships**: do they draw you closer to "
            "God or further away? Do they make you more or less like Jesus?\n"
            "4. **Discuss romantic relationships** with a trusted Christian adult: "
            "what does it mean to honour someone you date? What are your boundaries "
            "and why?\n"
            "5. **Invest intentionally** in the friendships that make you better."
        ),
        "parent_note_md": (
            "Proverbs 13:20: *'Walk with the wise and become wise, for a companion "
            "of fools suffers harm.'* 1 Corinthians 15:33: *'Bad company corrupts "
            "good character.'* At age 14, romantic relationships and deep friendships "
            "begin to become central to identity formation. Christian guidance on "
            "these relationships is not about restriction but protection — the goal "
            "is relationships that are life-giving, respectful, and God-honouring. "
            "The question is not 'how far can I go?' but 'how can I best honour "
            "this person and God in this relationship?' — a fundamentally different "
            "starting point."
        ),
    },
    {
        "slug": "christ-sexual-purity-age14",
        "title": "Understand Christian Sexual Ethics and the Dignity of the Body",
        "category": "social",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 Corinthians 6:18–20** and 1 Thessalonians 4:3–5 — "
            "the clearest New Testament statements on sexual purity.\n"
            "2. **Ground it positively**: the body is a temple (1 Cor 6:19), "
            "sexuality is a gift created by God (Genesis 2:24), designed for "
            "a specific context — not to restrict but to protect.\n"
            "3. **Address pornography directly**: it is incompatible with "
            "honouring the body and violates Matthew 5:28. Discuss practically "
            "what to do if you've encountered it or struggle with it.\n"
            "4. **Talk about accountability**: have a trusted same-sex adult "
            "you can speak honestly to about these struggles.\n"
            "5. **Pray together** — purity is sustained by the Spirit "
            "(Galatians 5:16), not by willpower alone."
        ),
        "parent_note_md": (
            "1 Corinthians 6:18–19: *'Flee from sexual immorality… Do you not know "
            "that your bodies are temples of the Holy Spirit?'* The average age of "
            "first exposure to pornography is now 11 — by age 14, most children "
            "have encountered it. Silence on this topic is not protection. "
            "Christian sexual ethics are not primarily about prohibition — they "
            "are a theology of the body rooted in the goodness of creation, the "
            "dignity of persons, and the design of covenant. Children who understand "
            "the 'why' are far better equipped than those given only the 'don't.' "
            "The most effective protection is a positive vision, not just a rule."
        ),
    },
    {
        "slug": "christ-gratitude-journal-age14",
        "title": "Keep a Gratitude Journal Grounded in Scripture",
        "category": "cognitive",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 Thessalonians 5:16–18**: *'Rejoice always, pray continually, "
            "give thanks in all circumstances; for this is God's will for you in "
            "Christ Jesus.'*\n"
            "2. **Each evening, write three things** you are genuinely grateful for — "
            "specific, not generic. Not 'my family' but 'Mum making my favourite "
            "dinner tonight without being asked.'\n"
            "3. **Link each to God**: 'I'm grateful for ___ because it shows me "
            "God is ___.' (Provider, Faithful, Present, Good, etc.)\n"
            "4. **On hard days**, still write three — gratitude in difficulty is "
            "specifically what Paul commands: 'in all circumstances.'\n"
            "5. **Review your journal monthly**: what patterns do you see? "
            "What does God consistently provide for you?"
        ),
        "parent_note_md": (
            "Gratitude is not a personality trait — it is a spiritual discipline. "
            "Paul commands it regardless of circumstances (Philippians 4:11–12: "
            "*'I have learned, in whatever state I am, to be content'*). Research "
            "by psychologist Robert Emmons shows that daily gratitude journalling "
            "produces measurable improvements in wellbeing, sleep, relationships, "
            "and resilience. At 14, adolescents are prone to negativity bias and "
            "comparison culture (amplified by social media) — a daily gratitude "
            "practice, rooted in God's character rather than mere positivity, "
            "is one of the most effective practical interventions available."
        ),
    },
    {
        "slug": "christ-social-justice-age14",
        "title": "Understand and Act on Biblical Justice",
        "category": "financial",
        "min_age": 14, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Micah 6:8**: *'He has shown you, O mortal, what is good. And "
            "what does the Lord require of you? To act justly and to love mercy and "
            "to walk humbly with your God.'*\n"
            "2. **Study three biblical justice themes**:\n"
            "   - Care for the poor and widow (Deuteronomy 15:11, James 1:27)\n"
            "   - Justice in the courts and marketplace (Amos 5:24, Proverbs 11:1)\n"
            "   - Care for the foreigner and stranger (Leviticus 19:34, Matthew 25:35)\n"
            "3. **Choose one justice issue** that matters to you and research it "
            "through a biblical lens: poverty, modern slavery, racial justice, "
            "creation care.\n"
            "4. **Take one concrete action**: volunteer, donate, advocate, raise "
            "awareness among peers.\n"
            "5. **Discuss the distinction**: charity addresses immediate need; "
            "justice addresses the structures that create the need."
        ),
        "parent_note_md": (
            "Amos 5:24: *'But let justice roll on like a river, righteousness like "
            "a never-failing stream.'* Isaiah 1:17: *'Learn to do right; seek "
            "justice. Defend the oppressed. Take up the cause of the fatherless; "
            "plead the case of the widow.'* Biblical justice is not a political "
            "category — it is a consistent demand of both Testaments. "
            "At age 14, young Christians are developing social awareness and "
            "passion. Grounding that passion in scripture rather than only in "
            "cultural movements gives it stability, humility, and depth. "
            "William Wilberforce, Martin Luther King Jr., and Jackie Pullinger "
            "were all motivated primarily by biblical conviction — not politics."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 15
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-christian-worldview-age15",
        "title": "Develop a Christian Worldview — See All of Life Through Scripture",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Romans 12:2**: *'Do not conform to the pattern of this world, "
            "but be transformed by the renewing of your mind.'* — a Christian "
            "worldview is a renewed mind.\n"
            "2. **Learn the four-chapter framework**: Creation (the world was good) → "
            "Fall (sin broke everything) → Redemption (Jesus restores) → "
            "New Creation (the final renewal). Apply this framework to any issue.\n"
            "3. **Practice on current topics** at school: evolution, sexuality, "
            "justice, mental health, politics — ask 'What does scripture say about "
            "the underlying question here?'\n"
            "4. **Read one book** that applies Christian thinking to culture — "
            "C.S. Lewis's *Mere Christianity*, Francis Schaeffer's *How Should We "
            "Then Live?*, or Tim Keller's *The Reason for God*.\n"
            "5. **Discuss with a trusted adult** — not to get the 'right answers' "
            "but to practise thinking Christianly."
        ),
        "parent_note_md": (
            "Paul's command in Romans 12:2 is comprehensive — the Christian mind "
            "is not just for 'religious' topics. Colossians 2:8 warns: *'See to it "
            "that no one takes you captive through hollow and deceptive philosophy, "
            "which depends on human tradition and the elemental spiritual forces of "
            "this world rather than on Christ.'* At 15, young people are immersed "
            "in a secular educational worldview — science, history, ethics, and "
            "social studies are all framed outside a Christian framework. A teenager "
            "who can think Christianly about these subjects — not defensively but "
            "confidently — is prepared for university and independent life."
        ),
    },
    {
        "slug": "christ-theology-of-suffering-age15",
        "title": "Understand Why Christians Suffer — and How to Respond",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Romans 5:3–5**: *'We also glory in our sufferings, because we "
            "know that suffering produces perseverance; perseverance, character; "
            "and character, hope.'* Suffering has a purpose.\n"
            "2. **Study three people in scripture** who suffered deeply and what "
            "they learnt: Job (suffering and God's sovereignty), Joseph (betrayal "
            "turned to purpose — Genesis 50:20), Paul (thorn in the flesh — "
            "2 Corinthians 12:7–10).\n"
            "3. **Address the question honestly**: 'If God is good, why does He "
            "allow suffering?' — explore both the intellectual answer (free will, "
            "fallen world, greater purposes) and the pastoral response "
            "(God suffers with us — Isaiah 53:3).\n"
            "4. **Apply personally**: identify a current difficulty and ask — "
            "what is God producing in me through this?"
        ),
        "parent_note_md": (
            "The question of suffering is the number one reason people leave or "
            "reject faith. James 1:2–4 is striking: *'Consider it pure joy, my "
            "brothers and sisters, whenever you face trials of many kinds, because "
            "you know that the testing of your faith produces perseverance.'* "
            "This is not masochism — it is a theology of growth through resistance. "
            "Peter adds: *'These trials will show that your faith is genuine… "
            "more precious than gold'* (1 Peter 1:7, NLT). At 15, young people "
            "are old enough to have experienced real suffering — bereavement, "
            "family breakdown, illness, social rejection. A robust theology of "
            "suffering is not optional preparation; it is essential equipment."
        ),
    },
    {
        "slug": "christ-share-your-faith-age15",
        "title": "Learn to Share Your Faith Story (Testimony)",
        "category": "social",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Write your testimony** in three parts:\n"
            "   - Before: what was your life/thinking like before faith became real?\n"
            "   - Turning point: what happened? When did faith become personal?\n"
            "   - After: what has changed? How does your faith affect your life now?\n"
            "2. **Keep it under 3 minutes** — practise saying it aloud until it is "
            "natural, not rehearsed-sounding.\n"
            "3. **Remove jargon**: say 'I started trusting God' not 'I got saved.' "
            "Say 'my perspective changed' not 'I was convicted.' Speak to be "
            "understood by someone with no church background.\n"
            "4. **Practise with family first**, then a friend, then a wider audience.\n"
            "5. **Discuss when to share it**: not forced, but when conversations "
            "naturally open — 'Can I tell you something that's made a big difference "
            "to me?'"
        ),
        "parent_note_md": (
            "Peter commands readiness to share: *'Always be prepared to give an "
            "answer to everyone who asks you to give the reason for the hope that "
            "you have. But do this with gentleness and respect'* (1 Peter 3:15, NIV). "
            "Revelation 12:11 says believers overcame *'by the blood of the Lamb "
            "and by the word of their testimony.'* A personal testimony is one of "
            "the most powerful evangelistic tools because it cannot be argued with — "
            "it is a first-person account of experience. At 15, teenagers have a "
            "genuine faith story forming. Teaching them to articulate it respectfully "
            "and naturally is both discipleship and preparation for the Great Commission."
        ),
    },
    {
        "slug": "christ-choose-friends-age15",
        "title": "Choose Friends Who Strengthen Your Faith",
        "category": "social",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 Corinthians 15:33**: *'Do not be misled: bad company "
            "corrupts good character.'* — this is not judgement, it is observation.\n"
            "2. **List your five closest friends** and answer honestly for each: "
            "Does this friendship make me more like Jesus or less? More loving, "
            "honest, and faithful — or more selfish, dishonest, and faithless?\n"
            "3. **Invest deliberately** in the friendships that build you up. "
            "Don't abandon others — but be intentional about where you place "
            "your closest trust.\n"
            "4. **Be the friend you are looking for**: if you want honest, "
            "faith-building friendships, be those things first.\n"
            "5. **Find an accountability partner** — one same-sex friend who "
            "has permission to ask hard questions and tell you the truth."
        ),
        "parent_note_md": (
            "Proverbs 27:17: *'As iron sharpens iron, so one person sharpens another.'* "
            "The New Testament vision of friendship is mutual sharpening — friends "
            "who make each other more like Christ. At 15, peer influence peaks "
            "neurologically — the social reward systems of the adolescent brain "
            "are highly sensitive. This makes peer selection at this age one of "
            "the most consequential choices a young person makes. It is not about "
            "avoiding non-Christians — Jesus ate with sinners — but about where "
            "closest intimacy and influence are placed. The accountability "
            "partnership (Galatians 6:1–2) is one of the most protective "
            "relationships a Christian teenager can have."
        ),
    },
    {
        "slug": "christ-fasting-regular-age15",
        "title": "Establish a Regular Personal Fasting Practice",
        "category": "household",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a rhythm** — weekly (every Friday), monthly (one day), "
            "or seasonal (Lent, Advent). Commit to it for 3 months.\n"
            "2. **On fasting days**: skip one or two meals. Use the time you would "
            "have eaten for extended prayer and Bible reading.\n"
            "3. **Read Isaiah 58:6–7** — God's chosen fast is both spiritual "
            "discipline and social action: loose chains of injustice, share food "
            "with the hungry. Pair your fast with a concrete act of giving.\n"
            "4. **Examine your relationship with comfort**: what does hunger reveal "
            "about what you depend on? Let physical discomfort drive you to God.\n"
            "5. **Keep it private** (Matthew 6:18) — fasting for God's eyes only "
            "is the only form that has spiritual value."
        ),
        "parent_note_md": (
            "Jesus assumes His disciples will fast: *'When you fast'* not *'if you "
            "fast'* (Matthew 6:16). The early church fasted before major decisions "
            "(Acts 13:2–3, 14:23). Isaiah 58 gives the deepest vision of fasting — "
            "not as a spiritual technique but as a reorientation of life around "
            "God and the needs of others. At 15, young people are developing "
            "their own spiritual disciplines independent of parents. Fasting "
            "is a powerful tool precisely because it is costly — it teaches "
            "the body that the Spirit is in charge, which is foundational for "
            "purity, self-control, and perseverance across every area of life."
        ),
    },
    {
        "slug": "christ-living-sacrifice-age15",
        "title": "Offer Your Life to God — Living as a Daily Sacrifice",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Romans 12:1**: *'Therefore, I urge you, brothers and sisters, "
            "in view of God's mercy, to offer your bodies as a living sacrifice, "
            "holy and pleasing to God — this is your true and proper worship.'*\n"
            "2. **Discuss what 'living sacrifice' means**: unlike Old Testament "
            "sacrifices which were killed, we remain alive — but our self-will, "
            "agenda, and desires are laid on the altar daily.\n"
            "3. **Start each day with this surrender prayer**: 'Lord, today I am "
            "yours. My time, my plans, my words, my body — use them as you will.'\n"
            "4. **Identify one area of your life** you have not yet surrendered "
            "to God — a relationship, an ambition, a habit. Bring it to Him.\n"
            "5. **Discuss calling and vocation**: if your life is God's, "
            "how does that affect your choices about future study and career?"
        ),
        "parent_note_md": (
            "Romans 12:1 is the hinge of the entire letter to the Romans — "
            "Paul moves from eleven chapters of theology to practical application "
            "with this verse. *'In view of God's mercy'* — the surrender is a "
            "response to grace, not an attempt to earn it. Jim Elliot wrote: "
            "*'He is no fool who gives what he cannot keep to gain what he cannot "
            "lose.'* At 15, young people are beginning to make life-defining "
            "choices — university direction, relationships, career. A young person "
            "who has consciously offered their life to God approaches these "
            "choices with a fundamentally different orientation than one who "
            "has not."
        ),
    },
    {
        "slug": "christ-doubt-honest-faith-age15",
        "title": "Engage Your Doubts Honestly — Faith That Has Been Tested",
        "category": "cognitive",
        "min_age": 15, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Write down your genuine doubts** — every question you have about "
            "Christianity that you haven't dared ask. Be completely honest.\n"
            "2. **Read John 20:24–29** — Thomas doubted, demanded evidence, "
            "and Jesus responded to his doubt with grace, not rebuke.\n"
            "3. **Take each doubt seriously** — research it. Read a thoughtful "
            "Christian response. Engage it as an intellectual question, not "
            "a spiritual failure.\n"
            "4. **Find a trusted adult** who can engage your questions without "
            "dismissing them or panicking.\n"
            "5. **Understand that doubt is not the opposite of faith** — "
            "certainty is. Faith that has wrestled with doubt and chosen to trust "
            "is far stronger than faith that has never been questioned."
        ),
        "parent_note_md": (
            "Jesus did not rebuke Thomas for doubting — He showed him the evidence "
            "(John 20:27). Jude 22 instructs: *'Be merciful to those who doubt.'* "
            "Research on faith and adolescence consistently shows that teenagers "
            "who are given permission to doubt and space to ask hard questions "
            "are significantly more likely to retain faith into adulthood than "
            "those who are told to suppress doubt. Suppressed doubt does not "
            "disappear — it resurfaces at university without any framework to "
            "process it. A faith that has engaged the questions is a faith "
            "that can be defended and sustained."
        ),
    },

    # ══════════════════════════════════════════════════════════════════════
    # AGE 16
    # ══════════════════════════════════════════════════════════════════════
    {
        "slug": "christ-complete-bible-plan-age16",
        "title": "Complete a Full Bible Reading Plan — All 66 Books",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose a one-year plan**: McCheyne's Calendar (NT + Psalms daily, "
            "OT separately), or a straight Genesis-to-Revelation plan.\n"
            "2. **Read 3–4 chapters per day**: approximately 20 minutes.\n"
            "3. **Keep a brief journal**: one observation and one application per day.\n"
            "4. **Don't skip the difficult parts**: Leviticus, Numbers, Chronicles, "
            "Revelation — these are part of the whole counsel of God and each "
            "has specific value when read in context.\n"
            "5. **Upon completion**: write a one-page reflection — what surprised "
            "you most? What changed in how you understand God? What will you "
            "read next?\n"
            "6. **Then restart**: the Bible rewards multiple readings — each time "
            "you are different, and so you see differently."
        ),
        "parent_note_md": (
            "Joshua 1:8: *'Keep this Book of the Law always on your lips; meditate "
            "on it day and night.'* 2 Timothy 3:16–17: *'All Scripture is "
            "God-breathed and is useful for teaching, rebuking, correcting and "
            "training in righteousness, so that the servant of God may be thoroughly "
            "equipped for every good work.'* Reading the entire Bible gives a young "
            "person the full narrative arc of Scripture — Creation, Fall, Israel, "
            "Christ, Church, New Creation — which provides the complete framework "
            "for understanding everything else. A 16-year-old who has read the "
            "whole Bible possesses a resource that the vast majority of adults "
            "in their church have never accessed."
        ),
    },
    {
        "slug": "christ-full-stewardship-age16",
        "title": "Understand Full Christian Stewardship — Time, Talent, and Treasure",
        "category": "financial",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read 1 Peter 4:10**: *'Each of you should use whatever gift you "
            "have received to serve others, as faithful stewards of God's grace "
            "in its various forms.'*\n"
            "2. **Conduct a full stewardship audit across three areas**:\n"
            "   - *Time*: where do your 168 hours per week actually go? "
            "Is God getting the first portion, or the leftovers?\n"
            "   - *Talent*: what are your top three abilities? Are they being used "
            "for God and others, or only for personal gain?\n"
            "   - *Treasure*: are you tithing? Giving to the poor? Saving wisely? "
            "Spending with integrity?\n"
            "3. **Set one goal in each area** for the next three months.\n"
            "4. **Ask the deeper question**: if everything I have belongs to God, "
            "what does that mean for my career choices, my spending habits, "
            "and how I spend my evenings?"
        ),
        "parent_note_md": (
            "The Parable of the Talents (Matthew 25:14–30) ends with the master "
            "returning to settle accounts — stewardship has an accountability "
            "dimension. Paul writes: *'Now it is required that those who have been "
            "given a trust must prove faithful'* (1 Corinthians 4:2, NIV). "
            "At 16, young people are approaching the point where they will manage "
            "their own time and money independently. A full stewardship framework "
            "— rooted in theology, not just financial advice — gives them a "
            "comprehensive approach to resources that will govern university, "
            "career, marriage, and ministry for the rest of their life."
        ),
    },
    {
        "slug": "christ-lead-prayer-study-age16",
        "title": "Lead a Prayer Time or Bible Study for Others",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start small**: offer to lead the family's Sunday evening prayer, "
            "or facilitate a 30-minute Bible discussion with two or three peers.\n"
            "2. **Prepare properly**: choose a passage, write 3 discussion questions, "
            "prepare a brief introduction (context of the passage), plan how "
            "to close in prayer.\n"
            "3. **Lead with questions, not answers**: the best facilitators draw "
            "insight out of the group rather than lecturing.\n"
            "4. **Reflect afterwards**: what went well? Where did conversation "
            "stall? What would you do differently?\n"
            "5. **Make it regular**: once a month for 6 months. Leadership "
            "grows through practice, not just intention."
        ),
        "parent_note_md": (
            "Paul instructs Timothy: *'And the things you have heard me say in "
            "the presence of many witnesses entrust to reliable people who will "
            "also be qualified to teach others'* (2 Timothy 2:2, NIV). "
            "This is the discipleship multiplication model — each generation "
            "teaches the next. Teaching is one of the most effective forms of "
            "learning: a young person who leads a Bible study must understand "
            "the passage well enough to guide others through it. At 16, teenagers "
            "have enough biblical knowledge and maturity to lead peers. "
            "This task activates them as disciple-makers, not just disciples."
        ),
    },
    {
        "slug": "christ-church-history-age16",
        "title": "Study Church History — From the Apostles to Today",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Cover the five major eras** in brief:\n"
            "   - Early Church (30–500 AD): Pentecost, persecution, councils, "
            "creeds, Augustine\n"
            "   - Medieval Church (500–1500): monasticism, Crusades, Aquinas, "
            "the papacy\n"
            "   - Reformation (1500–1700): Luther, Calvin, Tyndale, the Bible "
            "in the vernacular\n"
            "   - Modern missions (1700–1900): Wesley, Whitefield, Carey, "
            "Wilberforce, Hudson Taylor\n"
            "   - Contemporary (1900–now): Pentecostalism, the global church, "
            "persecution, ecumenism\n"
            "2. **Read one short church history book**: "
            "*Church History in Plain Language* by Bruce Shelley.\n"
            "3. **Discuss**: what mistakes did the church make? What should we "
            "learn? What is worth celebrating?"
        ),
        "parent_note_md": (
            "Hebrews 13:7: *'Remember your leaders, who spoke the word of God to "
            "you. Consider the outcome of their way of life and imitate their faith.'* "
            "Church history is not optional extra knowledge — it is the story of "
            "how the faith was transmitted across 2,000 years to reach us. "
            "It also reveals the church's failures honestly — the Crusades, the "
            "Inquisition, complicity with slavery — which inoculates against both "
            "naive triumphalism and easy cynicism. A young person who knows "
            "church history is harder to deceive with either 'the church is "
            "perfect' or 'the church has always been corrupt.' They know the "
            "actual complicated, Spirit-sustained story."
        ),
    },
    {
        "slug": "christ-great-commission-age16",
        "title": "Understand and Begin to Live the Great Commission",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Matthew 28:18–20**: *'All authority in heaven and on earth "
            "has been given to me. Therefore go and make disciples of all nations, "
            "baptising them in the name of the Father and of the Son and of the "
            "Holy Spirit, and teaching them to obey everything I have commanded "
            "you.'*\n"
            "2. **Understand the structure**: Go → Make disciples → Baptise → "
            "Teach obedience. It is a complete discipleship process, not just "
            "evangelism.\n"
            "3. **Identify your 'Jerusalem'** (Acts 1:8 — start local): "
            "who in your immediate world does not know Jesus and needs to?\n"
            "4. **Take one step this month**: pray for them by name daily, "
            "invite them to church, or have an honest conversation about faith.\n"
            "5. **Consider a short-term mission trip** as a concrete experience "
            "of the global dimension."
        ),
        "parent_note_md": (
            "Matthew 28:18–20 are the final words of Jesus in Matthew's Gospel — "
            "His parting commission to every disciple. The promise attached is "
            "Matthew 28:20: *'And surely I am with you always, to the very end "
            "of the age.'* Every Christian is called to this mission — not only "
            "professional missionaries. William Carey said: *'Expect great things "
            "from God; attempt great things for God.'* At 16, young people are "
            "old enough to engage their world with intentionality. Understanding "
            "the Great Commission reframes their entire social life — every "
            "relationship is an opportunity to love someone toward Christ."
        ),
    },
    {
        "slug": "christ-personal-testimony-age16",
        "title": "Write and Share Your Personal Testimony",
        "category": "social",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Write a full testimony** — not bullet points but a genuine "
            "personal account. Cover:\n"
            "   - Your background and where you started\n"
            "   - The moment(s) faith became real and personal\n"
            "   - How your life has changed and why Jesus matters to you now\n"
            "2. **Edit for a non-Christian audience**: remove all Christian jargon, "
            "assume zero prior knowledge, be honest about struggles — not a "
            "polished advertisement.\n"
            "3. **Practise sharing it** in 3 minutes (short version) and "
            "10 minutes (fuller version).\n"
            "4. **Find one natural opportunity** to share it this month — "
            "with a friend, in a group setting, or in writing.\n"
            "5. **Keep updating it**: your story is not finished — add to it "
            "as God continues to work."
        ),
        "parent_note_md": (
            "Revelation 12:11: *'They triumphed over him by the blood of the Lamb "
            "and by the word of their testimony.'* Paul's testimony appears three "
            "times in Acts (9, 22, 26) — each time adapted for the specific "
            "audience. A personal testimony is uniquely powerful because it is "
            "unarguable — no one can tell you your experience didn't happen. "
            "At 16, a young person has a genuine, multi-year faith story to "
            "tell. Writing and sharing it serves two purposes: it cements "
            "their own faith (articulation deepens conviction) and it witnesses "
            "to others. It is the most natural form of the Great Commission "
            "for a teenager."
        ),
    },
    {
        "slug": "christ-life-mission-age16",
        "title": "Develop a Personal Life Mission Statement from Scripture",
        "category": "cognitive",
        "min_age": 16, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Read Jeremiah 29:11**: *'For I know the plans I have for you, "
            "declares the Lord, plans to prosper you and not to harm you, plans "
            "to give you hope and a future.'* God has a specific purpose for "
            "each person.\n"
            "2. **Reflect on three questions**:\n"
            "   - What am I uniquely good at? (gifting)\n"
            "   - What breaks my heart when I see it in the world? (calling)\n"
            "   - Where do these two things meet? (vocation)\n"
            "3. **Draft a one-sentence mission statement**: e.g. 'To use my "
            "gift of communication to bring truth and hope to people who have "
            "lost both.'\n"
            "4. **Ground it in a key scripture** that captures the vision.\n"
            "5. **Share it with two trusted mentors** for input and accountability. "
            "Review it annually."
        ),
        "parent_note_md": (
            "Ephesians 2:10: *'For we are God's handiwork, created in Christ Jesus "
            "to do good works, which God prepared in advance for us to do.'* "
            "Every believer has been crafted by God for specific purposes — "
            "not vague spiritual ones but concrete works in the world. "
            "At 16, young people are making the educational choices that will "
            "shape their adult lives. A mission statement rooted in gifting, "
            "compassion, and scripture gives them a compass for those decisions "
            "that transcends 'what pays well' or 'what my parents want.' "
            "Frederick Buechner captured it: *'The place God calls you to is "
            "where your deep gladness and the world's deep hunger meet.'"
        ),
    },
]


class Command(BaseCommand):
    help = "Seed Christianity tasks — all batches: Ages 5–16 (~87 tasks)."

    def handle(self, *args, **options):
        all_envs = list(Environment.objects.all())
        if not all_envs:
            self.stdout.write(self.style.ERROR(
                "No Environment rows found. Run seed_demo first."
            ))
            return

        created_count = 0
        updated_count = 0

        for data in CHRISTIANITY_TASKS:
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
                    "religion":       "christianity",
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
