import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import API from '../api';
import { toast } from 'sonner';
import {
  Send, Plus, Search, Play, Pause, Square, RotateCcw, BarChart3,
  ChevronDown, ChevronUp, Users, FileText, Calendar, Mail, Settings,
  CheckCircle, Clock, AlertCircle, X
} from 'lucide-react';

const Campaigns = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [emailAccounts, setEmailAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showWizard, setShowWizard] = useState(false);
  const [expandedStep, setExpandedStep] = useState(1);
  const [wizardData, setWizardData] = useState({
    name: '',
    description: '',
    contact_ids: [],
    contact_tags: [],
    initial_template_id: '',
    follow_up_config: {
      enabled: true,
      count: 3,
      intervals: [2, 4, 6],
      template_ids: []
    },
    email_account_ids: [],
    daily_limit_per_account: 100,
    random_delay_min: 60,
    random_delay_max: 300,
    scheduled_start: '',
    timezone: 'UTC',
    verify_emails: false
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [campaignsData, contactsData, templatesData, accountsData] = await Promise.all([
        API.getCampaigns(),
        API.getCampaignContacts(),
        API.getCampaignTemplates(),
        API.getEmailAccounts()
      ]);
      setCampaigns(campaignsData);
      setContacts(contactsData);
      setTemplates(templatesData);
      setEmailAccounts(accountsData);
    } catch (error) {
      toast.error('Failed to load data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCampaign = async () => {
    try {
      // Validation
      if (!wizardData.name.trim()) {
        toast.error('Please enter a campaign name');
        return;
      }
      if (wizardData.contact_ids.length === 0 && wizardData.contact_tags.length === 0) {
        toast.error('Please select at least one contact or tag');
        return;
      }
      if (!wizardData.initial_template_id) {
        toast.error('Please select an initial email template');
        return;
      }
      if (wizardData.email_account_ids.length === 0) {
        toast.error('Please select at least one email account');
        return;
      }

      await API.createCampaign(wizardData);
      toast.success('Campaign created successfully');
      setShowWizard(false);
      resetWizard();
      loadData();
    } catch (error) {
      toast.error('Failed to create campaign');
      console.error(error);
    }
  };

  const handleControlAction = async (campaignId, action) => {
    try {
      let response;
      switch (action) {
        case 'start':
          response = await API.startCampaign(campaignId);
          toast.success('Campaign started successfully');
          break;
        case 'pause':
          response = await API.pauseCampaign(campaignId);
          toast.success('Campaign paused');
          break;
        case 'resume':
          response = await API.resumeCampaign(campaignId);
          toast.success('Campaign resumed');
          break;
        case 'stop':
          if (!window.confirm('Are you sure you want to stop this campaign? This cannot be undone.')) return;
          response = await API.stopCampaign(campaignId);
          toast.success('Campaign stopped');
          break;
        default:
          break;
      }
      loadData();
    } catch (error) {
      toast.error(`Failed to ${action} campaign`);
      console.error(error);
    }
  };

  const handleDeleteCampaign = async (id) => {
    if (!window.confirm('Are you sure you want to delete this campaign?')) return;
    try {
      await API.deleteCampaign(id);
      toast.success('Campaign deleted successfully');
      loadData();
    } catch (error) {
      toast.error('Failed to delete campaign');
      console.error(error);
    }
  };

  const resetWizard = () => {
    setWizardData({
      name: '',
      description: '',
      contact_ids: [],
      contact_tags: [],
      initial_template_id: '',
      follow_up_config: {
        enabled: true,
        count: 3,
        intervals: [2, 4, 6],
        template_ids: []
      },
      email_account_ids: [],
      daily_limit_per_account: 100,
      random_delay_min: 60,
      random_delay_max: 300,
      scheduled_start: '',
      timezone: 'UTC',
      verify_emails: false
    });
    setExpandedStep(1);
  };

  const toggleContact = (contactId) => {
    const newIds = wizardData.contact_ids.includes(contactId)
      ? wizardData.contact_ids.filter(id => id !== contactId)
      : [...wizardData.contact_ids, contactId];
    setWizardData({ ...wizardData, contact_ids: newIds });
  };

  const toggleTag = (tag) => {
    const newTags = wizardData.contact_tags.includes(tag)
      ? wizardData.contact_tags.filter(t => t !== tag)
      : [...wizardData.contact_tags, tag];
    setWizardData({ ...wizardData, contact_tags: newTags });
  };

  const toggleEmailAccount = (accountId) => {
    const newIds = wizardData.email_account_ids.includes(accountId)
      ? wizardData.email_account_ids.filter(id => id !== accountId)
      : [...wizardData.email_account_ids, accountId];
    setWizardData({ ...wizardData, email_account_ids: newIds });
  };

  const getStatusBadge = (status) => {
    const badges = {
      draft: { bg: 'bg-gray-100', text: 'text-gray-700', icon: <FileText className="w-3 h-3" /> },
      scheduled: { bg: 'bg-blue-100', text: 'text-blue-700', icon: <Clock className="w-3 h-3" /> },
      running: { bg: 'bg-green-100', text: 'text-green-700', icon: <Play className="w-3 h-3" /> },
      paused: { bg: 'bg-yellow-100', text: 'text-yellow-700', icon: <Pause className="w-3 h-3" /> },
      completed: { bg: 'bg-purple-100', text: 'text-purple-700', icon: <CheckCircle className="w-3 h-3" /> },
      stopped: { bg: 'bg-red-100', text: 'text-red-700', icon: <Square className="w-3 h-3" /> }
    };
    const badge = badges[status] || badges.draft;
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        {badge.icon}
        {status}
      </span>
    );
  };

  const getControlButtons = (campaign) => {
    switch (campaign.status) {
      case 'draft':
      case 'scheduled':
        return (
          <button
            onClick={() => handleControlAction(campaign.id, 'start')}
            className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
          >
            <Play className="w-3 h-3" /> Start
          </button>
        );
      case 'running':
        return (
          <>
            <button
              onClick={() => handleControlAction(campaign.id, 'pause')}
              className="flex items-center gap-1 px-3 py-1.5 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm"
            >
              <Pause className="w-3 h-3" /> Pause
            </button>
            <button
              onClick={() => handleControlAction(campaign.id, 'stop')}
              className="flex items-center gap-1 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
            >
              <Square className="w-3 h-3" /> Stop
            </button>
          </>
        );
      case 'paused':
        return (
          <>
            <button
              onClick={() => handleControlAction(campaign.id, 'resume')}
              className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
            >
              <RotateCcw className="w-3 h-3" /> Resume
            </button>
            <button
              onClick={() => handleControlAction(campaign.id, 'stop')}
              className="flex items-center gap-1 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
            >
              <Square className="w-3 h-3" /> Stop
            </button>
          </>
        );
      default:
        return null;
    }
  };

  const filteredCampaigns = campaigns.filter(campaign =>
    campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    campaign.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const allTags = [...new Set(contacts.flatMap(c => c.tags || []))];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <Send className="w-6 h-6 text-white" />
              </div>
              Campaigns
            </h1>
            <p className="text-gray-600 mt-2">Create and manage your outbound email campaigns</p>
          </div>
          <button
            onClick={() => setShowWizard(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-shadow"
          >
            <Plus className="w-4 h-4" />
            Create Campaign
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Campaigns</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{campaigns.length}</p>
            </div>
            <Send className="w-8 h-8 text-purple-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Running</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {campaigns.filter(c => c.status === 'running').length}
              </p>
            </div>
            <Play className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Emails Sent</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {campaigns.reduce((sum, c) => sum + c.emails_sent, 0)}
              </p>
            </div>
            <Mail className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Opened</p>
              <p className="text-2xl font-bold text-yellow-600 mt-1">
                {campaigns.reduce((sum, c) => sum + c.emails_opened, 0)}
              </p>
            </div>
            <AlertCircle className="w-8 h-8 text-yellow-600" />
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Replied</p>
              <p className="text-2xl font-bold text-pink-600 mt-1">
                {campaigns.reduce((sum, c) => sum + c.emails_replied, 0)}
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-pink-600" />
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="relative">
          <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search campaigns..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Campaigns List */}
      <div className="space-y-4">
        {loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <div className="inline-block w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
            <p className="text-gray-600 mt-4">Loading campaigns...</p>
          </div>
        ) : filteredCampaigns.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <Send className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No campaigns yet</h3>
            <p className="text-gray-600 mb-6">Create your first outbound email campaign</p>
            <button
              onClick={() => setShowWizard(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-shadow"
            >
              <Plus className="w-5 h-5" />
              Create Your First Campaign
            </button>
          </div>
        ) : (
          filteredCampaigns.map((campaign) => (
            <div key={campaign.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">{campaign.name}</h3>
                    {getStatusBadge(campaign.status)}
                  </div>
                  {campaign.description && (
                    <p className="text-gray-600">{campaign.description}</p>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {getControlButtons(campaign)}
                  <button
                    onClick={() => navigate(`/campaign/analytics/${campaign.id}`)}
                    className="flex items-center gap-1 px-3 py-1.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 text-sm"
                  >
                    <BarChart3 className="w-3 h-3" /> Analytics
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1">Total Contacts</p>
                  <p className="text-lg font-semibold text-gray-900">{campaign.total_contacts}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-xs text-blue-600 mb-1">Sent</p>
                  <p className="text-lg font-semibold text-blue-900">{campaign.emails_sent}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-xs text-green-600 mb-1">Opened</p>
                  <p className="text-lg font-semibold text-green-900">
                    {campaign.emails_opened} 
                    {campaign.emails_sent > 0 && (
                      <span className="text-xs ml-1">
                        ({Math.round((campaign.emails_opened / campaign.emails_sent) * 100)}%)
                      </span>
                    )}
                  </p>
                </div>
                <div className="bg-purple-50 rounded-lg p-3">
                  <p className="text-xs text-purple-600 mb-1">Replied</p>
                  <p className="text-lg font-semibold text-purple-900">
                    {campaign.emails_replied}
                    {campaign.emails_sent > 0 && (
                      <span className="text-xs ml-1">
                        ({Math.round((campaign.emails_replied / campaign.emails_sent) * 100)}%)
                      </span>
                    )}
                  </p>
                </div>
                <div className="bg-red-50 rounded-lg p-3">
                  <p className="text-xs text-red-600 mb-1">Bounced</p>
                  <p className="text-lg font-semibold text-red-900">{campaign.emails_bounced}</p>
                </div>
                <div className="bg-yellow-50 rounded-lg p-3">
                  <p className="text-xs text-yellow-600 mb-1">Pending</p>
                  <p className="text-lg font-semibold text-yellow-900">{campaign.emails_pending}</p>
                </div>
              </div>

              {campaign.status === 'running' && campaign.emails_sent > 0 && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-600">Progress</span>
                    <span className="text-xs text-gray-900 font-medium">
                      {Math.round((campaign.emails_sent / campaign.total_contacts) * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all"
                      style={{ width: `${Math.min((campaign.emails_sent / campaign.total_contacts) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Campaign Creation Wizard Modal */}
      {showWizard && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full my-8">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-xl">
              <h2 className="text-xl font-bold text-gray-900">Create New Campaign</h2>
              <button onClick={() => { setShowWizard(false); resetWizard(); }}>
                <X className="w-6 h-6 text-gray-400 hover:text-gray-600" />
              </button>
            </div>

            <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
              {/* Step 1: Basic Info */}
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => setExpandedStep(expandedStep === 1 ? 0 : 1)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-semibold">
                      1
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-gray-900">Campaign Details</h3>
                      <p className="text-sm text-gray-500">Name and description</p>
                    </div>
                  </div>
                  {expandedStep === 1 ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
                {expandedStep === 1 && (
                  <div className="p-4 border-t border-gray-200 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Campaign Name <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={wizardData.name}
                        onChange={(e) => setWizardData({ ...wizardData, name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        placeholder="e.g., Q1 Outreach - Tech Companies"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <textarea
                        value={wizardData.description}
                        onChange={(e) => setWizardData({ ...wizardData, description: e.target.value })}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        placeholder="Brief description of campaign goals"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Step 2: Select Contacts */}
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => setExpandedStep(expandedStep === 2 ? 0 : 2)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-semibold">
                      2
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-gray-900">Select Contacts</h3>
                      <p className="text-sm text-gray-500">
                        {wizardData.contact_ids.length} contacts, {wizardData.contact_tags.length} tags selected
                      </p>
                    </div>
                  </div>
                  {expandedStep === 2 ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
                {expandedStep === 2 && (
                  <div className="p-4 border-t border-gray-200 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Select by Tags</label>
                      <div className="flex flex-wrap gap-2">
                        {allTags.map((tag, idx) => (
                          <button
                            key={idx}
                            onClick={() => toggleTag(tag)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                              wizardData.contact_tags.includes(tag)
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            {tag}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Or Select Individual Contacts</label>
                      <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-lg divide-y">
                        {contacts.map((contact) => (
                          <label key={contact.id} className="flex items-center p-3 hover:bg-gray-50 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={wizardData.contact_ids.includes(contact.id)}
                              onChange={() => toggleContact(contact.id)}
                              className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                            />
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">
                                {contact.first_name} {contact.last_name}
                              </p>
                              <p className="text-xs text-gray-500">{contact.email}</p>
                            </div>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Step 3: Select Templates */}
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => setExpandedStep(expandedStep === 3 ? 0 : 3)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-semibold">
                      3
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-gray-900">Email Templates</h3>
                      <p className="text-sm text-gray-500">Initial email and follow-ups</p>
                    </div>
                  </div>
                  {expandedStep === 3 ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
                {expandedStep === 3 && (
                  <div className="p-4 border-t border-gray-200 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Initial Email Template <span className="text-red-500">*</span>
                      </label>
                      <select
                        value={wizardData.initial_template_id}
                        onChange={(e) => setWizardData({ ...wizardData, initial_template_id: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="">Select a template</option>
                        {templates.filter(t => t.template_type === 'initial').map(template => (
                          <option key={template.id} value={template.id}>{template.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="flex items-center gap-2 mb-2">
                        <input
                          type="checkbox"
                          checked={wizardData.follow_up_config.enabled}
                          onChange={(e) => setWizardData({
                            ...wizardData,
                            follow_up_config: { ...wizardData.follow_up_config, enabled: e.target.checked }
                          })}
                          className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                        />
                        <span className="text-sm font-medium text-gray-700">Enable Follow-ups</span>
                      </label>
                      {wizardData.follow_up_config.enabled && (
                        <div className="space-y-3 mt-3 pl-6 border-l-2 border-purple-200">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Number of Follow-ups</label>
                            <input
                              type="number"
                              min="1"
                              max="5"
                              value={wizardData.follow_up_config.count}
                              onChange={(e) => {
                                const count = parseInt(e.target.value);
                                const intervals = Array(count).fill(0).map((_, i) => (i + 1) * 2);
                                setWizardData({
                                  ...wizardData,
                                  follow_up_config: { ...wizardData.follow_up_config, count, intervals }
                                });
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Intervals (days between follow-ups)
                            </label>
                            <div className="flex gap-2">
                              {wizardData.follow_up_config.intervals.map((interval, idx) => (
                                <input
                                  key={idx}
                                  type="number"
                                  min="1"
                                  value={interval}
                                  onChange={(e) => {
                                    const newIntervals = [...wizardData.follow_up_config.intervals];
                                    newIntervals[idx] = parseInt(e.target.value);
                                    setWizardData({
                                      ...wizardData,
                                      follow_up_config: { ...wizardData.follow_up_config, intervals: newIntervals }
                                    });
                                  }}
                                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                                  placeholder={`Day ${idx + 1}`}
                                />
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Step 4: Schedule & Settings */}
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => setExpandedStep(expandedStep === 4 ? 0 : 4)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-semibold">
                      4
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-gray-900">Schedule & Settings</h3>
                      <p className="text-sm text-gray-500">Timing and rate limits</p>
                    </div>
                  </div>
                  {expandedStep === 4 ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
                {expandedStep === 4 && (
                  <div className="p-4 border-t border-gray-200 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Start Date & Time</label>
                        <input
                          type="datetime-local"
                          value={wizardData.scheduled_start}
                          onChange={(e) => setWizardData({ ...wizardData, scheduled_start: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Daily Limit per Account</label>
                        <input
                          type="number"
                          min="1"
                          value={wizardData.daily_limit_per_account}
                          onChange={(e) => setWizardData({ ...wizardData, daily_limit_per_account: parseInt(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Random Delay Between Emails</label>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <input
                            type="number"
                            min="30"
                            value={wizardData.random_delay_min}
                            onChange={(e) => setWizardData({ ...wizardData, random_delay_min: parseInt(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                          />
                          <p className="text-xs text-gray-500 mt-1">Min (seconds)</p>
                        </div>
                        <div>
                          <input
                            type="number"
                            min="60"
                            value={wizardData.random_delay_max}
                            onChange={(e) => setWizardData({ ...wizardData, random_delay_max: parseInt(e.target.value) })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                          />
                          <p className="text-xs text-gray-500 mt-1">Max (seconds)</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Step 5: Select Email Accounts */}
              <div className="border border-gray-200 rounded-lg">
                <button
                  onClick={() => setExpandedStep(expandedStep === 5 ? 0 : 5)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-semibold">
                      5
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-gray-900">Email Accounts</h3>
                      <p className="text-sm text-gray-500">{wizardData.email_account_ids.length} accounts selected</p>
                    </div>
                  </div>
                  {expandedStep === 5 ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
                {expandedStep === 5 && (
                  <div className="p-4 border-t border-gray-200">
                    <div className="space-y-2">
                      {emailAccounts.filter(a => a.is_active).map((account) => (
                        <label key={account.id} className="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={wizardData.email_account_ids.includes(account.id)}
                            onChange={() => toggleEmailAccount(account.id)}
                            className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                          />
                          <div className="ml-3">
                            <p className="text-sm font-medium text-gray-900">{account.email}</p>
                            <p className="text-xs text-gray-500">{account.account_type}</p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="border-t border-gray-200 px-6 py-4 flex items-center justify-between bg-gray-50 rounded-b-xl">
              <button
                onClick={() => { setShowWizard(false); resetWizard(); }}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-white"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateCampaign}
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-shadow"
              >
                Create Campaign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Campaigns;
