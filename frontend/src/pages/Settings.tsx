import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Settings as SettingsIcon, Bell, Shield, Palette, Globe, Trash2, CheckCircle } from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';

export default function Settings() {
  const { updatePreferences } = useUserStore();
  const [saved, setSaved] = useState(false);

  const [notifications, setNotifications] = useState({
    jobAlerts: true,
    careerUpdates: true,
    weeklyDigest: false,
    applicationReminders: true,
  });

  const [privacy, setPrivacy] = useState({
    shareProgress: false,
    allowAnalytics: true,
    publicProfile: false,
  });

  const [appearance, setAppearance] = useState({
    theme: 'dark',
    language: 'en',
    density: 'comfortable',
  });

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div id="settings-container" className="container mx-auto py-8 px-4 max-w-3xl">
      <motion.div
        id="settings-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <SettingsIcon className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-3xl font-bold">Settings</h1>
        </div>
        <p className="text-muted-foreground">Manage your preferences and account settings.</p>
      </motion.div>

      <div id="settings-sections" className="space-y-6">
        {/* Appearance */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card id="appearance-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Palette className="h-4 w-4 text-primary" />
                Appearance
              </CardTitle>
              <CardDescription>Customize the look and feel of the platform</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div id="theme-setting" className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Theme</Label>
                  <p className="text-sm text-muted-foreground">Choose your preferred color scheme</p>
                </div>
                <Select value={appearance.theme} onValueChange={(v) => setAppearance({ ...appearance, theme: v })}>
                  <SelectTrigger id="theme-select" className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Separator />
              <div id="language-setting" className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Language</Label>
                  <p className="text-sm text-muted-foreground">Set your display language</p>
                </div>
                <Select value={appearance.language} onValueChange={(v) => setAppearance({ ...appearance, language: v })}>
                  <SelectTrigger id="language-select" className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="fr">Français</SelectItem>
                    <SelectItem value="de">Deutsch</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Separator />
              <div id="density-setting" className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Display Density</Label>
                  <p className="text-sm text-muted-foreground">Control spacing and layout density</p>
                </div>
                <Select value={appearance.density} onValueChange={(v) => setAppearance({ ...appearance, density: v })}>
                  <SelectTrigger id="density-select" className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="compact">Compact</SelectItem>
                    <SelectItem value="comfortable">Comfortable</SelectItem>
                    <SelectItem value="spacious">Spacious</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Notifications */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card id="notifications-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Bell className="h-4 w-4 text-primary" />
                Notifications
              </CardTitle>
              <CardDescription>Control what updates you receive</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { key: 'jobAlerts', label: 'Job Alerts', desc: 'New jobs matching your profile' },
                { key: 'careerUpdates', label: 'Career Updates', desc: 'Insights and market trends' },
                { key: 'weeklyDigest', label: 'Weekly Digest', desc: 'Summary of your progress every week' },
                { key: 'applicationReminders', label: 'Application Reminders', desc: 'Follow-up prompts for saved jobs' },
              ].map(({ key, label, desc }) => (
                <div key={key} id={`notif-${key}`} className="flex items-center justify-between py-1">
                  <div>
                    <Label className="font-medium">{label}</Label>
                    <p className="text-sm text-muted-foreground">{desc}</p>
                  </div>
                  <Switch
                    id={`switch-${key}`}
                    checked={notifications[key as keyof typeof notifications]}
                    onCheckedChange={(v) => setNotifications({ ...notifications, [key]: v })}
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Privacy */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card id="privacy-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Shield className="h-4 w-4 text-primary" />
                Privacy & Data
              </CardTitle>
              <CardDescription>Control how your data is used</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { key: 'shareProgress', label: 'Share Progress', desc: 'Allow others to see your career milestones' },
                { key: 'allowAnalytics', label: 'Usage Analytics', desc: 'Help improve the platform with anonymous usage data' },
                { key: 'publicProfile', label: 'Public Profile', desc: 'Make your profile discoverable to employers' },
              ].map(({ key, label, desc }) => (
                <div key={key} id={`privacy-${key}`} className="flex items-center justify-between py-1">
                  <div>
                    <Label className="font-medium">{label}</Label>
                    <p className="text-sm text-muted-foreground">{desc}</p>
                  </div>
                  <Switch
                    id={`switch-privacy-${key}`}
                    checked={privacy[key as keyof typeof privacy]}
                    onCheckedChange={(v) => setPrivacy({ ...privacy, [key]: v })}
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Job Preferences */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card id="job-prefs-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Globe className="h-4 w-4 text-primary" />
                Job Preferences
              </CardTitle>
              <CardDescription>Refine what jobs are recommended to you</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div id="work-type-setting" className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Work Type</Label>
                  <p className="text-sm text-muted-foreground">Your preferred work arrangement</p>
                </div>
                <Select defaultValue="hybrid">
                  <SelectTrigger id="work-type-select" className="w-36">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="remote">Remote</SelectItem>
                    <SelectItem value="hybrid">Hybrid</SelectItem>
                    <SelectItem value="onsite">On-site</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Separator />
              <div id="experience-setting" className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Experience Level</Label>
                  <p className="text-sm text-muted-foreground">Show roles matching your level</p>
                </div>
                <Select defaultValue="entry">
                  <SelectTrigger id="experience-select" className="w-36">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="entry">Entry Level</SelectItem>
                    <SelectItem value="mid">Mid Level</SelectItem>
                    <SelectItem value="senior">Senior</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Danger Zone */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card id="danger-zone-card" className="border-destructive/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base text-destructive">
                <Trash2 className="h-4 w-4" />
                Danger Zone
              </CardTitle>
              <CardDescription>Irreversible account actions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div id="clear-data-row" className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                <div>
                  <p className="font-medium text-sm">Clear All Data</p>
                  <p className="text-xs text-muted-foreground">Remove all saved jobs, bookmarks, and progress</p>
                </div>
                <Button id="clear-data-btn" variant="outline" size="sm" className="border-destructive/30 text-destructive hover:bg-destructive/10">
                  Clear Data
                </Button>
              </div>
              <div id="delete-account-row" className="flex items-center justify-between p-3 rounded-lg border border-border/50">
                <div>
                  <p className="font-medium text-sm">Delete Account</p>
                  <p className="text-xs text-muted-foreground">Permanently delete your account and all data</p>
                </div>
                <Button id="delete-account-btn" variant="destructive" size="sm">
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Save Button */}
        <div id="settings-save-row" className="flex justify-end">
          <Button id="settings-save-btn" onClick={handleSave} className="gap-2 px-6">
            {saved ? (
              <>
                <CheckCircle className="h-4 w-4" />
                Saved!
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
