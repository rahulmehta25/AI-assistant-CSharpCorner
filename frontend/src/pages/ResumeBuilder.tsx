import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import {
  Upload,
  FileText,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Download,
  User,
  Mail,
  Briefcase,
  GraduationCap,
  Code,
  RefreshCw,
  X,
} from 'lucide-react';
import type { ParsedResume, ResumeSuggestion, WorkExperience, Education } from '@/types';

type UploadState = 'idle' | 'uploading' | 'processing' | 'complete' | 'error';

const mockParsedResume: ParsedResume = {
  name: 'Sarah Chen',
  email: 'sarah.chen@email.com',
  phone: '(555) 123-4567',
  location: 'San Francisco, CA',
  summary: 'Full-stack software engineer with 5+ years of experience building scalable web applications. Passionate about clean code, user experience, and mentoring junior developers.',
  experience: [
    {
      company: 'TechCorp Inc.',
      title: 'Senior Software Engineer',
      location: 'San Francisco, CA',
      startDate: '2021-03',
      current: true,
      description: [
        'Led development of customer-facing dashboard serving 50k+ daily users',
        'Reduced API response times by 40% through query optimization',
        'Mentored 3 junior engineers through code reviews and pair programming',
      ],
    },
    {
      company: 'StartupXYZ',
      title: 'Software Engineer',
      location: 'Remote',
      startDate: '2019-06',
      endDate: '2021-02',
      description: [
        'Built real-time notification system using WebSockets',
        'Implemented CI/CD pipeline reducing deployment time by 60%',
        'Collaborated with design team to improve mobile responsiveness',
      ],
    },
  ],
  education: [
    {
      institution: 'University of California, Berkeley',
      degree: 'Bachelor of Science',
      field: 'Computer Science',
      endDate: '2019',
      gpa: '3.7',
    },
  ],
  skills: ['React', 'TypeScript', 'Node.js', 'Python', 'PostgreSQL', 'AWS', 'Docker', 'GraphQL'],
  certifications: ['AWS Solutions Architect Associate', 'Google Cloud Professional'],
  projects: [
    {
      name: 'Open Source Contribution',
      description: 'Active contributor to React Query library',
      technologies: ['React', 'TypeScript'],
      url: 'https://github.com/tanstack/query',
    },
  ],
};

