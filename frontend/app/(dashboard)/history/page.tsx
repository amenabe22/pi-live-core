'use client';

import { useQuery } from '@tanstack/react-query';
import { historyApi } from '@/lib/api/history';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { formatDate, formatDuration, formatDistance } from '@/lib/utils/formatters';
import { motion } from 'framer-motion';
import { SkeletonTable } from '@/components/ui/loading-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { History } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function HistoryPage() {
  const { data: history, isLoading } = useQuery({
    queryKey: ['history'],
    queryFn: () => historyApi.getTravels({ limit: 100 }),
  });

  const getStatusColor = (status: string) => {
    return status === 'completed' ? 'bg-green-500 hover:bg-green-600' : 'bg-red-500 hover:bg-red-600';
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Travel History
        </h1>
        <p className="text-muted-foreground mt-2">Historical records of all trips</p>
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
        ) : history && history.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Vehicle</TableHead>
                <TableHead>Driver</TableHead>
                <TableHead>Departure</TableHead>
                <TableHead>Arrival</TableHead>
                <TableHead>Distance</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.map((item, index) => (
                <motion.tr
                  key={item.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="border-b hover:bg-muted/50 transition-colors"
                >
                  <TableCell className="font-medium">Vehicle #{item.vehicle_id}</TableCell>
                  <TableCell>Driver #{item.driver_id}</TableCell>
                  <TableCell className="text-muted-foreground">{formatDate(item.departure_time)}</TableCell>
                  <TableCell className="text-muted-foreground">{item.arrival_time ? formatDate(item.arrival_time) : 'N/A'}</TableCell>
                  <TableCell>{formatDistance(item.distance_km)}</TableCell>
                  <TableCell>{formatDuration(item.duration_minutes)}</TableCell>
                  <TableCell>
                    <Badge className={cn('transition-all', getStatusColor(item.status))}>
                      {item.status}
                    </Badge>
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        ) : (
          <EmptyState
            icon={History}
            title="No history found"
            description="Travel history will appear here once trips are completed"
          />
        )}
      </motion.div>
    </div>
  );
}
