import { io } from 'socket.io-client';

const WEBSOCKET_URL = 'wss://fatakeshto-application.vercel.app';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
  }

  connect(token) {
    this.socket = io(WEBSOCKET_URL, {
      auth: { token },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Setup default event listeners
    this.setupEventListeners();
  }

  setupEventListeners() {
    // Device status updates
    this.socket.on('device_status', (data) => {
      this.notifyListeners('device_status', data);
    });

    // Screen sharing updates
    this.socket.on('screen_data', (data) => {
      this.notifyListeners('screen_data', data);
    });

    // Device metrics updates
    this.socket.on('device_metrics', (data) => {
      this.notifyListeners('device_metrics', data);
    });

    // Command execution results
    this.socket.on('command_result', (data) => {
      this.notifyListeners('command_result', data);
    });
  }

  subscribe(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  unsubscribe(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  notifyListeners(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => callback(data));
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.listeners.clear();
    }
  }

  // Screen sharing methods
  startScreenShare(deviceId) {
    this.socket.emit('start_screen_share', { deviceId });
  }

  stopScreenShare(deviceId) {
    this.socket.emit('stop_screen_share', { deviceId });
  }

  // Command execution
  sendCommand(deviceId, command) {
    this.socket.emit('execute_command', { deviceId, command });
  }
}

// Create a singleton instance
const wsService = new WebSocketService();
export default wsService;