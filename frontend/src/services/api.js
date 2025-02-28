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
    try {
        // Input validation
        if (!credentials.username || !credentials.password) {
            throw new Error('Username and password are required');
        }

        const formData = new URLSearchParams();
        formData.append('username', credentials.username.trim());
        formData.append('password', credentials.password);
        if (credentials.mfa_token) {
            formData.append('mfa_token', credentials.mfa_token.trim());
        }
        
        const response = await api.post('/api/auth/token', formData.toString(), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            },
            timeout: 10000 // 10 second timeout
        });
        
        if (response.data.access_token) {
            // Store tokens securely
            try {
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('role', response.data.role);
                if (response.data.refresh_token) {
                    localStorage.setItem('refresh_token', response.data.refresh_token);
                }
                // Store token expiry time
                const expiryTime = new Date().getTime() + (3600 * 1000); // 1 hour from now
                localStorage.setItem('token_expiry', expiryTime.toString());
            } catch (storageError) {
                console.error('Failed to store auth tokens:', storageError);
                throw new Error('Failed to store authentication data');
            }
        }
        
        return response.data;
    } catch (error) {
        // Clear any existing tokens on error
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('role');
        localStorage.removeItem('token_expiry');

        if (error.response) {
            switch (error.response.status) {
                case 422:
                    throw new Error('Invalid credentials format. Please check your input.');
                case 401:
                    throw new Error(error.response.data.detail || 'Invalid username or password');
                case 403:
                    throw new Error('Access denied. Please check your permissions.');
                case 429:
                    const retryAfter = error.response.headers['retry-after'];
                    throw new Error(`Too many login attempts. Please try again ${retryAfter ? `after ${retryAfter} seconds` : 'later'}`);
                case 500:
                    throw new Error('Server error. Please try again later.');
                default:
                    throw new Error(error.response.data.detail || 'An unexpected error occurred');
            }
        }
        if (error.code === 'ECONNABORTED') {
            throw new Error('Request timed out. Please try again.');
        }
        throw new Error('Network error. Please check your connection.');
    }
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