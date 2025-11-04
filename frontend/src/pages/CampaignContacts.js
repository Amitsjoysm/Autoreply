import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import API from '../api';
import { toast } from 'sonner';
import {
  Users, Plus, Upload, Download, Trash2, Edit, Mail, Eye, MessageSquare,
  X, Search, Filter, Tag as TagIcon, ChevronDown, ChevronUp
} from 'lucide-react';

const CampaignContacts = () => {
  const { user } = useAuth();
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterTags, setFilterTags] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    company: '',
    title: '',
    linkedin_url: '',
    company_domain: '',
    tags: []
  });
  const [csvFile, setCsvFile] = useState(null);
  const [csvFieldMapping, setCsvFieldMapping] = useState({});
  const [csvHeaders, setCsvHeaders] = useState([]);
  const [tagInput, setTagInput] = useState('');

  useEffect(() => {
    loadContacts();
  }, [filterStatus, filterTags]);

  const loadContacts = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterStatus) params.status = filterStatus;
      if (filterTags.length > 0) params.tags = filterTags.join(',');
      const data = await API.getCampaignContacts(params);
      setContacts(data);
    } catch (error) {
      toast.error('Failed to load contacts');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddContact = async (e) => {
    e.preventDefault();
    try {
      if (editingContact) {
        await API.updateCampaignContact(editingContact.id, formData);
        toast.success('Contact updated successfully');
      } else {
        await API.createCampaignContact(formData);
        toast.success('Contact created successfully');
      }
      setShowAddModal(false);
      setEditingContact(null);
      resetForm();
      loadContacts();
    } catch (error) {
      toast.error(editingContact ? 'Failed to update contact' : 'Failed to create contact');
      console.error(error);
    }
  };

  const handleDeleteContact = async (id) => {
    if (!window.confirm('Are you sure you want to delete this contact?')) return;
    try {
      await API.deleteCampaignContact(id);
      toast.success('Contact deleted successfully');
      loadContacts();
    } catch (error) {
      toast.error('Failed to delete contact');
      console.error(error);
    }
  };

  const handleEditContact = (contact) => {
    setEditingContact(contact);
    setFormData({
      email: contact.email,
      first_name: contact.first_name || '',
      last_name: contact.last_name || '',
      company: contact.company || '',
      title: contact.title || '',
      linkedin_url: contact.linkedin_url || '',
      company_domain: contact.company_domain || '',
      tags: contact.tags || []
    });
    setShowAddModal(true);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.csv')) {
      setCsvFile(file);
      // Read CSV to get headers
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target.result;
        const lines = text.split('\n');
        if (lines.length > 0) {
          const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
          setCsvHeaders(headers);
          // Auto-map common headers
          const autoMapping = {};
          headers.forEach(header => {
            const lowerHeader = header.toLowerCase();
            if (lowerHeader.includes('email')) autoMapping[header] = 'email';
            else if (lowerHeader.includes('first') && lowerHeader.includes('name')) autoMapping[header] = 'first_name';
            else if (lowerHeader.includes('last') && lowerHeader.includes('name')) autoMapping[header] = 'last_name';
            else if (lowerHeader.includes('company') && !lowerHeader.includes('domain')) autoMapping[header] = 'company';
            else if (lowerHeader.includes('title') || lowerHeader.includes('position')) autoMapping[header] = 'title';
            else if (lowerHeader.includes('linkedin')) autoMapping[header] = 'linkedin_url';
            else if (lowerHeader.includes('domain')) autoMapping[header] = 'company_domain';
          });
          setCsvFieldMapping(autoMapping);
        }
      };
      reader.readAsText(file);
    } else {
      toast.error('Please select a CSV file');
    }
  };

  const handleUploadCSV = async () => {
    if (!csvFile) {
      toast.error('Please select a file');
      return;
    }
    try {
      const result = await API.uploadCampaignContactsCSV(csvFile, csvFieldMapping);
      toast.success(`Successfully uploaded ${result.created} contacts`);
      setShowUploadModal(false);
      setCsvFile(null);
      setCsvHeaders([]);
      setCsvFieldMapping({});
      loadContacts();
    } catch (error) {
      toast.error('Failed to upload CSV');
      console.error(error);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      await API.downloadCampaignContactTemplate();
      toast.success('Template downloaded successfully');
    } catch (error) {
      toast.error('Failed to download template');
      console.error(error);
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      first_name: '',
      last_name: '',
      company: '',
      title: '',
      linkedin_url: '',
      company_domain: '',
      tags: []
    });
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const removeTag = (tag) => {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) });
  };

  const filteredContacts = contacts.filter(contact => {
    const searchLower = searchTerm.toLowerCase();
    return (
      contact.email.toLowerCase().includes(searchLower) ||
      (contact.first_name && contact.first_name.toLowerCase().includes(searchLower)) ||
      (contact.last_name && contact.last_name.toLowerCase().includes(searchLower)) ||
      (contact.company && contact.company.toLowerCase().includes(searchLower))
    );
  });

  const availableFields = [
    { value: 'email', label: 'Email' },
    { value: 'first_name', label: 'First Name' },
    { value: 'last_name', label: 'Last Name' },
    { value: 'company', label: 'Company' },
    { value: 'title', label: 'Title' },
    { value: 'linkedin_url', label: 'LinkedIn URL' },
    { value: 'company_domain', label: 'Company Domain' }
  ];

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              Campaign Contacts
            </h1>
            <p className="text-gray-600 mt-2">Manage your outbound campaign contacts</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleDownloadTemplate}
              className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-purple-500 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download Template
            </button>
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:shadow-lg transition-shadow"
            >
              <Upload className="w-4 h-4" />
              Bulk Upload
            </button>
            <button
              onClick={() => { setEditingContact(null); resetForm(); setShowAddModal(true); }}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-shadow"
            >
              <Plus className="w-4 h-4" />
              Add Contact
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Contacts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{contacts.length}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {contacts.filter(c => c.status === 'active').length}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Mail className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Email Verified</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {contacts.filter(c => c.email_verified).length}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Eye className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Replied</p>
              <p className="text-2xl font-bold text-pink-600 mt-1">
                {contacts.reduce((sum, c) => sum + c.emails_replied, 0)}
              </p>
            </div>
            <div className="w-12 h-12 bg-pink-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-pink-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search contacts by name, email, or company..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="unsubscribed">Unsubscribed</option>
            <option value="bounced">Bounced</option>
          </select>
        </div>
      </div>

      {/* Contacts Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <div className="inline-block w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
            <p className="text-gray-600 mt-4">Loading contacts...</p>
          </div>
        ) : filteredContacts.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No contacts yet</h3>
            <p className="text-gray-600 mb-6">Start by adding contacts or uploading a CSV file</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-shadow"
            >
              <Plus className="w-5 h-5" />
              Add Your First Contact
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Engagement</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tags</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredContacts.map((contact) => (
                  <tr key={contact.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {contact.first_name} {contact.last_name}
                        </div>
                        <div className="text-sm text-gray-500">{contact.email}</div>
                        {contact.title && <div className="text-xs text-gray-400">{contact.title}</div>}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{contact.company || '-'}</div>
                      {contact.company_domain && (
                        <div className="text-xs text-gray-500">{contact.company_domain}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        contact.status === 'active' ? 'bg-green-100 text-green-800' :
                        contact.status === 'unsubscribed' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {contact.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-xs space-y-1">
                        <div className="flex items-center gap-2">
                          <Mail className="w-3 h-3 text-gray-400" />
                          <span className="text-gray-600">Sent: {contact.emails_sent}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Eye className="w-3 h-3 text-blue-400" />
                          <span className="text-gray-600">Opened: {contact.emails_opened}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <MessageSquare className="w-3 h-3 text-green-400" />
                          <span className="text-gray-600">Replied: {contact.emails_replied}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {contact.tags && contact.tags.length > 0 ? (
                          contact.tags.map((tag, idx) => (
                            <span key={idx} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                              {tag}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-gray-400">No tags</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleEditContact(contact)}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteContact(contact.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add/Edit Contact Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">
                {editingContact ? 'Edit Contact' : 'Add New Contact'}
              </h2>
              <button onClick={() => { setShowAddModal(false); setEditingContact(null); resetForm(); }}>
                <X className="w-6 h-6 text-gray-400 hover:text-gray-600" />
              </button>
            </div>
            <form onSubmit={handleAddContact} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="john@example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
                  <input
                    type="text"
                    value={formData.company}
                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Acme Inc"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Title/Position</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="CEO"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">LinkedIn URL</label>
                  <input
                    type="url"
                    value={formData.linkedin_url}
                    onChange={(e) => setFormData({ ...formData, linkedin_url: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="https://linkedin.com/in/..."
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company Domain</label>
                  <input
                    type="text"
                    value={formData.company_domain}
                    onChange={(e) => setFormData({ ...formData, company_domain: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="example.com"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="Add tag and press Enter"
                    />
                    <button
                      type="button"
                      onClick={addTag}
                      className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
                    >
                      Add
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map((tag, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                        {tag}
                        <button type="button" onClick={() => removeTag(tag)}>
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => { setShowAddModal(false); setEditingContact(null); resetForm(); }}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-shadow"
                >
                  {editingContact ? 'Update Contact' : 'Create Contact'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CSV Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Bulk Upload Contacts</h2>
              <button onClick={() => { setShowUploadModal(false); setCsvFile(null); setCsvHeaders([]); }}>
                <X className="w-6 h-6 text-gray-400 hover:text-gray-600" />
              </button>
            </div>
            <div className="p-6 space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select CSV File
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-500 transition-colors">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                    id="csv-upload"
                  />
                  <label htmlFor="csv-upload" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-2">
                      {csvFile ? csvFile.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-sm text-gray-500">CSV files only</p>
                  </label>
                </div>
              </div>

              {/* Field Mapping */}
              {csvHeaders.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Map CSV Fields</h3>
                  <div className="space-y-3">
                    {csvHeaders.map((header, idx) => (
                      <div key={idx} className="flex items-center gap-4">
                        <div className="flex-1">
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            CSV Column: <span className="font-semibold text-purple-600">{header}</span>
                          </label>
                        </div>
                        <div className="flex-1">
                          <select
                            value={csvFieldMapping[header] || ''}
                            onChange={(e) => setCsvFieldMapping({ ...csvFieldMapping, [header]: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          >
                            <option value="">Skip this field</option>
                            {availableFields.map(field => (
                              <option key={field.value} value={field.value}>{field.label}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => { setShowUploadModal(false); setCsvFile(null); setCsvHeaders([]); }}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUploadCSV}
                  disabled={!csvFile || csvHeaders.length === 0}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Upload Contacts
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignContacts;