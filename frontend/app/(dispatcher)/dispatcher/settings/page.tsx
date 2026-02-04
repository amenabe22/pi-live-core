'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Bell, Map, Moon, Shield, Smartphone, Globe, Volume2 } from 'lucide-react';
import { Separator } from '@/components/ui/separator';

export default function SettingsPage() {
  return (
    <div className="container max-w-4xl py-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Settings
        </h1>
        <p className="text-muted-foreground mt-2">
          Configure your dashboard preferences and system settings
        </p>
      </div>

      <div className="grid gap-6">
        {/* Notifications Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-primary" />
              <CardTitle>Notifications</CardTitle>
            </div>
            <CardDescription>Manage how you receive alerts and updates</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Emergency Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Receive high-priority notifications for emergency calls
                </p>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Status Updates</Label>
                <p className="text-sm text-muted-foreground">
                  Notify when drivers change their availability status
                </p>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Sound Alerts</Label>
                <p className="text-sm text-muted-foreground">
                  Play a sound when new calls arrive
                </p>
              </div>
              <Switch defaultChecked />
            </div>
          </CardContent>
        </Card>

        {/* Map Preferences */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Map className="w-5 h-5 text-blue-500" />
              <CardTitle>Map Configuration</CardTitle>
            </div>
            <CardDescription>Customize your map view and tracking settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Auto-Center Map</Label>
                <p className="text-sm text-muted-foreground">
                  Automatically focus on new incidents
                </p>
              </div>
              <Switch defaultChecked />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Traffic Layer</Label>
                <p className="text-sm text-muted-foreground">
                  Show real-time traffic conditions
                </p>
              </div>
              <Switch />
            </div>
            <Separator />
            <div className="grid gap-2">
              <Label>Default Zoom Level</Label>
              <div className="flex items-center gap-4">
                <Input type="range" min="1" max="20" defaultValue="12" className="flex-1" />
                <span className="w-12 text-center font-mono">12</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-500" />
              <CardTitle>System</CardTitle>
            </div>
            <CardDescription>Application-wide preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Dark Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Toggle dark/light theme appearance
                </p>
              </div>
              <Switch />
            </div>
            <Separator />
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label className="text-base">Compact Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Reduce spacing for higher information density
                </p>
              </div>
              <Switch />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4">
          <Button variant="outline">Reset to Defaults</Button>
          <Button className="bg-gradient-to-r from-primary to-primary/80">Save Preferences</Button>
        </div>
      </div>
    </div>
  );
}
