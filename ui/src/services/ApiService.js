class ApiService {
  constructor() {
    this.apiUrl = 'http://localhost:8000';
  }

  async sendMessage(philosopher, message) {
    try {
      const response = await fetch(`${this.apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          philosopher_id: philosopher.id
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      return data.response
    } catch (error) {
      console.error('Error sending message to API:', error);
      return this.getFallbackResponse(philosopher);
    }
  }

  getFallbackResponse(philosopher) {
    return "I'm so tired right now, I can't talk. I'm going to sleep now.";
  }
}

export default new ApiService(); 