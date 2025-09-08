import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Bot, Send, User, Sparkles, MessageCircle, BookOpen, Target, TrendingUp } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: string[];
}

const AIAssistant = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your AI Career Assistant. I'm here to help you with career planning, skill development, job search strategies, and more. What would you like to discuss today?",
      timestamp: new Date(),
      suggestions: [
        "Help me choose a career path",
        "Review my skills and suggest improvements", 
        "Find jobs that match my profile",
        "Create a learning roadmap"
      ]
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const quickActions = [
    {
      title: "Career Path Guidance",
      description: "Get personalized career recommendations",
      icon: Target,
      color: "bg-blue-100 text-blue-700",
      prompt: "Help me explore different career paths based on my interests and skills"
    },
    {
      title: "Skill Assessment",
      description: "Analyze your current skills and gaps",
      icon: TrendingUp,
      color: "bg-emerald-100 text-emerald-700",
      prompt: "Analyze my current skills and identify areas for improvement"
    },
    {
      title: "Learning Roadmap",
      description: "Create a personalized learning plan",
      icon: BookOpen,
      color: "bg-purple-100 text-purple-700",
      prompt: "Create a learning roadmap for my target career in software engineering"
    },
    {
      title: "Interview Prep",
      description: "Practice interviews and get feedback",
      icon: MessageCircle,
      color: "bg-amber-100 text-amber-700",
      prompt: "Help me prepare for technical interviews in my field"
    }
  ];

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate AI response (in real app, this would call your backend API)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: generateAIResponse(content),
        timestamp: new Date(),
        suggestions: generateSuggestions(content)
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('career') || input.includes('path')) {
      return "Based on your profile, I can see you have strong technical skills in JavaScript and Python. Here are some career paths that might interest you:\n\n• **Software Engineer** - Great match for your programming skills\n• **Data Scientist** - Leverage your Python experience\n• **Full-Stack Developer** - Combine frontend and backend skills\n\nWould you like me to create a detailed roadmap for any of these paths?";
    }
    
    if (input.includes('skill') || input.includes('improve')) {
      return "Looking at your current skill set, here's my analysis:\n\n**Strengths:**\n• Strong foundation in JavaScript and Python\n• Good understanding of React basics\n\n**Areas for Growth:**\n• Advanced React patterns (hooks, context)\n• Backend development (Node.js, databases)\n• DevOps and deployment skills\n\nI recommend focusing on backend development next to become a full-stack developer. Would you like specific learning resources?";
    }

    if (input.includes('job') || input.includes('search')) {
      return "I can help you optimize your job search! Here's what I recommend:\n\n1. **Update your profile** to highlight your JavaScript and Python skills\n2. **Target junior developer roles** that match your experience level\n3. **Focus on companies** that value growth and learning\n\nBased on your location (San Francisco) and skills, you should look at:\n• Startups in the Bay Area\n• Tech companies with junior programs\n• Remote-friendly organizations\n\nWould you like me to help you find specific job openings?";
    }

    if (input.includes('interview') || input.includes('prepare')) {
      return "Great! Let's prepare you for technical interviews. Here's a structured approach:\n\n**Technical Skills to Review:**\n• JavaScript fundamentals and ES6+ features\n• React component lifecycle and hooks\n• Python data structures and algorithms\n• Basic system design concepts\n\n**Practice Plan:**\n1. Code challenges on LeetCode (easy/medium)\n2. Build a small project to showcase\n3. Practice explaining your code\n4. Mock interviews with peers\n\nWant me to suggest specific coding problems to practice?";
    }

    return "That's a great question! I'm here to help you with all aspects of your career development. Whether it's choosing a career path, developing skills, finding jobs, or preparing for interviews, I can provide personalized guidance based on your profile and goals. What specific area would you like to explore further?";
  };

  const generateSuggestions = (userInput: string): string[] => {
    const input = userInput.toLowerCase();
    
    if (input.includes('career')) {
      return [
        "Show me the software engineer roadmap",
        "What about data science careers?", 
        "Help me compare different tech roles"
      ];
    }
    
    if (input.includes('skill')) {
      return [
        "Create a learning plan for React",
        "Find courses for backend development",
        "What skills do I need for senior roles?"
      ];
    }

    return [
      "Tell me more about this",
      "Show me examples",
      "What's the next step?"
    ];
  };

  const handleQuickAction = (prompt: string) => {
    handleSendMessage(prompt);
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-4">
          <Bot className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            AI Career Assistant
          </h1>
        </div>
        <p className="text-xl text-muted-foreground">
          Get personalized career guidance, skill recommendations, and job search strategies
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions Sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Quick Actions
            </CardTitle>
            <CardDescription>Start a conversation with one click</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="w-full p-4 h-auto justify-start"
                  onClick={() => handleQuickAction(action.prompt)}
                >
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${action.color}`}>
                      <action.icon className="h-4 w-4" />
                    </div>
                    <div className="text-left">
                      <p className="font-medium text-foreground">{action.title}</p>
                      <p className="text-xs text-muted-foreground">{action.description}</p>
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Chat Interface */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Chat with AI Assistant</CardTitle>
            <CardDescription>Ask me anything about your career development</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[500px] p-6">
              <div className="space-y-6">
                {messages.map((message) => (
                  <div key={message.id} className="space-y-3">
                    <div className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`flex gap-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                          message.role === 'user' 
                            ? 'bg-primary text-primary-foreground' 
                            : 'bg-muted text-muted-foreground'
                        }`}>
                          {message.role === 'user' ? (
                            <User className="h-4 w-4" />
                          ) : (
                            <Bot className="h-4 w-4" />
                          )}
                        </div>
                        <div className={`rounded-lg p-4 ${
                          message.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-muted-foreground'
                        }`}>
                          <div className="text-sm whitespace-pre-line">
                            {message.content}
                          </div>
                          <div className="text-xs opacity-70 mt-2">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Suggestions */}
                    {message.role === 'assistant' && message.suggestions && (
                      <div className="flex flex-wrap gap-2 ml-11">
                        {message.suggestions.map((suggestion, index) => (
                          <Button
                            key={index}
                            variant="outline"
                            size="sm"
                            className="text-xs"
                            onClick={() => handleSuggestionClick(suggestion)}
                          >
                            {suggestion}
                          </Button>
                        ))}
                      </div>
                    )}

                    {message.id !== messages[messages.length - 1].id && (
                      <Separator className="my-6" />
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                      <Bot className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="bg-muted rounded-lg p-4">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            <div className="border-t p-6">
              <div className="flex gap-2">
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask me about your career, skills, job search..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage(inputMessage);
                    }
                  }}
                  disabled={isLoading}
                />
                <Button 
                  onClick={() => handleSendMessage(inputMessage)}
                  disabled={isLoading || !inputMessage.trim()}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AIAssistant;