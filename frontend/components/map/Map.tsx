'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { Vehicle, Station, LocationUpdate } from '@/lib/types/api';

// Fix for default marker icons in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface MapComponentProps {
  vehicles: Vehicle[];
  stations: Station[];
  selectedVehicleId: number | null;
  vehicleLocation: LocationUpdate | null;
}

export function MapComponent({
  vehicles,
  stations,
  selectedVehicleId,
  vehicleLocation,
}: MapComponentProps) {
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Map<number, L.Marker>>(new Map());

  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('map').setView([40.7128, -74.0060], 10);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
      }).addTo(mapRef.current);
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current.clear();

    // Add station markers
    stations.forEach((station) => {
      const marker = L.marker([station.latitude, station.longitude])
        .addTo(mapRef.current!)
        .bindPopup(`<b>${station.name}</b><br/>Radius: ${station.radius}m`);
      
      marker.setIcon(
        L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
        })
      );
    });

    // Add vehicle location if available
    if (vehicleLocation && selectedVehicleId) {
      const vehicleMarker = L.marker([vehicleLocation.latitude, vehicleLocation.longitude])
        .addTo(mapRef.current!)
        .bindPopup(`<b>Vehicle Location</b><br/>Lat: ${vehicleLocation.latitude.toFixed(4)}<br/>Lng: ${vehicleLocation.longitude.toFixed(4)}`);
      
      vehicleMarker.setIcon(
        L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
        })
      );

      markersRef.current.set(selectedVehicleId, vehicleMarker);
      mapRef.current.setView([vehicleLocation.latitude, vehicleLocation.longitude], 13);
    }
  }, [stations, vehicleLocation, selectedVehicleId]);

  return <div id="map" style={{ height: '100%', width: '100%' }} />;
}
