import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let authToken = null;
let devUser = null;

export const setupApiAuth = ({ token, user, initData }) => {
  authToken = token || null;
  devUser = user || null;

  api.interceptors.request.use((config) => {
    // JWT, если есть
    if (authToken) {
      config.headers['Authorization'] = `Bearer ${authToken}`;
    }

    // Telegram initData для бэкенда
    if (initData) {
      config.headers['X-Telegram-Init-Data'] = initData;
    }

    // Dev заголовки для упрощения запуска MVP в non-prod окружении
    if (devUser?.id) {
      config.headers['X-Dev-User-Id'] = String(devUser.id);
      if (devUser.username) config.headers['X-Dev-Username'] = devUser.username;
      if (devUser.first_name) config.headers['X-Dev-First-Name'] = devUser.first_name;
      if (devUser.last_name) config.headers['X-Dev-Last-Name'] = devUser.last_name;
    }

    return config;
  });
};

// API методы
export const matchAPI = {
  create: async (userData, promise = null, stakeAmount = 0) => {
    const response = await api.post('/api/match/create', {
      telegram_id: userData.id.toString(),
      username: userData.username,
      full_name: `${userData.first_name} ${userData.last_name || ''}`.trim(),
      promise,
      stake_amount: stakeAmount,
    });
    return response.data;
  },

  join: async (matchId, userData) => {
    const response = await api.post(`/api/match/${matchId}/join`, {
      telegram_id: userData.id.toString(),
      username: userData.username,
      full_name: `${userData.first_name} ${userData.last_name || ''}`.trim(),
    });
    return response.data;
  },

  makeChoice: async (matchId, telegramId, choice) => {
    const response = await api.post(`/api/match/${matchId}/choice`, {
      telegram_id: telegramId.toString(),
      choice,
    });
    return response.data;
  },

  getStatus: async (matchId) => {
    const response = await api.get(`/api/match/${matchId}/status`);
    return response.data;
  },
};

export const userAPI = {
  getInfo: async (telegramId) => {
    const response = await api.get(`/api/user/${telegramId}`);
    return response.data;
  },
};

export default api;