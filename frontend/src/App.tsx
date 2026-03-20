import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import { useAuthStore } from './store/useAuthStore';
import 'antd/dist/reset.css';

// A wrapper for routes that require authentication
const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const { accessToken } = useAuthStore();
  
  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
