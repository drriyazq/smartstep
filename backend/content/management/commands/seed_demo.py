"""Seeds a small but non-trivial DAG so the Flutter ladder has real data to render.

Idempotent: uses get_or_create / update_or_create throughout. Safe to run repeatedly.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from content.models import Environment, PrerequisiteEdge, Tag, Task
from rewards.models import RewardCategory, RewardItem

TASKS = [
    # slug, title, tag, min/max age, envs, prereq_slugs
    ("count-change", "Count exact change", "money-basics", 7, 9, ["urban", "suburban", "rural"], []),
    ("read-price-tag", "Read a price tag", "money-basics", 7, 9, ["urban", "suburban", "rural"], []),
    ("pay-cashier", "Pay a cashier", "money-basics", 8, 11, ["urban", "suburban"], ["count-change", "read-price-tag"]),
    ("check-change", "Check your change", "money-basics", 8, 11, ["urban", "suburban"], ["count-change"]),
    ("compare-prices", "Compare two prices", "money-basics", 9, 11, ["urban", "suburban", "rural"], ["read-price-tag"]),
    ("use-atm-with-parent", "Use an ATM (with parent)", "money-basics", 10, 11, ["urban", "suburban"], ["count-change", "read-price-tag"]),

    ("boil-water", "Boil water safely", "kitchen-basics", 8, 11, ["urban", "suburban", "rural"], []),
    ("use-stove-knob", "Light a stove burner", "kitchen-basics", 8, 11, ["urban", "suburban", "rural"], []),
    ("crack-egg", "Crack and whisk an egg", "kitchen-basics", 7, 9, ["urban", "suburban", "rural"], []),
    ("cook-pasta", "Cook pasta from dry", "kitchen-basics", 9, 11, ["urban", "suburban", "rural"], ["boil-water", "use-stove-knob"]),
    ("pack-lunchbox", "Pack your own lunchbox", "kitchen-basics", 7, 10, ["urban", "suburban", "rural"], []),
    ("wash-dishes", "Wash a plate and cup", "kitchen-basics", 7, 11, ["urban", "suburban", "rural"], []),
    ("cook-egg", "Cook a fried egg", "kitchen-basics", 9, 11, ["urban", "suburban", "rural"], ["crack-egg", "use-stove-knob"]),
    ("clear-table", "Clear the table after a meal", "kitchen-basics", 7, 11, ["urban", "suburban", "rural"], []),
    ("cook-full-meal", "Cook a simple full meal", "kitchen-basics", 10, 11, ["urban", "suburban", "rural"], ["cook-pasta", "cook-egg", "wash-dishes"]),
]

TAG_META = {
    "money-basics": ("Money basics", Tag.Category.FINANCIAL),
    "kitchen-basics": ("Kitchen basics", Tag.Category.HOUSEHOLD),
}

REWARDS = [
    ("time", "Time", [
        ("Extra 15 min of screen time", 7, 11, True),
        ("Choose tonight's movie", 7, 11, True),
        ("Stay up 30 min past bedtime", 7, 11, True),
    ]),
    ("experience", "Experience", [
        ("Visit the park with a friend", 7, 11, True),
        ("Pick the weekend outing", 8, 11, True),
    ]),
    ("material", "Material", [
        ("Small toy or sticker pack", 7, 10, False),
        ("New book of your choice", 8, 11, False),
    ]),
]


class Command(BaseCommand):
    help = "Seeds demo tasks, tags, environments, and rewards. Idempotent."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding environments…")
        for kind, _ in Environment.Kind.choices:
            Environment.objects.get_or_create(kind=kind)

        self.stdout.write("Seeding tags…")
        tags: dict[str, Tag] = {}
        for slug, (name, category) in TAG_META.items():
            tag, _ = Tag.objects.get_or_create(name=name, defaults={"category": category})
            tag.category = category
            tag.save()
            tags[slug] = tag

        self.stdout.write("Seeding tasks…")
        task_objs: dict[str, Task] = {}
        for slug, title, tag_slug, lo, hi, envs, _prereqs in TASKS:
            task, _ = Task.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "how_to_md": f"## {title}\n\n1. Parent demonstrates first.\n2. Child attempts while parent watches.\n3. Mark complete when child can do it unaided.",
                    "safety_md": "Parent must be present for first attempt.",
                    "min_age": lo,
                    "max_age": hi,
                    "status": "approved",
                },
            )
            task.environments.set(Environment.objects.filter(kind__in=envs))
            task.tags.set([tags[tag_slug]])
            task_objs[slug] = task

        self.stdout.write("Seeding prerequisite edges…")
        for slug, _title, _tag, _lo, _hi, _envs, prereqs in TASKS:
            to_task = task_objs[slug]
            for p in prereqs:
                from_task = task_objs[p]
                if not PrerequisiteEdge.objects.filter(
                    from_task=from_task, to_task=to_task
                ).exists():
                    PrerequisiteEdge(
                        from_task=from_task, to_task=to_task, is_mandatory=True
                    ).save()

        self.stdout.write("Seeding reward categories + items…")
        for cat_slug, display_name, items in REWARDS:
            cat, _ = RewardCategory.objects.update_or_create(
                kind=cat_slug, defaults={"display_name": display_name}
            )
            for title, lo, hi, is_free in items:
                RewardItem.objects.update_or_create(
                    title=title,
                    defaults={
                        "category": cat,
                        "min_age": lo,
                        "max_age": hi,
                        "is_free": is_free,
                        "status": "approved",
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f"Done. Tasks: {Task.objects.count()}, edges: {PrerequisiteEdge.objects.count()}, "
            f"rewards: {RewardItem.objects.count()}."
        ))
