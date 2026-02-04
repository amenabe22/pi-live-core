'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
import { OperationsCenterHeader } from '@/components/dispatcher/OperationsCenterHeader';
import { Toaster } from 'sonner';

export default function DispatcherLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());
  const isDispatcher = useAuthStore((state) => state.isDispatcher());

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    } else if (!isDispatcher) {
      router.push('/');
    }
  }, [isAuthenticated, isDispatcher, router]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-background to-muted/20">
      <OperationsCenterHeader />
      <main className="flex-1 overflow-y-auto">{children}</main>
      <Toaster />
    </div>
  );
}
