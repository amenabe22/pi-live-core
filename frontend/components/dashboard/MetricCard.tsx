'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';
import { useCountUp } from '@/lib/hooks/useCountUp';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface MetricCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  gradient?: string;
  className?: string;
  isLoading?: boolean;
}

export function MetricCard({
  title,
  value,
  icon: Icon,
  description,
  trend,
  gradient = 'from-blue-500 to-purple-600',
  className,
  isLoading = false,
}: MetricCardProps) {
  const animatedValue = useCountUp({
    end: value,
    duration: 1500,
    enabled: !isLoading && value > 0,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -4 }}
      className="h-full"
    >
      <Card className={cn('relative overflow-hidden border-0 shadow-lg', className)}>
        <div className={cn('absolute inset-0 bg-gradient-to-br opacity-10', gradient)} />
        <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <div className={cn('rounded-lg bg-gradient-to-br p-2', gradient)}>
            <Icon className="h-5 w-5 text-white" />
          </div>
        </CardHeader>
        <CardContent className="relative">
          <div className="text-3xl font-bold mb-1">
            {isLoading ? (
              <div className="h-8 w-24 animate-pulse bg-muted rounded" />
            ) : (
              animatedValue.toLocaleString()
            )}
          </div>
          {description && (
            <p className="text-xs text-muted-foreground mt-1">{description}</p>
          )}
          {trend && (
            <p
              className={cn(
                'text-xs mt-2 flex items-center gap-1',
                trend.isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
              )}
            >
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              {Math.abs(trend.value)}% from last month
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
