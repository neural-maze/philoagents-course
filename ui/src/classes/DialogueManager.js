import ApiService from '../services/ApiService';

class DialogueManager {
  constructor(scene) {
    this.scene = scene;
    this.dialogueBox = null;
    this.activePhilosopher = null;
    this.isTyping = false;
    this.currentMessage = '';
    this.cursorBlinkEvent = null;
    this.cursorVisible = true;
    this.hasSetupListeners = false;
    this.isStreaming = false;
  }

  initialize(dialogueBox) {
    this.dialogueBox = dialogueBox;
    
    if (!this.hasSetupListeners) {
      this.setupKeyboardListeners();
      this.hasSetupListeners = true;
    }
  }

  setupKeyboardListeners() {
    let apiResponse = '';
    this.scene.input.keyboard.on('keydown', async (event) => {
      if (!this.isTyping) {
        // If we're streaming text and space is pressed, skip the animation
        if (this.isStreaming && (event.key === 'Space' || event.key === ' ')) {
          this.skipStreaming();
          return;
        }
        return;
      }
    
      if (event.key === 'Enter') {
        if (this.currentMessage.trim() !== '') {
          this.dialogueBox.show('...', true);
          
          if (this.cursorBlinkEvent) {
            this.cursorBlinkEvent.remove();
            this.cursorBlinkEvent = null;
          }
          
          if (this.activePhilosopher.defaultMessage) {
            apiResponse = this.activePhilosopher.defaultMessage;
          } else {
            apiResponse = await ApiService.sendMessage(
              this.activePhilosopher, 
              this.currentMessage
            );
          }

          // Show API response with streaming effect
          this.dialogueBox.show('', true); // Clear the box first
          await this.streamText(apiResponse);
          
          this.currentMessage = '';
          this.isTyping = false;
        } else if (this.dialogueBox.text !== '|') {
          this.restartTypingPrompt();
        }
      } else if (event.key === 'Escape') {
        this.closeDialogue();
      } else if (event.key === 'Backspace') {
        this.currentMessage = this.currentMessage.slice(0, -1);
        this.updateDialogueText();
      } else if (event.key.length === 1) { // Single character keys
        this.currentMessage += event.key;
        this.updateDialogueText();
      }
    });
  }

  updateDialogueText() {
    this.dialogueBox.show(this.currentMessage + 
      (this.cursorVisible ? '|' : ''));
  }

  restartTypingPrompt() {
    this.dialogueBox.show('|', true);
    
    // Restart cursor blinking
    if (this.cursorBlinkEvent) {
      this.cursorBlinkEvent.remove();
    }
    
    this.cursorVisible = true;
    this.cursorBlinkEvent = this.scene.time.addEvent({
      delay: 530,
      callback: () => {
        if (this.dialogueBox.isVisible() && this.isTyping) {
          this.cursorVisible = !this.cursorVisible;
          this.dialogueBox.show(this.currentMessage + (this.cursorVisible ? '|' : ''));
        }
      },
      loop: true
    });
  }

  startDialogue(philosopher) {
    this.activePhilosopher = philosopher;
    this.isTyping = true;
    this.currentMessage = '';
    
    this.dialogueBox.show('|', true);

    if (this.cursorBlinkEvent) {
      this.cursorBlinkEvent.remove();
    }
    
    this.cursorVisible = true;
    this.cursorBlinkEvent = this.scene.time.addEvent({
      delay: 300,  
      callback: () => {
        if (this.dialogueBox.isVisible() && this.isTyping) {
          this.cursorVisible = !this.cursorVisible;
          this.dialogueBox.show('' + 
            this.currentMessage + (this.cursorVisible ? '|' : ''));
        }
      },
      loop: true
    });
  }

  closeDialogue() {
    this.dialogueBox.hide();
    this.isTyping = false;
    this.currentMessage = '';
    
    if (this.cursorBlinkEvent) {
      this.cursorBlinkEvent.remove();
      this.cursorBlinkEvent = null;
    }
  }

  isInDialogue() {
    return this.dialogueBox && this.dialogueBox.isVisible();
  }

  continueDialogue() {
    if (this.dialogueBox.isVisible()) {
      if (this.isStreaming) {
        // Skip the streaming animation if it's in progress
        this.skipStreaming();
      } else if (!this.isTyping) {
        // Start a new input prompt
        this.isTyping = true;
        this.currentMessage = '';
        this.restartTypingPrompt();
      }
    }
  }

  async streamText(text, speed = 30) {
    this.isStreaming = true;
    let displayedText = '';
    
    // Clear any existing cursor blink event
    if (this.cursorBlinkEvent) {
      this.cursorBlinkEvent.remove();
      this.cursorBlinkEvent = null;
    }
    
    // Display characters one by one
    for (let i = 0; i < text.length; i++) {
      displayedText += text[i];
      this.dialogueBox.show(displayedText, true);
      
      // Add a small delay between characters
      await new Promise(resolve => setTimeout(resolve, speed));
      
      // Allow skipping the animation with spacebar
      if (!this.isStreaming) break;
    }
    
    // Make sure the full text is displayed at the end
    if (this.isStreaming) {
      this.dialogueBox.show(text, true);
    }
    
    this.isStreaming = false;
    return true;
  }

  skipStreaming() {
    if (this.isStreaming) {
      this.isStreaming = false;
    }
  }
}

export default DialogueManager; 
