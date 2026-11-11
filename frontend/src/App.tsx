import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { ActiveBatchesPage } from './pages/ActiveBatchesPage';
import { BatchDetailPage } from './pages/BatchDetailPage';
import { BatchHistoryPage } from './pages/BatchHistoryPage';
import { HubOverviewPage } from './pages/HubOverviewPage';
import { AnalyticsPage } from './pages/AnalyticsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: 30000, // 30s polling per context.md
      retry: 1,
      staleTime: 10000,
    },
  },
});

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="min-h-screen bg-gray-50 flex flex-col">
    <Navbar />
    <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {children}
    </main>
  </div>
);

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route
                path="/"
                element={
                  <Layout>
                    <ActiveBatchesPage />
                  </Layout>
                }
              />
              <Route
                path="/batches/:id"
                element={
                  <Layout>
                    <BatchDetailPage />
                  </Layout>
                }
              />
              <Route
                path="/history"
                element={
                  <Layout>
                    <BatchHistoryPage />
                  </Layout>
                }
              />
            </Route>

            {/* Admin Only Routes */}
            <Route element={<ProtectedRoute adminOnly />}>
              <Route
                path="/hubs"
                element={
                  <Layout>
                    <HubOverviewPage />
                  </Layout>
                }
              />
              <Route
                path="/analytics"
                element={
                  <Layout>
                    <AnalyticsPage />
                  </Layout>
                }
              />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;

