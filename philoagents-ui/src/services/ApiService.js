import { getPlayerId } from '../playerId';
import { httpBaseUrl } from './apiBase';
import { authHeaders, forgetSession, getSession } from './session';

class ApiService {
  constructor() {
    this.apiUrl = httpBaseUrl();
  }

  async request(endpoint, method, data, retried = false) {
    const url = `${this.apiUrl}${endpoint}`;
    const options = {
      method,
      // player_id is still sent for the benefit of a server running without
      // SESSION_SECRET; an authenticated one takes the identity from the token instead.
      headers: await authHeaders(),
      body: data ? JSON.stringify({ ...data, player_id: getPlayerId() }) : undefined,
    };

    const response = await fetch(url, options);

    if (response.status === 401 && !retried) {
      // A rotated server secret invalidates every stored token; mint one and try again
      // rather than leaving the player stuck on a dead session.
      forgetSession();
      await getSession(true);
      return this.request(endpoint, method, data, true);
    }

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async sendMessage(philosopher, message) {
    try {
      const data = await this.request('/chat', 'POST', {
        message,
        philosopher_id: philosopher.id
      });

      return data.response;
    } catch (error) {
      console.error('Error sending message to API:', error);
      return this.getFallbackResponse(philosopher);
    }
  }

  getFallbackResponse(philosopher) {
    return `I'm sorry, ${philosopher.name || 'the philosopher'} is unavailable at the moment. Please try again later.`;
  }

  async getChatHistory(philosopherId) {
    const url =
        `/chat-history/` +
        `${encodeURIComponent(philosopherId)}` +
        `?player_id=${encodeURIComponent(getPlayerId())}`;

    const data = await this.request(url, 'GET');
    return data.turns;
  }

  async resetMemory() {
    try {
      return await this.request('/reset-memory', 'POST', {});
    } catch (error) {
      console.error('Error resetting memory:', error);
      throw error;
    }
  }
}

export default new ApiService();
