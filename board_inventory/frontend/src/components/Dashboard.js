import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import Layout from './Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Clock,
  Wrench,
  ExternalLink,
  AlertCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [pendingRequests, setPendingRequests] = useState(0);
  const [repairingBoards, setRepairingBoards] = useState(0);
  const [lowStockCategories, setLowStockCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const handlePendingRequestsClick = () => {
    navigate('/issue-requests');
  };

  const handleRepairingBoardsClick = () => {
    // Navigate to a filtered view - for now go to search page with filter
    navigate('/search?location=Repairing');
  };

  const fetchDashboardStats = async () => {
    try {
      const [requestsRes, bulkRequestsRes, boardsRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/issue-requests`),
        axios.get(`${API}/bulk-issue-requests`),
        axios.get(`${API}/boards`),
        axios.get(`${API}/categories`)
      ]);
      
      // Count pending requests (both regular and bulk)
      const pendingRegular = requestsRes.data.filter(req => req.status === 'pending').length;
      const pendingBulk = bulkRequestsRes.data.filter(req => req.status === 'pending').length;
      setPendingRequests(pendingRegular + pendingBulk);
      
      // Count boards in repairing
      const repairingCount = boardsRes.data.filter(board => board.location === 'Repairing').length;
      setRepairingBoards(repairingCount);
      
      // Calculate low stock categories
      const categories = categoriesRes.data;
      const boards = boardsRes.data;
      const lowStock = categories.filter(category => {
        const currentStock = boards.filter(board => 
          board.category_id === category.id && 
          board.location === 'In stock' && 
          (board.condition === 'New' || board.condition === 'Repaired')
        ).length;
        return currentStock < category.minimum_stock_quantity;
      }).map(category => {
        const currentStock = boards.filter(board => 
          board.category_id === category.id && 
          board.location === 'In stock' && 
          (board.condition === 'New' || board.condition === 'Repaired')
        ).length;
        return {
          ...category,
          current_stock: currentStock
        };
      });
      setLowStockCategories(lowStock);
      
    } catch (error) {
      toast.error('Failed to fetch dashboard statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout user={user} onLogout={onLogout}>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardContent className="p-6">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-3"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/3"></div>
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
      <div className="space-y-8 animate-fade-in">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.first_name} {user?.last_name}. Here's your inventory management center.</p>
        </div>

        {/* Enhanced Dashboard Widgets */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Pending Issue Requests */}
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={handlePendingRequestsClick}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-yellow-100 rounded-full">
                    <Clock className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Pending Approvals</h3>
                    <p className="text-sm text-gray-600">Issue requests awaiting approval</p>
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 text-gray-400" />
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-3xl font-bold text-yellow-600">{pendingRequests}</span>
                <Badge className={`${pendingRequests > 0 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                  {pendingRequests > 0 ? 'Action Required' : 'All Clear'}
                </Badge>
              </div>
              
              <p className="text-xs text-gray-500 mt-3">
                Click to review and approve pending requests
              </p>
            </CardContent>
          </Card>

          {/* Boards in Repairing */}
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow cursor-pointer" onClick={handleRepairingBoardsClick}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-orange-100 rounded-full">
                    <Wrench className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Boards in Repair</h3>
                    <p className="text-sm text-gray-600">Currently being repaired</p>
                  </div>
                </div>
                <ExternalLink className="h-4 w-4 text-gray-400" />
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-3xl font-bold text-orange-600">{repairingBoards}</span>
                <Badge className="bg-orange-100 text-orange-800">
                  In Progress
                </Badge>
              </div>
              
              <p className="text-xs text-gray-500 mt-3">
                Click to view all boards currently under repair
              </p>
            </CardContent>
          </Card>

          {/* Low Stock Categories */}
          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-red-100 rounded-full">
                    <AlertCircle className="h-6 w-6 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">Low Stock Alert</h3>
                    <p className="text-sm text-gray-600">Categories below minimum stock</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-between mb-3">
                <span className="text-3xl font-bold text-red-600">{lowStockCategories.length}</span>
                <Badge className={`${lowStockCategories.length > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                  {lowStockCategories.length > 0 ? 'Needs Attention' : 'Adequate Stock'}
                </Badge>
              </div>
              
              {lowStockCategories.length > 0 ? (
                <div className="max-h-64 overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100">
                  {lowStockCategories.slice(0, 10).map((category) => (
                    <div key={category.id} className="p-2 bg-red-50 rounded border border-red-200">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-red-900">{category.name}</span>
                        <div className="text-xs text-red-700">
                          <span className="font-medium">{category.current_stock}</span>
                          <span className="mx-1">/</span>
                          <span>{category.minimum_stock_quantity}</span>
                        </div>
                      </div>
                      <div className="text-xs text-red-600 mt-1">
                        Need {category.minimum_stock_quantity - category.current_stock} more
                      </div>
                    </div>
                  ))}
                  {lowStockCategories.length > 10 && (
                    <div className="p-2 bg-gray-50 rounded border border-gray-200 text-center">
                      <p className="text-xs text-gray-600">
                        +{lowStockCategories.length - 10} more categories with low stock
                      </p>
                      <p className="text-xs text-blue-600 mt-1 cursor-pointer hover:underline" onClick={() => navigate('/reports')}>
                        View full report →
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-xs text-green-600 mt-3">
                  All categories have adequate stock levels
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
