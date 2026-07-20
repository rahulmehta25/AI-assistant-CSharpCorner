import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Bot, Send, User, Sparkles, MessageCircle, BookOpen, Target, TrendingUp, AlertCircle, RefreshCw } from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  error?: boolean;
}

const quickActions = [
  {
    title: 'Career Path Guidance',
    description: 'Get personalized career recommendations',
    icon: Target,
    color: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    prompt: 'Based on my background and skills, what career paths do you recommend and why? Please be specific to my profile.',
  },
  {
    title: 'Skill Gap Analysis',
    description: 'Identify what skills you need to develop',
    icon: TrendingUp,
    color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    prompt: 'Analyze my current skills and tell me specifically what I need to learn to advance to the next level in my career. Give me a prioritized list with resources.',
  },
  {
    title: 'Learning Roadmap',
    description: 'Create a structured learning plan',
    icon: BookOpen,
    color: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    prompt: 'Create a 6-month learning roadmap for me with specific courses, projects, and milestones. Focus on what will have the highest impact on my career.',
  },
  {
    title: 'Interview Prep',
    description: 'Practice and get interview strategies',
    icon: MessageCircle,
    color: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    prompt: 'Help me prepare for technical interviews. What are the most important topics to study for my target roles, and what interview strategies do you recommend?',
  },
];

const initialMessage: Message = {
  id: '1',
  role: 'assistant',
  content: "Hello! I'm your AI Career Assistant powered by Claude. I have access to your profile and can provide personalized career guidance tailored to your specific background and goals.\n\nWhat would you like to work on today?",
  timestamp: new Date(),
  suggestions: [
    'Help me choose a career path',
    'Review my skills and suggest improvements',
    'Find jobs that match my profile',
    'Create a learning roadmap',
  ],
};

