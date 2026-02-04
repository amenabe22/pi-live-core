'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
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
import { Sidebar } from '@/components/dashboard/Sidebar';
import { Topbar } from '@/components/dashboard/Topbar';
import { Toaster } from 'sonner';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Menu } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isDispatcher } = useAuthStore();
  const [isChecking, setIsChecking] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    // Wait a bit for Zustand persist to hydrate
    const timer = setTimeout(() => {
      const authenticated = isAuthenticated();
      const dispatcher = isDispatcher();

      if (!authenticated) {
        router.replace('/login');
      } else if (dispatcher) {
        router.replace('/dispatcher');
      } else {
        setIsChecking(false);
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [router, isAuthenticated, isDispatcher]);

  const { data: vehicles, isLoading: vehiclesLoading } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesApi.getAll(),
    enabled: !isChecking,
  });

  const { data: travels, isLoading: travelsLoading } = useQuery({
    queryKey: ['travels'],
    queryFn: () => travelsApi.getAll({ limit: 10 }),
    enabled: !isChecking,
  });

  const { data: stations, isLoading: stationsLoading } = useQuery({
    queryKey: ['stations'],
    queryFn: () => stationsApi.getAll(),
    enabled: !isChecking,
  });

  // Show loading state while checking auth
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">PI-Line</h1>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

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
      gradient: 'from-green-500 to-emerald-500',
    },
    {
      title: 'Stations',
      value: stations?.length || 0,
      icon: MapPin,
      description: 'Total locations',
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Vehicles in Motion',
      value: activeTravels.length,
      icon: Activity,
      description: 'Currently tracking',
      gradient: 'from-yellow-500 to-orange-500',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in_progress':
        return 'bg-blue-500';
      case 'scheduled':
        return 'bg-yellow-500';
      case 'cancelled':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="w-64 p-0">
          <Sidebar />
        </SheetContent>
      </Sheet>

      <div className="flex flex-1 flex-col overflow-hidden">
        <div className="lg:hidden border-b">
          <div className="flex items-center gap-4 p-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              PI-Line
            </h1>
          </div>
        </div>
        <Topbar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="space-y-6">
            <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                Dashboard
              </h1>
              <p className="text-muted-foreground mt-2">Overview of your fleet operations</p>
            </motion.div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.title}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <StatsCard
                    title={stat.title}
                    value={stat.value}
                    icon={stat.icon}
                    description={stat.description}
                    className={cn('relative overflow-hidden', stat.gradient && `bg-gradient-to-br ${stat.gradient} text-white`)}
                  />
                </motion.div>
              ))}
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle>Recent Travels</CardTitle>
                    <CardDescription>Latest travel activities</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {isLoading ? (
                      <SkeletonTable rows={5} />
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
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: index * 0.05 }}
                              className="border-b hover:bg-muted/50 transition-colors"
                            >
                              <TableCell className="font-medium">{travel.vehicle?.plate_number || 'N/A'}</TableCell>
                              <TableCell>
                                <Badge className={getStatusColor(travel.status)}>
                                  {travel.status}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-muted-foreground">{formatDate(travel.created_at)}</TableCell>
                            </motion.tr>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <EmptyState
                        icon={Route}
                        title="No recent travels"
                        description="Start a new travel to see it here."
                        actionLabel="Create Travel"
                        onAction={() => router.push('/travels')}
                      />
                    )}
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                    <CardDescription>Common tasks</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Link
                      href="/vehicles"
                      className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group"
                    >
                      <Truck className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                      <div>
                        <div className="font-medium">Manage Vehicles</div>
                        <div className="text-sm text-muted-foreground">View and edit fleet</div>
                      </div>
                      <ArrowRight className="ml-auto h-4 w-4 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
                    </Link>
                    <Link
                      href="/travels"
                      className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group"
                    >
                      <Plus className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                      <div>
                        <div className="font-medium">Create Travel</div>
                        <div className="text-sm text-muted-foreground">Schedule new trip</div>
                      </div>
                      <ArrowRight className="ml-auto h-4 w-4 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
                    </Link>
                    <Link
                      href="/tracking"
                      className="flex items-center gap-3 p-3 rounded-lg border hover:bg-accent transition-colors group"
                    >
                      <Clock className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                      <div>
                        <div className="font-medium">Live Tracking</div>
                        <div className="text-sm text-muted-foreground">Monitor vehicles</div>
                      </div>
                      <ArrowRight className="ml-auto h-4 w-4 text-muted-foreground group-hover:text-primary transition-transform group-hover:translate-x-1" />
                    </Link>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
        </div>
      </main>
      </div>
      <Toaster />
    </div>
  );
}
