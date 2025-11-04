import React, { useState, useEffect } from 'react';
import API from '../api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '../components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Trash2, Edit, Users, List, Search, UserPlus, UserMinus } from 'lucide-react';

const ContactLists = () => {
  const [lists, setLists] = useState([]);
  const [filteredLists, setFilteredLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [manageContactsDialogOpen, setManageContactsDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentList, setCurrentList] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [contacts, setContacts] = useState([]);
  const [listContacts, setListContacts] = useState([]);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    contact_ids: []
  });

  useEffect(() => {
    loadLists();
    loadContacts();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredLists(lists);
    } else {
      const query = searchQuery.toLowerCase();
      setFilteredLists(
        lists.filter(
          list =>
            list.name.toLowerCase().includes(query) ||
            (list.description && list.description.toLowerCase().includes(query))
        )
      );
    }
  }, [searchQuery, lists]);

  const loadLists = async () => {
    try {
      const data = await API.getContactLists();
      setLists(data);
      setFilteredLists(data);
    } catch (error) {
      toast.error('Failed to load contact lists');
    } finally {
      setLoading(false);
    }
  };

  const loadContacts = async () => {
    try {
      const data = await API.getCampaignContacts();
      setContacts(data);
    } catch (error) {
      console.error('Failed to load contacts:', error);
    }
  };

  const loadListContacts = async (listId) => {
    try {
      const data = await API.getListContacts(listId);
      setListContacts(data);
    } catch (error) {
      console.error('Failed to load list contacts:', error);
      setListContacts([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast.error('Please enter a list name');
      return;
    }

    try {
      if (editMode) {
        await API.updateContactList(currentList.id, formData);
        toast.success('List updated successfully');
      } else {
        await API.createContactList(formData);
        toast.success('List created successfully');
      }
      setDialogOpen(false);
      resetForm();
      loadLists();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save list');
    }
  };

  const handleEdit = (list) => {
    setEditMode(true);
    setCurrentList(list);
    setFormData({
      name: list.name,
      description: list.description || '',
      contact_ids: list.contact_ids
    });
    setDialogOpen(true);
  };

  const handleDelete = async (listId) => {
    if (!window.confirm('Are you sure you want to delete this list?')) return;
    
    try {
      await API.deleteContactList(listId);
      toast.success('List deleted successfully');
      loadLists();
    } catch (error) {
      toast.error('Failed to delete list');
    }
  };

  const handleManageContacts = async (list) => {
    setCurrentList(list);
    await loadListContacts(list.id);
    setManageContactsDialogOpen(true);
  };

  const handleAddContact = async (contactId) => {
    try {
      await API.addContactsToList(currentList.id, [contactId]);
      toast.success('Contact added to list');
      await loadListContacts(currentList.id);
      loadLists();
    } catch (error) {
      toast.error('Failed to add contact');
    }
  };

  const handleRemoveContact = async (contactId) => {
    try {
      await API.removeContactsFromList(currentList.id, [contactId]);
      toast.success('Contact removed from list');
      await loadListContacts(currentList.id);
      loadLists();
    } catch (error) {
      toast.error('Failed to remove contact');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      contact_ids: []
    });
    setEditMode(false);
    setCurrentList(null);
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
        <div className="text-gray-500">Loading contact lists...</div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <List className="w-8 h-8 text-blue-600" />
            Contact Lists
          </h1>
          <p className="text-gray-500 mt-1">Organize your contacts into lists for easier campaign management</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-600">
              <Plus className="w-4 h-4" />
              Create List
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>{editMode ? 'Edit List' : 'Create New List'}</DialogTitle>
              <DialogDescription>
                {editMode ? 'Update list details' : 'Create a new contact list'}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>List Name *</Label>
                <Input
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Hot Leads, Q1 Prospects"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of this list..."
                  rows={3}
                />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button type="button" variant="outline" onClick={() => handleDialogClose(false)}>
                  Cancel
                </Button>
                <Button type="submit">
                  {editMode ? 'Update List' : 'Create List'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="Search lists by name or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">Total Lists</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-600">{lists.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">Total Contacts</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-600">{contacts.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-500">Avg Contacts per List</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-600">
              {lists.length > 0 ? Math.round(lists.reduce((sum, l) => sum + l.total_contacts, 0) / lists.length) : 0}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Lists Grid */}
      {filteredLists.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <List className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No contact lists yet</h3>
            <p className="text-gray-500 mb-4">Create your first list to organize your contacts</p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First List
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredLists.map((list) => (
            <Card key={list.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Users className="w-5 h-5 text-blue-600" />
                      {list.name}
                    </CardTitle>
                    {list.description && (
                      <p className="text-sm text-gray-500 mt-1">{list.description}</p>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Contacts</span>
                    <Badge variant="secondary">{list.total_contacts}</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleManageContacts(list)}
                    >
                      <Users className="w-4 h-4 mr-1" />
                      Manage
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEdit(list)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(list.id)}
                      className="text-red-600 hover:text-red-700"
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

      {/* Manage Contacts Dialog */}
      <Dialog open={manageContactsDialogOpen} onOpenChange={setManageContactsDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Manage Contacts - {currentList?.name}</DialogTitle>
            <DialogDescription>
              Add or remove contacts from this list
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* Contacts in List */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Contacts in List ({listContacts.length})
              </h3>
              {listContacts.length === 0 ? (
                <p className="text-sm text-gray-500 py-4 text-center bg-gray-50 rounded-lg">
                  No contacts in this list yet
                </p>
              ) : (
                <div className="border rounded-lg divide-y max-h-48 overflow-y-auto">
                  {listContacts.map((contact) => (
                    <div key={contact.id} className="flex items-center justify-between p-3 hover:bg-gray-50">
                      <div>
                        <p className="text-sm font-medium">
                          {contact.first_name || contact.last_name
                            ? `${contact.first_name || ''} ${contact.last_name || ''}`.trim()
                            : contact.email}
                        </p>
                        <p className="text-xs text-gray-500">{contact.email}</p>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRemoveContact(contact.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <UserMinus className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Available Contacts */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                Available Contacts ({contacts.filter(c => !listContacts.find(lc => lc.id === c.id)).length})
              </h3>
              {contacts.filter(c => !listContacts.find(lc => lc.id === c.id)).length === 0 ? (
                <p className="text-sm text-gray-500 py-4 text-center bg-gray-50 rounded-lg">
                  All contacts are already in this list
                </p>
              ) : (
                <div className="border rounded-lg divide-y max-h-64 overflow-y-auto">
                  {contacts
                    .filter(c => !listContacts.find(lc => lc.id === c.id))
                    .map((contact) => (
                      <div key={contact.id} className="flex items-center justify-between p-3 hover:bg-gray-50">
                        <div>
                          <p className="text-sm font-medium">
                            {contact.first_name || contact.last_name
                              ? `${contact.first_name || ''} ${contact.last_name || ''}`.trim()
                              : contact.email}
                          </p>
                          <p className="text-xs text-gray-500">{contact.email}</p>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAddContact(contact.id)}
                          className="text-green-600 hover:text-green-700"
                        >
                          <UserPlus className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ContactLists;
