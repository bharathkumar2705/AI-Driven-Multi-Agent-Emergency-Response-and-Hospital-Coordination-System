const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

class SimWebSocket {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectDelay = 2000;
    this._reconnectTimer = null;
  }

  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) return;
    try {
      this.ws = new WebSocket(WS_URL);
      this.ws.onopen = () => {
        console.log('[WS] Connected');
        this._emit('connected', {});
        clearTimeout(this._reconnectTimer);
      };
      this.ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          this._emit(msg.type, msg.data || msg);
          this._emit('*', msg);
        } catch {}
      };
      this.ws.onclose = () => {
        console.log('[WS] Disconnected, reconnecting...');
        this._emit('disconnected', {});
        this._reconnectTimer = setTimeout(() => this.connect(), this.reconnectDelay);
      };
      this.ws.onerror = () => {};
    } catch (e) {
      console.warn('[WS] Failed to connect:', e);
    }
  }

  disconnect() {
    clearTimeout(this._reconnectTimer);
    if (this.ws) { this.ws.close(); this.ws = null; }
  }

  on(eventType, callback) {
    if (!this.listeners.has(eventType)) this.listeners.set(eventType, []);
    this.listeners.get(eventType).push(callback);
    return () => this.off(eventType, callback);
  }

  off(eventType, callback) {
    const arr = this.listeners.get(eventType) || [];
    this.listeners.set(eventType, arr.filter(fn => fn !== callback));
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  ping() { this.send({ type: 'PING' }); }

  _emit(type, data) {
    (this.listeners.get(type) || []).forEach(fn => { try { fn(data); } catch {} });
  }

  get isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

export const wsService = new SimWebSocket();
