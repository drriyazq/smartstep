"""Management command: seed age-5 tasks across all six categories.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev python manage.py seed_age5_catalog

Idempotent — safe to re-run. Uses update_or_create throughout.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task

# ---------------------------------------------------------------------------
# Tasks grouped by category
# ---------------------------------------------------------------------------

FINANCIAL_TASKS = [
    {
        "slug": "money-is-for-buying-age5",
        "title": "Understand That Money is Used to Buy Things",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show real coins and notes** — let them hold a coin and a small note. "
            "*This is money. We use money to get things we need.*\n"
            "2. **Point it out in real life** — at a shop, say: "
            "*We give money to the person at the counter and they give us the food.*\n"
            "3. **Roleplay a tiny shop** — put three toys on a table with a price sticker. "
            "Give them one coin and let them *buy* one item.\n"
            "4. **Ask the question** — over the next week, when they ask for something, "
            "ask: *How do we get that?* Wait for them to say *We buy it with money.*\n"
            "5. **Link money to effort** — *Where does money come from? Parents go to work "
            "and get paid money.* A very simple chain is enough at this age."
        ),
        "parent_note_md": (
            "Before a child can learn anything about money management, they must understand "
            "what money does. Many five-year-olds think items in shops are simply *taken*. "
            "This foundational concept unlocks every financial lesson that follows."
        ),
        "prereqs": [],
    },
    {
        "slug": "big-small-coin-age5",
        "title": "Tell Which Coin is Worth More",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Start with two coins** — place a ₹1 and ₹2 coin side by side. "
            "*Which one can buy more? This one — it is worth more.*\n"
            "2. **The more/less game** — lay two coins face up. "
            "*Point to the one worth more.* Vary the pair each time.\n"
            "3. **Link to a purchase** — show a ₹1 biscuit and a ₹2 biscuit. "
            "*Which coin do we need for this one?*\n"
            "4. **Sorting game** — give three coins. *Put them in order — least money to most money.*\n"
            "5. **Praise the logic** — when they get it right, name what they did: "
            "*You remembered which was worth more — that is clever.*"
        ),
        "parent_note_md": (
            "Understanding relative value — that some coins buy more than others — is the "
            "bridge between recognising coins and actually using them. At age 5 the goal is "
            "the concept, not memorising all denominations."
        ),
        "prereqs": ["money-is-for-buying-age5"],
    },
    {
        "slug": "shop-roleplay-age5",
        "title": "Play Shop and Exchange Items for Coins",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Set up the shop** — arrange 5 household items (apple, crayon, toy, book, cup). "
            "Stick a ₹1 or ₹2 label on each.\n"
            "2. **Give the child a small purse** — 5 coins. They are the customer.\n"
            "3. **Play out a purchase** — they pick an item, hand over the right coin, "
            "you hand over the item and say thank you.\n"
            "4. **Swap roles** — they become the shopkeeper. You are the customer. "
            "Did they hand over the item after receiving the coin?\n"
            "5. **Repeat weekly** — change items and prices slightly each time to keep it fresh."
        ),
        "parent_note_md": (
            "Shop roleplay is one of the most effective early financial education tools. "
            "It combines counting, social interaction, and the concept of exchange in a "
            "physical, memorable way. Children who play shop are far more comfortable at "
            "real counters when they are older."
        ),
        "prereqs": ["money-is-for-buying-age5"],
    },
    {
        "slug": "save-for-treat-age5",
        "title": "Save Three Coins for a Small Treat",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose the treat** — pick something that costs about ₹3–₹5. "
            "Show them a picture or the actual item.\n"
            "2. **Give one coin per day** — or one per earned task. "
            "They drop it in a jar or purse themselves.\n"
            "3. **Count together daily** — each morning or evening: "
            "*How many coins do we have? How many more do we need?*\n"
            "4. **The moment of purchase** — when they have enough, take them to the shop "
            "and let them hand over the coins themselves.\n"
            "5. **Name what happened** — *You saved up and got something you wanted. "
            "That is how saving works.*"
        ),
        "parent_note_md": (
            "Delayed gratification — waiting for something instead of demanding it now — "
            "is one of the strongest predictors of life success. Saving three coins over "
            "three days is the simplest version of this lesson a five-year-old can experience. "
            "Keep the goal small so the wait is short and the success is guaranteed."
        ),
        "prereqs": [],
    },
    {
        "slug": "my-things-not-free-age5",
        "title": "Know That Things in Shops Cost Money",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **At the shop entrance** — before going in, say: "
            "*Everything in here costs money. We are only getting what is on the list.*\n"
            "2. **Show the price label** — pick up one item, point to the price sticker: "
            "*See this number? That is how much money we need to take this home.*\n"
            "3. **When they ask for something** — don't say *we can't afford it.* Instead: "
            "*That costs money. It is not on our list today.*\n"
            "4. **Takeaway meal or snack** — let them watch you pay. "
            "*I gave money, they gave us food. That is buying.*\n"
            "5. **The nothing-is-free rule** — practise the phrase: "
            "*Things in shops cost money. You have to pay.*"
        ),
        "parent_note_md": (
            "Children who believe things in shops can simply be taken or are freely available "
            "are harder to manage in shops and slower to develop financial awareness. "
            "This simple concept — everything has a cost — is worth repeating in many "
            "different real-life settings until it is firmly understood."
        ),
        "prereqs": [],
    },
]

HOUSEHOLD_TASKS = [
    {
        "slug": "carry-plate-sink-age5",
        "title": "Carry Your Plate to the Sink After Eating",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Demonstrate first** — show the full action: both hands on the plate, "
            "walk carefully to the sink, place it gently.\n"
            "2. **Do it alongside them** — for the first week, you both carry your plates "
            "at the same time.\n"
            "3. **Set the expectation** — *After every meal, your plate goes to the sink. "
            "That is your job.*\n"
            "4. **Gentle reminder if forgotten** — call them back calmly: "
            "*Your plate is still on the table.* Don't do it for them.\n"
            "5. **Praise the habit** — *You remembered your plate without being asked — "
            "that is really helpful.*"
        ),
        "parent_note_md": (
            "Clearing your own plate is the most foundational household contribution a young "
            "child can make. It builds awareness of shared spaces, responsibility for one's "
            "own things, and the habit of leaving a space as you found it. Start here before "
            "any other household task."
        ),
        "prereqs": [],
    },
    {
        "slug": "put-shoes-away-age5",
        "title": "Put Your Shoes in the Right Place When You Come Home",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the spot** — walk to the shoe rack or spot together. "
            "*This is where your shoes always go. No other place.*\n"
            "2. **Do it on arrival** — shoes off at the door, straight to the rack. "
            "Make this the first action every time they come home.\n"
            "3. **Pair them up** — teach them to place both shoes facing the same way, side by side.\n"
            "4. **Don't put them away for them** — if shoes are left in the hall, "
            "walk them back to the door and let them put them away.\n"
            "5. **Morning benefit** — when shoes are always in the same place, "
            "mornings are faster. Connect the habit to a benefit they experience."
        ),
        "parent_note_md": (
            "A child who puts shoes away without being asked has learned to complete a "
            "two-step arrival routine independently. This seemingly trivial habit trains "
            "the brain to close loops — starting something and finishing it — which is the "
            "foundation of all organisational skills."
        ),
        "prereqs": [],
    },
    {
        "slug": "hang-bag-hook-age5",
        "title": "Hang Your Bag on the Hook When You Get Home",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Install a low hook** — at their height. This makes it physically possible "
            "for a 5-year-old to do it independently.\n"
            "2. **Show the action** — bag comes off the back, loops go over the hook, "
            "bag hangs flat against the wall.\n"
            "3. **Pair with shoes** — shoes off → bag on hook. Practise this two-step "
            "arrival routine together every day for a week.\n"
            "4. **Explain why** — *If your bag is on the hook, we always know where it is "
            "and it won't get squashed or lost.*\n"
            "5. **Ownership** — let them choose a sticker or label for their hook. "
            "Personal ownership increases compliance."
        ),
        "parent_note_md": (
            "The arrival routine — shoes off, bag on hook — reduces morning panic by "
            "ensuring nothing is ever lost or in a heap. Building this pair of habits before "
            "school starts pays dividends every single school day for years."
        ),
        "prereqs": ["put-shoes-away-age5"],
    },
    {
        "slug": "wipe-spill-age5",
        "title": "Wipe Up a Small Spill with a Cloth",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show where the cloth is** — a dedicated small cloth or paper towels at a "
            "low height they can reach independently.\n"
            "2. **Demonstrate the action** — spill a small amount of water on purpose. "
            "Show how to place the cloth, press down, wipe, rinse.\n"
            "3. **Their turn** — spill a small amount together. They do the full sequence.\n"
            "4. **When a real spill happens** — resist cleaning it for them. "
            "Calmly say: *There's the cloth — you can sort that.* Stay nearby.\n"
            "5. **No blame** — spills happen. The skill is the clean-up, not avoiding spills. "
            "*Everyone spills things. Wiping it up is what matters.*"
        ),
        "parent_note_md": (
            "Teaching a child to deal with their own messes — calmly and immediately — is "
            "one of the most practical independence skills there is. It also removes a major "
            "source of household stress: the adult who cleans up everything. Keep a "
            "low-level cloth accessible at all times."
        ),
        "prereqs": [],
    },
    {
        "slug": "water-plant-age5",
        "title": "Water One Plant Every Day",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Choose their plant** — let them pick one plant in the home that belongs to "
            "them to look after. A small, hardy plant works best.\n"
            "2. **Show the routine** — fill a small watering can to halfway, pour gently at "
            "the base of the plant (not the leaves), check the soil.\n"
            "3. **Link to a cue** — after breakfast every morning. Same time builds the habit.\n"
            "4. **Talk about why** — *Plants need water to live, just like we do. "
            "If we forget, the plant gets sick.*\n"
            "5. **Notice changes together** — check once a week: is it growing? "
            "Are there new leaves? Celebrating results reinforces the habit."
        ),
        "parent_note_md": (
            "Caring for a living thing teaches responsibility in a low-stakes, highly visible "
            "way. The plant's health is direct feedback on consistency. Children who "
            "successfully keep a plant alive gain a real sense of nurturing capability — "
            "a foundation for caring for pets, siblings, and eventually others."
        ),
        "prereqs": [],
    },
]

DIGITAL_TASKS = [
    {
        "slug": "open-close-app-age5",
        "title": "Open and Close an App Correctly",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the home screen** — *This is where all the apps live. "
            "Each picture is a different app.*\n"
            "2. **Open an app** — tap the icon once. Wait for it to load. "
            "Practise on a familiar app they already use.\n"
            "3. **Close the app** — show the home button or swipe gesture to return to home screen. "
            "Practise three times.\n"
            "4. **Do not force-close** — explain that leaving an app properly is better than "
            "pressing the power button.\n"
            "5. **Practise open→use→close** — open a drawing app, draw something, "
            "close it. Three times in a row."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Only open apps that a parent has approved.\n"
            "- If something unexpected appears on screen, come to a parent immediately.\n"
            "- Never tap on pop-ups or ads — close them or call a parent."
        ),
        "parent_note_md": (
            "Knowing how to open and close apps is the first practical device skill. "
            "Children who can do this have more structured interactions — they open an app "
            "for a purpose, use it, and close it — rather than endlessly tapping through "
            "content. This sets healthy use patterns from the start."
        ),
        "prereqs": [],
    },
    {
        "slug": "volume-buttons-age5",
        "title": "Use the Volume Buttons to Adjust Sound",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Show the buttons** — on the device they use. *This one makes it louder. "
            "This one makes it quieter.*\n"
            "2. **Set the rule** — indoors, volume stays at halfway or below. "
            "No blasting sound in the house.\n"
            "3. **Practise adjusting** — play a video, ask them to make it quieter. "
            "Then a little louder. Then back to medium.\n"
            "4. **Headphones** — if they use headphones, show the volume limit. "
            "Explain that too-loud headphones hurt ears permanently.\n"
            "5. **Reinforce the habit** — when you hear a device too loud, ask: "
            "*Can you adjust that?* Let them do it themselves."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Headphone volume for children should never exceed 85 dB — most devices have "
            "a children's volume limit in settings.\n"
            "- Repeated exposure to loud sound causes permanent hearing damage, even at age 5.\n"
            "- Turn volume all the way down before handing earbuds to a child."
        ),
        "parent_note_md": (
            "Volume control is the first form of self-regulation on a device. Teaching a "
            "child to manage sound at age 5 establishes the habit of adjusting the device "
            "to suit the environment — a consideration for others that carries into adult life."
        ),
        "prereqs": ["open-close-app-age5"],
    },
    {
        "slug": "put-device-down-when-asked-age5",
        "title": "Put the Device Down When a Grown-Up Asks",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **State the rule before handing over the device** — *I will ask you to stop "
            "at some point. When I do, you put it down right away.*\n"
            "2. **Give a 2-minute warning** — *Two more minutes, then we stop.* "
            "This reduces the shock of stopping.\n"
            "3. **When time is up** — say clearly: *Time to put it down now.* "
            "Expect compliance within 10 seconds.\n"
            "4. **Practise at low-emotion moments** — hand the device over for 5 minutes "
            "during a calm time, then ask for it back. Reward quick compliance with praise.\n"
            "5. **What if they refuse?** — remove the device calmly without arguing. "
            "Next session is shorter. State this rule in advance."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Devices in a child's bedroom after lights-out disrupt sleep at any age.\n"
            "- Mealtimes and bedtime routines should always be screen-free."
        ),
        "parent_note_md": (
            "The ability to put down a screen when asked is the single most important "
            "digital habit to establish before age 6. Children who master this are far easier "
            "to manage as they grow into heavier device users. Consistency is everything — "
            "every exception teaches that arguing works."
        ),
        "prereqs": [],
    },
    {
        "slug": "no-strangers-screen-age5",
        "title": "Never Show Your Screen to a Stranger",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the rule simply** — *Your screen is private. Only family and "
            "people Mum and Dad know can see it.*\n"
            "2. **Define a stranger** — someone we don't know. Even a friendly person in "
            "a park or shop is a stranger.\n"
            "3. **Roleplay** — you pretend to be a stranger and ask to see their game. "
            "They practise saying: *No, it's private* and turning away.\n"
            "4. **What to do** — if a stranger asks to hold or look at their device, "
            "come straight to a parent.\n"
            "5. **Reinforce regularly** — every few weeks, ask: "
            "*Who is allowed to see your screen?* Confirm: only family."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Strangers asking to use or look at a child's device is a safeguarding concern "
            "— take it seriously if reported.\n"
            "- Keep tone calm when teaching this — you are building a safety tool, "
            "not creating anxiety about strangers."
        ),
        "parent_note_md": (
            "A child's device contains personal photos, apps, and sometimes contact details. "
            "Teaching device privacy at 5 extends naturally into internet privacy as they grow. "
            "The rule — screen is private — is simple, memorable, and protective."
        ),
        "prereqs": [],
    },
    {
        "slug": "device-has-a-home-age5",
        "title": "Put the Device Back in Its Place After Using It",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Establish the device spot** — one clear, consistent place: charging dock, "
            "shelf, or drawer. Show them every time.\n"
            "2. **End-of-use routine** — close the app, turn the screen off, "
            "walk it to the spot and set it down.\n"
            "3. **Practise the full sequence** — hand them the device, let them use it "
            "briefly, then: *Now let's put it back in its home.*\n"
            "4. **Never leave it on furniture** — devices left on sofas fall and break. "
            "Explain the reason: *Its home keeps it safe.*\n"
            "5. **Connect to a benefit** — *When it lives in one place, we always know "
            "where it is. No searching, no panic.*"
        ),
        "parent_note_md": (
            "Devices left randomly around the house get damaged, drained, and lost. "
            "Teaching a child that the device has a specific home — just like shoes and bags — "
            "builds the same organisational habit. It also keeps charging consistent, "
            "meaning the device is always ready when needed."
        ),
        "prereqs": ["put-device-down-when-asked-age5"],
    },
]

NAVIGATION_TASKS = [
    {
        "slug": "know-parents-name-age5",
        "title": "Know Your Parent's Full Name",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Tell them the name clearly** — *My name is [full name]. "
            "Not just Mummy — my real name is [first and last name].*\n"
            "2. **Practise daily** — ask at breakfast: *What is my full name?* "
            "And the other parent's. Keep it light.\n"
            "3. **Write it and read it** — write the name on paper. "
            "Spell it together. Have them trace or copy it.\n"
            "4. **Explain when they would need it** — *If you were lost and a police officer "
            "asked who your mum is, you would say her full name.*\n"
            "5. **Test confidently** — ask them to say it clearly and loudly, as if telling "
            "a stranger. Practise the full sentence: *My mum is called [name].*"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Knowing a parent's full name helps emergency services and adults reunite a "
            "lost child with their family far faster than a first name alone."
        ),
        "parent_note_md": (
            "Most five-year-olds know a parent as *Mummy* or *Daddy* — not by their actual "
            "name. In an emergency, this is a significant barrier. A child who can clearly "
            "say their parent's full name gives emergency responders the information needed "
            "to make contact quickly."
        ),
        "prereqs": [],
    },
    {
        "slug": "hold-hand-crossing-age5",
        "title": "Always Hold a Hand When Crossing a Road",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **State the non-negotiable rule** — *At roads, we always hold hands. "
            "No exceptions. This is a safety rule, not optional.*\n"
            "2. **At every crossing** — reach for their hand before they reach the kerb, "
            "not at it. Make it automatic.\n"
            "3. **Explain the danger simply** — *Cars are very big and move very fast. "
            "A driver might not see a small child. Holding hands keeps you safe.*\n"
            "4. **Practise the approach** — walking towards a road, they should slow down "
            "and reach for your hand automatically. Practise until they do this unprompted.\n"
            "5. **No room to negotiate** — if they resist or run ahead, stop, return, "
            "and re-approach. The rule does not bend."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- A five-year-old must never cross a road independently under any circumstances.\n"
            "- Driveways count as roads — the rule applies there too.\n"
            "- If a child runs into a road, stay calm, retrieve them, and address the behaviour "
            "when you are both calm and safe."
        ),
        "parent_note_md": (
            "Road safety compliance at age 5 is entirely dependent on adult supervision and "
            "rule enforcement. This task is about building the automatic reflex of reaching "
            "for a hand — a habit that must be so deeply ingrained it requires no thought. "
            "Never waive this rule, even once."
        ),
        "prereqs": [],
    },
    {
        "slug": "stay-close-busy-place-age5",
        "title": "Stay Close to Your Parent in a Busy Place",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Define *close*** — *You can see me and I can see you at all times. "
            "If you can't see me, you are too far.*\n"
            "2. **Before entering** — at a market, shop, or park, say: "
            "*Stay within arm's reach today. If you move away, we come straight back.*\n"
            "3. **Practise the check-in** — every minute or two, ask: "
            "*Where am I?* They must be able to see you to answer.\n"
            "4. **What to do if separated** — *Stop where you are. Don't walk around. "
            "Shout my name.* Practise this phrase.\n"
            "5. **Praise compliance** — when they stay close without being asked, "
            "name it: *You stayed close to me the whole time. That keeps you safe.*"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- In busy places, hold hands or use a wrist link until the habit of staying "
            "close is solidly established.\n"
            "- Establish a meeting point at the entrance of any large venue before entering."
        ),
        "parent_note_md": (
            "Young children are easily distracted and do not have the spatial awareness to "
            "track a parent's position reliably. Teaching them to stay within sight — and "
            "the protocol for if they lose you — reduces the risk of becoming separated in "
            "busy environments significantly."
        ),
        "prereqs": [],
    },
    {
        "slug": "shout-parent-name-if-lost-age5",
        "title": "Shout a Parent's Name If You Cannot See Them",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Practise the shout** — yes, actually shout it at home. "
            "*[Parent's name]! I can't see you!* Loud and clear.\n"
            "2. **Stop first** — the protocol is: stop walking, stand still, then shout. "
            "Moving while shouting is confusing for rescuers.\n"
            "3. **Use the full name** — not *Mummy* — use the parent's actual name. "
            "More adults will understand and respond.\n"
            "4. **Keep shouting** — don't give up after one call. Keep calling until someone "
            "comes or a safe adult responds.\n"
            "5. **Roleplay it** — in a familiar safe space, step just out of their sight and "
            "ask: *What do you do?* They must stop, stay, and call out."
        ),
        "safety_md": (
            "## Safety\n\n"
            "- Children should know it is always safe to shout loudly in this situation — "
            "reassure them they will never be told off for calling for help.\n"
            "- If no parent comes, approach a shop worker or uniformed person — not a random adult."
        ),
        "parent_note_md": (
            "Many children, when separated, walk further away trying to find the parent — "
            "making them harder to locate. Stop, stay, shout reverses this instinct. "
            "Practise the shout in a safe context so it is available as a reflex when "
            "fear and adrenaline take over."
        ),
        "prereqs": ["know-parents-name-age5"],
    },
    {
        "slug": "know-where-home-is-age5",
        "title": "Describe What Your Home Looks Like",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Walk around outside together** — look at the front of your home. "
            "*What colour is the door? What floor is it on? Any special features?*\n"
            "2. **Describe it** — help them put it into words: "
            "*Our home has a blue door and a big tree in front.*\n"
            "3. **Draw a picture** — let them draw the front of the house. "
            "Label it together: *My Home.*\n"
            "4. **Quiz them** — *What does our front door look like?* "
            "*What colour is the building?* Vary the questions.\n"
            "5. **Link to finding their way back** — *If you were nearby but lost, "
            "you could look for these things to find home.*"
        ),
        "safety_md": (
            "## Safety\n\n"
            "- This is a preparatory skill — a five-year-old should never be alone near home "
            "or trying to navigate back independently. The goal is building the description "
            "for emergency use, not independent navigation."
        ),
        "parent_note_md": (
            "Being able to describe their home is an early building block of spatial awareness "
            "and emergency preparedness. At age 5 the goal is not a full address (that comes "
            "at age 6) but a clear verbal description that could help a neighbour or "
            "emergency responder identify the family's home."
        ),
        "prereqs": [],
    },
]

COGNITIVE_TASKS = [
    {
        "slug": "listen-till-finished-age5",
        "title": "Listen Until Someone Has Finished Talking",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the skill** — *Listening means being quiet and looking at the person "
            "while they speak. You wait until they stop before you talk.*\n"
            "2. **The finish signal** — agree on a signal for when you have finished speaking: "
            "a nod, or saying *Your turn.* This removes ambiguity.\n"
            "3. **Short stories** — tell a 30-second story. They must wait until the end "
            "to ask questions or comment. Practise five times.\n"
            "4. **Catch good listening** — *You waited until I finished — that was great listening.*\n"
            "5. **Model it yourself** — give your child your full attention when they speak. "
            "They learn from what they see."
        ),
        "parent_note_md": (
            "Listening is a skill, not a given. Five-year-olds are naturally egocentric and "
            "find waiting to speak very difficult. Gentle, consistent practice of this one "
            "skill pays enormous dividends in classroom settings, friendships, and family life. "
            "Start with 30-second waits and build up."
        ),
        "prereqs": [],
    },
    {
        "slug": "follow-two-step-instruction-age5",
        "title": "Follow a Two-Step Instruction",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Give a clear two-step instruction** — *Wash your hands, then come and sit "
            "at the table.* Say it once, calmly.\n"
            "2. **Check they heard** — *Can you tell me what I just asked?* "
            "Have them repeat it back before they start.\n"
            "3. **Watch without helping** — let them complete both steps independently. "
            "Only prompt if they forget the second step after a pause.\n"
            "4. **Build complexity slowly** — start with two familiar steps, then introduce "
            "one new step once the two-step routine is reliable.\n"
            "5. **Praise completion** — *You did both things I asked, in order — well done.*"
        ),
        "parent_note_md": (
            "Following multi-step instructions is the foundation of classroom learning. "
            "Children who can hear, retain, and execute a two-step instruction are better "
            "prepared for school than those who need constant reminders for each sub-step. "
            "Practise this dozens of times in daily life — at mealtimes, getting dressed, "
            "before outings."
        ),
        "prereqs": [],
    },
    {
        "slug": "put-things-back-age5",
        "title": "Put Something Back Where You Found It",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **The before-and-after rule** — before taking something, notice where it is. "
            "*Where did you get that from? That is where it goes back.*\n"
            "2. **Point out the place** — when they take a book from the shelf, "
            "say: *Remember — it goes back on this shelf, in this spot.*\n"
            "3. **After use, return** — build the habit: finish using → return immediately, "
            "before getting the next thing.\n"
            "4. **Treasure hunt reversal** — scatter 5 items around the room and "
            "*return each to its home.* Make it a game with a short timer.\n"
            "5. **Notice the benefit** — *Because you put that back, we knew exactly "
            "where it was when we needed it today.*"
        ),
        "parent_note_md": (
            "Putting things back is the simplest form of maintaining order. Children who do "
            "it consistently live and work in tidier environments, waste less time looking "
            "for lost items, and are more considerate of shared spaces. It also underpins "
            "every library, classroom, and workplace system they will ever encounter."
        ),
        "prereqs": [],
    },
    {
        "slug": "wait-without-fussing-age5",
        "title": "Wait for Two Minutes Without Fussing",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a visible timer** — a sand timer or phone countdown they can watch. "
            "Visible time makes waiting feel manageable.\n"
            "2. **Name the skill** — *Waiting calmly is something we all have to do. "
            "You are practising being patient.*\n"
            "3. **Start with one minute** — set the timer while you finish something. "
            "They must wait quietly without interrupting. Build up to two minutes.\n"
            "4. **Give them a micro-task** — *While you wait, see how many red things "
            "you can spot.* Redirecting attention makes waiting easier.\n"
            "5. **Immediate reward after** — as soon as the timer ends, give full attention: "
            "*You waited so well. What did you want to tell me?*"
        ),
        "parent_note_md": (
            "Delayed gratification — the ability to wait — is one of the most studied and "
            "robust predictors of life outcomes. A child who can wait two minutes at age 5 "
            "has far better self-control at 10 and 15. Start with short waits and extend "
            "gradually; success builds the capacity."
        ),
        "prereqs": [],
    },
    {
        "slug": "tidy-one-thing-before-next-age5",
        "title": "Tidy One Activity Before Starting the Next",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **State the rule before play** — *Before you get out the crayons, "
            "put the blocks away.*\n"
            "2. **One-out, one-away** — only one type of activity out at a time. "
            "The old one goes away before the new one comes out.\n"
            "3. **Be nearby for the transition** — the hardest moment is the swap. "
            "Stay close and prompt once: *Blocks away first.*\n"
            "4. **Don't do it for them** — if they skip ahead to the new activity, "
            "redirect: *Not yet — what needs to go away first?*\n"
            "5. **Celebrate the sequence** — *You put the crayons away before getting the Lego out. "
            "That was really well done.*"
        ),
        "parent_note_md": (
            "This rule prevents the layered-mess problem — where each activity is abandoned "
            "on top of the last until the room is unmanageable. More importantly, it trains "
            "sequential thinking: finish one thing before starting the next. This is the "
            "cognitive foundation of project management and task completion."
        ),
        "prereqs": [],
    },
]

SOCIAL_TASKS = [
    {
        "slug": "say-hello-back-age5",
        "title": "Say Hello When Someone Greets You",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the expectation** — *When someone says hello to you, you say "
            "hello back. It is polite and kind.*\n"
            "2. **Model it constantly** — when adults greet your child, do not answer for "
            "them. Look at your child and wait.\n"
            "3. **Gentle prompt** — if they don't respond, lean down and say quietly: "
            "*Someone said hello to you. What do we say?*\n"
            "4. **Roleplay** — practise at home. You say *Good morning!* They respond. "
            "Try different greetings: Hi, Hello, Good afternoon.\n"
            "5. **No pressure to hug or kiss** — saying hello verbally is the goal. "
            "Physical greetings are always the child's choice."
        ),
        "parent_note_md": (
            "Reciprocating a greeting is the most basic social contract. Children who "
            "respond to hello are perceived as warm and confident. Those who don't respond "
            "are often described as rude, even when they are simply shy. Practising the "
            "verbal response at home removes the anxiety of the in-the-moment expectation."
        ),
        "prereqs": [],
    },
    {
        "slug": "say-sorry-mean-it-age5",
        "title": "Say Sorry When You Have Done Something Wrong",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach when sorry is needed** — when you hurt someone (physically or "
            "with words), break something of theirs, or do something unkind.\n"
            "2. **What a good sorry looks like** — look at the person, say their name, "
            "*I'm sorry I [specific thing].*\n"
            "3. **Not forced, not fake** — a sorry said while rolling eyes or in a sing-song "
            "voice is worse than none. Aim for calm and direct.\n"
            "4. **Practise at calm moments** — roleplay a small incident and practise the "
            "apology. Don't wait for a real upset to teach the technique.\n"
            "5. **After the sorry** — *Is there anything you can do to help?* "
            "Rebuilding is the next step after apologising."
        ),
        "parent_note_md": (
            "At age 5, children are developmentally beginning to understand the effect of "
            "their actions on others. Teaching a genuine apology now lays the groundwork for "
            "the more complex accountability skills that come in middle childhood. Avoid "
            "forcing a robotic apology — model it instead, and wait for genuine moments."
        ),
        "prereqs": [],
    },
    {
        "slug": "use-words-not-hands-age5",
        "title": "Use Words Instead of Hitting or Pushing",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Name the rule** — *We use words when we are upset. Hands are for hugging, "
            "not hurting.*\n"
            "2. **Give the words** — *Instead of pushing, say: Stop it. I don't like that. "
            "Or: I need some space.*\n"
            "3. **Roleplay the trigger** — re-enact a common frustration calmly. "
            "Someone takes their toy. They practise using words.\n"
            "4. **Catch the feeling before the action** — *I can see you are getting angry. "
            "Take a breath. What words can you use?*\n"
            "5. **When they do use words** — acknowledge immediately: "
            "*You used your words instead of hitting. That took real control.*"
        ),
        "parent_note_md": (
            "Physical responses to frustration are developmentally normal before age 5 but "
            "need to be redirected from this age onward. The goal is not to suppress the "
            "feeling but to provide an alternative outlet. Children need the actual words "
            "given to them — they cannot generate them under emotional pressure without "
            "having practised."
        ),
        "prereqs": [],
    },
    {
        "slug": "wait-to-speak-age5",
        "title": "Wait for a Pause Before Talking",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Explain the rule** — *When someone is talking, we wait until they stop "
            "before we start. Talking over someone is rude.*\n"
            "2. **The hand signal** — teach them to hold up one finger when they want to "
            "speak. This lets them hold the thought without interrupting.\n"
            "3. **Story practice** — tell a short story. They must hold their finger up "
            "if they want to say something, and wait until you pause.\n"
            "4. **Name the behaviour when it happens** — *You waited for me to finish — "
            "that is really good manners.*\n"
            "5. **During family meals** — make one meal a week a practice zone for "
            "taking turns to speak."
        ),
        "parent_note_md": (
            "Interrupting is one of the most common and socially costly habits in childhood. "
            "It often persists into adulthood if not addressed early. The finger-raise technique "
            "is a physical anchor that prevents the thought from being lost while also "
            "preventing the verbal interruption — it is practical and highly effective."
        ),
        "prereqs": ["say-hello-back-age5"],
    },
    {
        "slug": "share-take-turns-age5",
        "title": "Take Turns With a Toy for Five Minutes",
        "min_age": 5, "max_age": 7,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Use a visible timer** — *Your turn is 5 minutes. When the timer beeps, "
            "it is the other person's turn.*\n"
            "2. **Start with a beloved toy** — the harder the item is to give up, "
            "the more valuable the practice. Start with it.\n"
            "3. **The handover** — teach them to hand it over willingly and say "
            "*Your turn.* Not to throw it or sulk.\n"
            "4. **Talk about the wait** — *While it is their turn, what will you do? "
            "You can watch, or find something else.*\n"
            "5. **Celebrate the full cycle** — once both turns are complete: "
            "*You both took turns and it worked. That is sharing.*"
        ),
        "parent_note_md": (
            "Turn-taking is the social mechanism behind fairness, cooperation, and friendship. "
            "Children who can take turns at 5 are better at group play, classroom activities, "
            "and sport. The visible timer externalises the rule — the timer says it is time "
            "to hand over, not the parent — which reduces conflict significantly."
        ),
        "prereqs": [],
    },
]

# ---------------------------------------------------------------------------
# Prerequisite edges: (to_slug, from_slug, is_mandatory)
# ---------------------------------------------------------------------------

PREREQ_EDGES = [
    ("big-small-coin-age5",          "money-is-for-buying-age5",    True),
    ("shop-roleplay-age5",           "money-is-for-buying-age5",    True),
    ("hang-bag-hook-age5",           "put-shoes-away-age5",         True),
    ("device-has-a-home-age5",       "put-device-down-when-asked-age5", True),
    ("volume-buttons-age5",          "open-close-app-age5",         True),
    ("shout-parent-name-if-lost-age5", "know-parents-name-age5",    True),
    ("wait-to-speak-age5",           "say-hello-back-age5",         True),
]

# ---------------------------------------------------------------------------
# Tag mappings
# ---------------------------------------------------------------------------

CATEGORY_TAGS = [
    ("Money basics",     Tag.Category.FINANCIAL),
    ("Home care",        Tag.Category.HOUSEHOLD),
    ("Digital literacy", Tag.Category.DIGITAL),
    ("Wayfinding",       Tag.Category.NAVIGATION),
    ("Reasoning",        Tag.Category.COGNITIVE),
    ("Social skills",    Tag.Category.SOCIAL),
]

ALL_AGE5_TASKS = [
    (FINANCIAL_TASKS,  "Money basics"),
    (HOUSEHOLD_TASKS,  "Home care"),
    (DIGITAL_TASKS,    "Digital literacy"),
    (NAVIGATION_TASKS, "Wayfinding"),
    (COGNITIVE_TASKS,  "Reasoning"),
    (SOCIAL_TASKS,     "Social skills"),
]


class Command(BaseCommand):
    help = "Seed age-5 tasks across all six categories (idempotent)."

    def handle(self, *args, **options):
        tags = {}
        for display_name, category in CATEGORY_TAGS:
            tag, _ = Tag.objects.get_or_create(
                name=display_name,
                defaults={"category": category},
            )
            tags[display_name] = tag

        all_envs = list(Environment.objects.all())

        total_upserted = 0
        for task_list, tag_name in ALL_AGE5_TASKS:
            tag = tags[tag_name]
            for t in task_list:
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
                total_upserted += 1

        self.stdout.write(f"Upserted {total_upserted} age-5 tasks.")

        all_slugs = [t["slug"] for task_list, _ in ALL_AGE5_TASKS for t in task_list]
        task_map = {t.slug: t for t in Task.objects.filter(slug__in=all_slugs)}
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
        self.stdout.write(self.style.SUCCESS("seed_age5_catalog complete."))
