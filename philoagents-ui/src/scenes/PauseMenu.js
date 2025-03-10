import { Scene } from 'phaser';
import ApiService from '../services/ApiService';

export class PauseMenu extends Scene {
    constructor() {
        super('PauseMenu');
    }

    create() {
        const overlay = this.add.graphics();
        overlay.fillStyle(0x000000, 0.7);
        overlay.fillRect(0, 0, this.cameras.main.width, this.cameras.main.height);

        const centerX = this.cameras.main.width / 2;
        const centerY = this.cameras.main.height / 2;
        
        const panel = this.add.graphics();
        panel.fillStyle(0xffffff, 1);
        panel.fillRoundedRect(centerX - 200, centerY - 150, 400, 300, 20);
        panel.lineStyle(4, 0x000000, 1);
        panel.strokeRoundedRect(centerX - 200, centerY - 150, 400, 300, 20);

        this.add.text(centerX, centerY - 120, 'GAME PAUSED', {
            fontSize: '28px',
            fontFamily: 'Arial',
            color: '#000000',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        const buttonY = centerY - 50;
        const buttonSpacing = 70;

        this.createButton(centerX, buttonY, 'Resume Game', () => {
            this.resumeGame();
        });

        this.createButton(centerX, buttonY + buttonSpacing, 'Main Menu', () => {
            this.returnToMainMenu();
        });

        this.createButton(centerX, buttonY + buttonSpacing * 2, 'Reset Game', () => {
            this.resetGame();
        });

        this.input.keyboard.on('keydown-ESC', () => {
            this.resumeGame();
        });
    }

    createButton(x, y, text, callback) {
        const buttonWidth = 250;
        const buttonHeight = 50;
        const cornerRadius = 15;
        
        const shadow = this.add.graphics();
        shadow.fillStyle(0x000000, 0.4);
        shadow.fillRoundedRect(x - buttonWidth / 2 + 5, y - buttonHeight / 2 + 5, buttonWidth, buttonHeight, cornerRadius);

        const button = this.add.graphics();
        button.fillStyle(0x4a90e2, 1); 
        button.lineStyle(2, 0x3a70b2, 1); 
        button.fillRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
        button.strokeRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
        button.setInteractive(
            new Phaser.Geom.Rectangle(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight),
            Phaser.Geom.Rectangle.Contains
        );

        const buttonText = this.add.text(x, y, text, {
            fontSize: '22px',
            fontFamily: 'Arial',
            color: '#FFFFFF', 
            fontStyle: 'bold'
        }).setOrigin(0.5);

        button.on('pointerover', () => {
            button.clear();
            button.fillStyle(0x5da0f2, 1); 
            button.lineStyle(2, 0x3a70b2, 1);
            button.fillRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
            button.strokeRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
            buttonText.y -= 2;
        });

        button.on('pointerout', () => {
            button.clear();
            button.fillStyle(0x4a90e2, 1);
            button.lineStyle(2, 0x3a70b2, 1);
            button.fillRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
            button.strokeRoundedRect(x - buttonWidth / 2, y - buttonHeight / 2, buttonWidth, buttonHeight, cornerRadius);
            buttonText.y += 2;
        });

        button.on('pointerdown', callback);
        
        return { button, shadow, text: buttonText };
    }

    resumeGame() {
        this.scene.resume('Game');
        this.scene.stop();
    }

    returnToMainMenu() {
        this.scene.stop('Game');
        this.scene.start('MainMenu');
    }

    async resetGame() {
        try {
            await ApiService.resetMemory();
            
            this.scene.stop('Game');
            this.scene.start('Game');
            this.scene.stop();
        } catch (error) {
            console.error('Failed to reset game:', error);

            const centerX = this.cameras.main.width / 2;
            const centerY = this.cameras.main.height / 2 + 120;
            
            const errorText = this.add.text(centerX, centerY, 'Failed to reset game. Try again.', {
                fontSize: '16px',
                fontFamily: 'Arial',
                color: '#FF0000'
            }).setOrigin(0.5);
            
            this.time.delayedCall(3000, () => {
                errorText.destroy();
            });
        }
    }
} 