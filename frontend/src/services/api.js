import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth endpoints
export const login = (credentials) => api.post('/auth/login', credentials);
export const register = (userData) => api.post('/auth/register', userData);

// Device endpoints
export const getDevices = () => api.get('/devices');
export const executeCommand = (deviceId, command) => api.post(`/devices/${deviceId}/execute`, { command });
export const uploadFile = (deviceId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/devices/${deviceId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// File management endpoints
export const listFiles = (deviceId, path) => api.get(`/devices/${deviceId}/files`, { params: { path } });
export const createFolder = (deviceId, path) => api.post(`/devices/${deviceId}/files/folder`, { path });
export const deleteFile = (deviceId, path) => api.delete(`/devices/${deviceId}/files`, { params: { path } });

// Live monitoring endpoints
export const getDeviceMetrics = (deviceId) => api.get(`/devices/${deviceId}/metrics`);

export default api;