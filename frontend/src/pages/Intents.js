import React, { useState, useEffect } from 'react';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '../components/ui/dialog';
import { toast } from 'sonner';
import { Target, Plus, Trash2, Edit, CheckCircle2, XCircle, ArrowUp, ArrowDown } from 'lucide-react';

const Intents = () => {
  const [intents, setIntents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentIntent, setCurrentIntent] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    keywords: '',
    prompt: '',
    priority: 1,
    auto_send: false,
    is_inbound_lead: false,
    is_active: true
  });

  useEffect(() => {
    loadIntents();
  }, []);

  const loadIntents = async () => {
    try {
      const data = await API.getIntents();
      setIntents(data.sort((a, b) => b.priority - a.priority));
    } catch (error) {
      toast.error('Failed to load intents');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const keywordsArray = formData.keywords
      .split(',')
      .map(k => k.trim())
      .filter(k => k.length > 0);

    if (keywordsArray.length === 0) {
      toast.error('Please provide at least one keyword');
      return;
    }

    const intentData = {
      name: formData.name,
      description: formData.description,
      keywords: keywordsArray,
      prompt: formData.prompt,
      priority: parseInt(formData.priority),
      auto_send: formData.auto_send,
      is_inbound_lead: formData.is_inbound_lead,
      is_active: formData.is_active
    };

    try {
      if (editMode) {
        await API.updateIntent(currentIntent.id, intentData);
        toast.success('Intent updated successfully');
      } else {
        await API.createIntent(intentData);
        toast.success('Intent created successfully');
      }
      setDialogOpen(false);
      resetForm();
      loadIntents();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save intent');
    }
  };

  const handleEdit = (intent) => {
    setEditMode(true);
    setCurrentIntent(intent);
    setFormData({
      name: intent.name,
      description: intent.description || '',
      keywords: intent.keywords.join(', '),
      prompt: intent.prompt,
      priority: intent.priority,
      auto_send: intent.auto_send || false,
      is_inbound_lead: intent.is_inbound_lead || false,
      is_active: intent.is_active
    });
    setDialogOpen(true);
  };

  const handleDelete = async (intentId) => {
    if (!window.confirm('Are you sure you want to delete this intent?')) return;
    
    try {
      await API.deleteIntent(intentId);
      toast.success('Intent deleted successfully');
      loadIntents();
    } catch (error) {
      toast.error('Failed to delete intent');
    }
  };

  const handleToggleActive = async (intent) => {
    try {
      await API.updateIntent(intent.id, {
        is_active: !intent.is_active
      });
      toast.success(`Intent ${!intent.is_active ? 'activated' : 'deactivated'}`);
      loadIntents();
    } catch (error) {
      toast.error('Failed to update intent');
    }
  };

  const handlePriorityChange = async (intent, direction) => {
    const newPriority = direction === 'up' ? intent.priority + 1 : intent.priority - 1;
    try {
      await API.updateIntent(intent.id, { priority: newPriority });
      toast.success('Priority updated');
      loadIntents();
    } catch (error) {
      toast.error('Failed to update priority');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      keywords: '',
      prompt: '',
      priority: 1,
      is_active: true
    });
    setEditMode(false);
    setCurrentIntent(null);
  };

  const handleDialogClose = (open) => {
    if (!open) {
      resetForm();
    }
    setDialogOpen(open);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading intents...</div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Email Intents</h1>
          <p className="text-gray-600 mt-1">Define intents for AI-powered email classification and responses</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
              <Plus className="w-4 h-4 mr-2" />
              Create Intent
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editMode ? 'Edit Intent' : 'Create New Intent'}</DialogTitle>
              <DialogDescription>
                Define how the AI should recognize and respond to specific types of emails
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">Intent Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="e.g., Customer Support Request"
                  required
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Brief description of this intent"
                />
              </div>

              <div>
                <Label htmlFor="keywords">Keywords (comma-separated) *</Label>
                <Input
                  id="keywords"
                  value={formData.keywords}
                  onChange={(e) => setFormData({...formData, keywords: e.target.value})}
                  placeholder="support, help, issue, problem, bug"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter keywords that help identify this intent
                </p>
              </div>

              <div>
                <Label htmlFor="prompt">Response Guidelines/Prompt *</Label>
                <Textarea
                  id="prompt"
                  value={formData.prompt}
                  onChange={(e) => setFormData({...formData, prompt: e.target.value})}
                  placeholder="Provide detailed instructions for the AI on how to respond to this type of email..."
                  rows={6}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Define how the AI should craft responses for this intent
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="priority">Priority (1-10)</Label>
                  <Input
                    id="priority"
                    type="number"
                    min="1"
                    max="10"
                    value={formData.priority}
                    onChange={(e) => setFormData({...formData, priority: e.target.value})}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Higher priority intents are matched first
                  </p>
                </div>

                <div className="flex items-center gap-2 pt-8">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="is_active" className="cursor-pointer">
                    Intent is active
                  </Label>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Button type="submit" className="flex-1">
                  {editMode ? 'Update Intent' : 'Create Intent'}
                </Button>
                <Button type="button" variant="outline" onClick={() => handleDialogClose(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Intents List */}
      {intents.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Target className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Intents Configured</h3>
            <p className="text-gray-600 text-center mb-4">
              Create your first intent to enable AI-powered email classification
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Intent
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {intents.map((intent, index) => (
            <Card 
              key={intent.id} 
              className={`transition-all ${intent.is_active ? 'border-purple-200 bg-purple-50/30' : 'border-gray-200 opacity-60'}`}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-xl">{intent.name}</CardTitle>
                      <Badge 
                        variant={intent.is_active ? 'default' : 'secondary'}
                        className={intent.is_active ? 'bg-purple-600' : ''}
                      >
                        {intent.is_active ? (
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
                      <Badge variant="outline">
                        Priority: {intent.priority}
                      </Badge>
                    </div>
                    {intent.description && (
                      <CardDescription className="mt-2">{intent.description}</CardDescription>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handlePriorityChange(intent, 'up')}
                      disabled={index === 0}
                    >
                      <ArrowUp className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handlePriorityChange(intent, 'down')}
                      disabled={index === intents.length - 1}
                    >
                      <ArrowDown className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-sm font-medium text-gray-700">Keywords</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {intent.keywords.map((keyword, idx) => (
                      <Badge key={idx} variant="secondary" className="bg-gray-100">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-700">Response Guidelines</Label>
                  <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap line-clamp-3">
                      {intent.prompt}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleEdit(intent)}
                    className="flex-1"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant={intent.is_active ? 'outline' : 'default'}
                    onClick={() => handleToggleActive(intent)}
                    className="flex-1"
                  >
                    {intent.is_active ? 'Deactivate' : 'Activate'}
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(intent.id)}
                  >
                    <Trash2 className="w-4 h-4" />
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

export default Intents;
