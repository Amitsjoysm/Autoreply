import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from './components/ui/sonner';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import EmailAccounts from './pages/EmailAccounts';
import Intents from './pages/Intents';
import KnowledgeBase from './pages/KnowledgeBase';
import EmailProcessing from './pages/EmailProcessing';
import Profile from './pages/Profile';
import CalendarProviders from './pages/CalendarProviders';
import CalendarEvents from './pages/CalendarEvents';
import MeetingDetection from './pages/MeetingDetection';
import FollowUps from './pages/FollowUps';
import LiveMonitoring from './pages/LiveMonitoring';
import TestEmail from './pages/TestEmail';
import CampaignContacts from './pages/CampaignContacts';
import CampaignTemplates from './pages/CampaignTemplates';
import Campaigns from './pages/Campaigns';
import CampaignAnalytics from './pages/CampaignAnalytics';
import ContactLists from './pages/ContactLists';
import '@/App.css';
import {
  Mail, BarChart3, User, Calendar, CalendarDays, Brain, Target, 
  Database, FileText, UserPlus, Activity, Zap, LogOut, MessageSquare,
  Users, Send, ChevronDown, ChevronRight
} from 'lucide-react';

const MainLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const [campaignExpanded, setCampaignExpanded] = useState(
    window.location.pathname.startsWith('/campaign')
  );

  useEffect(() => {
    setCurrentPath(window.location.pathname);
    if (window.location.pathname.startsWith('/campaign')) {
      setCampaignExpanded(true);
    }
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

  const campaignMenuItems = [
    { path: '/campaign/campaigns', label: 'Campaigns', icon: Send },
    { path: '/campaign/contacts', label: 'Contacts', icon: Users },
    { path: '/campaign/templates', label: 'Templates', icon: FileText },
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
          
          {/* Campaign Section */}
          <div className="mt-2">
            <button
              onClick={() => setCampaignExpanded(!campaignExpanded)}
              className="flex items-center justify-between w-full px-6 py-3 hover:bg-purple-800/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <Send className="w-5 h-5" />
                <span className="text-sm font-semibold">Campaigns</span>
              </div>
              {campaignExpanded ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
            {campaignExpanded && (
              <div className="bg-purple-900/30">
                {campaignMenuItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentPath === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setCurrentPath(item.path)}
                      className={`flex items-center gap-3 pl-12 pr-6 py-2.5 transition-colors text-sm ${
                        isActive
                          ? 'bg-gradient-to-r from-pink-500 to-purple-500 border-l-4 border-white'
                          : 'hover:bg-purple-800/50'
                      }`}
                      data-testid={`nav-campaign-${item.label.toLowerCase()}`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
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
                  <Profile />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/calendar-providers"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CalendarProviders />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/calendar-events"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CalendarEvents />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/meeting-detection"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <MeetingDetection />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/intents"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Intents />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/email-accounts"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <EmailAccounts />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/knowledge-base"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <KnowledgeBase />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/email-processing"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <EmailProcessing />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/follow-ups"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <FollowUps />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/live-monitoring"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <LiveMonitoring />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/test-email"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <TestEmail />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/campaign/campaigns"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <Campaigns />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/campaign/contacts"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CampaignContacts />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/campaign/templates"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CampaignTemplates />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/campaign/analytics/:campaignId"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <CampaignAnalytics />
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
