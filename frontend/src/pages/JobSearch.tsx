import { useState, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Job, JobType, JobSortOption } from '@/types';
import { useUserStore } from '@/store/useUserStore';
import { EmptyState } from '@/components/ui/empty-state';
import { JobCardSkeleton } from '@/components/ui/loading-skeletons';
import {
  Search,
  MapPin,
  Building2,
  Clock,
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  Filter,
  X,
  Briefcase,
  SlidersHorizontal
} from 'lucide-react';
import { cn } from '@/lib/utils';

const mockJobs: Job[] = [
  {
    id: '1',
    title: 'Frontend Developer',
    company: 'TechCorp',
    location: 'San Francisco, CA',
    salary: '$90,000 - $120,000',
    type: 'full-time',
    description: 'Build amazing user interfaces with React and TypeScript. Work on cutting-edge web applications.',
    requirements: ['3+ years React experience', 'TypeScript proficiency', 'CSS expertise'],
    benefits: ['Health insurance', '401k matching', 'Flexible PTO'],
    match: 94,
    postedDate: '2024-01-15',
    applied: false,
    saved: false,
    source: 'LinkedIn',
    remote: false,
  },
  {
    id: '2',
    title: 'Full Stack Engineer',
    company: 'StartupXYZ',
    location: 'Remote',
    salary: '$80,000 - $110,000',
    type: 'full-time',
    description: 'Work on both frontend and backend systems using modern technologies.',
    requirements: ['JavaScript/TypeScript', 'Node.js', 'Database design', 'API development'],
    benefits: ['Remote work', 'Stock options', 'Learning budget'],
    match: 89,
    postedDate: '2024-01-12',
    applied: true,
    saved: true,
    source: 'Indeed',
    remote: true,
  },
  {
    id: '3',
    title: 'Software Engineering Intern',
    company: 'BigTech Inc',
    location: 'Seattle, WA',
    salary: '$35/hour',
    type: 'internship',
    description: 'Summer internship program for computer science students.',
    requirements: ['CS major', 'Programming skills', 'Problem-solving abilities'],
    benefits: ['Mentorship', 'Housing stipend', 'Return offer potential'],
    match: 87,
    postedDate: '2024-01-10',
    applied: false,
    saved: true,
    source: 'Company Website',
    remote: false,
  },
  {
    id: '4',
    title: 'Data Scientist',
    company: 'DataCorp',
    location: 'New York, NY',
    salary: '$100,000 - $140,000',
    type: 'full-time',
    description: 'Analyze complex datasets to drive business insights and build ML models.',
    requirements: ['Python', 'Machine Learning', 'Statistics', 'SQL'],
    benefits: ['Health insurance', '401k', 'Flexible schedule'],
    match: 91,
    postedDate: '2024-01-08',
    applied: false,
    saved: false,
    source: 'Glassdoor',
    remote: false,
  },
  {
    id: '5',
    title: 'UX Designer',
    company: 'DesignStudio',
    location: 'Austin, TX',
    salary: '$75,000 - $95,000',
    type: 'full-time',
    description: 'Create user-centered designs for web and mobile applications.',
    requirements: ['Figma', 'User Research', 'Prototyping', 'Design Systems'],
    benefits: ['Creative environment', 'Professional development', 'Remote options'],
    match: 85,
    postedDate: '2024-01-05',
    applied: false,
    saved: true,
    source: 'Dribbble',
    remote: true,
  },
  {
    id: '6',
    title: 'Backend Engineer',
    company: 'CloudScale',
    location: 'Remote',
    salary: '$95,000 - $130,000',
    type: 'full-time',
    description: 'Design and implement scalable backend services and APIs.',
    requirements: ['Go or Python', 'Kubernetes', 'AWS/GCP', 'System Design'],
    benefits: ['Fully remote', 'Equity', 'Unlimited PTO'],
    match: 82,
    postedDate: '2024-01-03',
    applied: false,
    saved: false,
    source: 'AngelList',
    remote: true,
  },
];

function MatchRing({ percentage }: { percentage: number }) {
  const size = 36;
  const strokeWidth = 3;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center shrink-0">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--primary))"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="ring-progress"
        />
      </svg>
      <span className="absolute text-[10px] font-semibold">{percentage}%</span>
    </div>
  );
}

