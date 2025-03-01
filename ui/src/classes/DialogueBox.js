class DialogueBox {
    constructor(scene, config) {
        this.scene = scene;
        this.awaitingInput = false; // Add a flag to track input state
        
        // Create the dialogue box container
        const graphics = scene.add.graphics();
        graphics.fillStyle(0x000000, 0.7);
        graphics.fillRect(100, 500, 824, 200);
        graphics.lineStyle(2, 0xffffff);
        graphics.strokeRect(100, 500, 824, 200);
        
        // Create text
        this.text = scene.add.text(120, 520, '', {
            font: '24px Arial',
            fill: '#ffffff',
            wordWrap: { width: 784 }
        });
        
        // Group elements
        this.container = scene.add.container(0, 0, [graphics, this.text]);
        this.container.setDepth(30);
        this.container.setScrollFactor(0);
        this.hide();
    }
    
    show(message, awaitInput = false) {
        this.text.setText(message);
        this.container.setVisible(true);
        this.awaitingInput = awaitInput;
    }
    
    hide() {
        this.container.setVisible(false);
        this.awaitingInput = false;
    }
    
    isVisible() {
        return this.container.visible;
    }

    isAwaitingInput() {
        return this.awaitingInput;
    }
}

export default DialogueBox; 