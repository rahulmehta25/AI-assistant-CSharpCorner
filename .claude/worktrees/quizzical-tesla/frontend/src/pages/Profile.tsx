import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { User, MapPin, GraduationCap, Briefcase, Plus, X, CheckCircle, Star } from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';

export default function Profile() {
  const { user, updateProfile } = useUserStore();
  const [saved, setSaved] = useState(false);
  const [newSkill, setNewSkill] = useState('');

  const [formData, setFormData] = useState({
    name: user?.name ?? '',
    email: user?.email ?? '',
    title: user?.profile?.title ?? '',
    experience: user?.profile?.experience ?? '',
    education: user?.profile?.education ?? '',
    location: user?.profile?.location ?? '',
  });

  const interests = user?.profile?.interests ?? [];
  const skills = user?.profile?.skills ?? [];

  const completionFields = [
    { label: 'Basic Info', done: !!(formData.name && formData.email) },
    { label: 'Current Role', done: !!formData.title },
    { label: 'Location', done: !!formData.location },
    { label: 'Education', done: !!formData.education },
    { label: 'Skills Added', done: skills.length >= 3 },
    { label: 'Interests Set', done: interests.length >= 2 },
  ];
  const completionPct = Math.round((completionFields.filter((f) => f.done).length / completionFields.length) * 100);

  const handleSave = () => {
    updateProfile({
      title: formData.title,
      experience: formData.experience,
      education: formData.education,
      location: formData.location,
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const getSkillLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'expert': return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'advanced': return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'intermediate': return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      default: return 'bg-muted text-muted-foreground border-border';
    }
  };

  return (
    <div id="profile-container" className="container mx-auto py-8 px-4 max-w-4xl">
      <motion.div
        id="profile-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <User className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-3xl font-bold">My Profile</h1>
        </div>
        <p className="text-muted-foreground">Manage your personal information and career preferences.</p>
      </motion.div>

      <div id="profile-grid" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: avatar + completion */}
        <div id="profile-sidebar" className="space-y-4">
          <Card className="border-border/50">
            <CardContent className="pt-6 text-center">
              <div id="avatar-section" className="relative inline-block mb-4">
                <Avatar className="h-24 w-24 mx-auto">
                  <AvatarImage src={user?.avatar} alt={user?.name} />
                  <AvatarFallback className="text-2xl bg-gradient-to-br from-primary to-secondary text-white">
                    {user?.name?.charAt(0) ?? 'U'}
                  </AvatarFallback>
                </Avatar>
              </div>
              <h2 className="font-semibold text-lg">{user?.name}</h2>
              <p className="text-sm text-muted-foreground">{user?.profile?.title}</p>
              <p className="text-xs text-muted-foreground flex items-center justify-center gap-1 mt-1">
                <MapPin className="h-3 w-3" />
                {user?.profile?.location}
              </p>
            </CardContent>
          </Card>

          <Card id="completion-card" className="border-border/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Profile Strength</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 mb-3">
                <Progress value={completionPct} className="flex-1 h-2" />
                <span className="text-sm font-semibold">{completionPct}%</span>
              </div>
              <div id="completion-checklist" className="space-y-2">
                {completionFields.map((f, i) => (
                  <div key={i} id={`completion-item-${i}`} className="flex items-center gap-2 text-xs">
                    {f.done ? (
                      <CheckCircle className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                    ) : (
                      <div className="h-3.5 w-3.5 rounded-full border border-muted-foreground/40 flex-shrink-0" />
                    )}
                    <span className={f.done ? 'text-foreground' : 'text-muted-foreground'}>{f.label}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right column: form */}
        <div id="profile-form-col" className="lg:col-span-2 space-y-5">
          {/* Basic Info */}
          <Card id="basic-info-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <User className="h-4 w-4 text-primary" />
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div id="name-row" className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="profile-name">Full Name</Label>
                  <Input
                    id="profile-name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="profile-email">Email</Label>
                  <Input
                    id="profile-email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
              </div>
              <div id="location-row" className="space-y-1.5">
                <Label htmlFor="profile-location">
                  <MapPin className="inline h-3.5 w-3.5 mr-1" />
                  Location
                </Label>
                <Input
                  id="profile-location"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="City, State"
                />
              </div>
            </CardContent>
          </Card>

          {/* Career Info */}
          <Card id="career-info-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Briefcase className="h-4 w-4 text-primary" />
                Career Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div id="title-exp-row" className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label htmlFor="profile-title">Current Title</Label>
                  <Input
                    id="profile-title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="e.g. Software Engineer"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="profile-experience">Experience Level</Label>
                  <Select
                    value={formData.experience}
                    onValueChange={(v) => setFormData({ ...formData, experience: v })}
                  >
                    <SelectTrigger id="profile-experience">
                      <SelectValue placeholder="Select level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Entry Level">Entry Level</SelectItem>
                      <SelectItem value="Mid Level">Mid Level</SelectItem>
                      <SelectItem value="Senior">Senior</SelectItem>
                      <SelectItem value="Lead / Principal">Lead / Principal</SelectItem>
                      <SelectItem value="Executive">Executive</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div id="education-row" className="space-y-1.5">
                <Label htmlFor="profile-education">
                  <GraduationCap className="inline h-3.5 w-3.5 mr-1" />
                  Education
                </Label>
                <Input
                  id="profile-education"
                  value={formData.education}
                  onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                  placeholder="e.g. Bachelor's in Computer Science"
                />
              </div>
            </CardContent>
          </Card>

          {/* Skills */}
          <Card id="skills-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Star className="h-4 w-4 text-primary" />
                Skills
              </CardTitle>
              <CardDescription>Skills that power your career recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              <div id="skills-list" className="flex flex-wrap gap-2 mb-4">
                {skills.map((skill) => (
                  <Badge
                    key={skill.id}
                    className={`gap-1 pr-1 ${getSkillLevelColor(skill.level)}`}
                  >
                    {skill.name}
                    <span className="text-xs opacity-60 capitalize ml-1">{skill.level}</span>
                  </Badge>
                ))}
                {skills.length === 0 && (
                  <p className="text-sm text-muted-foreground">No skills added yet.</p>
                )}
              </div>
              <div id="add-skill-row" className="flex gap-2">
                <Input
                  id="new-skill-input"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  placeholder="Add a skill (e.g. TypeScript)"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && newSkill.trim()) {
                      setNewSkill('');
                    }
                  }}
                />
                <Button id="add-skill-btn" variant="outline" size="icon" onClick={() => setNewSkill('')}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Interests */}
          <Card id="interests-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="text-base">Interests & Goals</CardTitle>
              <CardDescription>Career fields you're excited about</CardDescription>
            </CardHeader>
            <CardContent>
              <div id="interests-list" className="flex flex-wrap gap-2">
                {interests.map((interest, i) => (
                  <Badge key={i} variant="secondary" className="gap-1 pr-1">
                    {interest}
                    <button className="ml-1 opacity-60 hover:opacity-100">
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
                {interests.length === 0 && (
                  <p className="text-sm text-muted-foreground">No interests added.</p>
                )}
              </div>
            </CardContent>
          </Card>

          <div id="profile-save-row" className="flex justify-end">
            <Button id="profile-save-btn" onClick={handleSave} className="gap-2 px-6">
              {saved ? (
                <>
                  <CheckCircle className="h-4 w-4" />
                  Saved!
                </>
              ) : (
                'Save Profile'
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
