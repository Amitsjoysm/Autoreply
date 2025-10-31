import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from './components/ui/sonner';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import '@/App.css';
import {
  Mail, BarChart3, User, Calendar, CalendarDays, Brain, Target, 
  Database, FileText, UserPlus, Activity, Zap, LogOut, MessageSquare
} from 'lucide-react';

const MainLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    setCurrentPath(window.location.pathname);
  }, [window.location.pathname]);

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: BarChart3 },
    { path: '/profile', label: 'Profile', icon: User },
    { path: '/calendar-providers', label: 'Calendar Providers', icon: Calendar },
    { path: '/calendar-events', label: 'Calendar Events', icon: CalendarDays },
    { path: '/meeting-detection', label: 'Meeting Detection', icon: Brain },
    { path: '/intents', label: 'Intents', icon: Target },
    { path: '/email-accounts', label: 'Email Accounts', icon: Mail },
    { path: '/knowledge-base', label: 'Knowledge Base', icon: Database },
    { path: '/email-processing', label: 'Email Processing', icon: FileText },
    { path: '/follow-ups', label: 'Follow-ups', icon: UserPlus },
    { path: '/live-monitoring', label: 'Live Monitoring', icon: Activity },
    { path: '/test-email', label: 'Test Email', icon: Zap },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-gradient-to-b from-purple-900 to-purple-800 text-white flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-purple-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-purple-500 rounded-lg flex items-center justify-center">
              <Mail className="w-6 h-6" />
            </div>
            <span className="text-lg font-bold">Email Assistant</span>
          </div>
        </div>

        {/* User Info */}
        <div className="p-6 border-b border-purple-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-700 rounded-full flex items-center justify-center">
              <User className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || user?.email}</p>
              <p className="text-xs text-purple-300 truncate">{user?.email}</p>
            </div>
          </div>
          <div className="mt-3 text-xs text-purple-300">
            Quota: {user?.quota_used || 0}/{user?.quota || 0}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setCurrentPath(item.path)}
                className={`flex items-center gap-3 px-6 py-3 transition-colors ${
                  isActive
                    ? 'bg-gradient-to-r from-pink-500 to-purple-500 border-l-4 border-white'
                    : 'hover:bg-purple-800/50'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(/ /g, '-')}`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-sm">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="p-4 border-t border-purple-700">
          <button
            onClick={logout}
            data-testid="logout-btn"
            className="flex items-center gap-3 w-full px-4 py-3 rounded-lg hover:bg-purple-800/50 transition-colors text-sm"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>

        {/* Footer */}
        <div className="p-4 text-xs text-purple-300 text-center border-t border-purple-700">
          Made by DevDay
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/" replace />;
};

// Placeholder pages
const PlaceholderPage = ({ title, description }) => (
  <div>
    <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
    <p className="text-gray-600 mt-2">{description}</p>
    <div className="mt-8 p-6 bg-white rounded-lg shadow">
      <p className="text-gray-500">This feature is available. Check the API documentation for integration.</p>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AuthPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Profile" description="Manage your account settings" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/calendar-providers"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Calendar Providers" description="Connect Google Calendar" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/calendar-events"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Calendar Events" description="View and manage calendar events" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/meeting-detection"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Meeting Detection" description="Configure AI meeting detection" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/intents"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Intents" description="Define email intents and auto-responses" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/email-accounts"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Email Accounts" description="Connect Gmail, Outlook, or custom SMTP" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/knowledge-base"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Knowledge Base" description="Add knowledge for AI responses" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/email-processing"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Email Processing" description="View processed emails and drafts" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/follow-ups"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Follow-ups" description="Manage scheduled follow-ups" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/live-monitoring"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Live Monitoring" description="Real-time email monitoring" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/test-email"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <PlaceholderPage title="Test Email" description="Test email processing" />
                </MainLayout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </AuthProvider>
  );
}

export default App;
