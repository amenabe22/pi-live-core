'use client';

import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { vehiclesApi } from '@/lib/api/vehicles';
import { authApi } from '@/lib/api/auth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import type { Vehicle, VehicleStatus } from '@/lib/types/api';

interface VehicleFormProps {
  vehicle?: Vehicle | null;
  onSuccess: () => void;
  onCancel: () => void;
}

export function VehicleForm({ vehicle, onSuccess, onCancel }: VehicleFormProps) {
  const [formData, setFormData] = useState({
    plate_number: '',
    model: '',
    status: 'active' as VehicleStatus,
    driver_id: null as number | null,
  });

  const queryClient = useQueryClient();

  const { data: users } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      // For now, we'll need to fetch users differently
      // This is a placeholder - you'd need a users API endpoint
      return [];
    },
  });

  useEffect(() => {
    if (vehicle) {
      setFormData({
        plate_number: vehicle.plate_number,
        model: vehicle.model,
        status: vehicle.status,
        driver_id: vehicle.driver_id,
      });
    }
  }, [vehicle]);

  const createMutation = useMutation({
    mutationFn: vehiclesApi.create,
    onSuccess: () => {
      toast.success('Vehicle created successfully');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create vehicle');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Parameters<typeof vehiclesApi.update>[1]) =>
      vehiclesApi.update(vehicle!.id, data),
    onSuccess: () => {
      toast.success('Vehicle updated successfully');
      onSuccess();
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update vehicle');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (vehicle) {
      updateMutation.mutate(formData);
    } else {
      createMutation.mutate(formData);
    }
  };

  const isLoading = createMutation.isPending || updateMutation.isPending;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="plate_number">Plate Number</Label>
        <Input
          id="plate_number"
          value={formData.plate_number}
          onChange={(e) => setFormData({ ...formData, plate_number: e.target.value })}
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="model">Model</Label>
        <Input
          id="model"
          value={formData.model}
          onChange={(e) => setFormData({ ...formData, model: e.target.value })}
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="status">Status</Label>
        <Select
          value={formData.status}
          onValueChange={(value: VehicleStatus) =>
            setFormData({ ...formData, status: value })
          }
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
            <SelectItem value="maintenance">Maintenance</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : vehicle ? 'Update' : 'Create'}
        </Button>
      </div>
    </form>
  );
}
