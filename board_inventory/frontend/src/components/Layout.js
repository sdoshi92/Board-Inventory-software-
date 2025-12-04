import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Button } from './ui/button';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import { 
  CircuitBoard, 
  Home, 
  Package, 
  Layers, 
  Search, 
  Menu, 
  LogOut, 
  User,
  FileText,
  Send,
  Users,
  BarChart3
} from 'lucide-react';

const Layout = ({ children, user, onLogout }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userPermissions, setUserPermissions] = useState([]);

  const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    const fetchUserPermissions = async () => {
      try {
        const response = await axios.get(`${API}/users/me/permissions`);
        setUserPermissions(response.data.permissions || []);
      } catch (error) {
        console.error('Failed to fetch user permissions:', error);
        setUserPermissions([]);
      }
    };

    if (user) {
      fetchUserPermissions();
    }
  }, [user]);

  const hasPermission = (permission) => {
    return user?.role === 'admin' || userPermissions.includes(permission);
  };

  // Define navigation with permission requirements
  const navigationItems = [
    { name: 'Dashboard', href: '/', icon: Home, permission: 'view_dashboard' },
    { name: 'Categories', href: '/categories', icon: Layers, permission: 'view_categories' },
    { name: 'Inward', href: '/inward', icon: Package, permission: 'view_inward' },
    { name: 'Issue Requests', href: '/issue-requests', icon: FileText, permission: 'view_issue_requests' },
    { name: 'Outward', href: '/outward', icon: Send, permission: 'view_outward' },
    { name: 'Search', href: '/search', icon: Search, permission: 'view_search' },
    { name: 'Reports', href: '/reports', icon: BarChart3, permission: 'view_reports' },
    { name: 'Users', href: '/users', icon: Users, permission: 'view_user_management' },
  ];

  // Filter navigation based on permissions
  const navigation = navigationItems.filter(item => hasPermission(item.permission));

  const isActive = (href) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  const Sidebar = ({ mobile = false }) => (
    <div className={`flex flex-col h-full ${
      mobile ? 'px-4 py-6' : 'px-6 py-8'
    }`}>
      {/* Logo */}
      <div className="flex items-center space-x-3 mb-8">
        <img 
          src="https://customer-assets.emergentagent.com/job_pcb-inventory-1/artifacts/dd8cln6f_Inter%20power%20logo%20_01.png"
          alt="Inter Power"
          className="h-10 w-10 rounded-lg object-contain bg-white p-1"
        />
        <div>
          <h1 className="text-lg font-bold text-gray-900">Inter Power</h1>
          <p className="text-xs text-gray-500">Board Inventory</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              to={item.href}
              data-testid={`nav-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
              className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
              onClick={() => mobile && setSidebarOpen(false)}
            >
              <Icon className="h-5 w-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User section */}
      <div className="border-t pt-4 mt-4">
        <div className="flex items-center space-x-3 px-3 py-2 mb-2">
          <div className="p-2 bg-gray-100 rounded-full">
            <User className="h-4 w-4 text-gray-600" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
          </div>
        </div>
        <Button
          data-testid="logout-button"
          variant="outline"
          size="sm"
          onClick={onLogout}
          className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sign Out
        </Button>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
        <div className="bg-white border-r border-gray-200 flex-1">
          <Sidebar />
        </div>
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="p-0 w-64">
          <Sidebar mobile />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="flex-1 lg:ml-64">
        {/* Mobile Header */}
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <Menu className="h-5 w-5" />
                  </Button>
                </SheetTrigger>
              </Sheet>
              <div className="flex items-center space-x-2">
                <img 
                  src="https://customer-assets.emergentagent.com/job_pcb-inventory-1/artifacts/dd8cln6f_Inter%20power%20logo%20_01.png"
                  alt="Inter Power"
                  className="h-6 w-6 rounded object-contain"
                />
                <span className="font-semibold text-gray-900">Inter Power</span>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          <div className="p-4 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
