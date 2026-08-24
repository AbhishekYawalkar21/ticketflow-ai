import React, { useState } from 'react';
import { api } from '../services/api';

export default function TicketList({ tickets, onRefresh, loading }) {
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [newTicketData, setNewTicketData] = useState({ subject: '', content: '' });

  const handleCreateTicket = async () => {
    if (!newTicketData.subject || !newTicketData.content) {
      alert('Please fill in all fields');
      return;
    }

    try {
      await api.createTicket({
        subject: newTicketData.subject,
        content: newTicketData.content,
        source: 'api'
      });
      setNewTicketData({ subject: '', content: '' });
      onRefresh();
    } catch (error) {
      alert('Failed to create ticket: ' + error.message);
    }
  };

  const handleClassifyTicket = async (ticketId) => {
    try {
      await api.classifyTicket(ticketId);
      alert('Classification started!');
      setTimeout(onRefresh, 2000);
    } catch (error) {
      alert('Failed to classify: ' + error.message);
    }
  };

  return (
    <div style={{ padding: '30px' }}>
      <h2>Support Tickets</h2>

      {/* Create New Ticket */}
      <div style={{
        background: 'white',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '30px',
        marginTop: '20px'
      }}>
        <h3>Create New Ticket</h3>
        <input
          type="text"
          placeholder="Subject"
          value={newTicketData.subject}
          onChange={(e) => setNewTicketData({ ...newTicketData, subject: e.target.value })}
          style={{
            width: '100%',
            padding: '10px',
            marginTop: '10px',
            marginBottom: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
        <textarea
          placeholder="Content"
          value={newTicketData.content}
          onChange={(e) => setNewTicketData({ ...newTicketData, content: e.target.value })}
          style={{
            width: '100%',
            padding: '10px',
            marginBottom: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            minHeight: '100px'
          }}
        />
        <button
          onClick={handleCreateTicket}
          style={{
            padding: '10px 20px',
            background: '#0066cc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Create Ticket
        </button>
      </div>

      {/* Tickets List */}
      <div style={{ background: 'white', borderRadius: '8px', overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '20px' }}>Loading tickets...</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ background: '#f5f5f5', borderBottom: '2px solid #ddd' }}>
                <th style={{ padding: '15px', textAlign: 'left' }}>ID</th>
                <th style={{ padding: '15px', textAlign: 'left' }}>Subject</th>
                <th style={{ padding: '15px', textAlign: 'left' }}>Status</th>
                <th style={{ padding: '15px', textAlign: 'left' }}>Category</th>
                <th style={{ padding: '15px', textAlign: 'left' }}>Sentiment</th>
                <th style={{ padding: '15px', textAlign: 'left' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map(ticket => (
                <tr
                  key={ticket.id}
                  style={{
                    borderBottom: '1px solid #eee',
                    cursor: 'pointer',
                    background: selectedTicket?.id === ticket.id ? '#f0f8ff' : 'white'
                  }}
                  onClick={() => setSelectedTicket(ticket)}
                >
                  <td style={{ padding: '15px' }}>#{ticket.id}</td>
                  <td style={{ padding: '15px' }}>{ticket.subject}</td>
                  <td style={{ padding: '15px' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      background: '#e8f4f8',
                      color: '#0066cc',
                      fontSize: '12px'
                    }}>
                      {ticket.status}
                    </span>
                  </td>
                  <td style={{ padding: '15px' }}>{ticket.category || '-'}</td>
                  <td style={{ padding: '15px' }}>
                    {ticket.sentiment ? `${(ticket.sentiment * 100).toFixed(0)}%` : '-'}
                  </td>
                  <td style={{ padding: '15px' }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleClassifyTicket(ticket.id);
                      }}
                      style={{
                        padding: '5px 10px',
                        background: '#2ecc71',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      Classify
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Ticket Details */}
      {selectedTicket && (
        <div style={{
          marginTop: '20px',
          background: 'white',
          padding: '20px',
          borderRadius: '8px'
        }}>
          <h3>Ticket Details</h3>
          <p><strong>Subject:</strong> {selectedTicket.subject}</p>
          <p><strong>Content:</strong> {selectedTicket.content}</p>
          <p><strong>Created:</strong> {new Date(selectedTicket.created_at).toLocaleString()}</p>
          <p><strong>Automation Score:</strong> {selectedTicket.automation_score}%</p>
        </div>
      )}
    </div>
  );
}