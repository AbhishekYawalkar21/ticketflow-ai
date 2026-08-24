import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import TicketList from './components/TicketList';
import Analytics from './components/Analytics';
import { api } from './services/api';

export default function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const response = await api.getTickets();
      setTickets(response);
    } catch (error) {
      console.error('Failed to fetch tickets:', error);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar */}
      <div style={{
        width: '250px',
        background: '#1a1a1a',
        color: 'white',
        padding: '20px',
      }}>
        <h1 style={{ fontSize: '20px', marginBottom: '30px' }}>🎫 TicketFlow AI</h1>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {['dashboard', 'tickets', 'analytics'].map(view => (
            <button
              key={view}
              onClick={() => setCurrentView(view)}
              style={{
                padding: '10px 15px',
                background: currentView === view ? '#0066cc' : 'transparent',
                color: 'white',
                border: 'none',
                cursor: 'pointer',
                borderRadius: '5px',
                textAlign: 'left',
                fontSize: '14px'
              }}
            >
              {view.charAt(0).toUpperCase() + view.slice(1)}
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {currentView === 'dashboard' && <Dashboard tickets={tickets} />}
        {currentView === 'tickets' && <TicketList tickets={tickets} onRefresh={fetchTickets} loading={loading} />}
        {currentView === 'analytics' && <Analytics />}
      </div>
    </div>
  );
}