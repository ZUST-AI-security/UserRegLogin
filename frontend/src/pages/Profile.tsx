import React, { useEffect, useState } from 'react';
import { Card, Button, Typography, message, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios_client';
import { useAuthStore } from '../store/useAuthStore';

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user, setUser, logout } = useAuthStore();
  const [lastFetch, setLastFetch] = useState<string>('');

  const fetchUser = async (manual = false) => {
    try {
      setLoading(true);
      const response = await api.get('/users/me');
      setUser(response.data);
      setLastFetch(new Date().toLocaleTimeString());
      if (manual) message.success('User data refreshed!');
    } catch (error) {
      message.error('Failed to fetch user data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const handleLogout = () => {
    logout();
    message.success('Logged out successfully');
    navigate('/login');
  };

  if (loading && !user) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><Spin size="large" /></div>;
  }

  return (
    <div style={{ padding: '50px', display: 'flex', justifyContent: 'center' }}>
      <Card title="User Profile" style={{ width: 500 }}>
        {user ? (
          <div>
            <Title level={4}>Welcome, {user.username}!</Title>
            <p><Text strong>User ID: </Text> {user.id}</p>
            <p><Text strong>Username: </Text> {user.username}</p>
            {lastFetch && <p><Text type="secondary">Last updated: {lastFetch}</Text></p>}
            
            <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
              <Button type="default" onClick={() => fetchUser(true)} loading={loading}>
                Manual Fetch User Info
              </Button>
              <Button type="primary" danger onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center' }}>
             <Text>No user data available.</Text>
             <br />
             <Button type="primary" onClick={() => fetchUser(true)} style={{ marginTop: '10px' }}>
               Try Fetching
             </Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Profile;
