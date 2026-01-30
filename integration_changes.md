# Pi-live Frontend-Backend Integration

This document describes how to run and test the integrated Pi-live frontend and backend.

## Prerequisites

- Python 3.11+ with venv (or conda)
- Node.js 18+
- PostgreSQL
- Redis

## Backend Setup

1. **Create and activate a virtual environment:**
   ```bash
   cd pi-live-core/backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Copy `.env.example` to `.env` if not already done
   - Set `DATABASE_URL` to your PostgreSQL connection string
   - Set `JWT_SECRET_KEY`, `APP_ENC_KEY`
   - Set `REDIS_URL` (e.g. `redis://localhost:6379/0`)
   - Ensure `BACKEND_CORS_ORIGINS` includes `http://localhost:3000`

4. **Run database migrations:**
   ```bash
   cd pi-live-core/backend
   alembic upgrade head
   ```
   This applies the auth schema and the public business tables (vehicles, stations, travels, etc.).

5. **Seed test users (optional):**
   ```bash
   cd pi-live-core/backend
   PYTHONPATH=src python scripts/seed_users.py
   ```
   This creates: admin@pilive.com, driver1@pilive.com, driver2@pilive.com, user1@pilive.com (see script output for passwords).

6. **Start the backend:**
   ```bash
   cd pi-live-core/backend/src
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```
   API docs: http://localhost:8000/docs

## Frontend Setup

1. **Install dependencies:**
   ```bash
   cd pi-live-core/frontend
   npm install
   ```

2. **Environment:**
   - `.env.local` is already created with:
     - `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
     - `NEXT_PUBLIC_WS_URL=ws://localhost:8000`

3. **Start the frontend:**
   ```bash
   cd pi-live-core/frontend
   npm run dev
   ```
   App: http://localhost:3000

## Testing the Flow

1. **Register:** Go to http://localhost:3000/register and create an account (email + password). Optionally choose role: user, driver, or admin.

2. **Login:** Use the same credentials at http://localhost:3000/login.

3. **Dashboard:** After login you should see the dashboard with stats (they will be 0 until you add data).

4. **Create data (as admin):**
   - **Vehicles:** Dashboard → Vehicles → Add vehicle (plate number, model, status, optional driver).
   - **Stations:** Dashboard → Stations → Add station (name, lat/lng, radius, address).
   - **Travels:** Dashboard → Travels → Create travel (vehicle, driver, origin/destination stations).

5. **Travel workflow:** Start a travel, then complete or cancel it from the Travels page.

6. **Live tracking:** Dashboard → Tracking → Select a vehicle. Real-time updates appear when a driver pushes location via WebSocket (`/ws/driver/{vehicle_id}`) or when location is published to Redis.

7. **History & Reviews:** Use History and Reviews pages to view travel history and driver ratings.

## API Summary

- **Auth (simple):** `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- **Vehicles:** CRUD at `/api/v1/vehicles`
- **Stations:** CRUD at `/api/v1/stations`, plus `GET /api/v1/stations/check/{vehicle_id}/at-station`
- **Travels:** CRUD at `/api/v1/travels`, plus `POST .../start`, `.../complete`, `.../cancel`
- **Tracking:** `GET /api/v1/tracking/vehicle/{id}/current`, `.../history`, `.../route`, `POST /api/v1/tracking`
- **History:** `GET /api/v1/history/travels`, `.../travels/{id}`, `.../vehicle/{id}`, `.../driver/{id}`
- **Reviews:** CRUD at `/api/v1/reviews`, plus `GET /api/v1/reviews/driver/{id}/stats`
- **WebSocket:** `WS /ws/track/{vehicle_id}?token=JWT` (subscribe to location), `WS /ws/driver/{vehicle_id}?token=JWT` (driver push location)

## Troubleshooting

- **CORS errors:** Ensure `BACKEND_CORS_ORIGINS` in backend `.env` includes your frontend origin (e.g. `http://localhost:3000`).
- **401 on /auth/me:** Token may be expired; log in again.
- **Migration errors:** Ensure PostgreSQL is running and `DATABASE_URL` is correct. If the auth schema already exists from a previous migration, only run the second migration (business tables) if needed.
- **WebSocket not updating:** Ensure Redis is running and the driver WebSocket or another process is publishing to `vehicle:{id}:updates`.
