import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { EmptyState } from '@/components/ui/empty-state';
import { CardSkeleton } from '@/components/ui/loading-skeletons';
import {
  MessageCircle,
  Lightbulb,
  ChevronRight,
  Play,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Eye,
  EyeOff,
  Target,
  Clock,
  ArrowRight,
  Send,
} from 'lucide-react';
import type {
  InterviewQuestion,
  InterviewCategory,
  DifficultyLevel,
  MockInterview,
  InterviewResponse,
  InterviewFeedback,
} from '@/types';

// Role options for the selector
const ROLES = [
  { value: 'software-engineer', label: 'Software Engineer' },
  { value: 'data-scientist', label: 'Data Scientist' },
  { value: 'product-manager', label: 'Product Manager' },
  { value: 'ux-designer', label: 'UX Designer' },
  { value: 'devops-engineer', label: 'DevOps Engineer' },
  { value: 'business-analyst', label: 'Business Analyst' },
];

// Mock interview questions data
const MOCK_QUESTIONS: InterviewQuestion[] = [
  // Behavioral Questions
  {
    id: 'beh-1',
    question: 'Tell me about a time when you had to deal with a difficult team member.',
    category: 'behavioral',
    difficulty: 'intermediate',
    tips: [
      'Use the STAR method (Situation, Task, Action, Result)',
      'Focus on your actions and what you learned',
      'Avoid speaking negatively about the other person',
    ],
    suggestedAnswer:
      'In my previous role, I worked with a colleague who consistently missed deadlines. I scheduled a private meeting to understand their challenges and discovered they were overwhelmed with tasks. I helped them prioritize work and suggested we implement daily check-ins. Within two weeks, their delivery improved significantly, and we completed the project on time.',
    followUps: [
      'What would you do differently if this happened again?',
      'How did this experience change your approach to teamwork?',
    ],
  },
  {
    id: 'beh-2',
    question: 'Describe a situation where you had to learn something new quickly.',
    category: 'behavioral',
    difficulty: 'beginner',
    tips: [
      'Choose a relevant example to the role',
      'Emphasize your learning process and resources used',
      'Highlight the outcome and business impact',
    ],
    suggestedAnswer:
      'When our team adopted a new cloud platform, I needed to become proficient in two weeks. I created a structured learning plan, completed official certifications, and built a prototype project. I then documented best practices and trained three team members, accelerating our migration timeline by a month.',
    followUps: [
      'What resources do you typically use when learning new technologies?',
    ],
  },
  {
    id: 'beh-3',
    question: 'Give an example of a goal you set and how you achieved it.',
    category: 'behavioral',
    difficulty: 'beginner',
    tips: [
      'Be specific about the goal and metrics',
      'Describe the steps you took',
      'Quantify the results if possible',
    ],
    suggestedAnswer:
      'I set a goal to reduce our application load time by 40%. I conducted performance audits, implemented lazy loading, optimized database queries, and introduced caching. Over three months, we achieved a 52% improvement, leading to a 15% increase in user engagement.',
    followUps: [
      'How do you prioritize when you have multiple goals?',
    ],
  },
  {
    id: 'beh-4',
    question: 'Tell me about a time you failed and what you learned from it.',
    category: 'behavioral',
    difficulty: 'advanced',
    tips: [
      'Choose a genuine failure, not a disguised success',
      'Take responsibility without making excuses',
      'Focus on the lessons learned and how you applied them',
    ],
    suggestedAnswer:
      'I once launched a feature without adequate user testing, confident it would succeed. The feature had low adoption and confused users. I learned to always validate assumptions with real user feedback. Since then, I advocate for user research in every project, which has led to much higher feature success rates.',
    followUps: [
      'How do you ensure you learn from failures systematically?',
    ],
  },
  // Technical Questions
  {
    id: 'tech-1',
    question: 'Explain the difference between SQL and NoSQL databases and when to use each.',
    category: 'technical',
    difficulty: 'intermediate',
    tips: [
      'Compare structure, scalability, and use cases',
      'Give specific examples of each type',
      'Discuss trade-offs in real-world scenarios',
    ],
    suggestedAnswer:
      'SQL databases use structured schemas and excel at complex queries and transactions. NoSQL databases offer flexible schemas and horizontal scalability. Use SQL for financial systems requiring ACID compliance, and NoSQL for high-volume, schema-flexible applications like user activity logs or real-time analytics.',
    followUps: [
      'Can you give an example where you might use both in the same application?',
    ],
  },
  {
    id: 'tech-2',
    question: 'How would you design a URL shortening service like bit.ly?',
    category: 'technical',
    difficulty: 'advanced',
    tips: [
      'Start with requirements and scale estimates',
      'Discuss the encoding strategy for short URLs',
      'Address caching, database choices, and analytics',
    ],
    suggestedAnswer:
      'I would use Base62 encoding to generate short codes from auto-incrementing IDs. The system would include a web server layer, a distributed cache for hot URLs, and a NoSQL database for scalability. Analytics would be handled asynchronously via a message queue to avoid impacting redirect latency.',
    followUps: [
      'How would you handle custom short URLs?',
      'What if the same URL is shortened multiple times?',
    ],
  },
  {
    id: 'tech-3',
    question: 'What is the time complexity of common sorting algorithms?',
    category: 'technical',
    difficulty: 'beginner',
    tips: [
      'Cover at least 3-4 algorithms',
      'Explain best, average, and worst cases',
      'Mention space complexity as well',
    ],
    suggestedAnswer:
      'QuickSort averages O(n log n) but worst case O(n^2). MergeSort is always O(n log n) but needs O(n) space. HeapSort is O(n log n) with O(1) space. For nearly sorted data, InsertionSort can be O(n). The choice depends on data characteristics and memory constraints.',
    followUps: [
      'When would you choose one over another?',
    ],
  },
  {
    id: 'tech-4',
    question: 'Explain RESTful API design principles.',
    category: 'technical',
    difficulty: 'intermediate',
    tips: [
      'Cover the key constraints: stateless, uniform interface, etc.',
      'Discuss HTTP methods and status codes',
      'Mention versioning and error handling',
    ],
    suggestedAnswer:
      'REST APIs use HTTP methods semantically: GET for reading, POST for creating, PUT/PATCH for updating, DELETE for removing. Resources are identified by URIs. Key principles include statelessness, use of proper status codes, and consistent naming conventions. Versioning can be done via URL path or headers.',
    followUps: [
      'How would you handle authentication?',
      'What is the difference between PUT and PATCH?',
    ],
  },
  // Situational Questions
  {
    id: 'sit-1',
    question: 'How would you handle a situation where you disagree with your manager\'s decision?',
    category: 'situational',
    difficulty: 'intermediate',
    tips: [
      'Show respect for authority while valuing your own judgment',
      'Emphasize communication and data-driven arguments',
      'Be open to different perspectives',
    ],
    suggestedAnswer:
      'I would first ensure I fully understand their reasoning by asking clarifying questions. If I still disagree, I would request a private conversation, present my concerns with supporting data, and propose alternatives. Ultimately, I would respect the final decision while ensuring my perspective was heard.',
    followUps: [
      'What if they still disagree after you present your case?',
    ],
  },
  {
    id: 'sit-2',
    question: 'You have two high-priority tasks with the same deadline. How do you handle this?',
    category: 'situational',
    difficulty: 'beginner',
    tips: [
      'Discuss prioritization criteria',
      'Mention communication with stakeholders',
      'Consider delegation or deadline negotiation',
    ],
    suggestedAnswer:
      'I would assess both tasks for business impact and dependencies. Then I would communicate with stakeholders to understand true priorities and explore deadline flexibility. If both are truly equal, I would break them into smaller pieces, work on the most critical parts first, and keep stakeholders updated on progress.',
    followUps: [
      'What if neither deadline can be moved?',
    ],
  },
  {
    id: 'sit-3',
    question: 'A production bug is reported during your vacation. What do you do?',
    category: 'situational',
    difficulty: 'advanced',
    tips: [
      'Balance work-life boundaries with responsibility',
      'Mention documentation and knowledge sharing',
      'Consider severity and team capability',
    ],
    suggestedAnswer:
      'First, I would ensure proper handoff documentation exists before any vacation. If contacted, I would assess the severity. For critical issues affecting users, I would provide guidance or briefly help troubleshoot. For non-critical issues, I would point to documentation and trust my team. This highlights the importance of knowledge sharing.',
    followUps: [
      'How do you ensure you are not a single point of failure?',
    ],
  },
  {
    id: 'sit-4',
    question: 'How would you onboard a new team member who is struggling?',
    category: 'situational',
    difficulty: 'intermediate',
    tips: [
      'Show empathy and patience',
      'Discuss structured onboarding approaches',
      'Emphasize feedback and adjustment',
    ],
    suggestedAnswer:
      'I would have a one-on-one to understand their specific challenges and learning style. I would pair them with a buddy, create a structured learning path with clear milestones, and schedule regular check-ins. I would also ensure they know that asking questions is encouraged and that struggle is normal.',
    followUps: [
      'What if they continue to struggle after several weeks?',
    ],
  },
  // Case Study Questions
  {
    id: 'case-1',
    question: 'How would you approach launching a new mobile app feature with a limited budget?',
    category: 'case-study',
    difficulty: 'advanced',
    tips: [
      'Define scope and priorities clearly',
      'Discuss MVP approach and iterations',
      'Consider metrics for success',
    ],
    suggestedAnswer:
      'I would start by identifying the core value proposition and defining an MVP scope. I would prioritize features using impact vs effort analysis, use existing design systems to reduce costs, and plan for staged rollouts. Success metrics would be defined upfront, and we would iterate based on user feedback from the initial release.',
    followUps: [
      'How would you decide what to cut from the initial scope?',
      'What metrics would you track?',
    ],
  },
  {
    id: 'case-2',
    question: 'A competitor just launched a similar product. How would you respond?',
    category: 'case-study',
    difficulty: 'advanced',
    tips: [
      'Stay calm and gather information first',
      'Analyze competitive advantages',
      'Consider short-term and long-term strategies',
    ],
    suggestedAnswer:
      'First, I would conduct a thorough competitive analysis to understand their offering. Then I would identify our unique differentiators and double down on them. In the short term, I might accelerate certain roadmap items. Long term, I would focus on our core strengths and customer relationships rather than reactive feature matching.',
    followUps: [
      'How would you communicate this to your team?',
    ],
  },
  {
    id: 'case-3',
    question: 'User engagement has dropped 20% this quarter. How do you diagnose and address this?',
    category: 'case-study',
    difficulty: 'intermediate',
    tips: [
      'Start with data analysis',
      'Consider multiple hypotheses',
      'Propose both quick wins and long-term solutions',
    ],
    suggestedAnswer:
      'I would segment the data by user cohort, feature, and time to identify patterns. I would review recent changes, conduct user interviews, and analyze competitor activity. Based on findings, I would prioritize quick wins while planning longer-term improvements. A/B testing would validate solutions before full rollout.',
    followUps: [
      'What if the data does not show a clear cause?',
    ],
  },
  {
    id: 'case-4',
    question: 'How would you prioritize features for the next product roadmap?',
    category: 'case-study',
    difficulty: 'intermediate',
    tips: [
      'Discuss frameworks like RICE or MoSCoW',
      'Balance customer needs with business goals',
      'Consider technical constraints',
    ],
    suggestedAnswer:
      'I would use a RICE framework (Reach, Impact, Confidence, Effort) to score features objectively. I would gather input from customers, sales, and support to understand needs. Features would be balanced against strategic goals and technical feasibility. The final roadmap would be shared transparently with stakeholders.',
    followUps: [
      'How do you handle stakeholders who disagree with priorities?',
    ],
  },
];

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

