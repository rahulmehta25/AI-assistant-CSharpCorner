import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, SlidersHorizontal } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { CareerCard } from '@/components/careers/CareerCard';
import { mockCareers } from '@/services/api';

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

export default function CareerExplorer() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGrowth, setSelectedGrowth] = useState<string>('');
  const [selectedSalary, setSelectedSalary] = useState<string>('');
  const [selectedEducation, setSelectedEducation] = useState<string>('');

  const filteredCareers = mockCareers.filter((career) => {
    const matchesSearch = career.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         career.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         career.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesGrowth = !selectedGrowth || career.growth === selectedGrowth;
    
    const matchesSalary = !selectedSalary || (() => {
      const minSalary = career.salary.min;
      switch (selectedSalary) {
        case 'entry': return minSalary < 60000;
        case 'mid': return minSalary >= 60000 && minSalary < 100000;
        case 'senior': return minSalary >= 100000;
        default: return true;
      }
    })();
    
    const matchesEducation = !selectedEducation || career.education.toLowerCase().includes(selectedEducation.toLowerCase());
    
    return matchesSearch && matchesGrowth && matchesSalary && matchesEducation;
  });

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedGrowth('');
    setSelectedSalary('');
    setSelectedEducation('');
  };

  const activeFiltersCount = [selectedGrowth, selectedSalary, selectedEducation].filter(Boolean).length;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="space-y-2">
        <h1 className="text-3xl font-bold">Career Explorer</h1>
        <p className="text-muted-foreground text-lg">
          Discover your perfect career path from 100+ opportunities
        </p>
      </motion.div>

      {/* Search and Filters */}
      <motion.div variants={itemVariants} className="space-y-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search careers, skills, or industries..."
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
          <Select value={selectedGrowth} onValueChange={setSelectedGrowth}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Growth" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="high">High Growth</SelectItem>
              <SelectItem value="medium">Medium Growth</SelectItem>
              <SelectItem value="low">Low Growth</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedSalary} onValueChange={setSelectedSalary}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Salary" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="entry">Entry Level</SelectItem>
              <SelectItem value="mid">Mid Level</SelectItem>
              <SelectItem value="senior">Senior Level</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedEducation} onValueChange={setSelectedEducation}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="Education" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="bachelor">Bachelor's Degree</SelectItem>
              <SelectItem value="master">Master's Degree</SelectItem>
              <SelectItem value="associate">Associate Degree</SelectItem>
              <SelectItem value="certificate">Certificate</SelectItem>
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
            Showing {filteredCareers.length} careers
            {searchQuery && ` for "${searchQuery}"`}
          </p>
          
          <Select defaultValue="match">
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="match">Best Match</SelectItem>
              <SelectItem value="salary">Highest Salary</SelectItem>
              <SelectItem value="growth">Growth Rate</SelectItem>
              <SelectItem value="title">A to Z</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </motion.div>

      {/* Career Grid */}
      <motion.div variants={itemVariants}>
        {filteredCareers.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredCareers.map((career, index) => (
              <motion.div
                key={career.id}
                variants={itemVariants}
                transition={{ delay: index * 0.05 }}
              >
                <CareerCard career={career} showMatch />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="mx-auto h-24 w-24 text-muted-foreground/40 mb-4">
              <Search className="h-full w-full" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No careers found</h3>
            <p className="text-muted-foreground mb-4">
              Try adjusting your search terms or filters to find more results.
            </p>
            <Button variant="outline" onClick={clearFilters}>
              Clear All Filters
            </Button>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}