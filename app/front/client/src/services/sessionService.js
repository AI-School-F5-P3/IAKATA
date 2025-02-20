import axios from './api';
import SocketService from './socketService';

class SessionService {
  static instance = null;
  socket = SocketService.getInstance();
  activeUsers = new Set();

  constructor() {
    this.setupSessionSync();
  }

  static getInstance() {
    if (!this.instance) {
      this.instance = new SessionService();
    }
    return this.instance;
  }

  setupSessionSync() {
    window.addEventListener('storage', (event) => {
      if (event.key === 'token' && !event.newValue) {
        this.handleSessionExpired();
      }
    });

    this.socket.subscribe('session', (event) => {
      switch (event.type) {
        case 'USER_CONNECTED':
          this.activeUsers.add(event.userId);
          break;
        case 'USER_DISCONNECTED':
          this.activeUsers.delete(event.userId);
          break;
      }
    });
  }

  async validateSession() {
    try {
      const token = sessionStorage.getItem('token');
      if (!token) return false;

      const response = await axios.post('/auth/validate', { token });
      return response.data.valid;
    } catch {
      return false;
    }
  }

  handleSessionExpired() {
    window.dispatchEvent(new CustomEvent('session-expired'));
  }

  getActiveUsers() {
    return Array.from(this.activeUsers);
  }
}

export default SessionService;
