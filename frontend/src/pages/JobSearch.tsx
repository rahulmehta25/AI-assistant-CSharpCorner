import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, MapPin, Briefcase, DollarSign, SlidersHorizontal } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { JobCard } from '@/components/jobs/JobCard';
import { Job } from '@/types';

// Mock jobs data for now (since jobs endpoint doesn't exist yet)
const mockJobs: Job[] = [
  {
    id: '1',
    title: 'Frontend Developer',
    company: 'TechCorp',
    location: 'San Francisco, CA',
    salary: '$90,000 - $120,000',
    type: 'full-time',
    description: 'Build amazing user interfaces with React and TypeScript.',
    requirements: ['3+ years React experience', 'TypeScript proficiency', 'CSS expertise'],
    benefits: ['Health insurance', '401k matching', 'Flexible PTO'],
    match: 94,
    postedDate: '2024-01-15',
    applied: false,
    saved: false,
    source: 'LinkedIn',
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
  },
  {
    id: '4',
    title: 'Data Scientist',
    company: 'DataCorp',
    location: 'New York, NY',
    salary: '$100,000 - $140,000',
    type: 'full-time',
    description: 'Analyze complex datasets to drive business insights.',
    requirements: ['Python', 'Machine Learning', 'Statistics', 'SQL'],
    benefits: ['Health insurance', '401k', 'Flexible schedule'],
    match: 91,
    postedDate: '2024-01-08',
    applied: false,
    saved: false,
    source: 'Glassdoor',
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
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

export default function JobSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [selectedSalary, setSelectedSalary] = useState<string>('');

  const filteredJobs = mockJobs.filter((job) => {
    const matchesSearch = job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesLocation = !selectedLocation || job.location.toLowerCase().includes(selectedLocation.toLowerCase());
    const matchesType = !selectedType || job.type === selectedType;
    
    const matchesSalary = !selectedSalary || (() => {
      if (!job.salary) return false;
      const salaryNum = parseInt(job.salary.replace(/[^0-9]/g, ''));
      switch (selectedSalary) {
        case 'entry': return salaryNum < 70000;
        case 'mid': return salaryNum >= 70000 && salaryNum < 120000;
        case 'senior': return salaryNum >= 120000;
        default: return true;
      }
    })();
    
    return matchesSearch && matchesLocation && matchesType && matchesSalary;
  });

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedLocation('');
    setSelectedType('');
    setSelectedSalary('');
  };

  const activeFiltersCount = [selectedLocation, selectedType, selectedSalary].filter(Boolean).length;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="space-y-2">
        <h1 className="text-3xl font-bold">Job Search</h1>
        <p className="text-muted-foreground text-lg">
          Find your next opportunity from thousands of job listings
        </p>
      </motion.div>

      {/* Search and Filters */}
      <motion.div variants={itemVariants} className="space-y-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search jobs, companies, or keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button variant="outline" className="flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4" />
            Filters
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-1">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>
        </div>

        {/* Filter Bar */}
        <div className="flex flex-wrap gap-3">
          <Select value={selectedLocation} onValueChange={setSelectedLocation}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Location" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="san francisco">San Francisco</SelectItem>
              <SelectItem value="seattle">Seattle</SelectItem>
              <SelectItem value="remote">Remote</SelectItem>
              <SelectItem value="new york">New York</SelectItem>
              <SelectItem value="austin">Austin</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedType} onValueChange={setSelectedType}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Job Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="full-time">Full-time</SelectItem>
              <SelectItem value="part-time">Part-time</SelectItem>
              <SelectItem value="contract">Contract</SelectItem>
              <SelectItem value="internship">Internship</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedSalary} onValueChange={setSelectedSalary}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Salary" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="entry">$50k - $70k</SelectItem>
              <SelectItem value="mid">$70k - $120k</SelectItem>
              <SelectItem value="senior">$120k+</SelectItem>
            </SelectContent>
          </Select>

          {activeFiltersCount > 0 && (
            <Button variant="ghost" onClick={clearFilters} className="text-muted-foreground">
              Clear Filters
            </Button>
          )}
        </div>

        {/* Results Count */}
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {filteredJobs.length} jobs
            {searchQuery && ` for "${searchQuery}"`}
          </p>
          
          <Select defaultValue="match">
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
      </motion.div>

      {/* Jobs Grid */}
      <motion.div variants={itemVariants}>
        {filteredJobs.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2">
            {filteredJobs.map((job, index) => (
              <motion.div
                key={job.id}
                variants={itemVariants}
                transition={{ delay: index * 0.05 }}
              >
                <JobCard job={job} showMatch />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto h-24 w-24 text-muted-foreground/40 mb-4">
              <Briefcase className="h-full w-full" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No jobs found</h3>
            <p className="text-muted-foreground mb-4">
              Try adjusting your search terms or filters to find more results.
            </p>
            <Button variant="outline" onClick={clearFilters}>
              Clear All Filters
            </Button>
          </div>
        )}
      </motion.div>

      {/* Quick Stats */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-4">
        <div className="bg-card rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold text-primary">2,847</div>
          <div className="text-sm text-muted-foreground">Total Jobs</div>
        </div>
        <div className="bg-card rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold text-success">156</div>
          <div className="text-sm text-muted-foreground">New This Week</div>
        </div>
        <div className="bg-card rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold text-warning">43</div>
          <div className="text-sm text-muted-foreground">Applications Sent</div>
        </div>
        <div className="bg-card rounded-lg border p-4 text-center">
          <div className="text-2xl font-bold text-secondary">12</div>
          <div className="text-sm text-muted-foreground">Interviews</div>
        </div>
      </motion.div>
    </motion.div>
  );
}