const mockSuggestions: ResumeSuggestion[] = [
  {
    id: '1',
    section: 'summary',
    type: 'improvement',
    message: 'Add quantifiable achievements to your summary. Consider including metrics like "increased revenue by X%" or "managed team of Y engineers".',
  },
  {
    id: '2',
    section: 'experience',
    type: 'success',
    message: 'Excellent use of action verbs and quantified results in your work experience section.',
  },
  {
    id: '3',
    section: 'skills',
    type: 'warning',
    message: 'Consider adding more soft skills like "Leadership" or "Communication" to balance technical skills.',
  },
  {
    id: '4',
    section: 'experience',
    type: 'improvement',
    message: 'Include specific technologies used in each role to improve ATS keyword matching.',
  },
  {
    id: '5',
    section: 'education',
    type: 'success',
    message: 'GPA is well above average and appropriately included.',
  },
  {
    id: '6',
    section: 'summary',
    type: 'warning',
    message: 'Summary could be more targeted. Consider tailoring it to specific job roles you are applying for.',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function ResumeBuilder() {
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [isDragOver, setIsDragOver] = useState(false);
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null);
  const [suggestions, setSuggestions] = useState<ResumeSuggestion[]>([]);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [fileName, setFileName] = useState<string>('');

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const simulateUpload = useCallback((file: File) => {
    setFileName(file.name);
    setUploadState('uploading');

    setTimeout(() => {
      setUploadState('processing');
      setTimeout(() => {
        setParsedResume(mockParsedResume);
        setSuggestions(mockSuggestions);
        setAtsScore(78);
        setUploadState('complete');
      }, 1500);
    }, 1000);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && (file.type === 'application/pdf' || file.name.endsWith('.docx'))) {
      simulateUpload(file);
    }
  }, [simulateUpload]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      simulateUpload(file);
    }
  }, [simulateUpload]);

  const handleReset = useCallback(() => {
    setUploadState('idle');
    setParsedResume(null);
    setSuggestions([]);
    setAtsScore(null);
    setFileName('');
  }, []);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Work';
  };

  const getSuggestionIcon = (type: ResumeSuggestion['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-emerald-600" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-amber-600" />;
      case 'improvement':
        return <Lightbulb className="h-4 w-4 text-blue-600" />;
    }
  };

  const getSuggestionStyle = (type: ResumeSuggestion['type']) => {
    switch (type) {
      case 'success':
        return 'border-l-emerald-500 bg-emerald-50';
      case 'warning':
        return 'border-l-amber-500 bg-amber-50';
      case 'improvement':
        return 'border-l-blue-500 bg-blue-50';
    }
  };

  const formatDate = (date?: string) => {
    if (!date) return '';
    const [year, month] = date.split('-');
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return month ? `${monthNames[parseInt(month) - 1]} ${year}` : year;
  };

  const renderUploadArea = () => (
    <Card className="border-2 border-dashed transition-colors duration-200" style={{ borderColor: isDragOver ? 'hsl(var(--primary))' : undefined }}>
      <CardContent className="py-16">
        <div
          className="flex flex-col items-center justify-center cursor-pointer"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            className="hidden"
          />
          <div className="rounded-full bg-muted p-4 mb-4">
            <Upload className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Upload your resume</h3>
          <p className="text-sm text-muted-foreground mb-4 text-center max-w-sm">
            Drag and drop your PDF or DOCX file here, or click to browse
          </p>
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Select File
          </Button>
          <p className="text-xs text-muted-foreground mt-4">
            Supported formats: PDF, DOCX (Max 5MB)
          </p>
        </div>
      </CardContent>
    </Card>
  );

  const renderUploadingState = () => (
    <Card>
      <CardContent className="py-16">
        <div className="flex flex-col items-center justify-center">
          <div className="rounded-full bg-muted p-4 mb-4">
            <RefreshCw className="h-8 w-8 text-primary animate-spin" />
          </div>
          <h3 className="text-lg font-semibold mb-2">
            {uploadState === 'uploading' ? 'Uploading...' : 'Analyzing your resume...'}
          </h3>
          <p className="text-sm text-muted-foreground mb-4">{fileName}</p>
          <div className="w-64">
            <Progress value={uploadState === 'uploading' ? 40 : 80} className="h-2" />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderLoadingSkeleton = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-64 mt-2" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <div className="grid grid-cols-2 gap-4 mt-4">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </div>
        </CardContent>
      </Card>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Skeleton className="h-32" />
        <Skeleton className="h-32 lg:col-span-2" />
      </div>
    </div>
  );

  const renderResumePreview = () => {
    if (!parsedResume) return null;

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Resume Preview
              </CardTitle>
              <CardDescription className="mt-1">{fileName}</CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={handleReset}>
              <X className="h-4 w-4 mr-1" />
              Remove
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="experience">Experience</TabsTrigger>
              <TabsTrigger value="education">Education</TabsTrigger>
              <TabsTrigger value="skills">Skills</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                  <User className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Name</p>
                    <p className="font-medium">{parsedResume.name}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                  <Mail className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Email</p>
                    <p className="font-medium">{parsedResume.email}</p>
                  </div>
                </div>
              </div>
              {parsedResume.summary && (
                <div className="p-4 bg-muted/30 rounded-lg">
                  <p className="text-sm text-muted-foreground mb-2">Summary</p>
                  <p className="text-sm leading-relaxed">{parsedResume.summary}</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="experience" className="space-y-4">
              {parsedResume.experience.map((exp: WorkExperience, index: number) => (
                <div key={index} className="p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium">{exp.title}</h4>
                      <p className="text-sm text-muted-foreground">{exp.company}</p>
                    </div>
                    <Badge variant="secondary" className="text-xs">
                      {formatDate(exp.startDate)} - {exp.current ? 'Present' : formatDate(exp.endDate)}
                    </Badge>
                  </div>
                  <ul className="text-sm space-y-1 mt-3">
                    {exp.description.map((item: string, i: number) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-muted-foreground mt-1.5">-</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="education" className="space-y-4">
              {parsedResume.education.map((edu: Education, index: number) => (
                <div key={index} className="p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium">{edu.degree}{edu.field && ` in ${edu.field}`}</h4>
                      <p className="text-sm text-muted-foreground">{edu.institution}</p>
                    </div>
                    <div className="text-right">
                      {edu.endDate && (
                        <Badge variant="secondary" className="text-xs">
                          {edu.endDate}
                        </Badge>
                      )}
                      {edu.gpa && (
                        <p className="text-sm text-muted-foreground mt-1">GPA: {edu.gpa}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="skills" className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {parsedResume.skills.map((skill: string, index: number) => (
                  <Badge key={index} variant="secondary">
                    {skill}
                  </Badge>
                ))}
              </div>
              {parsedResume.certifications && parsedResume.certifications.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm text-muted-foreground mb-2">Certifications</p>
                  <div className="flex flex-wrap gap-2">
                    {parsedResume.certifications.map((cert: string, index: number) => (
                      <Badge key={index} variant="outline">
                        {cert}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    );
  };

  const renderATSScore = () => {
    if (atsScore === null) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">ATS Score</CardTitle>
          <CardDescription>How well your resume matches ATS requirements</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center">
            <div className="relative w-32 h-32 mb-4">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-muted stroke-current"
                  strokeWidth="3"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className={`${atsScore >= 80 ? 'text-emerald-500' : atsScore >= 60 ? 'text-amber-500' : 'text-red-500'} stroke-current`}
                  strokeWidth="3"
                  strokeLinecap="round"
                  fill="none"
                  strokeDasharray={`${atsScore}, 100`}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-3xl font-bold ${getScoreColor(atsScore)}`}>{atsScore}</span>
                <span className="text-xs text-muted-foreground">out of 100</span>
              </div>
            </div>
            <Badge className={`${atsScore >= 80 ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : atsScore >= 60 ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-red-100 text-red-700 border-red-200'}`}>
              {getScoreLabel(atsScore)}
            </Badge>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderSuggestions = () => {
    if (suggestions.length === 0) return null;

    const groupedSuggestions = suggestions.reduce((acc, suggestion) => {
      if (!acc[suggestion.section]) {
        acc[suggestion.section] = [];
      }
      acc[suggestion.section].push(suggestion);
      return acc;
    }, {} as Record<string, ResumeSuggestion[]>);

    const sectionLabels: Record<string, string> = {
      summary: 'Summary',
      experience: 'Experience',
      education: 'Education',
      skills: 'Skills',
      header: 'Header',
      projects: 'Projects',
    };

    const sectionIcons: Record<string, React.ReactNode> = {
      summary: <User className="h-4 w-4" />,
      experience: <Briefcase className="h-4 w-4" />,
      education: <GraduationCap className="h-4 w-4" />,
      skills: <Code className="h-4 w-4" />,
    };

    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Improvement Suggestions</CardTitle>
          <CardDescription>
            {suggestions.filter(s => s.type === 'success').length} strengths, {' '}
            {suggestions.filter(s => s.type !== 'success').length} areas for improvement
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {Object.entries(groupedSuggestions).map(([section, sectionSuggestions]) => (
            <div key={section}>
              <div className="flex items-center gap-2 mb-3">
                {sectionIcons[section]}
                <h4 className="font-medium text-sm">{sectionLabels[section] || section}</h4>
              </div>
              <div className="space-y-2">
                {sectionSuggestions.map((suggestion) => (
                  <div
                    key={suggestion.id}
                    className={`p-3 border-l-4 rounded-r-lg ${getSuggestionStyle(suggestion.type)}`}
                  >
                    <div className="flex items-start gap-3">
                      {getSuggestionIcon(suggestion.type)}
                      <p className="text-sm flex-1">{suggestion.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  };

  const renderExportButtons = () => (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Export Options</CardTitle>
        <CardDescription>Download your optimized resume</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button className="w-full justify-start" variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Download as PDF
        </Button>
        <Button className="w-full justify-start" variant="outline">
          <FileText className="h-4 w-4 mr-2" />
          Download as DOCX
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="container mx-auto py-8 px-4 max-w-7xl"
    >
      <motion.div variants={itemVariants} className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <FileText className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 via-violet-800 to-slate-900 bg-clip-text text-transparent">Resume Builder</h1>
        </div>
        <p className="text-lg text-muted-foreground">
          Upload your resume to get ATS optimization suggestions and improve your chances of landing interviews
        </p>
      </motion.div>

      {uploadState === 'idle' && (
        <motion.div variants={itemVariants}>
          {renderUploadArea()}
        </motion.div>
      )}

      {(uploadState === 'uploading' || uploadState === 'processing') && (
        <motion.div variants={itemVariants}>
          {renderUploadingState()}
        </motion.div>
      )}

      {uploadState === 'complete' && parsedResume && (
        <motion.div variants={containerVariants} className="space-y-6">
          <motion.div variants={itemVariants}>
            {renderResumePreview()}
          </motion.div>

          <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-6">
              {renderATSScore()}
              {renderExportButtons()}
            </div>
            <div className="lg:col-span-2">
              {renderSuggestions()}
            </div>
          </motion.div>
        </motion.div>
      )}

      {uploadState === 'error' && (
        <motion.div variants={itemVariants}>
          <EmptyState
            icon={AlertTriangle}
            title="Upload failed"
            description="There was an error processing your resume. Please try again with a different file."
            action={{
              label: 'Try Again',
              onClick: handleReset,
            }}
          />
        </motion.div>
      )}
    </motion.div>
  );
}
