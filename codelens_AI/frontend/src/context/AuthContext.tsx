import React, { createContext, useContext, useState, useEffect } from 'react';
import { getMe, login as apiLogin, register as apiRegister } from '../api/auth';

interface User {
  id: number;
  email: string;
  full_name: string | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (formData: FormData) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const userData = await getMe();
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to fetch user', error);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async (formData: FormData) => {
    const data = await apiLogin(formData);
    localStorage.setItem('token', data.access_token);
    await fetchUser();
  };

  const register = async (data: any) => {
    await apiRegister(data);
    // Auto login after registration
    const formData = new FormData();
    formData.append('username', data.email);
    formData.append('password', data.password);
    await login(formData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
