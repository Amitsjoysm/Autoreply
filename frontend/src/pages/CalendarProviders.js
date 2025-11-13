import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { Calendar, Plus, Trash2, CheckCircle2 } from 'lucide-react';
import { format } from 'date-fns';

const CalendarProviders = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProviders();
    
    // Check for OAuth success/error
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    const email = searchParams.get('email');
    
    if (success === 'true' && email) {
      toast.success(`Successfully connected calendar for ${email}!`);
      // Clear URL params
      setSearchParams({});
    } else if (error) {
      toast.error(`OAuth failed: ${error}`);
      setSearchParams({});
    }
  }, []);

  const loadProviders = async () => {
    try {
      const data = await API.getCalendarProviders();
      setProviders(data);
    } catch (error) {
      toast.error('Failed to load calendar providers');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectGoogle = async () => {
    try {
      const response = await API.axios.get('/oauth/google/url?account_type=calendar');
      window.location.href = response.data.url;
    } catch (error) {
      console.error('Google OAuth error:', error);
      toast.error('Failed to initiate OAuth flow');
    }
  };

  const handleConnectMicrosoft = async () => {
    try {
      const data = await API.getMicrosoftOAuthUrl('calendar');
      window.location.href = data.url;
    } catch (error) {
      console.error('Microsoft OAuth error:', error);
      toast.error('Failed to initiate OAuth flow');
    }
  };

  const handleDelete = async (providerId) => {
    if (!window.confirm('Are you sure you want to disconnect this calendar?')) return;
    
    try {
      await API.deleteCalendarProvider(providerId);
      toast.success('Calendar provider disconnected');
      loadProviders();
    } catch (error) {
      toast.error('Failed to disconnect provider');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading calendar providers...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calendar Providers</h1>
          <p className="text-gray-600 mt-1">Connect your calendar for AI-powered meeting management</p>
        </div>
        <Button 
          onClick={handleConnectGoogle}
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Connect Google Calendar
        </Button>
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
            <Button onClick={handleConnectGoogle}>
              <Plus className="w-4 h-4 mr-2" />
              Connect Google Calendar
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {providers.map((provider) => (
            <Card key={provider.id} className="border-green-200 bg-green-50/30">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-red-600" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{provider.email}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <Badge className="bg-green-500">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          Connected
                        </Badge>
                        <Badge variant="secondary">Google Calendar</Badge>
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Connected:</span>
                    <p className="text-gray-600 mt-1">
                      {provider.created_at && format(new Date(provider.created_at), 'MMM dd, yyyy HH:mm')}
                    </p>
                  </div>
                  
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(provider.id)}
                    className="w-full"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Disconnect
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default CalendarProviders;