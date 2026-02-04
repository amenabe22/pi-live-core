'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  MOCK_DISPATCHABLE_CALLS,
  MOCK_UNASSIGNED_CALLS,
  MOCK_RECENT_DISPATCHES,
  type DispatchCall,
} from '@/lib/types/dispatcher';
import { AssignDriverModal } from '@/components/dispatcher/AssignDriverModal';
import { AlertTriangle, Map, Phone, Users, CheckCircle2, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import DummyMap from '@/components/dispatcher/DummyMap';

const statusColors: Record<string, string> = {
  new: 'bg-slate-500/90',
  emergency: 'bg-red-500/90',
  reassigned: 'bg-amber-500/90',
  unassigned: 'bg-orange-500/90',
};

const driverStatusColors: Record<string, string> = {
  available: 'bg-green-500/90',
  busy: 'bg-orange-500/90',
  on_route: 'bg-blue-500/90',
  offline: 'bg-gray-500/90',
  emergency: 'bg-red-500/90',
};

export default function OperationsCenterPage() {
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedCall, setSelectedCall] = useState<DispatchCall | null>(null);

  const openAssignModal = (call: DispatchCall) => {
    setSelectedCall(call);
    setAssignModalOpen(true);
  };

  const handleAssign = (callId: string, driverId: string) => {
    console.log('Assign', callId, driverId);
  };

  const summaryStats = [
    {
      label: 'Total Call',
      value: 14,
      subLabel: 'On Scene',
      subValue: 5,
      icon: Phone,
      gradient: 'from-blue-500 to-cyan-500',
    },
    {
      label: 'Assigned',
      value: 6,
      subLabel: 'In Progress',
      subValue: 4,
      icon: CheckCircle2,
      gradient: 'from-green-500 to-emerald-500',
    },
    {
      label: 'Open Issues',
      value: 3,
      subLabel: 'Critical',
      subValue: 7,
      icon: XCircle,
      gradient: 'from-red-500 to-rose-500',
    },
  ];

  return (
    <div className="space-y-6 p-6">
      {/* Page Title */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Dispatch Dashboard
        </h1>
        <p className="text-muted-foreground mt-2">Real-time operations and call management</p>
      </motion.div>

      {/* Summary Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 sm:grid-cols-3"
      >
        {summaryStats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
            >
              <Card className="relative overflow-hidden border-0 shadow-lg hover:shadow-xl transition-shadow">
                <div className={cn('absolute inset-0 bg-gradient-to-br opacity-5', stat.gradient)} />
                <CardContent className="pt-6 relative z-10">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                      <p className="text-3xl font-bold mt-1">{stat.value}</p>
                    </div>
                    <div className={cn('rounded-lg p-2.5 bg-gradient-to-br', stat.gradient)}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <div className="mt-3 flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{stat.subLabel}</span>
                    <span className="font-semibold">{stat.subValue}</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Alerts */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="space-y-3"
      >
        <motion.div
          whileHover={{ x: 4 }}
          className="flex items-center gap-3 rounded-lg border border-red-500/50 bg-gradient-to-r from-red-500/10 to-transparent px-4 py-3 text-sm font-medium text-red-800 dark:text-red-200 shadow-sm"
        >
          <AlertTriangle className="h-5 w-5 shrink-0 animate-pulse" />
          <span>ALERT: Critical incident in progress - require immediate emergency response</span>
        </motion.div>
        <motion.div
          whileHover={{ x: 4 }}
          className="flex items-center justify-between gap-2 rounded-lg border border-amber-500/50 bg-gradient-to-r from-amber-500/10 to-transparent px-4 py-3 text-sm font-medium text-amber-800 dark:text-amber-200 shadow-sm"
        >
          <span>ALERT: 10 calls pending assignment</span>
          <Button variant="outline" size="sm" className="border-amber-500/50 hover:bg-amber-500/20 shrink-0">
            View All
          </Button>
        </motion.div>
      </motion.div>

      {/* Call Lists */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Dispatchable Calls */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="border-0 shadow-lg overflow-hidden h-full">
            <CardHeader className="border-b bg-gradient-to-r from-primary/10 to-primary/5 py-4">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-lg font-bold text-primary">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Phone className="h-5 w-5" />
                  </div>
                  Dispatchable Calls
                </CardTitle>
                <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                  {MOCK_DISPATCHABLE_CALLS.length} Active
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="max-h-80 overflow-y-auto">
                <div className="space-y-0 divide-y">
                  {MOCK_DISPATCHABLE_CALLS.map((call, index) => (
                    <motion.div
                      key={call.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.05 }}
                      className="flex flex-wrap items-start justify-between gap-3 p-4 hover:bg-muted/50 transition-colors cursor-pointer group"
                    >
                      <div className="min-w-0 flex-1 space-y-1.5">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-sm font-bold group-hover:text-primary transition-colors">{call.id}</span>
                          <Badge className={cn('text-xs text-white', statusColors[call.status] ?? 'bg-gray-500')}>
                            {call.status === 'emergency' ? 'Emergency Call' : call.status === 'new' ? 'New Call' : 'Reassigned'}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground font-medium">{call.location}</p>
                        <p className="text-xs text-muted-foreground">Time: {call.time}</p>
                        <p className="text-sm leading-relaxed">{call.description}</p>
                      </div>
                      <div className="flex gap-2 shrink-0">
                        <Button size="sm" variant="outline" className="hover:bg-accent">
                          Open In
                        </Button>
                        <Button size="sm" onClick={() => openAssignModal(call)} className="bg-gradient-to-r from-primary to-primary/80 shadow-sm hover:shadow-md transition-all">
                          Assign
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Unassigned Calls */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="border-0 shadow-lg overflow-hidden h-full">
            <CardHeader className="border-b bg-gradient-to-r from-orange-500/10 to-orange-500/5 py-4">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-lg font-bold text-orange-700 dark:text-orange-400">
                  <div className="p-2 rounded-lg bg-orange-500/10">
                    <AlertTriangle className="h-5 w-5 text-orange-500" />
                  </div>
                  Unassigned Calls
                </CardTitle>
                <Badge variant="secondary" className="bg-orange-500/10 text-orange-600 border-orange-500/20">
                  {MOCK_UNASSIGNED_CALLS.length} Pending
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="max-h-80 overflow-y-auto">
                <div className="space-y-0 divide-y">
                  {MOCK_UNASSIGNED_CALLS.map((call, index) => (
                    <motion.div
                      key={call.id}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.05 }}
                      className="flex flex-wrap items-start justify-between gap-3 p-4 hover:bg-muted/50 transition-colors cursor-pointer group"
                    >
                      <div className="min-w-0 flex-1 space-y-1.5">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono text-sm font-bold group-hover:text-orange-500 transition-colors">{call.id}</span>
                          <Badge className={cn('text-xs text-white', statusColors[call.status] ?? 'bg-gray-500')}>
                            {call.status === 'unassigned' ? 'Unassigned' : 'New Call'}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground font-medium">{call.location}</p>
                        <p className="text-xs text-muted-foreground">Time: {call.time}</p>
                        <p className="text-sm leading-relaxed">{call.description}</p>
                      </div>
                      <Button size="sm" onClick={() => openAssignModal(call)} className="shrink-0 bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-sm hover:shadow-md transition-all">
                        Assign
                      </Button>
                    </motion.div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Dispatches */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card className="border-0 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between border-b bg-gradient-to-r from-green-500/10 to-transparent pb-3">
            <CardTitle className="flex items-center gap-2 text-lg text-green-700 dark:text-green-400">
              <div className="p-2 rounded-lg bg-green-500/10">
                <Users className="h-5 w-5 text-green-500" />
              </div>
              Recent Dispatches
            </CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="hover:bg-accent">
                Map View
              </Button>
              <Button variant="outline" size="sm" className="hover:bg-accent">
                Live Map
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-96 overflow-y-auto">
              <div className="space-y-0 divide-y">
                {MOCK_RECENT_DISPATCHES.map((driver, index) => (
                  <motion.div
                    key={driver.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 + index * 0.05 }}
                    className="flex flex-wrap items-center justify-between gap-3 p-4 hover:bg-muted/50 transition-colors"
                  >
                    <div className="space-y-1.5">
                      <p className="font-semibold">{driver.name}</p>
                      <p className="text-sm text-muted-foreground">{driver.location}</p>
                      <div className="flex items-center gap-2 text-xs">
                        <Badge className={cn('text-xs text-white', driverStatusColors[driver.status] ?? 'bg-gray-500')}>
                          {driver.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-muted-foreground">{driver.lastUpdated}</span>
                      </div>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <Button variant="ghost" size="sm" className="hover:bg-accent">
                        Map View
                      </Button>
                      <Button variant="ghost" size="sm" className="hover:bg-accent">
                        Live Map
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Map Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        <Card className="border-0 shadow-lg">
          <CardHeader className="flex flex-row items-center justify-between border-b bg-gradient-to-r from-blue-500/10 to-transparent pb-3">
            <CardTitle className="flex items-center gap-2 text-lg text-blue-700 dark:text-blue-400">
              <div className="p-2 rounded-lg bg-blue-500/10">
                <Map className="h-5 w-5 text-blue-500" />
              </div>
              Live Map View
            </CardTitle>
            <div className="flex gap-2 flex-wrap">
              <select className="rounded-lg border bg-background px-3 py-1.5 text-sm hover:bg-accent transition-colors">
                <option>All Status</option>
                <option>Available</option>
                <option>Busy</option>
                <option>On Route</option>
              </select>
              <select className="rounded-lg border bg-background px-3 py-1.5 text-sm hover:bg-accent transition-colors">
                <option>All Types</option>
                <option>Emergency</option>
                <option>Standard</option>
              </select>
              <Button variant="outline" size="sm" className="hover:bg-accent">
                Map View
              </Button>
              <Button variant="outline" size="sm" className="hover:bg-accent">
                Live Map
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <DummyMap />
          </CardContent>
        </Card>
      </motion.div>

      <AssignDriverModal
        open={assignModalOpen}
        onOpenChange={setAssignModalOpen}
        call={selectedCall}
        onAssign={handleAssign}
      />
    </div>
  );
}
