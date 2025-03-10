import ApiService from '../services/ApiService';
import WebSocketApiService from '../services/WebSocketApiService';

class DialogueManager {
  constructor(scene) {
    // Core properties
    this.scene = scene;
    this.dialogueBox = null;
    this.activePhilosopher = null;
    
    // State management
    this.isTyping = false;
    this.isStreaming = false;
    this.currentMessage = '';
    this.streamingText = '';
    
    // Cursor properties
    this.cursorBlinkEvent = null;
    this.cursorVisible = true;
    
    // Connection management
    this.hasSetupListeners = false;
    this.disconnectTimeout = null;
  }

  // === Initialization ===
  
  initialize(dialogueBox) {
    this.dialogueBox = dialogueBox;
    
    if (!this.hasSetupListeners) {
      this.setupKeyboardListeners();
      this.hasSetupListeners = true;
    }
  }

  setupKeyboardListeners() {
    this.scene.input.keyboard.on('keydown', async (event) => {
      if (!this.isTyping) {
        if (this.isStreaming && (event.key === 'Space' || event.key === ' ')) {
          this.skipStreaming();
        }
        return;
      }
    
      this.handleKeyPress(event);
    });
  }

  // === Input Handling ===
  
  async handleKeyPress(event) {
    if (event.key === 'Enter') {
      await this.handleEnterKey();
    } else if (event.key === 'Escape') {
      this.closeDialogue();
    } else if (event.key === 'Backspace') {
      this.currentMessage = this.currentMessage.slice(0, -1);
      this.updateDialogueText();
    } else if (event.key.length === 1) { // Single character keys
      if (!this.isTyping) {
        this.currentMessage = '';
        this.isTyping = true;
      }
      
      this.currentMessage += event.key;
      this.updateDialogueText();
    }
  }

  async handleEnterKey() {
    if (this.currentMessage.trim() !== '') {
      this.dialogueBox.show('...', true);
      this.stopCursorBlink();
      
      if (this.activePhilosopher.defaultMessage) {
        await this.handleDefaultMessage();
      } else {
        await this.handleWebSocketMessage();
      }
      
      this.currentMessage = '';
      this.isTyping = false;
    } else if (!this.isTyping) {
      this.restartTypingPrompt();
    }
  }

  // === Message Processing ===
  
  async handleDefaultMessage() {
    const apiResponse = this.activePhilosopher.defaultMessage;
    this.dialogueBox.show('', true);
    await this.streamText(apiResponse);
  }

  async handleWebSocketMessage() {
    this.dialogueBox.show('', true);
    this.isStreaming = true;
    this.streamingText = '';
    
    try {
      await this.processWebSocketMessage();
    } catch (error) {
      console.error('WebSocket error:', error);
      await this.fallbackToRegularApi();
    } finally {
      this.isTyping = false;
    }
  }

  async processWebSocketMessage() {
    await WebSocketApiService.connect();
    
    const callbacks = {
      onMessage: () => { 
        this.finishStreaming();
      },
      onChunk: (chunk) => {
        this.streamingText += chunk;
        this.dialogueBox.show(this.streamingText, true);
      },
      onStreamingStart: () => {
        this.isStreaming = true;
      },
      onStreamingEnd: () => {
        this.finishStreaming();
      }
    };
    
    await WebSocketApiService.sendMessage(
      this.activePhilosopher,
      this.currentMessage,
      callbacks
    );
    
    while (this.isStreaming) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    this.currentMessage = '';
    WebSocketApiService.disconnect();
  }

  finishStreaming() {
    this.isStreaming = false;
    this.dialogueBox.show(this.streamingText, true);
  }

  async fallbackToRegularApi() {
    const apiResponse = await ApiService.sendMessage(
      this.activePhilosopher, 
      this.currentMessage
    );
    await this.streamText(apiResponse);
  }

  // === UI Management ===
  
  updateDialogueText() {
    const displayText = this.currentMessage + (this.cursorVisible ? '|' : '');
    this.dialogueBox.show(displayText, true);
  }

  restartTypingPrompt() {
    this.currentMessage = '';
    this.dialogueBox.show('|', true);
    
    this.stopCursorBlink();
    this.cursorVisible = true;
    this.startCursorBlink();
    
    this.updateDialogueText();
  }

  // === Cursor Management ===
  
  startCursorBlink() {
    this.cursorBlinkEvent = this.scene.time.addEvent({
      delay: 300,  
      callback: () => {
        if (this.dialogueBox.isVisible() && this.isTyping) {
          this.cursorVisible = !this.cursorVisible;
          this.updateDialogueText();
        }
      },
      loop: true
    });
  }

  stopCursorBlink() {
    if (this.cursorBlinkEvent) {
      this.cursorBlinkEvent.remove();
      this.cursorBlinkEvent = null;
    }
  }

  // === Dialogue Flow Control ===
  
  startDialogue(philosopher) {
    this.cancelDisconnectTimeout();
    
    this.activePhilosopher = philosopher;
    this.isTyping = true;
    this.currentMessage = '';
    
    this.dialogueBox.show('|', true);
    this.stopCursorBlink();
    
    this.cursorVisible = true;
    this.startCursorBlink();
  }

  closeDialogue() {
    this.dialogueBox.hide();
    this.isTyping = false;
    this.currentMessage = '';
    this.isStreaming = false;
    
    this.stopCursorBlink();
    this.scheduleDisconnect();
  }

  isInDialogue() {
    return this.dialogueBox && this.dialogueBox.isVisible();
  }

  continueDialogue() {
    if (!this.dialogueBox.isVisible()) return;
    
    if (this.isStreaming) {
      this.skipStreaming();
    } else if (!this.isTyping) {
      this.isTyping = true;
      this.currentMessage = '';
      this.dialogueBox.show('', false);
      this.restartTypingPrompt();
    }
  }

  // === Text Streaming ===
  
  async streamText(text, speed = 30) {
    this.isStreaming = true;
    let displayedText = '';
    
    this.stopCursorBlink();
    
    for (let i = 0; i < text.length; i++) {
      displayedText += text[i];
      this.dialogueBox.show(displayedText, true);
      
      await new Promise(resolve => setTimeout(resolve, speed));
      
      if (!this.isStreaming) break;
    }
    
    if (this.isStreaming) {
      this.dialogueBox.show(text, true);
    }
    
    this.isStreaming = false;
    return true;
  }

  skipStreaming() {
    this.isStreaming = false;
  }

  // === Connection Management ===
  
  cancelDisconnectTimeout() {
    if (this.disconnectTimeout) {
      clearTimeout(this.disconnectTimeout);
      this.disconnectTimeout = null;
    }
  }

  scheduleDisconnect() {
    this.cancelDisconnectTimeout();
    
    this.disconnectTimeout = setTimeout(() => {
      WebSocketApiService.disconnect();
    }, 5000);
  }
}

export default DialogueManager; 
