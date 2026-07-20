import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Bot, Send, User, Sparkles, MessageCircle, BookOpen,
  Target, TrendingUp, AlertCircle, RotateCcw, Zap,
} from 'lucide-react';
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
    description: 'Get personalized recommendations',
    icon: Target,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    prompt: 'Based on my background and skills, what career paths do you recommend and why? Please be specific to my profile.',
  },
  {
    title: 'Skill Gap Analysis',
    description: 'Identify what to learn next',
    icon: TrendingUp,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
    prompt: 'Analyze my current skills and tell me specifically what I need to learn to advance. Give me a prioritized list with resources.',
  },
  {
    title: 'Learning Roadmap',
    description: 'Structured 6-month plan',
    icon: BookOpen,
    color: 'text-violet-400',
    bg: 'bg-violet-500/10',
    border: 'border-violet-500/20',
    prompt: 'Create a 6-month learning roadmap for me with specific courses, projects, and milestones. Focus on highest impact.',
  },
  {
    title: 'Interview Prep',
    description: 'Practice & strategy',
    icon: MessageCircle,
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/20',
    prompt: 'Help me prepare for technical interviews. What are the most important topics and strategies for my target roles?',
  },
];

const initialMessage: Message = {
  id: '1',
  role: 'assistant',
  content: "Hello! I'm your AI Career Assistant powered by Claude. I have full context of your profile and can provide personalized guidance tailored to your background and goals.\n\nWhat would you like to explore today?",
  timestamp: new Date(),
  suggestions: [
    'Help me choose a career path',
    'Analyze my skill gaps',
    'Find jobs that match my profile',
    'Create a learning roadmap',
  ],
};

function generateFollowUps(userInput: string): string[] {
  const input = userInput.toLowerCase();
  if (input.includes('career') || input.includes('path'))
    return ['What skills should I build first?', 'What salary can I expect?', 'How long will this take?'];
  if (input.includes('skill') || input.includes('learn'))
    return ['Recommend specific courses', 'How do I practice these?', 'What projects should I build?'];
  if (input.includes('interview') || input.includes('job'))
    return ['Give me practice questions', 'Tips for resume?', 'How to negotiate salary?'];
  return ['Tell me more', 'What should I do next?', 'Give me a specific example'];
}

function formatContent(content: string): React.ReactNode[] {
  const parts = content.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>;
    return <span key={i}>{part}</span>;
  });
}

/* ── Typing indicator ─────────────────────────────────── */
const TypingIndicator = () => (
  <div id="typing-indicator" className="flex gap-3">
    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center shadow-glow">
      <Bot className="h-4 w-4 text-white" />
    </div>
    <div className="bg-card border border-border/50 rounded-2xl rounded-tl-sm px-4 py-3.5 shadow-sm">
      <div id="typing-dots" className="flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-2 w-2 rounded-full bg-primary/70 animate-bounce-dot"
            style={{ animationDelay: `${i * 0.18}s` }}
          />
        ))}
      </div>
    </div>
  </div>
);

