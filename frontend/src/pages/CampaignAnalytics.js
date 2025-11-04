import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import API from '../api';
import { toast } from 'sonner';
import {
  ArrowLeft, Mail, Eye, MessageSquare, XCircle, TrendingUp,
  Calendar, Users, FileText, BarChart3
} from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const CampaignAnalytics = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [campaign, setCampaign] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCampaignData();
  }, [id]);

  const loadCampaignData = async () => {
    try {
      setLoading(true);
      const [campaignData, analyticsData] = await Promise.all([
        API.getCampaign(id),
        API.getCampaignAnalytics(id)
      ]);
      setCampaign(campaignData);
      setAnalytics(analyticsData);
    } catch (error) {
      toast.error('Failed to load campaign analytics');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-96">
          <div className="inline-block w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!campaign || !analytics) {
    return (
      <div className="p-8">
        <div className="text-center">
          <p className="text-gray-600">Campaign not found</p>
          <button
            onClick={() => navigate('/campaigns')}
            className="mt-4 text-purple-600 hover:text-purple-700"
          >
            Back to Campaigns
          </button>
        </div>
      </div>
    );
  }

  const openRate = campaign.emails_sent > 0 ? (campaign.emails_opened / campaign.emails_sent * 100).toFixed(1) : 0;
  const replyRate = campaign.emails_sent > 0 ? (campaign.emails_replied / campaign.emails_sent * 100).toFixed(1) : 0;
  const bounceRate = campaign.emails_sent > 0 ? (campaign.emails_bounced / campaign.emails_sent * 100).toFixed(1) : 0;

  const statusData = [
    { name: 'Sent', value: campaign.emails_sent, color: '#3b82f6' },
    { name: 'Opened', value: campaign.emails_opened, color: '#10b981' },
    { name: 'Replied', value: campaign.emails_replied, color: '#8b5cf6' },
    { name: 'Bounced', value: campaign.emails_bounced, color: '#ef4444' },
    { name: 'Pending', value: campaign.emails_pending, color: '#f59e0b' }
  ].filter(item => item.value > 0);

  const emailTypeData = [
    { name: 'Initial', value: analytics.emails_by_type?.initial || 0 },
    { name: 'Follow-up', value: analytics.emails_by_type?.follow_up || 0 }
  ];

  const metricsData = [
    { name: 'Sent', value: campaign.emails_sent },
    { name: 'Opened', value: campaign.emails_opened },
    { name: 'Replied', value: campaign.emails_replied },
    { name: 'Bounced', value: campaign.emails_bounced }
  ];

  const COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#ef4444', '#f59e0b'];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/campaigns')}
          className="flex items-center gap-2 text-purple-600 hover:text-purple-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Campaigns
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              {campaign.name}
            </h1>
            <p className="text-gray-600 mt-2">{campaign.description || 'Campaign Analytics Dashboard'}</p>
          </div>
          <div className="text-right">
            <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium ${
              campaign.status === 'running' ? 'bg-green-100 text-green-700' :
              campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
              campaign.status === 'completed' ? 'bg-purple-100 text-purple-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {campaign.status}
            </span>
            <p className="text-sm text-gray-500 mt-2">
              Created: {new Date(campaign.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Mail className="w-8 h-8 opacity-80" />
            <span className="text-2xl font-bold">{campaign.emails_sent}</span>
          </div>
          <p className="text-blue-100 text-sm">Emails Sent</p>
          <div className="mt-2 flex items-center gap-2">
            <div className="flex-1 bg-blue-400 rounded-full h-2">
              <div
                className="bg-white h-2 rounded-full"
                style={{ width: `${Math.min((campaign.emails_sent / campaign.total_contacts) * 100, 100)}%` }}
              />
            </div>
            <span className="text-xs">
              {campaign.total_contacts > 0 ? Math.round((campaign.emails_sent / campaign.total_contacts) * 100) : 0}%
            </span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Eye className="w-8 h-8 opacity-80" />
            <span className="text-2xl font-bold">{campaign.emails_opened}</span>
          </div>
          <p className="text-green-100 text-sm">Emails Opened</p>
          <div className="mt-2 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-semibold">{openRate}% open rate</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <MessageSquare className="w-8 h-8 opacity-80" />
            <span className="text-2xl font-bold">{campaign.emails_replied}</span>
          </div>
          <p className="text-purple-100 text-sm">Replies Received</p>
          <div className="mt-2 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm font-semibold">{replyRate}% reply rate</span>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <XCircle className="w-8 h-8 opacity-80" />
            <span className="text-2xl font-bold">{campaign.emails_bounced}</span>
          </div>
          <p className="text-red-100 text-sm">Emails Bounced</p>
          <div className="mt-2 flex items-center gap-2">
            <span className="text-sm font-semibold">{bounceRate}% bounce rate</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Email Status Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Email Type Breakdown */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Type Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={emailTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8b5cf6" name="Emails Sent" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={metricsData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="url(#colorGradient)" name="Count" />
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#ec4899" stopOpacity={0.8}/>
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Campaign Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-purple-600" />
            Campaign Details
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Contacts:</span>
              <span className="font-semibold text-gray-900">{campaign.total_contacts}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Email Accounts:</span>
              <span className="font-semibold text-gray-900">{campaign.email_account_ids?.length || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Daily Limit:</span>
              <span className="font-semibold text-gray-900">{campaign.daily_limit_per_account}/account</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Random Delay:</span>
              <span className="font-semibold text-gray-900">
                {campaign.random_delay_min}s - {campaign.random_delay_max}s
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-purple-600" />
            Timeline
          </h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Created</p>
              <p className="font-semibold text-gray-900">
                {new Date(campaign.created_at).toLocaleString()}
              </p>
            </div>
            {campaign.started_at && (
              <div>
                <p className="text-sm text-gray-600">Started</p>
                <p className="font-semibold text-gray-900">
                  {new Date(campaign.started_at).toLocaleString()}
                </p>
              </div>
            )}
            {campaign.completed_at && (
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="font-semibold text-gray-900">
                  {new Date(campaign.completed_at).toLocaleString()}
                </p>
              </div>
            )}
            {campaign.scheduled_start && (
              <div>
                <p className="text-sm text-gray-600">Scheduled Start</p>
                <p className="font-semibold text-gray-900">
                  {new Date(campaign.scheduled_start).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-600" />
            Follow-up Configuration
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Follow-ups Enabled:</span>
              <span className="font-semibold text-gray-900">
                {campaign.follow_up_config?.enabled ? 'Yes' : 'No'}
              </span>
            </div>
            {campaign.follow_up_config?.enabled && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600">Number of Follow-ups:</span>
                  <span className="font-semibold text-gray-900">
                    {campaign.follow_up_config.count}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Intervals (days):</p>
                  <div className="flex flex-wrap gap-2">
                    {campaign.follow_up_config.intervals?.map((interval, idx) => (
                      <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                        {interval} days
                      </span>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Rate Analysis */}
      <div className="mt-8 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Open Rate</span>
              <Eye className="w-5 h-5 text-green-500" />
            </div>
            <p className="text-3xl font-bold text-green-600">{openRate}%</p>
            <p className="text-xs text-gray-500 mt-1">
              Industry average: 20-25%
            </p>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-500 h-2 rounded-full"
                style={{ width: `${Math.min(openRate, 100)}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Reply Rate</span>
              <MessageSquare className="w-5 h-5 text-purple-500" />
            </div>
            <p className="text-3xl font-bold text-purple-600">{replyRate}%</p>
            <p className="text-xs text-gray-500 mt-1">
              Industry average: 1-5%
            </p>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-500 h-2 rounded-full"
                style={{ width: `${Math.min(replyRate * 20, 100)}%` }}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Bounce Rate</span>
              <XCircle className="w-5 h-5 text-red-500" />
            </div>
            <p className="text-3xl font-bold text-red-600">{bounceRate}%</p>
            <p className="text-xs text-gray-500 mt-1">
              Target: {'<'} 2%
            </p>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div
                className="bg-red-500 h-2 rounded-full"
                style={{ width: `${Math.min(bounceRate * 10, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CampaignAnalytics;
