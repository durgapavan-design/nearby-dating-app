# Nearby — Dating App MVP

A personal/learning-project MVP: signup/login, profile + interests, nearby
discovery, like/pass matching, "who liked you", and chat.

## Stack

- **Frontend**: React + TypeScript + Vite, plain CSS (no framework)
- **Backend**: FastAPI + SQLAlchemy + Alembic, Python
- **DB**: PostgreSQL
- **Auth**: Phone number + OTP. No real SMS provider is wired up — in dev
  mode the backend returns the OTP code directly in the `/auth/otp/request`
  response (`debug_code`), and the frontend pre-fills the verify screen with
  it. Swap `services/otp_service.py`'s `generate_and_store_otp` for a real
  provider (e.g. Twilio) later without touching the rest of the auth flow.
- **Chat**: WebSocket per open conversation (`/ws/chat/{match_id}`) plus a
  REST fallback (`GET`/`POST /matches/{id}/messages`) for history and for
  sending when no socket is open — not a global always-on socket, not
  continuous polling.
- **Nearby**: MVP uses a manually-picked city (from a fixed list) rather than
  live GPS. `location_source` on the user model is already `manual`/`gps` so
  live geolocation can be added later without a schema change.

## Running locally

Everything runs via Docker Compose — no local Python/Node install needed.

```bash
docker compose up -d db
# wait a few seconds for Postgres to become healthy, then:
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.seed.seed_data   # ~150 fake profiles, run once
docker compose up -d backend frontend
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000 (docs at `/docs`)
- Postgres: localhost:5432 (user/pass/db: `dating`/`dating`/`dating`)

To stop: `docker compose down` (add `-v` to also wipe the DB and uploaded
photos).

## Project layout

```
backend/
  app/
    core/       config, JWT
    db/         SQLAlchemy session/base
    models/     ORM models (users, interests, photos, swipes, matches, messages, otp)
    schemas/    Pydantic request/response shapes
    api/routers/ auth, profile, discovery, matches, chat
    services/   OTP generation/verification, matching/ranking, websocket connection manager
    seed/       fixed cities + interests lists, seed script
  alembic/      migrations
frontend/
  src/
    api/        typed fetch client
    context/    auth context (JWT in localStorage)
    pages/      Login, VerifyOtp, ProfileSetup, Discover, Matches, Chat, Profile
    components/ NavBar, SwipeCard, PhotoUploader, InterestPicker
```

## Notes on the matching/ranking logic

`app/services/matching.py` scores discovery candidates: +10 for same city,
+2 per shared interest. Gender compatibility (`show_me` vs `gender`) is
filtered before scoring. This is intentionally simple — a good place to
extend later (distance-based scoring once live GPS lands, activity recency,
etc.) without changing the API surface.

## What's not done (by design, for MVP scope)

- No real SMS provider (mocked OTP)
- No push notifications
- No payments/premium gating ("who liked you" is open to everyone)
- No production deployment config (this is local-dev only for now)
