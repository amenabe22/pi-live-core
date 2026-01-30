'use client';

import { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { stationsApi } from '@/lib/api/stations';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import type { Station } from '@/lib/types/api';

interface StationFormProps {
  station?: Station | null;
  onSuccess: () => void;
  onCancel: () => void;
}

export function StationForm({ station, onSuccess, onCancel }: StationFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    latitude: '',
    longitude: '',
    radius: '100',
    address: '',
  });

  useEffect(() => {
    if (station) {
      setFormData({
        name: station.name,
        latitude: station.latitude.toString(),
        longitude: station.longitude.toString(),
        radius: station.radius.toString(),
        address: station.address || '',
      });
    }
  }, [station]);

  const createMutation = useMutation({
    mutationFn: stationsApi.create,
    onSuccess: () => {
      toast.success('Station created successfully');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create station');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Parameters<typeof stationsApi.update>[1]) =>
      stationsApi.update(station!.id, data),
    onSuccess: () => {
      toast.success('Station updated successfully');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update station');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      name: formData.name,
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude),
      radius: parseFloat(formData.radius),
      address: formData.address || null,
    };

    if (station) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Name</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="latitude">Latitude</Label>
          <Input
            id="latitude"
            type="number"
            step="any"
            value={formData.latitude}
            onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="longitude">Longitude</Label>
          <Input
            id="longitude"
            type="number"
            step="any"
            value={formData.longitude}
            onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
            required
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="radius">Radius (meters)</Label>
        <Input
          id="radius"
          type="number"
          value={formData.radius}
          onChange={(e) => setFormData({ ...formData, radius: e.target.value })}
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="address">Address (optional)</Label>
        <Input
          id="address"
          value={formData.address}
          onChange={(e) => setFormData({ ...formData, address: e.target.value })}
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : station ? 'Update' : 'Create'}
        </Button>
      </div>
    </form>
  );
}
