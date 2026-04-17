import pytest
from django.core.exceptions import ValidationError

from content.models import PrerequisiteEdge, Task


def _task(slug: str) -> Task:
    return Task.objects.create(slug=slug, title=slug, how_to_md="_", min_age=7, max_age=11)


@pytest.mark.django_db
def test_self_edge_is_rejected():
    a = _task("a")
    with pytest.raises(ValidationError):
        PrerequisiteEdge(from_task=a, to_task=a).save()


@pytest.mark.django_db
def test_simple_chain_is_allowed():
    a, b, c = _task("a"), _task("b"), _task("c")
    PrerequisiteEdge(from_task=a, to_task=b).save()
    PrerequisiteEdge(from_task=b, to_task=c).save()
    assert PrerequisiteEdge.objects.count() == 2


@pytest.mark.django_db
def test_cycle_is_rejected():
    a, b, c = _task("a"), _task("b"), _task("c")
    PrerequisiteEdge(from_task=a, to_task=b).save()
    PrerequisiteEdge(from_task=b, to_task=c).save()
    # Closing the triangle c -> a would form a cycle.
    with pytest.raises(ValidationError):
        PrerequisiteEdge(from_task=c, to_task=a).save()


@pytest.mark.django_db
def test_duplicate_edge_is_rejected():
    a, b = _task("a"), _task("b")
    PrerequisiteEdge(from_task=a, to_task=b).save()
    with pytest.raises(ValidationError):
        PrerequisiteEdge(from_task=a, to_task=b).save()


@pytest.mark.django_db
def test_age_range_must_be_ordered():
    t = Task(slug="bad", title="bad", how_to_md="_", min_age=11, max_age=7)
    with pytest.raises(ValidationError):
        t.full_clean()
