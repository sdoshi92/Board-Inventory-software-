import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from './Layout';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Plus, 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  User, 
  Calendar,
  Package,
  Trash2,
  ChevronDown,
  ChevronRight,
  Minus
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IssueRequests = ({ user, onLogout }) => {
  const [requests, setRequests] = useState([]);
  const [bulkRequests, setBulkRequests] = useState([]);
  const [categories, setCategories] = useState([]);
  const [boards, setBoards] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    approved: false,
    issued: false,
    rejected: false
  });
  const [deleteConfirmDialog, setDeleteConfirmDialog] = useState(false);
  const [requestToDelete, setRequestToDelete] = useState(null);
  const [formData, setFormData] = useState({
    category_id: '',
    serial_number: '',
    issued_to: '',
    project_number: '',
    comments: ''
  });

  const [bulkFormData, setBulkFormData] = useState({
    categories: [{ 
      category_id: '', 
      quantity: 1
    }], 
    issued_to: '',
    project_number: '',
    comments: ''
  });

  useEffect(() => {
    fetchRequests();
    fetchCategories();
    fetchBoards();
    fetchUsers();
  }, []);

  const fetchRequests = async () => {
    try {
      const [requestsRes, bulkRequestsRes] = await Promise.all([
        axios.get(`${API}/issue-requests`),
        axios.get(`${API}/bulk-issue-requests`)
      ]);
      setRequests(requestsRes.data);
      setBulkRequests(bulkRequestsRes.data);
    } catch (error) {
      toast.error('Failed to fetch issue requests');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      toast.error('Failed to fetch categories');
    }
  };

  const fetchBoards = async () => {
    try {
      const response = await axios.get(`${API}/boards`);
      setBoards(response.data); // Get all boards to calculate availability
    } catch (error) {
      toast.error('Failed to fetch boards');
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data.filter(user => user.is_active));
    } catch (error) {
      // If not admin, fallback to empty array (users can type manually)
      setUsers([]);
    }
  };

  const resetForm = () => {
    setFormData({
      category_id: '',
      serial_number: '',
      issued_to: '',
      project_number: '',
      comments: ''
    });
    setBulkFormData({
      categories: [{ 
        category_id: '', 
        quantity: 1
      }],
      issued_to: '',
      project_number: '',
      comments: ''
    });
  };

  const addCategory = () => {
    if (bulkFormData.categories.length < 5) {
      setBulkFormData({
        ...bulkFormData,
        categories: [...bulkFormData.categories, { 
          category_id: '', 
          quantity: 1
        }]
      });
    }
  };

  const removeCategory = (index) => {
    if (bulkFormData.categories.length > 1) {
      const newCategories = bulkFormData.categories.filter((_, i) => i !== index);
      setBulkFormData({
        ...bulkFormData,
        categories: newCategories
      });
    }
  };

  const updateCategory = (index, field, value) => {
    const newCategories = [...bulkFormData.categories];
    if (field === 'quantity') {
      // Ensure quantity is between 1 and 50
      const quantity = Math.max(1, Math.min(50, parseInt(value) || 1));
      newCategories[index][field] = quantity;
    } else if (field === 'category_id') {
      // Reset quantity when category changes
      newCategories[index][field] = value;
      newCategories[index]['quantity'] = 1;
    } else {
      newCategories[index][field] = value;
    }
    setBulkFormData({
      ...bulkFormData,
      categories: newCategories
    });
  };

  const previewAutoSelect = async (categoryIndex) => {
    const category = bulkFormData.categories[categoryIndex];
    if (!category.category_id || !category.quantity) return;

    try {
      const response = await axios.post(`${API}/boards/preview-auto-select`, {
        category_id: category.category_id,
        quantity: category.quantity
      });
      
      const newCategories = [...bulkFormData.categories];
      newCategories[categoryIndex]['auto_select_preview'] = response.data.selected_boards;
      setBulkFormData({
        ...bulkFormData,
        categories: newCategories
      });
    } catch (error) {
      toast.error('Failed to preview auto-select boards');
    }
  };

  const toggleBoardSelection = (categoryIndex, board) => {
    const newCategories = [...bulkFormData.categories];
    const category = newCategories[categoryIndex];
    const existingIndex = category.selected_boards.findIndex(b => b.id === board.id);
    
    if (existingIndex >= 0) {
      // Remove board
      category.selected_boards.splice(existingIndex, 1);
    } else {
      // Add board (max 50)
      if (category.selected_boards.length < 50) {
        category.selected_boards.push({
          id: board.id,
          serial_number: board.serial_number,
          condition: board.condition
        });
      }
    }
    
    setBulkFormData({
      ...bulkFormData,
      categories: newCategories
    });
  };

  const getAvailableBoards = (categoryId) => {
    if (!categoryId) return [];
    return boards.filter(board => 
      board.category_id === categoryId && 
      board.location === 'In stock' && 
      (board.condition === 'New' || board.condition === 'Repaired')
    );
  };

  const getAvailableBoardCount = (categoryId) => {
    if (!categoryId) return 0;
    return boards.filter(board => 
      board.category_id === categoryId && 
      board.location === 'In stock' && 
      (board.condition === 'New' || board.condition === 'Repaired')
    ).length;
  };

  const getTotalBoardsRequested = () => {
    return bulkFormData.categories.reduce((total, cat) => {
      if (cat.mode === 'specific') {
        return total + (cat.selected_boards?.length || 0);
      } else {
        return total + (cat.auto_select_preview?.length || cat.quantity || 0);
      }
    }, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.category_id || !formData.serial_number || !formData.issued_to || !formData.project_number) {
      toast.error('Please fill in all required fields including specific serial number');
      return;
    }

    if (formData.serial_number === 'no-boards') {
      toast.error('No boards available in the selected category');
      return;
    }

    try {
      await axios.post(`${API}/issue-requests`, {
        category_id: formData.category_id,
        serial_number: formData.serial_number,
        issued_to: formData.issued_to,
        project_number: formData.project_number,
        comments: formData.comments
      });
      toast.success('Issue request created successfully');
      setDialogOpen(false);
      resetForm();
      fetchRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create request');
    }
  };

  const handleBulkSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!bulkFormData.issued_to || !bulkFormData.project_number) {
      toast.error('Please fill in issued to and project number');
      return;
    }

    const validCategories = bulkFormData.categories.filter(cat => {
      if (cat.mode === 'specific') {
        return cat.category_id && cat.selected_boards && cat.selected_boards.length > 0;
      } else {
        return cat.category_id && cat.quantity > 0;
      }
    });
    
    if (validCategories.length === 0) {
      toast.error('Please select at least one category with boards');
      return;
    }

    // Check availability for each category
    const unavailableCategories = [];
    for (const cat of validCategories) {
      if (cat.mode === 'specific') {
        // Check if selected boards are still available
        const available = getAvailableBoards(cat.category_id);
        const unavailable = cat.selected_boards.filter(selected => 
          !available.some(avail => avail.id === selected.id)
        );
        if (unavailable.length > 0) {
          const categoryName = getCategoryName(cat.category_id);
          unavailableCategories.push(`${categoryName}: ${unavailable.length} selected boards no longer available`);
        }
      } else {
        const available = getAvailableBoardCount(cat.category_id);
        if (available < cat.quantity) {
          const categoryName = getCategoryName(cat.category_id);
          unavailableCategories.push(`${categoryName}: need ${cat.quantity}, available ${available}`);
        }
      }
    }

    if (unavailableCategories.length > 0) {
      toast.error(`Insufficient boards: ${unavailableCategories.join(', ')}`);
      return;
    }

    const totalBoards = getTotalBoardsRequested();
    if (totalBoards > 250) { // Max total across all categories
      toast.error('Maximum 250 total boards can be requested at once');
      return;
    }

    try {
      // Convert to backend format
      const categories = validCategories.map(cat => ({
        category_id: cat.category_id,
        ...(cat.mode === 'specific' ? 
          { serial_numbers: cat.selected_boards.map(b => b.serial_number) } : 
          { quantity: cat.quantity }
        )
      }));
      
      const response = await axios.post(`${API}/issue-requests/bulk`, {
        categories,
        issued_to: bulkFormData.issued_to,
        project_number: bulkFormData.project_number,
        comments: bulkFormData.comments
      });
      
      toast.success(`Successfully created bulk issue request for ${totalBoards} boards`);
      
      if (response.data.failed_categories && response.data.failed_categories.length > 0) {
        const failures = response.data.failed_categories.map(f => f.error).join(', ');
        toast.warning(`Some categories failed: ${failures}`);
      }
      
      setDialogOpen(false);
      resetForm();
      fetchRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create bulk issue requests');
    }
  };

  const handleApprove = async (requestId) => {
    try {
      // Check if this is a bulk request by finding it in bulkRequests array
      const isBulkRequest = bulkRequests.some(req => req.id === requestId);
      const endpoint = isBulkRequest ? `/bulk-issue-requests/${requestId}` : `/issue-requests/${requestId}`;
      
      await axios.put(`${API}${endpoint}`, {
        status: 'approved'
      });
      toast.success('Request approved successfully');
      fetchRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to approve request');
    }
  };

  const handleReject = async (requestId) => {
    try {
      // Check if this is a bulk request by finding it in bulkRequests array
      const isBulkRequest = bulkRequests.some(req => req.id === requestId);
      const endpoint = isBulkRequest ? `/bulk-issue-requests/${requestId}` : `/issue-requests/${requestId}`;
      
      await axios.put(`${API}${endpoint}`, {
        status: 'rejected'
      });
      toast.success('Request rejected');
      fetchRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reject request');
    }
  };

  const handleDelete = (requestId) => {
    const request = requests.find(req => req.id === requestId);
    setRequestToDelete(request);
    setDeleteConfirmDialog(true);
  };

  const deleteRequest = async (requestId, isBulkRequest = false) => {
    try {
      const endpoint = isBulkRequest ? `/bulk-issue-requests/${requestId}` : `/issue-requests/${requestId}`;
      await axios.delete(`${API}${endpoint}`);
      toast.success('Request deleted successfully');
      fetchRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete request');
    }
  };

  const confirmDelete = async () => {
    if (!requestToDelete) return;

    try {
      await axios.delete(`${API}/issue-requests/${requestToDelete.id}`);
      toast.success('Issue request deleted successfully');
      setDeleteConfirmDialog(false);
      setRequestToDelete(null);
      fetchRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete request');
      setDeleteConfirmDialog(false);
      setRequestToDelete(null);
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.name : 'Unknown';
  };

  const getStatusBadge = (status) => {
    const variants = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'approved': 'bg-green-100 text-green-800',
      'issued': 'bg-blue-100 text-blue-800',
      'rejected': 'bg-red-100 text-red-800'
    };
    return variants[status] || 'bg-gray-100 text-gray-800';
  };

  const getLocationBadge = (location) => {
    const variants = {
      'In stock': 'bg-green-100 text-green-800',
      'Issued': 'bg-blue-100 text-blue-800',
      'Maintenance': 'bg-yellow-100 text-yellow-800',
      'Retired': 'bg-red-100 text-red-800'
    };
    return variants[location] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'approved': return <CheckCircle className="h-4 w-4" />;
      case 'issued': return <Package className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const pendingRequests = [...requests.filter(req => req.status === 'pending'), ...bulkRequests.filter(req => req.status === 'pending')];
  const approvedRequests = [...requests.filter(req => req.status === 'approved'), ...bulkRequests.filter(req => req.status === 'approved')];
  const issuedRequests = [...requests.filter(req => req.status === 'issued'), ...bulkRequests.filter(req => req.status === 'issued')];
  const rejectedRequests = [...requests.filter(req => req.status === 'rejected'), ...bulkRequests.filter(req => req.status === 'rejected')];

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const renderRequestItem = (request, showActions = false) => {
    const isBulkRequest = request.boards && Array.isArray(request.boards);
    const categoryName = isBulkRequest 
      ? `Multiple Categories (${request.boards.length} boards)` 
      : getCategoryName(request.category_id);

    return (
      <div key={request.id} className="border rounded-lg bg-white hover:shadow-md transition-shadow">
        {/* Header */}
        <div className="p-4 border-b bg-gray-50">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-semibold text-gray-900 text-lg">{categoryName}</h4>
              <p className="text-sm text-gray-600 mt-1">
                {isBulkRequest ? `Bulk Request - ${request.boards.length} boards` : `Serial: ${request.serial_number || 'TBD'}`}
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Badge className={`${getStatusBadge(request.status)} text-sm px-3 py-1`}>
                {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
              </Badge>
              {user?.role === 'admin' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => deleteRequest(request.id, isBulkRequest)}
                  className="text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Request Details */}
        <div className="p-4 space-y-4">
          {/* Basic Request Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-blue-900">Requested by:</p>
              <p className="text-sm text-blue-800">{request.requested_by_name || request.requested_by}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-blue-900">Issued to:</p>
              <p className="text-sm text-blue-800 font-medium">{request.issued_to_name || request.issued_to}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-blue-900">Project Number:</p>
              <p className="text-sm text-blue-800 font-medium">{request.project_number}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-blue-900">Request Date:</p>
              <p className="text-sm text-blue-800">{formatDate(request.created_date)}</p>
            </div>
          </div>

          {/* Board Details Section */}
          <div>
            <h5 className="font-medium text-gray-900 mb-3 flex items-center">
              <Package className="h-4 w-4 mr-2 text-blue-600" />
              Board Details
            </h5>
            
            {isBulkRequest ? (
              /* Bulk Request - Show all boards */
              <div className="space-y-2">
                {request.boards.map((board, index) => {
                  const boardCategoryName = getCategoryName(board.category_id);
                  return (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                      <div className="flex items-center space-x-4">
                        <span className="w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </span>
                        <div>
                          <p className="font-medium text-gray-900">{boardCategoryName}</p>
                          <p className="text-sm text-gray-600">Serial: {board.serial_number}</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Badge className={`text-xs ${getStatusBadge(board.condition)}`}>
                          {board.condition}
                        </Badge>
                        <Badge className="text-xs bg-green-100 text-green-800">
                          In Stock
                        </Badge>
                      </div>
                    </div>
                  );
                })}
                
                {/* Summary */}
                <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm font-medium text-green-800">
                    Total: {request.boards.length} boards from {[...new Set(request.boards.map(b => getCategoryName(b.category_id)))].length} categories
                  </p>
                </div>
              </div>
            ) : (
              /* Single Request - Show board details */
              <div className="p-4 bg-gray-50 rounded-lg border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{getCategoryName(request.category_id)}</p>
                    <p className="text-sm text-gray-600">Serial Number: {request.serial_number || 'To be assigned'}</p>
                  </div>
                  <div className="flex space-x-2">
                    <Badge className="text-xs bg-blue-100 text-blue-800">
                      Single Board
                    </Badge>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Comments */}
          {request.comments && (
            <div>
              <h5 className="font-medium text-gray-900 mb-2">Comments:</h5>
              <div className="p-3 bg-gray-50 rounded-md border-l-4 border-blue-500">
                <p className="text-sm text-gray-700">{request.comments}</p>
              </div>
            </div>
          )}

          {/* Approval Actions for Pending Requests */}
          {request.status === 'pending' && user?.role === 'admin' && (
            <div className="flex justify-end space-x-3 pt-4 border-t">
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleReject(request.id)}
                className="text-red-600 hover:text-red-700 border-red-200 hover:border-red-300"
              >
                <XCircle className="h-4 w-4 mr-2" />
                Reject Request
              </Button>
              <Button
                size="sm"
                onClick={() => handleApprove(request.id)}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve & Issue
              </Button>
            </div>
          )}

          {/* Approved/Issued Information */}
          {(request.status === 'approved' || request.status === 'issued') && request.approved_by && (
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm font-medium text-green-800">
                Approved by: {request.approved_by}
              </p>
              {request.approved_date && (
                <p className="text-xs text-green-600 mt-1">
                  Approved on: {formatDate(request.approved_date)}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
            <div className="h-10 bg-gray-200 rounded w-32 animate-pulse"></div>
          </div>
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
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Issue Requests</h1>
            <p className="text-gray-600">Request electronics boards for projects and operations</p>
          </div>
          <Button 
            data-testid="create-issue-request-button"
            onClick={() => setDialogOpen(true)} 
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Request
          </Button>
        </div>

        {/* Requests List */}
        {requests.length === 0 ? (
          <Card className="border-2 border-dashed border-gray-300">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No issue requests yet</h3>
              <p className="text-gray-500 text-center mb-4">Create your first request to get boards for your projects.</p>
              <Button onClick={() => setDialogOpen(true)} className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                New Request
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Pending Requests - Always Visible */}
            {pendingRequests.length > 0 && (
              <Card className="border-0 shadow-lg">
                <CardHeader className="bg-yellow-50 border-b">
                  <CardTitle className="flex items-center space-x-2 text-yellow-800">
                    <Clock className="h-5 w-5" />
                    <span>Pending Requests ({pendingRequests.length})</span>
                  </CardTitle>
                  <CardDescription className="text-yellow-700">
                    Requests waiting for admin approval
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-gray-200">
                    {pendingRequests.map((request) => renderRequestItem(request, true))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Approved Requests - Collapsible */}
            {approvedRequests.length > 0 && (
              <Card className="border-0 shadow-sm">
                <CardHeader 
                  className="cursor-pointer hover:bg-gray-50" 
                  onClick={() => toggleSection('approved')}
                >
                  <CardTitle className="flex items-center justify-between text-green-700">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="h-5 w-5" />
                      <span>Approved Requests ({approvedRequests.length})</span>
                    </div>
                    {expandedSections.approved ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
                  </CardTitle>
                </CardHeader>
                {expandedSections.approved && (
                  <CardContent className="p-0 border-t">
                    <div className="divide-y divide-gray-200">
                      {approvedRequests.map((request) => renderRequestItem(request))}
                    </div>
                  </CardContent>
                )}
              </Card>
            )}

            {/* Issued Requests - Collapsible */}
            {issuedRequests.length > 0 && (
              <Card className="border-0 shadow-sm">
                <CardHeader 
                  className="cursor-pointer hover:bg-gray-50" 
                  onClick={() => toggleSection('issued')}
                >
                  <CardTitle className="flex items-center justify-between text-blue-700">
                    <div className="flex items-center space-x-2">
                      <Package className="h-5 w-5" />
                      <span>Issued Requests ({issuedRequests.length})</span>
                    </div>
                    {expandedSections.issued ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
                  </CardTitle>
                </CardHeader>
                {expandedSections.issued && (
                  <CardContent className="p-0 border-t">
                    <div className="divide-y divide-gray-200">
                      {issuedRequests.map((request) => renderRequestItem(request))}
                    </div>
                  </CardContent>
                )}
              </Card>
            )}

            {/* Rejected Requests - Collapsible */}
            {rejectedRequests.length > 0 && (
              <Card className="border-0 shadow-sm">
                <CardHeader 
                  className="cursor-pointer hover:bg-gray-50" 
                  onClick={() => toggleSection('rejected')}
                >
                  <CardTitle className="flex items-center justify-between text-red-700">
                    <div className="flex items-center space-x-2">
                      <XCircle className="h-5 w-5" />
                      <span>Rejected Requests ({rejectedRequests.length})</span>
                    </div>
                    {expandedSections.rejected ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
                  </CardTitle>
                </CardHeader>
                {expandedSections.rejected && (
                  <CardContent className="p-0 border-t">
                    <div className="divide-y divide-gray-200">
                      {rejectedRequests.map((request) => renderRequestItem(request))}
                    </div>
                  </CardContent>
                )}
              </Card>
            )}
          </div>
        )}

        {/* Create Request Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Issue Request</DialogTitle>
              <DialogDescription>
                Request electronics board(s) for your project or operation.
              </DialogDescription>
            </DialogHeader>
            
            <Tabs defaultValue="single" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="single">Single Board</TabsTrigger>
                <TabsTrigger value="multiple">Multiple Boards</TabsTrigger>
              </TabsList>
              
              {/* Single Board Tab */}
              <TabsContent value="single">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="category_id">Category *</Label>
                    <Select value={formData.category_id} onValueChange={(value) => setFormData({ ...formData, category_id: value, serial_number: '' })}>
                      <SelectTrigger data-testid="category-select">
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map((category) => (
                          <SelectItem key={category.id} value={category.id}>
                            {category.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="serial_number">Specific Serial Number *</Label>
                    <Select value={formData.serial_number} onValueChange={(value) => setFormData({ ...formData, serial_number: value })}>
                      <SelectTrigger data-testid="serial-select">
                        <SelectValue placeholder="Select serial number" />
                      </SelectTrigger>
                      <SelectContent>
                        {formData.category_id ? (
                          getAvailableBoards(formData.category_id).length > 0 ? (
                            getAvailableBoards(formData.category_id).map((board) => (
                              <SelectItem key={board.serial_number} value={board.serial_number}>
                                <div className="flex justify-between items-center w-full">
                                  <span>{board.serial_number}</span>
                                  <div className="flex space-x-2 ml-2">
                                    <Badge className={`text-xs ${getStatusBadge(board.condition)}`}>
                                      {board.condition}
                                    </Badge>
                                    <Badge className={`text-xs ${getLocationBadge(board.location)}`}>
                                      {board.location}
                                    </Badge>
                                  </div>
                                </div>
                              </SelectItem>
                            ))
                          ) : (
                            <SelectItem value="no-boards" disabled>No available boards in this category</SelectItem>
                          )
                        ) : (
                          <SelectItem value="no-category" disabled>Please select a category first</SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                    {formData.category_id && (
                      <p className="text-xs text-gray-500 mt-1">
                        Available boards: {getAvailableBoards(formData.category_id).length}
                      </p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="issued_to">Issued To *</Label>
                    {users.length > 0 ? (
                      <Select 
                        value={formData.issued_to} 
                        onValueChange={(value) => setFormData({ ...formData, issued_to: value })}
                      >
                        <SelectTrigger data-testid="issued-to-select">
                          <SelectValue placeholder="Select user" />
                        </SelectTrigger>
                        <SelectContent>
                          {users.map((user) => (
                            <SelectItem key={user.email} value={user.email}>
                              <div className="flex justify-between items-center w-full">
                                <div>
                                  <span className="font-medium">{user.first_name} {user.last_name}</span>
                                  <span className="text-xs text-gray-500 ml-2">({user.designation})</span>
                                </div>
                                <span className={`ml-2 px-2 py-1 text-xs rounded ${
                                  user.role === 'admin' ? 'bg-red-100 text-red-800' : 
                                  user.role === 'manager' ? 'bg-blue-100 text-blue-800' : 
                                  'bg-green-100 text-green-800'
                                }`}>
                                  {user.role}
                                </span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <Input
                        id="issued_to"
                        data-testid="issued-to-input"
                        value={formData.issued_to}
                        onChange={(e) => setFormData({ ...formData, issued_to: e.target.value })}
                        placeholder="Person or department name"
                        required
                      />
                    )}
                  </div>

                  <div>
                    <Label htmlFor="project_number">Project Number *</Label>
                    <Input
                      id="project_number"
                      data-testid="project-number-input"
                      value={formData.project_number}
                      onChange={(e) => setFormData({ ...formData, project_number: e.target.value })}
                      placeholder="e.g., PRJ-2024-001"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="comments">Comments</Label>
                    <Textarea
                      id="comments"
                      data-testid="comments-input"
                      value={formData.comments}
                      onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
                      placeholder="Additional information or special requirements"
                      rows={3}
                    />
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button 
                      data-testid="create-request-button"
                      type="submit" 
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Create Request
                    </Button>
                  </div>
                </form>
              </TabsContent>
              
              {/* Multiple Boards Tab */}
              <TabsContent value="multiple">
                <form onSubmit={handleBulkSubmit} className="space-y-4">
                  <div className="bg-blue-50 p-4 rounded-lg border">
                    <h4 className="font-medium text-blue-900 mb-2">Bulk Issue Request</h4>
                    <p className="text-sm text-blue-700">
                      Issue multiple boards from up to 5 different categories in a single request.
                      Only "New" and "Repaired" condition boards will be allocated.
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Total boards: {getTotalBoardsRequested()} • Max: 250
                    </p>
                  </div>
                  
                  {/* Category Sections */}
                  {bulkFormData.categories.map((category, index) => (
                    <Card key={index} className="border-2">
                      <CardHeader className="pb-3">
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-lg">Category {index + 1}</CardTitle>
                          {bulkFormData.categories.length > 1 && (
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => removeCategory(index)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Minus className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <Label>Category *</Label>
                          <Select 
                            value={category.category_id} 
                            onValueChange={(value) => updateCategory(index, 'category_id', value)}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select category" />
                            </SelectTrigger>
                            <SelectContent>
                              {categories.map((cat) => (
                                <SelectItem key={cat.id} value={cat.id}>
                                  {cat.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          {category.category_id && (
                            <p className="text-xs text-gray-500 mt-1">
                              Available: {getAvailableBoardCount(category.category_id)} boards
                            </p>
                          )}
                        </div>
                        
                        {/* Quantity Input - Simplified */}
                        {category.category_id && getAvailableBoards(category.category_id).length > 0 && (
                          <div>
                            <Label>Quantity * (Max: 50)</Label>
                            <Input
                              type="number"
                              min="1"
                              max="50"
                              value={category.quantity}
                              onChange={(e) => updateCategory(index, 'quantity', e.target.value)}
                              placeholder="Number of boards needed"
                            />
                            {category.category_id && category.quantity > getAvailableBoardCount(category.category_id) && (
                              <p className="text-xs text-red-600 mt-1">
                                Not enough boards available! Only {getAvailableBoardCount(category.category_id)} boards in stock.
                              </p>
                            )}
                            <p className="text-xs text-gray-500 mt-1">
                              Specific boards will be assigned during approval
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                  
                  {/* Add Category Button */}
                  {bulkFormData.categories.length < 5 && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={addCategory}
                      className="w-full border-dashed"
                    >
                      <Plus className="h-4 w-4 mr-2" />
                      Add Category ({bulkFormData.categories.length}/5)
                    </Button>
                  )}
                  
                  {/* Common Fields */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="bulk_issued_to">Issued To *</Label>
                      {users.length > 0 ? (
                        <Select 
                          value={bulkFormData.issued_to} 
                          onValueChange={(value) => setBulkFormData({ ...bulkFormData, issued_to: value })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select user" />
                          </SelectTrigger>
                          <SelectContent>
                            {users.map((user) => (
                              <SelectItem key={user.email} value={user.email}>
                                <div className="flex justify-between items-center w-full">
                                  <div>
                                    <span className="font-medium">{user.first_name} {user.last_name}</span>
                                    <span className="text-xs text-gray-500 ml-2">({user.designation})</span>
                                  </div>
                                  <span className={`ml-2 px-2 py-1 text-xs rounded ${
                                    user.role === 'admin' ? 'bg-red-100 text-red-800' : 
                                    user.role === 'manager' ? 'bg-blue-100 text-blue-800' : 
                                    'bg-green-100 text-green-800'
                                  }`}>
                                    {user.role}
                                  </span>
                                </div>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Input
                          value={bulkFormData.issued_to}
                          onChange={(e) => setBulkFormData({ ...bulkFormData, issued_to: e.target.value })}
                          placeholder="Person or department name"
                          required
                        />
                      )}
                    </div>
                    
                    <div>
                      <Label htmlFor="bulk_project_number">Project Number *</Label>
                      <Input
                        value={bulkFormData.project_number}
                        onChange={(e) => setBulkFormData({ ...bulkFormData, project_number: e.target.value })}
                        placeholder="e.g., PRJ-2024-001"
                        required
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="bulk_comments">Comments</Label>
                    <Textarea
                      value={bulkFormData.comments}
                      onChange={(e) => setBulkFormData({ ...bulkFormData, comments: e.target.value })}
                      placeholder="Additional information for all boards in this bulk request"
                      rows={3}
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-3 pt-4">
                    <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                      Cancel
                    </Button>
                    <Button 
                      type="submit" 
                      className="bg-green-600 hover:bg-green-700"
                      disabled={getTotalBoardsRequested() === 0 || getTotalBoardsRequested() > 250}
                    >
                      <FileText className="h-4 w-4 mr-2" />
                      Create {getTotalBoardsRequested()} Requests
                    </Button>
                  </div>
                </form>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteConfirmDialog} onOpenChange={setDeleteConfirmDialog}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2 text-red-700">
                <Trash2 className="h-5 w-5" />
                <span>Delete Issue Request</span>
              </DialogTitle>
              <DialogDescription>
                Are you sure you want to delete this issue request? This action cannot be undone.
              </DialogDescription>
            </DialogHeader>
            
            {requestToDelete && (
              <div className="space-y-4">
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-700">
                    <p><strong>Category:</strong> {getCategoryName(requestToDelete.category_id)}</p>
                    <p><strong>Serial:</strong> {requestToDelete.serial_number || 'Any available'}</p>
                    <p><strong>Issued To:</strong> {requestToDelete.issued_to_name || requestToDelete.issued_to}</p>
                    <p><strong>Project:</strong> {requestToDelete.project_number}</p>
                    <p><strong>Status:</strong> <span className="capitalize">{requestToDelete.status}</span></p>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setDeleteConfirmDialog(false);
                      setRequestToDelete(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button 
                    data-testid="confirm-delete-request"
                    onClick={confirmDelete}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Request
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default IssueRequests;
