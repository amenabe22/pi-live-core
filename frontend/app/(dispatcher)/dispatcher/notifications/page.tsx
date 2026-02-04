'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bell, AlertTriangle, Info, CheckCircle2, Clock, Trash2 } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

const MOCK_NOTIFICATIONS = [
  {
    id: 1,
    type: 'emergency',
    title: 'New Emergency Call',
    message: 'Reported cardiac arrest at 123 Main St. Require immediate dispatch.',
    time: '2 mins ago',
    read: false,
  },
  {
    id: 2,
    type: 'warning',
    title: 'High Call Volume',
    message: 'Call volume has exceeded normal thresholds for this sector.',
    time: '15 mins ago',
    read: false,
  },
  {
    id: 3,
    type: 'success',
    title: 'Unit Arrived',
    message: 'Unit A-12 has arrived at scene #4092.',
    time: '32 mins ago',
    read: true,
  },
  {
    id: 4,
    type: 'info',
    title: 'System Update',
    message: 'Maintenance scheduled for tonight at 03:00 AM.',
    time: '2 hours ago',
    read: true,
  },
  {
    id: 5,
    type: 'info',
    title: 'Shift Change',
    message: 'Shift handover report is ready for review.',
    time: '4 hours ago',
    read: true,
  },
];

export default function NotificationsPage() {
  return (
    <div className="container max-w-4xl py-6 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            Notifications
          </h1>
          <p className="text-muted-foreground mt-2">
            Stay updated with alerts and system messages
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <CheckCircle2 className="mr-2 h-4 w-4" />
            Mark all as read
          </Button>
          <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive hover:bg-destructive/10">
            <Trash2 className="mr-2 h-4 w-4" />
            Clear all
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <ScrollArea className="h-[600px]">
            <div className="divide-y">
              {MOCK_NOTIFICATIONS.map((notification, index) => {
                const getIcon = () => {
                  switch (notification.type) {
                    case 'emergency': return <AlertTriangle className="h-5 w-5 text-red-500" />;
                    case 'warning': return <AlertTriangle className="h-5 w-5 text-orange-500" />;
                    case 'success': return <CheckCircle2 className="h-5 w-5 text-green-500" />;
                    default: return <Info className="h-5 w-5 text-blue-500" />;
                  }
                };

                const getBgClass = () => {
                  if (notification.read) return 'bg-background';
                  switch (notification.type) {
                    case 'emergency': return 'bg-red-500/5';
                    case 'warning': return 'bg-orange-500/5';
                    default: return 'bg-primary/5';
                  }
                };

                return (
                  <motion.div
                    key={notification.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={cn(
                      'flex items-start gap-4 p-4 transition-colors hover:bg-muted/50 relative group',
                      getBgClass()
                    )}
                  >
                    <div className={cn(
                      'rounded-full p-2 border shrink-0',
                      notification.read ? 'bg-muted' : 'bg-background shadow-sm'
                    )}>
                      {getIcon()}
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between">
                        <p className={cn("font-medium", !notification.read && "text-foreground")}>
                          {notification.title}
                        </p>
                        <span className="flex items-center text-xs text-muted-foreground">
                          <Clock className="mr-1 h-3 w-3" />
                          {notification.time}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {notification.message}
                      </p>
                    </div>
                    {!notification.read && (
                      <div className="absolute top-4 right-4 h-2 w-2 rounded-full bg-primary ring-4 ring-primary/20" />
                    )}
                  </motion.div>
                );
              })}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
