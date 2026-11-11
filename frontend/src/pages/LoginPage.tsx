import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sun, Lock, User, Globe, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const toggleLanguage = () => {
    const nextLang = i18n.language === 'en' ? 'sw' : 'en';
    i18n.changeLanguage(nextLang);
    localStorage.setItem('bt_language', nextLang);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch {
      setError(t('auth.invalidCredentials'));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setError(null);
    setLoading(true);
    try {
      await login(u, p);
      navigate('/');
    } catch {
      setError(t('auth.invalidCredentials'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-background to-amber-50/40 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Top language toggle */}
      <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
        <Button
          variant="outline"
          size="sm"
          onClick={toggleLanguage}
          className="bg-card text-foreground shadow-2xs"
        >
          <Globe className="w-4 h-4 mr-1.5 text-brand-600" />
          {i18n.language === 'en' ? 'English (EN)' : 'Kiswahili (SW)'}
        </Button>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-solar-500 flex items-center justify-center text-white shadow-lg">
          <Sun className="w-10 h-10" />
        </div>
        <h2 className="mt-4 text-center text-3xl font-extrabold tracking-tight text-foreground">
          {t('app.title')}
        </h2>
        <p className="mt-1 text-center text-sm font-medium text-brand-700">
          {t('app.subtitle')}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <Card className="shadow-xl rounded-2xl border-border">
          <CardContent className="py-8 px-6 sm:px-10">
            <form className="space-y-5" onSubmit={handleSubmit}>
              {error && (
                <div className="rounded-lg bg-destructive/10 p-3.5 border border-destructive/20 flex items-start space-x-3">
                  <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                  <p className="text-sm font-medium text-destructive">{error}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-foreground">
                  {t('auth.username')}
                </label>
                <div className="mt-1 relative rounded-md shadow-2xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                    <User className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2.5 border border-input rounded-lg bg-background focus:ring-2 focus:ring-brand-500 text-sm"
                    placeholder="e.g. operator_meru"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-foreground">
                  {t('auth.password')}
                </label>
                <div className="mt-1 relative rounded-md shadow-2xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                    <Lock className="w-5 h-5" />
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2.5 border border-input rounded-lg bg-background focus:ring-2 focus:ring-brand-500 text-sm"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                variant="brand"
                className="w-full h-11 text-sm font-semibold"
              >
                {loading ? t('auth.signingIn') : t('auth.signIn')}
              </Button>
            </form>

            {/* Quick preset account shortcuts */}
            <div className="mt-6 pt-6 border-t border-border">
              <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground text-center mb-3">
                {t('auth.quickPresets')}
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleQuickLogin('operator_meru', 'operatorpassword123')}
                  className="h-auto p-2.5 border-emerald-200 bg-emerald-50/60 text-emerald-800 hover:bg-emerald-100 font-medium justify-start"
                >
                  🌾 Meru Hub
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleQuickLogin('operator_tharaka', 'operatorpassword123')}
                  className="h-auto p-2.5 border-emerald-200 bg-emerald-50/60 text-emerald-800 hover:bg-emerald-100 font-medium justify-start"
                >
                  🌺 Tharaka Nithi
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleQuickLogin('operator_eldoret', 'operatorpassword123')}
                  className="h-auto p-2.5 border-emerald-200 bg-emerald-50/60 text-emerald-800 hover:bg-emerald-100 font-medium justify-start"
                >
                  🌳 Eldoret Hub
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleQuickLogin('admin', 'adminpassword123')}
                  className="h-auto p-2.5 border-purple-200 bg-purple-50/60 text-purple-800 hover:bg-purple-100 font-medium justify-start"
                >
                  ⚡ Administrator
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
