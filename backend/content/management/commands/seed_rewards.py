"""
Comprehensive reward catalog — replaces the sparse demo rewards.

Covers all age bands:
  5–8   young children
  7–13  children (core)
  13–16 teens
  17+   adults

Run: DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_rewards
Idempotent: clears existing items then re-seeds from REWARDS list.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from rewards.models import RewardCategory, RewardItem

# (title, min_age, max_age, is_free)
REWARDS = {
    "time": {
        "display": "Time & Freedom",
        "items": [
            # Young children 5–8
            ("Stay up 15 min past bedtime",        5,  8, True),
            ("Choose the bedtime story",            5,  8, True),
            ("Extra storytime tonight",             5,  8, True),
            # Children 7–13
            ("Extra 15 min of screen time",         7, 10, True),
            ("Extra 30 min of screen time",         9, 13, True),
            ("Choose tonight's movie",              7, 13, True),
            ("Stay up 30 min past bedtime",         7, 13, True),
            ("Choose the music in the car",         7, 13, True),
            ("1 hour of uninterrupted free play",   7, 12, True),
            ("Breakfast in bed on the weekend",     8, 13, True),
            ("Skip one chore today",                8, 13, True),
            # Teens 13–16
            ("Extra 1 hour of screen time",        13, 16, True),
            ("Sleep in on a holiday morning",      13, 16, True),
            ("Skip a household chore this week",   13, 16, True),
            ("Stay out 30 min later than usual",   14, 16, True),
            # Adults 17+
            ("One obligation-free morning",        17, 99, True),
            ("An afternoon of your chosen leisure",17, 99, True),
            ("Skip a household task this week",    17, 99, True),
            ("A guilt-free rest hour",             17, 99, True),
        ],
    },
    "experience": {
        "display": "Experience",
        "items": [
            # Young children 5–8
            ("Visit the park with a parent",              5,  8, True),
            ("Family game night — you pick the game",     5, 13, True),
            ("Movie night with popcorn",                  5,  9, True),
            # Children 7–13
            ("Visit the park with a friend",              7, 13, True),
            ("Camp out in the living room",               7, 12, True),
            ("Visit the library and choose any 3 books",  7, 13, True),
            ("Invite a friend over for the afternoon",    8, 13, True),
            ("Cook a meal together — your choice",        8, 13, True),
            ("Pick the weekend outing",                   8, 13, True),
            ("Teach a parent your favourite game",        7, 13, True),
            ("Trip to a favourite restaurant",            9, 13, False),
            ("Day trip to a local attraction",            9, 13, False),
            # Teens 13–16
            ("Choose the family weekend plan",           13, 16, True),
            ("Outing with a friend — you decide where",  13, 16, True),
            ("Movie at the cinema",                      13, 16, False),
            ("Cooking session — you design the menu",    13, 16, True),
            ("Day trip somewhere you've been wanting",   14, 16, False),
            # Adults 17+
            ("Dinner at a restaurant of your choice",    17, 99, False),
            ("An evening for your hobby, uninterrupted", 17, 99, True),
            ("Day trip somewhere you've been wanting",   17, 99, False),
            ("Visit a museum, gallery, or cultural site",17, 99, False),
            ("Cook something new — you choose the recipe",17,99, True),
        ],
    },
    "material": {
        "display": "Material",
        "items": [
            # Young children 5–8
            ("Sticker or small toy of your choice",        5,  8, False),
            ("Favourite snack of your choice",             5, 16, True),
            ("Choose what's for dinner tonight",           5, 13, True),
            # Children 7–13
            ("Craft supplies of your choice",              7, 13, False),
            ("Printable achievement certificate",          7, 13, True),
            ("Small stationery set",                       8, 13, False),
            ("New book of your choice",                    8, 16, False),
            ("Choose a new phone wallpaper together",      9, 13, True),
            ("Pocket money bonus",                         9, 16, False),
            # Teens 13–16
            ("Stationery or art supply of your choice",   13, 16, False),
            ("Choose a show for the family to watch",     13, 16, True),
            # Adults 17+
            ("A book or course you've been wanting",      17, 99, False),
            ("A small self-care item or treat",           17, 99, False),
            ("Something for a hobby or interest",         17, 99, False),
            ("Personal spending bonus",                   17, 99, False),
        ],
    },
}


class Command(BaseCommand):
    help = "Seed comprehensive reward catalog (clears old items first). Idempotent."

    @transaction.atomic
    def handle(self, *args, **options):
        # Clear existing items (not categories — keep foreign keys intact)
        deleted, _ = RewardItem.objects.all().delete()
        self.stdout.write(f"Cleared {deleted} existing reward items.")

        total = 0
        for kind, data in REWARDS.items():
            cat, _ = RewardCategory.objects.update_or_create(
                kind=kind,
                defaults={"display_name": data["display"]},
            )
            for title, lo, hi, is_free in data["items"]:
                RewardItem.objects.create(
                    title=title,
                    category=cat,
                    min_age=lo,
                    max_age=hi,
                    is_free=is_free,
                    status="approved",
                )
                total += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Seeded {total} reward items across {len(REWARDS)} categories."
        ))
