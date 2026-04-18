from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0002_task_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="parent_note_md",
            field=models.TextField(
                blank=True,
                help_text="Markdown. Shown to parents only — why this skill matters and what benefits to expect.",
            ),
        ),
    ]
