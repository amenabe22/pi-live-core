'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, AlertCircle, CheckCircle2 } from 'lucide-react';
import type { DispatchCall, DispatchDriver } from '@/lib/types/dispatcher';
import { MOCK_DRIVERS } from '@/lib/types/dispatcher';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

const statusColors: Record<string, string> = {
  available: 'from-green-500 to-green-600',
  busy: 'from-orange-500 to-orange-600',
  on_route: 'from-blue-500 to-blue-600',
  offline: 'from-gray-500 to-gray-600',
  emergency: 'from-red-500 to-red-600',
};

interface AssignDriverModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  call: DispatchCall | null;
  onAssign?: (callId: string, driverId: string) => void;
}

export function AssignDriverModal({
  open,
  onOpenChange,
  call,
  onAssign,
}: AssignDriverModalProps) {
  const [search, setSearch] = useState('');
  const [assignError, setAssignError] = useState<string | null>(null);
  const [assigningDriverId, setAssigningDriverId] = useState<string | null>(null);

  const filteredDrivers = MOCK_DRIVERS.filter(
    (d) =>
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.location.toLowerCase().includes(search.toLowerCase())
  );

  const handleAssign = (driver: DispatchDriver) => {
    if (!call) return;
    setAssigningDriverId(driver.id);
    setAssignError(null);
    // Simulate compatibility check: Moya Anderson (d3) is "not compatible with vehicle"
    if (driver.id === 'd3') {
      setAssignError('Not compatible with vehicle - accessibility requirements not met');
      setAssigningDriverId(null);
      return;
    }
    // Simulate API delay
    setTimeout(() => {
      onAssign?.(call.id, driver.id);
      setAssigningDriverId(null);
      onOpenChange(false);
    }, 800);
  };

  const handleOpenChange = (o: boolean) => {
    if (!o) {
      setSearch('');
      setAssignError(null);
      setAssigningDriverId(null);
    }
    onOpenChange(o);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-h-[85vh] max-w-xl overflow-hidden flex flex-col p-6 gap-0" showCloseButton={true}>
        <DialogHeader className="mb-4 space-y-2">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-xl font-semibold">
              Assign Unit
            </DialogTitle>
          </div>
          {call && (
            <div className="flex flex-col gap-1 text-sm bg-muted/40 p-3 rounded-md border">
              <span className="font-medium text-foreground">Call #{call.id}</span>
              <span className="text-muted-foreground">{call.location}</span>
            </div>
          )}
        </DialogHeader>

        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground z-10" />
          <Input
            placeholder="Search drivers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 h-10 bg-muted/30 border-muted-foreground/20"
          />
        </div>

        <AnimatePresence>
          {assignError && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-4 overflow-hidden"
            >
              <div className="flex items-start gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-red-900 dark:bg-red-900/10 dark:text-red-200 dark:border-red-900/20">
                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium">Assignment Failed</p>
                  <p className="opacity-90 text-xs mt-0.5">{assignError}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setAssignError(null)}
                  className="ml-auto h-auto p-0 px-2 text-red-900 hover:bg-red-100 dark:text-red-200 dark:hover:bg-red-900/30"
                >
                  Dismiss
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex-1 overflow-y-auto -mx-2 px-2">
          <div className="space-y-1">
            {filteredDrivers.map((driver, index) => (
              <motion.div
                key={driver.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.02 }}
                className={cn(
                  'group flex items-center justify-between gap-3 rounded-lg border border-transparent p-3 transition-colors hover:bg-muted/50',
                  assigningDriverId === driver.id && 'bg-muted border-primary/20'
                )}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className={cn("h-2.5 w-2.5 rounded-full shrink-0",
                    driver.status === 'available' && "bg-green-500",
                    driver.status === 'busy' && "bg-orange-500",
                    driver.status === 'on_route' && "bg-blue-500",
                    driver.status === 'offline' && "bg-slate-400",
                  )} />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{driver.name}</span>
                      <span className="text-xs text-muted-foreground">({driver.id})</span>
                    </div>
                    <div className="flex items-center text-xs text-muted-foreground gap-2 mt-0.5">
                      <span>{driver.location}</span>
                      {driver.distance && (
                        <>
                          <span>•</span>
                          <span>{driver.distance}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <Button
                  size="sm"
                  variant={assigningDriverId === driver.id ? "secondary" : "ghost"}
                  onClick={() => handleAssign(driver)}
                  disabled={assigningDriverId !== null && assigningDriverId !== driver.id}
                  className={cn(
                    "text-xs h-8 opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100",
                    assigningDriverId === driver.id && "opacity-100"
                  )}
                >
                  {assigningDriverId === driver.id ? 'Assigning...' : 'Assign'}
                </Button>
              </motion.div>
            ))}
          </div>

          {filteredDrivers.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <p className="text-sm">No drivers found</p>
            </div>
          )}
        </div>

        <DialogFooter className="border-t pt-4 mt-4">
          <Button variant="ghost" onClick={() => handleOpenChange(false)}>
            Cancel
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
