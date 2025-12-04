import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from './Layout';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Checkbox } from './ui/checkbox';
import { 
  Users, 
  UserCheck, 
  UserX, 
  Shield, 
  Edit2, 
  Mail, 
  Calendar,
  Settings,
  Key,
  Trash2,
  AlertTriangle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UserManagement = ({ user, onLogout }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [availablePermissions, setAvailablePermissions] = useState([]);
  const [passwordResetDialog, setPasswordResetDialog] = useState(false);
  const [deleteUserDialog, setDeleteUserDialog] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null);
  const [newPassword, setNewPassword] = useState('');
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    designation: '',
    role: '',
    permissions: [],
    is_active: true
  });

  const roles = [
    { value: 'admin', label: 'Administrator', description: 'Full system access' },
    { value: 'manager', label: 'Manager', description: 'Can approve requests and manage inventory' },
    { value: 'user', label: 'User', description: 'Basic operations and requests' }
  ];

  useEffect(() => {
    if (user.role !== 'admin') {
      toast.error('Access denied. Admin privileges required.');
      return;
    }
    fetchUsers();
    fetchAvailablePermissions();
  }, [user]);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      toast.error('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailablePermissions = async () => {
    try {
      const response = await axios.get(`${API}/permissions/available`);
      setAvailablePermissions(response.data.permissions || []);
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      designation: '',
      role: '',
      permissions: [],
      is_active: true
    });
    setEditingUser(null);
  };

  const handleEdit = (userToEdit) => {
    setEditingUser(userToEdit);
    setFormData({
      first_name: userToEdit.first_name || '',
      last_name: userToEdit.last_name || '',
      designation: userToEdit.designation || '',
      role: userToEdit.role,
      permissions: userToEdit.permissions || [],
      is_active: userToEdit.is_active
    });
    setDialogOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API}/users/${editingUser.id}/permissions`, {
        user_id: editingUser.id,
        permissions: formData.permissions
      });
      
      await axios.put(`${API}/users/${editingUser.email}`, {
        first_name: formData.first_name,
        last_name: formData.last_name,
        designation: formData.designation,
        role: formData.role,
        is_active: formData.is_active
      });
      
      toast.success('User updated successfully');
      setDialogOpen(false);
      resetForm();
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update user');
    }
  };

  const handlePasswordReset = async () => {
    if (!newPassword || newPassword.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    try {
      await axios.post(`${API}/users/reset-password`, {
        user_id: editingUser.id,
        new_password: newPassword
      });
      
      toast.success('Password reset successfully');
      setPasswordResetDialog(false);
      setNewPassword('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reset password');
    }
  };

  const handleDeleteUser = async () => {
    try {
      await axios.delete(`${API}/users/${userToDelete.id}`);
      toast.success('User deleted successfully');
      setDeleteUserDialog(false);
      setUserToDelete(null);
      fetchUsers();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    }
  };

  const togglePermission = (permission) => {
    const newPermissions = formData.permissions.includes(permission)
      ? formData.permissions.filter(p => p !== permission)
      : [...formData.permissions, permission];
    
    setFormData({ ...formData, permissions: newPermissions });
  };

  const getRoleBadge = (role) => {
    const variants = {
      'admin': 'bg-red-100 text-red-800',
      'manager': 'bg-blue-100 text-blue-800',
      'user': 'bg-green-100 text-green-800'
    };
    return variants[role] || 'bg-gray-100 text-gray-800';
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin': return <Shield className="h-4 w-4" />;
      case 'manager': return <UserCheck className="h-4 w-4" />;
      case 'user': return <Users className="h-4 w-4" />;
      default: return <Users className="h-4 w-4" />;
    }
  };

  if (user.role !== 'admin') {
    return (
      <Layout user={user} onLogout={onLogout}>
        <Card className="max-w-md mx-auto mt-8">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <UserX className="h-12 w-12 text-red-500 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Access Denied</h3>
            <p className="text-gray-500 text-center">You need administrator privileges to access user management.</p>
          </CardContent>
        </Card>
      </Layout>
    );
  }

  if (loading) {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="space-y-6">
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
                  <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-6 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">User Management</h1>
          <p className="text-gray-600">Manage user roles and permissions for the inventory system</p>
        </div>

        {/* Users Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {users.map((userItem) => (
            <Card key={userItem.email} className={`hover:shadow-lg transition-all duration-200 border-0 shadow-sm ${
              !userItem.is_active ? 'opacity-60' : ''
            }`}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {getRoleIcon(userItem.role)}
                      <Badge className={`text-xs ${getRoleBadge(userItem.role)}`}>
                        {userItem.role.charAt(0).toUpperCase() + userItem.role.slice(1)}
                      </Badge>
                      {!userItem.is_active && (
                        <Badge variant="secondary" className="text-xs">
                          Inactive
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-lg font-semibold text-gray-900 mb-1">
                      {userItem.first_name} {userItem.last_name}
                    </CardTitle>
                    <p className="text-sm text-gray-600">{userItem.designation}</p>
                  </div>
                  <div className="flex space-x-1">
                    <Button
                      data-testid={`edit-user-${userItem.email}`}
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(userItem)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Mail className="h-4 w-4 mr-2" />
                    <span>{userItem.email}</span>
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    <span>Joined {new Date(userItem.created_at).toLocaleDateString()}</span>
                  </div>

                  {userItem.permissions && userItem.permissions.length > 0 && (
                    <div className="pt-2">
                      <p className="text-xs font-medium text-gray-700 mb-2">Permissions:</p>
                      <div className="flex flex-wrap gap-1">
                        {userItem.permissions.slice(0, 3).map((permission) => (
                          <Badge key={permission} variant="outline" className="text-xs">
                            {permission.replace('_', ' ')}
                          </Badge>
                        ))}
                        {userItem.permissions.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{userItem.permissions.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-2 pt-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditingUser(userItem);
                        setPasswordResetDialog(true);
                      }}
                      className="flex-1 text-orange-600 hover:text-orange-700"
                    >
                      <Key className="h-3 w-3 mr-1" />
                      Reset Password
                    </Button>
                    {userItem.id !== user.id && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setUserToDelete(userItem);
                          setDeleteUserDialog(true);
                        }}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Edit User Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Edit User Permissions</DialogTitle>
              <DialogDescription>
                Update role and permissions for {editingUser?.email}
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSave} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    placeholder="Enter first name"
                  />
                </div>
                <div>
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    placeholder="Enter last name"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="designation">Designation</Label>
                <Input
                  id="designation"
                  value={formData.designation}
                  onChange={(e) => setFormData({ ...formData, designation: e.target.value })}
                  placeholder="Enter job title or designation"
                />
              </div>
              
              <div>
                <Label htmlFor="role">Role *</Label>
                <Select 
                  value={formData.role} 
                  onValueChange={(value) => setFormData({ ...formData, role: value })}
                >
                  <SelectTrigger data-testid="user-role-select">
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                  <SelectContent>
                    {roles.map((role) => (
                      <SelectItem key={role.value} value={role.value}>
                        <div>
                          <div className="font-medium">{role.label}</div>
                          <div className="text-sm text-gray-500">{role.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="is_active">Account Status</Label>
                  <p className="text-sm text-gray-500">Enable or disable user access</p>
                </div>
                <Switch
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                />
              </div>
              
              <div>
                <Label>Specific Permissions</Label>
                <p className="text-sm text-gray-500 mb-3">Grant specific permissions beyond role defaults</p>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {availablePermissions.map((permission) => (
                    <div key={permission} className="flex items-center space-x-2">
                      <Switch
                        id={permission}
                        checked={(formData.permissions || []).includes(permission)}
                        onCheckedChange={() => togglePermission(permission)}
                      />
                      <Label htmlFor={permission} className="text-sm font-normal">
                        {permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button 
                  data-testid="save-user-button"
                  type="submit" 
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Update User
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>

        {/* Password Reset Dialog */}
        <Dialog open={passwordResetDialog} onOpenChange={setPasswordResetDialog}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Reset Password</DialogTitle>
              <DialogDescription>
                Set a new password for {editingUser?.email}
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="new-password">New Password</Label>
                <Input
                  id="new-password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password (min 6 characters)"
                  className="mt-1"
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setPasswordResetDialog(false);
                    setNewPassword('');
                  }}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handlePasswordReset}
                  className="bg-orange-600 hover:bg-orange-700"
                >
                  Reset Password
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Delete User Dialog */}
        <Dialog open={deleteUserDialog} onOpenChange={setDeleteUserDialog}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Delete User</DialogTitle>
              <DialogDescription>
                Are you sure you want to delete {userToDelete?.email}? This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            
            <div className="flex items-center space-x-2 p-4 bg-red-50 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <p className="text-sm text-red-800">
                This will permanently remove the user and all associated data.
              </p>
            </div>
            
            <div className="flex justify-end space-x-3">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setDeleteUserDialog(false);
                  setUserToDelete(null);
                }}
              >
                Cancel
              </Button>
              <Button 
                onClick={handleDeleteUser}
                className="bg-red-600 hover:bg-red-700"
              >
                Delete User
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default UserManagement;
