import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

class API {
  constructor() {
    this.axios = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  // Auth
  async register(data) {
    const response = await this.axios.post('/auth/register', data);
    return response.data;
  }

  async login(data) {
    const response = await this.axios.post('/auth/login', data);
    return response.data;
  }

  async getProfile() {
    const response = await this.axios.get('/auth/me');
    return response.data;
  }

  async getQuota() {
    const response = await this.axios.get('/auth/quota');
    return response.data;
  }

  // Email Accounts
  async getEmailAccounts() {
    const response = await this.axios.get('/email-accounts');
    return response.data;
  }

  async createEmailAccount(data) {
    const response = await this.axios.post('/email-accounts', data);
    return response.data;
  }

  async updateEmailAccount(id, data) {
    const response = await this.axios.patch(`/email-accounts/${id}`, data);
    return response.data;
  }

  async deleteEmailAccount(id) {
    const response = await this.axios.delete(`/email-accounts/${id}`);
    return response.data;
  }

  async testEmailAccount(id) {
    const response = await this.axios.post(`/email-accounts/${id}/test`);
    return response.data;
  }

  // Emails
  async getEmails(params) {
    const response = await this.axios.get('/emails', { params });
    return response.data;
  }

  async getEmail(id) {
    const response = await this.axios.get(`/emails/${id}`);
    return response.data;
  }

  async getEmailStats() {
    const response = await this.axios.get('/emails/stats');
    return response.data;
  }

  async sendEmail(data) {
    const response = await this.axios.post('/emails/send', data);
    return response.data;
  }

  async approveDraft(id) {
    const response = await this.axios.post(`/emails/${id}/approve-draft`);
    return response.data;
  }

  async reprocessEmail(id) {
    const response = await this.axios.post(`/emails/${id}/reprocess`);
    return response.data;
  }

  // Intents
  async getIntents() {
    const response = await this.axios.get('/intents');
    return response.data;
  }

  async createIntent(data) {
    const response = await this.axios.post('/intents', data);
    return response.data;
  }

  async updateIntent(id, data) {
    const response = await this.axios.patch(`/intents/${id}`, data);
    return response.data;
  }

  async deleteIntent(id) {
    const response = await this.axios.delete(`/intents/${id}`);
    return response.data;
  }

  // Knowledge Base
  async getKnowledgeBase() {
    const response = await this.axios.get('/knowledge-base');
    return response.data;
  }

  async createKnowledgeBase(data) {
    const response = await this.axios.post('/knowledge-base', data);
    return response.data;
  }

  async updateKnowledgeBase(id, data) {
    const response = await this.axios.patch(`/knowledge-base/${id}`, data);
    return response.data;
  }

  async deleteKnowledgeBase(id) {
    const response = await this.axios.delete(`/knowledge-base/${id}`);
    return response.data;
  }

  // Calendar
  async getCalendarProviders() {
    const response = await this.axios.get('/calendar/providers');
    return response.data;
  }

  async deleteCalendarProvider(id) {
    const response = await this.axios.delete(`/calendar/providers/${id}`);
    return response.data;
  }

  async getCalendarEvents() {
    const response = await this.axios.get('/calendar/events');
    return response.data;
  }

  async createCalendarEvent(data) {
    const response = await this.axios.post('/calendar/events', data);
    return response.data;
  }

  async getUpcomingEvents(hours = 24) {
    const response = await this.axios.get(`/calendar/events/upcoming?hours=${hours}`);
    return response.data;
  }

  // Follow-ups
  async getFollowUps() {
    const response = await this.axios.get('/follow-ups');
    return response.data;
  }

  async createFollowUp(data) {
    const response = await this.axios.post('/follow-ups', data);
    return response.data;
  }

  async deleteFollowUp(id) {
    const response = await this.axios.delete(`/follow-ups/${id}`);
    return response.data;
  }

  // OAuth
  async getGoogleOAuthUrl() {
    const response = await this.axios.get('/oauth/google/url');
    return response.data;
  }

  async handleGoogleCallback(code, state, accountType = 'email') {
    const response = await this.axios.post(`/oauth/google/callback?code=${code}&state=${state}&account_type=${accountType}`);
    return response.data;
  }

  // System
  async getSystemStatus() {
    const response = await this.axios.get('/system/status');
    return response.data;
  }

  async testEmailProcessing() {
    const response = await this.axios.post('/system/test-email-processing');
    return response.data;
  }

  async startPolling() {
    const response = await this.axios.post('/system/start-polling');
    return response.data;
  }

  async stopPolling() {
    const response = await this.axios.post('/system/stop-polling');
    return response.data;
  }
}

export default new API();
