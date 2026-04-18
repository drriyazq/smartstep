"""Replaces RewardItem.is_published with status + review_notes — mirrors
the content.Task migration so both models share the same review workflow."""
from django.db import migrations, models


def copy_is_published_to_status(apps, schema_editor):
    RewardItem = apps.get_model("rewards", "RewardItem")
    RewardItem.objects.filter(is_published=True).update(status="approved")
    RewardItem.objects.filter(is_published=False).update(status="draft")


def copy_status_back_to_is_published(apps, schema_editor):
    RewardItem = apps.get_model("rewards", "RewardItem")
    RewardItem.objects.filter(status="approved").update(is_published=True)
    RewardItem.objects.exclude(status="approved").update(is_published=False)


class Migration(migrations.Migration):

    dependencies = [
        ("rewards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rewarditem",
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
            model_name="rewarditem",
            name="review_notes",
            field=models.TextField(blank=True, help_text="Internal reviewer notes."),
        ),
        migrations.RunPython(
            copy_is_published_to_status,
            reverse_code=copy_status_back_to_is_published,
        ),
        migrations.RemoveField(
            model_name="rewarditem",
            name="is_published",
        ),
    ]
