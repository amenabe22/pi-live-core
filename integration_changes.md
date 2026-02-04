Implementation summary
Backend (Pi-live-core)
Simple auth (backend/src/auth/simple/)
POST /auth/register, POST /auth/login, GET /auth/me (email/password, JWT)
Schemas and security (bcrypt, PyJWT) aligned with Pi-hire
Business APIs
Vehicles – CRUD at /api/v1/vehicles
Stations – CRUD + GET /stations/check/{vehicle_id}/at-station (Redis location check)
Travels – CRUD + /start, /complete, /cancel
Tracking – current, history, route, POST /tracking
History – /history/travels, by vehicle, by driver
Reviews – CRUD + /reviews/driver/{id}/stats
WebSocket
WS /ws/track/{vehicle_id} – subscribe to live location (Redis pub/sub)
WS /ws/driver/{vehicle_id} – driver sends location
Redis set in lifespan and passed to the WebSocket manager
Models
Vehicle, Station, Travel, TravelHistory, Review, LiveTracking in common/models/ (UUID primary keys, public schema)
Config / deps
Redis dependency in core/dependencies.py for stations
PyJWT in requirements.txt
Migration alembic/versions/2026-01-30_add_public_business_tables.py for the new tables
Frontend
.env.local – NEXT_PUBLIC_API_URL, NEXT_PUBLIC_WS_URL
Types – IDs and FKs switched from number to string in lib/types/api.ts
API modules – vehicles, stations, travels, history, reviews, tracking use string IDs
Pages/components – handleDelete/handleStart/etc. and state (e.g. selectedVehicleId) use string IDs; TravelForm and VehicleForm submit string IDs; Map and useWebSocket use string vehicle IDs
StatsCard – unsupported props removed in app/page.tsx
