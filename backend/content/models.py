from django.core.exceptions import ValidationError
from django.db import models


class Environment(models.Model):
    class Kind(models.TextChoices):
        URBAN = "urban", "Urban"
        SUBURBAN = "suburban", "Suburban"
        RURAL = "rural", "Rural"

    kind = models.CharField(max_length=16, choices=Kind.choices, unique=True)

    def __str__(self) -> str:
        return self.get_kind_display()


class ReviewStatus(models.TextChoices):
    """Review workflow: draft → pending → approved (or rejected). Only `approved`
    rows are served by the public API."""

    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class Tag(models.Model):
    class Category(models.TextChoices):
        FINANCIAL = "financial", "Financial"
        HOUSEHOLD = "household", "Household"
        DIGITAL = "digital", "Digital"
        NAVIGATION = "navigation", "Navigation"
        COGNITIVE = "cognitive", "Cognitive"
        SOCIAL = "social", "Social"

    name = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=16, choices=Category.choices)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return f"{self.get_category_display()}: {self.name}"


class SexFilter(models.TextChoices):
    ANY = "any", "Any"
    MALE = "male", "Male only"
    FEMALE = "female", "Female only"


class Task(models.Model):
    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=140)
    how_to_md = models.TextField(help_text="Markdown. Step-by-step for the parent-facilitated session.")
    safety_md = models.TextField(
        blank=True,
        help_text="Markdown. Risks and mitigations. Required for Navigation / Digital tasks.",
    )
    parent_note_md = models.TextField(
        blank=True,
        help_text="Markdown. Shown to parents only — why this skill matters and what benefits to expect.",
    )
    sex_filter = models.CharField(
        max_length=8,
        choices=SexFilter.choices,
        default=SexFilter.ANY,
        help_text="Which sex this task applies to. 'Any' means suitable for all.",
    )
    min_age = models.PositiveSmallIntegerField(default=7)
    max_age = models.PositiveSmallIntegerField(default=13)
    environments = models.ManyToManyField(Environment, related_name="tasks", blank=True)
    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)
    status = models.CharField(
        max_length=16,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
        db_index=True,
    )
    review_notes = models.TextField(blank=True, help_text="Internal reviewer notes.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:
        return f"{self.slug}: {self.title}"

    def clean(self) -> None:
        if self.min_age > self.max_age:
            raise ValidationError("min_age cannot exceed max_age.")


class PrerequisiteEdge(models.Model):
    """A directed edge in the DAG: completing `from_task` helps unlock `to_task`.

    `is_mandatory=True` means `to_task` stays locked (with warning) until `from_task`
    is completed or explicitly bypassed. `is_mandatory=False` is a soft hint only —
    the UI surfaces it but doesn't block.
    """

    from_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="unlocks")
    to_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="prerequisites")
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        unique_together = [("from_task", "to_task")]
        ordering = ["to_task", "from_task"]

    def __str__(self) -> str:
        arrow = "==>" if self.is_mandatory else "-->"
        return f"{self.from_task.slug} {arrow} {self.to_task.slug}"

    def clean(self) -> None:
        if self.from_task_id == self.to_task_id:
            raise ValidationError("A task cannot be a prerequisite of itself.")
        if self._would_create_cycle():
            raise ValidationError(
                f"Adding {self.from_task.slug} -> {self.to_task.slug} would create a cycle."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def _would_create_cycle(self) -> bool:
        """DFS from `to_task` over existing edges; if we reach `from_task`, this new
        edge would close a cycle."""
        if self.from_task_id is None or self.to_task_id is None:
            return False
        target = self.from_task_id
        stack = [self.to_task_id]
        seen: set[int] = set()
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node in seen:
                continue
            seen.add(node)
            downstream = PrerequisiteEdge.objects.filter(from_task_id=node).values_list(
                "to_task_id", flat=True
            )
            stack.extend(downstream)
        return False


class TaskCompletionEvent(models.Model):
    """Anonymous telemetry. Intentionally carries no child identifiers."""

    class AgeBand(models.TextChoices):
        AGE_7_8 = "7_8", "7–8"
        AGE_9_10 = "9_10", "9–10"
        AGE_11 = "11", "11"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completion_events")
    age_band = models.CharField(max_length=8, choices=AgeBand.choices)
    environment = models.CharField(max_length=16, choices=Environment.Kind.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task", "age_band", "environment"]),
        ]

    def __str__(self) -> str:
        return f"{self.task.slug} · {self.age_band} · {self.environment}"
