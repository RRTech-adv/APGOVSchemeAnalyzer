import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  username: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUsername = localStorage.getItem('auth_username');
    
    if (storedToken && storedUsername) {
      setToken(storedToken);
      setUsername(storedUsername);
    }
    
    setLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const { api } = await import('@/lib/api');
      const response = await api.login(username, password);
      
      if (response && response.access_token) {
        setToken(response.access_token);
        setUsername(response.username || username);
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('auth_username', response.username || username);
        return true;
      }
      console.error('Login failed: No access token in response', response);
      return false;
    } catch (error) {
      console.error('Login error:', error);
      if (error instanceof Error) {
        console.error('Error details:', error.message);
      }
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    setUsername(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_username');
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
        token,
        username,
        login,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

