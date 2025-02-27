import axios from 'axios';

const API_URL = 'https://fatakeshto-application.onrender.com';

const authService = {
    login: async (username, password) => {
        try {
            const response = await axios.post(`${API_URL}/api/auth/token`, 
                new URLSearchParams({
                    'username': username,
                    'password': password
                }), {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            if (response.data.access_token) {
                localStorage.setItem('user', JSON.stringify(response.data));
            }
            return response.data;
        } catch (error) {
            throw error.response?.data || { detail: 'An error occurred during login' };
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