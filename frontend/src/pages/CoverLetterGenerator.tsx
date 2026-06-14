import { useState } from 'react';
import { motion } from 'framer-motion';
import { Wand2, Copy, Download, FileText, Loader2, Check, Sparkles } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Badge } from '@/components/ui/badge';
import { CoverLetter, CoverLetterTone, CoverLetterGenerationRequest } from '@/types';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

const toneOptions: { value: CoverLetterTone; label: string; description: string }[] = [
  { value: 'professional', label: 'Professional', description: 'Formal and business-appropriate' },
  { value: 'enthusiastic', label: 'Enthusiastic', description: 'Energetic and passionate' },
  { value: 'casual', label: 'Casual', description: 'Friendly and approachable' },
  { value: 'formal', label: 'Formal', description: 'Traditional and structured' },
];

const mockGenerateCoverLetter = async (request: CoverLetterGenerationRequest): Promise<CoverLetter> => {
  await new Promise((resolve) => setTimeout(resolve, 2000));

  const toneIntros: Record<CoverLetterTone, string> = {
    professional: 'I am writing to express my strong interest in',
    enthusiastic: 'I am thrilled to apply for',
    casual: 'I came across your job posting and wanted to reach out about',
    formal: 'I respectfully submit my application for',
  };

  const content = `Dear Hiring Manager,

${toneIntros[request.tone]} the position described in your job posting. With my background and skills, I am confident I would be a valuable addition to your team.

${request.highlights?.length ? `Key strengths I would bring to this role include: ${request.highlights.join(', ')}.` : ''}

Based on the requirements outlined, I believe my experience aligns well with what you are looking for. I have developed strong capabilities in the areas most relevant to this position and am eager to contribute to your organization's success.

I am particularly drawn to this opportunity because of the challenges it presents and the potential for growth. I am committed to delivering high-quality work and collaborating effectively with team members to achieve shared goals.

Thank you for considering my application. I would welcome the opportunity to discuss how my background and skills could benefit your team. Please feel free to contact me at your convenience to schedule a conversation.

Sincerely,
[Your Name]`;

  return {
    id: `cl-${Date.now()}`,
    jobId: 'mock-job-id',
    content,
    tone: request.tone,
    lastUpdated: new Date().toISOString(),
  };
};

const countWords = (text: string): number => {
  return text
    .trim()
    .split(/\s+/)
    .filter((word) => word.length > 0).length;
};

export default function CoverLetterGenerator() {
  const [jobDescription, setJobDescription] = useState('');
  const [tone, setTone] = useState<CoverLetterTone>('professional');
  const [highlights, setHighlights] = useState('');
  const [generatedLetter, setGeneratedLetter] = useState<CoverLetter | null>(null);
  const [editedContent, setEditedContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!jobDescription.trim()) return;

    setIsGenerating(true);
    try {
      const request: CoverLetterGenerationRequest = {
        jobDescription: jobDescription.trim(),
        tone,
        highlights: highlights
          .split('\n')
          .map((h) => h.trim())
          .filter((h) => h.length > 0),
      };

      const letter = await mockGenerateCoverLetter(request);
      setGeneratedLetter(letter);
      setEditedContent(letter.content);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = async () => {
    const content = editedContent || generatedLetter?.content || '';
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const content = editedContent || generatedLetter?.content || '';
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cover-letter-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const wordCount = countWords(editedContent || generatedLetter?.content || '');
  const canGenerate = jobDescription.trim().length > 0;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="container mx-auto py-8 px-4 max-w-5xl"
    >
      <motion.div variants={itemVariants} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <FileText className="h-7 w-7 text-foreground" />
          <h1 className="text-3xl font-semibold tracking-tight bg-gradient-to-r from-slate-900 via-violet-800 to-slate-900 bg-clip-text text-transparent">
            Cover Letter Generator
          </h1>
        </div>
        <p className="text-muted-foreground">
          Create a tailored cover letter for your job application in seconds
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-medium">Job Description</CardTitle>
              <CardDescription>
                Paste the job description to generate a tailored cover letter
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="Paste the full job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="min-h-[180px] resize-none"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-medium">Tone</CardTitle>
              <CardDescription>Select the tone for your cover letter</CardDescription>
            </CardHeader>
            <CardContent>
              <RadioGroup
                value={tone}
                onValueChange={(value) => setTone(value as CoverLetterTone)}
                className="grid grid-cols-2 gap-3"
              >
                {toneOptions.map((option) => (
                  <label
                    key={option.value}
                    htmlFor={option.value}
                    className={`flex items-start space-x-3 rounded-lg border p-4 cursor-pointer transition-colors hover:bg-muted/50 ${
                      tone === option.value ? 'border-primary bg-muted/30' : 'border-border'
                    }`}
                  >
                    <RadioGroupItem value={option.value} id={option.value} className="mt-0.5" />
                    <div className="space-y-1">
                      <Label htmlFor={option.value} className="font-medium cursor-pointer">
                        {option.label}
                      </Label>
                      <p className="text-xs text-muted-foreground">{option.description}</p>
                    </div>
                  </label>
                ))}
              </RadioGroup>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-medium">Key Highlights</CardTitle>
              <CardDescription>
                Add key points to emphasize (one per line, optional)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="5+ years of experience in React development&#10;Led a team of 8 engineers&#10;Increased conversion rates by 40%"
                value={highlights}
                onChange={(e) => setHighlights(e.target.value)}
                className="min-h-[120px] resize-none"
              />
            </CardContent>
          </Card>

          <Button
            onClick={handleGenerate}
            disabled={!canGenerate || isGenerating}
            className="w-full h-11"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="h-4 w-4" />
                Generate Cover Letter
              </>
            )}
          </Button>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="h-full flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-medium">Generated Letter</CardTitle>
                  <CardDescription>Edit and refine your cover letter</CardDescription>
                </div>
                {generatedLetter && (
                  <Badge variant="secondary" className="font-normal">
                    {wordCount} words
                  </Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              {!generatedLetter && !isGenerating ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center py-12 border border-dashed rounded-lg">
                  <Sparkles className="h-10 w-10 text-muted-foreground/40 mb-4" />
                  <p className="text-sm text-muted-foreground mb-1">No cover letter yet</p>
                  <p className="text-xs text-muted-foreground/70">
                    Enter a job description and click generate
                  </p>
                </div>
              ) : isGenerating ? (
                <div className="flex-1 flex flex-col items-center justify-center py-12 border border-dashed rounded-lg">
                  <Loader2 className="h-8 w-8 text-muted-foreground animate-spin mb-4" />
                  <p className="text-sm text-muted-foreground">Generating your cover letter...</p>
                </div>
              ) : (
                <div className="flex-1 flex flex-col space-y-4">
                  <Textarea
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="flex-1 min-h-[400px] resize-none font-mono text-sm leading-relaxed"
                  />
                  <div className="flex items-center gap-3">
                    <Button
                      variant="outline"
                      onClick={handleCopy}
                      className="flex-1"
                      disabled={!editedContent}
                    >
                      {copied ? (
                        <>
                          <Check className="h-4 w-4" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4" />
                          Copy
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleDownload}
                      className="flex-1"
                      disabled={!editedContent}
                    >
                      <Download className="h-4 w-4" />
                      Download
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
