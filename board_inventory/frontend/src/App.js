import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import AuthPage from './components/AuthPage';
import Dashboard from './components/Dashboard';
import Categories from './components/Categories';
import Boards from './components/Boards';
import Inward from './components/Inward';
import Search from './components/Search';
import IssueRequests from './components/IssueRequests';
import Outward from './components/Outward';
import Reports from './components/Reports';
import UserManagement from './components/UserManagement';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Axios interceptor for auth
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
      // Verify token is still valid
      axios.get(`${API}/auth/me`)
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleAuthSuccess = (authData) => {
    localStorage.setItem('token', authData.access_token);
    localStorage.setItem('user', JSON.stringify(authData.user));
    setUser(authData.user);
    toast.success('Welcome to Electronics Board Inventory!');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Logged out successfully');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Router>
        <Routes>
          <Route 
            path="/auth" 
            element={
              user ? <Navigate to="/" replace /> : 
              <AuthPage onAuthSuccess={handleAuthSuccess} />
            } 
          />
          <Route 
            path="/" 
            element={
              user ? 
              <Dashboard user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/categories" 
            element={
              user ? 
              <Categories user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/inward" 
            element={
              user ? 
              <Inward user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/boards" 
            element={
              user ? 
              <Boards user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/search" 
            element={
              user ? 
              <Search user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/issue-requests" 
            element={
              user ? 
              <IssueRequests user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/outward" 
            element={
              user ? 
              <Outward user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/reports" 
            element={
              user ? 
              <Reports user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
          <Route 
            path="/users" 
            element={
              user ? 
              <UserManagement user={user} onLogout={handleLogout} /> : 
              <Navigate to="/auth" replace />
            } 
          />
        </Routes>
      </Router>
      <Toaster 
        position="top-right"
        expand={false}
        richColors
        closeButton
      />
    </div>
  );
}

export default App;
