import { wsBaseUrl } from './apiBase';
import { authFrame, forgetSession } from './session';
class WebSocketApiService {
  constructor() {
    // Initialize connection-related properties
    this.initializeConnectionProperties();
    
    // Set up WebSocket URL based on environment
    this.baseUrl = wsBaseUrl();
  }

  initializeConnectionProperties() {
    this.socket = null;
    this.messageCallbacks = new Map();
    this.connected = false;
    this.connectionPromise = null;
    this.connectionTimeout = 10000;
  }

  connect() {
    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    // The token is fetched before the socket opens so onopen can send it immediately;
    // anything queued behind it would otherwise be rejected as an unauthenticated turn.
    this.connectionPromise = authFrame().then((frame) => this.openSocket(frame));

    return this.connectionPromise;
  }

  openSocket(frame) {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        if (this.socket) {
          this.socket.close();
        }
        this.connectionPromise = null;
        reject(new Error('WebSocket connection timeout'));
      }, this.connectionTimeout);

      this.socket = new WebSocket(`${this.baseUrl}/ws/chat`);
      
      this.socket.onopen = () => {
        this.socket.send(frame);
        console.log('WebSocket connection established');
        this.connected = true;
        clearTimeout(timeoutId);
        resolve();
      };

      this.socket.onmessage = this.handleMessage.bind(this);

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        clearTimeout(timeoutId);
        this.connectionPromise = null;
        reject(error);
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket connection closed');
        this.connected = false;
        this.connectionPromise = null;
        if (event.code === 4401) {
          // The server refused our token, so drop it and let the next send mint a new one.
          forgetSession();
        }
      };
    });
  }

  handleMessage(event) {
    const data = JSON.parse(event.data);
    
    if (data.error) {
      console.error('WebSocket error:', data.error);
      return;
    }
    
    if (data.streaming !== undefined) {
      this.handleStreamingUpdate(data.streaming);
      return;
    }
    
    if (data.chunk) {
      this.triggerCallback('chunk', data.chunk);
      return;
    }
    
    if (data.response) {
      this.triggerCallback('message', data.response);
    }
  }

  handleStreamingUpdate(isStreaming) {
    const streamingCallback = this.messageCallbacks.get('streaming');
    if (streamingCallback) {
      streamingCallback(isStreaming);
    }
  }

  triggerCallback(type, data) {
    const callback = this.messageCallbacks.get(type);
    if (callback) {
      callback(data);
    }
  }

  async sendMessage(philosopher, message, callbacks = {}) {
    try {
      if (!this.connected) {
        await this.connect();
      }

      this.registerCallbacks(callbacks);

      this.socket.send(JSON.stringify({
        message: message,
        philosopher_id: philosopher.id
      }));
    } catch (error) {
      console.error('Error sending message via WebSocket:', error);
      return this.getFallbackResponse(philosopher);
    }
  }

  registerCallbacks(callbacks) {
    if (callbacks.onMessage) {
      this.messageCallbacks.set('message', callbacks.onMessage);
    }
    
    if (callbacks.onStreamingStart) {
      this.messageCallbacks.set('streaming', (isStreaming) => {
        if (isStreaming) {
          callbacks.onStreamingStart();
        } else if (callbacks.onStreamingEnd) {
          callbacks.onStreamingEnd();
        }
      });
    }
    
    if (callbacks.onChunk) {
      this.messageCallbacks.set('chunk', callbacks.onChunk);
    }
  }

  getFallbackResponse(philosopher) {
    return "I'm so tired right now, I can't talk. I'm going to sleep now.";
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.connected = false;
      this.connectionPromise = null;
      this.messageCallbacks.clear();
    }
  }
}

export default new WebSocketApiService();
