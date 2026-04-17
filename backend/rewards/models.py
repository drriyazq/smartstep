from django.db import models


class RewardCategory(models.Model):
    class Kind(models.TextChoices):
        TIME = "time", "Time"
        EXPERIENCE = "experience", "Experience"
        MATERIAL = "material", "Material"

    kind = models.CharField(max_length=16, choices=Kind.choices, unique=True)
    display_name = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "reward categories"

    def __str__(self) -> str:
        return self.display_name


class RewardItem(models.Model):
    title = models.CharField(max_length=140)
    category = models.ForeignKey(RewardCategory, on_delete=models.PROTECT, related_name="items")
    min_age = models.PositiveSmallIntegerField(default=7)
    max_age = models.PositiveSmallIntegerField(default=11)
    is_free = models.BooleanField(default=True, help_text="Zero monetary cost to the parent.")
    notes = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self) -> str:
        return self.title
