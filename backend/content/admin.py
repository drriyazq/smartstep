from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, render
from django.utils.html import format_html

from .models import Environment, PrerequisiteEdge, ReviewStatus, Tag, Task, TaskCompletionEvent


# ── Screening form ──────────────────────────────────────────────────────────────

class TaskScreenForm(forms.Form):
    slug = forms.SlugField(max_length=80)
    title = forms.CharField(max_length=140)
    status = forms.ChoiceField(choices=ReviewStatus.choices)
    min_age = forms.IntegerField(min_value=1, max_value=18, initial=7)
    max_age = forms.IntegerField(min_value=1, max_value=18, initial=11)
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by("category", "name"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    environments = forms.ModelMultipleChoiceField(
        queryset=Environment.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    how_to_md = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 8}),
        help_text="Markdown. Step-by-step for the parent-facilitated session.",
    )
    safety_md = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
        help_text="Markdown. Risks and mitigations. Required for Navigation / Digital tasks.",
    )
    parent_note_md = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5}),
        required=False,
        help_text="Markdown. Shown to parents — why this skill matters and what benefits to expect.",
    )
    review_notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        help_text="Internal reviewer notes (not shown in app).",
    )

    def clean(self):
        cleaned = super().clean()
        lo = cleaned.get("min_age")
        hi = cleaned.get("max_age")
        if lo and hi and lo > hi:
            raise ValidationError("min_age cannot exceed max_age.")
        return cleaned


STATUS_COLORS = {
    ReviewStatus.DRAFT: "#9ca3af",
    ReviewStatus.PENDING: "#f59e0b",
    ReviewStatus.APPROVED: "#10b981",
    ReviewStatus.REJECTED: "#ef4444",
}


