import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, MapPin, Briefcase, SlidersHorizontal, Bookmark, BookmarkCheck,
  Building, Clock, DollarSign, ExternalLink, X,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { JobMatchRing } from '@/components/ui/job-match-ring';
import { SkeletonJobCard } from '@/components/ui/skeleton-card';
import type { Job } from '@/types';
import { useUserStore } from '@/store/useUserStore';

/* ── Mock data ──────────────────────────────────────────── */
const mockJobs: Job[] = [
  {
    id: '1', title: 'Frontend Developer', company: 'TechCorp',
    location: 'San Francisco, CA', salary: '$90k – $120k', type: 'full-time',
    description: 'Build stunning UIs with React and TypeScript in a fast-paced product team.',
    requirements: ['3+ yrs React', 'TypeScript', 'CSS expertise', 'REST APIs'],
    benefits: ['Health insurance', '401k matching', 'Flexible PTO', 'Home office budget'],
    match: 94, postedDate: '2024-01-15', applied: false, saved: false, source: 'LinkedIn',
  },
  {
    id: '2', title: 'Full Stack Engineer', company: 'StartupXYZ',
    location: 'Remote', salary: '$80k – $110k', type: 'full-time',
    description: 'Own full product features end-to-end across React frontend and Node.js backend.',
    requirements: ['TypeScript', 'Node.js', 'PostgreSQL', 'API design'],
    benefits: ['Remote-first', 'Stock options', 'Learning budget', 'Async culture'],
    match: 89, postedDate: '2024-01-12', applied: true, saved: true, source: 'Indeed',
  },
  {
    id: '3', title: 'Software Engineering Intern', company: 'BigTech Inc',
    location: 'Seattle, WA', salary: '$35/hr', type: 'internship',
    description: 'Summer internship with structured mentorship and return offer potential.',
    requirements: ['CS major', 'Data structures', 'Problem-solving'],
    benefits: ['Mentorship', 'Housing stipend', 'Full-time conversion'],
    match: 87, postedDate: '2024-01-10', applied: false, saved: true, source: 'Company',
  },
  {
    id: '4', title: 'Data Scientist', company: 'DataCorp',
    location: 'New York, NY', salary: '$100k – $140k', type: 'full-time',
    description: 'Build ML pipelines and deliver insights that drive $10M+ decisions.',
    requirements: ['Python', 'Machine Learning', 'Statistics', 'SQL'],
    benefits: ['Health & dental', '401k', 'Flexible schedule', 'Conference budget'],
    match: 91, postedDate: '2024-01-08', applied: false, saved: false, source: 'Glassdoor',
  },
  {
    id: '5', title: 'UX Designer', company: 'DesignStudio',
    location: 'Austin, TX', salary: '$75k – $95k', type: 'full-time',
    description: 'Shape user experiences for mobile and web applications serving millions.',
    requirements: ['Figma', 'User Research', 'Prototyping', 'Design Systems'],
    benefits: ['Creative studio', 'Pro development', 'Partial remote'],
    match: 85, postedDate: '2024-01-05', applied: false, saved: true, source: 'Dribbble',
  },
  {
    id: '6', title: 'Backend Engineer', company: 'ScaleCo',
    location: 'Remote', salary: '$105k – $135k', type: 'full-time',
    description: 'Scale our infrastructure to handle 100M+ monthly requests.',
    requirements: ['Go or Rust', 'Distributed systems', 'Kubernetes', 'PostgreSQL'],
    benefits: ['Remote', 'Equity', 'Unlimited PTO', 'Top-of-market comp'],
    match: 77, postedDate: '2024-01-03', applied: false, saved: false, source: 'LinkedIn',
  },
];

/* ── Helpers ────────────────────────────────────────────── */
function formatDate(dateString: string): string {
  const diff = Math.ceil((Date.now() - new Date(dateString).getTime()) / 86_400_000);
  if (diff <= 1) return 'Today';
  if (diff < 7) return `${diff}d ago`;
  if (diff < 30) return `${Math.ceil(diff / 7)}w ago`;
  return `${Math.ceil(diff / 30)}mo ago`;
}

function typeColor(type: string) {
  const map: Record<string, string> = {
    'full-time':  'border-emerald-500/30 text-emerald-400',
    'part-time':  'border-amber-500/30 text-amber-400',
    'contract':   'border-violet-500/30 text-violet-400',
    'internship': 'border-blue-500/30 text-blue-400',
  };
  return map[type] ?? 'border-border text-muted-foreground';
}

