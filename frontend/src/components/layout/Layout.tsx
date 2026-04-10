/**
 * Layout.tsx
 * Root shell component that wraps all authenticated routes.
 * Uses Outlet from react-router-dom to render child routes.
 *
 * Usage: App.tsx renders <Layout /> as the parent route element.
 * All child pages are injected via <Outlet />.
 */

import { useState } from 'react';
import { Outlet, NavLink, useMatch, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  Search,
  BarChart2,
  Bot,
  GitBranch,
  ClipboardList,
  BookOpen,
  Award,
  LineChart,
  Settings,
  HelpCircle,
  User,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const primaryNavItems: NavItem[] = [
  { to: '/',            icon: <LayoutDashboard className="h-4 w-4" />, label: 'Dashboard' },
  { to: '/careers',     icon: <Briefcase className="h-4 w-4" />,       label: 'Career Explorer' },
  { to: '/jobs',        icon: <Search className="h-4 w-4" />,          label: 'Job Search' },
  { to: '/skills',      icon: <BarChart2 className="h-4 w-4" />,       label: 'Skills Analysis' },
  { to: '/assistant',   icon: <Bot className="h-4 w-4" />,             label: 'AI Assistant' },
  { to: '/pathways',    icon: <GitBranch className="h-4 w-4" />,       label: 'Pathways' },
  { to: '/applications',icon: <ClipboardList className="h-4 w-4" />,   label: 'Applications' },
  { to: '/learning',    icon: <BookOpen className="h-4 w-4" />,        label: 'Learning' },
  { to: '/achievements',icon: <Award className="h-4 w-4" />,           label: 'Achievements' },
  { to: '/analytics',   icon: <LineChart className="h-4 w-4" />,       label: 'Analytics' },
];

const secondaryNavItems: NavItem[] = [
  { to: '/profile',  icon: <User className="h-4 w-4" />,     label: 'Profile' },
  { to: '/settings', icon: <Settings className="h-4 w-4" />, label: 'Settings' },
  { to: '/help',     icon: <HelpCircle className="h-4 w-4" />,label: 'Help' },
];

export function Layout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div id="layout-root" className="flex h-screen bg-background overflow-hidden">
      <a
        href="#layout-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-2 focus:bg-primary focus:text-primary-foreground focus:rounded focus:top-2 focus:left-2"
      >
        Skip to main content
      </a>
      {/* Sidebar */}
      <aside
        id="layout-sidebar"
        className={cn(
          'flex flex-col border-r border-border/60 bg-[hsl(var(--sidebar-background))] transition-all duration-300 ease-in-out flex-shrink-0',
          collapsed ? 'w-[60px]' : 'w-[220px]'
        )}
      >
        {/* Brand / Header */}
        <div
          id="sidebar-header"
          className={cn(
            'flex items-center h-14 px-3 border-b border-border/60 flex-shrink-0',
            collapsed ? 'justify-center' : 'justify-between'
          )}
        >
          {!collapsed && (
            <div id="sidebar-brand" className="flex items-center gap-2 overflow-hidden">
              <div className="flex-shrink-0 h-7 w-7 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Sparkles className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="font-semibold text-sm truncate text-foreground">
                Career AI
              </span>
            </div>
          )}
          {collapsed && (
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Sparkles className="h-3.5 w-3.5 text-white" />
            </div>
          )}
          {!collapsed && (
            <Button
              id="sidebar-collapse-btn"
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-muted-foreground hover:text-foreground"
              onClick={() => setCollapsed(true)}
              aria-label="Collapse sidebar"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Expand button when collapsed */}
        {collapsed && (
          <div className="flex justify-center pt-2">
            <Button
              id="sidebar-expand-btn"
              variant="ghost"
              size="icon"
              className="h-6 w-6 text-muted-foreground hover:text-foreground"
              onClick={() => setCollapsed(false)}
              aria-label="Expand sidebar"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}

        {/* Primary Nav */}
        <nav
          id="sidebar-primary-nav"
          className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5"
          aria-label="Primary navigation"
        >
          {primaryNavItems.map((item) => (
            <SidebarNavLink
              key={item.to}
              item={item}
              collapsed={collapsed}
            />
          ))}
        </nav>

        <Separator className="bg-border/60" />

        {/* Secondary Nav */}
        <nav
          id="sidebar-secondary-nav"
          className="py-2 px-2 space-y-0.5"
          aria-label="Account navigation"
        >
          {secondaryNavItems.map((item) => (
            <SidebarNavLink
              key={item.to}
              item={item}
              collapsed={collapsed}
            />
          ))}
        </nav>
      </aside>

      {/* Main content area */}
      <div id="layout-main" className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Top header bar */}
        <header
          id="layout-header"
          className="h-14 flex-shrink-0 border-b border-border/60 flex items-center px-6 bg-background/80 backdrop-blur-sm"
        >
          <div id="layout-header-inner" className="flex items-center justify-between w-full">
            <div id="header-breadcrumb" className="text-sm text-muted-foreground">
              {/* Intentionally minimal — child pages own their headings */}
            </div>
            <div id="header-actions" className="flex items-center gap-2">
              <div
                id="header-user-avatar"
                className="h-7 w-7 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white text-xs font-semibold cursor-pointer"
                role="button"
                tabIndex={0}
                aria-label="User profile"
              >
                U
              </div>
            </div>
          </div>
        </header>

        {/* Page content — Outlet renders the matched child route */}
        <main
          id="layout-content"
          className="flex-1 overflow-y-auto p-6"
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}

/* ── Helper sub-component ──────────────────────────── */

interface SidebarNavLinkProps {
  item: NavItem;
  collapsed: boolean;
}

function SidebarNavLink({ item, collapsed }: SidebarNavLinkProps) {
  const isActive = !!useMatch(item.to === '/' ? { path: item.to, end: true } : item.to);

  return (
    <NavLink
      to={item.to}
      end={item.to === '/'}
      aria-current={isActive ? 'page' : undefined}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 rounded-md px-2 py-1.5 text-sm font-medium transition-colors duration-150',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          isActive
            ? 'bg-[hsl(var(--sidebar-accent))] text-primary'
            : 'text-[hsl(var(--sidebar-foreground))] hover:bg-[hsl(var(--sidebar-accent))] hover:text-foreground',
          collapsed && 'justify-center px-0'
        )
      }
      aria-label={collapsed ? item.label : undefined}
      title={collapsed ? item.label : undefined}
    >
      {({ isActive }) => (
        <>
          <span
            className={cn(
              'flex-shrink-0 transition-colors duration-150',
              isActive ? 'text-primary' : 'text-[hsl(var(--sidebar-foreground))]'
            )}
            aria-hidden="true"
          >
            {item.icon}
          </span>
          {!collapsed && (
            <span className="truncate">
              {item.label}
              {isActive && <span className="sr-only"> (current page)</span>}
            </span>
          )}
        </>
      )}
    </NavLink>
  );
}