/* ── Main component ───────────────────────────────────── */
const AIAssistant = () => {
  const { user } = useUserStore();
  const [messages, setMessages] = useState<Message[]>([initialMessage]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef  = useRef<HTMLDivElement>(null);
  const inputRef   = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const userProfile = user
    ? {
        name:       user.name,
        title:      user.profile.title,
        experience: user.profile.experience,
        education:  user.profile.education,
        location:   user.profile.location,
        interests:  user.profile.interests,
        skills:     user.profile.skills?.map((s) => ({ name: s.name, level: s.level, category: s.category })),
      }
    : undefined;

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(), role: 'user', content: content.trim(), timestamp: new Date(),
    };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInputMessage('');
    setIsLoading(true);

    const apiMessages = updated
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

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          suggestions: generateFollowUps(content),
        },
      ]);
    } catch (error) {
      const isApiKeyMissing =
        error instanceof Error && error.message.includes('API key not configured');
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: isApiKeyMissing
            ? 'The AI assistant requires an API key. Please add ANTHROPIC_API_KEY to your environment variables.'
            : `I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
          timestamp: new Date(),
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputMessage);
    }
  };

  const resetChat = () => {
    setMessages([initialMessage]);
    setInputMessage('');
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  return (
    <div id="ai-assistant-container" className="max-w-6xl mx-auto space-y-6">
      {/* ── Header ──────────────────────────────────────── */}
      <motion.div
        id="ai-assistant-header"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between flex-wrap gap-4"
      >
        <div className="flex items-center gap-3">
          <div className="h-11 w-11 rounded-2xl bg-gradient-primary flex items-center justify-center shadow-glow animate-pulse-glow">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-gradient-primary">
              AI Career Assistant
            </h1>
            <div className="flex items-center gap-2 mt-0.5">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs text-muted-foreground">
                Powered by Claude · Personalized to your profile
              </span>
            </div>
          </div>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={resetChat}
          className="gap-2 text-muted-foreground hover:text-foreground"
        >
          <RotateCcw className="h-4 w-4" />
          New Chat
        </Button>
      </motion.div>

      {/* ── Body grid ───────────────────────────────────── */}
      <div id="ai-assistant-grid" className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Sidebar: quick actions + profile context */}
        <div id="ai-sidebar" className="lg:col-span-1 space-y-4">
          {/* Quick actions */}
          <Card className="border-border/50 bg-card/80">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm">
                <Sparkles className="h-4 w-4 text-primary" />
                Quick Start
              </CardTitle>
              <CardDescription className="text-xs">One-click conversation starters</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 pt-0">
              {quickActions.map((action, idx) => (
                <button
                  key={idx}
                  id={`quick-action-${idx}`}
                  onClick={() => sendMessage(action.prompt)}
                  disabled={isLoading}
                  className={`w-full p-3 rounded-xl border ${action.border} ${action.bg}/40 hover:${action.bg} hover:border-opacity-60 transition-all duration-200 text-left group disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-1.5 rounded-lg ${action.bg} flex-shrink-0`}>
                      <action.icon className={`h-3.5 w-3.5 ${action.color}`} />
                    </div>
                    <div className="min-w-0">
                      <p className={`font-semibold text-xs text-foreground group-hover:${action.color} transition-colors`}>
                        {action.title}
                      </p>
                      <p className="text-[11px] text-muted-foreground mt-0.5 leading-snug">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Profile context */}
          {user && (
            <Card id="ai-profile-card" className="border-border/50 bg-card/80">
              <CardContent className="pt-4 pb-4 space-y-2">
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                  Advising based on
                </p>
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 p-2 rounded-lg bg-muted/40">
                    <Zap className="h-3.5 w-3.5 text-primary flex-shrink-0" />
                    <span className="text-xs text-foreground font-medium truncate">{user.profile.title}</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 rounded-lg bg-muted/40">
                    <TrendingUp className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                    <span className="text-xs text-muted-foreground">{user.profile.experience}</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 rounded-lg bg-muted/40">
                    <Target className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                    <span className="text-xs text-muted-foreground">{user.profile.location}</span>
                  </div>
                </div>
                {user.profile.skills && user.profile.skills.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {user.profile.skills.slice(0, 4).map((s) => (
                      <Badge key={s.id} variant="secondary" className="text-[10px] h-4 px-1.5">
                        {s.name}
                      </Badge>
                    ))}
                    {user.profile.skills.length > 4 && (
                      <Badge variant="outline" className="text-[10px] h-4 px-1.5 text-muted-foreground">
                        +{user.profile.skills.length - 4}
                      </Badge>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Chat window */}
        <Card
          id="chat-window"
          className="lg:col-span-2 border-border/50 bg-card/80 flex flex-col"
          style={{ height: '72vh', minHeight: 480 }}
        >
          <CardHeader className="pb-3 border-b border-border/50 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm">Conversation</CardTitle>
                <CardDescription className="text-xs">
                  {messages.length - 1} messages
                </CardDescription>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Claude claude-sonnet-4-6
              </div>
            </div>
          </CardHeader>

          {/* Messages */}
          <CardContent className="p-0 flex-1 flex flex-col min-h-0">
            <ScrollArea id="chat-messages-area" className="flex-1 px-4 py-3">
              <div id="chat-messages" className="space-y-5">
                <AnimatePresence initial={false}>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      id={`msg-${message.id}`}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.25 }}
                      className="space-y-2"
                    >
                      <div
                        className={`flex gap-2.5 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`flex gap-2.5 max-w-[88%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                        >
                          {/* Avatar */}
                          <div
                            className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                              message.role === 'user'
                                ? 'bg-gradient-primary'
                                : message.error
                                ? 'bg-destructive/20'
                                : 'bg-gradient-primary'
                            } shadow-sm`}
                          >
                            {message.role === 'user' ? (
                              <User className="h-3.5 w-3.5 text-white" />
                            ) : message.error ? (
                              <AlertCircle className="h-3.5 w-3.5 text-destructive" />
                            ) : (
                              <Bot className="h-3.5 w-3.5 text-white" />
                            )}
                          </div>

                          {/* Bubble */}
                          <div
                            className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                              message.role === 'user'
                                ? 'bg-gradient-primary text-white rounded-tr-sm'
                                : message.error
                                ? 'bg-destructive/10 text-destructive border border-destructive/20 rounded-tl-sm'
                                : 'bg-card border border-border/50 text-foreground rounded-tl-sm'
                            }`}
                          >
                            <div className="whitespace-pre-line">
                              {formatContent(message.content)}
                            </div>
                            <div className={`text-[10px] mt-2 ${message.role === 'user' ? 'text-white/60 text-right' : 'text-muted-foreground'}`}>
                              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Suggestion chips */}
                      {message.role === 'assistant' && message.suggestions && !message.error && (
                        <div id={`chips-${message.id}`} className="flex flex-wrap gap-1.5 ml-11">
                          {message.suggestions.map((s, i) => (
                            <button
                              key={i}
                              onClick={() => sendMessage(s)}
                              disabled={isLoading}
                              className="text-xs px-3 py-1 rounded-full border border-border/60 hover:border-primary/50 hover:bg-primary/5 hover:text-primary text-muted-foreground transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {s}
                            </button>
                          ))}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>

                {isLoading && <TypingIndicator />}
                <div ref={bottomRef} />
              </div>
            </ScrollArea>

            {/* Input area */}
            <div id="chat-input-area" className="border-t border-border/50 p-3 flex-shrink-0">
              <div className="flex gap-2 items-end">
                <Textarea
                  ref={inputRef}
                  id="chat-textarea"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about careers, skills, or job strategies… (Enter to send)"
                  disabled={isLoading}
                  rows={2}
                  className="flex-1 resize-none min-h-[2.5rem] max-h-32 bg-muted/40 border-border/50 focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/30 text-sm placeholder:text-muted-foreground/60"
                />
                <Button
                  id="chat-send-btn"
                  onClick={() => sendMessage(inputMessage)}
                  disabled={isLoading || !inputMessage.trim()}
                  size="icon"
                  className="h-10 w-10 flex-shrink-0 bg-gradient-primary hover:opacity-90 border-0 shadow-glow disabled:shadow-none"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-[10px] text-muted-foreground/50 mt-2 text-center">
                Shift+Enter for new line · Claude has full context of your profile
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AIAssistant;
