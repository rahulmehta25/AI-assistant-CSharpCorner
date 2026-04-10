import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  FileText,
  Search,
  Plus,
  Building,
  MapPin,
  Calendar,
  ExternalLink,
  CheckCircle,
  Clock,
  XCircle,
  Send,
  Filter,
} from 'lucide-react';
import { addDays, format } from 'date-fns';

interface Application {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  appliedDate: string;
  status: 'applied' | 'screening' | 'interview' | 'offer' | 'rejected' | 'withdrawn';
  nextStep?: string;
  nextStepDate?: string;
  notes?: string;
  source: string;
}

const today = new Date();

const mockApplications: Application[] = [
  {
    id: '1',
    title: 'Frontend Developer',
    company: 'TechCorp',
    location: 'San Francisco, CA',
    salary: '$95,000 – $125,000',
    appliedDate: format(addDays(today, -14), 'yyyy-MM-dd'),
    status: 'interview',
    nextStep: 'Technical Interview Round 2',
    nextStepDate: format(addDays(today, 4), 'yyyy-MM-dd'),
    source: 'LinkedIn',
  },
  {
    id: '2',
    title: 'Full Stack Engineer',
    company: 'StartupXYZ',
    location: 'Remote',
    salary: '$85,000 – $115,000',
    appliedDate: format(addDays(today, -10), 'yyyy-MM-dd'),
    status: 'screening',
    nextStep: 'Phone screen with recruiter',
    nextStepDate: format(addDays(today, 2), 'yyyy-MM-dd'),
    source: 'Indeed',
  },
  {
    id: '3',
    title: 'React Developer',
    company: 'DesignStudio',
    location: 'Austin, TX',
    salary: '$80,000 – $100,000',
    appliedDate: format(addDays(today, -21), 'yyyy-MM-dd'),
    status: 'rejected',
    source: 'Company Website',
    notes: 'Not enough years of experience with Vue.js',
  },
  {
    id: '4',
    title: 'Software Engineer – AI Products',
    company: 'AIFirst Inc',
    location: 'New York, NY',
    salary: '$110,000 – $145,000',
    appliedDate: format(addDays(today, -5), 'yyyy-MM-dd'),
    status: 'applied',
    source: 'Referral',
  },
  {
    id: '5',
    title: 'TypeScript Engineer',
    company: 'FinTech Co',
    location: 'Remote',
    salary: '$100,000 – $130,000',
    appliedDate: format(addDays(today, -3), 'yyyy-MM-dd'),
    status: 'applied',
    source: 'LinkedIn',
  },
];

