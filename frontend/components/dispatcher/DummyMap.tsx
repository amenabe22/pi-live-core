'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/loading-skeleton';
import { Card } from '@/components/ui/card';

// Dynamically import MapContainer and other Leaflet components with no SSR
const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false, loading: () => <MapSkeleton /> }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);
const Marker = dynamic(
  () => import('react-leaflet').then((mod) => mod.Marker),
  { ssr: false }
);
const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
);

function MapSkeleton() {
  return (
    <div className="w-full h-full min-h-[400px] flex items-center justify-center bg-muted/20">
      <div className="space-y-4 text-center">
        <Skeleton className="h-12 w-12 rounded-full mx-auto" />
        <Skeleton className="h-4 w-32 mx-auto" />
      </div>
    </div>
  );
}

// Fix for default marker icon in Leaflet
const FixLeafletIcon = () => {
  useEffect(() => {
    // We only want to run this on the client
    if (typeof window !== 'undefined') {
      import('leaflet').then((L) => {
        // @ts-ignore
        delete L.Icon.Default.prototype._getIconUrl;
        L.Icon.Default.mergeOptions({
          iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
          iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        });
      });
    }
  }, []);
  return null;
}

const DUMMY_LOCATIONS = [
  { id: 1, lat: 40.7128, lng: -74.0060, title: "Unit A-12 (Available)", type: "driver" },
  { id: 2, lat: 40.7282, lng: -73.9942, title: "Emergency Call #4001", type: "call" },
  { id: 3, lat: 40.7580, lng: -73.9855, title: "Unit B-05 (Busy)", type: "driver" },
];

export default function DummyMap() {
  return (
    <div className="h-[400px] w-full rounded-xl overflow-hidden border shadow-sm relative z-0">
      <FixLeafletIcon />
      <MapContainer
        center={[40.730610, -73.935242]}
        zoom={12}
        scrollWheelZoom={false}
        className="h-full w-full"
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {DUMMY_LOCATIONS.map((loc) => (
          <Marker key={loc.id} position={[loc.lat, loc.lng]}>
            <Popup>
              {loc.title}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