/* ── Job card ───────────────────────────────────────────── */
const JobCardEnhanced = ({ job }: { job: Job }) => {
  const { savedJobs, saveJob, unsaveJob } = useUserStore();
  const isSaved = savedJobs.some((j) => j.id === job.id);
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      id={`job-card-${job.id}`}
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-border/50 bg-card/80 hover:border-primary/25 hover:shadow-lg transition-all duration-300 group">
        <CardContent className="pt-4 pb-4">
          <div className="flex items-start gap-3">
            {/* Match ring */}
            <JobMatchRing
              percentage={job.match ?? 0}
              size={64}
              strokeWidth={5}
              className="flex-shrink-0 mt-0.5"
            />

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <h3 className="font-bold text-foreground group-hover:text-primary transition-colors truncate">
                    {job.title}
                  </h3>
                  <div className="flex items-center gap-1.5 mt-0.5 text-sm text-muted-foreground">
                    <Building className="h-3.5 w-3.5 flex-shrink-0" />
                    <span>{job.company}</span>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => isSaved ? unsaveJob(job.id) : saveJob(job)}
                  className="h-8 w-8 p-0 flex-shrink-0 text-muted-foreground hover:text-primary"
                  aria-label={isSaved ? 'Unsave job' : 'Save job'}
                >
                  {isSaved
                    ? <BookmarkCheck className="h-4 w-4 text-primary" />
                    : <Bookmark className="h-4 w-4" />}
                </Button>
              </div>

              {/* Meta badges */}
              <div className="flex flex-wrap items-center gap-1.5 mt-2">
                <Badge variant="outline" className={`text-xs ${typeColor(job.type)}`}>
                  {job.type.replace('-', ' ')}
                </Badge>
                <Badge variant="outline" className="text-xs border-border/60 text-muted-foreground">
                  <MapPin className="h-2.5 w-2.5 mr-1" />{job.location}
                </Badge>
                {job.salary && (
                  <Badge variant="outline" className="text-xs border-border/60 text-muted-foreground">
                    <DollarSign className="h-2.5 w-2.5 mr-1" />{job.salary}
                  </Badge>
                )}
                <Badge variant="outline" className="text-xs border-border/60 text-muted-foreground">
                  <Clock className="h-2.5 w-2.5 mr-1" />{formatDate(job.postedDate)}
                </Badge>
              </div>

              {/* Description */}
              <p className="text-xs text-muted-foreground mt-2 line-clamp-2 leading-relaxed">
                {job.description}
              </p>

              {/* Expandable requirements */}
              <AnimatePresence>
                {expanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="mt-3 space-y-2.5"
                  >
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground mb-1.5">Key requirements</p>
                      <div className="flex flex-wrap gap-1">
                        {job.requirements?.map((r) => (
                          <Badge key={r} variant="secondary" className="text-xs">{r}</Badge>
                        ))}
                      </div>
                    </div>
                    {job.benefits && job.benefits.length > 0 && (
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground mb-1.5">Benefits</p>
                        <div className="flex flex-wrap gap-1">
                          {job.benefits.map((b) => (
                            <Badge key={b} variant="outline" className="text-xs border-border/60 text-muted-foreground">{b}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Actions */}
              <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-border/40">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setExpanded(!expanded)}
                    className="text-xs text-muted-foreground hover:text-primary transition-colors"
                  >
                    {expanded ? 'Show less' : 'Show details'}
                  </button>
                  {job.applied && (
                    <Badge variant="default" className="text-[10px] h-4 px-1.5 bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                      Applied
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-muted-foreground/60">via {job.source}</span>
                  <Button
                    size="sm"
                    className="h-7 px-3 text-xs bg-gradient-primary hover:opacity-90 border-0 text-white gap-1.5"
                  >
                    Apply <ExternalLink className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

/* ── Main page ──────────────────────────────────────────── */
export default function JobSearch() {
  const [searchQuery, setSearchQuery]     = useState('');
  const [selectedLocation, setLocation]   = useState('');
  const [selectedType, setType]           = useState('');
  const [selectedSalary, setSalary]       = useState('');
  const [loading]                         = useState(false);

  const filtered = mockJobs.filter((job) => {
    const q = searchQuery.toLowerCase();
    const matchSearch = !q || job.title.toLowerCase().includes(q) ||
                        job.company.toLowerCase().includes(q) ||
                        (job.description ?? '').toLowerCase().includes(q);
    const matchLoc  = !selectedLocation || job.location.toLowerCase().includes(selectedLocation.toLowerCase());
    const matchType = !selectedType || job.type === selectedType;
    const matchSal  = !selectedSalary || (() => {
      const n = parseInt(job.salary?.replace(/\D/g, '') || '0');
      return selectedSalary === 'entry' ? n < 70000 :
             selectedSalary === 'mid'   ? n >= 70000 && n < 120000 :
                                          n >= 120000;
    })();
    return matchSearch && matchLoc && matchType && matchSal;
  });

  const activeFilters = [selectedLocation, selectedType, selectedSalary].filter(Boolean).length;

  const clearFilters = () => {
    setSearchQuery('');
    setLocation('');
    setType('');
    setSalary('');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.06 } },
  };

  return (
    <motion.div
      id="job-search-container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 max-w-5xl"
    >
      {/* ── Header ──────────────────────────────────────── */}
      <motion.div
        variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
        className="space-y-1"
      >
        <h1 className="text-2xl font-extrabold tracking-tight">Job Search</h1>
        <p className="text-muted-foreground text-sm">
          AI-matched opportunities ranked by fit with your profile
        </p>
      </motion.div>

      {/* ── Search + filters ────────────────────────────── */}
      <motion.div
        id="job-filters"
        variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0 } }}
        className="space-y-3"
      >
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            <Input
              id="job-search-input"
              placeholder="Search by title, company, or keyword…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 bg-muted/40 border-border/50 focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/30"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          {activeFilters > 0 && (
            <Button variant="ghost" onClick={clearFilters} className="text-muted-foreground gap-2 text-sm">
              <X className="h-4 w-4" />
              Clear ({activeFilters})
            </Button>
          )}
        </div>

        {/* Filter row */}
        <div id="job-filter-row" className="flex flex-wrap gap-2">
          {[
            {
              value: selectedLocation, onChange: setLocation,
              placeholder: 'Location', id: 'filter-location',
              options: [
                ['san francisco', 'San Francisco'],
                ['seattle', 'Seattle'],
                ['remote', 'Remote'],
                ['new york', 'New York'],
                ['austin', 'Austin'],
              ],
            },
            {
              value: selectedType, onChange: setType,
              placeholder: 'Job Type', id: 'filter-type',
              options: [
                ['full-time', 'Full-time'],
                ['part-time', 'Part-time'],
                ['contract', 'Contract'],
                ['internship', 'Internship'],
              ],
            },
            {
              value: selectedSalary, onChange: setSalary,
              placeholder: 'Salary', id: 'filter-salary',
              options: [
                ['entry', '< $70k'],
                ['mid', '$70k – $120k'],
                ['senior', '$120k+'],
              ],
            },
          ].map(({ value, onChange, placeholder, id, options }) => (
            <Select key={id} value={value} onValueChange={onChange}>
              <SelectTrigger
                id={id}
                className="w-[140px] h-9 text-sm bg-muted/40 border-border/50 focus:border-primary/50"
              >
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
              <SelectContent>
                {options.map(([val, label]) => (
                  <SelectItem key={val} value={val}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          ))}

          <div className="flex-1" />

          <Select defaultValue="match">
            <SelectTrigger id="sort-select" className="w-[140px] h-9 text-sm bg-muted/40 border-border/50">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="match">Best Match</SelectItem>
              <SelectItem value="date">Most Recent</SelectItem>
              <SelectItem value="salary">Highest Salary</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Results count */}
        <p id="job-results-count" className="text-xs text-muted-foreground">
          Showing <span className="font-semibold text-foreground">{filtered.length}</span> of{' '}
          {mockJobs.length} jobs{searchQuery && ` for "${searchQuery}"`}
        </p>
      </motion.div>

      {/* ── Job cards ───────────────────────────────────── */}
      <div id="job-cards-grid">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => <SkeletonJobCard key={i} />)}
          </div>
        ) : filtered.length > 0 ? (
          <AnimatePresence mode="popLayout">
            <div className="space-y-4">
              {filtered.map((job) => (
                <JobCardEnhanced key={job.id} job={job} />
              ))}
            </div>
          </AnimatePresence>
        ) : (
          <motion.div
            id="job-empty-state"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-16 space-y-3"
          >
            <div className="h-16 w-16 rounded-2xl bg-muted/40 flex items-center justify-center mx-auto">
              <Briefcase className="h-8 w-8 text-muted-foreground/40" />
            </div>
            <h3 className="text-lg font-semibold">No jobs found</h3>
            <p className="text-muted-foreground text-sm max-w-xs mx-auto">
              Try adjusting your search terms or filters.
            </p>
            <Button variant="outline" onClick={clearFilters} className="mt-2">
              Clear All Filters
            </Button>
          </motion.div>
        )}
      </div>

      {/* ── Quick stats footer ──────────────────────────── */}
      <motion.div
        id="job-stats-footer"
        variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
        className="grid grid-cols-2 sm:grid-cols-4 gap-3"
      >
        {[
          { label: 'Total Jobs',    value: '2,847', color: 'text-primary' },
          { label: 'New This Week', value: '156',   color: 'text-emerald-400' },
          { label: 'Applications',  value: '43',    color: 'text-amber-400' },
          { label: 'Interviews',    value: '12',    color: 'text-violet-400' },
        ].map(({ label, value, color }) => (
          <div key={label} id={`stat-${label.replace(/\s/g,'-').toLowerCase()}`} className="p-4 rounded-xl border border-border/40 bg-card/60 text-center">
            <p className={`text-2xl font-extrabold ${color}`}>{value}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{label}</p>
          </div>
        ))}
      </motion.div>
    </motion.div>
  );
}
