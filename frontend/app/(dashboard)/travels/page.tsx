'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { travelsApi } from '@/lib/api/travels';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { TravelForm } from '@/components/travels/TravelForm';
import { Plus, Play, Check, X } from 'lucide-react';
import { toast } from 'sonner';
import { useAuthStore } from '@/lib/store/authStore';
import { formatDate } from '@/lib/utils/formatters';
import type { Travel } from '@/lib/types/api';
import { motion } from 'framer-motion';
import { SkeletonTable } from '@/components/ui/loading-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Route } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function TravelsPage() {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const queryClient = useQueryClient();
  const isAdmin = useAuthStore((state) => {
    const { user } = state;
    return user?.role === 'admin';
  });

  const { data: travels, isLoading } = useQuery({
    queryKey: ['travels'],
    queryFn: () => travelsApi.getAll(),
  });

  const startMutation = useMutation({
    mutationFn: travelsApi.start,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['travels'] });
      toast.success('Travel started');
    },
  });

  const completeMutation = useMutation({
    mutationFn: travelsApi.complete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['travels'] });
      toast.success('Travel completed');
    },
  });

  const cancelMutation = useMutation({
    mutationFn: travelsApi.cancel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['travels'] });
      toast.success('Travel cancelled');
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 hover:bg-green-600';
      case 'in_progress':
        return 'bg-blue-500 hover:bg-blue-600';
      case 'scheduled':
        return 'bg-yellow-500 hover:bg-yellow-600';
      case 'cancelled':
        return 'bg-red-500 hover:bg-red-600';
      default:
        return 'bg-gray-500';
    }
  };

  const handleStart = (id: string) => {
    startMutation.mutate(id);
  };

  const handleComplete = (id: string) => {
    completeMutation.mutate(id);
  };

  const handleCancel = (id: string) => {
    if (confirm('Are you sure you want to cancel this travel?')) {
      cancelMutation.mutate(id);
    }
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
            Travels
          </h1>
          <p className="text-muted-foreground mt-2">Manage trips and journeys</p>
        </div>
        {(isAdmin || true) && (
          <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
            <DialogTrigger asChild>
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button onClick={() => setIsFormOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Travel
                </Button>
              </motion.div>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Travel</DialogTitle>
              </DialogHeader>
              <TravelForm
                onSuccess={() => {
                  setIsFormOpen(false);
                  queryClient.invalidateQueries({ queryKey: ['travels'] });
                }}
                onCancel={() => setIsFormOpen(false)}
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
        ) : travels && travels.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Vehicle</TableHead>
                <TableHead>Driver</TableHead>
                <TableHead>Origin</TableHead>
                <TableHead>Destination</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {travels.map((travel, index) => (
                <motion.tr
                  key={travel.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b hover:bg-muted/50 transition-colors"
                >
                  <TableCell className="font-medium">{travel.vehicle?.plate_number || 'N/A'}</TableCell>
                  <TableCell>{travel.driver?.email || 'N/A'}</TableCell>
                  <TableCell>{travel.origin_station?.name || 'N/A'}</TableCell>
                  <TableCell>{travel.destination_station?.name || 'N/A'}</TableCell>
                  <TableCell>
                    <Badge className={cn('transition-all', getStatusColor(travel.status))}>
                      {travel.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{formatDate(travel.created_at)}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      {travel.status === 'scheduled' && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleStart(travel.id)}
                          className="hover:bg-green-500/10 hover:text-green-600"
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      {travel.status === 'in_progress' && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleComplete(travel.id)}
                          className="hover:bg-blue-500/10 hover:text-blue-600"
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                      )}
                      {(travel.status === 'scheduled' || travel.status === 'in_progress') && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleCancel(travel.id)}
                          className="hover:bg-red-500/10 hover:text-red-600"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        ) : (
          <EmptyState
            icon={Route}
            title="No travels found"
            description="Create your first travel to get started"
            actionLabel="Create Travel"
            onAction={() => setIsFormOpen(true)}
          />
        )}
      </motion.div>
    </div>
  );
}
