'use client';

import { useQuery } from '@tanstack/react-query';
import { travelsApi } from '@/lib/api/travels';
import { vehiclesApi } from '@/lib/api/vehicles';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { useCountUp } from '@/lib/hooks/useCountUp';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'];

export default function AnalyticsPage() {
  const { data: travels, isLoading: travelsLoading } = useQuery({
    queryKey: ['travels'],
    queryFn: () => travelsApi.getAll(),
  });

  const { data: vehicles, isLoading: vehiclesLoading } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesApi.getAll(),
  });

  const isLoading = travelsLoading || vehiclesLoading;

  // Calculate statistics
  const completedTravels = travels?.filter((t) => t.status === 'completed').length || 0;
  const inProgressTravels = travels?.filter((t) => t.status === 'in_progress').length || 0;
  const scheduledTravels = travels?.filter((t) => t.status === 'scheduled').length || 0;

  const statusData = [
    { name: 'Completed', value: completedTravels },
    { name: 'In Progress', value: inProgressTravels },
    { name: 'Scheduled', value: scheduledTravels },
  ];

  const vehicleStatusData = vehicles?.reduce((acc, vehicle) => {
    acc[vehicle.status] = (acc[vehicle.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>) || {};

  const vehicleStatusChart = Object.entries(vehicleStatusData).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  const totalVehicles = useCountUp({ end: vehicles?.length || 0, enabled: !isLoading });
  const totalTravels = useCountUp({ end: travels?.length || 0, enabled: !isLoading });
  const completed = useCountUp({ end: completedTravels, enabled: !isLoading });
  const inProgress = useCountUp({ end: inProgressTravels, enabled: !isLoading });

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Analytics
        </h1>
        <p className="text-muted-foreground mt-2">Fleet performance and statistics</p>
      </motion.div>

      <div className="grid gap-6 md:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
              <CardTitle>Travel Status Distribution</CardTitle>
              <CardDescription>Breakdown of travel statuses</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-0 shadow-lg">
            <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
              <CardTitle>Vehicle Status Distribution</CardTitle>
              <CardDescription>Breakdown of vehicle statuses</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={vehicleStatusChart}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="name" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--popover))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="value" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-primary/5 to-transparent border-b">
            <CardTitle>Summary Statistics</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.4 }}
                className="text-center p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-transparent"
              >
                <p className="text-sm text-muted-foreground mb-2">Total Vehicles</p>
                <p className="text-3xl font-bold">{isLoading ? '...' : totalVehicles}</p>
              </motion.div>
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.5 }}
                className="text-center p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-transparent"
              >
                <p className="text-sm text-muted-foreground mb-2">Total Travels</p>
                <p className="text-3xl font-bold">{isLoading ? '...' : totalTravels}</p>
              </motion.div>
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.6 }}
                className="text-center p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-transparent"
              >
                <p className="text-sm text-muted-foreground mb-2">Completed</p>
                <p className="text-3xl font-bold">{isLoading ? '...' : completed}</p>
              </motion.div>
              <motion.div
                initial={{ scale: 0.9 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.7 }}
                className="text-center p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-transparent"
              >
                <p className="text-sm text-muted-foreground mb-2">In Progress</p>
                <p className="text-3xl font-bold">{isLoading ? '...' : inProgress}</p>
              </motion.div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
