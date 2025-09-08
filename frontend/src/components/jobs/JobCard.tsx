import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Bookmark, BookmarkCheck, MapPin, Building, Clock, DollarSign } from 'lucide-react';
import { Job } from '@/types';
import { useUserStore } from '@/store/useUserStore';
import { cn } from '@/lib/utils';

interface JobCardProps {
  job: Job;
  showMatch?: boolean;
  compact?: boolean;
}

export const JobCard = ({ job, showMatch = true, compact = false }: JobCardProps) => {
  const { savedJobs, saveJob, unsaveJob } = useUserStore();
  const isSaved = savedJobs.some((j) => j.id === job.id);

  const handleSave = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isSaved) {
      unsaveJob(job.id);
    } else {
      saveJob(job);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'full-time':
        return 'bg-success/10 text-success border-success/20';
      case 'part-time':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'contract':
        return 'bg-secondary/10 text-secondary border-secondary/20';
      case 'internship':
        return 'bg-primary/10 text-primary border-primary/20';
      default:
        return 'bg-muted/50 text-muted-foreground border-muted/20';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
  };

  return (
    <Card className="group transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer">
      <Link to={`/jobs/${job.id}`} className="block">
        <CardHeader className={cn('pb-3', compact && 'pb-2')}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className={cn(
                'text-lg font-semibold group-hover:text-primary transition-colors line-clamp-2',
                compact && 'text-base'
              )}>
                {job.title}
              </CardTitle>
              <div className="flex items-center space-x-2 mt-1 text-sm text-muted-foreground">
                <Building className="h-4 w-4" />
                <span className="font-medium">{job.company}</span>
              </div>
              {showMatch && job.match && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Match</span>
                    <span className="font-medium text-primary">{job.match}%</span>
                  </div>
                  <Progress value={job.match} className="mt-1 h-2" />
                </div>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSave}
              className="ml-2 text-muted-foreground hover:text-primary"
            >
              {isSaved ? (
                <BookmarkCheck className="h-4 w-4 text-primary" />
              ) : (
                <Bookmark className="h-4 w-4" />
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className={cn('pt-0', compact && 'pt-0')}>
          {!compact && (
            <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
              {job.description}
            </p>
          )}

          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="outline" className={getTypeColor(job.type)}>
              {job.type.replace('-', ' ')}
            </Badge>
            <Badge variant="outline">
              <MapPin className="w-3 h-3 mr-1" />
              {job.location}
            </Badge>
            {job.salary && (
              <Badge variant="outline">
                <DollarSign className="w-3 h-3 mr-1" />
                {job.salary}
              </Badge>
            )}
            <Badge variant="outline">
              <Clock className="w-3 h-3 mr-1" />
              {formatDate(job.postedDate)}
            </Badge>
          </div>

          {!compact && job.requirements && (
            <div className="space-y-2">
              <div>
                <h4 className="text-sm font-medium mb-1">Key Requirements</h4>
                <div className="flex flex-wrap gap-1">
                  {job.requirements.slice(0, 3).map((req, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {req}
                    </Badge>
                  ))}
                  {job.requirements.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{job.requirements.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between mt-4 pt-3 border-t">
            <div className="flex space-x-2">
              {job.applied && (
                <Badge variant="default" className="text-xs">
                  Applied
                </Badge>
              )}
              {job.saved && (
                <Badge variant="outline" className="text-xs">
                  Saved
                </Badge>
              )}
            </div>
            <span className="text-xs text-muted-foreground">
              via {job.source}
            </span>
          </div>
        </CardContent>
      </Link>
    </Card>
  );
};