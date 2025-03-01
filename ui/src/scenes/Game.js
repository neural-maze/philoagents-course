import { Scene } from 'phaser';
import Character from '../classes/Character';
import DialogueBox from '../classes/DialogueBox';
import DialogueManager from '../classes/DialogueManager';

export class Game extends Scene
{
    constructor ()
    {
        super('Game');
        this.controls = null;
        this.player = null;
        this.cursors = null;
        this.dialogueBox = null;
        this.spaceKey = null;
        this.activePhilosopher = null;
        this.dialogueManager = null;
    }

    create ()
    {
        const map = this.createTilemap();
        const tileset = this.addTileset(map);
        const layers = this.createLayers(map, tileset);
        let screenPadding = 20;
        let maxDialogueHeight = 200;

        this.createPhilosophers(map, layers);

        this.setupPlayer(map, layers.worldLayer);
        const camera = this.setupCamera(map);

        this.setupControls(camera);

        this.dialogueBox = new DialogueBox(this);
        this.dialogueText = this.add
            .text(60, this.game.config.height - maxDialogueHeight - screenPadding + screenPadding, '', {
            font: "18px monospace",
            fill: "#ffffff",
            padding: { x: 20, y: 10 },
            wordWrap: { width: 680 },
            lineSpacing: 6,
            maxLines: 5
            })
            .setScrollFactor(0)
            .setDepth(30)
            .setVisible(false);

        this.spaceKey = this.input.keyboard.addKey('SPACE');
        
        // Initialize the dialogue manager
        this.dialogueManager = new DialogueManager(this);
        this.dialogueManager.initialize(this.dialogueBox);
    }

    createPhilosophers(map, layers) {

        const philosopherConfigs = [
            { id: "socrates", name: "Socrates", defaultDirection: "right"},
            { id: "aristotle", name: "Aristotle", defaultDirection: "right" },
            { id: "plato", name: "Plato", defaultDirection: "front" },
            { id: "descartes", name: "Descartes", defaultDirection: "front" },
            { id: "leibniz", name: "Leibniz", defaultDirection: "front" },
            { id: "ada_lovelace", name: "Ada Lovelace", defaultDirection: "front" },
            { id: "turing", name: "Turing", defaultDirection: "front" },
            { id: "searle", name: "Searle", defaultDirection: "front" },
            { id: "chomsky", name: "Chomsky", defaultDirection: "front" },
            { id: "dennett", name: "Dennett", defaultDirection: "front" },
            { 
                id: "miguel", 
                name: "Miguel", 
                defaultDirection: "front", 
                defaultMessage: "Hey! Sorry friend, but I'm a currently writing my Substack article for tomorrow. Check out The Neural Maze if you are interested in my projects!" 
            },
            { 
                id: "paul", 
                name: "Paul", 
                defaultDirection: "front",
                defaultMessage: "Hey, I'm busy teaching my cat AI with my latest course. I can't talk right now. Check out Decoding ML for more on my thoughts." 
            }
        ];

        philosopherConfigs.forEach(config => {
            const spawnPoint = map.findObject("Objects", (obj) => obj.name === config.name);
            
            this[config.id] = new Character(this, {
                id: config.id,
                name: config.name,
                spawnPoint: spawnPoint,
                atlas: config.id,
                defaultDirection: config.defaultDirection,
                worldLayer: layers.worldLayer,
                defaultMessage: config.defaultMessage
            });
        });
    }

    checkPhilosopherInteraction() {
        const philosophers = [
            this.socrates, this.aristotle, this.plato, 
            this.descartes, this.leibniz, this.ada_lovelace, 
            this.turing, this.searle, this.chomsky,
             this.dennett, this.miguel, this.paul];

        let nearbyPhilosopher = null;

        for (const philosopher of philosophers) {
            if (philosopher.isPlayerNearby(this.player)) {
                nearbyPhilosopher = philosopher;
                break;
            }
        }
        
        if (nearbyPhilosopher) {
            if (Phaser.Input.Keyboard.JustDown(this.spaceKey)) {
                if (!this.dialogueBox.isVisible()) {
                    // Start a new dialogue
                    this.dialogueManager.startDialogue(nearbyPhilosopher);
                } else if (!this.dialogueManager.isTyping) {
                    // Continue the dialogue if we're not already typing
                    this.dialogueManager.continueDialogue();
                }
            }
            
            // Update philosopher facing the player when in dialogue
            if (this.dialogueBox.isVisible()) {
                nearbyPhilosopher.facePlayer(this.player);
            }
        } else {
            // No philosopher nearby, close dialogue if open
            if (this.dialogueBox.isVisible()) {
                this.dialogueManager.closeDialogue();
            }
        }
    }

    createTilemap() {
        return this.make.tilemap({ key: "map" });
    }

    addTileset(map) {
        const tuxmonTileset = map.addTilesetImage("tuxmon-sample-32px-extruded", "tuxmon-tiles");
        const greeceTileset = map.addTilesetImage("ancient_greece_tileset", "greece-tiles");
        const plantTileset = map.addTilesetImage("plant", "plant-tiles");

        return [tuxmonTileset, greeceTileset, plantTileset];
    }

