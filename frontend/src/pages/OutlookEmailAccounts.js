import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog';
import { toast } from 'sonner';
import { Mail, Plus, Trash2, Edit, CheckCircle2, XCircle, Calendar } from 'lucide-react';

const OutlookEmailAccounts = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);

  useEffect(() => {
    loadAccounts();
    
    // Check for OAuth success/error
    const success = searchParams.get('success');
    const error = searchParams.get('error');
    const email = searchParams.get('email');
    
    if (success === 'true' && email) {
      toast.success(`Successfully connected Outlook account: ${email}!`);
      // Clear URL params
      setSearchParams({});
      loadAccounts();
    } else if (error) {
      toast.error(`OAuth failed: ${error}`);
      setSearchParams({});
    }
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await API.getEmailAccounts();
      // Filter only Outlook accounts
      const outlookAccounts = data.filter(acc => acc.account_type === 'oauth_outlook');
      setAccounts(outlookAccounts);
    } catch (error) {
      toast.error('Failed to load email accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthConnect = async () => {
    try {
      const data = await API.getMicrosoftOAuthUrl('email');
      window.location.href = data.url;
    } catch (error) {
      toast.error('Failed to initiate Outlook OAuth flow');
    }
  };

  const handleUpdateAccount = async (e) => {
    e.preventDefault();
    try {
      await API.updateEmailAccount(editingAccount.id, {
        persona: editingAccount.persona,
        signature: editingAccount.signature,
        auto_reply_enabled: editingAccount.auto_reply_enabled,
        is_active: editingAccount.is_active
      });
      toast.success('Account updated successfully');
      setEditDialogOpen(false);
      loadAccounts();
    } catch (error) {
      toast.error('Failed to update account');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to remove this account?')) return;
    
    try {
      await API.deleteEmailAccount(id);
      toast.success('Account removed successfully');
      loadAccounts();
    } catch (error) {
      toast.error('Failed to remove account');
    }
  };

  const handleToggleActive = async (account) => {
    try {
      await API.updateEmailAccount(account.id, {
        is_active: !account.is_active
      });
      toast.success(`Account ${!account.is_active ? 'activated' : 'deactivated'}`);
      loadAccounts();
    } catch (error) {
      toast.error('Failed to update account status');
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
        <h1 className="text-3xl font-bold mb-2">Outlook Email Accounts</h1>
        <p className="text-gray-600">
          Manage your Outlook/Microsoft 365 email accounts for automated email processing
        </p>
      </div>

      {/* Connect Outlook Account Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="w-5 h-5" />
            Connect Outlook Account
          </CardTitle>
          <CardDescription>
            Connect your Outlook or Microsoft 365 email account using OAuth
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={handleOAuthConnect}
            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700"
          >
            <Mail className="w-4 h-4 mr-2" />
            Connect Outlook Email
          </Button>
        </CardContent>
      </Card>

      {/* Connected Accounts */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Connected Outlook Accounts</h2>
        
        {accounts.length === 0 ? (
          <Card>
            <CardContent className="py-8">
              <div className="text-center text-gray-500">
                <Mail className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No Outlook accounts connected yet</p>
                <p className="text-sm mt-1">Click "Connect Outlook Email" above to get started</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          accounts.map(account => (
            <Card key={account.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <CardTitle className="text-lg">{account.email}</CardTitle>
                      <Badge variant={account.is_active ? 'success' : 'secondary'}>
                        {account.is_active ? (
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
                        <Mail className="w-3 h-3 mr-1" />
                        Outlook
                      </Badge>
                    </div>
                    <CardDescription className="space-y-1">
                      <div>Last synced: {account.last_sync_at ? new Date(account.last_sync_at).toLocaleString() : 'Never'}</div>
                      {account.sync_status && (
                        <div>
                          Sync status: <Badge variant="outline" className="text-xs">{account.sync_status}</Badge>
                        </div>
                      )}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleToggleActive(account)}
                    >
                      {account.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditingAccount(account);
                        setEditDialogOpen(true);
                      }}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(account.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              {(account.persona || account.signature) && (
                <CardContent className="space-y-3">
                  {account.persona && (
                    <div>
                      <Label className="text-sm font-medium">Persona</Label>
                      <p className="text-sm text-gray-600 mt-1">{account.persona}</p>
                    </div>
                  )}
                  {account.signature && (
                    <div>
                      <Label className="text-sm font-medium">Signature</Label>
                      <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">{account.signature}</p>
                    </div>
                  )}
                </CardContent>
              )}
            </Card>
          ))
        )}
      </div>

      {/* Edit Account Dialog */}
      {editingAccount && (
        <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Edit Outlook Account</DialogTitle>
              <DialogDescription>
                Update persona, signature, and settings for {editingAccount.email}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleUpdateAccount} className="space-y-4">
              <div>
                <Label htmlFor="persona">Persona (Optional)</Label>
                <Textarea
                  id="persona"
                  value={editingAccount.persona || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, persona: e.target.value})}
                  placeholder="Describe how you want the AI to represent you in emails..."
                  rows={3}
                />
                <p className="text-xs text-gray-500 mt-1">
                  The AI will use this to maintain your communication style
                </p>
              </div>

              <div>
                <Label htmlFor="signature">Email Signature (Optional)</Label>
                <Textarea
                  id="signature"
                  value={editingAccount.signature || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, signature: e.target.value})}
                  placeholder="Best regards,&#10;Your Name&#10;Your Company"
                  rows={4}
                />
                <p className="text-xs text-gray-500 mt-1">
                  This signature will be added to all outgoing emails
                </p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={editingAccount.is_active || false}
                  onChange={(e) => setEditingAccount({...editingAccount, is_active: e.target.checked})}
                  className="rounded"
                />
                <Label htmlFor="is_active" className="cursor-pointer">
                  Account is active (email polling enabled)
                </Label>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setEditDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  Save Changes
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default OutlookEmailAccounts;
