import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { Calendar, Plus, Trash2, CheckCircle2, XCircle } from 'lucide-react';

const OutlookCalendarProviders = () => {
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
      toast.success(`Successfully connected Outlook Calendar: ${email}!`);
      // Clear URL params
      setSearchParams({});
      loadProviders();
    } else if (error) {
      toast.error(`OAuth failed: ${error}`);
      setSearchParams({});
    }
  }, []);

  const loadProviders = async () => {
    try {
      const data = await API.getCalendarProviders();
      // Filter only Microsoft/Outlook providers
      const outlookProviders = data.filter(p => p.provider === 'microsoft');
      setProviders(outlookProviders);
    } catch (error) {
      toast.error('Failed to load calendar providers');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectOutlook = async () => {
    try {
      const data = await API.getMicrosoftOAuthUrl('calendar');
      window.location.href = data.url;
    } catch (error) {
      toast.error('Failed to initiate Outlook Calendar OAuth flow');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to disconnect this calendar provider?')) return;
    
    try {
      await API.deleteCalendarProvider(id);
      toast.success('Calendar provider disconnected successfully');
      loadProviders();
    } catch (error) {
      toast.error('Failed to disconnect calendar provider');
    }
  };

  const handleToggleActive = async (provider) => {
    try {
      await API.updateCalendarProvider(provider.id, {
        is_active: !provider.is_active
      });
      toast.success(`Calendar provider ${!provider.is_active ? 'activated' : 'deactivated'}`);
      loadProviders();
    } catch (error) {
      toast.error('Failed to update calendar provider status');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Outlook Calendar Providers</h1>
        <p className="text-gray-600">
          Connect your Outlook/Microsoft 365 calendar for automatic meeting scheduling
        </p>
      </div>

      {/* Connect Outlook Calendar Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Connect Outlook Calendar
          </CardTitle>
          <CardDescription>
            Connect your Outlook or Microsoft 365 calendar to automatically create events from meeting requests
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={handleConnectOutlook}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700"
          >
            <Calendar className="w-4 h-4 mr-2" />
            Connect Outlook Calendar
          </Button>
        </CardContent>
      </Card>

      {/* Connected Providers */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Connected Outlook Calendars</h2>
        
        {providers.length === 0 ? (
          <Card>
            <CardContent className="py-8">
              <div className="text-center text-gray-500">
                <Calendar className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No Outlook calendars connected yet</p>
                <p className="text-sm mt-1">Click "Connect Outlook Calendar" above to get started</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          providers.map(provider => (
            <Card key={provider.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <CardTitle className="text-lg">{provider.email}</CardTitle>
                      <Badge variant={provider.is_active ? 'success' : 'secondary'}>
                        {provider.is_active ? (
                          <>
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                            Active
                          </>
                        ) : (
                          <>
                            <XCircle className="w-3 h-3 mr-1" />
                            Inactive
                          </>
                        )}
                      </Badge>
                      <Badge variant="outline" className="bg-blue-50">
                        <Calendar className="w-3 h-3 mr-1" />
                        Outlook
                      </Badge>
                    </div>
                    <CardDescription className="space-y-1">
                      <div>Connected: {new Date(provider.created_at).toLocaleDateString()}</div>
                      {provider.updated_at && (
                        <div>Last updated: {new Date(provider.updated_at).toLocaleString()}</div>
                      )}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleActive(provider)}
                    >
                      {provider.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(provider.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <strong>Features enabled:</strong>
                  </p>
                  <ul className="text-sm text-gray-600 mt-2 space-y-1 list-disc list-inside">
                    <li>Automatic meeting creation from email requests</li>
                    <li>Microsoft Teams meeting links</li>
                    <li>Calendar conflict detection</li>
                    <li>Event updates and notifications</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default OutlookCalendarProviders;
