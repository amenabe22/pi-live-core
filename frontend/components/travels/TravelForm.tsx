'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { travelsApi } from '@/lib/api/travels';
import { vehiclesApi } from '@/lib/api/vehicles';
import { stationsApi } from '@/lib/api/stations';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';

interface TravelFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export function TravelForm({ onSuccess, onCancel }: TravelFormProps) {
  const [formData, setFormData] = useState({
    vehicle_id: '',
    driver_id: '',
    origin_station_id: '',
    destination_station_id: '',
  });

  const { data: vehicles } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesApi.getAll(),
  });

  const { data: stations } = useQuery({
    queryKey: ['stations'],
    queryFn: () => stationsApi.getAll(),
  });

  const createMutation = useMutation({
    mutationFn: travelsApi.create,
    onSuccess: () => {
      toast.success('Travel created successfully');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create travel');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      vehicle_id: parseInt(formData.vehicle_id),
      driver_id: parseInt(formData.driver_id),
      origin_station_id: parseInt(formData.origin_station_id),
      destination_station_id: parseInt(formData.destination_station_id),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="vehicle_id">Vehicle</Label>
        <Select
          value={formData.vehicle_id}
          onValueChange={(value) => setFormData({ ...formData, vehicle_id: value })}
        >
          <SelectTrigger>
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
      </div>
      <div className="space-y-2">
        <Label htmlFor="driver_id">Driver</Label>
        <Select
          value={formData.driver_id}
          onValueChange={(value) => setFormData({ ...formData, driver_id: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select driver" />
          </SelectTrigger>
          <SelectContent>
            {/* Drivers would come from users API - placeholder for now */}
            <SelectItem value="1">Driver 1</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label htmlFor="origin_station_id">Origin Station</Label>
        <Select
          value={formData.origin_station_id}
          onValueChange={(value) => setFormData({ ...formData, origin_station_id: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select origin" />
          </SelectTrigger>
          <SelectContent>
            {stations?.map((station) => (
              <SelectItem key={station.id} value={station.id.toString()}>
                {station.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label htmlFor="destination_station_id">Destination Station</Label>
        <Select
          value={formData.destination_station_id}
          onValueChange={(value) => setFormData({ ...formData, destination_station_id: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select destination" />
          </SelectTrigger>
          <SelectContent>
            {stations?.map((station) => (
              <SelectItem key={station.id} value={station.id.toString()}>
                {station.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? 'Creating...' : 'Create'}
        </Button>
      </div>
    </form>
  );
}
