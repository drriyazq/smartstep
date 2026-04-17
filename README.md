# SmartStep

Parent-facilitated gamified life-skills app for kids aged 7–11. Maps "street smarts"
into a DAG of unlockable micro-tasks with prerequisite logic.

**Privacy boundary:** all child PII lives on-device (Flutter + Hive). The server
stores only the content graph and anonymous telemetry counters.

## Layout

```
backend/   Django + DRF API (content graph, rewards, admin, telemetry)
app/       Flutter Android app (onboarding, ladder, task detail)
infra/     docker-compose for local dev
```

## Local development

### Option A — docker-compose (recommended)

```bash
cd infra
docker compose up --build
```

- API: http://localhost:8000/api/v1/
- Admin: http://localhost:8000/admin/  (superuser `admin` / `admin` created by entrypoint in dev)
- `seed_demo` runs automatically on first boot

### Option B — bare-metal backend

```bash
cd backend
uv sync                            # or: pip install -e .[dev]
export DATABASE_URL=postgres://smartstep:smartstep@localhost:5432/smartstep
export DJANGO_SETTINGS_MODULE=smartstep.settings.dev
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

### Flutter app

```bash
cd app
flutter pub get
flutter run -d <android-emulator-id>
```

OTP is stubbed in dev — any phone number + OTP `000000` logs you in.

## Testing

```bash
# Backend
cd backend && pytest

# Flutter
cd app && flutter analyze && flutter test
```

## API surface (`/api/v1/`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/dev-token/` | Dev-only: returns JWT for a fixed dev user |
| GET  | `/tasks/` | Task catalog with inline prerequisites. Filters: `environment`, `min_age`, `max_age`, `tag` |
| GET  | `/rewards/` | Reward catalog. Filter: `age` |
| GET  | `/notifications/active/` | Currently-live scheduled notifications |
| POST | `/telemetry/task-completion/` | Anonymous completion event (no child identifiers) |

## Repo conventions

- **No child data on the server.** Telemetry must never include child identifiers.
- **DAG integrity is enforced at save time** (`PrerequisiteEdge.save`).
- **Task taxonomy = 5 categories**: Financial, Household, Digital, Navigation, Cognitive.
