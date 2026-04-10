import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Compass,
  GraduationCap,
  Briefcase,
  Target,
  FileText,
  TrendingUp,
  BookOpen,
  Award,
  Settings,
  HelpCircle,
  Bot,
  Brain,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const navigationItems = [
  { title: 'Dashboard',       href: '/',            icon: Home,         badge: null    },
  { title: 'Career Explorer', href: '/careers',     icon: Compass,      badge: 'New'   },
  { title: 'Job Search',      href: '/jobs',        icon: Briefcase,    badge: '12'    },
  { title: 'Skills Analysis', href: '/skills',      icon: Brain,        badge: null    },
  { title: 'AI Assistant',    href: '/assistant',   icon: Bot,          badge: 'Beta'  },
  { title: 'Pathways',        href: '/pathways',    icon: GraduationCap,badge: null    },
  { title: 'Applications',    href: '/applications',icon: FileText,     badge: '3'     },
];

const secondaryItems = [
  { title: 'Learning Hub',    href: '/learning',    icon: BookOpen,     badge: null },
  { title: 'Achievements',    href: '/achievements',icon: Award,        badge: null },
  { title: 'Analytics',       href: '/analytics',   icon: TrendingUp,   badge: null },
];

const bottomItems = [
  { title: 'Settings',        href: '/settings',    icon: Settings,     badge: null },
  { title: 'Help & Support',  href: '/help',        icon: HelpCircle,   badge: null },
];

type NavItem = typeof navigationItems[number];

const NavLink = ({
  item,
  isActive,
  onClose,
}: {
  item: NavItem;
  isActive: boolean;
  onClose: () => void;
}) => (
  <Link
    to={item.href}
    onClick={onClose}
    id={`nav-${item.href.replace(/\//g, '') || 'home'}`}
    className={cn(
      'relative flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group select-none',
      isActive
        ? 'bg-primary/12 text-primary'
        : 'text-muted-foreground hover:text-foreground hover:bg-muted/40'
    )}
  >
    {/* Active indicator stripe */}
    {isActive && (
      <div className="absolute left-0 inset-y-2.5 w-0.5 rounded-r-full bg-primary" />
    )}

    <div className="flex items-center gap-3 min-w-0">
      <item.icon
        className={cn(
          'h-4 w-4 flex-shrink-0 transition-colors',
          isActive
            ? 'text-primary'
            : 'text-muted-foreground/70 group-hover:text-foreground'
        )}
      />
      <span className="truncate">{item.title}</span>
    </div>

    {item.badge && (
      <Badge
        variant={isActive ? 'default' : 'outline'}
        className={cn(
          'h-4 px-1.5 text-[10px] font-semibold flex-shrink-0 ml-1',
          isActive
            ? 'bg-primary/25 text-primary border-primary/30 hover:bg-primary/25'
            : 'border-border/60 text-muted-foreground'
        )}
      >
        {item.badge}
      </Badge>
    )}
  </Link>
);

export const Sidebar = ({ open, onClose }: SidebarProps) => {
  const location = useLocation();

  const isActive = (href: string) =>
    href === '/'
      ? location.pathname === '/'
      : location.pathname === href || location.pathname.startsWith(href + '/');

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          id="sidebar-overlay"
          className="fixed inset-0 z-40 bg-background/70 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar panel */}
      <aside
        id="sidebar-panel"
        className={cn(
          'fixed top-16 left-0 z-50 h-[calc(100vh-4rem)] w-64 transform border-r border-border/50 bg-sidebar transition-transform duration-300 ease-in-out lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Subtle inner glow at top */}
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-primary opacity-20" />

        <div id="sidebar-content" className="flex h-full flex-col p-3 overflow-y-auto">
          {/* ── Main navigation ── */}
          <nav id="sidebar-main-nav" className="space-y-0.5">
            <p className="px-3 pb-2 pt-1 text-[10px] font-bold text-muted-foreground/50 uppercase tracking-widest">
              Main
            </p>
            {navigationItems.map((item) => (
              <NavLink
                key={item.href}
                item={item}
                isActive={isActive(item.href)}
                onClose={onClose}
              />
            ))}
          </nav>

          <div className="my-3 border-t border-border/40" />

          {/* ── Tools ── */}
          <nav id="sidebar-tools-nav" className="space-y-0.5">
            <p className="px-3 pb-2 text-[10px] font-bold text-muted-foreground/50 uppercase tracking-widest">
              Tools
            </p>
            {secondaryItems.map((item) => (
              <NavLink
                key={item.href}
                item={item}
                isActive={isActive(item.href)}
                onClose={onClose}
              />
            ))}
          </nav>

          {/* ── Push bottom items down ── */}
          <div className="flex-1" />

          {/* Upgrade / promo card */}
          <div
            id="sidebar-promo"
            className="mx-1 mb-3 p-3 rounded-xl border border-primary/20 bg-primary/5"
          >
            <p className="text-xs font-semibold text-foreground mb-0.5">Resume Review</p>
            <p className="text-[11px] text-muted-foreground mb-2 leading-snug">
              AI-powered feedback in seconds
            </p>
            <Link
              to="/assistant"
              onClick={onClose}
              className="block text-center text-[11px] font-semibold text-primary hover:text-primary-light transition-colors py-1 px-2 bg-primary/10 rounded-md"
            >
              Try it free →
            </Link>
          </div>

          {/* ── Bottom nav ── */}
          <div id="sidebar-bottom-nav" className="border-t border-border/40 pt-3 space-y-0.5">
            {bottomItems.map((item) => (
              <NavLink
                key={item.href}
                item={item}
                isActive={isActive(item.href)}
                onClose={onClose}
              />
            ))}
          </div>
        </div>
      </aside>
    </>
  );
};
