import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, TrendingUp, DollarSign, Briefcase, Clock, Building2, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { apiService } from '@/services/api';
import type { Career } from '@/types';

export default function CareerDetails() {
  const { id } = useParams<{ id: string }>();
  const [career, setCareer] = useState<Career | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (!id) return;
    apiService.getCareerById(id)
      .then((data) => {
        if (data) setCareer(data);
        else setNotFound(true);
      })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div id="career-details-loading" className="container mx-auto py-8 px-4 max-w-3xl space-y-4">
        <div className="h-8 w-48 rounded bg-muted animate-pulse" />
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
      </div>
    );
  }

  if (notFound || !career) {
    return (
      <div id="career-details-not-found" className="container mx-auto py-16 px-4 text-center">
        <h2 className="text-2xl font-bold mb-4">Career Not Found</h2>
        <p className="text-muted-foreground mb-6">The career you are looking for does not exist.</p>
        <Button asChild>
          <Link to="/careers">Back to Career Explorer</Link>
        </Button>
      </div>
    );
  }

  const demandColor = {
    high: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    low: 'bg-muted text-muted-foreground',
  }[career.demandLevel];

  return (
    <div id="career-details-container" className="container mx-auto py-8 px-4 max-w-3xl">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Button asChild variant="ghost" className="mb-6 gap-2 -ml-2">
          <Link to="/careers">
            <ArrowLeft className="h-4 w-4" />
            Back to Careers
          </Link>
        </Button>

        <div id="career-details-header" className="mb-6">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-3xl font-bold mb-1">{career.title}</h1>
              <p className="text-muted-foreground">{career.category}</p>
            </div>
            <Badge className={demandColor} variant="outline">
              {career.demandLevel} demand
            </Badge>
          </div>
        </div>

        <div id="career-details-grid" className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <Card id="career-match-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground">Match Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary mb-2">{career.matchScore}%</div>
              <Progress value={career.matchScore} className="h-2" />
            </CardContent>
          </Card>

          <Card id="career-salary-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
                <DollarSign className="h-3 w-3" /> Salary Range
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xl font-semibold">{career.salaryRange}</div>
              <p className="text-xs text-muted-foreground mt-1">Annual compensation</p>
            </CardContent>
          </Card>

          <Card id="career-growth-card">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
                <TrendingUp className="h-3 w-3" /> Growth Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xl font-semibold text-emerald-500">{career.growthRate}</div>
              <p className="text-xs text-muted-foreground mt-1">Industry growth projection</p>
            </CardContent>
          </Card>

          {career.timeToTransition && (
            <Card id="career-transition-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3 w-3" /> Time to Transition
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-xl font-semibold">{career.timeToTransition}</div>
                <p className="text-xs text-muted-foreground mt-1">Estimated preparation time</p>
              </CardContent>
            </Card>
          )}
        </div>

        <Card id="career-description-card" className="mb-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="h-4 w-4 text-primary" />
              About This Career
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground leading-relaxed">{career.description}</p>
          </CardContent>
        </Card>

        <Card id="career-skills-card" className="mb-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-primary" />
              Key Skills Required
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {career.skills.map((skill) => (
                <Badge key={skill} variant="secondary">{skill}</Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {career.companies && career.companies.length > 0 && (
          <Card id="career-companies-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-4 w-4 text-primary" />
                Top Hiring Companies
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {career.companies.map((company) => (
                  <Badge key={company} variant="outline">{company}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <div id="career-details-actions" className="mt-6 flex gap-3">
          <Button className="flex-1">Start Learning Path</Button>
          <Button variant="outline" asChild>
            <Link to="/jobs">Find Related Jobs</Link>
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
