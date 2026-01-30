'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { vehiclesApi } from '@/lib/api/vehicles';
import { stationsApi } from '@/lib/api/stations';
import { useVehicleTracking } from '@/lib/hooks/useWebSocket';
import { MapComponent } from '@/components/map/Map';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Activity, MapPin, Truck, Radio, Gauge } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

export default function TrackingPage() {
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const { location, isConnected } = useVehicleTracking(selectedVehicleId);

  const { data: vehicles } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesApi.getAll(),
  });

  const { data: stations } = useQuery({
    queryKey: ['stations'],
    queryFn: () => stationsApi.getAll(),
  });

  const selectedVehicle = vehicles?.find((v) => v.id === selectedVehicleId);

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Live Tracking
          </h1>
          <p className="text-muted-foreground mt-2">Monitor vehicles in real-time</p>
        </div>
      </motion.div>

      <div className="grid gap-4 md:grid-cols-3">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
              <CardTitle className="flex items-center gap-2">
                <Truck className="h-5 w-5 text-primary" />
                Select Vehicle
              </CardTitle>
              <CardDescription>Choose a vehicle to track</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <Select
                value={selectedVehicleId || ''}
                onValueChange={(value) => setSelectedVehicleId(value || null)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select vehicle" />
                </SelectTrigger>
                <SelectContent>
                  {vehicles?.map((vehicle) => (
                    <SelectItem key={vehicle.id} value={vehicle.id.toString()}>
                      {vehicle.plate_number} - {vehicle.model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>
        </motion.div>

        <AnimatePresence>
          {selectedVehicle && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
                  <CardTitle>Vehicle Info</CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div>
                      <span className="text-sm text-muted-foreground">Plate Number</span>
                      <p className="font-semibold text-lg">{selectedVehicle.plate_number}</p>
                    </div>
                    <div>
                      <span className="text-sm text-muted-foreground">Model</span>
                      <p className="font-medium">{selectedVehicle.model}</p>
                    </div>
                    <div>
                      <span className="text-sm text-muted-foreground">Status</span>
                      <div className="mt-1">
                        <Badge className={cn(
                          selectedVehicle.status === 'active' && 'bg-green-500 hover:bg-green-600',
                          selectedVehicle.status === 'inactive' && 'bg-gray-500',
                          selectedVehicle.status === 'maintenance' && 'bg-yellow-500 hover:bg-yellow-600'
                        )}>
                          {selectedVehicle.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {location && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
            >
              <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
                  <CardTitle className="flex items-center gap-2">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ repeat: Infinity, duration: 2 }}
                    >
                      <Activity className="h-5 w-5 text-primary" />
                    </motion.div>
                    Current Location
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div>
                      <span className="text-sm text-muted-foreground flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        Latitude
                      </span>
                      <p className="font-mono font-medium">{location.latitude.toFixed(6)}</p>
                    </div>
                    <div>
                      <span className="text-sm text-muted-foreground flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        Longitude
                      </span>
                      <p className="font-mono font-medium">{location.longitude.toFixed(6)}</p>
                    </div>
                    {location.speed && (
                      <div>
                        <span className="text-sm text-muted-foreground flex items-center gap-1">
                          <Gauge className="h-3 w-3" />
                          Speed
                        </span>
                        <p className="font-semibold text-lg">{location.speed.toFixed(1)} km/h</p>
                      </div>
                    )}
                    <div className="pt-2">
                      <div className="flex items-center gap-2">
                        <motion.div
                          animate={isConnected ? { scale: [1, 1.2, 1] } : {}}
                          transition={{ repeat: isConnected ? Infinity : 0, duration: 1.5 }}
                        >
                          <Radio className={cn(
                            'h-4 w-4',
                            isConnected ? 'text-green-500' : 'text-gray-400'
                          )} />
                        </motion.div>
                        <Badge variant={isConnected ? 'default' : 'secondary'}>
                          {isConnected ? 'Connected' : 'Disconnected'}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="border-0 shadow-lg overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-primary" />
              Map View
            </CardTitle>
            <CardDescription>Real-time vehicle positions</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="h-[600px] w-full relative">
              <MapComponent
                vehicles={vehicles || []}
                stations={stations || []}
                selectedVehicleId={selectedVehicleId}
                vehicleLocation={location}
              />
              {!selectedVehicleId && (
                <div className="absolute inset-0 flex items-center justify-center bg-muted/50 backdrop-blur-sm z-10">
                  <div className="text-center p-6 bg-background rounded-lg shadow-lg border">
                    <MapPin className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-lg font-semibold">Select a vehicle to start tracking</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Choose a vehicle from the dropdown above
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
