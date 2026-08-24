import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function Analytics() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const response = await api.getDashboard();
      setDashboardData(response);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    }
    setLoading(false);
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;
  if (!dashboardData) return <div style={{ padding: '20px' }}>No data</div>;

  const statusData = Object.entries(dashboardData.status || {}).map(([name, count]) => ({
    name,
    value: count
  }));

  const categoryData = Object.entries(dashboardData.categories || {}).map(([name, count]) => ({
    name,
    value: count
  }));

  return (
    <div style={{ padding: '30px' }}>
      <h2>Analytics Dashboard</h2>

      {/* Status Distribution */}
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginTop: '20px',
        marginBottom: '20px'
      }}>
        <h3>Ticket Status Distribution</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', marginTop: '15px' }}>
          {statusData.map((stat, idx) => (
            <div
              key={idx}
              style={{
                padding: '15px',
                background: '#f5f5f5',
                borderRadius: '4px',
                textAlign: 'center'
              }}
            >
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>{stat.name}</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0066cc' }}>{stat.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Category Distribution */}
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h3>Categories</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '15px' }}>
          {categoryData.map((cat, idx) => (
            <div
              key={idx}
              style={{
                padding: '15px',
                background: '#f5f5f5',
                borderRadius: '4px',
                textAlign: 'center'
              }}
            >
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>{cat.name}</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0066cc' }}>{cat.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px'
      }}>
        <h3>Key Metrics</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '20px', marginTop: '15px' }}>
          <div>
            <span style={{ color: '#666' }}>Automation Rate: </span>
            <strong>{dashboardData.metrics?.automation_rate.toFixed(1)}%</strong>
          </div>
          <div>
            <span style={{ color: '#666' }}>Avg Resolution Time: </span>
            <strong>{dashboardData.metrics?.avg_resolution_time.toFixed(1)} minutes</strong>
          </div>
          <div>
            <span style={{ color: '#666' }}>Avg Sentiment: </span>
            <strong>{(dashboardData.metrics?.avg_sentiment || 0).toFixed(2)}</strong>
          </div>
          <div>
            <span style={{ color: '#666' }}>Total Tickets: </span>
            <strong>{dashboardData.metrics?.total_tickets}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}