import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
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
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-amber-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Top language toggle */}
      <div className="absolute top-4 right-4 sm:top-6 sm:right-6">
        <button
          onClick={toggleLanguage}
          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-md border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 shadow-sm"
        >
          <Globe className="w-4 h-4 mr-1.5 text-brand-600" />
          {i18n.language === 'en' ? 'English (EN)' : 'Kiswahili (SW)'}
        </button>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-solar-500 flex items-center justify-center text-white shadow-lg">
          <Sun className="w-10 h-10" />
        </div>
        <h2 className="mt-4 text-center text-3xl font-extrabold tracking-tight text-gray-900">
          {t('app.title')}
        </h2>
        <p className="mt-1 text-center text-sm font-medium text-brand-700">
          {t('app.subtitle')}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl sm:px-10 border border-gray-100">
          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-md bg-red-50 p-4 border border-red-200 flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm font-medium text-red-800">{error}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-gray-700">
                {t('auth.username')}
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <User className="w-5 h-5" />
                </div>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm"
                  placeholder="e.g. operator_meru"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700">
                {t('auth.password')}
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-5 h-5" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 transition-colors disabled:opacity-50"
            >
              {loading ? t('auth.signingIn') : t('auth.signIn')}
            </button>
          </form>

          {/* Quick preset account shortcuts */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs font-bold uppercase tracking-wider text-gray-500 text-center mb-3">
              {t('auth.quickPresets')}
            </p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => handleQuickLogin('operator_meru', 'operatorpassword123')}
                className="p-2 border border-emerald-200 bg-emerald-50 text-emerald-800 rounded-md hover:bg-emerald-100 font-medium text-left transition-colors"
              >
                🌾 Meru Hub
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('operator_tharaka', 'operatorpassword123')}
                className="p-2 border border-emerald-200 bg-emerald-50 text-emerald-800 rounded-md hover:bg-emerald-100 font-medium text-left transition-colors"
              >
                🌺 Tharaka Nithi
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('operator_eldoret', 'operatorpassword123')}
                className="p-2 border border-emerald-200 bg-emerald-50 text-emerald-800 rounded-md hover:bg-emerald-100 font-medium text-left transition-colors"
              >
                🌳 Eldoret Hub
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('admin', 'adminpassword123')}
                className="p-2 border border-purple-200 bg-purple-50 text-purple-800 rounded-md hover:bg-purple-100 font-medium text-left transition-colors"
              >
                ⚡ Administrator
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