function JobCard({
  job,
  onSave,
  onUnsave,
  isSaved,
}: {
  job: Job;
  onSave: () => void;
  onUnsave: () => void;
  isSaved: boolean;
}) {
  const daysAgo = Math.floor(
    (Date.now() - new Date(job.postedDate).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <Card className="transition-colors h-full hover-lift">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold truncate">{job.title}</h3>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Building2 className="h-3.5 w-3.5" />
                  <span>{job.company}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {job.match && <MatchRing percentage={job.match} />}
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={isSaved ? onUnsave : onSave}
                >
                  {isSaved ? (
                    <BookmarkCheck className="h-4 w-4 text-primary" />
                  ) : (
                    <Bookmark className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Meta info */}
            <div className="flex flex-wrap items-center gap-3 mb-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                <span>{job.location}</span>
              </div>
              {job.salary && (
                <span className="font-medium text-foreground">{job.salary}</span>
              )}
              <Badge variant="outline" className="text-xs">
                {job.type}
              </Badge>
              {job.remote && (
                <Badge variant="secondary" className="text-xs">
                  Remote
                </Badge>
              )}
            </div>

            {/* Description */}
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
              {job.description}
            </p>

            {/* Requirements */}
            <div className="flex flex-wrap gap-1.5 mb-4">
              {job.requirements.slice(0, 4).map((req) => (
                <Badge key={req} variant="secondary" className="text-xs font-normal">
                  {req}
                </Badge>
              ))}
              {job.requirements.length > 4 && (
                <Badge variant="secondary" className="text-xs font-normal">
                  +{job.requirements.length - 4} more
                </Badge>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>{daysAgo === 0 ? 'Today' : `${daysAgo}d ago`}</span>
                <span className="mx-1">via</span>
                <span>{job.source}</span>
              </div>
              <div className="flex items-center gap-2">
                {job.applied && (
                  <Badge variant="default" className="text-xs">
                    Applied
                  </Badge>
                )}
                <Button variant="outline" size="sm">
                  View Details
                  <ExternalLink className="h-3 w-3 ml-1" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function JobSearch() {
  const { savedJobs, saveJob, unsaveJob } = useUserStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedSalary, setSelectedSalary] = useState<string>('all');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [sortBy, setSortBy] = useState<JobSortOption>('match');
  const [showFilters, setShowFilters] = useState(false);

  const filteredJobs = useMemo(() => {
    let result = [...mockJobs];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (job) =>
          job.title.toLowerCase().includes(query) ||
          job.company.toLowerCase().includes(query) ||
          job.description.toLowerCase().includes(query)
      );
    }

    // Location filter
    if (selectedLocation && selectedLocation !== 'all') {
      result = result.filter((job) =>
        job.location.toLowerCase().includes(selectedLocation.toLowerCase())
      );
    }

    // Type filter
    if (selectedType && selectedType !== 'all') {
      result = result.filter((job) => job.type === selectedType);
    }

    // Salary filter
    if (selectedSalary && selectedSalary !== 'all') {
      result = result.filter((job) => {
        if (!job.salary) return false;
        const salaryNum = parseInt(job.salary.replace(/[^0-9]/g, ''));
        switch (selectedSalary) {
          case 'entry':
            return salaryNum < 70000;
          case 'mid':
            return salaryNum >= 70000 && salaryNum < 120000;
          case 'senior':
            return salaryNum >= 120000;
          default:
            return true;
        }
      });
    }

    // Remote filter
    if (remoteOnly) {
      result = result.filter((job) => job.remote || job.location.toLowerCase() === 'remote');
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'match':
          return (b.match || 0) - (a.match || 0);
        case 'date':
          return new Date(b.postedDate).getTime() - new Date(a.postedDate).getTime();
        case 'salary':
          const salaryA = parseInt((a.salary || '0').replace(/[^0-9]/g, ''));
          const salaryB = parseInt((b.salary || '0').replace(/[^0-9]/g, ''));
          return salaryB - salaryA;
        case 'company':
          return a.company.localeCompare(b.company);
        default:
          return 0;
      }
    });

    return result;
  }, [searchQuery, selectedLocation, selectedType, selectedSalary, remoteOnly, sortBy]);

  const activeFiltersCount = [
    selectedLocation !== 'all' && selectedLocation,
    selectedType !== 'all' && selectedType,
    selectedSalary !== 'all' && selectedSalary,
    remoteOnly,
  ].filter(Boolean).length;

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedLocation('all');
    setSelectedType('all');
    setSelectedSalary('all');
    setRemoteOnly(false);
  };

  const isJobSaved = (jobId: string) => savedJobs.some((j) => j.id === jobId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="animate-fade-in-up">
        <h1 className="text-2xl font-semibold gradient-text">
          Find Jobs
        </h1>
        <p className="text-muted-foreground mt-1">
          {filteredJobs.length} jobs matching your profile
        </p>
      </div>

      {/* Search & Filters */}
      <div className="space-y-4 animate-fade-in-up stagger-1">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search jobs, companies, skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className={cn(showFilters && 'bg-muted')}
          >
            <SlidersHorizontal className="h-4 w-4 mr-2" />
            Filters
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>
          <Select value={sortBy} onValueChange={(v) => setSortBy(v as JobSortOption)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="match">Best Match</SelectItem>
              <SelectItem value="date">Most Recent</SelectItem>
              <SelectItem value="salary">Highest Salary</SelectItem>
              <SelectItem value="company">Company A-Z</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <Card className="animate-fade-in-scale">
            <CardContent className="p-4">
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div className="space-y-2">
                  <Label className="text-sm">Location</Label>
                  <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any location" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any location</SelectItem>
                      <SelectItem value="san francisco">San Francisco</SelectItem>
                      <SelectItem value="seattle">Seattle</SelectItem>
                      <SelectItem value="new york">New York</SelectItem>
                      <SelectItem value="austin">Austin</SelectItem>
                      <SelectItem value="remote">Remote</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm">Job Type</Label>
                  <Select value={selectedType} onValueChange={setSelectedType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any type</SelectItem>
                      <SelectItem value="full-time">Full-time</SelectItem>
                      <SelectItem value="part-time">Part-time</SelectItem>
                      <SelectItem value="contract">Contract</SelectItem>
                      <SelectItem value="internship">Internship</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm">Salary Range</Label>
                  <Select value={selectedSalary} onValueChange={setSelectedSalary}>
                    <SelectTrigger>
                      <SelectValue placeholder="Any salary" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Any salary</SelectItem>
                      <SelectItem value="entry">Under $70k</SelectItem>
                      <SelectItem value="mid">$70k - $120k</SelectItem>
                      <SelectItem value="senior">$120k+</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-sm">Options</Label>
                  <div className="flex items-center space-x-2 pt-2">
                    <Checkbox
                      id="remote"
                      checked={remoteOnly}
                      onCheckedChange={(checked) => setRemoteOnly(checked === true)}
                    />
                    <Label htmlFor="remote" className="text-sm font-normal cursor-pointer">
                      Remote only
                    </Label>
                  </div>
                </div>
              </div>

              {activeFiltersCount > 0 && (
                <div className="flex justify-end mt-4 pt-4 border-t">
                  <Button variant="ghost" size="sm" onClick={clearFilters}>
                    <X className="h-4 w-4 mr-1" />
                    Clear filters
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Job List */}
      {filteredJobs.length > 0 ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {filteredJobs.map((job, index) => (
            <div
              key={job.id}
              className="animate-fade-in-up"
              style={{ animationDelay: `${index * 60}ms` }}
            >
              <JobCard
                job={job}
                isSaved={isJobSaved(job.id)}
                onSave={() => saveJob(job)}
                onUnsave={() => unsaveJob(job.id)}
              />
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Briefcase}
          title="No jobs found"
          description="Try adjusting your search or filters to find more results."
          action={{ label: 'Clear filters', onClick: clearFilters }}
        />
      )}

      {/* Stats Footer */}
      <Card className="animate-fade-in-up stagger-6">
        <CardContent className="p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-semibold">{mockJobs.length}</div>
              <div className="text-xs text-muted-foreground">Total Jobs</div>
            </div>
            <div>
              <div className="text-2xl font-semibold">
                {mockJobs.filter((j) => {
                  const daysAgo = Math.floor(
                    (Date.now() - new Date(j.postedDate).getTime()) / (1000 * 60 * 60 * 24)
                  );
                  return daysAgo <= 7;
                }).length}
              </div>
              <div className="text-xs text-muted-foreground">New This Week</div>
            </div>
            <div>
              <div className="text-2xl font-semibold">
                {mockJobs.filter((j) => j.applied).length}
              </div>
              <div className="text-xs text-muted-foreground">Applied</div>
            </div>
            <div>
              <div className="text-2xl font-semibold">{savedJobs.length}</div>
              <div className="text-xs text-muted-foreground">Saved</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
