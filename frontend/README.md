# PI-Line Admin Dashboard - Frontend

Modern Next.js 14 admin dashboard for the PI-Line vehicle tracking system.

## Features

- **Authentication**: JWT-based login and registration
- **Fleet Management**: Complete CRUD for vehicles
- **Station Management**: Manage pickup/dropoff locations
- **Travel Management**: Create, track, and manage trips
- **Real-time Tracking**: Live vehicle positions via WebSocket
- **Historical Data**: View travel history and analytics
- **Review System**: Manage user reviews and ratings
- **Analytics Dashboard**: Charts and statistics

## Tech Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **React Query** for data fetching
- **Zustand** for state management
- **Leaflet** for maps
- **Recharts** for data visualization

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── (auth)/          # Authentication pages
│   ├── (dashboard)/     # Protected dashboard pages
│   └── layout.tsx       # Root layout
├── components/
│   ├── dashboard/        # Dashboard layout components
│   ├── vehicles/         # Vehicle management components
│   ├── stations/         # Station management components
│   ├── travels/          # Travel management components
│   └── map/              # Map components
├── lib/
│   ├── api/              # API client functions
│   ├── hooks/            # Custom React hooks
│   ├── store/            # Zustand stores
│   ├── types/            # TypeScript types
│   └── utils/            # Utility functions
└── public/               # Static assets
```

## Pages

- `/login` - User login
- `/register` - User registration
- `/` - Dashboard home
- `/vehicles` - Vehicle management
- `/stations` - Station management
- `/travels` - Travel management
- `/tracking` - Live vehicle tracking
- `/history` - Travel history
- `/reviews` - Review management
- `/analytics` - Analytics and reports

## Authentication

The app uses JWT tokens stored in localStorage. Protected routes automatically redirect to login if not authenticated.

## API Integration

All API calls are made through the `lib/api` modules which use Axios with automatic token injection.

## WebSocket

Real-time vehicle tracking uses WebSocket connections. The `useVehicleTracking` hook manages WebSocket connections automatically.

## License

MIT
