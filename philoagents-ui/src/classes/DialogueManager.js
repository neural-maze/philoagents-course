import { createHistoryPanel } from '../chatHistory';
import ApiService from '../services/ApiService';
import WebSocketApiService from '../services/WebSocketApiService';
import { t } from '../i18n';
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
    if(!this.hasSetupListeners)
    {
      this.setupKeyboardListeners();
      this.createChineseInput();
      createHistoryPanel(this.scene);
      this.hasSetupListeners = true;
    }
    if (!this.hasSetupListeners) {
      this.setupKeyboardListeners();
      this.createChineseInput();
      this.hasSetupListeners = true;
    }
  }

  
    

  
  createChineseInput() {
    // 使用浏览器原生输入框，而不是 Phaser DOM
    const input = document.createElement('input');

    input.id = 'philo-chat-input';
    input.type = 'text';
    input.placeholder = '请输入中文，按回车发送';
    input.maxLength = 1000;
    input.autocomplete = 'off';

    Object.assign(input.style, {
      position: 'fixed',
      left: '50%',
      bottom: '12%',
      transform: 'translateX(-50%)',
      width: 'min(700px, 85vw)',
      height: '46px',
      padding: '8px 12px',
      boxSizing: 'border-box',
      fontSize: '20px',
      fontFamily: 'Microsoft YaHei, Arial, sans-serif',
      background: '#ffffff',
      color: '#111111',
      border: '2px solid #4a90e2',
      borderRadius: '8px',
      zIndex: '9999',
      display: 'none',
      outline: 'none'
    });

    document.body.appendChild(input);
    this.chatInput = input;

    let composing = false;
    let lastCompositionEnd = 0;

    input.addEventListener('compositionstart', () => {
      composing = true;
    });

    input.addEventListener('compositionend', () => {
      composing = false;
      lastCompositionEnd = Date.now();
    });

    input.addEventListener('keydown', async (event) => {
      // 不让输入框里的按键传给游戏
      event.stopPropagation();

      // 输入法正在选词时，不触发游戏操作
      if (composing || event.isComposing || event.keyCode === 229) {
        return;
      }

      if (event.key === 'Escape') {
        event.preventDefault();
        this.closeDialogue();
        return;
      }

      if (event.key === 'Enter') {
        event.preventDefault();

        // 防止拼音选词时的回车被当作发送
        if (Date.now() - lastCompositionEnd < 100) return;
        if (!this.isTyping || this.isStreaming) return;

        const message = input.value.trim();
        if (!message) return;

        this.currentMessage = message;
        this.isTyping = false;

        input.style.display = 'none';
        input.blur();

        await this.handleEnterKey();
      }
    });

    // 离开游戏场景时清理输入框
    this.scene.events.once('shutdown', () => {
      input.remove();
      this.chatInput = null;
    });
  }






  setupKeyboardListeners() {
  this.scene.input.keyboard.on('keydown-SPACE', () => {
    if (this.isStreaming) {
      this.skipStreaming();
    }
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
    this.isTyping = true;

    this.stopCursorBlink();
    this.dialogueBox.show('请输入内容，按回车发送', true);

    this.chatInput.value = '';
    this.chatInput.style.display = 'block';
    this.chatInput.focus();
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

    this.stopCursorBlink();
    this.dialogueBox.show('请输入内容，按回车发送', true);

    this.chatInput.value = '';
    this.chatInput.style.display = 'block';
    this.chatInput.focus();
  }



  closeDialogue() {
    if (this.chatInput) {
      this.chatInput.style.display = 'none';
      this.chatInput.blur();
    }

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
