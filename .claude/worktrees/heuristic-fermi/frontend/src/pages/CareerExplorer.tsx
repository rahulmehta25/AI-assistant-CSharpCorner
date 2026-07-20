import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { TrendingUp, Search, ArrowRight, Briefcase } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { apiService } from '@/services/api';
import type { Career } from '@/types';

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};
const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function CareerExplorer() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    apiService.getCareers()
      .then(setCareers)
      .catch((err) => {
        console.error(err);
        setError(true);
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = careers.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase()) ||
    c.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div id="career-explorer-container" className="container mx-auto py-8 px-4 max-w-5xl">
      <motion.div
        id="career-explorer-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-3xl font-bold">Career Explorer</h1>
        </div>
        <p className="text-muted-foreground">Discover career paths matched to your skills and interests.</p>
      </motion.div>

      <div id="career-explorer-search" className="relative mb-6">
        <label htmlFor="career-search-input" className="sr-only">Search careers</label>
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          id="career-search-input"
          placeholder="Search careers..."
          className="pl-10"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div id="career-loading" className="grid grid-cols-1 md:grid-cols-2 gap-4" aria-label="Loading careers" aria-busy="true">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-48 rounded-xl bg-muted animate-pulse" aria-hidden="true" />
          ))}
        </div>
      ) : error ? (
        <div id="career-error" className="text-center py-16">
          <TrendingUp className="h-10 w-10 mx-auto mb-3 text-muted-foreground opacity-30" />
          <p className="text-base font-medium text-foreground mb-1">Unable to load careers</p>
          <p className="text-sm text-muted-foreground">There was a problem fetching career data. Please try refreshing the page.</p>
        </div>
      ) : (
        <motion.div
          id="careers-grid"
          variants={container}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          {filtered.map((career) => (
            <motion.div key={career.id} variants={item}>
              <Card id={`career-card-${career.id}`} className="hover:border-primary/50 transition-colors">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <CardTitle className="text-lg">{career.title}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">{career.category}</p>
                    </div>
                    <Badge variant="secondary" className="shrink-0">
                      {career.matchScore}% match
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground line-clamp-2">{career.description}</p>
                  <div
                    id={`career-match-${career.id}`}
                    role="progressbar"
                    aria-valuenow={career.matchScore}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`Match score: ${career.matchScore}%`}
                  >
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground">Match score</span>
                      <span className="font-medium">{career.matchScore}%</span>
                    </div>
                    <Progress value={career.matchScore} className="h-1.5" />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Briefcase className="h-3 w-3" />
                      <span>{career.salaryRange}</span>
                    </div>
                    <Button asChild size="sm" variant="ghost" className="h-7 gap-1">
                      <Link to={`/careers/${career.id}`}>
                        Details <ArrowRight className="h-3 w-3" />
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}

      {!loading && filtered.length === 0 && (
        <div id="career-empty" className="text-center py-16 text-muted-foreground">
          No careers found matching your search.
        </div>
      )}
    </div>
  );
}
