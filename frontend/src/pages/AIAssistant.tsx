import { useState, useRef, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage, ChatConversation } from '@/types';
import { cn } from '@/lib/utils';
import {
  Bot,
  Send,
  User,
  Plus,
  MessageSquare,
  Trash2,
  Target,
  TrendingUp,
  BookOpen,
  Briefcase
} from 'lucide-react';

const mockConversations: ChatConversation[] = [
  {
    id: '1',
    title: 'Career path discussion',
    messages: [],
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-01-15'),
  },
  {
    id: '2',
    title: 'Interview preparation',
    messages: [],
    createdAt: new Date('2024-01-12'),
    updatedAt: new Date('2024-01-12'),
  },
  {
    id: '3',
    title: 'Resume review',
    messages: [],
    createdAt: new Date('2024-01-10'),
    updatedAt: new Date('2024-01-10'),
  },
];

const quickPrompts = [
  {
    title: 'Career Path',
    description: 'Get career recommendations',
    icon: Target,
    prompt: 'Help me explore career paths based on my skills and interests',
  },
  {
    title: 'Skill Gap Analysis',
    description: 'Identify areas to improve',
    icon: TrendingUp,
    prompt: 'Analyze my skills and identify areas for improvement',
  },
  {
    title: 'Learning Plan',
    description: 'Create a study roadmap',
    icon: BookOpen,
    prompt: 'Create a learning roadmap for becoming a software engineer',
  },
  {
    title: 'Job Search',
    description: 'Optimize your search',
    icon: Briefcase,
    prompt: 'Help me optimize my job search strategy',
  },
];

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn('flex gap-3 animate-fade-in-up', isUser && 'flex-row-reverse')}
    >
      <div
        className={cn(
          'h-8 w-8 rounded-full flex items-center justify-center shrink-0',
          isUser ? 'bg-primary' : 'bg-muted'
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-primary-foreground" />
        ) : (
          <Bot className="h-4 w-4 text-muted-foreground" />
        )}
      </div>
      <div className={cn('flex-1 max-w-[80%]', isUser && 'text-right')}>
        <div
          className={cn(
            'inline-block rounded-lg px-4 py-2 text-sm',
            isUser ? 'bg-primary text-primary-foreground' : 'bg-muted text-foreground'
          )}
        >
          <div className="whitespace-pre-line">{message.content}</div>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}

function SuggestionButtons({
  suggestions,
  onSelect,
}: {
  suggestions: string[];
  onSelect: (suggestion: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2 ml-11 animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
      {suggestions.map((suggestion, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          className="text-xs h-7"
          onClick={() => onSelect(suggestion)}
        >
          {suggestion}
        </Button>
      ))}
    </div>
  );
}

function TypingIndicator() {
  return (
    <motion.div
      className="flex gap-3"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
        <Bot className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="bg-muted rounded-lg px-4 py-3">
        <div className="flex space-x-1.5">
          <div className="w-2 h-2 bg-muted-foreground/50 rounded-full typing-dot" />
          <div className="w-2 h-2 bg-muted-foreground/50 rounded-full typing-dot" />
          <div className="w-2 h-2 bg-muted-foreground/50 rounded-full typing-dot" />
        </div>
      </div>
    </motion.div>
  );
}

function ConversationSidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: {
  conversations: ChatConversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div className="w-64 border-r flex flex-col h-full">
      <div className="p-3 border-b">
        <Button onClick={onNew} className="w-full" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          New Chat
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={cn(
                'flex items-center gap-2 p-2 rounded-lg cursor-pointer group transition-colors',
                activeId === conv.id ? 'bg-muted' : 'hover:bg-muted/50'
              )}
              onClick={() => onSelect(conv.id)}
            >
              <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm truncate">{conv.title}</p>
                <p className="text-xs text-muted-foreground">
                  {conv.updatedAt.toLocaleDateString()}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(conv.id);
                }}
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