    createLayers(map, tilesets) {
        const belowLayer = map.createLayer("Below Player", tilesets, 0, 0);
        const worldLayer = map.createLayer("World", tilesets, 0, 0);
        const aboveLayer = map.createLayer("Above Player", tilesets, 0, 0);
        worldLayer.setCollisionByProperty({ collides: true });
        aboveLayer.setDepth(10);
        return { belowLayer, worldLayer, aboveLayer };
    }

    setupPlayer(map, worldLayer) {
        const spawnPoint = map.findObject("Objects", (obj) => obj.name === "Spawn Point");
        this.player = this.physics.add.sprite(spawnPoint.x, spawnPoint.y, "sophia", "misa-front")
            .setSize(30, 40)
            .setOffset(0, 24);

        this.physics.add.collider(this.player, worldLayer);
        
        const philosophers = [
            this.socrates, this.aristotle, this.plato, 
            this.descartes, this.leibniz, this.ada_lovelace, 
            this.turing, this.searle, this.chomsky,
            this.dennett, this.miguel, this.paul
        ];
        
        philosophers.forEach(philosopher => {
            this.physics.add.collider(this.player, philosopher.sprite);
        });

        this.createPlayerAnimations();
    }

    createPlayerAnimations() {
        const anims = this.anims;
        anims.create({
            key: "misa-left-walk",
            frames: anims.generateFrameNames("sophia", { prefix: "misa-left-walk.", start: 0, end: 3, zeroPad: 3 }),
            frameRate: 10,
            repeat: -1,
        });
        anims.create({
            key: "misa-right-walk",
            frames: anims.generateFrameNames("sophia", { prefix: "misa-right-walk.", start: 0, end: 3, zeroPad: 3 }),
            frameRate: 10,
            repeat: -1,
        });
        anims.create({
            key: "misa-front-walk",
            frames: anims.generateFrameNames("sophia", { prefix: "misa-front-walk.", start: 0, end: 3, zeroPad: 3 }),
            frameRate: 10,
            repeat: -1,
        });
        anims.create({
            key: "misa-back-walk",
            frames: anims.generateFrameNames("sophia", { prefix: "misa-back-walk.", start: 0, end: 3, zeroPad: 3 }),
            frameRate: 10,
            repeat: -1,
        });
    }

    setupCamera(map) {
        const camera = this.cameras.main;
        camera.startFollow(this.player);
        camera.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        return camera;
    }

    setupControls(camera) {
        this.cursors = this.input.keyboard.createCursorKeys();
        this.controls = new Phaser.Cameras.Controls.FixedKeyControl({
            camera: camera,
            left: this.cursors.left,
            right: this.cursors.right,
            up: this.cursors.up,
            down: this.cursors.down,
            speed: 0.5,
        });
    }

    addHelpText() {
        this.add.text(16, 16, 'Arrow keys to move\nPress SPACE near philosophers to talk', {
            font: "18px monospace",
            fill: "#000000",
            padding: { x: 20, y: 10 },
            backgroundColor: "#ffffff",
        }).setScrollFactor(0).setDepth(30);
    }

    update(time, delta) {
        // Only allow movement if not in dialogue
        if (!this.dialogueBox.isVisible()) {
            this.updatePlayerMovement();
        }
        
        this.checkPhilosopherInteraction();
        
        // Update all philosophers
        const isInDialogue = this.dialogueBox.isVisible();
        this.socrates.update(this.player, isInDialogue);
        this.aristotle.update(this.player, isInDialogue);
        this.plato.update(this.player, isInDialogue);
        
        if (this.controls) {
            this.controls.update(delta);
        }
    }

    updatePlayerMovement() {
        const speed = 175;
        const prevVelocity = this.player.body.velocity.clone();
        this.player.body.setVelocity(0);

        if (this.cursors.left.isDown) {
            this.player.body.setVelocityX(-speed);
        } else if (this.cursors.right.isDown) {
            this.player.body.setVelocityX(speed);
        }

        if (this.cursors.up.isDown) {
            this.player.body.setVelocityY(-speed);
        } else if (this.cursors.down.isDown) {
            this.player.body.setVelocityY(speed);
        }

        this.player.body.velocity.normalize().scale(speed);

        if (this.cursors.left.isDown) {
            this.player.anims.play("misa-left-walk", true);
        } else if (this.cursors.right.isDown) {
            this.player.anims.play("misa-right-walk", true);
        } else if (this.cursors.up.isDown) {
            this.player.anims.play("misa-back-walk", true);
        } else if (this.cursors.down.isDown) {
            this.player.anims.play("misa-front-walk", true);
        } else {
            this.player.anims.stop();
            if (prevVelocity.x < 0) this.player.setTexture("sophia", "misa-left");
            else if (prevVelocity.x > 0) this.player.setTexture("sophia", "misa-right");
            else if (prevVelocity.y < 0) this.player.setTexture("sophia", "misa-back");
            else if (prevVelocity.y > 0) this.player.setTexture("sophia", "misa-front");
        }
    }
}
