import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from './Layout';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { 
  Send, 
  Package, 
  FileText, 
  User, 
  Calendar,
  CheckCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Outward = ({ user, onLogout }) => {
  const [approvedRequests, setApprovedRequests] = useState([]);
  const [availableBoards, setAvailableBoards] = useState([]);
  const [categories, setCategories] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingRequest, setProcessingRequest] = useState(null);
  const [confirmationDialog, setConfirmationDialog] = useState(false);
  const [issueDetails, setIssueDetails] = useState(null);
  const [editableIssueDetails, setEditableIssueDetails] = useState({
    issuedBy: '',
    issuedTo: ''
  });
  const [directIssueForm, setDirectIssueForm] = useState({
    board_id: '',
    issued_to: '',
    project_number: '',
    comments: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [requestsRes, bulkRequestsRes, boardsRes, categoriesRes, usersRes] = await Promise.all([
        axios.get(`${API}/issue-requests`),
        axios.get(`${API}/bulk-issue-requests`).catch(() => ({ data: [] })), // Fallback if permission denied
        axios.get(`${API}/boards`),
        axios.get(`${API}/categories`),
        axios.get(`${API}/users`).catch(() => ({ data: [] })) // Fallback if not admin
      ]);
      
      // Combine individual and bulk approved requests
      const individualApproved = requestsRes.data.filter(req => req.status === 'approved');
      const bulkApproved = bulkRequestsRes.data.filter(req => req.status === 'approved');
      setApprovedRequests([...individualApproved, ...bulkApproved]);
      setAvailableBoards(boardsRes.data.filter(board => 
        (board.location === 'In stock' && (board.condition === 'New' || board.condition === 'Repaired')) ||
        (board.location === 'Repairing' && board.condition === 'Repaired')
      ));
      setCategories(categoriesRes.data);
      setUsers(usersRes.data.filter(user => user.is_active));
    } catch (error) {
      toast.error('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const handleIssueFromRequest = (requestId) => {
    const request = approvedRequests.find(req => req.id === requestId);
    if (request) {
      let details;
      if (isBulkRequest(request)) {
        // For bulk requests, show summary
        details = {
          type: 'bulk-request',
          requestId: requestId,
          issuedTo: request.issued_to,
          issuedBy: user.email,
          projectNumber: request.project_number,
          category: `Bulk Request (${request.boards.length} boards)`,
          serialNumber: `${request.boards.length} boards total`,
          boards: request.boards,
          timestamp: new Date().toLocaleString()
        };
      } else {
        // For individual requests
        details = {
          type: 'request',
          requestId: requestId,
          issuedTo: request.issued_to,
          issuedBy: user.email,
          projectNumber: request.project_number,
          category: getCategoryName(request.category_id),
          serialNumber: request.serial_number || 'Any available',
          timestamp: new Date().toLocaleString()
        };
      }
      
      setIssueDetails(details);
      setEditableIssueDetails({
        issuedBy: user.email,
        issuedTo: request.issued_to
      });
      setConfirmationDialog(true);
    }
  };

  const confirmIssueFromRequest = async () => {
    setProcessingRequest(issueDetails.requestId);
    setConfirmationDialog(false);
    try {
      const response = await axios.post(`${API}/outward`, {
        request_id: issueDetails.requestId,
        issued_by_override: editableIssueDetails.issuedBy,
        issued_to_override: editableIssueDetails.issuedTo
      });
      
      if (issueDetails.type === 'bulk-request') {
        // Handle bulk request response
        if (response.data.issued_boards && response.data.issued_boards.length > 0) {
          let message = `${response.data.issued_boards.length} boards issued successfully`;
          if (response.data.failed_boards && response.data.failed_boards.length > 0) {
            message += `, ${response.data.failed_boards.length} failed`;
          }
          toast.success(message);
        } else {
          toast.error('No boards could be issued from the bulk request');
        }
      } else {
        // Handle individual request response
        toast.success(`Board ${response.data.serial_number} issued successfully`);
      }
      
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to issue board');
    } finally {
      setProcessingRequest(null);
      setIssueDetails(null);
    }
  };

  const handleDirectIssue = (e) => {
    e.preventDefault();
    
    if (!directIssueForm.board_id || !directIssueForm.issued_to) {
      toast.error('Please fill in all required fields');
      return;
    }

    const boardInfo = getBoardInfo(directIssueForm.board_id);
    setIssueDetails({
      type: 'direct',
      boardId: directIssueForm.board_id,
      issuedTo: directIssueForm.issued_to,
      issuedBy: user.email,
      projectNumber: directIssueForm.project_number || 'N/A',
      category: boardInfo.category,
      serialNumber: boardInfo.serial,
      timestamp: new Date().toLocaleString()
    });
    setEditableIssueDetails({
      issuedBy: user.email,
      issuedTo: directIssueForm.issued_to
    });
    setConfirmationDialog(true);
  };

  const confirmDirectIssue = async () => {
    setConfirmationDialog(false);
    try {
      const response = await axios.post(`${API}/outward`, {
        board_id: issueDetails.boardId,
        issued_to: editableIssueDetails.issuedTo,
        issued_by_override: editableIssueDetails.issuedBy,
        project_number: directIssueForm.project_number,
        comments: directIssueForm.comments
      });
      toast.success(`Board ${response.data.serial_number} issued successfully`);
      setDirectIssueForm({ board_id: '', issued_to: '', project_number: '', comments: '' });
      setIssueDetails(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to issue board');
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.name : 'Unknown Category';
  };

  const isBulkRequest = (request) => {
    return request.boards && Array.isArray(request.boards);
  };

  const renderRequestTitle = (request) => {
    if (isBulkRequest(request)) {
      return `Bulk Request (${request.boards.length} boards)`;
    } else {
      return getCategoryName(request.category_id);
    }
  };

  const renderRequestDescription = (request) => {
    if (isBulkRequest(request)) {
      const uniqueCategories = [...new Set(request.boards.map(board => getCategoryName(board.category_id)))];
      return `Categories: ${uniqueCategories.join(', ')}`;
    } else {
      return request.serial_number ? `Serial: ${request.serial_number}` : 'Any available board';
    }
  };

  const getBoardInfo = (boardId) => {
    const board = availableBoards.find(b => b.id === boardId);
    if (!board) return { serial: 'Unknown', category: 'Unknown' };
    return {
      serial: board.serial_number,
      category: getCategoryName(board.category_id)
    };
  };

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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Outward Operations</h1>
          <p className="text-gray-600">Issue electronics boards to projects and operations</p>
        </div>

        <Tabs defaultValue="requests" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger data-testid="approved-requests-tab" value="requests">
              Approved Requests ({approvedRequests.length})
            </TabsTrigger>
            <TabsTrigger data-testid="direct-issue-tab" value="direct">
              Direct Issue
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="requests" className="space-y-6">
            {/* Approved Requests */}
            {approvedRequests.length === 0 ? (
              <Card className="border-2 border-dashed border-gray-300">
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <FileText className="h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No approved requests</h3>
                  <p className="text-gray-500 text-center">All approved requests have been processed or no requests are pending.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {approvedRequests.map((request) => (
                  <Card key={request.id} className="hover:shadow-lg transition-all duration-200 border-0 shadow-sm">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <CheckCircle className="h-4 w-4 text-green-600" />
                            <Badge className="bg-green-100 text-green-800 text-xs">
                              Approved
                            </Badge>
                          </div>
                          <CardTitle className="text-lg font-semibold text-gray-900 mb-1">
                            {renderRequestTitle(request)}
                          </CardTitle>
                          <CardDescription className="text-sm text-gray-600">
                            {renderRequestDescription(request)}
                          </CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        <div className="flex items-center text-sm text-gray-600">
                          <User className="h-4 w-4 mr-2" />
                          <span className="font-medium">Issue to:</span>
                          <span className="ml-1">{request.issued_to_name || request.issued_to}</span>
                        </div>
                        
                        <div className="flex items-center text-sm text-gray-600">
                          <FileText className="h-4 w-4 mr-2" />
                          <span className="font-medium">Project:</span>
                          <span className="ml-1">{request.project_number}</span>
                        </div>
                        
                        <div className="flex items-center text-sm text-gray-600">
                          <User className="h-4 w-4 mr-2" />
                          <span className="font-medium">Requested by:</span>
                          <span className="ml-1">{request.requested_by_name || request.requested_by}</span>
                        </div>
                        
                        <div className="flex items-center text-xs text-gray-500 pt-2 border-t">
                          <Calendar className="h-3 w-3 mr-1" />
                          <span>Approved {new Date(request.approved_date_time).toLocaleDateString()}</span>
                        </div>
                        
                        {request.comments && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-700">{request.comments}</p>
                          </div>
                        )}
                        
                        <Button
                          data-testid={`issue-request-${request.id}`}
                          onClick={() => handleIssueFromRequest(request.id)}
                          disabled={processingRequest === request.id}
                          className="w-full bg-blue-600 hover:bg-blue-700 mt-4"
                        >
                          <Send className="h-4 w-4 mr-2" />
                          {processingRequest === request.id ? 'Processing...' : 'Issue Board'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="direct" className="space-y-6">
            {/* Direct Issue Form */}
            <Card className="max-w-md mx-auto">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Send className="h-5 w-5 text-blue-600" />
                  <span>Direct Board Issue</span>
                </CardTitle>
                <CardDescription>
                  Issue a board directly without going through the request process
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleDirectIssue} className="space-y-4">
                  <div>
                    <Label htmlFor="board_id">Select Board *</Label>
                    <Select 
                      value={directIssueForm.board_id} 
                      onValueChange={(value) => setDirectIssueForm({ ...directIssueForm, board_id: value })}
                    >
                      <SelectTrigger data-testid="direct-board-select">
                        <SelectValue placeholder="Choose available board" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableBoards.map((board) => {
                          const boardInfo = getBoardInfo(board.id);
                          return (
                            <SelectItem key={board.id} value={board.id}>
                              {boardInfo.serial} - {boardInfo.category}
                            </SelectItem>
                          );
                        })}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="issued_to">Issued To *</Label>
                    {users.length > 0 ? (
                      <Select 
                        value={directIssueForm.issued_to} 
                        onValueChange={(value) => setDirectIssueForm({ ...directIssueForm, issued_to: value })}
                      >
                        <SelectTrigger data-testid="direct-issued-to-select">
                          <SelectValue placeholder="Select user or department" />
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
                        data-testid="direct-issued-to-input"
                        value={directIssueForm.issued_to}
                        onChange={(e) => setDirectIssueForm({ ...directIssueForm, issued_to: e.target.value })}
                        placeholder="Person or department name"
                        required
                      />
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="project_number">Project Number</Label>
                    <Input
                      id="project_number"
                      data-testid="direct-project-input"
                      value={directIssueForm.project_number}
                      onChange={(e) => setDirectIssueForm({ ...directIssueForm, project_number: e.target.value })}
                      placeholder="e.g., PRJ-2024-001"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="comments">Comments</Label>
                    <Input
                      id="comments"
                      data-testid="direct-comments-input"
                      value={directIssueForm.comments}
                      onChange={(e) => setDirectIssueForm({ ...directIssueForm, comments: e.target.value })}
                      placeholder="Optional comments or notes"
                    />
                  </div>
                  
                  <Button 
                    data-testid="direct-issue-button"
                    type="submit" 
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Issue Board
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Available Boards Summary */}
            {availableBoards.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Package className="h-5 w-5 text-green-600" />
                    <span>Available Boards ({availableBoards.length})</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {availableBoards.slice(0, 6).map((board) => (
                      <div key={board.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="font-medium text-gray-900">{board.serial_number}</div>
                        <div className="text-sm text-gray-600">{getCategoryName(board.category_id)}</div>
                        <div className="text-xs text-green-600 mt-1">In Stock • {board.condition}</div>
                      </div>
                    ))}
                    {availableBoards.length > 6 && (
                      <div className="p-3 bg-gray-50 rounded-lg flex items-center justify-center">
                        <span className="text-sm text-gray-500">+{availableBoards.length - 6} more</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Issue Confirmation Dialog */}
        <Dialog open={confirmationDialog} onOpenChange={setConfirmationDialog}>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center space-x-2">
                <Send className="h-5 w-5 text-blue-600" />
                <span>Confirm Board Issue</span>
              </DialogTitle>
              <DialogDescription>
                Please review and edit the details before issuing the board
              </DialogDescription>
            </DialogHeader>
            
            {issueDetails && (
              <div className="space-y-6">
                {/* Request Info */}
                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">Type:</span>
                    <span className="text-sm font-semibold text-gray-900">{issueDetails.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">
                      {issueDetails.type === 'bulk-request' ? 'Boards:' : 'Serial:'}
                    </span>
                    <span className="text-sm font-semibold text-gray-900">{issueDetails.serialNumber}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">Project:</span>
                    <span className="text-sm font-semibold text-gray-900">{issueDetails.projectNumber}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">Time:</span>
                    <span className="text-sm font-semibold text-purple-700">{issueDetails.timestamp}</span>
                  </div>
                  
                  {/* Show board details for bulk requests */}
                  {issueDetails.type === 'bulk-request' && issueDetails.boards && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <span className="text-sm font-medium text-gray-600 block mb-2">Board Details:</span>
                      <div className="max-h-32 overflow-y-auto space-y-1">
                        {issueDetails.boards.map((board, index) => (
                          <div key={index} className="text-xs text-gray-700 bg-white p-2 rounded">
                            <span className="font-medium">{getCategoryName(board.category_id)}</span>
                            {board.serial_number && <span className="ml-2">({board.serial_number})</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Editable Fields */}
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="issued_by_edit">Issued By *</Label>
                    <Select 
                      value={editableIssueDetails.issuedBy} 
                      onValueChange={(value) => setEditableIssueDetails({...editableIssueDetails, issuedBy: value})}
                    >
                      <SelectTrigger data-testid="edit-issued-by-select" className="mt-1">
                        <SelectValue placeholder="Select who is issuing this board" />
                      </SelectTrigger>
                      <SelectContent>
                        {users.map((user) => (
                          <SelectItem key={`issued-by-${user.email}`} value={user.email}>
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
                  </div>
                  
                  <div>
                    <Label htmlFor="issued_to_edit">Issued To *</Label>
                    <Select 
                      value={editableIssueDetails.issuedTo} 
                      onValueChange={(value) => setEditableIssueDetails({...editableIssueDetails, issuedTo: value})}
                    >
                      <SelectTrigger data-testid="edit-issued-to-select" className="mt-1">
                        <SelectValue placeholder="Select who is receiving this board" />
                      </SelectTrigger>
                      <SelectContent>
                        {users.map((user) => (
                          <SelectItem key={`issued-to-${user.email}`} value={user.email}>
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
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setConfirmationDialog(false);
                      setIssueDetails(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button 
                    data-testid="confirm-issue-button"
                    onClick={issueDetails.type === 'request' || issueDetails.type === 'bulk-request' ? confirmIssueFromRequest : confirmDirectIssue}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Confirm Issue
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

export default Outward;