const getDifficultyColor = (difficulty: DifficultyLevel) => {
  switch (difficulty) {
    case 'beginner':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'intermediate':
      return 'bg-amber-50 text-amber-700 border-amber-200';
    case 'advanced':
      return 'bg-red-50 text-red-700 border-red-200';
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200';
  }
};

const getDifficultyLabel = (difficulty: DifficultyLevel) => {
  switch (difficulty) {
    case 'beginner':
      return 'Easy';
    case 'intermediate':
      return 'Medium';
    case 'advanced':
      return 'Hard';
    default:
      return difficulty;
  }
};

const getCategoryLabel = (category: InterviewCategory) => {
  switch (category) {
    case 'behavioral':
      return 'Behavioral';
    case 'technical':
      return 'Technical';
    case 'situational':
      return 'Situational';
    case 'case-study':
      return 'Case Study';
    default:
      return category;
  }
};

interface QuestionCardProps {
  question: InterviewQuestion;
  onAnswer?: (questionId: string) => void;
  isAnswered?: boolean;
}

function QuestionCard({ question, onAnswer, isAnswered }: QuestionCardProps) {
  const [showAnswer, setShowAnswer] = useState(false);

  return (
    <Card className="transition-shadow hover:shadow-sm">
      <Accordion type="single" collapsible>
        <AccordionItem value={question.id} className="border-0">
          <AccordionTrigger className="px-6 py-4 hover:no-underline">
            <div className="flex items-start gap-4 text-left flex-1">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge
                    variant="outline"
                    className={getDifficultyColor(question.difficulty)}
                  >
                    {getDifficultyLabel(question.difficulty)}
                  </Badge>
                  {isAnswered && (
                    <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Practiced
                    </Badge>
                  )}
                </div>
                <p className="font-medium text-foreground">{question.question}</p>
              </div>
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-6 pb-4">
            <div className="space-y-4">
              {/* Tips Section */}
              {question.tips && question.tips.length > 0 && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Lightbulb className="h-4 w-4 text-blue-600" />
                    <span className="font-medium text-blue-900">Tips for Answering</span>
                  </div>
                  <ul className="space-y-1 text-sm text-blue-800">
                    {question.tips.map((tip, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <ChevronRight className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Sample Answer Section */}
              {question.suggestedAnswer && (
                <div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAnswer(!showAnswer)}
                    className="mb-3"
                  >
                    {showAnswer ? (
                      <>
                        <EyeOff className="h-4 w-4 mr-2" />
                        Hide Sample Answer
                      </>
                    ) : (
                      <>
                        <Eye className="h-4 w-4 mr-2" />
                        Show Sample Answer
                      </>
                    )}
                  </Button>
                  {showAnswer && (
                    <div className="bg-muted/50 rounded-lg p-4">
                      <p className="text-sm text-muted-foreground">
                        {question.suggestedAnswer}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Follow-up Questions */}
              {question.followUps && question.followUps.length > 0 && (
                <div className="border-t pt-4">
                  <p className="text-sm font-medium text-muted-foreground mb-2">
                    Possible Follow-up Questions:
                  </p>
                  <ul className="space-y-1">
                    {question.followUps.map((followUp, index) => (
                      <li
                        key={index}
                        className="text-sm text-foreground flex items-start gap-2"
                      >
                        <ArrowRight className="h-4 w-4 mt-0.5 text-muted-foreground flex-shrink-0" />
                        {followUp}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Button */}
              <div className="flex justify-end pt-2">
                <Button
                  size="sm"
                  onClick={() => onAnswer?.(question.id)}
                  disabled={isAnswered}
                >
                  {isAnswered ? 'Already Practiced' : 'Mark as Practiced'}
                </Button>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </Card>
  );
}

interface MockInterviewState {
  isActive: boolean;
  currentQuestionIndex: number;
  questions: InterviewQuestion[];
  responses: InterviewResponse[];
  currentResponse: string;
  showFeedback: boolean;
  currentFeedback: string | null;
}

function MockInterviewMode({
  selectedRole,
  onComplete,
}: {
  selectedRole: string;
  onComplete: (interview: MockInterview) => void;
}) {
  const [state, setState] = useState<MockInterviewState>({
    isActive: false,
    currentQuestionIndex: 0,
    questions: [],
    responses: [],
    currentResponse: '',
    showFeedback: false,
    currentFeedback: null,
  });

  const startInterview = () => {
    // Select 5 random questions across categories
    const shuffled = [...MOCK_QUESTIONS].sort(() => Math.random() - 0.5);
    const selected = shuffled.slice(0, 5);
    setState({
      isActive: true,
      currentQuestionIndex: 0,
      questions: selected,
      responses: [],
      currentResponse: '',
      showFeedback: false,
      currentFeedback: null,
    });
  };

  const submitResponse = () => {
    const currentQuestion = state.questions[state.currentQuestionIndex];
    const response: InterviewResponse = {
      questionId: currentQuestion.id,
      response: state.currentResponse,
      timestamp: new Date().toISOString(),
      score: Math.floor(Math.random() * 30) + 70, // Mock score 70-100
      feedback: generateMockFeedback(state.currentResponse),
    };

    setState((prev) => ({
      ...prev,
      responses: [...prev.responses, response],
      showFeedback: true,
      currentFeedback: response.feedback || null,
    }));
  };

  const nextQuestion = () => {
    if (state.currentQuestionIndex < state.questions.length - 1) {
      setState((prev) => ({
        ...prev,
        currentQuestionIndex: prev.currentQuestionIndex + 1,
        currentResponse: '',
        showFeedback: false,
        currentFeedback: null,
      }));
    } else {
      // Interview complete
      const interview: MockInterview = {
        id: `interview-${Date.now()}`,
        role: selectedRole,
        questions: state.questions,
        responses: state.responses,
        startedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
        overallScore: Math.round(
          state.responses.reduce((acc, r) => acc + (r.score || 0), 0) /
            state.responses.length
        ),
        feedback: {
          strengths: ['Clear communication', 'Structured responses'],
          improvements: ['Add more specific examples', 'Quantify results when possible'],
          overallComments: 'Good interview performance with room for improvement in specific areas.',
        },
      };
      onComplete(interview);
      setState({
        isActive: false,
        currentQuestionIndex: 0,
        questions: [],
        responses: [],
        currentResponse: '',
        showFeedback: false,
        currentFeedback: null,
      });
    }
  };

  const generateMockFeedback = (response: string): string => {
    if (response.length < 50) {
      return 'Your response is quite brief. Try to provide more detail and specific examples to strengthen your answer.';
    }
    if (response.length < 150) {
      return 'Good start! Consider adding more context about the situation and the specific results of your actions.';
    }
    return 'Well-structured response with good detail. Consider quantifying your results for even more impact.';
  };

  const currentQuestion = state.questions[state.currentQuestionIndex];
  const progress = ((state.currentQuestionIndex + 1) / state.questions.length) * 100;

  if (!state.isActive) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="rounded-full bg-muted p-4 mb-4 inline-flex">
            <Play className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Mock Interview Mode</h3>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            Practice answering interview questions in a simulated interview environment.
            You will receive feedback after each response.
          </p>
          <Button onClick={startInterview} size="lg">
            <Play className="h-4 w-4 mr-2" />
            Start Mock Interview
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Progress Header */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              Question {state.currentQuestionIndex + 1} of {state.questions.length}
            </span>
            <span className="text-sm text-muted-foreground">
              {Math.round(progress)}% Complete
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </CardContent>
      </Card>

      {/* Current Question */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2 mb-2">
            <Badge
              variant="outline"
              className={getDifficultyColor(currentQuestion.difficulty)}
            >
              {getDifficultyLabel(currentQuestion.difficulty)}
            </Badge>
            <Badge variant="outline">{getCategoryLabel(currentQuestion.category)}</Badge>
          </div>
          <CardTitle className="text-lg">{currentQuestion.question}</CardTitle>
          {currentQuestion.tips && currentQuestion.tips.length > 0 && (
            <CardDescription className="flex items-center gap-2 mt-2">
              <Lightbulb className="h-4 w-4" />
              Tip: {currentQuestion.tips[0]}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {!state.showFeedback ? (
            <>
              <Textarea
                placeholder="Type your response here..."
                value={state.currentResponse}
                onChange={(e) =>
                  setState((prev) => ({ ...prev, currentResponse: e.target.value }))
                }
                rows={6}
                className="resize-none"
              />
              <div className="flex justify-end">
                <Button
                  onClick={submitResponse}
                  disabled={state.currentResponse.trim().length === 0}
                >
                  <Send className="h-4 w-4 mr-2" />
                  Submit Response
                </Button>
              </div>
            </>
          ) : (
            <div className="space-y-4">
              {/* Your Response */}
              <div className="bg-muted/50 rounded-lg p-4">
                <p className="text-sm font-medium mb-2">Your Response:</p>
                <p className="text-sm text-muted-foreground">{state.currentResponse}</p>
              </div>

              {/* Feedback */}
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <MessageCircle className="h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-900">Feedback</span>
                </div>
                <p className="text-sm text-blue-800">{state.currentFeedback}</p>
              </div>

              {/* Score */}
              <div className="flex items-center justify-between bg-muted/50 rounded-lg p-4">
                <span className="text-sm font-medium">Response Score:</span>
                <Badge
                  variant="outline"
                  className={
                    (state.responses[state.responses.length - 1]?.score || 0) >= 80
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border-amber-200'
                  }
                >
                  {state.responses[state.responses.length - 1]?.score}/100
                </Badge>
              </div>

              {/* Follow-up Question */}
              {currentQuestion.followUps && currentQuestion.followUps.length > 0 && (
                <div className="border-t pt-4">
                  <p className="text-sm font-medium text-muted-foreground mb-2">
                    Follow-up Question:
                  </p>
                  <p className="text-sm text-foreground">
                    {currentQuestion.followUps[0]}
                  </p>
                </div>
              )}

              <div className="flex justify-end">
                <Button onClick={nextQuestion}>
                  {state.currentQuestionIndex < state.questions.length - 1 ? (
                    <>
                      Next Question
                      <ChevronRight className="h-4 w-4 ml-2" />
                    </>
                  ) : (
                    <>
                      Complete Interview
                      <CheckCircle2 className="h-4 w-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function InterviewPrep() {
  const [selectedRole, setSelectedRole] = useState<string>('software-engineer');
  const [selectedCategory, setSelectedCategory] = useState<InterviewCategory>('behavioral');
  const [answeredQuestions, setAnsweredQuestions] = useState<Set<string>>(new Set());
  const [completedInterviews, setCompletedInterviews] = useState<MockInterview[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<string>('practice');

  // Simulate initial loading
  useState(() => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 500);
  });

  const filteredQuestions = useMemo(() => {
    return MOCK_QUESTIONS.filter((q) => q.category === selectedCategory);
  }, [selectedCategory]);

  const handleMarkAnswered = (questionId: string) => {
    setAnsweredQuestions((prev) => new Set(prev).add(questionId));
  };

  const handleInterviewComplete = (interview: MockInterview) => {
    setCompletedInterviews((prev) => [...prev, interview]);
    setActiveTab('practice');
  };

  const totalQuestions = MOCK_QUESTIONS.length;
  const answeredCount = answeredQuestions.size;
  const avgScore =
    completedInterviews.length > 0
      ? Math.round(
          completedInterviews.reduce((acc, i) => acc + (i.overallScore || 0), 0) /
            completedInterviews.length
        )
      : 0;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-slate-900 via-violet-800 to-slate-900 bg-clip-text text-transparent">Interview Preparation</h1>
        <p className="text-muted-foreground text-lg">
          Practice interview questions and improve your responses
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Questions Practiced
                </p>
                <p className="text-2xl font-bold">
                  {answeredCount}/{totalQuestions}
                </p>
              </div>
              <Target className="h-8 w-8 text-muted-foreground" />
            </div>
            <Progress
              value={(answeredCount / totalQuestions) * 100}
              className="h-2 mt-3"
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Mock Interviews
                </p>
                <p className="text-2xl font-bold">{completedInterviews.length}</p>
              </div>
              <MessageCircle className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Average Score</p>
                <p className="text-2xl font-bold">
                  {completedInterviews.length > 0 ? `${avgScore}%` : '--'}
                </p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Time Spent</p>
                <p className="text-2xl font-bold">
                  {completedInterviews.length * 15}m
                </p>
              </div>
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Role Selector */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardContent className="py-4">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4">
              <label className="text-sm font-medium">Select Role:</label>
              <Select value={selectedRole} onValueChange={setSelectedRole}>
                <SelectTrigger className="w-full sm:w-[240px]">
                  <SelectValue placeholder="Select a role" />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((role) => (
                    <SelectItem key={role.value} value={role.value}>
                      {role.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Main Content Tabs */}
      <motion.div variants={itemVariants}>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="practice">Practice Questions</TabsTrigger>
            <TabsTrigger value="mock">Mock Interview</TabsTrigger>
          </TabsList>

          <TabsContent value="practice">
            {/* Category Tabs */}
            <Tabs
              value={selectedCategory}
              onValueChange={(v) => setSelectedCategory(v as InterviewCategory)}
            >
              <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 mb-6">
                <TabsTrigger value="behavioral">Behavioral</TabsTrigger>
                <TabsTrigger value="technical">Technical</TabsTrigger>
                <TabsTrigger value="situational">Situational</TabsTrigger>
                <TabsTrigger value="case-study">Case Study</TabsTrigger>
              </TabsList>

              {['behavioral', 'technical', 'situational', 'case-study'].map(
                (category) => (
                  <TabsContent key={category} value={category} className="space-y-4">
                    {isLoading ? (
                      <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                          <CardSkeleton key={i} />
                        ))}
                      </div>
                    ) : filteredQuestions.length === 0 ? (
                      <EmptyState
                        icon={MessageCircle}
                        title="No questions available"
                        description="Questions for this category will be added soon."
                      />
                    ) : (
                      <div className="space-y-4">
                        {filteredQuestions.map((question) => (
                          <QuestionCard
                            key={question.id}
                            question={question}
                            onAnswer={handleMarkAnswered}
                            isAnswered={answeredQuestions.has(question.id)}
                          />
                        ))}
                      </div>
                    )}
                  </TabsContent>
                )
              )}
            </Tabs>
          </TabsContent>

          <TabsContent value="mock">
            <MockInterviewMode
              selectedRole={selectedRole}
              onComplete={handleInterviewComplete}
            />

            {/* Completed Interviews */}
            {completedInterviews.length > 0 && (
              <div className="mt-8 space-y-4">
                <h3 className="text-lg font-semibold">Completed Mock Interviews</h3>
                {completedInterviews.map((interview, index) => (
                  <Card key={interview.id}>
                    <CardContent className="py-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">
                            Mock Interview #{index + 1}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {interview.questions.length} questions answered
                          </p>
                        </div>
                        <div className="text-right">
                          <Badge
                            variant="outline"
                            className={
                              (interview.overallScore || 0) >= 80
                                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                : 'bg-amber-50 text-amber-700 border-amber-200'
                            }
                          >
                            Score: {interview.overallScore}%
                          </Badge>
                        </div>
                      </div>
                      {interview.feedback && (
                        <div className="mt-4 pt-4 border-t">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm font-medium text-emerald-700 mb-1">
                                Strengths
                              </p>
                              <ul className="text-sm text-muted-foreground space-y-1">
                                {interview.feedback.strengths.map((s, i) => (
                                  <li key={i} className="flex items-center gap-2">
                                    <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                                    {s}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-amber-700 mb-1">
                                Areas to Improve
                              </p>
                              <ul className="text-sm text-muted-foreground space-y-1">
                                {interview.feedback.improvements.map((s, i) => (
                                  <li key={i} className="flex items-center gap-2">
                                    <ArrowRight className="h-3 w-3 text-amber-500" />
                                    {s}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </motion.div>
    </motion.div>
  );
}
