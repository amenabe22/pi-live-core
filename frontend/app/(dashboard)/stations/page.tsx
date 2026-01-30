'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { stationsApi } from '@/lib/api/stations';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { StationForm } from '@/components/stations/StationForm';
import { Plus, Edit, Trash2, MapPin } from 'lucide-react';
import { toast } from 'sonner';
import { useAuthStore } from '@/lib/store/authStore';
import { formatDate } from '@/lib/utils/formatters';
import type { Station } from '@/lib/types/api';
import { motion } from 'framer-motion';
import { SkeletonTable } from '@/components/ui/loading-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { cn } from '@/lib/utils';

export default function StationsPage() {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingStation, setEditingStation] = useState<Station | null>(null);
  const queryClient = useQueryClient();
  const isAdmin = useAuthStore((state) => {
    const { user } = state;
    return user?.role === 'admin';
  });

  const { data: stations, isLoading } = useQuery({
    queryKey: ['stations'],
    queryFn: () => stationsApi.getAll(),
  });

  const deleteMutation = useMutation({
    mutationFn: stationsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stations'] });
      toast.success('Station deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete station');
    },
  });

  const handleEdit = (station: Station) => {
    setEditingStation(station);
    setIsFormOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this station?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleFormSuccess = () => {
    setIsFormOpen(false);
    setEditingStation(null);
    queryClient.invalidateQueries({ queryKey: ['stations'] });
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
            Stations
          </h1>
          <p className="text-muted-foreground mt-2">Manage pickup and dropoff locations</p>
        </div>
        {isAdmin && (
          <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
            <DialogTrigger asChild>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button onClick={() => setEditingStation(null)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Station
                </Button>
              </motion.div>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>{editingStation ? 'Edit Station' : 'Add Station'}</DialogTitle>
              </DialogHeader>
              <StationForm
                station={editingStation}
                onSuccess={handleFormSuccess}
                onCancel={() => {
                  setIsFormOpen(false);
                  setEditingStation(null);
                }}
              />
            </DialogContent>
          </Dialog>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-lg border bg-card shadow-md overflow-hidden"
      >
        {isLoading ? (
          <div className="p-6">
            <SkeletonTable rows={5} />
          </div>
        ) : stations && stations.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Radius</TableHead>
                <TableHead>Address</TableHead>
                <TableHead>Created</TableHead>
                {isAdmin && <TableHead className="text-right">Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {stations.map((station, index) => (
                <motion.tr
                  key={station.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b hover:bg-muted/50 transition-colors"
                >
                  <TableCell className="font-medium">{station.name}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      {station.latitude.toFixed(4)}, {station.longitude.toFixed(4)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{station.radius}m</Badge>
                  </TableCell>
                  <TableCell>{station.address || 'N/A'}</TableCell>
                  <TableCell className="text-muted-foreground">{formatDate(station.created_at)}</TableCell>
                  {isAdmin && (
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEdit(station)}
                          className="hover:bg-primary/10"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(station.id)}
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
        ) : (
          <EmptyState
            icon={MapPin}
            title="No stations found"
            description="Add your first station to get started"
            actionLabel="Add Station"
            onAction={() => setIsFormOpen(true)}
          />
        )}
      </motion.div>
    </div>
  );
}
