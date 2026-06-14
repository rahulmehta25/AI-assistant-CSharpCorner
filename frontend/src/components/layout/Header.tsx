import { Link } from 'react-router-dom';
import { Bell, Menu, X, Command } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useUserStore } from '@/store/useUserStore';

interface HeaderProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
}

export const Header = ({ onToggleSidebar, sidebarOpen }: HeaderProps) => {
  const { user } = useUserStore();

  const openCommandPalette = () => {
    const event = new KeyboardEvent('keydown', {
      key: 'k',
      metaKey: true,
      bubbles: true,
    });
    document.dispatchEvent(event);
  };

  return (
    <header className="sticky top-0 z-50 h-14 border-b bg-background">
      <div className="flex h-full items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleSidebar}
            className="lg:hidden h-8 w-8"
          >
            {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </Button>

          <Link to="/" className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-md bg-primary flex items-center justify-center">
              <span className="text-xs font-semibold text-primary-foreground">CA</span>
            </div>
            <span className="hidden font-semibold sm:inline-block">
              Career Assistant
            </span>
          </Link>
        </div>

        <div className="flex items-center gap-2">
          {/* Search trigger */}
          <Button
            variant="outline"
            size="sm"
            onClick={openCommandPalette}
            className="hidden md:flex items-center gap-2 text-muted-foreground h-8 px-3"
          >
            <Command className="h-3 w-3" />
            <span className="text-xs">Search...</span>
            <kbd className="pointer-events-none hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 text-[10px] font-medium text-muted-foreground sm:flex">
              K
            </kbd>
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="h-8 w-8 relative">
            <Bell className="h-4 w-4" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-primary" />
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full">
                <Avatar className="h-7 w-7">
                  <AvatarImage src={user?.avatar} alt={user?.name} />
                  <AvatarFallback className="text-xs bg-muted">
                    {user?.name?.charAt(0) || 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <div className="px-2 py-1.5">
                <p className="text-sm font-medium">{user?.name}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/profile">Profile</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/settings">Settings</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive">Sign out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};
