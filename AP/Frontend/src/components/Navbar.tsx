import { MessageSquare, Home, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import apLogo from "@/assets/ap-logo.png";

interface NavbarProps {
  onChatClick: () => void;
}

const Navbar = ({ onChatClick }: NavbarProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { username, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-card border-b border-border shadow-card sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title - Clickable to go to dashboard */}
          <div 
            className="flex items-center space-x-4 cursor-pointer hover:opacity-80 transition-opacity"
            onClick={() => navigate('/dashboard')}
          >
            <img src={apLogo} alt="AP Government" className="h-10 w-10" />
            <div className="flex flex-col">
              <h1 className="text-lg font-semibold text-foreground leading-tight">
                Development Dashboard
              </h1>
              <p className="text-xs text-muted-foreground">
                Government of Arunachal Pradesh
              </p>
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="flex items-center space-x-2">
            {location.pathname !== '/' && (
              <Button 
                variant="ghost" 
                size="icon"
                onClick={() => navigate('/')}
                title="Home"
              >
                <Home className="h-5 w-5" />
                <span className="sr-only">Home</span>
              </Button>
            )}
            <Button 
              variant="ghost" 
              size="icon"
              onClick={onChatClick}
              className="relative"
              title="Chat"
            >
              <MessageSquare className="h-5 w-5" />
              <span className="sr-only">Open Chat</span>
            </Button>
            
            {/* User info and logout */}
            {username && (
              <>
                <div className="flex items-center space-x-2 px-3 py-1 rounded-md bg-muted">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">{username}</span>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={handleLogout}
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                  <span className="sr-only">Logout</span>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
