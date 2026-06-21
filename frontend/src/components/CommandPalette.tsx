import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Compass,
  Briefcase,
  FileText,
  Mail,
  Mic,
  Bot,
  TrendingUp,
  Plus,
  Upload,
  Play,
  Clock,
} from 'lucide-react';
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
  CommandShortcut,
} from '@/components/ui/command';
import type { CommandItem as CommandItemType } from '@/types';

interface CommandPaletteItem extends Omit<CommandItemType, 'action'> {
  action: () => void;
  keywords?: string[];
}

const RECENT_SEARCHES_KEY = 'command-palette-recent';
const MAX_RECENT = 5;

export const CommandPalette = () => {
  const [open, setOpen] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const navigate = useNavigate();

  // Load recent searches from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
    if (stored) {
      try {
        setRecentSearches(JSON.parse(stored));
      } catch {
        setRecentSearches([]);
      }
    }
  }, []);

  // Handle keyboard shortcut
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const addRecentSearch = useCallback((title: string) => {
    setRecentSearches((prev) => {
      const filtered = prev.filter((item) => item !== title);
      const updated = [title, ...filtered].slice(0, MAX_RECENT);
      localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const handleSelect = useCallback(
    (item: CommandPaletteItem) => {
      addRecentSearch(item.title);
      setOpen(false);
      item.action();
    },
    [addRecentSearch]
  );

  const navigationItems: CommandPaletteItem[] = [
    {
      id: 'dashboard',
      title: 'Dashboard',
      description: 'View your career progress overview',
      icon: LayoutDashboard,
      shortcut: 'G D',
      action: () => navigate('/'),
      keywords: ['home', 'overview', 'main'],
    },
    {
      id: 'careers',
      title: 'Careers',
      description: 'Explore career paths and opportunities',
      icon: Compass,
      shortcut: 'G C',
      action: () => navigate('/careers'),
      keywords: ['explore', 'paths', 'opportunities'],
    },
    {
      id: 'jobs',
      title: 'Jobs',
      description: 'Search and browse job listings',
      icon: Briefcase,
      shortcut: 'G J',
      action: () => navigate('/jobs'),
      keywords: ['search', 'listings', 'positions', 'openings'],
    },
    {
      id: 'resume',
      title: 'Resume Builder',
      description: 'Build and analyze your resume',
      icon: FileText,
      shortcut: 'G R',
      action: () => navigate('/resume'),
      keywords: ['cv', 'curriculum', 'vitae', 'ats'],
    },
    {
      id: 'cover-letter',
      title: 'Cover Letter',
      description: 'Generate cover letters',
      icon: Mail,
      shortcut: 'G L',
      action: () => navigate('/cover-letter'),
      keywords: ['letter', 'application', 'generate'],
    },
    {
      id: 'interview-prep',
      title: 'Interview Prep',
      description: 'Practice interview questions',
      icon: Mic,
      shortcut: 'G I',
      action: () => navigate('/interview'),
      keywords: ['practice', 'questions', 'mock'],
    },
    {
      id: 'ai-assistant',
      title: 'AI Assistant',
      description: 'Chat with your AI career advisor',
      icon: Bot,
      shortcut: 'G A',
      action: () => navigate('/assistant'),
      keywords: ['chat', 'help', 'advisor', 'ai'],
    },
    {
      id: 'progress',
      title: 'Progress',
      description: 'Track your career development',
      icon: TrendingUp,
      shortcut: 'G P',
      action: () => navigate('/progress'),
      keywords: ['tracking', 'analytics', 'stats', 'milestones'],
    },
  ];

  const actionItems: CommandPaletteItem[] = [
    {
      id: 'upload-resume',
      title: 'Upload Resume',
      description: 'Upload and analyze your resume',
      icon: Upload,
      shortcut: 'U R',
      action: () => navigate('/resume'),
      keywords: ['import', 'cv', 'document', 'ats'],
    },
    {
      id: 'generate-cover-letter',
      title: 'Generate Cover Letter',
      description: 'Create a new cover letter',
      icon: Plus,
      shortcut: 'N L',
      action: () => navigate('/cover-letter'),
      keywords: ['create', 'write', 'letter'],
    },
    {
      id: 'start-mock-interview',
      title: 'Start Mock Interview',
      description: 'Begin a practice interview session',
      icon: Play,
      shortcut: 'M I',
      action: () => navigate('/interview'),
      keywords: ['practice', 'simulate', 'prepare'],
    },
  ];

  const recentItems: CommandPaletteItem[] = recentSearches
    .map((title) => {
      const allItems = [...navigationItems, ...actionItems];
      return allItems.find((item) => item.title === title);
    })
    .filter((item): item is CommandPaletteItem => item !== undefined);

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        {recentItems.length > 0 && (
          <>
            <CommandGroup heading="Recent">
              {recentItems.map((item) => {
                const Icon = item.icon;
                return (
                  <CommandItem
                    key={`recent-${item.id}`}
                    value={item.title}
                    onSelect={() => handleSelect(item)}
                    className="flex items-center gap-3 px-3 py-2.5"
                  >
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
                    <div className="flex flex-col gap-0.5">
                      <span className="text-sm font-medium">{item.title}</span>
                      {item.description && (
                        <span className="text-xs text-muted-foreground">
                          {item.description}
                        </span>
                      )}
                    </div>
                    {item.shortcut && (
                      <CommandShortcut>{item.shortcut}</CommandShortcut>
                    )}
                  </CommandItem>
                );
              })}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        <CommandGroup heading="Navigation">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <CommandItem
                key={item.id}
                value={`${item.title} ${item.keywords?.join(' ') || ''}`}
                onSelect={() => handleSelect(item)}
                className="flex items-center gap-3 px-3 py-2.5"
              >
                {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
                <div className="flex flex-col gap-0.5">
                  <span className="text-sm font-medium">{item.title}</span>
                  {item.description && (
                    <span className="text-xs text-muted-foreground">
                      {item.description}
                    </span>
                  )}
                </div>
                {item.shortcut && (
                  <CommandShortcut>{item.shortcut}</CommandShortcut>
                )}
              </CommandItem>
            );
          })}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Actions">
          {actionItems.map((item) => {
            const Icon = item.icon;
            return (
              <CommandItem
                key={item.id}
                value={`${item.title} ${item.keywords?.join(' ') || ''}`}
                onSelect={() => handleSelect(item)}
                className="flex items-center gap-3 px-3 py-2.5"
              >
                {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
                <div className="flex flex-col gap-0.5">
                  <span className="text-sm font-medium">{item.title}</span>
                  {item.description && (
                    <span className="text-xs text-muted-foreground">
                      {item.description}
                    </span>
                  )}
                </div>
                {item.shortcut && (
                  <CommandShortcut>{item.shortcut}</CommandShortcut>
                )}
              </CommandItem>
            );
          })}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
};
