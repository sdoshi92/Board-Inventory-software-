import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from './Layout';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Badge } from './ui/badge';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Layers, 
  Factory, 
  Clock, 
  Package,
  AlertCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Categories = ({ user, onLogout }) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    manufacturer: '',
    version: '',
    lead_time_days: '',
    minimum_stock_quantity: '',
    picture: null
  });

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      toast.error('Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      manufacturer: '',
      version: '',
      lead_time_days: '',
      minimum_stock_quantity: '',
      picture: null
    });
    setEditingCategory(null);
  };

  const handleCreate = () => {
    resetForm();
    setDialogOpen(true);
  };

  const handleEdit = (category) => {
    setFormData({
      name: category.name,
      description: category.description,
      manufacturer: category.manufacturer,
      version: category.version,
      lead_time_days: category.lead_time_days.toString(),
      minimum_stock_quantity: category.minimum_stock_quantity.toString(),
      picture: null
    });
    setEditingCategory(category);
    setDialogOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.description || !formData.manufacturer) {
      toast.error('Please fill in all required fields');
      return;
    }

    const submitData = {
      ...formData,
      lead_time_days: parseInt(formData.lead_time_days) || 0,
      minimum_stock_quantity: parseInt(formData.minimum_stock_quantity) || 0
    };

    try {
      if (editingCategory) {
        await axios.put(`${API}/categories/${editingCategory.id}`, submitData);
        toast.success('Category updated successfully');
      } else {
        await axios.post(`${API}/categories`, submitData);
        toast.success('Category created successfully');
      }
      setDialogOpen(false);
      resetForm();
      fetchCategories();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleDelete = async (categoryId, categoryName) => {
    if (!window.confirm(`Are you sure you want to delete "${categoryName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await axios.delete(`${API}/categories/${categoryId}`);
      toast.success('Category deleted successfully');
      fetchCategories();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete category');
    }
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Categories</h1>
            <p className="text-gray-600">Manage your electronics board categories</p>
          </div>
          <Button 
            data-testid="add-category-button"
            onClick={handleCreate} 
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Category
          </Button>
        </div>

        {/* Categories Grid */}
        {categories.length === 0 ? (
          <Card className="border-2 border-dashed border-gray-300">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Layers className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No categories yet</h3>
              <p className="text-gray-500 text-center mb-4">Get started by creating your first electronics board category.</p>
              <Button onClick={handleCreate} className="bg-blue-600 hover:bg-blue-700">
                <Plus className="h-4 w-4 mr-2" />
                Add Category
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category) => (
              <Card key={category.id} className="hover:shadow-lg transition-all duration-200 border-0 shadow-sm">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg font-semibold text-gray-900 mb-1">
                        {category.name}
                      </CardTitle>
                      <CardDescription className="text-sm text-gray-600">
                        {category.description}
                      </CardDescription>
                    </div>
                    <div className="flex space-x-1 ml-2">
                      <Button
                        data-testid={`edit-category-${category.id}`}
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(category)}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        data-testid={`delete-category-${category.id}`}
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(category.id, category.name)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <Factory className="h-4 w-4 mr-2" />
                      <span>{category.manufacturer}</span>
                      <Badge variant="secondary" className="ml-auto">
                        v{category.version}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="h-4 w-4 mr-2" />
                      <span>Lead time: {category.lead_time_days} days</span>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-600">
                      <Package className="h-4 w-4 mr-2" />
                      <span>Min stock: {category.minimum_stock_quantity}</span>
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
                {editingCategory ? 'Edit Category' : 'Add New Category'}
              </DialogTitle>
              <DialogDescription>
                {editingCategory 
                  ? 'Update the category information below.'
                  : 'Fill in the details to create a new electronics board category.'
                }
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">Category Name *</Label>
                <Input
                  id="name"
                  data-testid="category-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., EELM 4650"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  data-testid="category-description-input"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Brief description of the board category"
                  rows={3}
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="manufacturer">Manufacturer *</Label>
                  <Input
                    id="manufacturer"
                    data-testid="category-manufacturer-input"
                    value={formData.manufacturer}
                    onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                    placeholder="e.g., Texas Instruments"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="version">Version</Label>
                  <Input
                    id="version"
                    data-testid="category-version-input"
                    value={formData.version}
                    onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                    placeholder="e.g., 1.0"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="lead_time_days">Lead Time (days)</Label>
                  <Input
                    id="lead_time_days"
                    data-testid="category-leadtime-input"
                    type="number"
                    min="0"
                    value={formData.lead_time_days}
                    onChange={(e) => setFormData({ ...formData, lead_time_days: e.target.value })}
                    placeholder="30"
                  />
                </div>
                
                <div>
                  <Label htmlFor="minimum_stock_quantity">Min Stock Quantity</Label>
                  <Input
                    id="minimum_stock_quantity"
                    data-testid="category-minstock-input"
                    type="number"
                    min="0"
                    value={formData.minimum_stock_quantity}
                    onChange={(e) => setFormData({ ...formData, minimum_stock_quantity: e.target.value })}
                    placeholder="10"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="picture">Category Picture</Label>
                <Input
                  id="picture"
                  data-testid="category-picture-input"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setFormData({ ...formData, picture: e.target.files[0] })}
                  className="mt-1"
                />
                <p className="text-xs text-gray-500 mt-1">Upload an image for this category (optional)</p>
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
                  data-testid="save-category-button"
                  type="submit" 
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {editingCategory ? 'Update' : 'Create'} Category
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default Categories;
