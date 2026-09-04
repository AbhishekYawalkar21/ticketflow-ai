import axios from 'axios';

// Ensure /api/v1 is always attached
const BASE_HOST = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = BASE_HOST.endsWith('/api/v1') ? BASE_HOST : `${BASE_HOST}/api/v1`;

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const api = {
  // Tickets
  getTickets: async (skip = 0, limit = 20) => {
    const response = await client.get('/tickets', {
      params: { skip, limit }
    });
    return response.data;
  },

  createTicket: async (data) => {
    const response = await client.post('/tickets/', data);
    return response.data;
  },

  getTicket: async (id) => {
    const response = await client.get(`/tickets/${id}`);
    return response.data;
  },

  updateTicket: async (id, data) => {
    const response = await client.patch(`/tickets/${id}`, data);
    return response.data;
  },

  deleteTicket: async (id) => {
    await client.delete(`/tickets/${id}`);
  },

  // Classifications
  classifyTicket: async (ticketId) => {
    const response = await client.post(`/classifications/${ticketId}/classify`);
    return response.data;
  },

  getClassificationStatus: async (taskId) => {
    const response = await client.get(`/classifications/tasks/${taskId}`);
    return response.data;
  },

  // Analytics
  getMetrics: async (days = 7) => {
    const response = await client.get('/analytics/metrics', {
      params: { days }
    });
    return response.data;
  },

  getDashboard: async () => {
    const response = await client.get('/analytics/dashboard');
    return response.data;
  },

  // Interactions
  addInteraction: async (ticketId, data) => {
    const response = await client.post(`/tickets/${ticketId}/interactions`, data);
    return response.data;
  },

  getInteractions: async (ticketId) => {
    const response = await client.get(`/tickets/${ticketId}/interactions`);
    return response.data;
  }
};