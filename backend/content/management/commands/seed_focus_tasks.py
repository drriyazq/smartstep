"""Management command: 5 focus / self-discipline tasks (cognitive category).

Added 2026-05-20 to unlock the **Focus & Self-Discipline** mastery (age ~13).
The catalog had zero tasks covering attention span, beating procrastination,
single-tasking, distraction control, or habit-building — easily the most
parent-requested life skill we don't yet teach.

All 5 tasks are tagged `Reasoning` (the only existing cognitive Tag),
category `cognitive`, environment-agnostic, sex-agnostic.

Run:
    DJANGO_SETTINGS_MODULE=smartstep.settings.dev venv/bin/python manage.py seed_focus_tasks

Idempotent — `update_or_create(slug=...)` upserts.
"""
from django.core.management.base import BaseCommand

from content.models import Environment, ReviewStatus, Tag, Task


FOCUS_TASKS = [
    {
        "slug": "phone-away-while-studying-age10",
        "title": "Keep the Phone Out of Reach While Studying",
        "min_age": 10, "max_age": 14,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Decide one study slot per day** — agree on a fixed time (e.g. 5–6 pm). "
            "Same time, same place, every weekday.\n"
            "2. **Phone goes to another room** — not face-down on the desk, not on silent in "
            "the bag. Out of arm's reach, ideally out of sight. The brain can't ignore what it "
            "can see.\n"
            "3. **One paper notebook for parking thoughts** — when a 'check Instagram' urge "
            "hits, write it on the notebook and keep going. The urge passes in 30 seconds.\n"
            "4. **No notifications, no music with lyrics** — instrumental fine, lyrics break "
            "language processing.\n"
            "5. **Earn the phone back at the end of the slot** — the contrast makes it feel "
            "like a reward, not a deprivation."
        ),
        "parent_note_md": (
            "Children with phones within reach during study spend ~30% less time on actual "
            "work — even when they don't pick the phone up. The mere presence of a phone "
            "drains attention. This task builds the single habit that protects every other "
            "study skill they have."
        ),
    },
    {
        "slug": "pomodoro-25min-age11",
        "title": "Work in 25-Minute Focused Blocks",
        "min_age": 11, "max_age": 15,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick one task** — homework page, music practice, drawing. One thing, not "
            "three.\n"
            "2. **Set a 25-minute timer** — any clock, phone, or kitchen timer. Tell them "
            "when the timer rings, they get a 5-minute break, no matter what.\n"
            "3. **No leaving the chair, no looking up unrelated things** — water bottle "
            "already there, toilet break already done. Twenty-five minutes is short.\n"
            "4. **5-minute break is non-negotiable** — stand up, look out a window, drink "
            "water. NOT a phone scroll — that resets the brain and the next block suffers.\n"
            "5. **After three blocks, take a longer break** — 15–20 minutes. Three blocks = "
            "75 real minutes of focused work, more than most adults manage."
        ),
        "parent_note_md": (
            "The Pomodoro technique is one of the most replicable productivity habits ever "
            "studied. For children, 25 minutes is also roughly the sustained-attention ceiling "
            "of an 11-year-old — pushing past it produces diminishing returns. Building this "
            "rhythm at 11 means it's automatic by exam years."
        ),
    },
    {
        "slug": "two-minute-rule-procrastination-age12",
        "title": "Beat Procrastination with the Two-Minute Rule",
        "min_age": 12, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Teach the rule** — if a task takes less than two minutes, do it now. "
            "Putting the dish in the sink, sending the reply, packing the bag for tomorrow. "
            "Do not 'remember to do it later.'\n"
            "2. **For bigger tasks, commit to only two minutes** — open the textbook, "
            "write one sentence of the essay, do five push-ups. Starting is 90% of "
            "the work.\n"
            "3. **Notice the urge to delay** — name it out loud: 'I'm procrastinating "
            "right now.' Awareness halves the avoidance.\n"
            "4. **Move physically before deciding** — stand up, go to the desk, open "
            "the book. Body first, motivation follows.\n"
            "5. **Track wins** — at the end of the day, count how many two-minute "
            "actions you took. The number climbs fast."
        ),
        "parent_note_md": (
            "Procrastination is rarely a discipline problem — it's a starting problem. The "
            "two-minute rule lowers the cost of beginning to almost zero. Once started, the "
            "brain's intrinsic completion drive usually carries the task through. This is "
            "the single most useful adult-life habit a teenager can learn."
        ),
    },
    {
        "slug": "single-task-not-multi-age13",
        "title": "Single-Task Instead of Multitasking",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Notice the multitasking impulse** — having WhatsApp open while doing "
            "homework, watching a show while eating dinner, scrolling while talking to "
            "parents. List the daily ones.\n"
            "2. **Pick three slots a day for single-tasking** — homework, meals, family "
            "conversation. One task at a time, fully.\n"
            "3. **Close every other tab/app** — physical and digital. If studying, only the "
            "study material. If eating, no phone at the table.\n"
            "4. **Notice how it feels** — most teenagers say single-tasking feels boring at "
            "first, then sharp and calm by week two. Both feelings are normal.\n"
            "5. **Measure output, not time** — pages read with full attention beat pages "
            "scrolled past in parallel."
        ),
        "parent_note_md": (
            "Neuroscience is now unambiguous: multitasking does not exist for cognitive "
            "tasks — what looks like multitasking is rapid task-switching, and every switch "
            "costs ~30 seconds of mental re-loading. Teenagers who learn to single-task "
            "outperform their multitasking peers on every measure of comprehension, retention, "
            "and emotional regulation."
        ),
    },
    {
        "slug": "build-seven-day-habit-age13",
        "title": "Build a New Habit Over Seven Days",
        "min_age": 13, "max_age": 16,
        "how_to_md": (
            "## How to practise\n\n"
            "1. **Pick a small, specific habit** — drink one glass of water on waking, "
            "write one sentence in a journal before bed, ten push-ups after brushing teeth. "
            "Tiny and clearly defined.\n"
            "2. **Anchor it to an existing routine** — 'right after I brush my teeth' is a "
            "stronger anchor than 'in the morning.' The existing routine becomes the trigger.\n"
            "3. **Tick a paper chart for seven days** — visible on the wall or fridge. "
            "Manual ticks beat phone apps for habit-building — the friction makes it "
            "meaningful.\n"
            "4. **Miss a day? Resume the next day, don't restart the count** — perfectionism "
            "kills habits. Consistency over time matters more than an unbroken streak.\n"
            "5. **At day seven, decide** — keep it (it now feels almost automatic), or "
            "swap it for a different small habit. Either way, you've practised the meta-"
            "skill of habit-building."
        ),
        "parent_note_md": (
            "Seven days isn't enough for a habit to become fully automatic (research suggests "
            "30–60 days for that) — but it IS enough to feel the early hook, where the brain "
            "starts cuing the behaviour without conscious prompting. Once a teenager has "
            "experienced that hook even once, they know it's a learnable skill rather than "
            "a personality trait."
        ),
    },
]


class Command(BaseCommand):
    help = "Seed 5 focus / self-discipline tasks (cognitive). Run once; idempotent."

    def handle(self, *args, **options):
        all_envs = list(Environment.objects.all())
        tag, _ = Tag.objects.get_or_create(
            name="Reasoning", defaults={"category": Tag.Category.COGNITIVE}
        )

        added = 0
        updated = 0
        for t in FOCUS_TASKS:
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
                },
            )
            task.tags.set([tag])
            task.environments.set(all_envs)
            if created:
                added += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"seed_focus_tasks: {added} new, {updated} updated. "
                f"Total focus tasks now: {len(FOCUS_TASKS)}."
            )
        )
