import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { api } from '../api/client';
import { useTranslation } from 'react-i18next';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAdmin: boolean;
  isOperator: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const cached = localStorage.getItem('bt_user');
    return cached ? JSON.parse(cached) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('bt_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { i18n } = useTranslation();

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          const profile = await api.getCurrentUser();
          setUser(profile);
          localStorage.setItem('bt_user', JSON.stringify(profile));
          if (profile.preferred_language) {
            i18n.changeLanguage(profile.preferred_language);
            localStorage.setItem('bt_language', profile.preferred_language);
          }
        } catch {
          logout();
        }
      }
      setIsLoading(false);
    };
    fetchUser();
  }, [token]);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const tokenRes = await api.login(formData);
      localStorage.setItem('bt_token', tokenRes.access_token);
      setToken(tokenRes.access_token);

      const profile = await api.getCurrentUser();
      setUser(profile);
      localStorage.setItem('bt_user', JSON.stringify(profile));
      if (profile.preferred_language) {
        i18n.changeLanguage(profile.preferred_language);
        localStorage.setItem('bt_language', profile.preferred_language);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('bt_token');
    localStorage.removeItem('bt_user');
    setToken(null);
    setUser(null);
  };

  const isAdmin = user?.role === 'administrator';
  const isOperator = user?.role === 'operator';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isLoading,
        isAdmin,
        isOperator,
      }}
    >
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

