from rest_framework import serializers

from content.models import Environment, PrerequisiteEdge, Tag, Task, TaskCompletionEvent
from notifications.models import ScheduledNotification
from rewards.models import RewardItem


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "category")


class PrerequisiteOnTaskSerializer(serializers.ModelSerializer):
    task_slug = serializers.SlugRelatedField(
        source="from_task", slug_field="slug", read_only=True
    )

    class Meta:
        model = PrerequisiteEdge
        fields = ("task_slug", "is_mandatory")


class TaskSerializer(serializers.ModelSerializer):
    environments = serializers.SlugRelatedField(slug_field="kind", many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    prerequisites = PrerequisiteOnTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "slug",
            "title",
            "how_to_md",
            "safety_md",
            "min_age",
            "max_age",
            "environments",
            "tags",
            "prerequisites",
        )


class RewardItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="kind", read_only=True)

    class Meta:
        model = RewardItem
        fields = ("id", "title", "category", "min_age", "max_age", "is_free", "notes")


class ScheduledNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledNotification
        fields = ("id", "title", "body", "scheduled_for", "audience_filter")


class TaskCompletionEventSerializer(serializers.Serializer):
    """Write-only. Only carries a slug + anonymous buckets — never child identifiers."""

    task_slug = serializers.SlugField()
    age_band = serializers.ChoiceField(choices=TaskCompletionEvent.AgeBand.choices)
    environment = serializers.ChoiceField(choices=Environment.Kind.choices)

    def create(self, validated_data):
        try:
            task = Task.objects.get(slug=validated_data["task_slug"])
        except Task.DoesNotExist as exc:
            raise serializers.ValidationError({"task_slug": "Unknown task slug."}) from exc
        return TaskCompletionEvent.objects.create(
            task=task,
            age_band=validated_data["age_band"],
            environment=validated_data["environment"],
        )