def _status_badge(status_value: str) -> str:
    label = dict(ReviewStatus.choices).get(status_value, status_value)
    color = STATUS_COLORS.get(status_value, "#6b7280")
    return format_html(
        '<span style="background:{};color:white;padding:2px 8px;'
        'border-radius:10px;font-size:11px;font-weight:600;">{}</span>',
        color,
        label,
    )


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
    list_display = ("slug", "title", "status_badge", "min_age", "max_age", "updated_at")
    list_filter = ("status", "tags__category", "environments")
    search_fields = ("slug", "title", "how_to_md")
    filter_horizontal = ("environments", "tags")
    inlines = [PrerequisiteInlineIncoming, PrerequisiteInlineOutgoing]
    readonly_fields = ("created_at", "updated_at")
    actions = [
        "approve_tasks",
        "reject_tasks",
        "submit_for_review",
        "send_back_to_draft",
    ]
    fieldsets = (
        (None, {"fields": ("slug", "title", "status", "review_notes")}),
        ("Content", {"fields": ("how_to_md", "safety_md", "parent_note_md")}),
        ("Audience", {"fields": ("min_age", "max_age", "environments", "tags")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    change_list_template = "admin/content/task_changelist.html"

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        return _status_badge(obj.status)

    @admin.action(description="✓ Approve (publish to app)")
    def approve_tasks(self, request, queryset):
        count = queryset.update(status=ReviewStatus.APPROVED)
        self.message_user(request, f"Approved {count} task(s).", messages.SUCCESS)

    @admin.action(description="✗ Reject")
    def reject_tasks(self, request, queryset):
        count = queryset.update(status=ReviewStatus.REJECTED)
        self.message_user(request, f"Rejected {count} task(s).", messages.WARNING)

    @admin.action(description="→ Submit for review")
    def submit_for_review(self, request, queryset):
        count = queryset.update(status=ReviewStatus.PENDING)
        self.message_user(request, f"Moved {count} task(s) to pending review.", messages.INFO)

    @admin.action(description="← Send back to draft")
    def send_back_to_draft(self, request, queryset):
        count = queryset.update(status=ReviewStatus.DRAFT)
        self.message_user(request, f"Moved {count} task(s) back to draft.", messages.INFO)

    def get_urls(self):
        urls = super().get_urls()
        return [
            path(
                "graph/",
                self.admin_site.admin_view(self.graph_view),
                name="content_task_graph",
            ),
            path(
                "screen/",
                self.admin_site.admin_view(self.screen_list_view),
                name="content_task_screen",
            ),
            path(
                "screen/add/",
                self.admin_site.admin_view(self.screen_form_view),
                name="content_task_screen_add",
            ),
            path(
                "screen/<int:pk>/",
                self.admin_site.admin_view(self.screen_form_view),
                name="content_task_screen_edit",
            ),
        ] + urls

    def graph_view(self, request):
        """Read-only DAG view. Renders a Mermaid graph of approved tasks, optionally
        filtered by tag category."""
        category = request.GET.get("category") or ""
        tasks = Task.objects.filter(status=ReviewStatus.APPROVED).prefetch_related("tags")
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


    # ── Screening list view ──────────────────────────────────────────────────

    def screen_list_view(self, request):
        status_filter = request.GET.get("status", "pending")
        category_filter = request.GET.get("category", "")
        q = request.GET.get("q", "").strip()

        # Quick-action POST (approve / reject / draft a single task)
        if request.method == "POST":
            task_id = request.POST.get("task_id")
            action = request.POST.get("action")
            if task_id and action in ("approve", "reject", "draft", "pending", "delete"):
                task = get_object_or_404(Task, pk=task_id)
                if action == "delete":
                    title = task.title
                    task.delete()
                    messages.success(request, f'Deleted task "{title}".')
                else:
                    status_map = {
                        "approve": ReviewStatus.APPROVED,
                        "reject": ReviewStatus.REJECTED,
                        "draft": ReviewStatus.DRAFT,
                        "pending": ReviewStatus.PENDING,
                    }
                    task.status = status_map[action]
                    task.save(update_fields=["status", "updated_at"])
                    messages.success(request, f'"{task.title}" set to {task.get_status_display()}.')
            return HttpResponseRedirect(request.get_full_path())

        qs = Task.objects.prefetch_related("tags").order_by("slug")
        if status_filter and status_filter != "all":
            qs = qs.filter(status=status_filter)
        if category_filter:
            qs = qs.filter(tags__category=category_filter).distinct()
        if q:
            qs = qs.filter(Q(slug__icontains=q) | Q(title__icontains=q))

        counts = {
            "all": Task.objects.count(),
            **{s: Task.objects.filter(status=s).count() for s, _ in ReviewStatus.choices},
        }

        return render(
            request,
            "admin/content/task_screen.html",
            {
                **self.admin_site.each_context(request),
                "title": "Task Screening",
                "tasks": qs,
                "counts": counts,
                "status_filter": status_filter,
                "category_filter": category_filter,
                "q": q,
                "categories": Tag.Category.choices,
                "review_statuses": ReviewStatus.choices,
                "status_colors": STATUS_COLORS,
            },
        )

    # ── Screening add / edit form view ───────────────────────────────────────

    def screen_form_view(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk) if pk else None
        is_new = task is None

        if request.method == "POST":
            form = TaskScreenForm(request.POST)
            if form.is_valid():
                d = form.cleaned_data
                override_status = request.POST.get("save_action")
                final_status = override_status if override_status in dict(ReviewStatus.choices) else d["status"]

                with transaction.atomic():
                    if is_new:
                        task = Task(slug=d["slug"])
                    elif d["slug"] != task.slug:
                        task.slug = d["slug"]

                    task.title = d["title"]
                    task.how_to_md = d["how_to_md"]
                    task.safety_md = d["safety_md"]
                    task.parent_note_md = d["parent_note_md"]
                    task.review_notes = d["review_notes"]
                    task.min_age = d["min_age"]
                    task.max_age = d["max_age"]
                    task.status = final_status
                    task.save()
                    task.tags.set(d["tags"])
                    task.environments.set(d["environments"])

                verb = "Created" if is_new else "Saved"
                messages.success(request, f'{verb} "{task.title}" ({task.get_status_display()}).')
                return HttpResponseRedirect(reverse("admin:content_task_screen"))
        else:
            initial = {}
            if task:
                initial = {
                    "slug": task.slug,
                    "title": task.title,
                    "status": task.status,
                    "min_age": task.min_age,
                    "max_age": task.max_age,
                    "tags": task.tags.all(),
                    "environments": task.environments.all(),
                    "how_to_md": task.how_to_md,
                    "safety_md": task.safety_md,
                    "parent_note_md": task.parent_note_md,
                    "review_notes": task.review_notes,
                }
            form = TaskScreenForm(initial=initial)

        return render(
            request,
            "admin/content/task_screen_form.html",
            {
                **self.admin_site.each_context(request),
                "title": "Add task" if is_new else f"Edit: {task.title}",
                "form": form,
                "task": task,
                "is_new": is_new,
                "review_statuses": ReviewStatus.choices,
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