export default function AIAssistant() {
  const [conversations, setConversations] = useState<ChatConversation[]>(mockConversations);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        "Hello! I'm your AI Career Assistant. I can help you with career planning, skill development, job search strategies, and more. What would you like to discuss today?",
      timestamp: new Date(),
      suggestions: [
        'Help me choose a career',
        'Review my skills',
        'Find matching jobs',
        'Create a learning plan',
      ],
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const generateResponse = (input: string): { content: string; suggestions: string[] } => {
    const lowerInput = input.toLowerCase();

    if (lowerInput.includes('career') || lowerInput.includes('path')) {
      return {
        content: `Based on your profile, I can see you have strong technical skills. Here are some career paths that might interest you:

**Software Engineer** - Great match for your programming skills
**Data Scientist** - Leverage your Python experience
**Full-Stack Developer** - Combine frontend and backend skills

Would you like me to create a detailed roadmap for any of these paths?`,
        suggestions: [
          'Tell me about software engineering',
          'What skills do I need?',
          'Show me the roadmap',
        ],
      };
    }

    if (lowerInput.includes('skill') || lowerInput.includes('improve')) {
      return {
        content: `Here's my analysis of your current skills:

**Strengths:**
- Strong foundation in JavaScript and Python
- Good understanding of React basics

**Areas for Growth:**
- Advanced React patterns (hooks, context)
- Backend development (Node.js, databases)
- DevOps and deployment skills

I recommend focusing on backend development next. Would you like specific learning resources?`,
        suggestions: [
          'Show learning resources',
          'Create a study plan',
          'What courses do you recommend?',
        ],
      };
    }

    if (lowerInput.includes('job') || lowerInput.includes('search')) {
      return {
        content: `Here are my recommendations for your job search:

1. **Update your profile** to highlight your JavaScript and Python skills
2. **Target junior developer roles** that match your experience level
3. **Focus on companies** that value growth and learning

Based on your skills, you should look at startups in tech hubs and remote-friendly organizations.`,
        suggestions: [
          'Show me job listings',
          'Help with my resume',
          'Interview tips',
        ],
      };
    }

    if (lowerInput.includes('interview') || lowerInput.includes('prepare')) {
      return {
        content: `Let's prepare you for technical interviews. Here's a structured approach:

**Technical Skills to Review:**
- JavaScript fundamentals and ES6+ features
- React component lifecycle and hooks
- Python data structures and algorithms

**Practice Plan:**
1. Code challenges on LeetCode (easy/medium)
2. Build a small project to showcase
3. Practice explaining your code
4. Mock interviews with peers`,
        suggestions: [
          'Practice coding problems',
          'Behavioral questions',
          'System design basics',
        ],
      };
    }

    return {
      content:
        "That's a great question! I'm here to help you with career development, skill building, job searching, and interview preparation. What specific area would you like to explore?",
      suggestions: [
        'Career guidance',
        'Skill assessment',
        'Job search tips',
      ],
    };
  };

  const handleSend = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate API delay
    setTimeout(() => {
      const { content: responseContent, suggestions } = generateResponse(content);
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseContent,
        timestamp: new Date(),
        suggestions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content:
          "Hello! I'm your AI Career Assistant. I can help you with career planning, skill development, job search strategies, and more. What would you like to discuss today?",
        timestamp: new Date(),
        suggestions: [
          'Help me choose a career',
          'Review my skills',
          'Find matching jobs',
          'Create a learning plan',
        ],
      },
    ]);
  };

  const handleDeleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) {
      handleNewConversation();
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex">
      {/* Sidebar */}
      <ConversationSidebar
        conversations={conversations}
        activeId={activeConversationId}
        onSelect={setActiveConversationId}
        onNew={handleNewConversation}
        onDelete={handleDeleteConversation}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b p-4">
          <h1 className="font-semibold gradient-text">
            AI Career Assistant
          </h1>
          <p className="text-sm text-muted-foreground">
            Get personalized career guidance and recommendations
          </p>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div key={message.id} className="space-y-3">
                <MessageBubble message={message} />
                {message.suggestions && index === messages.length - 1 && !isLoading && (
                  <SuggestionButtons
                    suggestions={message.suggestions}
                    onSelect={handleSend}
                  />
                )}
              </div>
            ))}

            <AnimatePresence>
              {isLoading && <TypingIndicator />}
            </AnimatePresence>
          </div>
        </ScrollArea>

        {/* Quick Prompts (shown when no messages except initial) */}
        {messages.length === 1 && (
          <div className="border-t p-4 animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
            <div className="max-w-3xl mx-auto">
              <p className="text-sm text-muted-foreground mb-3">Quick prompts</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {quickPrompts.map((prompt, index) => (
                  <Button
                    key={prompt.title}
                    variant="outline"
                    className="h-auto py-3 flex-col items-start text-left animate-fade-in-scale hover-lift"
                    style={{ animationDelay: `${index * 60}ms` }}
                    onClick={() => handleSend(prompt.prompt)}
                  >
                    <prompt.icon className="h-4 w-4 mb-1" />
                    <span className="text-sm font-medium">{prompt.title}</span>
                    <span className="text-xs text-muted-foreground">{prompt.description}</span>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Input with focus glow */}
        <div className="border-t p-4">
          <div className="max-w-3xl mx-auto flex gap-2">
            <div className="flex-1 rounded-md border chat-input-glow transition-all">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about careers, skills, jobs, or interviews..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend(inputValue);
                  }
                }}
                disabled={isLoading}
                className="border-0 shadow-none focus-visible:ring-0"
              />
            </div>
            <Button onClick={() => handleSend(inputValue)} disabled={isLoading || !inputValue.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
