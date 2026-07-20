import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Bookmark, BookmarkCheck, TrendingUp, DollarSign, GraduationCap } from 'lucide-react';
import { Career } from '@/types';
import { useUserStore } from '@/store/useUserStore';
import { cn } from '@/lib/utils';

interface CareerCardProps {
  career: Career;
  showMatch?: boolean;
  compact?: boolean;
}

export const CareerCard = ({ career, showMatch = true, compact = false }: CareerCardProps) => {
  const { bookmarkedCareers, bookmarkCareer, unbookmarkCareer } = useUserStore();
  const isBookmarked = bookmarkedCareers.some((c) => c.id === career.id);

  const handleBookmark = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (isBookmarked) {
      unbookmarkCareer(career.id);
    } else {
      bookmarkCareer(career);
    }
  };

  const formatSalary = (min: number, max: number) => {
    return `$${(min / 1000).toFixed(0)}k - $${(max / 1000).toFixed(0)}k`;
  };

  const getGrowthColor = (growth: string) => {
    switch (growth) {
      case 'high':
        return 'text-success bg-success/10 border-success/20';
      case 'medium':
        return 'text-warning bg-warning/10 border-warning/20';
      case 'low':
        return 'text-muted-foreground bg-muted/50 border-muted/20';
      default:
        return 'text-muted-foreground bg-muted/50 border-muted/20';
    }
  };

  return (
    <Card className="group transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer">
      <Link to={`/careers/${career.id}`} className="block">
        <CardHeader className={cn('pb-3', compact && 'pb-2')}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className={cn(
                'text-lg font-semibold group-hover:text-primary transition-colors',
                compact && 'text-base'
              )}>
                {career.title}
              </CardTitle>
              {showMatch && career.match && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Match</span>
                    <span className="font-medium text-primary">{career.match}%</span>
                  </div>
                  <Progress value={career.match} className="mt-1 h-2" />
                </div>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBookmark}
              className="ml-2 text-muted-foreground hover:text-primary"
            >
              {isBookmarked ? (
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
              {career.description}
            </p>
          )}

          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="outline" className={getGrowthColor(career.growth)}>
              <TrendingUp className="w-3 h-3 mr-1" />
              {career.growth} growth
            </Badge>
            <Badge variant="outline">
              <DollarSign className="w-3 h-3 mr-1" />
              {formatSalary(career.salary.min, career.salary.max)}
            </Badge>
            <Badge variant="outline">
              <GraduationCap className="w-3 h-3 mr-1" />
              {career.education}
            </Badge>
          </div>

          {!compact && (
            <div className="space-y-2">
              <div>
                <h4 className="text-sm font-medium mb-1">Key Skills</h4>
                <div className="flex flex-wrap gap-1">
                  {career.skills.slice(0, 3).map((skill) => (
                    <Badge key={skill} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                  {career.skills.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{career.skills.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Link>
    </Card>
  );
};