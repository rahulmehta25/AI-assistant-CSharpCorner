import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { HelpCircle, Search, ChevronDown, ChevronRight, Bot, BookOpen, Mail, Compass, Brain, Briefcase } from 'lucide-react';
import { Link } from 'react-router-dom';

interface FAQ {
  question: string;
  answer: string;
  category: string;
}

const faqs: FAQ[] = [
  {
    question: 'How does the AI Career Assistant work?',
    answer: 'The AI Career Assistant is powered by Claude (Anthropic). It reads your profile — including your skills, experience level, location, and interests — and provides personalized advice. Every conversation is context-aware: the AI knows who you are and tailors responses accordingly. Simply type your question or use one of the Quick Action prompts to get started.',
    category: 'AI Assistant',
  },
  {
    question: 'How do I get better AI recommendations?',
    answer: 'The more complete your profile, the better the advice. Make sure your Profile page has your current title, experience level, skills, and location filled in. The AI uses all of this when crafting career guidance. You can update your profile at any time from the Profile page.',
    category: 'AI Assistant',
  },
  {
    question: 'What is the Career Explorer and how do I use it?',
    answer: "The Career Explorer gives you access to 300+ occupations sourced from the O*NET database (the US Department of Labor's official career database). You can search by keyword, filter by salary or growth rate, and click into any career to see a detailed breakdown including typical tasks, required skills, and median wages.",
    category: 'Career Explorer',
  },
  {
    question: 'How are job match percentages calculated?',
    answer: "Job match scores are based on how well your skill set aligns with the requirements listed for each career or job posting. A higher match means more of your skills are relevant. You can improve your match score by adding more skills to your profile and by exploring careers in fields that align with your existing knowledge.",
    category: 'Job Search',
  },
  {
    question: 'What are Career Pathways?',
    answer: 'Career Pathways are structured, step-by-step learning roadmaps designed to take you from your current skill level to a specific career goal. Each pathway includes courses, projects, and certifications in the right order, with time estimates and resource recommendations. Track your progress as you complete each step.',
    category: 'Pathways',
  },
  {
    question: 'How do I track my job applications?',
    answer: 'The Applications page lets you log every job you apply to and track its status through the hiring pipeline: Applied → Screening → Interview → Offer. You can add notes, record next steps, and set follow-up reminders. Use the filter and search to find specific applications quickly.',
    category: 'Applications',
  },
  {
    question: 'What courses does the Learning Hub recommend?',
    answer: 'The Learning Hub curates high-quality courses from providers like Frontend Masters, Coursera, Udemy, AWS, and Google. Courses are tagged with skills and rated by community feedback. The platform highlights courses that match your skill gaps and career goals based on your profile. Free courses are clearly marked.',
    category: 'Learning',
  },
  {
    question: 'Is my data stored securely?',
    answer: 'Your profile and progress data is stored locally in your browser (localStorage) for now. No data is sent to external servers except your chat messages to the AI Assistant, which go through a secure serverless function. We never store or log your chat conversations.',
    category: 'Privacy',
  },
  {
    question: 'Can I use this without creating an account?',
    answer: "Yes! The platform currently works without a traditional account. Your profile is stored in your browser. This means your data persists across sessions on the same device and browser, but won't sync across multiple devices.",
    category: 'Account',
  },
  {
    question: 'How do I set up the ANTHROPIC_API_KEY for the AI?',
    answer: 'If you are deploying this yourself on Vercel, add ANTHROPIC_API_KEY as an Environment Variable in your Vercel project settings. The key is only used server-side — it is never exposed to the browser. Get your key from console.anthropic.com.',
    category: 'Setup',
  },
];

const quickLinks = [
  { title: 'AI Career Assistant', href: '/assistant', icon: Bot, desc: 'Get personalized career advice' },
  { title: 'Career Explorer', href: '/careers', icon: Compass, desc: 'Browse 300+ career paths' },
  { title: 'Skills Analysis', href: '/skills', icon: Brain, desc: 'Identify and close skill gaps' },
  { title: 'Career Pathways', href: '/pathways', icon: BookOpen, desc: 'Structured learning roadmaps' },
  { title: 'Job Search', href: '/jobs', icon: Briefcase, desc: 'Find roles that match you' },
];

