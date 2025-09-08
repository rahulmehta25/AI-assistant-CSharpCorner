import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, MapPin, Briefcase, DollarSign, SlidersHorizontal } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { JobCard } from '@/components/jobs/JobCard';
import { mockJobs } from '@/services/api';

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