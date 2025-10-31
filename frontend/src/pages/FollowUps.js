import React, { useState, useEffect } from 'react';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { toast } from 'sonner';
import { UserPlus, Clock, Trash2, CheckCircle2, XCircle } from 'lucide-react';
import { format } from 'date-fns';

const FollowUps = () => {
  const [followUps, setFollowUps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFollowUps();
  }, []);

  const loadFollowUps = async () => {
    try {
      const data = await API.getFollowUps();
      setFollowUps(data);
    } catch (error) {
      toast.error('Failed to load follow-ups');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (followUpId) => {
    if (!window.confirm('Are you sure you want to cancel this follow-up?')) return;
    
    try {
      await API.deleteFollowUp(followUpId);
      toast.success('Follow-up cancelled');
      loadFollowUps();
    } catch (error) {
      toast.error('Failed to cancel follow-up');
    }
  };

  const getStatusBadge = (followUp) => {
    if (followUp.sent) {
      return (
        <Badge className="bg-green-500">
          <CheckCircle2 className="w-3 h-3 mr-1" />
          Sent
        </Badge>
      );
    }
    if (followUp.cancelled) {
      return (
        <Badge variant="destructive">
          <XCircle className="w-3 h-3 mr-1" />
          Cancelled
        </Badge>
      );
    }
    return (
      <Badge className="bg-blue-500">
        <Clock className="w-3 h-3 mr-1" />
        Scheduled
      </Badge>
    );
  };

  const stats = {
    total: followUps.length,
    scheduled: followUps.filter(f => !f.sent && !f.cancelled).length,
    sent: followUps.filter(f => f.sent).length,
    cancelled: followUps.filter(f => f.cancelled).length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading follow-ups...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Follow-ups</h1>
        <p className="text-gray-600 mt-1">Manage scheduled follow-up emails</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-700">Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-blue-900">Scheduled</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-900">{stats.scheduled}</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-green-900">Sent</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-900">{stats.sent}</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-red-900">Cancelled</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-900">{stats.cancelled}</div>
          </CardContent>
        </Card>
      </div>

      {/* Follow-ups List */}
      {followUps.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <UserPlus className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Follow-ups</h3>
            <p className="text-gray-600 text-center">
              Follow-ups are automatically scheduled based on email responses
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {followUps.map((followUp) => (
            <Card key={followUp.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <CardTitle className="text-lg">Follow-up for: {followUp.original_subject}</CardTitle>
                      {getStatusBadge(followUp)}
                    </div>
                    <CardDescription className="flex items-center gap-4">
                      <span>To: {followUp.recipient_email}</span>
                      {followUp.scheduled_at && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          Scheduled: {format(new Date(followUp.scheduled_at), 'MMM dd, yyyy HH:mm')}
                        </span>
                      )}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {followUp.follow_up_message && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <Label className="text-sm font-medium text-gray-700">Follow-up Message</Label>
                    <p className="text-sm text-gray-900 mt-2 whitespace-pre-wrap line-clamp-3">
                      {followUp.follow_up_message}
                    </p>
                  </div>
                )}

                <div className="flex items-center justify-between pt-2 border-t">
                  <div className="text-sm text-gray-600">
                    {followUp.sent && followUp.sent_at && (
                      <span>Sent: {format(new Date(followUp.sent_at), 'MMM dd, yyyy HH:mm')}</span>
                    )}
                  </div>
                  {!followUp.sent && !followUp.cancelled && (
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(followUp.id)}
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Cancel Follow-up
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default FollowUps;