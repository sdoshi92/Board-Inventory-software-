import React, { useState } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Loader2, CircuitBoard, Shield, Users, BarChart3 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AuthPage = ({ onAuthSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [registerData, setRegisterData] = useState({ 
    email: '', 
    first_name: '',
    last_name: '',
    designation: '',
    password: '', 
    confirmPassword: '' 
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginData.email || !loginData.password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email: loginData.email,
        password: loginData.password
      });
      onAuthSuccess(response.data);
    } catch (error) {
      if (error.response) {
        toast.error(error.response.data?.detail || 'Login failed');
      } else if (error.request) {
        toast.error('Network error: Cannot reach server');
      } else {
        toast.error('Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!registerData.email || !registerData.first_name || !registerData.last_name || 
        !registerData.designation || !registerData.password || !registerData.confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    if (registerData.password !== registerData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (registerData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email: registerData.email,
        first_name: registerData.first_name,
        last_name: registerData.last_name,
        designation: registerData.designation,
        password: registerData.password
      });
      onAuthSuccess(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 p-12 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 opacity-30" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
        
        <div className="relative z-10">
          <div className="flex items-center space-x-3 mb-8">
            <div className="p-3 bg-white/10 rounded-xl backdrop-blur-sm">
              <img 
                src="https://customer-assets.emergentagent.com/job_pcb-inventory-1/artifacts/dd8cln6f_Inter%20power%20logo%20_01.png"
                alt="Inter Power"
                className="h-8 w-8 object-contain"
              />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Inter Power</h1>
              <p className="text-blue-100">Inventory Management System</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-white/10 rounded-lg">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Secure & Reliable</h3>
                <p className="text-blue-100">Advanced security features with role-based access control to protect your inventory data.</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-white/10 rounded-lg">
                <Users className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Multi-User Support</h3>
                <p className="text-blue-100">Collaborative platform for teams to manage electronics board inventory efficiently.</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-white/10 rounded-lg">
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Real-time Analytics</h3>
                <p className="text-blue-100">Track inventory levels, generate reports, and get insights into your electronics board usage.</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="relative z-10 text-blue-100 text-sm">
          <p>© 2024 Inter Power Inventory System. Streamline your electronics management.</p>
        </div>
      </div>

      {/* Right side - Auth Form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="lg:hidden flex items-center justify-center space-x-2 mb-6">
              <img 
                src="https://customer-assets.emergentagent.com/job_pcb-inventory-1/artifacts/dd8cln6f_Inter%20power%20logo%20_01.png"
                alt="Inter Power"
                className="h-8 w-8 object-contain"
              />
              <h1 className="text-xl font-bold text-gray-900">Inter Power</h1>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome</h2>
            <p className="text-gray-600">Sign in to your account or create a new one</p>
          </div>

          <Card className="border-0 shadow-lg">
            <CardContent className="p-6">
              <Tabs defaultValue="login" className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-6">
                  <TabsTrigger data-testid="login-tab" value="login">Sign In</TabsTrigger>
                  <TabsTrigger data-testid="register-tab" value="register">Sign Up</TabsTrigger>
                </TabsList>
                
                <TabsContent value="login">
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                      <Label htmlFor="login-email">Email Address</Label>
                      <Input
                        id="login-email"
                        data-testid="login-email-input"
                        type="email"
                        placeholder="Enter your email"
                        value={loginData.email}
                        onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                        className="mt-1"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="login-password">Password</Label>
                      <Input
                        id="login-password"
                        data-testid="login-password-input"
                        type="password"
                        placeholder="Enter your password"
                        value={loginData.password}
                        onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                        className="mt-1"
                        required
                      />
                    </div>
                    <Button
                      data-testid="login-submit-button"
                      type="submit"
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Signing In...
                        </>
                      ) : (
                        'Sign In'
                      )}
                    </Button>
                  </form>
                </TabsContent>
                
                <TabsContent value="register">
                  <form onSubmit={handleRegister} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="register-first-name">First Name</Label>
                        <Input
                          id="register-first-name"
                          data-testid="register-first-name-input"
                          type="text"
                          placeholder="Enter your first name"
                          value={registerData.first_name}
                          onChange={(e) => setRegisterData({ ...registerData, first_name: e.target.value })}
                          className="mt-1"
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="register-last-name">Last Name</Label>
                        <Input
                          id="register-last-name"
                          data-testid="register-last-name-input"
                          type="text"
                          placeholder="Enter your last name"
                          value={registerData.last_name}
                          onChange={(e) => setRegisterData({ ...registerData, last_name: e.target.value })}
                          className="mt-1"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="register-designation">Designation</Label>
                      <Input
                        id="register-designation"
                        data-testid="register-designation-input"
                        type="text"
                        placeholder="Enter your job title/designation"
                        value={registerData.designation}
                        onChange={(e) => setRegisterData({ ...registerData, designation: e.target.value })}
                        className="mt-1"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="register-email">Email Address</Label>
                      <Input
                        id="register-email"
                        data-testid="register-email-input"
                        type="email"
                        placeholder="Enter your email"
                        value={registerData.email}
                        onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                        className="mt-1"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="register-password">Password</Label>
                        <Input
                          id="register-password"
                          data-testid="register-password-input"
                          type="password"
                          placeholder="Create a password (min 6 characters)"
                          value={registerData.password}
                          onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                          className="mt-1"
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="register-confirm-password">Confirm Password</Label>
                        <Input
                          id="register-confirm-password"
                          data-testid="register-confirm-password-input"
                          type="password"
                          placeholder="Confirm your password"
                          value={registerData.confirmPassword}
                          onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                          className="mt-1"
                          required
                        />
                      </div>
                    </div>
                    <Button
                      data-testid="register-submit-button"
                      type="submit"
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Creating Account...
                        </>
                      ) : (
                        'Create Account'
                      )}
                    </Button>
                  </form>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
