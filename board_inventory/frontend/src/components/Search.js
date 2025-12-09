import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from './Layout';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  Search as SearchIcon, 
  Filter, 
  Package, 
  MapPin, 
  User, 
  Calendar,
  FileText,
  Layers
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Search = ({ user, onLogout }) => {
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [conditionFilter, setConditionFilter] = useState('all');
  const [searchResults, setSearchResults] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const conditions = ['New', 'Repaired', 'Scrap'];

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      toast.error('Failed to fetch categories');
    }
  };

  const performSearch = async () => {
    setLoading(true);
    setHasSearched(true);
    
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('query', searchQuery);
      if (categoryFilter && categoryFilter !== 'all') params.append('category_id', categoryFilter);
      if (conditionFilter && conditionFilter !== 'all') params.append('condition', conditionFilter);
      
      const response = await axios.get(`${API}/search?${params.toString()}`);
      setSearchResults(response.data);
    } catch (error) {
      toast.error('Search failed');
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    performSearch();
  };

  useEffect(() => {
    fetchCategories();
    
    // Handle URL parameters for direct filtering (e.g., from dashboard)
    const urlParams = new URLSearchParams(location.search);
    const categoryParam = urlParams.get('category_id');
    const conditionParam = urlParams.get('condition');
    if (categoryParam) {
      setCategoryFilter(categoryParam);
    }
    if (conditionParam) {
      setConditionFilter(conditionParam);
    }
  }, [location.search]);

  const clearFilters = () => {
    setSearchQuery('');
    setCategoryFilter('all');
    setLocationFilter('all');
    setConditionFilter('all');
    setSearchResults([]);
    setHasSearched(false);
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

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-6 animate-fade-in">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Boards</h1>
          <p className="text-gray-600">Find specific electronics boards in your inventory</p>
        </div>

        {/* Search Form */}
        <Card className="border-0 shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <SearchIcon className="h-5 w-5 text-blue-600" />
              <span>Search Criteria</span>
            </CardTitle>
            <CardDescription>
              Use the filters below to search for specific boards in your inventory
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Search Query */}
            <div>
              <Label htmlFor="search-query">Search Text</Label>
              <div className="relative">
                <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  id="search-query"
                  data-testid="search-query-input"
                  placeholder="Search by serial number, issued to, project number, or comments..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>

            {/* Filters Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label>Category</Label>
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger data-testid="search-category-filter">
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
                <Label>Condition</Label>
                <Select value={conditionFilter} onValueChange={setConditionFilter}>
                  <SelectTrigger data-testid="search-condition-filter">
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
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 pt-4">
              <Button 
                data-testid="search-button"
                onClick={handleSearch} 
                className="bg-blue-600 hover:bg-blue-700"
                disabled={loading}
              >
                <SearchIcon className="h-4 w-4 mr-2" />
                {loading ? 'Searching...' : 'Search Boards'}
              </Button>
              <Button 
                variant="outline" 
                onClick={clearFilters}
                disabled={loading}
              >
                Clear All Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Search Results */}
        {hasSearched && (
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Search Results</span>
                <Badge variant="secondary" className="text-sm">
                  {searchResults.length} board{searchResults.length !== 1 ? 's' : ''} found
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-1/2 mb-1"></div>
                      <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                    </div>
                  ))}
                </div>
              ) : searchResults.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No boards found</h3>
                  <p className="text-gray-500">Try adjusting your search criteria or filters.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {searchResults.map((board) => (
                    <Card key={board.id} className="border border-gray-200 hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                          {/* Main Info */}
                          <div className="lg:col-span-2">
                            <div className="flex items-start justify-between mb-3">
                              <div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                                  {board.serial_number}
                                </h3>
                                <p className="text-sm text-gray-600 flex items-center">
                                  <Layers className="h-4 w-4 mr-1" />
                                  {getCategoryName(board.category_id)}
                                </p>
                              </div>
                              <div className="flex space-x-2">
                                <Badge className={`text-xs ${getLocationBadge(board.location)}`}>
                                  {board.location}
                                </Badge>
                                <Badge className={`text-xs ${getStatusBadge(board.condition)}`}>
                                  {board.condition}
                                </Badge>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                              {board.issued_to && (
                                <div className="flex items-center text-gray-600">
                                  <User className="h-4 w-4 mr-2" />
                                  <span className="font-medium">Issued to:</span>
                                  <span className="ml-1">{board.issued_to}</span>
                                </div>
                              )}
                              
                              {board.project_number && (
                                <div className="flex items-center text-gray-600">
                                  <FileText className="h-4 w-4 mr-2" />
                                  <span className="font-medium">Project:</span>
                                  <span className="ml-1">{board.project_number}</span>
                                </div>
                              )}
                              
                              {board.qc_by && (
                                <div className="flex items-center text-gray-600">
                                  <User className="h-4 w-4 mr-2" />
                                  <span className="font-medium">QC by:</span>
                                  <span className="ml-1">{board.qc_by}</span>
                                </div>
                              )}
                              
                              <div className="flex items-center text-gray-600">
                                <Calendar className="h-4 w-4 mr-2" />
                                <span className="font-medium">Added:</span>
                                <span className="ml-1">{new Date(board.created_at).toLocaleDateString()}</span>
                              </div>
                            </div>
                            
                            {board.comments && (
                              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                <p className="text-sm text-gray-700">
                                  <span className="font-medium">Comments:</span> {board.comments}
                                </p>
                              </div>
                            )}
                          </div>
                          
                          {/* Timeline */}
                          <div className="lg:border-l lg:pl-4">
                            <h4 className="text-sm font-medium text-gray-900 mb-3">Timeline</h4>
                            <div className="space-y-2 text-xs">
                              <div className="flex items-center text-gray-600">
                                <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                                <span>Added {new Date(board.inward_date_time).toLocaleString()}</span>
                              </div>
                              
                              {board.issued_date_time && (
                                <div className="flex items-center text-gray-600">
                                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                                  <span>Issued {new Date(board.issued_date_time).toLocaleString()}</span>
                                </div>
                              )}
                              
                              <div className="flex items-center text-gray-600">
                                <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
                                <span>Created by {board.created_by}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default Search;
