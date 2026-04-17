import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from content.models import Environment, PrerequisiteEdge, Tag, Task


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def seed_tasks(db):
    urban = Environment.objects.create(kind=Environment.Kind.URBAN)
    rural = Environment.objects.create(kind=Environment.Kind.RURAL)
    tag = Tag.objects.create(name="atm-use", category=Tag.Category.FINANCIAL)

    boil = Task.objects.create(
        slug="boil-water", title="Boil water", how_to_md="_", min_age=7, max_age=11, is_published=True
    )
    boil.environments.add(urban, rural)
    boil.tags.add(tag)

    pasta = Task.objects.create(
        slug="cook-pasta", title="Cook pasta", how_to_md="_", min_age=9, max_age=11, is_published=True
    )
    pasta.environments.add(urban)
    pasta.tags.add(tag)

    PrerequisiteEdge(from_task=boil, to_task=pasta, is_mandatory=True).save()
    return boil, pasta


def test_task_list_returns_prereqs_inline(client, seed_tasks):
    resp = client.get(reverse("task-list"))
    assert resp.status_code == 200
    data = {t["slug"]: t for t in resp.json()}
    assert "cook-pasta" in data
    prereqs = data["cook-pasta"]["prerequisites"]
    assert prereqs == [{"task_slug": "boil-water", "is_mandatory": True}]


def test_task_list_filters_by_environment(client, seed_tasks):
    resp = client.get(reverse("task-list"), {"environment": "rural"})
    slugs = [t["slug"] for t in resp.json()]
    assert slugs == ["boil-water"]


def test_task_list_filters_by_age(client, seed_tasks):
    resp = client.get(reverse("task-list"), {"min_age": 9, "max_age": 10})
    slugs = sorted(t["slug"] for t in resp.json())
    assert slugs == ["boil-water", "cook-pasta"]

    resp = client.get(reverse("task-list"), {"min_age": 7, "max_age": 8})
    slugs = [t["slug"] for t in resp.json()]
    assert slugs == ["boil-water"]


def test_telemetry_rejects_without_auth(client, seed_tasks):
    resp = client.post(
        reverse("task-completion"),
        {"task_slug": "cook-pasta", "age_band": "9_10", "environment": "urban"},
        format="json",
    )
    assert resp.status_code == 401


def test_telemetry_accepts_with_jwt(client, seed_tasks, settings):
    settings.DEBUG = True
    token = client.post(reverse("auth-dev-token")).json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.post(
        reverse("task-completion"),
        {"task_slug": "cook-pasta", "age_band": "9_10", "environment": "urban"},
        format="json",
    )
    assert resp.status_code == 201