export default function Help() {
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = faqs.filter(
    (faq) =>
      faq.question.toLowerCase().includes(search.toLowerCase()) ||
      faq.answer.toLowerCase().includes(search.toLowerCase()) ||
      faq.category.toLowerCase().includes(search.toLowerCase())
  );

  const categories = [...new Set(faqs.map((f) => f.category))];

  return (
    <div id="help-container" className="container mx-auto py-8 px-4 max-w-4xl">
      <motion.div id="help-header" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <HelpCircle className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Help & Support</h1>
            <p className="text-muted-foreground">Everything you need to get the most out of the platform</p>
          </div>
        </div>
      </motion.div>

      {/* Quick Links */}
      <motion.div id="quick-links-section" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
        <h2 className="text-base font-semibold mb-3">Quick Navigation</h2>
        <div id="quick-links-grid" className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {quickLinks.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                to={link.href}
                id={`quick-link-${link.href.replace('/', '')}`}
                className="flex flex-col items-center gap-2 p-4 rounded-xl border border-border/50 hover:border-primary/30 hover:bg-primary/5 transition-all text-center group"
              >
                <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                  <Icon className="h-4.5 w-4.5 text-primary" />
                </div>
                <div>
                  <p className="text-xs font-medium">{link.title}</p>
                  <p className="text-xs text-muted-foreground hidden sm:block">{link.desc}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </motion.div>

      {/* FAQ Search */}
      <motion.div id="faq-section" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold">Frequently Asked Questions</h2>
          <div className="flex gap-2 flex-wrap">
            {categories.map((cat) => (
              <Badge key={cat} variant="outline" className="text-xs cursor-pointer hover:border-primary/30"
                onClick={() => setSearch(cat)}>
                {cat}
              </Badge>
            ))}
          </div>
        </div>

        <div className="relative mb-5">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="faq-search"
            placeholder="Search for answers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div id="faq-list" className="space-y-2">
          {filtered.map((faq, i) => (
            <Card
              key={i}
              id={`faq-${i}`}
              className={`border-border/50 transition-colors cursor-pointer ${
                expanded === faq.question ? 'border-primary/30 bg-primary/3' : 'hover:border-border'
              }`}
              onClick={() => setExpanded(expanded === faq.question ? null : faq.question)}
            >
              <CardContent className="pt-4 pb-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-0.5">
                      <Badge variant="outline" className="text-xs">{faq.category}</Badge>
                    </div>
                    <p className="font-medium text-sm">{faq.question}</p>
                    {expanded === faq.question && (
                      <motion.p
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="text-sm text-muted-foreground mt-2 leading-relaxed"
                      >
                        {faq.answer}
                      </motion.p>
                    )}
                  </div>
                  {expanded === faq.question ? (
                    <ChevronDown className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-muted-foreground flex-shrink-0 mt-0.5" />
                  )}
                </div>
              </CardContent>
            </Card>
          ))}

          {filtered.length === 0 && (
            <div id="faq-empty" className="text-center py-10 text-muted-foreground">
              <HelpCircle className="h-8 w-8 mx-auto mb-2 opacity-20" />
              <p>No answers found for "{search}"</p>
              <Button variant="link" onClick={() => setSearch('')}>Clear search</Button>
            </div>
          )}
        </div>
      </motion.div>

      {/* Contact */}
      <motion.div id="contact-section" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mt-8">
        <Card className="border-border/50 bg-gradient-to-br from-primary/5 to-secondary/5">
          <CardContent className="pt-6 pb-6 text-center">
            <Mail className="h-8 w-8 text-primary mx-auto mb-3" />
            <h3 className="font-semibold mb-1">Still have questions?</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Open an issue on GitHub or ask the AI Assistant directly — it can answer questions about how the platform works.
            </p>
            <div id="contact-actions" className="flex gap-3 justify-center flex-wrap">
              <Button id="contact-github" variant="outline" asChild>
                <a href="https://github.com/rahulmehta25/AI-assistant-CSharpCorner/issues" target="_blank" rel="noopener noreferrer">
                  Open GitHub Issue
                </a>
              </Button>
              <Button id="contact-ai" asChild>
                <Link to="/assistant">Ask AI Assistant</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