const AIAssistant = () => {
  const { user } = useUserStore();
  const [messages, setMessages] = useState<Message[]>([initialMessage]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const userProfile = user
    ? {
        name: user.name,
        title: user.profile.title,
        experience: user.profile.experience,
        education: user.profile.education,
        location: user.profile.location,
        interests: user.profile.interests,
        skills: user.profile.skills?.map((s) => ({
          name: s.name,
          level: s.level,
          category: s.category,
        })),
      }
    : undefined;

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInputMessage('');
    setIsLoading(true);

    // Build conversation history for the API (exclude initial welcome message system-side)
    const apiMessages = updatedMessages
      .filter((m) => !m.error)
      .map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content }));

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: apiMessages, userProfile }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(err.error || `HTTP ${res.status}`);
      }

      const data = await res.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        suggestions: generateFollowUps(content),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const isApiKeyMissing =
        error instanceof Error && error.message.includes('API key not configured');

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: isApiKeyMissing
            ? 'The AI assistant requires an API key to be configured. Please add ANTHROPIC_API_KEY to your environment variables in Vercel.'
            : `I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const generateFollowUps = (userInput: string): string[] => {
    const input = userInput.toLowerCase();
    if (input.includes('career') || input.includes('path')) {
      return ['What skills should I build first?', 'What salary can I expect?', 'How long will this take?'];
    }
    if (input.includes('skill') || input.includes('learn')) {
      return ['Recommend specific courses', 'How do I practice these skills?', 'What projects should I build?'];
    }
    if (input.includes('interview') || input.includes('job')) {
      return ['Give me practice questions', 'Review my resume tips', 'How should I negotiate salary?'];
    }
    return ['Tell me more', 'What should I do next?', 'Can you give me a specific example?'];
  };

  const formatContent = (content: string) => {
    // Convert **bold** markdown to spans and preserve newlines
    const parts = content.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-foreground">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div id="ai-assistant-container" className="container mx-auto py-8 px-4 max-w-6xl">
      <motion.div
        id="ai-assistant-header"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              AI Career Assistant
            </h1>
            <div className="flex items-center gap-2 mt-0.5">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs text-muted-foreground">Powered by Claude — Personalized to your profile</span>
            </div>
          </div>
        </div>
      </motion.div>

      <div id="ai-assistant-grid" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div id="quick-actions-panel" className="lg:col-span-1 space-y-4">
          <Card className="border-border/50 bg-card/50 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-primary" />
                Quick Actions
              </CardTitle>
              <CardDescription>Start with one click</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  id={`quick-action-${index}`}
                  onClick={() => sendMessage(action.prompt)}
                  disabled={isLoading}
                  className="w-full p-3 rounded-lg border border-border/50 hover:border-primary/30 hover:bg-muted/50 transition-all duration-200 text-left group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-1.5 rounded-lg border ${action.color} transition-colors`}>
                      <action.icon className="h-3.5 w-3.5" />
                    </div>
                    <div>
                      <p className="font-medium text-sm text-foreground group-hover:text-primary transition-colors">
                        {action.title}
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">{action.description}</p>
                    </div>
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Profile context badge */}
          {user && (
            <Card id="profile-context-card" className="border-border/50 bg-card/50 backdrop-blur">
              <CardContent className="pt-4 pb-4">
                <p className="text-xs font-medium text-muted-foreground mb-2">Advising based on your profile</p>
                <div className="space-y-1.5">
                  <Badge variant="secondary" className="text-xs w-full justify-start">
                    {user.profile.title}
                  </Badge>
                  <Badge variant="outline" className="text-xs w-full justify-start">
                    {user.profile.experience}
                  </Badge>
                  <Badge variant="outline" className="text-xs w-full justify-start">
                    {user.profile.location}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Chat Interface */}
        <Card id="chat-card" className="lg:col-span-2 border-border/50 flex flex-col min-h-[50vh] max-h-[70vh] lg:max-h-none" style={{ height: '70vh', minHeight: '500px' }}>
          <CardHeader className="pb-3 border-b border-border/50">
            <CardTitle className="text-base">Chat</CardTitle>
            <CardDescription>Get personalized career advice</CardDescription>
          </CardHeader>
          <CardContent className="p-0 flex flex-col flex-1 min-h-0">
            <ScrollArea id="chat-scroll-area" className="flex-1 p-4">
              <div id="chat-messages" role="log" aria-live="polite" aria-label="Chat messages" className="space-y-4">
                {messages.map((message) => (
                  <div key={message.id} id={`message-${message.id}`} className="space-y-2">
                    <div
                      className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`flex gap-2.5 max-w-[85%] ${
                          message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                        }`}
                      >
                        <div
                          aria-label={message.role === 'user' ? 'You' : message.error ? 'Error' : 'AI Assistant'}
                          className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center ${
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : message.error
                              ? 'bg-destructive/10 text-destructive'
                              : 'bg-gradient-to-br from-primary to-secondary text-white'
                          }`}
                        >
                          {message.role === 'user' ? (
                            <User className="h-3.5 w-3.5" />
                          ) : message.error ? (
                            <AlertCircle className="h-3.5 w-3.5" />
                          ) : (
                            <Bot className="h-3.5 w-3.5" />
                          )}
                        </div>
                        <div
                          className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${
                            message.role === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : message.error
                              ? 'bg-destructive/10 text-destructive border border-destructive/20'
                              : 'bg-muted text-foreground'
                          }`}
                        >
                          <div className="whitespace-pre-line">
                            {formatContent(message.content)}
                          </div>
                          <div className="text-xs opacity-50 mt-2">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    </div>

                    {message.role === 'assistant' && message.suggestions && !message.error && (
                      <div id={`suggestions-${message.id}`} className="flex flex-wrap gap-1.5 ml-9">
                        {message.suggestions.map((suggestion, idx) => (
                          <button
                            key={idx}
                            onClick={() => sendMessage(suggestion)}
                            disabled={isLoading}
                            className="text-xs px-3 py-1 rounded-full border border-border hover:border-primary/50 hover:bg-primary/5 hover:text-primary text-muted-foreground transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div id="loading-indicator" className="flex gap-2.5">
                    <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                      <Bot className="h-3.5 w-3.5 text-white" />
                    </div>
                    <div className="bg-muted rounded-xl px-4 py-3">
                      <div className="flex items-center gap-1.5">
                        <RefreshCw className="h-3 w-3 text-muted-foreground animate-spin" />
                        <span className="text-xs text-muted-foreground">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
            </ScrollArea>

            <div id="chat-input-area" className="border-t border-border/50 p-4">
              <div className="flex gap-2">
                <label htmlFor="chat-input" className="sr-only">Message the AI Career Assistant</label>
                <Input
                  ref={inputRef}
                  id="chat-input"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask about your career, skills, job search..."
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage(inputMessage);
                    }
                  }}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  id="chat-send-btn"
                  onClick={() => sendMessage(inputMessage)}
                  disabled={isLoading || !inputMessage.trim()}
                  size="icon"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                Claude has full context of your profile and career goals
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AIAssistant;
