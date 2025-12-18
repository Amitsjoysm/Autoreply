import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Calendar, Plus, CheckCircle2, RefreshCw, Trash2, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CalendarProviders = () => {
  const navigate = useNavigate();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const apiUrl = import.meta.env.VITE_API_URL || process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${apiUrl}/api/calendar/providers`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProviders(response.data);
    } catch (error) {
      console.error('Error fetching calendar providers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectGoogle = () => {
    const token = localStorage.getItem('token');
    window.location.href = `${apiUrl}/api/calendar/oauth/google?token=${token}`;
  };

  const handleConnectMicrosoft = () => {
    const token = localStorage.getItem('token');
    window.location.href = `${apiUrl}/api/calendar/oauth/microsoft?token=${token}`;
  };

  const handleRefreshToken = async (providerId) => {
    setRefreshing(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${apiUrl}/api/calendar/providers/${providerId}/refresh`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await fetchProviders();
    } catch (error) {
      console.error('Error refreshing token:', error);
      alert('Failed to refresh token. Please reconnect your calendar.');
    } finally {
      setRefreshing(false);
    }
  };

  const handleDisconnect = async (providerId) => {
    if (!window.confirm('Are you sure you want to disconnect this calendar?')) {
      return;
    }

    setDeleting(providerId);
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${apiUrl}/api/calendar/providers/${providerId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchProviders();
    } catch (error) {
      console.error('Error disconnecting calendar:', error);
      alert('Failed to disconnect calendar.');
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calendar Integration</h1>
          <p className="text-gray-600 mt-1">Connect your calendar for AI-powered meeting management</p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={handleConnectGoogle}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Connect Google Calendar
          </Button>
          <Button 
            onClick={handleConnectMicrosoft}
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
          >
            <Plus className="w-4 h-4 mr-2" />
            Connect Outlook Calendar
          </Button>
        </div>
      </div>

      {/* Providers List */}
      {providers.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Calendar className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Calendar Connected</h3>
            <p className="text-gray-600 text-center mb-4">
              Connect your calendar to enable AI-powered meeting detection and scheduling
            </p>
            <div className="flex gap-3">
              <Button onClick={handleConnectGoogle} className="bg-blue-600 hover:bg-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                Connect Google Calendar
              </Button>
              <Button onClick={handleConnectMicrosoft} className="bg-blue-600 hover:bg-blue-700">
                <Plus className="w-4 h-4 mr-2" />
                Connect Outlook Calendar
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {providers.map((provider) => (
            <Card key={provider.id} className="border-green-200 bg-green-50/30">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      provider.provider === 'google' ? 'bg-blue-100' : 'bg-blue-100'
                    }`}>
                      <Calendar className={`w-6 h-6 ${
                        provider.provider === 'google' ? 'text-blue-600' : 'text-blue-600'
                      }`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{provider.email}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <Badge className="bg-green-500">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                        <span className="text-xs capitalize">
                          {provider.provider === 'google' ? 'Google Calendar' : 'Outlook Calendar'}
                        </span>
                      </CardDescription>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDisconnect(provider.id)}
                    disabled={deleting === provider.id}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    {deleting === provider.id ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Status</span>
                    <span className="font-medium text-green-600">Active</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Connected On</span>
                    <span className="font-medium">
                      {new Date(provider.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {provider.last_sync && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Last Synced</span>
                      <span className="font-medium">
                        {new Date(provider.last_sync).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {provider.token_expires_at && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-yellow-600" />
                        <span className="text-sm text-gray-600">Token expires soon</span>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRefreshToken(provider.id)}
                        disabled={refreshing}
                      >
                        {refreshing ? (
                          <RefreshCw className="w-3 h-3 mr-2 animate-spin" />
                        ) : (
                          <RefreshCw className="w-3 h-3 mr-2" />
                        )}
                        Refresh Token
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default CalendarProviders;
