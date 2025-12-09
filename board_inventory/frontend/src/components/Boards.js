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
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Package, 
  Search,
  Filter,
  CheckCircle,
  AlertTriangle,
  XCircle,
  MapPin,
  Calendar,
  User
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Boards = ({ user, onLogout }) => {
  const [boards, setBoards] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingBoard, setEditingBoard] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterCondition, setFilterCondition] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    category_id: '',
    serial_number: '',
    condition: 'New',
    qc_by: '',
    comments: '',
    picture: null
  });

  const locations = [
    'In stock',
    'Issued for machine',
    'Repairing',
    'Issued for spares',
    'At customer site'
  ];

  const conditions = ['New', 'Repaired', 'Scrap'];

  useEffect(() => {
    fetchBoards();
    fetchCategories();
  }, []);

  const fetchBoards = async () => {
    try {
      const response = await axios.get(`${API}/boards`);
      setBoards(response.data);
    } catch (error) {
      toast.error('Failed to fetch boards');
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

  const resetForm = () => {
    setFormData({
      category_id: '',
      serial_number: '',
      condition: 'New',
      qc_by: '',
      comments: '',
      picture: null
    });
    setEditingBoard(null);
  };

  const getNextSerialNumber = (categoryId) => {
    if (!categoryId) return '';
    
    const categoryBoards = boards.filter(board => board.category_id === categoryId);
    if (categoryBoards.length === 0) return '0001';
    
    const serialNumbers = categoryBoards
      .map(board => parseInt(board.serial_number) || 0)
      .filter(num => !isNaN(num))
      .sort((a, b) => b - a);
    
    const nextNumber = serialNumbers.length > 0 ? serialNumbers[0] + 1 : 1;
    return nextNumber.toString().padStart(4, '0');
  };

  const handleCreate = () => {
    resetForm();
    setDialogOpen(true);
  };

  const handleEdit = (board) => {
    setFormData({
      category_id: board.category_id,
      serial_number: board.serial_number,
      condition: board.condition,
      qc_by: board.qc_by || '',
      comments: board.comments || '',
      picture: null
    });
    setEditingBoard(board);
    setDialogOpen(true);
  };

  const handleCategoryChange = (categoryId) => {
    const nextSerial = getNextSerialNumber(categoryId);
    setFormData({
      ...formData,
      category_id: categoryId,
      serial_number: nextSerial
    });
  };

  const getSelectedCategory = () => {
    return categories.find(cat => cat.id === formData.category_id);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.category_id || !formData.serial_number) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      if (editingBoard) {
        await axios.put(`${API}/boards/${editingBoard.id}`, {
          condition: formData.condition,
          qc_by: formData.qc_by,
          comments: formData.comments
        });
        toast.success('Board updated successfully');
      } else {
        // For new boards, always set location to "In stock"
        const boardData = {
          ...formData,
          location: 'In stock'
        };
        delete boardData.picture; // Handle picture upload separately if needed
        await axios.post(`${API}/boards`, boardData);
        toast.success('Board created successfully');
      }
      setDialogOpen(false);
      resetForm();
      fetchBoards();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (boardId, serialNumber) => {
    if (!window.confirm(`Are you sure you want to delete board "${serialNumber}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await axios.delete(`${API}/boards/${boardId}`);
      toast.success('Board deleted successfully');
      fetchBoards();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete board');
    }
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.name : 'Unknown';
  };

  const getStatusBadge = (condition) => {
    const variants = {
      'New': 'bg-green-100 text-green-800',
      'Repaired': 'bg-blue-100 text-blue-800',
      'Scrap': 'bg-red-100 text-red-800'
    };
    return variants[condition] || 'bg-gray-100 text-gray-800';
  };

  const getLocationBadge = (location) => {
    const variants = {
      'In stock': 'bg-blue-100 text-blue-800',
      'Issued for machine': 'bg-purple-100 text-purple-800',
      'Repairing': 'bg-orange-100 text-orange-800',
      'Issued for spares': 'bg-indigo-100 text-indigo-800',
      'At customer site': 'bg-pink-100 text-pink-800'
    };
    return variants[location] || 'bg-gray-100 text-gray-800';
  };

  const filteredBoards = boards.filter(board => {
    const matchesCategory = !filterCategory || filterCategory === 'all' || board.category_id === filterCategory;
    const matchesLocation = !filterLocation || filterLocation === 'all' || board.location === filterLocation;
    const matchesCondition = !filterCondition || filterCondition === 'all' || board.condition === filterCondition;
    const matchesSearch = !searchTerm || 
      board.serial_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (board.issued_to && board.issued_to.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (board.project_number && board.project_number.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesCategory && matchesLocation && matchesCondition && matchesSearch;
  });

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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Electronics Boards</h1>
            <p className="text-gray-600">Manage your electronics board inventory</p>
          </div>
          <Button 
            data-testid="add-board-button"
            onClick={handleCreate} 
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Board
          </Button>
        </div>

        {/* Filters */}
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div>
                <Label htmlFor="search">Search</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    id="search"
                    data-testid="board-search-input"
                    placeholder="Serial number, issued to..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div>
                <Label>Category</Label>
                <Select value={filterCategory} onValueChange={setFilterCategory}>
                  <SelectTrigger data-testid="category-filter">
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Location</Label>
                <Select value={filterLocation} onValueChange={setFilterLocation}>
                  <SelectTrigger data-testid="location-filter">
                    <SelectValue placeholder="All locations" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All locations</SelectItem>
                    {locations.map((location) => (
                      <SelectItem key={location} value={location}>
                        {location}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label>Condition</Label>
                <Select value={filterCondition} onValueChange={setFilterCondition}>
                  <SelectTrigger data-testid="condition-filter">
                    <SelectValue placeholder="All conditions" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All conditions</SelectItem>
                    {conditions.map((condition) => (
                      <SelectItem key={condition} value={condition}>
                        {condition}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-end">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setFilterCategory('all');
                    setFilterLocation('all');
                    setFilterCondition('all');
                    setSearchTerm('');
                  }}
                  className="w-full"
                >
                  Clear Filters
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Boards Grid */}
        {filteredBoards.length === 0 ? (
          <Card className="border-2 border-dashed border-gray-300">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {boards.length === 0 ? 'No boards yet' : 'No boards match your filters'}
              </h3>
              <p className="text-gray-500 text-center mb-4">
                {boards.length === 0 
                  ? 'Get started by adding your first electronics board.' 
                  : 'Try adjusting your search criteria or filters.'
                }
              </p>
              {boards.length === 0 && (
                <Button onClick={handleCreate} className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Board
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBoards.map((board) => (
              <Card key={board.id} className="hover:shadow-lg transition-all duration-200 border-0 shadow-sm">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg font-semibold text-gray-900 mb-1">
                        {board.serial_number}
                      </CardTitle>
                      <CardDescription className="text-sm text-gray-600">
                        {getCategoryName(board.category_id)}
                      </CardDescription>
                    </div>
                    <div className="flex space-x-1 ml-2">
                      <Button
                        data-testid={`edit-board-${board.id}`}
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(board)}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        data-testid={`delete-board-${board.id}`}
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(board.id, board.serial_number)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        Location
                      </span>
                      <Badge className={`text-xs ${getLocationBadge(board.location)}`}>
                        {board.location}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Condition</span>
                      <Badge className={`text-xs ${getStatusBadge(board.condition)}`}>
                        {board.condition}
                      </Badge>
                    </div>
                    
                    {board.issued_to && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 flex items-center">
                          <User className="h-4 w-4 mr-1" />
                          Issued to
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {board.issued_to}
                        </span>
                      </div>
                    )}
                    
                    {board.project_number && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Project</span>
                        <span className="text-sm font-medium text-gray-900">
                          {board.project_number}
                        </span>
                      </div>
                    )}
                    
                    <div className="flex items-center text-xs text-gray-500 pt-2 border-t">
                      <Calendar className="h-3 w-3 mr-1" />
                      <span>Added {new Date(board.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Add/Edit Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>
                {editingBoard ? 'Edit Board' : 'Add New Board'}
              </DialogTitle>
              <DialogDescription>
                {editingBoard 
                  ? 'Update the board information below.'
                  : 'Fill in the details to add a new electronics board to inventory.'
                }
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="category_id">Category *</Label>
                <Select 
                  value={formData.category_id} 
                  onValueChange={handleCategoryChange}
                  disabled={!!editingBoard}
                >
                  <SelectTrigger data-testid="board-category-select">
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        <div className="flex items-center space-x-2">
                          {category.picture_url && (
                            <img 
                              src={category.picture_url} 
                              alt={category.name}
                              className="w-6 h-6 object-cover rounded"
                            />
                          )}
                          <span>{category.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                {/* Category Picture Preview */}
                {formData.category_id && getSelectedCategory() && (
                  <div className="mt-3 p-4 bg-gray-50 rounded-lg border">
                    <div className="flex items-center space-x-4">
                      {getSelectedCategory().picture_url ? (
                        <img 
                          src={getSelectedCategory().picture_url} 
                          alt={getSelectedCategory().name}
                          className="w-20 h-20 object-cover rounded-lg border shadow-sm"
                        />
                      ) : (
                        <div className="w-20 h-20 bg-gray-200 rounded-lg border flex items-center justify-center">
                          <Package className="h-8 w-8 text-gray-400" />
                        </div>
                      )}
                      <div>
                        <h4 className="font-semibold text-gray-900">{getSelectedCategory().name}</h4>
                        <p className="text-sm text-gray-600">{getSelectedCategory().manufacturer}</p>
                        <p className="text-xs text-gray-500">Version {getSelectedCategory().version}</p>
                        <p className="text-xs text-blue-600 font-medium mt-1">
                          Next Serial: {formData.serial_number}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div>
                <Label htmlFor="serial_number">Serial Number * (Auto-generated)</Label>
                <Input
                  id="serial_number"
                  data-testid="board-serial-input"
                  value={formData.serial_number}
                  onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                  placeholder="Auto-generated based on category"
                  disabled={!!editingBoard}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  {!editingBoard && formData.category_id && `Next available: ${formData.serial_number}`}
                </p>
              </div>
              
              <div>
                <Label htmlFor="condition">Condition</Label>
                <Select 
                  value={formData.condition} 
                  onValueChange={(value) => setFormData({ ...formData, condition: value })}
                >
                  <SelectTrigger data-testid="board-condition-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {conditions.map((condition) => (
                      <SelectItem key={condition} value={condition}>
                        {condition}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div>
                <Label htmlFor="qc_by">QC By</Label>
                <Input
                  id="qc_by"
                  data-testid="board-qc-input"
                  value={formData.qc_by}
                  onChange={(e) => setFormData({ ...formData, qc_by: e.target.value })}
                  placeholder="Quality control personnel"
                />
              </div>
              
              <div>
                <Label htmlFor="picture">Board Picture</Label>
                <Input
                  id="picture"
                  data-testid="board-picture-input"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFormData({ ...formData, picture: e.target.files[0] })}
                  className="mt-1"
                />
                <p className="text-xs text-gray-500 mt-1">Upload an image of this board (optional)</p>
              </div>

              <div>
                <Label htmlFor="comments">Comments</Label>
                <Textarea
                  id="comments"
                  data-testid="board-comments-input"
                  value={formData.comments}
                  onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
                  placeholder="Additional notes or comments"
                  rows={3}
                />
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
                  data-testid="save-board-button"
                  type="submit" 
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {editingBoard ? 'Update' : 'Add'} Board
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default Boards;
