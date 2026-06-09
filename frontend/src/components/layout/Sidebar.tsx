import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Home,
  Compass,
  Briefcase,
  FileText,
  TrendingUp,
  Settings,
  HelpCircle,
  Bot,
  Brain,
  PenTool,
  MessageSquare,
  BarChart3
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const mainItems = [
  { title: 'Dashboard', href: '/', icon: Home },
  { title: 'Careers', href: '/careers', icon: Compass },
  { title: 'Jobs', href: '/jobs', icon: Briefcase },
  { title: 'Progress', href: '/progress', icon: BarChart3 },
];

const toolsItems = [
  { title: 'AI Assistant', href: '/assistant', icon: Bot },
  { title: 'Resume Builder', href: '/resume', icon: FileText },
  { title: 'Cover Letter', href: '/cover-letter', icon: PenTool },
  { title: 'Interview Prep', href: '/interview', icon: MessageSquare },
  { title: 'Skills', href: '/skills', icon: Brain },
];

const bottomItems = [
  { title: 'Settings', href: '/settings', icon: Settings },
  { title: 'Help', href: '/help', icon: HelpCircle },
];

export const Sidebar = ({ open, onClose }: SidebarProps) => {
  const location = useLocation();

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/';
    return location.pathname.startsWith(href);
  };

  const NavItem = ({ item }: { item: typeof mainItems[0] }) => {
    const active = isActive(item.href);
    return (
      <Link
        to={item.href}
        onClick={onClose}
        className={cn(
          'relative flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
          active
            ? 'text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground hover:bg-muted'
        )}
      >
        {active && (
          <motion.div
            layoutId="sidebar-indicator"
            className="absolute inset-0 bg-primary rounded-lg"
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        )}
        <item.icon className="h-4 w-4 relative z-10" />
        <span className="relative z-10">{item.title}</span>
      </Link>
    );
  };

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-14 left-0 z-50 h-[calc(100vh-3.5rem)] w-56 transform border-r bg-background transition-transform duration-200 lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col py-4">
          {/* Main Navigation */}
          <nav className="px-3 space-y-1">
            <p className="px-3 mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Main
            </p>
            {mainItems.map((item) => (
              <NavItem key={item.href} item={item} />
            ))}
          </nav>

          <div className="my-4 mx-3 border-t" />

          {/* Tools Navigation */}
          <nav className="px-3 space-y-1">
            <p className="px-3 mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Tools
            </p>
            {toolsItems.map((item) => (
              <NavItem key={item.href} item={item} />
            ))}
          </nav>

          {/* Bottom Navigation */}
          <nav className="mt-auto px-3 space-y-1 border-t pt-4">
            {bottomItems.map((item) => (
              <NavItem key={item.href} item={item} />
            ))}
          </nav>

          {/* Keyboard shortcut hint */}
          <div className="px-6 py-3 border-t animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
            <p className="text-xs text-muted-foreground">
              Press{' '}
              <kbd className="inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] font-medium bg-muted rounded border border-border/80 shadow-sm hover:bg-muted/80 transition-colors">
                <span className="text-[11px]">&#8984;</span>K
              </kbd>{' '}
              for quick navigation
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};
