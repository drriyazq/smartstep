"""Replaces Task.is_published (bool) with Task.status (enum) + review_notes.

Workflow: draft → pending → approved → (rejected). Only `approved` rows are
served by the public API. Existing is_published=True rows become approved;
False rows become draft so they stay hidden until a reviewer acts on them.
"""
from django.db import migrations, models


def copy_is_published_to_status(apps, schema_editor):
    Task = apps.get_model("content", "Task")
    Task.objects.filter(is_published=True).update(status="approved")
    Task.objects.filter(is_published=False).update(status="draft")


def copy_status_back_to_is_published(apps, schema_editor):
    Task = apps.get_model("content", "Task")
    Task.objects.filter(status="approved").update(is_published=True)
    Task.objects.exclude(status="approved").update(is_published=False)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("pending", "Pending review"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                db_index=True,
                default="draft",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="review_notes",
            field=models.TextField(blank=True, help_text="Internal reviewer notes."),
        ),
        migrations.RunPython(
            copy_is_published_to_status,
            reverse_code=copy_status_back_to_is_published,
        ),
        migrations.RemoveField(
            model_name="task",
            name="is_published",
        ),
    ]
