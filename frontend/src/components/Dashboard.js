import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function Dashboard({ tickets }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const response = await api.getMetrics();
      setMetrics(response);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
    setLoading(false);
  };

  if (loading) return <div style={{ padding: '20px' }}>Loading...</div>;

  const stats = [
    { label: 'Total Tickets', value: metrics?.total_tickets || 0, color: '#3498db' },
    { label: 'Automated', value: metrics?.automated_count || 0, color: '#2ecc71' },
    { label: 'Automation Rate', value: `${metrics?.automation_rate.toFixed(1) || 0}%`, color: '#f39c12' },
    { label: 'Avg Resolution Time', value: `${metrics?.avg_resolution_time.toFixed(1) || 0}m`, color: '#e74c3c' },
  ];

  return (
    <div style={{ padding: '30px' }}>
      <h2>Dashboard</h2>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginTop: '20px'
      }}>
        {stats.map((stat, idx) => (
          <div
            key={idx}
            style={{
              background: 'white',
              padding: '20px',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              borderLeft: `4px solid ${stat.color}`
            }}
          >
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
              {stat.label}
            </div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: stat.color }}>
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      {/* Recent Tickets */}
      <div style={{ marginTop: '40px', background: 'white', padding: '20px', borderRadius: '8px' }}>
        <h3>Recent Tickets</h3>
        <table style={{ width: '100%', marginTop: '15px', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #eee' }}>
              <th style={{ textAlign: 'left', padding: '10px' }}>Subject</th>
              <th style={{ textAlign: 'left', padding: '10px' }}>Status</th>
              <th style={{ textAlign: 'left', padding: '10px' }}>Priority</th>
              <th style={{ textAlign: 'left', padding: '10px' }}>Category</th>
              <th style={{ textAlign: 'left', padding: '10px' }}>Automation</th>
            </tr>
          </thead>
          <tbody>
            {tickets.slice(0, 5).map(ticket => (
              <tr key={ticket.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '10px' }}>{ticket.subject.substring(0, 40)}</td>
                <td style={{ padding: '10px' }}>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    background: ticket.status === 'open' ? '#e8f4f8' : '#e8f8f0',
                    color: ticket.status === 'open' ? '#0066cc' : '#009966'
                  }}>
                    {ticket.status}
                  </span>
                </td>
                <td style={{ padding: '10px' }}>{ticket.priority}</td>
                <td style={{ padding: '10px' }}>{ticket.category || '-'}</td>
                <td style={{ padding: '10px' }}>{ticket.automation_score.toFixed(0)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}