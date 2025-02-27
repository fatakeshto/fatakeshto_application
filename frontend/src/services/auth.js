import axios from 'axios';

const API_URL = 'https://fatakeshto-application.onrender.com';

const authService = {
    login: async (username, password, mfaToken = null) => {
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            if (mfaToken) {
                formData.append('mfa_token', mfaToken);
            }

            const response = await axios.post(`${API_URL}/api/auth/token`, formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                }
            });

            if (response.data.requires_mfa) {
                return { requires_mfa: true };
            }

            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('role', response.data.role);
            }
            return response.data;
        } catch (error) {
            if (error.response?.status === 422) {
                throw { detail: error.response.data.detail || 'Username and password are required' };
            } else if (error.response?.status === 401) {
                throw { detail: error.response.data.detail || 'Authentication failed' };
            }
            throw { detail: 'An error occurred during login' };
        }
    },

    logout: () => {
        localStorage.removeItem('user');
    },

    getCurrentUser: () => {
        const userStr = localStorage.getItem('user');
        if (userStr) return JSON.parse(userStr);
        return null;
    },

    getToken: () => {
        const user = authService.getCurrentUser();
        return user?.access_token;
    },

    isAuthenticated: () => {
        return !!authService.getToken();
    }
};

export default authService;