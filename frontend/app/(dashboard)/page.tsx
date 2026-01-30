'use client';

import { useQuery } from '@tanstack/react-query';
import { vehiclesApi } from '@/lib/api/vehicles';
import { travelsApi } from '@/lib/api/travels';
import { stationsApi } from '@/lib/api/stations';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { Truck, Route, MapPin, Activity, Plus, ArrowRight, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { formatDate } from '@/lib/utils/formatters';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { SkeletonTable } from '@/components/ui/loading-skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { cn } from '@/lib/utils';

export default function DashboardPage() {
  const { data: vehicles, isLoading: vehiclesLoading } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesApi.getAll(),
  });

  const { data: travels, isLoading: travelsLoading } = useQuery({
    queryKey: ['travels'],
    queryFn: () => travelsApi.getAll({ limit: 10 }),
  });

  const { data: stations, isLoading: stationsLoading } = useQuery({
    queryKey: ['stations'],
    queryFn: () => stationsApi.getAll(),
  });

  const activeTravels = travels?.filter((t) => t.status === 'in_progress') || [];
  const activeVehicles = vehicles?.filter((v) => v.status === 'active') || [];
  const isLoading = vehiclesLoading || travelsLoading || stationsLoading;

  const stats = [
    {
      title: 'Total Vehicles',
      value: vehicles?.length || 0,
      icon: Truck,
      description: `${activeVehicles.length} active`,
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      title: 'Active Travels',
      value: activeTravels.length,
      icon: Route,
      description: 'Currently in progress',
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Stations',
      value: stations?.length || 0,
      icon: MapPin,
      description: 'Total locations',
      gradient: 'from-green-500 to-emerald-500',
    },
    {
      title: 'Vehicles in Motion',
      value: activeTravels.length,
      icon: Activity,
      description: 'Currently tracking',
      gradient: 'from-orange-500 to-red-500',
    },
  ];

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

  const quickActions = [
    {
      href: '/vehicles',
      title: 'Manage Vehicles',
      description: 'View and edit fleet',
      icon: Truck,
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      href: '/travels',
      title: 'Create Travel',
      description: 'Schedule new trip',
      icon: Plus,
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      href: '/tracking',
      title: 'Live Tracking',
      description: 'Monitor vehicles',
      icon: Activity,
      gradient: 'from-green-500 to-emerald-500',
    },
  ];

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Dashboard
        </h1>
        <p className="text-muted-foreground mt-2">Overview of your fleet operations</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 + index * 0.1 }}
          >
            <StatsCard
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              description={stat.description}
              isLoading={isLoading}
            />
          </motion.div>
        ))}
      </motion.div>

      <div className="grid gap-6 md:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-primary" />
                Recent Travels
              </CardTitle>
              <CardDescription>Latest travel activities</CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              {travelsLoading ? (
                <div className="p-6">
                  <SkeletonTable rows={5} />
                </div>
              ) : travels && travels.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Vehicle</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Created</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {travels.slice(0, 5).map((travel, index) => (
                      <motion.tr
                        key={travel.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 + index * 0.05 }}
                        className="border-b hover:bg-muted/50 transition-colors"
                      >
                        <TableCell className="font-medium">
                          {travel.vehicle?.plate_number || 'N/A'}
                        </TableCell>
                        <TableCell>
                          <Badge className={cn('transition-all', getStatusColor(travel.status))}>
                            {travel.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {formatDate(travel.created_at)}
                        </TableCell>
                      </motion.tr>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <EmptyState
                  icon={Route}
                  title="No travels yet"
                  description="Create your first travel to get started"
                  actionLabel="Create Travel"
                  onAction={() => window.location.href = '/travels'}
                />
              )}
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common tasks</CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-3">
              {quickActions.map((action, index) => {
                const Icon = action.icon;
                return (
                  <motion.div
                    key={action.href}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.1 }}
                    whileHover={{ x: 4 }}
                  >
                    <Link
                      href={action.href}
                      className={cn(
                        'group flex items-center justify-between p-4 rounded-lg border-2',
                        'bg-gradient-to-r from-background to-muted/20',
                        'hover:border-primary/50 hover:shadow-md transition-all',
                        'relative overflow-hidden'
                      )}
                    >
                      <div className={cn(
                        'absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-5 transition-opacity',
                        action.gradient
                      )} />
                      <div className="flex items-center gap-4 relative z-10">
                        <div className={cn(
                          'rounded-lg p-2 bg-gradient-to-br',
                          action.gradient
                        )}>
                          <Icon className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <div className="font-semibold">{action.title}</div>
                          <div className="text-sm text-muted-foreground">{action.description}</div>
                        </div>
                      </div>
                      <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all relative z-10" />
                    </Link>
                  </motion.div>
                );
              })}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
