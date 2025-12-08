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
  User,
  Wrench,
  PackagePlus
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Inward = ({ user, onLogout }) => {
  const [boards, setBoards] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inwardTypeDialog, setInwardTypeDialog] = useState(true); // Show selection dialog by default
  const [boardDialog, setBoardDialog] = useState(false);
  const [inwardType, setInwardType] = useState(''); // 'new' or 'repair'
  const [editingBoard, setEditingBoard] = useState(null);
  const [formData, setFormData] = useState({
    category_id: '',
    serial_number: '',
    condition: 'New',
    qc_by: '',
    comments: '',
    picture: null
  });

  const [bulkFormData, setBulkFormData] = useState({
    category_id: '',
    start_serial: '',
    end_serial: '',
    condition: 'New',
    qc_by: '',
    comments: ''
  });

  // Conditions based on inward type
  const getAvailableConditions = () => {
    if (inwardType === 'new') {
      return ['New']; // New boards can only be in "New" condition
    } else if (inwardType === 'repair') {
      return ['Repairing', 'New', 'Repaired', 'Scrap']; // Repair/Return boards can have multiple conditions
    }
    return ['New']; // Default
  };

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
      condition: inwardType === 'new' ? 'New' : 'New', // Allow all conditions for repair workflow
      qc_by: '',
      comments: '',
      picture: null
    });
    setBulkFormData({
      category_id: '',
      start_serial: '',
      end_serial: '',
      condition: 'New',
      qc_by: '',
      comments: ''
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

  const getExistingSerialNumbers = (categoryId) => {
    if (!categoryId) return [];
    // For repair/return workflow, only show boards that are NOT in stock
    // (issued boards, scrapped boards, etc.)
    return boards.filter(board => 
      board.category_id === categoryId && board.location !== 'In stock'
    );
  };

  const handleInwardTypeSelect = (type) => {
    setInwardType(type);
    setInwardTypeDialog(false);
    setBoardDialog(true);
    resetForm();
  };

  const handleCategoryChange = (categoryId) => {
    if (inwardType === 'new') {
      const nextSerial = getNextSerialNumber(categoryId);
      setFormData({
        ...formData,
        category_id: categoryId,
        serial_number: nextSerial
      });
    } else {
      setFormData({
        ...formData,
        category_id: categoryId,
        serial_number: ''
      });
    }
  };

  const handleBulkCategoryChange = (categoryId) => {
    const nextSerial = getNextSerialNumber(categoryId);
    setBulkFormData({
      ...bulkFormData,
      category_id: categoryId,
      start_serial: nextSerial,
      end_serial: ''
    });
  };

  const calculateBoardCount = () => {
    if (!bulkFormData.start_serial || !bulkFormData.end_serial) return 0;
    const start = parseInt(bulkFormData.start_serial) || 0;
    const end = parseInt(bulkFormData.end_serial) || 0;
    return end >= start ? end - start + 1 : 0;
  };

  const validateSerialRange = () => {
    const start = parseInt(bulkFormData.start_serial) || 0;
    const end = parseInt(bulkFormData.end_serial) || 0;
    
    if (end < start) {
      return "End serial number must be greater than or equal to start serial number";
    }
    
    // Check for existing serial numbers in the range
    if (bulkFormData.category_id) {
      const categoryBoards = boards.filter(board => board.category_id === bulkFormData.category_id);
      for (let i = start; i <= end; i++) {
        const serialStr = i.toString().padStart(4, '0');
        if (categoryBoards.some(board => board.serial_number === serialStr)) {
          return `Serial number ${serialStr} already exists`;
        }
      }
    }
    
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.category_id || !formData.serial_number) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      if (inwardType === 'repair') {
        // For repair workflow, validate that serial number exists and update existing board
        const existingBoard = boards.find(board => 
          board.serial_number === formData.serial_number && board.category_id === formData.category_id
        );
        
        if (!existingBoard) {
          toast.error('Serial number does not exist in the selected category');
          return;
        }
        
        // Update existing board to set location to "Repairing" and update condition
        await axios.put(`${API}/boards/${existingBoard.id}`, {
          location: 'Repairing',
          condition: formData.condition,
          comments: formData.comments
        });
        toast.success('Board processed for repairing/return successfully');
      } else {
        // For new workflow, create new board with location "In stock"
        const boardData = {
          ...formData,
          location: 'In stock'
        };
        delete boardData.picture; // Handle picture upload separately if needed
        
        await axios.post(`${API}/boards`, boardData);
        toast.success('Board added to inventory successfully');
      }
      
      setBoardDialog(false);
      resetForm();
      fetchBoards();
      setInwardTypeDialog(true); // Show selection dialog again
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleBulkSubmit = async (e) => {
    e.preventDefault();
    
    if (!bulkFormData.category_id || !bulkFormData.start_serial || !bulkFormData.end_serial) {
      toast.error('Please fill in all required fields');
      return;
    }

    const validationError = validateSerialRange();
    if (validationError) {
      toast.error(validationError);
      return;
    }

    const count = calculateBoardCount();
    if (count === 0) {
      toast.error('Invalid serial number range');
      return;
    }

    if (count > 100) {
      toast.error('Cannot add more than 100 boards at once');
      return;
    }

    try {
      const start = parseInt(bulkFormData.start_serial);
      const end = parseInt(bulkFormData.end_serial);
      
      // Create array of boards to add
      const boardsToAdd = [];
      for (let i = start; i <= end; i++) {
        const serialNumber = i.toString().padStart(4, '0');
        boardsToAdd.push({
          category_id: bulkFormData.category_id,
          serial_number: serialNumber,
          condition: bulkFormData.condition,
          location: 'In stock',
          qc_by: bulkFormData.qc_by,
          comments: bulkFormData.comments
        });
      }

      // Add boards in batches to avoid overwhelming the server
      const batchSize = 10;
      let successCount = 0;
      
      for (let i = 0; i < boardsToAdd.length; i += batchSize) {
        const batch = boardsToAdd.slice(i, i + batchSize);
        const promises = batch.map(boardData => axios.post(`${API}/boards`, boardData));
        
        try {
          await Promise.all(promises);
          successCount += batch.length;
        } catch (error) {
          console.error(`Error in batch ${i / batchSize + 1}:`, error);
          toast.error(`Error adding some boards. Successfully added ${successCount} out of ${count} boards.`);
          break;
        }
      }
      
      if (successCount === count) {
        toast.success(`Successfully added ${count} boards to inventory`);
        setBoardDialog(false);
        resetForm();
        fetchBoards();
        setInwardTypeDialog(true);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Bulk add operation failed');
    }
  };

  const getSelectedCategory = () => {
    return categories.find(cat => cat.id === formData.category_id);
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(cat => cat.id === categoryId);
    return category ? category.name : 'Unknown';
  };

  const getStatusBadge = (condition) => {
    const variants = {
      'New': 'bg-green-100 text-green-800',
      'Repaired': 'bg-blue-100 text-blue-800',
      'Repairing': 'bg-yellow-100 text-yellow-800',
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

  if (loading) {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Inward Operations</h1>
          <p className="text-gray-600">Add new boards to inventory or process boards for repair and return</p>
        </div>

        {/* Recent Inward Activities */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {boards.slice(0, 6).map((board) => (
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
                  
                  <div className="flex items-center text-xs text-gray-500 pt-2 border-t">
                    <Calendar className="h-3 w-3 mr-1" />
                    <span>Added {new Date(board.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Inward Type Selection Dialog */}
        <Dialog open={inwardTypeDialog} onOpenChange={setInwardTypeDialog}>
          <DialogContent className="sm:max-w-lg border-0 shadow-2xl rounded-2xl">
            <DialogHeader className="text-center pb-6">
              <DialogTitle className="text-2xl font-light text-gray-900 mb-2">
                Choose Operation Type
              </DialogTitle>
              <DialogDescription className="text-base text-gray-600">
                Select the type of inward operation to begin
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-3">
              <div 
                className="group cursor-pointer rounded-xl border border-gray-200 hover:border-green-300 hover:shadow-lg transition-all duration-300 bg-white"
                onClick={() => handleInwardTypeSelect('new')}
              >
                <div className="p-6 flex items-center space-x-4">
                  <div className="p-4 bg-green-50 rounded-full group-hover:bg-green-100 transition-colors">
                    <PackagePlus className="h-7 w-7 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-1">New Board</h3>
                    <p className="text-sm text-gray-500">Add new electronics boards to inventory</p>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  </div>
                </div>
              </div>

              <div 
                className="group cursor-pointer rounded-xl border border-gray-200 hover:border-orange-300 hover:shadow-lg transition-all duration-300 bg-white"
                onClick={() => handleInwardTypeSelect('repair')}
              >
                <div className="p-6 flex items-center space-x-4">
                  <div className="p-4 bg-orange-50 rounded-full group-hover:bg-orange-100 transition-colors">
                    <Wrench className="h-7 w-7 text-orange-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-1">Repairing/Return</h3>
                    <p className="text-sm text-gray-500">Process existing boards for repair or return</p>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-100">
              <Button 
                variant="ghost" 
                onClick={() => setInwardTypeDialog(false)}
                className="w-full text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Board Form Dialog */}
        <Dialog open={boardDialog} onOpenChange={setBoardDialog}>
          <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {inwardType === 'new' ? 'Add New Board' : 'Process Board for Repairing/Return'}
              </DialogTitle>
              <DialogDescription>
                {inwardType === 'new' 
                  ? 'Add new electronics board(s) to inventory'
                  : 'Select an existing board to process for repair or return'
                }
              </DialogDescription>
            </DialogHeader>
            
            {inwardType === 'new' ? (
              /* New Board - Show Tabs for Single/Multiple */
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
                      <Select 
                        value={formData.category_id} 
                        onValueChange={handleCategoryChange}
                      >
                        <SelectTrigger data-testid="inward-category-select">
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
                        data-testid="inward-serial-input"
                        value={formData.serial_number}
                        onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                        placeholder="Auto-generated based on category"
                        required
                      />
                      {formData.category_id && (
                        <p className="text-xs text-gray-500 mt-1">
                          Next available: {formData.serial_number}
                        </p>
                      )}
                    </div>
                    
                    <div>
                      <Label htmlFor="condition">Condition</Label>
                      <Select 
                        value={formData.condition} 
                        onValueChange={(value) => setFormData({ ...formData, condition: value })}
                      >
                        <SelectTrigger data-testid="inward-condition-select">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {getAvailableConditions().map((condition) => (
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
                        data-testid="inward-qc-input"
                        value={formData.qc_by}
                        onChange={(e) => setFormData({ ...formData, qc_by: e.target.value })}
                        placeholder="Quality control personnel"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="picture">Board Picture</Label>
                      <Input
                        id="picture"
                        data-testid="inward-picture-input"
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
                        data-testid="inward-comments-input"
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
                        onClick={() => setBoardDialog(false)}
                      >
                        Cancel
                      </Button>
                      <Button 
                        data-testid="save-inward-button"
                        type="submit" 
                        className="bg-green-600 hover:bg-green-700"
                      >
                        Add to Inventory
                      </Button>
                    </div>
                  </form>
                </TabsContent>
                
                {/* Multiple Boards Tab */}
                <TabsContent value="multiple">
                  <form onSubmit={handleBulkSubmit} className="space-y-4">
                    <div>
                      <Label htmlFor="bulk_category_id">Category *</Label>
                      <Select 
                        value={bulkFormData.category_id} 
                        onValueChange={handleBulkCategoryChange}
                      >
                        <SelectTrigger data-testid="bulk-category-select">
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
                      {bulkFormData.category_id && categories.find(cat => cat.id === bulkFormData.category_id) && (
                        <div className="mt-3 p-4 bg-gray-50 rounded-lg border">
                          <div className="flex items-center space-x-4">
                            {categories.find(cat => cat.id === bulkFormData.category_id).picture_url ? (
                              <img 
                                src={categories.find(cat => cat.id === bulkFormData.category_id).picture_url} 
                                alt={categories.find(cat => cat.id === bulkFormData.category_id).name}
                                className="w-20 h-20 object-cover rounded-lg border shadow-sm"
                              />
                            ) : (
                              <div className="w-20 h-20 bg-gray-200 rounded-lg border flex items-center justify-center">
                                <Package className="h-8 w-8 text-gray-400" />
                              </div>
                            )}
                            <div>
                              <h4 className="font-semibold text-gray-900">{categories.find(cat => cat.id === bulkFormData.category_id).name}</h4>
                              <p className="text-sm text-gray-600">{categories.find(cat => cat.id === bulkFormData.category_id).manufacturer}</p>
                              <p className="text-xs text-gray-500">Version {categories.find(cat => cat.id === bulkFormData.category_id).version}</p>
                              <p className="text-xs text-blue-600 font-medium mt-1">
                                Suggested Start: {bulkFormData.start_serial}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="start_serial">Start Serial Number *</Label>
                        <Input
                          id="start_serial"
                          data-testid="bulk-start-serial-input"
                          value={bulkFormData.start_serial}
                          onChange={(e) => setBulkFormData({ ...bulkFormData, start_serial: e.target.value })}
                          placeholder="e.g., 0001"
                          required
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Suggested: {bulkFormData.start_serial}
                        </p>
                      </div>
                      
                      <div>
                        <Label htmlFor="end_serial">End Serial Number *</Label>
                        <Input
                          id="end_serial"
                          data-testid="bulk-end-serial-input"
                          value={bulkFormData.end_serial}
                          onChange={(e) => setBulkFormData({ ...bulkFormData, end_serial: e.target.value })}
                          placeholder="e.g., 0100"
                          required
                        />
                        {calculateBoardCount() > 0 && (
                          <p className="text-xs text-green-600 font-medium mt-1">
                            Will add {calculateBoardCount()} boards
                          </p>
                        )}
                        {calculateBoardCount() > 100 && (
                          <p className="text-xs text-red-600 mt-1">
                            Maximum 100 boards allowed
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <Label htmlFor="bulk_condition">Condition</Label>
                      <Select 
                        value={bulkFormData.condition} 
                        onValueChange={(value) => setBulkFormData({ ...bulkFormData, condition: value })}
                      >
                        <SelectTrigger data-testid="bulk-condition-select">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {getAvailableConditions().map((condition) => (
                            <SelectItem key={condition} value={condition}>
                              {condition}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="bulk_qc_by">QC By</Label>
                      <Input
                        id="bulk_qc_by"
                        data-testid="bulk-qc-input"
                        value={bulkFormData.qc_by}
                        onChange={(e) => setBulkFormData({ ...bulkFormData, qc_by: e.target.value })}
                        placeholder="Quality control personnel"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="bulk_comments">Comments</Label>
                      <Textarea
                        id="bulk_comments"
                        data-testid="bulk-comments-input"
                        value={bulkFormData.comments}
                        onChange={(e) => setBulkFormData({ ...bulkFormData, comments: e.target.value })}
                        placeholder="Comments for all boards in this batch"
                        rows={3}
                      />
                    </div>
                    
                    <div className="flex justify-end space-x-3 pt-4">
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setBoardDialog(false)}
                      >
                        Cancel
                      </Button>
                      <Button 
                        data-testid="save-bulk-inward-button"
                        type="submit" 
                        className="bg-green-600 hover:bg-green-700"
                        disabled={calculateBoardCount() === 0 || calculateBoardCount() > 100}
                      >
                        Add {calculateBoardCount()} Boards
                      </Button>
                    </div>
                  </form>
                </TabsContent>
              </Tabs>
            ) : (
              /* Repair/Return Form - No Tabs Needed */
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="category_id">Category *</Label>
                  <Select 
                    value={formData.category_id} 
                    onValueChange={handleCategoryChange}
                  >
                    <SelectTrigger data-testid="inward-category-select">
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
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="serial_number">
                    Serial Number * (Select Issued/Scrapped Board)
                  </Label>
                  <Select 
                    value={formData.serial_number} 
                    onValueChange={(value) => setFormData({ ...formData, serial_number: value })}
                    disabled={getExistingSerialNumbers(formData.category_id).length === 0}
                  >
                    <SelectTrigger data-testid="inward-serial-select">
                      <SelectValue placeholder={
                        getExistingSerialNumbers(formData.category_id).length === 0 
                          ? "No issued or scrapped boards available" 
                          : "Select board serial number to process"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      {getExistingSerialNumbers(formData.category_id).map((board) => (
                        <SelectItem key={board.id} value={board.serial_number}>
                          <div className="flex justify-between items-center w-full">
                            <span className="font-medium">{board.serial_number}</span>
                            <div className="flex space-x-2 ml-3">
                              <Badge className={`text-xs ${getStatusBadge(board.condition)}`}>
                                {board.condition}
                              </Badge>
                              <Badge className={`text-xs ${getLocationBadge(board.location)}`}>
                                {board.location}
                              </Badge>
                            </div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="condition">Condition</Label>
                  <Select 
                    value={formData.condition} 
                    onValueChange={(value) => setFormData({ ...formData, condition: value })}
                  >
                    <SelectTrigger data-testid="inward-condition-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {getAvailableConditions().map((condition) => (
                        <SelectItem key={condition} value={condition}>
                          {condition}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-gray-500 mt-1">Set condition based on board status after processing</p>
                </div>
                
                <div>
                  <Label htmlFor="qc_by">Processed By</Label>
                  <Input
                    id="qc_by"
                    data-testid="inward-qc-input"
                    value={formData.qc_by}
                    onChange={(e) => setFormData({ ...formData, qc_by: e.target.value })}
                    placeholder="Person processing the board"
                  />
                </div>
                
                <div>
                  <Label htmlFor="comments">Comments</Label>
                  <Textarea
                    id="comments"
                    data-testid="inward-comments-input"
                    value={formData.comments}
                    onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
                    placeholder="Processing notes, repair details, or return reason"
                    rows={3}
                  />
                </div>
                
                <div className="flex justify-end space-x-3 pt-4">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => setBoardDialog(false)}
                  >
                    Cancel
                  </Button>
                  <Button 
                    data-testid="save-inward-button"
                    type="submit" 
                    className="bg-orange-600 hover:bg-orange-700"
                  >
                    Process for Repairing/Return
                  </Button>
                </div>
              </form>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default Inward;