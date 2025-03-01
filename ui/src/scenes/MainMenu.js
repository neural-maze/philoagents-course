import { Scene } from 'phaser';

export class MainMenu extends Scene {
    constructor() {
        super('MainMenu');
    }

    create() {
        this.add.image(0, 0, 'background').setOrigin(0, 0);
        this.add.image(510, 260, 'logo').setScale(0.55);

        const centerX = this.cameras.main.width / 2;
        const imageBottomY = 574;

        // Buttons
        this.createButton(centerX, imageBottomY - 50, 'Let\'s Play!', () => {
            this.scene.start('Game');
        });

        this.createButton(centerX, imageBottomY + 20, 'Instructions', () => {
            this.showInstructions();
        });

        this.createButton(centerX, imageBottomY + 90, 'Support Philoagents', () => {
            window.open('https://github.com/neural-maze/philoagents', '_blank');
        });

        // TODO: Maybe add here a button for restarting, that basically cleans all the Database?
        
    }

    showInstructions() {
        // Create a semi-transparent background
        const overlay = this.add.graphics();
        overlay.fillStyle(0x000000, 0.7);
        overlay.fillRect(0, 0, this.cameras.main.width, this.cameras.main.height);
        overlay.setInteractive(new Phaser.Geom.Rectangle(0, 0, this.cameras.main.width, this.cameras.main.height), Phaser.Geom.Rectangle.Contains);
        
        // Create a panel for the instructions
        const panel = this.add.graphics();
        panel.fillStyle(0xffffff, 1);
        panel.fillRoundedRect(this.cameras.main.width / 2 - 200, this.cameras.main.height / 2 - 150, 400, 300, 20);
        panel.lineStyle(4, 0x000000, 1);
        panel.strokeRoundedRect(this.cameras.main.width / 2 - 200, this.cameras.main.height / 2 - 150, 400, 300, 20);
        
        // Add title
        this.add.text(this.cameras.main.width / 2, this.cameras.main.height / 2 - 120, 'INSTRUCTIONS', {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#000000',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Add instruction text
        const instructions = [
            'Arrow keys for moving',
            'SPACE for talking to philosophers',
            'ESC for closing the dialogue'
        ];
        
        let yPos = this.cameras.main.height / 2 - 60;
        instructions.forEach(instruction => {
            this.add.text(this.cameras.main.width / 2, yPos, instruction, {
                fontSize: '22px',
                fontFamily: 'Arial',
                color: '#000000'
            }).setOrigin(0.5);
            yPos += 40;
        });
        
        // Add close button
        const closeButton = this.add.graphics();
        closeButton.fillStyle(0x87CEEB, 1);
        closeButton.fillRoundedRect(this.cameras.main.width / 2 - 60, this.cameras.main.height / 2 + 80, 120, 40, 10);
        closeButton.lineStyle(2, 0x000000, 1);
        closeButton.strokeRoundedRect(this.cameras.main.width / 2 - 60, this.cameras.main.height / 2 + 80, 120, 40, 10);
        
        const closeText = this.add.text(this.cameras.main.width / 2, this.cameras.main.height / 2 + 100, 'Close', {
            fontSize: '20px',
            fontFamily: 'Arial',
            color: '#000000',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        
        // Make close button interactive
        closeButton.setInteractive(new Phaser.Geom.Rectangle(this.cameras.main.width / 2 - 60, this.cameras.main.height / 2 + 80, 120, 40), Phaser.Geom.Rectangle.Contains);
        
        closeButton.on('pointerover', () => {
            closeButton.clear();
            closeButton.fillStyle(0x5CACEE, 1);
            closeButton.fillRoundedRect(this.cameras.main.width / 2 - 60, this.cameras.main.height / 2 + 80, 120, 40, 10);
            closeButton.lineStyle(2, 0x000000, 1);
            closeButton.strokeRoundedRect(this.cameras.main.width / 2 - 60, this.cameras.main.height / 2 + 80, 120, 40, 10);
        });
        
        closeButton.on('pointerout', () => {
            closeButton.clear();
            closeButton.fillStyle(0x87CEEB, 1);
            closeButton.fillRoundedRect(this.cameras.main.width / 2 - 60, this.cameras.main.height / 2 + 80, 120, 40, 10);
            closeButton.lineStyle(2, 0x000000, 1);
            closeButton.strokeRoundedRect(this.cameras.main.width / 2 - 60, this.cameras.main.height / 2 + 80, 120, 40, 10);
        });
        
        const closeInstructions = () => {
            overlay.destroy();
            panel.destroy();
            closeButton.destroy();
            closeText.destroy();
            
            // Remove all text elements
            this.children.list
                .filter(child => child.type === 'Text' && 
                       (child.text === 'INSTRUCTIONS' || 
                        instructions.includes(child.text) || 
                        child.text === 'Close'))
                .forEach(text => text.destroy());
        };
        
        closeButton.on('pointerdown', closeInstructions);
        overlay.on('pointerdown', closeInstructions);
    }

    createButton(x, y, text, callback) {
        const buttonWidth = 350;
        const buttonHeight = 60;
        const cornerRadius = 20;

        const shadow = this.add.graphics();
        shadow.fillStyle(0x666666, 1);
        shadow.fillRoundedRect(x - buttonWidth / 2 + 4, y - buttonHeight / 2 + 4, buttonWidth, buttonHeight, cornerRadius);

        const button = this.add.graphics();
        button.fillStyle(0xffffff, 1);
        button.fillRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
        button.setInteractive(new Phaser.Geom.Rectangle(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight), Phaser.Geom.Rectangle.Contains);

        const maxFontSize = 28;
        const padding = 10;
        let fontSize = maxFontSize;
        let buttonText;

        do {
            buttonText = this.add.text(x, y, text, {
                fontSize: `${fontSize}px`,
                fontFamily: 'Arial',
                color: '#000000',
                fontStyle: 'bold'
            }).setOrigin(0.5);

            if (buttonText.width > buttonWidth - padding) {
                buttonText.destroy();
                fontSize -= 1;
            }
        } while (buttonText.width > buttonWidth - padding);

        button.on('pointerover', () => {
            button.clear();
            button.fillStyle(0x87CEEB, 1);
            button.fillRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
            shadow.clear();
            shadow.fillStyle(0x888888, 1);
            shadow.fillRoundedRect(x - buttonWidth / 2 + 2, y - buttonHeight / 2 + 2, buttonWidth, buttonHeight, cornerRadius);
            buttonText.y -= 2;
        });

        button.on('pointerout', () => {
            button.clear();
            button.fillStyle(0xffffff, 1);
            button.fillRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
            shadow.clear();
            shadow.fillStyle(0x666666, 1);
            shadow.fillRoundedRect(x - buttonWidth / 2 + 4, y - buttonHeight / 2 + 4, buttonWidth, buttonHeight, cornerRadius);
            buttonText.y += 2;
        });

        button.on('pointerdown', () => {
            callback();
        });
    }
}
