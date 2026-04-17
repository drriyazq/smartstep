from django.contrib import admin
from django.urls import path
from django.shortcuts import render

from .models import Environment, PrerequisiteEdge, Tag, Task, TaskCompletionEvent


class PrerequisiteInlineIncoming(admin.TabularInline):
    model = PrerequisiteEdge
    fk_name = "to_task"
    extra = 0
    verbose_name = "Required prerequisite"
    verbose_name_plural = "Required prerequisites (this task needs…)"
    autocomplete_fields = ["from_task"]


class PrerequisiteInlineOutgoing(admin.TabularInline):
    model = PrerequisiteEdge
    fk_name = "from_task"
    extra = 0
    verbose_name = "Unlocks downstream"
    verbose_name_plural = "Unlocks downstream (this task enables…)"
    autocomplete_fields = ["to_task"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "min_age", "max_age", "is_published")
    list_filter = ("is_published", "tags__category", "environments")
    search_fields = ("slug", "title", "how_to_md")
    filter_horizontal = ("environments", "tags")
    inlines = [PrerequisiteInlineIncoming, PrerequisiteInlineOutgoing]
    actions = ["unpublish_tasks", "publish_tasks"]

    @admin.action(description="Unpublish selected tasks")
    def unpublish_tasks(self, request, queryset):
        queryset.update(is_published=False)

    @admin.action(description="Publish selected tasks")
    def publish_tasks(self, request, queryset):
        queryset.update(is_published=True)

    def get_urls(self):
        urls = super().get_urls()
        return [
            path(
                "graph/",
                self.admin_site.admin_view(self.graph_view),
                name="content_task_graph",
            ),
        ] + urls

    def graph_view(self, request):
        """Read-only DAG view. Renders a Mermaid graph of published tasks, optionally
        filtered by tag category."""
        category = request.GET.get("category") or ""
        tasks = Task.objects.filter(is_published=True).prefetch_related("tags")
        if category:
            tasks = tasks.filter(tags__category=category).distinct()
        task_ids = set(tasks.values_list("id", flat=True))
        edges = PrerequisiteEdge.objects.filter(
            from_task_id__in=task_ids, to_task_id__in=task_ids
        )
        mermaid_lines = ["graph LR"]
        for t in tasks:
            mermaid_lines.append(f'    {t.slug}["{t.title}"]')
        for e in edges:
            arrow = "-->" if e.is_mandatory else "-.->"
            mermaid_lines.append(f"    {e.from_task.slug} {arrow} {e.to_task.slug}")
        return render(
            request,
            "admin/content/task_graph.html",
            {
                **self.admin_site.each_context(request),
                "title": "Task DAG",
                "mermaid": "\n".join(mermaid_lines),
                "categories": Tag.Category.choices,
                "selected_category": category,
            },
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ("kind",)


@admin.register(PrerequisiteEdge)
class PrerequisiteEdgeAdmin(admin.ModelAdmin):
    list_display = ("from_task", "to_task", "is_mandatory")
    list_filter = ("is_mandatory",)
    autocomplete_fields = ("from_task", "to_task")


@admin.register(TaskCompletionEvent)
class TaskCompletionEventAdmin(admin.ModelAdmin):
    list_display = ("task", "age_band", "environment", "created_at")
    list_filter = ("age_band", "environment")
    search_fields = ("task__slug",)
    readonly_fields = ("task", "age_band", "environment", "created_at")

    def has_add_permission(self, request):
        return False
