import React, { useState, useEffect } from 'react';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';
import { Mail, Plus, Trash2, Edit, CheckCircle2, XCircle, Globe } from 'lucide-react';

const EmailAccounts = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  
  const [formData, setFormData] = useState({
    account_type: 'custom_smtp',
    email: '',
    password: '',
    smtp_host: '',
    smtp_port: '587',
    imap_host: '',
    imap_port: '993',
    persona: '',
    signature: ''
  });

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const data = await API.getEmailAccounts();
      setAccounts(data);
    } catch (error) {
      toast.error('Failed to load email accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuthConnect = (provider) => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    if (provider === 'gmail') {
      window.location.href = `${backendUrl}/api/oauth/google/authorize`;
    } else if (provider === 'outlook') {
      window.location.href = `${backendUrl}/api/oauth/microsoft/authorize`;
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();
    try {
      await API.createEmailAccount(formData);
      toast.success('Email account added successfully');
      setDialogOpen(false);
      resetForm();
      loadAccounts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add email account');
    }
  };

  const handleUpdateAccount = async (e) => {
    e.preventDefault();
    try {
      await API.updateEmailAccount(editingAccount.id, {
        persona: editingAccount.persona,
        signature: editingAccount.signature,
        auto_send: editingAccount.auto_send,
        is_active: editingAccount.is_active
      });
      toast.success('Account updated successfully');
      setEditDialogOpen(false);
      setEditingAccount(null);
      loadAccounts();
    } catch (error) {
      toast.error('Failed to update account');
    }
  };

  const handleDeleteAccount = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this account?')) return;
    
    try {
      await API.deleteEmailAccount(accountId);
      toast.success('Account deleted successfully');
      loadAccounts();
    } catch (error) {
      toast.error('Failed to delete account');
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

  const resetForm = () => {
    setFormData({
      account_type: 'custom_smtp',
      email: '',
      password: '',
      smtp_host: '',
      smtp_port: '587',
      imap_host: '',
      imap_port: '993',
      persona: '',
      signature: ''
    });
  };

  const openEditDialog = (account) => {
    setEditingAccount({...account});
    setEditDialogOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading accounts...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Email Accounts</h1>
          <p className="text-gray-600 mt-1">Connect and manage your email accounts</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
              <Plus className="w-4 h-4 mr-2" />
              Add Account
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Add Email Account</DialogTitle>
              <DialogDescription>Connect via OAuth or manual SMTP/IMAP configuration</DialogDescription>
            </DialogHeader>
            
            {/* OAuth Options */}
            <div className="space-y-4">
              <div>
                <Label className="text-sm font-medium">Quick Connect (OAuth)</Label>
                <div className="grid grid-cols-2 gap-3 mt-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleOAuthConnect('gmail')}
                    className="h-auto py-4"
                  >
                    <div className="flex flex-col items-center gap-2">
                      <Mail className="w-6 h-6 text-red-500" />
                      <span className="font-medium">Gmail</span>
                      <span className="text-xs text-gray-500">OAuth 2.0</span>
                    </div>
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => handleOAuthConnect('outlook')}
                    className="h-auto py-4"
                  >
                    <div className="flex flex-col items-center gap-2">
                      <Mail className="w-6 h-6 text-blue-500" />
                      <span className="font-medium">Outlook</span>
                      <span className="text-xs text-gray-500">OAuth 2.0</span>
                    </div>
                  </Button>
                </div>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-white px-2 text-gray-500">Or manual configuration</span>
                </div>
              </div>

              {/* Manual SMTP Form */}
              <form onSubmit={handleManualSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      placeholder="your@email.com"
                      required
                    />
                  </div>
                  
                  <div className="col-span-2">
                    <Label htmlFor="password">Password/App Password *</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({...formData, password: e.target.value})}
                      placeholder="••••••••"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="smtp_host">SMTP Host *</Label>
                    <Input
                      id="smtp_host"
                      value={formData.smtp_host}
                      onChange={(e) => setFormData({...formData, smtp_host: e.target.value})}
                      placeholder="smtp.gmail.com"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="smtp_port">SMTP Port *</Label>
                    <Input
                      id="smtp_port"
                      value={formData.smtp_port}
                      onChange={(e) => setFormData({...formData, smtp_port: e.target.value})}
                      placeholder="587"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="imap_host">IMAP Host *</Label>
                    <Input
                      id="imap_host"
                      value={formData.imap_host}
                      onChange={(e) => setFormData({...formData, imap_host: e.target.value})}
                      placeholder="imap.gmail.com"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="imap_port">IMAP Port *</Label>
                    <Input
                      id="imap_port"
                      value={formData.imap_port}
                      onChange={(e) => setFormData({...formData, imap_port: e.target.value})}
                      placeholder="993"
                      required
                    />
                  </div>

                  <div className="col-span-2">
                    <Label htmlFor="persona">Persona (Optional)</Label>
                    <Textarea
                      id="persona"
                      value={formData.persona}
                      onChange={(e) => setFormData({...formData, persona: e.target.value})}
                      placeholder="e.g., Professional, friendly tone. Customer support representative..."
                      rows={3}
                    />
                  </div>

                  <div className="col-span-2">
                    <Label htmlFor="signature">Email Signature (Optional)</Label>
                    <Textarea
                      id="signature"
                      value={formData.signature}
                      onChange={(e) => setFormData({...formData, signature: e.target.value})}
                      placeholder="Best regards,&#10;John Doe&#10;Support Team"
                      rows={3}
                    />
                  </div>

                  <div className="col-span-2 flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="auto_send"
                      checked={formData.auto_send}
                      onChange={(e) => setFormData({...formData, auto_send: e.target.checked})}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="auto_send" className="cursor-pointer">
                      Auto-send validated drafts
                    </Label>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button type="submit" className="flex-1">Add Account</Button>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Accounts List */}
      {accounts.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Mail className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Email Accounts</h3>
            <p className="text-gray-600 text-center mb-4">
              Get started by connecting your first email account
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Account
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {accounts.map((account) => (
            <Card key={account.id} className={account.is_active ? 'border-green-200 bg-green-50/30' : 'border-gray-200'}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      account.account_type === 'oauth_gmail' ? 'bg-red-100' :
                      account.account_type === 'oauth_outlook' ? 'bg-blue-100' :
                      'bg-purple-100'
                    }`}>
                      {account.account_type === 'oauth_gmail' ? (
                        <Mail className="w-6 h-6 text-red-600" />
                      ) : account.account_type === 'oauth_outlook' ? (
                        <Mail className="w-6 h-6 text-blue-600" />
                      ) : (
                        <Globe className="w-6 h-6 text-purple-600" />
                      )}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{account.email}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-1">
                        <Badge variant={account.account_type.includes('oauth') ? 'default' : 'secondary'}>
                          {account.account_type === 'oauth_gmail' ? 'Gmail OAuth' :
                           account.account_type === 'oauth_outlook' ? 'Outlook OAuth' :
                           'Manual SMTP'}
                        </Badge>
                        {account.is_active ? (
                          <Badge className="bg-green-500">
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                            Active
                          </Badge>
                        ) : (
                          <Badge variant="destructive">
                            <XCircle className="w-3 h-3 mr-1" />
                            Inactive
                          </Badge>
                        )}
                      </CardDescription>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {account.persona && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">Persona:</span>
                      <p className="text-gray-600 mt-1 line-clamp-2">{account.persona}</p>
                    </div>
                  )}
                  
                  {account.signature && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">Signature:</span>
                      <p className="text-gray-600 mt-1 whitespace-pre-wrap line-clamp-2">{account.signature}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-2 border-t">
                    <div className="text-xs text-gray-500">
                      Auto-send: {account.auto_send ? 'Enabled' : 'Disabled'}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openEditDialog(account)}
                      className="flex-1"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      variant={account.is_active ? 'outline' : 'default'}
                      onClick={() => handleToggleActive(account)}
                      className="flex-1"
                    >
                      {account.is_active ? 'Deactivate' : 'Activate'}
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDeleteAccount(account.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Account Settings</DialogTitle>
            <DialogDescription>Update persona, signature, and auto-send settings</DialogDescription>
          </DialogHeader>
          
          {editingAccount && (
            <form onSubmit={handleUpdateAccount} className="space-y-4">
              <div>
                <Label htmlFor="edit_persona">Persona</Label>
                <Textarea
                  id="edit_persona"
                  value={editingAccount.persona || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, persona: e.target.value})}
                  placeholder="Define the tone and style for AI responses..."
                  rows={4}
                />
              </div>

              <div>
                <Label htmlFor="edit_signature">Email Signature</Label>
                <Textarea
                  id="edit_signature"
                  value={editingAccount.signature || ''}
                  onChange={(e) => setEditingAccount({...editingAccount, signature: e.target.value})}
                  placeholder="Your email signature..."
                  rows={4}
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="edit_auto_send"
                  checked={editingAccount.auto_send || false}
                  onChange={(e) => setEditingAccount({...editingAccount, auto_send: e.target.checked})}
                  className="w-4 h-4"
                />
                <Label htmlFor="edit_auto_send" className="cursor-pointer">
                  Auto-send validated drafts
                </Label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="edit_is_active"
                  checked={editingAccount.is_active || false}
                  onChange={(e) => setEditingAccount({...editingAccount, is_active: e.target.checked})}
                  className="w-4 h-4"
                />
                <Label htmlFor="edit_is_active" className="cursor-pointer">
                  Account is active
                </Label>
              </div>

              <div className="flex gap-3">
                <Button type="submit" className="flex-1">Save Changes</Button>
                <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EmailAccounts;
