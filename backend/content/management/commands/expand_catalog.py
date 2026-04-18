"""
expand_catalog.py — adds full how-to steps for all tasks, extends max_age
to 13, adds sex-specific tasks, and approves all pending tasks.
Safe to run repeatedly (idempotent).
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import Environment, PrerequisiteEdge, ReviewStatus, SexFilter, Tag, Task

ALL_ENVS = ("urban", "suburban", "rural")
URBAN_SUB = ("urban", "suburban")
RURAL_ALL = ("urban", "suburban", "rural")

# ─── Full how-to text keyed by slug ─────────────────────────────────────────
HOW_TOS = {
    # FINANCIAL ───────────────────────────────────────────────────────────────
    "identify-coins": (
        "1. Lay all coins face-up on a flat surface.\n"
        "2. Point to each coin and name its value — drill until instant.\n"
        "3. Mix them up, flip some over, and ask the child to sort by value.\n"
        "4. Quiz: pick up a random coin and wait — child names it without help.\n"
        "5. Done when they can name every denomination in under 20 seconds."
    ),
    "recognize-currency-symbol": (
        "1. Show price tags, receipts, and online prices together.\n"
        "2. Point out the symbol on each and name the currency (£, $, €, ₹).\n"
        "3. Ask: 'Which one costs more — $5 or ₹5?' Discuss why.\n"
        "4. Find 5 different currency symbols in newspapers or online.\n"
        "5. Mark complete when the child can identify 3+ symbols without prompting."
    ),
    "count-coins-to-total": (
        "1. Set a target amount (e.g. 73p / $0.73).\n"
        "2. Tip out a pile of mixed coins and ask the child to count out exactly that amount.\n"
        "3. Count together to verify — celebrate if correct.\n"
        "4. Repeat 3 times with different amounts, including totals requiring multiple coin types.\n"
        "5. Mark complete when the child can hit any target under £2 / $2 without help."
    ),
    "distinguish-need-want": (
        "1. Write 'NEED' and 'WANT' on two pieces of paper.\n"
        "2. Read out 10 items (food, toy, shoes, game, medicine) — child places each.\n"
        "3. Discuss any disagreements without being dismissive of their reasoning.\n"
        "4. Ask: 'What would happen if we never spent on wants? Never on needs?'\n"
        "5. Mark complete when the child can explain the difference in their own words."
    ),
    "track-savings-ledger": (
        "1. Give the child a small notebook labelled 'My Money Ledger'.\n"
        "2. Start with whatever they already have — write it as the opening balance.\n"
        "3. Each time money comes in or goes out, they write: date, reason, +/−, new total.\n"
        "4. Check together weekly — spot any entries they missed.\n"
        "5. Mark complete after 4 weeks of consistent, accurate tracking."
    ),
    "save-for-goal": (
        "1. Help the child choose one specific thing to save for (name and price).\n"
        "2. Write the goal on paper and stick it where they see it daily.\n"
        "3. Each time they receive money, they decide how much goes into savings.\n"
        "4. Use a jar or envelope — visible savings feel real.\n"
        "5. Mark complete when they reach their goal through their own saving."
    ),
    "donate-small-amount": (
        "1. Talk about what a charity does — pick one together that resonates with the child.\n"
        "2. Agree on a small amount (even 50p / $1) from their pocket money.\n"
        "3. Let the child physically make the donation — charity box, online, or envelope.\n"
        "4. Discuss: 'How does it feel to give? Do you think it makes a difference?'\n"
        "5. Mark complete after the child has donated at least once with genuine understanding."
    ),
    "read-receipt": (
        "1. After a shop trip, give the child the receipt before leaving the shop.\n"
        "2. Ask them to find: the total, the number of items, and the most expensive item.\n"
        "3. Check one item price against what was expected — did they charge correctly?\n"
        "4. Spot the VAT or tax line if visible — explain briefly what it is.\n"
        "5. Mark complete when the child can verify a receipt independently."
    ),
    "calculate-simple-discount": (
        "1. Find a sale item — show the original price and the discount percentage.\n"
        "2. Teach: 10% = move decimal one place left. 50% = halve it.\n"
        "3. Ask the child to calculate the saving and the new price.\n"
        "4. Practise with 10%, 25%, 50% discounts on 3 different items.\n"
        "5. Mark complete when the child can work out any of the three without help."
    ),
    "estimate-grocery-total": (
        "1. Before the checkout, challenge the child to estimate the basket total.\n"
        "2. Teach rounding: round each item to the nearest pound/dollar.\n"
        "3. Run a running total in their head (or on fingers) as items go in the trolley.\n"
        "4. Compare estimate to actual receipt — within 20% counts as a win.\n"
        "5. Mark complete after 3 successful estimates on different shopping trips."
    ),
    "compare-unit-prices": (
        "1. In a supermarket, pick two versions of the same product (different sizes).\n"
        "2. Show the price-per-100g or price-per-litre label (usually in small print).\n"
        "3. Ask: 'Which is the better value? Is the bigger one always cheaper per unit?'\n"
        "4. Compare 3 product pairs together.\n"
        "5. Mark complete when the child can find and compare unit prices independently."
    ),
    "spot-ad-vs-content": (
        "1. Open a webpage or social media feed together.\n"
        "2. Ask: 'Point to anything here that is trying to sell you something.'\n"
        "3. Show the 'Sponsored' / 'Ad' labels — explain they can be tiny or hidden.\n"
        "4. Watch a YouTube video — pause and ask 'Is this an ad or genuine content?'\n"
        "5. Mark complete when the child spots ads without prompting."
    ),
    "plan-weekly-budget": (
        "1. Together, list the child's expected income for the week (pocket money).\n"
        "2. List their likely expenses (snack, saving, fun) in a simple table.\n"
        "3. Check income ≥ expenses — if not, decide what to cut or delay.\n"
        "4. The child sticks to their budget for one week. Review together at the end.\n"
        "5. Mark complete after one successful week of living within the plan."
    ),
    "recognize-scam-offer": (
        "1. Show a real example of a scam offer (email screenshot, fake prize).\n"
        "2. List the warning signs together: urgency, too-good price, spelling errors, requests for personal info.\n"
        "3. Ask: 'What would you do if you saw this?' — correct answer: ignore and tell an adult.\n"
        "4. Show 2 more examples — real offer vs. scam — child identifies which is which.\n"
        "5. Mark complete when the child can list 3 warning signs from memory."
    ),
    # DEMO financial tasks
    "check-change": (
        "1. At a shop, before handing over money, agree on what change to expect.\n"
        "2. Count the change received back in front of the cashier.\n"
        "3. If incorrect, calmly point it out — practise the words together.\n"
        "4. Repeat 3 times on real shopping trips.\n"
        "5. Mark complete when the child can check change independently and confidently."
    ),
    "pay-cashier": (
        "1. Let the child carry the money and queue at a till.\n"
        "2. They tell the cashier the item, listen to the price, hand over money.\n"
        "3. Wait for the change — count it.\n"
        "4. Say thank you and keep the receipt.\n"
        "5. Mark complete after 3 successful independent cashier transactions."
    ),
    "use-atm-with-parent": (
        "1. Stand with the child at an ATM you use regularly.\n"
        "2. Walk through: insert card, PIN (cover the hand), choose amount, take cash, take card.\n"
        "3. Explain: the money isn't 'free' — it comes from your balance.\n"
        "4. Let the child press the buttons while you supervise.\n"
        "5. Mark complete when they can operate the ATM sequence with minimal prompting."
    ),
    "count-change": (
        "1. Set up a mock shop at home with priced items and coins.\n"
        "2. The child is the cashier: customer pays, child counts out correct change.\n"
        "3. Start with simple amounts (10p change from 50p), then increase complexity.\n"
        "4. 5 rounds without error = mastered.\n"
        "5. Mark complete when the child can make change for any purchase under £5 / $5."
    ),
    "read-price-tag": (
        "1. Pick up any item in a shop and point to the price label.\n"
        "2. Ask: 'How much is this?' — child reads the label aloud.\n"
        "3. Practice with 10 different items — vary the format (£1.49, $3.00, 75p).\n"
        "4. Introduce sale tags: original price crossed out, sale price shown.\n"
        "5. Mark complete when the child reads any price format correctly."
    ),
    "compare-prices": (
        "1. Hold two similar items with different prices.\n"
        "2. Ask: 'Which is cheaper? By how much?'\n"
        "3. Extend: 'Which is better value — cheaper item or the one on offer?'\n"
        "4. Do this across 3 different product types on one shopping trip.\n"
        "5. Mark complete when the child can compare and explain their reasoning."
    ),
    # HOUSEHOLD ───────────────────────────────────────────────────────────────
    "make-bed": (
        "1. Show the steps once: straighten sheet, pull up duvet/blanket, fluff pillows.\n"
        "2. Agree it must be done within 10 minutes of waking up.\n"
        "3. The child does it alone for 7 consecutive days.\n"
        "4. Resist correcting minor imperfections — consistency matters more than perfection.\n"
        "5. Mark complete when making the bed is a no-reminder habit."
    ),
    "sort-laundry-by-color": (
        "1. Empty the laundry basket onto the floor.\n"
        "2. Explain the three piles: darks (navy, black, dark grey), lights (white, cream, pale), colours (everything else).\n"
        "3. Child sorts the pile. You check together — discuss borderline items.\n"
        "4. Explain why mixing causes colours to bleed into whites.\n"
        "5. Mark complete when the child sorts correctly without help."
    ),
    "fold-tshirt": (
        "1. Lay the t-shirt face down on a flat surface.\n"
        "2. Fold one side in (⅓ width), sleeve folded back.\n"
        "3. Fold the other side in the same way.\n"
        "4. Fold the bottom up to the collar — flip over.\n"
        "5. Mark complete when the child can fold a t-shirt neatly in under 60 seconds."
    ),
    "sweep-small-area": (
        "1. Show the correct grip — lower hand near bristles for control.\n"
        "2. Sweep in small overlapping strokes towards one corner, not scattering dust.\n"
        "3. Collect the pile with dustpan and brush — tip into bin.\n"
        "4. Child sweeps a small defined area (bathroom, hallway) unsupervised.\n"
        "5. Mark complete when the area is visibly clean after the child's sweep."
    ),
    "wipe-kitchen-counters": (
        "1. Show which cloth to use and where it lives.\n"
        "2. Spray surface cleaner or dampen cloth — wipe in one direction, not circles.\n"
        "3. Move items off the counter first, wipe, replace.\n"
        "4. Rinse cloth after use.\n"
        "5. Mark complete when the child wipes counters as part of clearing up after meals."
    ),
    "water-plants": (
        "1. Explain each plant's needs — finger in soil: if dry, water; if damp, wait.\n"
        "2. Show the right amount: water until it runs from the drainage hole.\n"
        "3. Assign the child responsibility for 2 plants for 2 weeks.\n"
        "4. Check plants together at day 7 — how are they doing?\n"
        "5. Mark complete when the plants are healthy after 2 weeks of child-led care."
    ),
    "take-out-trash-sort-recycle": (
        "1. Show the bins: which is general waste, recycling, food waste.\n"
        "2. Walk through the recycling rules for your local area (what can/can't go in).\n"
        "3. Child takes out the correct bin on collection day for 4 weeks.\n"
        "4. Check they've rinsed recyclables where required.\n"
        "5. Mark complete when the child manages bin day without prompting."
    ),
    "make-cold-sandwich": (
        "1. Set out ingredients and equipment — the child decides what goes in.\n"
        "2. Child spreads filling (butter, hummus, mayo) without tearing the bread.\n"
        "3. Add fillings, close sandwich, cut if desired.\n"
        "4. Clean up the work surface before eating.\n"
        "5. Mark complete when the child makes a complete packed lunch independently."
    ),
    "use-microwave-safely": (
        "1. Show what containers are safe (microwave-safe label) and what's not (foil, metal).\n"
        "2. Demonstrate: place food, set time, check halfway, stir if needed.\n"
        "3. Warn about steam when removing the lid — lift away from face.\n"
        "4. Child reheats a portion of leftovers independently.\n"
        "5. Mark complete when the child reheats food safely without reminders."
    ),
    "load-dishwasher": (
        "1. Show the logic: plates in the rack slots, bowls angled to drain, cutlery handles down.\n"
        "2. Glasses on the top rack, large items on the bottom.\n"
        "3. Don't pre-rinse — scrape food into the bin.\n"
        "4. Add tablet/powder and select the correct cycle.\n"
        "5. Mark complete when the child loads and starts the dishwasher correctly."
    ),
    "operate-washing-machine": (
        "1. Place the sorted load (darks only to start) into the drum — don't overfill.\n"
        "2. Measure detergent to the line — use liquid or pod as appropriate.\n"
        "3. Select the programme: 30° or 40° for colours, 60° for whites.\n"
        "4. Press start. Transfer to dryer or airer when done.\n"
        "5. Mark complete when the child runs a full cycle independently."
    ),
    # DIGITAL ─────────────────────────────────────────────────────────────────
    "turn-device-on-off": (
        "1. Show the power button location and how long to hold it.\n"
        "2. Explain the difference between sleep/lock and full shutdown.\n"
        "3. Show how to charge: cable orientation, charge indicator.\n"
        "4. Ask the child to turn off, charge, and turn on the device independently.\n"
        "5. Mark complete when they manage device power without guidance."
    ),
    "type-own-name": (
        "1. Open a text editor or notes app.\n"
        "2. Show the child their name on paper — they find and type each letter.\n"
        "3. Practise the shift key for capital letters.\n"
        "4. Extend: type their full name, address, school name.\n"
        "5. Mark complete when the child can type their full name without looking for keys."
    ),
    "open-close-app": (
        "1. Show the home screen and how to find apps.\n"
        "2. Demonstrate opening an app, using it briefly, then closing it properly.\n"
        "3. Show the app switcher (recent apps) — swipe away to close.\n"
        "4. Child opens 3 apps and closes each one completely.\n"
        "5. Mark complete when the child navigates apps without help."
    ),
    "take-and-delete-photo": (
        "1. Open the camera app together.\n"
        "2. Take a photo — check the result.\n"
        "3. Open the gallery — find the photo, long-press to select, delete.\n"
        "4. Discuss: 'Once you share a photo online, you can't un-share it.'\n"
        "5. Mark complete when the child can shoot and delete photos independently."
    ),
    "use-kid-safe-search": (
        "1. Show a child-safe search engine (e.g. Kiddle, Safe Search Kids).\n"
        "2. Ask the child to look up a topic they're curious about.\n"
        "3. Look at the results together — is this what they expected?\n"
        "4. Discuss: 'Not everything on the internet is true. How can we check?'\n"
        "5. Mark complete when the child can find information on a topic independently."
    ),
    "adjust-volume-brightness": (
        "1. Show the volume buttons and what the on-screen indicator looks like.\n"
        "2. Demonstrate brightness slider in settings.\n"
        "3. Explain: high brightness drains battery faster; loud headphone volume damages hearing.\n"
        "4. Child sets appropriate volume for headphones (below 60%) and adjusts brightness.\n"
        "5. Mark complete when the child self-regulates volume and brightness."
    ),
    "passwords-are-private": (
        "1. Explain: a password is like a house key — you don't give it to strangers.\n"
        "2. Ask: 'Who should know your password?' (Nobody except parents.)\n"
        "3. Role-play: a 'friend' asks for the password. Child practises saying no.\n"
        "4. Explain that websites/services will never ask for your password by email.\n"
        "5. Mark complete when the child can explain why passwords must stay private."
    ),
    "dont-share-personal-info": (
        "1. List what counts as personal info: full name, address, school, age, photos.\n"
        "2. Scenario: an online game asks for your address. What do you do?\n"
        "3. Explain the rule: never share this info without a parent's knowledge.\n"
        "4. Show how to spot forms asking for personal info online.\n"
        "5. Mark complete when the child can identify and refuse inappropriate info requests."
    ),
    "ask-before-downloading": (
        "1. Explain: apps and files can carry hidden malware.\n"
        "2. Role-play: child finds an app they want — they come to ask permission.\n"
        "3. Together, check reviews, developer name, permission requests before installing.\n"
        "4. Agree the rule: nothing gets downloaded without a parent seeing it first.\n"
        "5. Mark complete when the child consistently asks before downloading."
    ),
    "recognize-ad-banner": (
        "1. Open a website and ask: 'What on this page is trying to sell you something?'\n"
        "2. Highlight ad banners, sponsored results, affiliate links.\n"
        "3. Show YouTube ads — the skip button, and how ads are labelled.\n"
        "4. Ask: 'Why does the website show ads?' (To make money.)\n"
        "5. Mark complete when the child spots ads on any platform without prompting."
    ),
    "close-suspicious-popup": (
        "1. Show a screenshot of a suspicious popup ('You've won!', 'Virus detected!').\n"
        "2. Explain: never click the button inside the popup — use the browser's X.\n"
        "3. If the X won't close it, show Alt+F4 / swipe away on mobile.\n"
        "4. Role-play: child encounters the popup scenario, closes it correctly.\n"
        "5. Mark complete when the child can close a suspicious popup calmly."
    ),
    "report-block-content": (
        "1. Walk through the report button on one platform the child uses.\n"
        "2. Show: three dots → Report → choose reason.\n"
        "3. Show how to block a person so they can't contact you.\n"
        "4. Agree: always tell a trusted adult if something online felt wrong or scary.\n"
        "5. Mark complete when the child can report and block on at least one platform."
    ),
    "video-call-etiquette": (
        "1. Practise a mock call: find a quiet spot, tidy the background.\n"
        "2. Check camera angle — face visible, not looking up nostrils.\n"
        "3. Mute when not speaking if background is noisy.\n"
        "4. Look at the camera, not your own image — it feels more like eye contact.\n"
        "5. Mark complete after a real video call where the child applies all four points."
    ),
    "respect-screen-time": (
        "1. Agree on a daily screen-time limit together — the child is more likely to follow a rule they helped set.\n"
        "2. Use built-in screen-time settings or a timer to track.\n"
        "3. When the timer goes off, the child stops without argument (this is the skill).\n"
        "4. Discuss: 'What did you do with the offline time? How did you feel?'\n"
        "5. Mark complete after 2 weeks of consistent self-stopping."
    ),
    "create-strong-password": (
        "1. Explain what makes a password weak (123456, your name, pet's name).\n"
        "2. Teach a method: 3 random words + number + symbol (e.g. PurpleElephantSpoon7!).\n"
        "3. Child creates a strong password for a hypothetical account — test it on a password-strength checker.\n"
        "4. Discuss: never reuse the same password across accounts.\n"
        "5. Mark complete when the child creates a genuinely strong password independently."
    ),
    "spot-phishing-link": (
        "1. Show a phishing email screenshot — point out: fake sender address, urgent language, suspicious link.\n"
        "2. Hover over links (on desktop) to reveal the real URL before clicking.\n"
        "3. Rule: if you didn't ask for an email, don't click the link — go directly to the website instead.\n"
        "4. Quiz: show 3 emails — child identifies which are phishing.\n"
        "5. Mark complete when the child correctly identifies phishing in 3 out of 3 examples."
    ),
    "digital-footprint-awareness": (
        "1. Explain: anything posted online can be saved, shared, and found years later.\n"
        "2. Ask: 'Would you be comfortable if your future teacher saw this post?'\n"
        "3. Search for an example of a real person's old post causing a problem — discuss.\n"
        "4. Help the child check and tighten privacy settings on any account they use.\n"
        "5. Mark complete when the child can explain digital footprint in their own words."
    ),
    "evaluate-source-credibility": (
        "1. Find two articles on the same topic — one from a reputable source, one from a blog.\n"
        "2. Check: Who wrote it? When? Does it cite sources? Does the site have an 'About' page?\n"
        "3. Ask: 'Which would you trust for a school project? Why?'\n"
        "4. Introduce the SIFT method: Stop, Investigate, Find better coverage, Trace claims.\n"
        "5. Mark complete when the child can evaluate a source using at least 3 criteria."
    ),
    "recognize-ai-generated-media": (
        "1. Show side-by-side examples: real photo vs. AI-generated image.\n"
        "2. Point out tell-tale signs: odd hands, unnatural eyes, blurred backgrounds.\n"
        "3. Discuss: AI can also generate realistic-sounding text. What does that mean for news?\n"
        "4. Use a tool like 'Is It AI?' or a reverse image search to check a suspicious image together.\n"
        "5. Mark complete when the child can spot at least 2 signs of AI-generated content."
    ),
    "use-two-step-verification": (
        "1. Open account settings on an email or social media account.\n"
        "2. Enable two-factor authentication — show the SMS or app-based options.\n"
        "3. Log out and log back in to experience the 2-step process.\n"
        "4. Explain: even if someone steals your password, they still can't get in.\n"
        "5. Mark complete when 2FA is enabled on at least one account."
    ),
    # NAVIGATION ──────────────────────────────────────────────────────────────
    "know-full-name-address-phone": (
        "1. Write the child's full name, home address, and parent phone on a card.\n"
        "2. Drill until they can recite all three without looking — test daily for a week.\n"
        "3. Ask random questions: 'What's your postcode?' 'What's our street number?'\n"
        "4. Practice saying it clearly and calmly, as if to a police officer or shop assistant.\n"
        "5. Mark complete when the child answers all three from memory under pressure."
    ),
    "know-parent-phone-memorized": (
        "1. Write one parent's mobile number in large digits.\n"
        "2. Repeat it aloud with the child 10 times a day for 3 days.\n"
        "3. Test without the paper — forwards and backwards.\n"
        "4. Once mastered, add the second parent's number.\n"
        "5. Mark complete when both numbers are recalled without hesitation."
    ),
    "identify-home-school-shop": (
        "1. Walk the route from home to school together, naming key landmarks.\n"
        "2. Ask the child to describe the route back.\n"
        "3. On a blank page, draw a simple map together — home, school, nearest shop.\n"
        "4. Ask: 'Which way would you go if school was shut and you needed to get home?'\n"
        "5. Mark complete when the child can describe all three locations and routes."
    ),
    "walk-to-mailbox-and-back": (
        "1. Show the child exactly where the mailbox or front gate is.\n"
        "2. Walk with them once, then watch from the door as they do it alone.\n"
        "3. Extend: walk to the end of the street and back.\n"
        "4. Discuss: 'What would you do if a car stopped and the driver asked you to get in?'\n"
        "5. Mark complete after 5 successful solo micro-trips."
    ),
    "look-both-ways": (
        "1. Stand at the kerb together — not touching the road.\n"
        "2. Drill the habit: stop at edge, look right, look left, look right again.\n"
        "3. Wait for a clear gap in traffic — not just a slowing car.\n"
        "4. Practise at 5 different crossing points over 2 weeks.\n"
        "5. Mark complete when the habit is automatic and requires no reminder."
    ),
    "cross-crosswalk-with-parent": (
        "1. At a zebra crossing: stop, look both ways, make eye contact with drivers.\n"
        "2. Walk (don't run) — and keep looking as you cross.\n"
        "3. At a pelican crossing: press button, wait for green man, check traffic still stopping.\n"
        "4. Cross together 10 times on real crossings, varying the crossing type.\n"
        "5. Mark complete when the child follows all crossing rules without prompts."
    ),
    "use-pedestrian-signal": (
        "1. Show the button, the light, and the green/red man.\n"
        "2. Explain: the green man means it's safe, but STILL check traffic.\n"
        "3. Practice waiting patiently — no crossing on red, even if road looks empty.\n"
        "4. Show what to do when signals are broken (treat as give-way, make eye contact with drivers).\n"
        "5. Mark complete when the child uses pedestrian signals correctly every time."
    ),
    "stranger-safety-basics": (
        "1. Clarify the rule: most strangers are fine — but don't go anywhere with one alone.\n"
        "2. Safe adults if lost: police, shop staff, a family with children.\n"
        "3. Role-play: a stranger asks them to help find a lost dog. Child says 'No' and walks to a safe place.\n"
        "4. Agree a family codeword — if someone says 'Your mum sent me', they must say the codeword.\n"
        "5. Mark complete when the child can explain the rule and demonstrate 2 safe responses."
    ),
    "dial-emergency-number": (
        "1. Tell the child the emergency number (999 / 911 / 112 for your country).\n"
        "2. Explain what counts as an emergency: fire, someone seriously hurt, danger.\n"
        "3. Role-play: 'A stranger has collapsed. What do you do?' — child calls, gives address, stays calm.\n"
        "4. Explain: emergency calls are free even from a locked phone.\n"
        "5. Mark complete when the child can recall the number and simulate the call correctly."
    ),
    "identify-landmarks-near-home": (
        "1. Walk a 10-minute radius around home together.\n"
        "2. Name 5 landmarks: a distinctive building, a park, a shop, a post box, a school.\n"
        "3. At home, the child draws or lists all 5 from memory.\n"
        "4. Quiz: 'If you came out of school and turned left, what's the first landmark?'\n"
        "5. Mark complete when the child can name 5 landmarks and place them correctly relative to home."
    ),
    "follow-simple-sketch-map": (
        "1. Draw a simple map of your neighbourhood with labelled landmarks.\n"
        "2. Give the child the map and a starting point — they navigate to a destination.\n"
        "3. Discuss: 'Which way does the map need to face to match the real world?'\n"
        "4. Try a second route using the same map.\n"
        "5. Mark complete when the child follows a sketch map to a correct destination."
    ),
    "read-street-transit-signs": (
        "1. Walk around and point out 10 common signs: stop, give way, bus stop, no entry.\n"
        "2. Ask the child to explain each one in their own words.\n"
        "3. For transit signs: bus route numbers, direction arrows, timetable boards.\n"
        "4. Quiz: point to a sign — 'What does this mean? What should a driver/pedestrian do?'\n"
        "5. Mark complete when the child correctly explains 10 common signs."
    ),
    "ride-bike-with-helmet": (
        "1. Check helmet fit — two fingers above eyebrows, straps snug, no wobble.\n"
        "2. On a quiet road or path: start, stop, and signal before turning.\n"
        "3. Left/right hand signal before every turn.\n"
        "4. Ride 15 minutes on a route with minor road crossings.\n"
        "5. Mark complete when the child rides confidently with correct signals and road awareness."
    ),
    "take-bus-with-parent": (
        "1. Find the correct bus stop and route number together.\n"
        "2. At the stop: check the timetable, wait back from the kerb.\n"
        "3. Board: tap card or pay fare — say 'Thank you' to driver.\n"
        "4. Track the stops — know when to press the bell and exit.\n"
        "5. Mark complete after 2 full bus journeys with the child leading each step."
    ),
    "buy-transit-ticket": (
        "1. At the machine or counter: look up the correct ticket type first.\n"
        "2. Child inserts payment (card or cash), selects ticket, collects it.\n"
        "3. Check the ticket: is it for the right route and date?\n"
        "4. Tap out/in with a contactless card if applicable.\n"
        "5. Mark complete after the child buys a ticket independently on 2 occasions."
    ),
    "cross-busy-intersection-solo": (
        "1. Practise the intersection many times with you present first.\n"
        "2. Agree a signal (wave from far side) so you know they're safe.\n"
        "3. First solo crossing: you watch from a distance they can't see you.\n"
        "4. Debrief: 'What did you check? Were you nervous? What would you do differently?'\n"
        "5. Mark complete after 3 successful solo crossings on different days."
    ),
    "walk-to-friend-house-solo": (
        "1. Walk the route together twice, naming key landmarks and turn points.\n"
        "2. Agree: text when you leave, text when you arrive.\n"
        "3. If not heard from in 15 minutes, parent calls.\n"
        "4. First solo trip. Debrief together — what did they notice, how did they feel?\n"
        "5. Mark complete when the child completes the trip reliably without reminders."
    ),
    "use-phone-maps-app": (
        "1. Open Google Maps / Apple Maps and search for a destination.\n"
        "2. Explore the route before starting — zoom in on key turns.\n"
        "3. Set off walking (not in a car) following the app.\n"
        "4. Discuss: 'What if the battery dies? What if the GPS is wrong?' Always have a backup plan.\n"
        "5. Mark complete when the child can plan and follow a walking route independently."
    ),
    "plan-route-with-stops": (
        "1. Set a real task: walk to the library, then the park, then home.\n"
        "2. Child plans the order of stops to minimise backtracking.\n"
        "3. Estimate how long the trip will take — check against actual time.\n"
        "4. Discuss what to do if one stop is closed or plans change mid-trip.\n"
        "5. Mark complete when the child plans and executes a multi-stop trip."
    ),
    "ride-transit-independently": (
        "1. Choose a short, familiar route for the first solo trip.\n"
        "2. Agree: text at departure, arrival, and any delays.\n"
        "3. Child boards, tracks stops, exits at the right stop without help.\n"
        "4. Debrief: what was easy, what was harder than expected?\n"
        "5. Mark complete after 3 solo transit trips on 3 different days."
    ),
    # COGNITIVE ───────────────────────────────────────────────────────────────
    "follow-three-step-instruction": (
        "1. Give a 3-step instruction once, clearly: 'Bring your jacket, put on your shoes, wait by the door.'\n"
        "2. Child does all three without asking you to repeat.\n"
        "3. Gradually increase complexity: 4 steps, then 5, with sub-steps.\n"
        "4. If they forget, discuss what went wrong — without frustration.\n"
        "5. Mark complete when the child reliably follows 3-step instructions."
    ),
    "tell-time-analog-clock": (
        "1. Show an analog clock and explain the hour hand (short) and minute hand (long).\n"
        "2. Hour hand: whatever number it's on = the hour. Minute hand: count by 5s.\n"
        "3. Set the clock to 5 times and the child reads each aloud.\n"
        "4. Introduce quarter-past, half-past, quarter-to.\n"
        "5. Mark complete when the child reads any time on an analog clock without help."
    ),
    "use-calendar-find-date": (
        "1. Ask the child to find today's date on a wall calendar.\n"
        "2. Questions: 'What day is it? What day is your birthday? How many days until school break?'\n"
        "3. Show how to count forward and backward across months.\n"
        "4. Let the child add an upcoming event to the calendar.\n"
        "5. Mark complete when the child can find any date and count days between events."
    ),
    "sort-by-invented-rule": (
        "1. Place 20 mixed objects on a table (coins, pencils, books, food items).\n"
        "2. Ask the child to invent a rule and sort by it — without telling you the rule first.\n"
        "3. You try to guess the rule — then they reveal it.\n"
        "4. Swap: they guess YOUR sorting rule.\n"
        "5. Mark complete when the child invents 3 different rules and applies each consistently."
    ),
    "spot-pattern-in-sequence": (
        "1. Write a number sequence (2, 4, 6, 8 ...) — ask: 'What comes next? What's the rule?'\n"
        "2. Move to harder patterns: 1, 2, 4, 8... or A, C, E, G...\n"
        "3. Extend to visual patterns with shapes — draw the next in the sequence.\n"
        "4. Ask the child to CREATE a pattern for you to guess.\n"
        "5. Mark complete when the child can solve and create patterns with varying difficulty."
    ),
    "summarize-short-story": (
        "1. Read a short story or news article aloud together.\n"
        "2. Ask: 'What happened? Who was involved? What was the key event?'\n"
        "3. Child writes or says a 3-sentence summary.\n"
        "4. Check: does the summary cover the main points without too much detail?\n"
        "5. Mark complete after 3 successful summaries of different texts."
    ),
    "ask-why-research-answer": (
        "1. The next time the child asks a question, pause: 'Where could we find out?'\n"
        "2. Together, find the answer in a book, encyclopaedia, or trusted website.\n"
        "3. Read the source — discuss whether it's trustworthy.\n"
        "4. Encourage the child to ask one 'why?' per day and look it up.\n"
        "5. Mark complete when the child initiates research independently 5 times."
    ),
    "explain-process-in-order": (
        "1. Ask the child to explain something they know well: how to make toast, how football works.\n"
        "2. Listen without interrupting — note any steps they skip or put out of order.\n"
        "3. Point out the gaps gently: 'What happens before that?' 'Did you miss a step?'\n"
        "4. Child repeats the explanation — this time in correct order.\n"
        "5. Mark complete when the child can explain 2 different processes without gaps."
    ),
    "estimate-before-measuring": (
        "1. Before measuring anything (length, weight, volume), the child states their estimate first.\n"
        "2. Measure the actual value and compare — no shame if way off!\n"
        "3. Discuss: 'Why was your estimate off? What would help you guess better next time?'\n"
        "4. Practice daily: 'How long do you think dinner will take? How far is it to the shops?'\n"
        "5. Mark complete after 10 estimate-then-measure rounds across different types."
    ),
    "make-pros-cons-list": (
        "1. Face a real decision together: a purchase, a plan, a choice.\n"
        "2. Draw a line down the middle — PROS on one side, CONS on the other.\n"
        "3. Fill in both columns honestly. Which side has more, or more weight?\n"
        "4. Make the decision — then check it was the right call later.\n"
        "5. Mark complete when the child reaches for a pros/cons list naturally before deciding."
    ),
    "set-personal-goal-weekly": (
        "1. Every Sunday evening: 'What is ONE thing you want to achieve this week?'\n"
        "2. Write it down — specific and achievable in 7 days.\n"
        "3. Check in mid-week: 'How is the goal going?'\n"
        "4. Sunday again: 'Did you achieve it? What helped or got in the way?'\n"
        "5. Mark complete after 4 consecutive weeks of setting and reviewing goals."
    ),
    "break-task-into-steps": (
        "1. Choose a big task (a school project, tidying a room).\n"
        "2. Ask the child: 'What needs to happen first? Then what? What's last?'\n"
        "3. Write out the steps — number them.\n"
        "4. Work through them one at a time, ticking each off.\n"
        "5. Mark complete when the child can decompose any big task into steps without help."
    ),
    "manage-homework-schedule": (
        "1. On Monday, list all homework due that week and the deadline for each.\n"
        "2. Allocate each piece to a specific day — don't cram everything to Thursday.\n"
        "3. Child follows the schedule without reminders for a full week.\n"
        "4. Review: was anything left too late? Adjust for next week.\n"
        "5. Mark complete after 3 weeks of self-managed homework scheduling."
    ),
    "resolve-disagreement-words": (
        "1. When a disagreement arises, pause: 'Let's each say what we think without interrupting.'\n"
        "2. Child says their view — you listen. You say yours — child listens.\n"
        "3. Ask: 'What does the other person actually need here?'\n"
        "4. Find a compromise that addresses both sides — or agree to disagree calmly.\n"
        "5. Mark complete when the child uses words (not tears or shouting) to resolve 3 real disagreements."
    ),
    "accept-feedback-calmly": (
        "1. Give genuine, honest feedback on something the child did.\n"
        "2. Child's job: listen without interrupting, say 'Thank you', ask one question.\n"
        "3. Discuss: 'Was any of it true? What could you use from it?'\n"
        "4. Repeat with feedback from a teacher or friend — discuss how it felt.\n"
        "5. Mark complete when the child can receive feedback without shutting down or arguing."
    ),
    "ask-clarifying-question": (
        "1. Give an ambiguous instruction (vague or incomplete).\n"
        "2. Wait to see if the child asks for clarification instead of guessing.\n"
        "3. Teach the formula: 'Just to check — do you mean X or Y?'\n"
        "4. Role-play 3 scenarios requiring clarifying questions.\n"
        "5. Mark complete when the child asks clarifying questions naturally in real situations."
    ),
    "decide-with-incomplete-info": (
        "1. Present a realistic scenario with missing information: 'You're planning a picnic but don't know the weather.'\n"
        "2. Ask: 'What do you know? What don't you know? What's the safest decision?'\n"
        "3. Discuss: gathering more info vs. deciding now with a backup plan.\n"
        "4. Repeat with 2 more scenarios.\n"
        "5. Mark complete when the child can reason through uncertainty without paralysis."
    ),
    "detect-biased-argument": (
        "1. Find a one-sided opinion piece or advertisement.\n"
        "2. Ask: 'What information is missing? Who is this trying to persuade?'\n"
        "3. Find a counter-argument together.\n"
        "4. Repeat with a political example — age appropriately — and a product claim.\n"
        "5. Mark complete when the child can identify at least 2 signs of bias in new material."
    ),
    "spot-basic-logical-fallacy": (
        "1. Introduce the straw-man: exaggerating someone's argument to knock it down.\n"
        "2. Introduce ad hominem: attacking the person, not the argument.\n"
        "3. Show real examples from adverts or debates (age-appropriate).\n"
        "4. Child identifies which fallacy is being used in 3 new examples.\n"
        "5. Mark complete when the child can name and spot at least 2 fallacies."
    ),
    "teach-younger-kid-skill": (
        "1. Child selects a skill they know well and a younger sibling/cousin/neighbour to teach.\n"
        "2. They plan how to explain it — what steps? What might be hard?\n"
        "3. They teach it — you observe quietly.\n"
        "4. Discuss afterward: 'What was hard to explain? What did you have to think about differently?'\n"
        "5. Mark complete when the younger child can perform the skill after being taught."
    ),
    # First aid / safety (new tasks added below in NEW_TASKS)
    "first-aid-small-cut": (
        "1. Show the first aid kit — know where it is and what's in it.\n"
        "2. Wash hands first, then clean the cut under running water.\n"
        "3. Pat dry with a clean cloth — don't rub.\n"
        "4. Apply antiseptic if available, then cover with an appropriately sized plaster.\n"
        "5. Mark complete when the child can treat a minor cut correctly without help."
    ),
    "call-for-help-emergency": (
        "1. Discuss what counts as an emergency vs. not (cut finger = no; unconscious person = yes).\n"
        "2. Practice: 'Call 999/911, state your name, address, and what's happened.'\n"
        "3. Stay on the line — the operator will guide you.\n"
        "4. Practice the script aloud 3 times.\n"
        "5. Mark complete when the child can recite the emergency script confidently."
    ),
    "fire-escape-plan": (
        "1. Walk every room in the house and identify: the two best exit routes.\n"
        "2. Set a family meeting point outside (e.g. the front gate).\n"
        "3. Practice: if the fire alarm goes off, everyone stops everything and exits.\n"
        "4. Drill it — unannounced — at least twice.\n"
        "5. Mark complete when the child knows the plan and exits to the meeting point in a drill."
    ),
    "home-alone-safely": (
        "1. Agree the rules: keep the door locked, don't open to strangers, no mention on social media.\n"
        "2. Know what to do if the fire alarm goes off, or if someone unwell calls.\n"
        "3. Have a list of numbers to call: parent, neighbour, emergency.\n"
        "4. Start with 30-minute periods — build up over weeks.\n"
        "5. Mark complete when the child manages 2 hours alone calmly and safely."
    ),
}

# ─── New tasks to add with full content ──────────────────────────────────────
# (slug, title, sex_filter, tag_category, min_age, max_age, envs, parent_note, prereqs)
NEW_TASKS = [
    (
        "first-aid-small-cut",
        "Treat a small cut with basic first aid",
        SexFilter.ANY,
        "reasoning",
        8, 13,
        ALL_ENVS,
        (
            "Basic first aid is one of the highest-value safety skills a child can learn. "
            "A child who can clean and dress a small wound calmly reduces infection risk, "
            "avoids unnecessary panic, and begins to understand that their body is something "
            "they can care for themselves. Studies show children with first aid training are "
            "significantly calmer in emergencies throughout their lives."
        ),
        [],
    ),
    (
        "call-for-help-emergency",
        "Call the emergency services and give your address",
        SexFilter.ANY,
        "reasoning",
        8, 13,
        ALL_ENVS,
        (
            "Children are often first on scene in household emergencies. A child who can dial "
            "the emergency number, state their address clearly, and stay on the line can summon "
            "life-saving help minutes faster than an adult who arrives after the fact. "
            "This skill costs nothing to teach and has saved lives."
        ),
        ["know-full-name-address-phone"],
    ),
    (
        "fire-escape-plan",
        "Know and practise your home fire escape plan",
        SexFilter.ANY,
        "reasoning",
        8, 13,
        ALL_ENVS,
        (
            "House fires move faster than most people expect — toxic smoke can incapacitate within "
            "minutes. A pre-drilled escape plan removes the need to think under panic. Children "
            "who have practiced the route exit up to 3 times faster than those who haven't. "
            "This is one of the simplest and highest-impact safety drills a family can do."
        ),
        [],
    ),
    (
        "home-alone-safely",
        "Stay home alone safely for up to 2 hours",
        SexFilter.ANY,
        "reasoning",
        10, 13,
        ALL_ENVS,
        (
            "Learning to be home alone responsibly is a major developmental milestone. Children "
            "given graduated independence report higher self-confidence and lower anxiety than "
            "those kept in close supervision. The key is explicit preparation — not just leaving "
            "and hoping for the best. Rules, contact numbers, and practiced scenarios make the "
            "difference between a frightening experience and an empowering one."
        ),
        ["call-for-help-emergency", "fire-escape-plan"],
    ),
    (
        "make-simple-meal",
        "Cook a simple hot meal with light supervision",
        SexFilter.ANY,
        "kitchen-basics",
        11, 13,
        ALL_ENVS,
        (
            "Cooking a meal — even pasta with sauce — is transformative for a child's sense of "
            "independence. It combines planning, safe tool use, timing, and nutrition awareness. "
            "Research consistently shows that children who cook regularly eat more healthily as "
            "adults and have a significantly more positive relationship with food."
        ),
        ["use-microwave-safely", "make-cold-sandwich"],
    ),
    (
        "iron-clothing",
        "Iron a simple item of clothing safely",
        SexFilter.ANY,
        "home-care",
        12, 13,
        ALL_ENVS,
        (
            "Ironing is often deferred until a child leaves home — when it's usually learned "
            "in a rush before an interview or important event. Teaching it early removes a common "
            "gap in practical self-sufficiency. The safety aspects (burns, fire risk) are also "
            "important life skills in their own right."
        ),
        ["operate-washing-machine", "fold-tshirt"],
    ),
    (
        "sew-on-button",
        "Sew a loose button back onto clothing",
        SexFilter.ANY,
        "home-care",
        11, 13,
        ALL_ENVS,
        (
            "Sewing a button is a small but meaningful act of self-sufficiency. It prevents "
            "perfectly good clothing being discarded for a trivial fault. Children who can do "
            "basic repairs develop a 'fix it first' mindset that reduces waste and saves money "
            "throughout their lives."
        ),
        [],
    ),
    (
        "shaving-basics",
        "Learn the basics of safe face shaving",
        SexFilter.MALE,
        "home-care",
        12, 13,
        ALL_ENVS,
        (
            "The first shave is a rite of passage that's increasingly neglected because parents "
            "assume boys will 'figure it out'. Poor technique leads to cuts, ingrown hairs, and "
            "skin damage. A parent who takes 20 minutes to teach correct method — grain direction, "
            "moisture, no pressure — protects their son's skin and earns significant trust."
        ),
        [],
    ),
    (
        "menstrual-health-basics",
        "Understand and manage menstrual health independently",
        SexFilter.FEMALE,
        "reasoning",
        10, 13,
        ALL_ENVS,
        (
            "Girls who understand menstruation before it starts report significantly lower anxiety "
            "and fewer absences from school. This skill is about practical management — knowing "
            "what to use, keeping a spare kit at school, tracking the cycle — as well as "
            "normalising a natural process. Open, factual teaching from a parent is the most "
            "effective way to build both competence and confidence."
        ),
        [],
    ),
    (
        "self-advocacy-asking-for-help",
        "Ask a teacher or adult for help confidently",
        SexFilter.ANY,
        "reasoning",
        8, 13,
        ALL_ENVS,
        (
            "Many children — especially high-achieving ones — avoid asking for help because it "
            "feels like admitting weakness. Normalising help-seeking as a strength, not a flaw, "
            "has measurable effects on learning outcomes, mental health, and adult career success. "
            "Children who ask for help when needed outperform those who struggle silently."
        ),
        [],
    ),
    (
        "pack-travel-bag",
        "Pack a bag for an overnight trip independently",
        SexFilter.ANY,
        "home-care",
        9, 13,
        ALL_ENVS,
        (
            "Packing independently requires forward planning — thinking about what you'll need "
            "for each part of the trip, what the weather might be, and what you can't forget. "
            "Children who do this regularly develop significantly stronger anticipation and "
            "planning skills than those who are packed for by their parents."
        ),
        ["make-bed"],
    ),
    (
        "read-a-food-label",
        "Read and understand a food nutrition label",
        SexFilter.ANY,
        "reasoning",
        10, 13,
        ALL_ENVS,
        (
            "Food labels contain enormous amounts of health information that most adults ignore "
            "or can't interpret. Children who learn to read labels from an early age make healthier "
            "choices, spot hidden sugar and salt, and develop a critical relationship with food "
            "marketing. This is one of the most direct health-literacy skills available."
        ),
        ["read-price-tag"],
    ),
    (
        "write-a-thank-you-note",
        "Write a genuine, specific thank-you note or message",
        SexFilter.ANY,
        "reasoning",
        8, 13,
        ALL_ENVS,
        (
            "Thank-you notes teach children that gratitude is an action, not just a feeling. "
            "The discipline of being specific — saying what they received and why it mattered — "
            "builds empathy, communication skills, and social intelligence. Adults who were "
            "taught this as children report stronger relationships and professional networks."
        ),
        [],
    ),
    (
        "navigate-public-library",
        "Use a public library: find, borrow, and return books",
        SexFilter.ANY,
        "wayfinding",
        9, 13,
        ALL_ENVS,
        (
            "Public libraries are one of the most valuable free resources available to children, "
            "yet many never learn to use them independently. A child who can navigate a library "
            "— find a section, use a catalogue, get a library card — gains access to thousands "
            "of books and resources for life. This skill also builds institutional confidence."
        ),
        ["identify-home-school-shop"],
    ),
    (
        "handle-peer-pressure",
        "Recognise and calmly resist peer pressure",
        SexFilter.ANY,
        "reasoning",
        10, 13,
        ALL_ENVS,
        (
            "Peer pressure is one of the primary drivers of risk-taking behaviour in adolescence. "
            "Children who have practised refusal skills — not just been told to say no — are "
            "significantly more resistant to pressure around substances, dangerous activities, "
            "and social exclusion. The key is rehearsing the specific words and calm body language."
        ),
        ["resolve-disagreement-words"],
    ),
    (
        "manage-emotions-calm-down",
        "Use a calming strategy when angry or overwhelmed",
        SexFilter.ANY,
        "reasoning",
        7, 13,
        ALL_ENVS,
        (
            "Emotional regulation is the single most important social-emotional skill — it "
            "underpins academic performance, relationship quality, and mental health. Children "
            "who have a practiced 'calm-down' strategy (deep breathing, counting, stepping away) "
            "recover from emotional flooding faster and make better decisions under stress."
        ),
        [],
    ),
    (
        "plan-and-host-event",
        "Plan and host a simple event (birthday party, study group)",
        SexFilter.ANY,
        "reasoning",
        10, 13,
        ALL_ENVS,
        (
            "Planning an event requires project management in miniature: budgeting, scheduling, "
            "delegating, anticipating problems. Children who host events — even small ones — "
            "develop leadership, hospitality, and organisational skills that transfer directly "
            "to school projects, work, and adult life."
        ),
        ["make-pros-cons-list", "break-task-into-steps"],
    ),
]

# How-to text for new tasks (slug → markdown)
NEW_HOW_TOS = {
    "make-simple-meal": (
        "1. Choose a recipe with 5 or fewer ingredients (e.g. pasta with tomato sauce, egg on toast).\n"
        "2. Read the full recipe before starting — gather all ingredients and equipment.\n"
        "3. Follow each step in order, asking for help only when genuinely unsure.\n"
        "4. Use oven gloves for hot pans — always turn handles inward so they can't be knocked.\n"
        "5. Mark complete when the child cooks a full meal from start to clean-up independently."
    ),
    "iron-clothing": (
        "1. Check the garment's label for the correct temperature setting.\n"
        "2. Set the iron to the right heat and wait until it's fully warm.\n"
        "3. Iron with the grain of the fabric — slow, steady strokes.\n"
        "4. Never leave the iron face-down — always stand it upright or switch off.\n"
        "5. Mark complete when the child irons a shirt or trousers without creasing or scorching."
    ),
    "sew-on-button": (
        "1. Thread the needle and knot the end of the thread.\n"
        "2. Push needle up through fabric from the back — through one button hole.\n"
        "3. Stitch up through one hole, down through the other — 6 times.\n"
        "4. Wrap thread around the stitches (the shank) twice, then knot behind the fabric.\n"
        "5. Mark complete when the child's button is secure and doesn't wobble."
    ),
    "shaving-basics": (
        "1. Wet the face with warm water — this softens the hair.\n"
        "2. Apply shaving foam or gel and work it in with fingers.\n"
        "3. Shave WITH the grain (direction of hair growth) using light, short strokes.\n"
        "4. Rinse the razor after each stroke — never press hard.\n"
        "5. Mark complete when the child can complete a full shave without cuts."
    ),
    "menstrual-health-basics": (
        "1. Explain the menstrual cycle factually — what happens and why.\n"
        "2. Show the products available (pads, tampons, period pants) — let them choose what they prefer.\n"
        "3. Prepare a period kit for school bag: 2 pads, spare underwear, small bag.\n"
        "4. Show how to track the cycle on a calendar or app.\n"
        "5. Mark complete when the child can manage a period independently and know who to ask for help."
    ),
    "self-advocacy-asking-for-help": (
        "1. Identify one situation where the child struggles but doesn't ask for help.\n"
        "2. Practise the words: 'I don't understand X — could you explain it differently?'\n"
        "3. Role-play asking a teacher, a stranger in a shop, or a friend for help.\n"
        "4. Do the real thing — report back how it went.\n"
        "5. Mark complete when the child asks for help in a real situation without prompting."
    ),
    "pack-travel-bag": (
        "1. Before packing, list what you'll need for each part of the trip.\n"
        "2. Lay everything out on the bed first — check nothing is missing.\n"
        "3. Heavier items at the bottom of the bag, breakables in the middle.\n"
        "4. Pack enough — but challenge yourself not to overpack.\n"
        "5. Mark complete when the child packs for an overnight trip without reminders or repacking by a parent."
    ),
    "read-a-food-label": (
        "1. Pick up any packaged food and find the nutrition information panel.\n"
        "2. Identify: calories per serving, sugar, salt, saturated fat.\n"
        "3. Compare two similar products (e.g. two cereals) — which is healthier?\n"
        "4. Find the ingredients list — note where sugar appears (any word ending in '-ose' counts).\n"
        "5. Mark complete when the child can read and compare two labels independently."
    ),
    "write-a-thank-you-note": (
        "1. Sit down within 24 hours of receiving a gift or help.\n"
        "2. Write three things: what you received, something specific you liked about it, how you'll use it.\n"
        "3. Hand-write the note — or send a genuine message (not just 'thanks!').\n"
        "4. Post or deliver it.\n"
        "5. Mark complete when the child has written 3 specific, genuine thank-you notes."
    ),
    "navigate-public-library": (
        "1. Visit the library together — get the child a library card.\n"
        "2. Show the Dewey Decimal System sections or genre labels.\n"
        "3. The child picks 2 books independently and checks them out at the desk.\n"
        "4. Return books on time — they set a reminder themselves.\n"
        "5. Mark complete when the child visits and borrows without adult guidance."
    ),
    "handle-peer-pressure": (
        "1. Describe the scenario: a group is doing something risky and pressuring your child to join.\n"
        "2. Practise the phrase: 'No thanks, that's not for me' — said calmly, without lengthy explanation.\n"
        "3. Role-play 3 different scenarios — escalating pressure each time.\n"
        "4. Discuss: 'What makes it hard to say no? What helps?'\n"
        "5. Mark complete when the child demonstrates a calm refusal in at least 2 role-plays."
    ),
    "manage-emotions-calm-down": (
        "1. When calm, teach one strategy: deep breaths (4 in, hold 4, out 4).\n"
        "2. Practise the strategy when NOT upset — so it's available when they are.\n"
        "3. Next time emotions run high: remind (once) of the strategy and step back.\n"
        "4. Debrief afterward: 'Did it help? What felt different?'\n"
        "5. Mark complete when the child uses the strategy independently in a real moment of distress."
    ),
    "plan-and-host-event": (
        "1. Child decides on the event type, date, and guest list (keep it small).\n"
        "2. Write a simple plan: invitations, food/snacks, activities, timing.\n"
        "3. Agree a budget — child manages it.\n"
        "4. Child runs the event: welcomes guests, manages activities, handles anything that goes differently.\n"
        "5. Mark complete when the event happens and the child debriefs what worked and what they'd change."
    ),
}

TAGS_ENSURE = [
    ("home-care",        "Home care",        "household"),
    ("kitchen-basics",   "Kitchen basics",   "household"),
    ("money-basics",     "Money basics",     "financial"),
    ("digital-literacy", "Digital literacy", "digital"),
    ("wayfinding",       "Wayfinding",       "navigation"),
    ("reasoning",        "Reasoning",        "cognitive"),
]


class Command(BaseCommand):
    help = "Expands catalog with full how-to steps, sex filter, extended ages. Idempotent."

    @transaction.atomic
    def handle(self, *args, **options):
        # ── Ensure environments & tags ─────────────────────────────────────
        for kind, _ in Environment.Kind.choices:
            Environment.objects.get_or_create(kind=kind)
        env_cache = {e.kind: e for e in Environment.objects.all()}

        tags: dict[str, Tag] = {}
        for key, display_name, cat in TAGS_ENSURE:
            obj, _ = Tag.objects.get_or_create(name=display_name, defaults={"category": cat})
            tags[key] = obj

        # ── Extend all existing tasks to max_age=13 ────────────────────────
        updated = Task.objects.filter(max_age__lt=13).update(max_age=13)
        self.stdout.write(f"Extended max_age to 13 on {updated} tasks.")

        # ── Update how_to_md for all tasks with expanded steps ─────────────
        improved = 0
        for slug, how_to in HOW_TOS.items():
            n = Task.objects.filter(slug=slug).update(how_to_md=how_to)
            improved += n
        self.stdout.write(f"Updated how-to steps for {improved} tasks.")

        # ── Approve all currently pending tasks ────────────────────────────
        approved = Task.objects.filter(status=ReviewStatus.PENDING).update(
            status=ReviewStatus.APPROVED
        )
        self.stdout.write(f"Approved {approved} pending tasks.")

        # ── Add new tasks ──────────────────────────────────────────────────
        new_count = 0
        for (slug, title, sex_filter, tag_key, lo, hi, envs, parent_note, prereqs) in NEW_TASKS:
            how_to = NEW_HOW_TOS.get(slug, HOW_TOS.get(slug, ""))
            task, created = Task.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "sex_filter": sex_filter,
                    "how_to_md": how_to,
                    "safety_md": "",
                    "parent_note_md": parent_note,
                    "min_age": lo,
                    "max_age": hi,
                    "status": ReviewStatus.APPROVED,
                },
            )
            if created:
                task.environments.set([env_cache[e] for e in envs if e in env_cache])
                tag_obj = tags.get(tag_key)
                if tag_obj:
                    task.tags.set([tag_obj])
                new_count += 1
            else:
                # Update sex_filter and how_to for existing tasks
                Task.objects.filter(slug=slug).update(
                    sex_filter=sex_filter,
                    how_to_md=how_to,
                    parent_note_md=parent_note,
                    status=ReviewStatus.APPROVED,
                )

        self.stdout.write(f"Added {new_count} new tasks.")

        # ── Wire prerequisites for new tasks ───────────────────────────────
        edge_count = 0
        for (slug, _title, _sf, _tag, _lo, _hi, _envs, _note, prereqs) in NEW_TASKS:
            try:
                to_task = Task.objects.get(slug=slug)
            except Task.DoesNotExist:
                continue
            for p_slug in prereqs:
                try:
                    from_task = Task.objects.get(slug=p_slug)
                    _edge, edge_created = PrerequisiteEdge.objects.get_or_create(
                        from_task=from_task,
                        to_task=to_task,
                        defaults={"is_mandatory": True},
                    )
                    if edge_created:
                        edge_count += 1
                except (Task.DoesNotExist, Exception) as e:
                    self.stdout.write(self.style.WARNING(f"  edge skipped: {p_slug}→{slug}: {e}"))

        self.stdout.write(f"Added {edge_count} new prerequisite edges.")
        self.stdout.write(self.style.SUCCESS("expand_catalog complete."))
