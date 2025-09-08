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
  Brain
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const navigationItems = [
  {
    title: 'Dashboard',
    href: '/',
    icon: Home,
    badge: null,
  },
  {
    title: 'Career Explorer',
    href: '/careers',
    icon: Compass,
    badge: 'New',
  },
  {
    title: 'Job Search',
    href: '/jobs',
    icon: Briefcase,
    badge: '12',
  },
  {
    title: 'Skills Analysis',
    href: '/skills',
    icon: Brain,
    badge: null,
  },
  {
    title: 'AI Assistant',
    href: '/assistant',
    icon: Bot,
    badge: 'Beta',
  },
  {
    title: 'Student Pathways',
    href: '/pathways',
    icon: GraduationCap,
    badge: null,
  },
  {
    title: 'Applications',
    href: '/applications',
    icon: FileText,
    badge: '3',
  },
];

const secondaryItems = [
  {
    title: 'Learning Hub',
    href: '/learning',
    icon: BookOpen,
    badge: null,
  },
  {
    title: 'Achievements',
    href: '/achievements',
    icon: Award,
    badge: null,
  },
  {
    title: 'Analytics',
    href: '/analytics',
    icon: TrendingUp,
    badge: null,
  },
];

const bottomItems = [
  {
    title: 'Settings',
    href: '/settings',
    icon: Settings,
    badge: null,
  },
  {
    title: 'Help & Support',
    href: '/help',
    icon: HelpCircle,
    badge: null,
  },
];

export const Sidebar = ({ open, onClose }: SidebarProps) => {
  const location = useLocation();

  const NavItem = ({ item, isActive }: { item: typeof navigationItems[0]; isActive: boolean }) => (
    <Link
      to={item.href}
      onClick={onClose}
      className={cn(
        'flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 group',
        isActive
          ? 'bg-primary text-primary-foreground shadow-md'
          : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
      )}
    >
      <div className="flex items-center space-x-3">
        <item.icon className={cn(
          'h-5 w-5 transition-colors',
          isActive ? 'text-primary-foreground' : 'text-muted-foreground group-hover:text-foreground'
        )} />
        <span>{item.title}</span>
      </div>
      {item.badge && (
        <Badge 
          variant={isActive ? "secondary" : "outline"} 
          className={cn(
            'h-5 px-2 text-xs',
            isActive ? 'bg-primary-foreground/20 text-primary-foreground border-primary-foreground/20' : ''
          )}
        >
          {item.badge}
        </Badge>
      )}
    </Link>
  );

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
          'fixed top-16 left-0 z-50 h-[calc(100vh-4rem)] w-64 transform border-r bg-card transition-transform duration-300 ease-in-out lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-full flex-col p-4">
          {/* Main Navigation */}
          <nav className="space-y-1">
            <div className="pb-2">
              <h3 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Main
              </h3>
            </div>
            {navigationItems.map((item) => (
              <NavItem
                key={item.href}
                item={item}
                isActive={location.pathname === item.href || (item.href === '/careers' && location.pathname.startsWith('/careers'))}
              />
            ))}
          </nav>

          {/* Divider */}
          <div className="my-4 border-t" />

          {/* Secondary Navigation */}
          <nav className="space-y-1">
            <div className="pb-2">
              <h3 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Tools
              </h3>
            </div>
            {secondaryItems.map((item) => (
              <NavItem
                key={item.href}
                item={item}
                isActive={location.pathname === item.href}
              />
            ))}
          </nav>

          {/* Bottom Navigation */}
          <div className="mt-auto">
            <div className="border-t pt-4">
              <nav className="space-y-1">
                {bottomItems.map((item) => (
                  <NavItem
                    key={item.href}
                    item={item}
                    isActive={location.pathname === item.href}
                  />
                ))}
              </nav>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};