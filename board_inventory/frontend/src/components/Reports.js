import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from './Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Badge } from "./ui/badge";
import { toast } from 'sonner';
import { 
  FileDown, 
  TrendingDown, 
  Wrench, 
  History, 
  Database,
  Search,
  AlertTriangle,
  Eye,
  Download
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Reports = ({ user, onLogout }) => {
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [lowStockReport, setLowStockReport] = useState([]);
  const [underRepairReport, setUnderRepairReport] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [serialNumber, setSerialNumber] = useState('');
  const [serialHistory, setSerialHistory] = useState(null);
  const [serialHistoryCategory, setSerialHistoryCategory] = useState('');
  const [availableSerials, setAvailableSerials] = useState([]);
  const [categoryData, setCategoryData] = useState(null);
  const [categoryLoading, setCategoryLoading] = useState(false);

  const testDownload = () => {
    // Create a simple test file to verify download mechanism works
    const testContent = 'Test file content';
    const blob = new Blob([testContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'test-download.txt';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    toast.success('Test download triggered');
  };

  const manualDownloadLink = (endpoint, filename) => {
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error('No authentication token found');
      return '#';
    }
    return `${API}/reports/export/${endpoint}?token=${encodeURIComponent(token)}`;
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      toast.error('Failed to fetch categories');
    }
  };

  const fetchLowStockReport = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/reports/low-stock`);
      setLowStockReport(response.data);
      if (response.data.length === 0) {
        toast.success('No categories are low on stock!');
      }
    } catch (error) {
      toast.error('Failed to fetch low stock report');
    } finally {
      setLoading(false);
    }
  };

  const fetchUnderRepairReport = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/reports/under-repair`);
      setUnderRepairReport(response.data);
      if (response.data.length === 0) {
        toast.success('No boards are currently under repair!');
      }
    } catch (error) {
      toast.error('Failed to fetch under repair report');
    } finally {
      setLoading(false);
    }
  };

  const fetchSerialsByCategory = async (categoryId) => {
    if (!categoryId) {
      setAvailableSerials([]);
      return;
    }
    
    try {
      const response = await axios.get(`${API}/reports/serial-numbers/${categoryId}`);
      setAvailableSerials(response.data.serial_numbers);
      setSerialNumber(''); // Reset selected serial when category changes
    } catch (error) {
      toast.error('Failed to fetch serial numbers');
      setAvailableSerials([]);
    }
  };

  const fetchSerialHistory = async () => {
    if (!serialNumber.trim()) {
      toast.error('Please select a serial number');
      return;
    }
    
    setLoading(true);
    try {
      const response = await axios.get(`${API}/reports/serial-history/${serialNumber.trim()}`);
      setSerialHistory(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        toast.error('Serial number not found');
      } else {
        toast.error('Failed to fetch serial history');
      }
      setSerialHistory(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategoryData = async (categoryId) => {
    if (!categoryId) {
      setCategoryData(null);
      return;
    }
    
    setCategoryLoading(true);
    try {
      const response = await axios.get(`${API}/reports/category-export/${categoryId}`);
      setCategoryData(response.data);
    } catch (error) {
      toast.error('Failed to fetch category data');
      setCategoryData(null);
    } finally {
      setCategoryLoading(false);
    }
  };

  const downloadExcel = async (endpoint, filename) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      // Method 1: Try direct browser download using window.location
      window.location.href = `${API}/reports/export/${endpoint}?token=${encodeURIComponent(token)}`;
      
      toast.success('Download started - check your browser downloads');
      
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Download failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout user={user} onLogout={onLogout}>
      <div className="space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports</h1>
          <p className="text-gray-600">Generate and export comprehensive inventory reports</p>
        </div>

      <Tabs defaultValue="low-stock" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="low-stock" className="flex items-center gap-2">
            <TrendingDown className="w-4 h-4" />
            Low Stock
          </TabsTrigger>
          <TabsTrigger value="under-repair" className="flex items-center gap-2">
            <Wrench className="w-4 h-4" />
            Under Repair
          </TabsTrigger>
          <TabsTrigger value="serial-history" className="flex items-center gap-2">
            <History className="w-4 h-4" />
            Serial History
          </TabsTrigger>
          <TabsTrigger value="category-export" className="flex items-center gap-2">
            <Database className="w-4 h-4" />
            Category Export
          </TabsTrigger>
        </TabsList>

        {/* Low Stock Report */}
        <TabsContent value="low-stock">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-red-500" />
                Low Stock Report
              </CardTitle>
              <CardDescription>
                Categories with stock below minimum threshold requiring refill
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 mb-6 flex-wrap">
                <Button 
                  onClick={fetchLowStockReport}
                  disabled={loading}
                  className="flex items-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  {loading ? 'Loading...' : 'Generate Report'}
                </Button>
                <Button 
                  onClick={() => downloadExcel('low-stock', 'low_stock_report.xlsx')}
                  disabled={loading}
                  className="flex items-center gap-2"
                >
                  <FileDown className="w-4 h-4" />
                  Download Excel
                </Button>
                <div className="text-sm text-gray-600 bg-green-50 border border-green-200 p-3 rounded-lg mt-2 w-full">
                  <strong>📥 Guaranteed Download Method:</strong><br/>
                  <a 
                    href={`${API}/reports/export/low-stock?token=${encodeURIComponent(localStorage.getItem('token') || '')}`}
                    className="text-green-700 hover:text-green-900 underline font-medium text-base"
                    target="_blank"
                  >
                    Right-click here → Save Link As → low_stock_report.xlsx
                  </a>
                  <br/>
                  <span className="text-xs text-gray-500 mt-1 block">This method works in all browsers and downloads directly to your computer</span>
                </div>
              </div>

              {lowStockReport.length > 0 && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {lowStockReport.map((item, index) => (
                      <Card key={index} className="border-red-200">
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-4 h-4 text-red-500" />
                            <h3 className="font-semibold text-sm">{item.category_name}</h3>
                          </div>
                          <div className="space-y-1 text-xs text-gray-600">
                            <div className="flex justify-between">
                              <span>Current Stock:</span>
                              <Badge variant="destructive">{item.current_stock}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span>Minimum Required:</span>
                              <span>{item.minimum_stock_quantity}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Need to Refill:</span>
                              <Badge variant="secondary">{item.required_to_refill}</Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Under Repair Report */}
        <TabsContent value="under-repair">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wrench className="w-5 h-5 text-orange-500" />
                Under Repair Report
              </CardTitle>
              <CardDescription>
                All boards currently under repair or in repairing location
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4 mb-6">
                <Button 
                  onClick={fetchUnderRepairReport}
                  disabled={loading}
                  className="flex items-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  {loading ? 'Loading...' : 'Generate Report'}
                </Button>
                <Button 
                  onClick={() => downloadExcel('under-repair', 'under_repair_report.xlsx')}
                  disabled={loading}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <FileDown className="w-4 h-4" />
                  Export to Excel
                </Button>
                <div className="text-sm text-gray-600 bg-green-50 border border-green-200 p-2 rounded mt-2">
                  <strong>📥 Guaranteed Download:</strong> <a 
                    href={`${API}/reports/export/under-repair?token=${encodeURIComponent(localStorage.getItem('token') || '')}`}
                    className="text-green-700 hover:text-green-900 underline font-medium"
                    target="_blank"
                  >
                    Right-click → Save As
                  </a>
                </div>
              </div>

              {underRepairReport.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-300">
                    <thead>
                      <tr className="bg-gray-50">
                        <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Serial Number</th>
                        <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Category</th>
                        <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Manufacturer</th>
                        <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Condition</th>
                        <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Inward Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {underRepairReport.map((board, index) => (
                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                          <td className="border border-gray-300 px-3 py-2 text-sm font-medium">{board.serial_number}</td>
                          <td className="border border-gray-300 px-3 py-2 text-sm">{board.category_name}</td>
                          <td className="border border-gray-300 px-3 py-2 text-sm">{board.manufacturer}</td>
                          <td className="border border-gray-300 px-3 py-2 text-sm">
                            <Badge variant="outline" className="bg-orange-100 text-orange-800">{board.condition}</Badge>
                          </td>
                          <td className="border border-gray-300 px-3 py-2 text-sm">{board.inward_date}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Serial History Report */}
        <TabsContent value="serial-history">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5 text-blue-500" />
                Serial Number History
              </CardTitle>
              <CardDescription>
                Complete history and details for any specific serial number
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 mb-6">
                {/* Category Selection */}
                <div className="flex gap-4">
                  <Select 
                    value={serialHistoryCategory} 
                    onValueChange={(value) => {
                      setSerialHistoryCategory(value);
                      fetchSerialsByCategory(value);
                      setSerialHistory(null); // Clear previous history
                    }}
                  >
                    <SelectTrigger className="max-w-md">
                      <SelectValue placeholder="First, select category..." />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name} - {category.manufacturer}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Serial Number Selection */}
                {serialHistoryCategory && (
                  <div className="flex gap-4">
                    <Select 
                      value={serialNumber} 
                      onValueChange={setSerialNumber}
                      disabled={availableSerials.length === 0}
                    >
                      <SelectTrigger className="max-w-md">
                        <SelectValue placeholder={availableSerials.length === 0 ? "No serials available" : "Select serial number..."} />
                      </SelectTrigger>
                      <SelectContent>
                        {availableSerials.map((serial) => (
                          <SelectItem key={serial.serial_number} value={serial.serial_number}>
                            {serial.serial_number} ({serial.status})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button 
                      onClick={fetchSerialHistory}
                      disabled={loading || !serialNumber}
                      className="flex items-center gap-2"
                    >
                      <Search className="w-4 h-4" />
                      {loading ? 'Loading...' : 'Get History'}
                    </Button>
                    {serialHistory && (
                      <Button 
                        onClick={() => downloadExcel(`serial-history/${serialNumber}`, `${serialNumber}_history.xlsx`)}
                        disabled={loading}
                        variant="outline"
                        className="flex items-center gap-2"
                      >
                        <FileDown className="w-4 h-4" />
                        Export to Excel
                      </Button>
                    )}
                  </div>
                )}

                {serialHistoryCategory && availableSerials.length === 0 && (
                  <div className="text-sm text-gray-600 bg-yellow-50 p-3 rounded-lg">
                    No serial numbers found for this category.
                  </div>
                )}
              </div>

              {serialHistory && (
                <div className="space-y-6">
                  {/* Current Status */}
                  <Card className="border-blue-200">
                    <CardHeader>
                      <CardTitle className="text-lg">Current Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-semibold text-sm mb-2">Board Details</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Serial Number:</span>
                              <span className="font-medium">{serialHistory.serial_number}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Category:</span>
                              <span>{serialHistory.category_name}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Manufacturer:</span>
                              <span>{serialHistory.manufacturer}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Version:</span>
                              <span>{serialHistory.version}</span>
                            </div>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm mb-2">Current State</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Condition:</span>
                              <Badge variant="secondary">{serialHistory.current_status.condition}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Issued To:</span>
                              <span>{serialHistory.current_status.issued_to || 'N/A'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Project:</span>
                              <span>{serialHistory.current_status.project_number || 'N/A'}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      {serialHistory.current_status.comments && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                          <h4 className="font-semibold text-sm mb-1">Comments</h4>
                          <p className="text-sm text-gray-700">{serialHistory.current_status.comments}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Issue History */}
                  {serialHistory.issue_history && serialHistory.issue_history.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Issue Request History</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {serialHistory.issue_history.map((request, index) => (
                            <div key={index} className="p-3 border rounded-lg">
                              <div className="flex justify-between items-start mb-2">
                                <span className="font-medium text-sm">Request ID: {request.id}</span>
                                <Badge variant={request.status === 'approved' ? 'default' : request.status === 'pending' ? 'secondary' : 'destructive'}>
                                  {request.status}
                                </Badge>
                              </div>
                              <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                                <div>Requested by: {request.requested_by}</div>
                                <div>Issued to: {request.issued_to}</div>
                                <div>Project: {request.project_number || 'N/A'}</div>
                                <div>Date: {new Date(request.created_date_time).toLocaleDateString()}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Category Export */}
        <TabsContent value="category-export">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5 text-green-500" />
                Category Database Export
              </CardTitle>
              <CardDescription>
                Export complete database for a specific category including all boards and history
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 mb-6">
                <div className="flex gap-4">
                  <Select 
                    value={selectedCategory} 
                    onValueChange={(value) => {
                      setSelectedCategory(value);
                      fetchCategoryData(value);
                    }}
                  >
                    <SelectTrigger className="max-w-md">
                      <SelectValue placeholder="Select category to preview and export..." />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name} - {category.manufacturer}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button 
                    onClick={() => downloadExcel(`category/${selectedCategory}`, `category_export.xlsx`)}
                    disabled={loading || categoryLoading || !selectedCategory}
                    className="flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    {loading || categoryLoading ? 'Loading...' : 'Export to Excel'}
                  </Button>
                </div>

                {/* Add backup download link */}
                {selectedCategory && (
                  <div className="text-sm text-gray-600 bg-green-50 border border-green-200 p-2 rounded">
                    <strong>📥 Alternative:</strong> <a 
                      href={`${API}/reports/export/category/${selectedCategory}?token=${encodeURIComponent(localStorage.getItem('token') || '')}`}
                      className="text-green-700 hover:text-green-900 underline font-medium"
                      target="_blank"
                    >
                      Right-click → Save As
                    </a>
                  </div>
                )}
              </div>

              {/* Category Data Preview */}
              {categoryLoading && (
                <div className="flex items-center justify-center py-8">
                  <div className="text-gray-500">Loading category data...</div>
                </div>
              )}

              {categoryData && (
                <div className="space-y-6">
                  {/* Category Information */}
                  <Card className="border-green-200">
                    <CardHeader>
                      <CardTitle className="text-lg text-green-800">Category Overview</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-semibold text-sm mb-2">Category Details</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Name:</span>
                              <span className="font-medium">{categoryData.category.name}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Manufacturer:</span>
                              <span>{categoryData.category.manufacturer}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Version:</span>
                              <span>{categoryData.category.version}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Min Stock:</span>
                              <span>{categoryData.category.minimum_stock_quantity}</span>
                            </div>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-semibold text-sm mb-2">Statistics</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Total Boards:</span>
                              <Badge variant="secondary">{categoryData.statistics.total_boards}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">In Stock:</span>
                              <Badge variant="default">{categoryData.statistics.in_stock}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Issued:</span>
                              <Badge variant="outline">{categoryData.statistics.issued}</Badge>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Repairing:</span>
                              <Badge variant="destructive">{categoryData.statistics.repairing}</Badge>
                            </div>
                          </div>
                        </div>
                      </div>
                      {categoryData.category.description && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                          <h4 className="font-semibold text-sm mb-1">Description</h4>
                          <p className="text-sm text-gray-700">{categoryData.category.description}</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Boards Summary */}
                  {categoryData.boards && categoryData.boards.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Boards Summary</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-sm text-gray-600 mb-3">
                          Showing first 10 of {categoryData.boards.length} total boards
                        </div>
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse border border-gray-300">
                            <thead>
                              <tr className="bg-gray-50">
                                <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Serial Number</th>
                                <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Condition</th>
                                <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Location</th>
                                <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Issued To</th>
                                <th className="border border-gray-300 px-3 py-2 text-left text-xs font-semibold">Project</th>
                              </tr>
                            </thead>
                            <tbody>
                              {categoryData.boards.slice(0, 10).map((board, index) => (
                                <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                  <td className="border border-gray-300 px-3 py-2 text-sm font-medium">{board.serial_number}</td>
                                  <td className="border border-gray-300 px-3 py-2 text-sm">
                                    <Badge variant={board.condition === 'New' ? 'default' : board.condition === 'Repaired' ? 'secondary' : 'destructive'}>
                                      {board.condition}
                                    </Badge>
                                  </td>
                                  <td className="border border-gray-300 px-3 py-2 text-sm">{board.location}</td>
                                  <td className="border border-gray-300 px-3 py-2 text-sm">{board.issued_to || '-'}</td>
                                  <td className="border border-gray-300 px-3 py-2 text-sm">{board.project_number || '-'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        {categoryData.boards.length > 10 && (
                          <div className="text-center text-sm text-gray-600 mt-3">
                            ... and {categoryData.boards.length - 10} more boards (export Excel for complete list)
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )}

                  {/* Requests Summary */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Request History Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="bg-blue-50 p-3 rounded">
                          <div className="font-semibold text-blue-800">Individual Requests</div>
                          <div className="text-blue-700">{categoryData.statistics.total_requests} total</div>
                        </div>
                        <div className="bg-purple-50 p-3 rounded">
                          <div className="font-semibold text-purple-800">Bulk Requests</div>
                          <div className="text-purple-700">{categoryData.statistics.total_bulk_requests} total</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {!selectedCategory && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-sm mb-2 text-blue-800">Excel Export Includes:</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Complete category information and settings</li>
                    <li>• All boards with serial numbers, conditions, and locations</li>
                    <li>• Full issue request history for the category</li>
                    <li>• Board assignment and project history</li>
                    <li>• Comments and maintenance records</li>
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      </div>
    </Layout>
  );
};

export default Reports;