const statusConfig: Record<Application['status'], { label: string; color: string; icon: React.ComponentType<any> }> = {
  applied: { label: 'Applied', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20', icon: Send },
  screening: { label: 'Screening', color: 'bg-amber-500/10 text-amber-400 border-amber-500/20', icon: Clock },
  interview: { label: 'Interview', color: 'bg-purple-500/10 text-purple-400 border-purple-500/20', icon: Clock },
  offer: { label: 'Offer!', color: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20', icon: CheckCircle },
  rejected: { label: 'Rejected', color: 'bg-destructive/10 text-destructive border-destructive/20', icon: XCircle },
  withdrawn: { label: 'Withdrawn', color: 'bg-muted text-muted-foreground border-border', icon: XCircle },
};

function ApplicationCard({ app }: { app: Application }) {
  const cfg = statusConfig[app.status];
  const Icon = cfg.icon;
  return (
    <Card id={`app-card-${app.id}`} className="border-border/50 hover:border-primary/20 transition-colors">
      <CardContent className="pt-4 pb-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <h3 className="font-semibold text-base">{app.title}</h3>
              <Badge className={`text-xs border ${cfg.color} gap-1`} aria-label={`Status: ${cfg.label}`}>
                <Icon className="h-3 w-3" aria-hidden="true" />
                {cfg.label}
              </Badge>
            </div>
            <div className="flex items-center gap-3 text-sm text-muted-foreground mb-2 flex-wrap">
              <span className="flex items-center gap-1">
                <Building className="h-3.5 w-3.5" />
                {app.company}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {app.location}
              </span>
              <span className="font-medium text-primary text-xs">{app.salary}</span>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Applied {new Date(app.appliedDate).toLocaleDateString()}
              </span>
              <Badge variant="outline" className="text-xs">{app.source}</Badge>
            </div>
            {app.nextStep && (
              <div id={`next-step-${app.id}`} className="mt-3 p-2.5 bg-primary/5 rounded-lg border border-primary/10">
                <p className="text-xs font-medium text-primary">Next: {app.nextStep}</p>
                {app.nextStepDate && (
                  <p className="text-xs text-muted-foreground">
                    {new Date(app.nextStepDate).toLocaleDateString()}
                  </p>
                )}
              </div>
            )}
            {app.notes && (
              <p className="mt-2 text-xs text-muted-foreground italic">{app.notes}</p>
            )}
          </div>
          <Button id={`app-action-${app.id}`} variant="ghost" size="icon" className="flex-shrink-0">
            <ExternalLink className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Applications() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filtered = mockApplications.filter((a) => {
    const matchesSearch =
      a.title.toLowerCase().includes(search.toLowerCase()) ||
      a.company.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || a.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: mockApplications.length,
    active: mockApplications.filter((a) => ['applied', 'screening', 'interview'].includes(a.status)).length,
    interviews: mockApplications.filter((a) => a.status === 'interview').length,
    offers: mockApplications.filter((a) => a.status === 'offer').length,
  };

  const byStatus = (status: Application['status']) => filtered.filter((a) => a.status === status);
  const active = filtered.filter((a) => ['applied', 'screening', 'interview'].includes(a.status));
  const closed = filtered.filter((a) => ['offer', 'rejected', 'withdrawn'].includes(a.status));

  return (
    <div id="applications-container" className="container mx-auto py-8 px-4 max-w-5xl">
      <motion.div id="applications-header" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <FileText className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Applications</h1>
              <p className="text-muted-foreground">Track every job you've applied to</p>
            </div>
          </div>
          <Button id="add-application-btn" className="gap-2">
            <Plus className="h-4 w-4" />
            Add Application
          </Button>
        </div>
      </motion.div>

      {/* Stats */}
      <motion.div id="applications-stats" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Applied', value: stats.total, color: 'text-foreground' },
          { label: 'Active', value: stats.active, color: 'text-blue-400' },
          { label: 'Interviews', value: stats.interviews, color: 'text-purple-400' },
          { label: 'Offers', value: stats.offers, color: 'text-emerald-500' },
        ].map((s, i) => (
          <Card key={i} id={`stat-card-${i}`} className="border-border/50">
            <CardContent className="pt-4 pb-4 text-center">
              <p className={`text-3xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Filters */}
      <motion.div id="applications-filters" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="flex gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="apps-search"
            placeholder="Search by title or company..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger id="status-filter" className="w-40">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="applied">Applied</SelectItem>
            <SelectItem value="screening">Screening</SelectItem>
            <SelectItem value="interview">Interview</SelectItem>
            <SelectItem value="offer">Offer</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </SelectContent>
        </Select>
      </motion.div>

      {/* Application list */}
      <Tabs id="applications-tabs" defaultValue="active">
        <TabsList id="applications-tablist" className="mb-6" aria-label="Application status filter">
          <TabsTrigger value="active">Active ({active.length})</TabsTrigger>
          <TabsTrigger value="closed">Closed ({closed.length})</TabsTrigger>
          <TabsTrigger value="all">All ({filtered.length})</TabsTrigger>
        </TabsList>

        <TabsContent id="tab-active" value="active">
          <div className="space-y-3">
            {active.length === 0 ? (
              <Card className="border-border/50">
                <CardContent className="py-12 text-center">
                  <Send className="h-8 w-8 mx-auto mb-3 text-muted-foreground/30" />
                  <p className="text-muted-foreground">No active applications. Start applying!</p>
                </CardContent>
              </Card>
            ) : (
              active.map((app) => <ApplicationCard key={app.id} app={app} />)
            )}
          </div>
        </TabsContent>

        <TabsContent id="tab-closed" value="closed">
          <div className="space-y-3">
            {closed.length === 0 ? (
              <Card className="border-border/50">
                <CardContent className="py-12 text-center">
                  <p className="text-muted-foreground">No closed applications.</p>
                </CardContent>
              </Card>
            ) : (
              closed.map((app) => <ApplicationCard key={app.id} app={app} />)
            )}
          </div>
        </TabsContent>

        <TabsContent id="tab-all" value="all">
          <div className="space-y-3">
            {filtered.map((app) => <ApplicationCard key={app.id} app={app} />)}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
