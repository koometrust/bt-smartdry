import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import {
  Sun,
  Layers,
  History,
  Building2,
  BarChart3,
  LogOut,
  Globe,
  Menu,
  X,
  User as UserIcon,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, isAdmin } = useAuth();
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleLanguage = () => {
    const nextLang = i18n.language === 'en' ? 'sw' : 'en';
    i18n.changeLanguage(nextLang);
    localStorage.setItem('bt_language', nextLang);
  };

  const navLinks = [
    { to: '/', label: t('nav.activeBatches'), icon: Layers },
    { to: '/history', label: t('nav.history'), icon: History },
    ...(isAdmin
      ? [
          { to: '/hubs', label: t('nav.hubOverview'), icon: Building2 },
          { to: '/analytics', label: t('nav.analytics'), icon: BarChart3 },
        ]
      : []),
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2.5">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-brand-600 to-solar-500 flex items-center justify-center text-white shadow-md">
                <Sun className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <span className="text-xl font-bold tracking-tight text-gray-900 block leading-tight">
                  BT-SmartDry
                </span>
                <span className="text-xs text-brand-700 font-medium block leading-none">
                  Botanic Treasures IoT
                </span>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:ml-8 md:flex md:space-x-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const active = location.pathname === link.to;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      active
                        ? 'bg-brand-50 text-brand-800 font-semibold'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-1.5" />
                    {link.label}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right controls: Language toggle, User profile, Logout */}
          <div className="hidden md:flex md:items-center md:space-x-4">
            {/* Language Switcher */}
            <button
              onClick={toggleLanguage}
              className="inline-flex items-center px-2.5 py-1.5 text-xs font-semibold rounded-md border border-gray-300 text-gray-700 bg-gray-50 hover:bg-gray-100 transition-colors shadow-sm"
              title="Switch Language / Badilisha Lugha"
            >
              <Globe className="w-3.5 h-3.5 mr-1 text-brand-600" />
              {i18n.language === 'en' ? 'EN | Kiswahili' : 'SW | English'}
            </button>

            {/* User Profile Badge */}
            {user && (
              <div className="flex items-center text-xs text-gray-700 bg-gray-100 px-3 py-1.5 rounded-full border border-gray-200">
                <UserIcon className="w-3.5 h-3.5 mr-1.5 text-gray-500" />
                <span className="font-semibold text-gray-900 mr-1.5">{user.username}</span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    isAdmin ? 'bg-purple-100 text-purple-800' : 'bg-emerald-100 text-emerald-800'
                  }`}
                >
                  {isAdmin ? t('nav.admin') : t('nav.operator')}
                </span>
              </div>
            )}

            {/* Logout button */}
            <button
              onClick={logout}
              className="p-1.5 rounded-md text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
              title={t('nav.logout')}
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>

          {/* Mobile hamburger button */}
          <div className="flex items-center md:hidden space-x-2">
            <button
              onClick={toggleLanguage}
              className="p-1.5 text-xs font-bold rounded border border-gray-300 bg-gray-50 text-gray-700"
            >
              {i18n.language.toUpperCase()}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white px-4 pt-2 pb-4 space-y-1 shadow-lg">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const active = location.pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center px-3 py-2 rounded-md text-base font-medium ${
                  active ? 'bg-brand-50 text-brand-700' : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {link.label}
              </Link>
            );
          })}
          {user && (
            <div className="pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between px-3 py-2">
                <div>
                  <p className="text-sm font-bold text-gray-900">{user.username}</p>
                  <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                </div>
                <button
                  onClick={logout}
                  className="inline-flex items-center px-3 py-1.5 text-sm text-red-600 font-semibold bg-red-50 rounded-md"
                >
                  <LogOut className="w-4 h-4 mr-1.5" />
                  {t('nav.logout')}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

