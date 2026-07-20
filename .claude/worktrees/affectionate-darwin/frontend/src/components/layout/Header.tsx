import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Search, Settings, User, Menu, X, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useUserStore } from '@/store/useUserStore';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
}

export const Header = ({ onToggleSidebar, sidebarOpen }: HeaderProps) => {
  const { user } = useUserStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocused, setSearchFocused] = useState(false);

  const initials = user?.name
    ? user.name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : 'RM';

  return (
    <header
      id="site-header"
      className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/70"
    >
      {/* Subtle top-edge gradient */}
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-primary opacity-40" />

      <div id="header-inner" className="flex h-16 items-center justify-between px-4 lg:px-6 relative">
        {/* ── Left: Hamburger + Logo ── */}
        <div id="header-left" className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleSidebar}
            className="lg:hidden h-9 w-9 p-0 text-muted-foreground hover:text-foreground"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>

          <Link
            to="/"
            id="header-logo"
            className="flex items-center gap-2.5 group"
          >
            <div className="h-8 w-8 rounded-xl bg-gradient-primary flex items-center justify-center shadow-glow group-hover:scale-105 transition-transform duration-200">
              <Zap className="h-4 w-4 text-white" />
            </div>
            <div className="hidden lg:flex flex-col leading-none">
              <span className="font-extrabold text-sm tracking-tight text-gradient-primary">
                CareerAI
              </span>
              <span className="text-[10px] text-muted-foreground font-medium tracking-wide">
                by Rahul Mehta
              </span>
            </div>
          </Link>
        </div>

        {/* ── Center: Search ── */}
        <div id="header-search" className="flex-1 max-w-sm mx-4 hidden md:block">
          <div
            className={cn(
              'relative transition-all duration-200',
              searchFocused && 'scale-[1.01]'
            )}
          >
            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground pointer-events-none" />
            <Input
              id="header-search-input"
              placeholder="Search careers, jobs, skills…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
              className="pl-9 h-9 text-sm bg-muted/40 border-border/50 hover:border-primary/30 focus-visible:border-primary/50 focus-visible:ring-1 focus-visible:ring-primary/30 placeholder:text-muted-foreground/60"
            />
          </div>
        </div>

        {/* ── Right: Status + Notifications + User ── */}
        <div id="header-right" className="flex items-center gap-2">
          {/* AI Active indicator */}
          <div
            id="header-ai-status"
            className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20"
          >
            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-semibold text-emerald-500 tracking-wide">
              AI ACTIVE
            </span>
          </div>

          {/* Notifications */}
          <Button
            id="header-notifications"
            variant="ghost"
            size="sm"
            className="relative h-9 w-9 p-0 text-muted-foreground hover:text-foreground"
            aria-label="Notifications"
          >
            <Bell className="h-4.5 w-4.5" />
            <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-primary text-[9px] text-white flex items-center justify-center font-bold shadow-glow">
              3
            </span>
          </Button>

          {/* User dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                id="header-user-trigger"
                variant="ghost"
                className="relative h-9 w-9 rounded-full p-0 ring-1 ring-border/60 hover:ring-primary/40 transition-all"
                aria-label="User menu"
              >
                <Avatar className="h-8 w-8">
                  <AvatarImage src={user?.avatar} alt={user?.name} />
                  <AvatarFallback className="bg-gradient-primary text-white text-xs font-bold">
                    {initials}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              id="header-user-menu"
              className="w-56 border-border/70 bg-popover/95 backdrop-blur-xl shadow-xl"
              align="end"
              forceMount
            >
              {/* Profile summary */}
              <div
                id="header-user-profile"
                className="flex items-center gap-2.5 p-3 border-b border-border/50"
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-gradient-primary text-white text-xs font-bold">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col leading-none min-w-0">
                  <p className="font-semibold text-sm text-foreground">
                    {user?.name || 'Rahul Mehta'}
                  </p>
                  <p className="text-xs text-muted-foreground truncate max-w-[140px]">
                    {user?.email || 'rahul@example.com'}
                  </p>
                </div>
              </div>

              <DropdownMenuItem asChild className="mt-1">
                <Link to="/profile" className="flex items-center">
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/settings" className="flex items-center">
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive focus:text-destructive">
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};
