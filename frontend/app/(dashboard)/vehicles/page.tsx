'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vehiclesApi } from '@/lib/api/vehicles';
import { authApi } from '@/lib/api/auth';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { VehicleForm } from '@/components/vehicles/VehicleForm';
import { Plus, Edit, Trash2, Grid3x3, List, Truck } from 'lucide-react';
import { toast } from 'sonner';
import { useAuthStore } from '@/lib/store/authStore';
import { formatDate } from '@/lib/utils/formatters';
import type { Vehicle } from '@/lib/types/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { SkeletonTable, SkeletonCard } from '@/components/ui/loading-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { cn } from '@/lib/utils';

type ViewMode = 'grid' | 'list';

export default function VehiclesPage() {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const queryClient = useQueryClient();
  const isAdmin = useAuthStore((state) => {
    const { user } = state;
    return user?.role === 'admin';
  });

  const { data: vehicles, isLoading } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesApi.getAll(),
  });

  const { data: users } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      // We'll need to add a users API endpoint, for now return empty
      return [];
    },
    enabled: false,
  });

  const deleteMutation = useMutation({
    mutationFn: vehiclesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vehicles'] });
      toast.success('Vehicle deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete vehicle');
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500 hover:bg-green-600';
      case 'inactive':
        return 'bg-gray-500 hover:bg-gray-600';
      case 'maintenance':
        return 'bg-yellow-500 hover:bg-yellow-600';
      default:
        return 'bg-gray-500';
    }
  };

  const handleEdit = (vehicle: Vehicle) => {
    setEditingVehicle(vehicle);
    setIsFormOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this vehicle?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleFormSuccess = () => {
    setIsFormOpen(false);
    setEditingVehicle(null);
    queryClient.invalidateQueries({ queryKey: ['vehicles'] });
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Vehicles
          </h1>
          <p className="text-muted-foreground mt-2">Manage your fleet</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 rounded-lg border bg-background p-1">
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className="h-8"
            >
              <List className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              className="h-8"
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
          </div>
          {isAdmin && (
            <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
              <DialogTrigger asChild>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button onClick={() => setEditingVehicle(null)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Vehicle
                  </Button>
                </motion.div>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>{editingVehicle ? 'Edit Vehicle' : 'Add Vehicle'}</DialogTitle>
                </DialogHeader>
                <VehicleForm
                  vehicle={editingVehicle}
                  onSuccess={handleFormSuccess}
                  onCancel={() => {
                    setIsFormOpen(false);
                    setEditingVehicle(null);
                  }}
                />
              </DialogContent>
            </Dialog>
          )}
        </div>
      </motion.div>

      {isLoading ? (
        <div className={cn('grid gap-4', viewMode === 'grid' ? 'md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1')}>
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : vehicles && vehicles.length > 0 ? (
        <AnimatePresence mode="wait">
          {viewMode === 'list' ? (
            <motion.div
              key="list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="rounded-lg border bg-card shadow-md overflow-hidden"
            >
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Plate Number</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Driver</TableHead>
                    <TableHead>Created</TableHead>
                    {isAdmin && <TableHead className="text-right">Actions</TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {vehicles.map((vehicle, index) => (
                    <motion.tr
                      key={vehicle.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-b hover:bg-muted/50 transition-colors"
                    >
                      <TableCell className="font-medium">{vehicle.plate_number}</TableCell>
                      <TableCell>{vehicle.model}</TableCell>
                      <TableCell>
                        <Badge className={cn('transition-all', getStatusColor(vehicle.status))}>
                          {vehicle.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{vehicle.driver?.email || 'Unassigned'}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {formatDate(vehicle.created_at)}
                      </TableCell>
                      {isAdmin && (
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleEdit(vehicle)}
                              className="hover:bg-primary/10"
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(vehicle.id)}
                              className="hover:bg-destructive/10 hover:text-destructive"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      )}
                    </motion.tr>
                  ))}
                </TableBody>
              </Table>
            </motion.div>
          ) : (
            <motion.div
              key="grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
            >
              {vehicles.map((vehicle, index) => (
                <motion.div
                  key={vehicle.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ y: -4 }}
                >
                  <Card className="border-2 hover:border-primary/50 transition-all shadow-md hover:shadow-lg">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="rounded-lg bg-gradient-to-br from-primary to-primary/60 p-3">
                          <Truck className="h-6 w-6 text-white" />
                        </div>
                        <Badge className={cn('transition-all', getStatusColor(vehicle.status))}>
                          {vehicle.status}
                        </Badge>
                      </div>
                      <h3 className="text-xl font-bold mb-1">{vehicle.plate_number}</h3>
                      <p className="text-muted-foreground mb-4">{vehicle.model}</p>
                      <div className="space-y-2 text-sm mb-4">
                        <div>
                          <span className="text-muted-foreground">Driver: </span>
                          <span className="font-medium">{vehicle.driver?.email || 'Unassigned'}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Created: </span>
                          <span className="font-medium">{formatDate(vehicle.created_at)}</span>
                        </div>
                      </div>
                      {isAdmin && (
                        <div className="flex gap-2 pt-4 border-t">
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1"
                            onClick={() => handleEdit(vehicle)}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="flex-1 text-destructive hover:text-destructive"
                            onClick={() => handleDelete(vehicle.id)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      ) : (
        <EmptyState
          icon={Truck}
          title="No vehicles found"
          description="Get started by adding your first vehicle to the fleet"
          actionLabel="Add Vehicle"
          onAction={() => setIsFormOpen(true)}
        />
      )}
    </div>
  );
}
