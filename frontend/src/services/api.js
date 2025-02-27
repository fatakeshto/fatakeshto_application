import axios from 'axios';

const API_BASE_URL = 'https://fatakeshto-application.onrender.com';

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
export const login = async (credentials) => {
    const formData = new URLSearchParams();
    formData.append('grant_type', 'password');
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    if (credentials.mfa_token) {
        formData.append('mfa_token', credentials.mfa_token);
    }
    return api.post('/api/auth/login', formData.toString(), {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
};
export const register = (userData) => api.post('/api/auth/register', userData);

// Device endpoints
export const getDevices = () => api.get('/api/devices');
export const executeCommand = (deviceId, command) => api.post(`/api/devices/${deviceId}/execute`, { command });
export const uploadFile = (deviceId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/api/devices/${deviceId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// File management endpoints
export const listFiles = (deviceId, path) => api.get(`/api/devices/${deviceId}/files`, { params: { path } });
export const createFolder = (deviceId, path) => api.post(`/api/devices/${deviceId}/files/folder`, { path });
export const deleteFile = (deviceId, path) => api.delete(`/api/devices/${deviceId}/files`, { params: { path } });

// Live monitoring endpoints
export const getDeviceMetrics = (deviceId) => api.get(`/api/devices/${deviceId}/metrics`);

export default api;