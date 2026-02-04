'use client';

import { useAuthStore } from '@/lib/store/authStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { User, Mail, Phone, Shield, Camera } from 'lucide-react';

export default function ProfilePage() {
  const user = useAuthStore((state) => state.user);

  return (
    <div className="container max-w-4xl py-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Profile Settings
        </h1>
        <p className="text-muted-foreground mt-2">
          Manage your account settings and personal information
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-[1fr_2fr]">
        <Card className="h-fit">
          <CardContent className="pt-6 text-center space-y-4">
            <div className="relative mx-auto w-32 h-32">
              <Avatar className="w-32 h-32 border-4 border-background shadow-xl">
                <AvatarFallback className="text-4xl bg-primary/10 text-primary">
                  {user?.email?.charAt(0).toUpperCase() || 'D'}
                </AvatarFallback>
              </Avatar>
              <Button
                size="icon"
                variant="secondary"
                className="absolute bottom-0 right-0 rounded-full shadow-lg"
              >
                <Camera className="w-4 h-4" />
              </Button>
            </div>
            <div>
              <h2 className="text-xl font-semibold">{user?.email?.split('@')[0] || 'Dispatcher'}</h2>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
            </div>
            <div className="flex justify-center gap-2">
              <Badge variant="secondary" className="px-4 py-1">
                Dispatcher
              </Badge>
              <Badge variant="outline" className="px-4 py-1 border-green-500/50 text-green-600 bg-green-500/10">
                Active
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input id="firstName" placeholder="First Name" className="pl-9" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input id="lastName" placeholder="Last Name" className="pl-9" />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  defaultValue={user?.email || ''}
                  disabled
                  className="pl-9 bg-muted/50"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone Number</Label>
              <div className="relative">
                <Phone className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input id="phone" type="tel" placeholder="+1 (555) 000-0000" className="pl-9" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <div className="relative">
                <Shield className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input id="role" defaultValue="Senior Dispatcher" disabled className="pl-9 bg-muted/50" />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <Button variant="outline">Cancel</Button>
              <Button className="bg-gradient-to-r from-primary to-primary/80">Save Changes</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
