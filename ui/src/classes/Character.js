class Character {
  constructor(scene, config) {
    this.scene = scene;
    this.id = config.id;
    this.name = config.name;
    this.spawnPoint = config.spawnPoint;
    this.atlas = config.atlas;
    this.defaultFrame = `${this.id}-${config.defaultDirection || 'front'}`;
    this.defaultMessage = config.defaultMessage;
    
    this.sprite = this.scene.physics.add
      .sprite(this.spawnPoint.x, this.spawnPoint.y, this.atlas, this.defaultFrame)
      .setSize(30, 40)
      .setOffset(0, 0)
      .setImmovable(true);

    this.scene.physics.add.collider(this.sprite, config.worldLayer);
    
    this.createAnimations();
    this.createNameLabel();
  }
  
  // Animation methods
  createAnimations() {
    const anims = this.scene.anims;
    const directions = ['left', 'right', 'front', 'back'];
    
    directions.forEach(direction => {
      const animKey = `${this.id}-${direction}-walk`;
      
      if (!anims.exists(animKey)) {
        anims.create({
          key: animKey,
          frames: anims.generateFrameNames(this.atlas, {
            prefix: `${this.id}-${direction}-walk-`,
            end: 8,
            zeroPad: 4,
          }),
          frameRate: 10,
          repeat: -1,
        });
      }
    });
  }
  
  // Player interaction methods
  facePlayer(player) {
    const dx = player.x - this.sprite.x;
    const dy = player.y - this.sprite.y;
    
    if (Math.abs(dx) > Math.abs(dy)) {
      this.sprite.setTexture(this.atlas, `${this.id}-${dx < 0 ? 'left' : 'right'}`);
    } else {
      this.sprite.setTexture(this.atlas, `${this.id}-${dy < 0 ? 'back' : 'front'}`);
    }
  }
  
  distanceToPlayer(player) {
    return Phaser.Math.Distance.Between(
      player.x, player.y,
      this.sprite.x, this.sprite.y
    );
  }
  
  isPlayerNearby(player, distance = 55) {
    return this.distanceToPlayer(player) < distance;
  }
  
  // Update loop
  update(player, isInDialogue) {
    this.sprite.body.setVelocity(0);
    
    if (isInDialogue && this.isPlayerNearby(player)) {
      this.facePlayer(player);
      this.sprite.anims.stop();
    }
    
    this.updateNameLabelPosition();
  }

  // Property getters
  get position() {
    return {
      x: this.sprite.x,
      y: this.sprite.y
    };
  }
  
  get body() {
    return this.sprite;
  }

  createNameLabel() {
    this.nameLabel = this.scene.add.text(0, 0, this.name, {
      font: "14px Arial",
      fill: "#ffffff",
      backgroundColor: "#000000",
      padding: { x: 4, y: 2 },
      align: "center"
    });
    this.nameLabel.setOrigin(0.5, 1);
    this.nameLabel.setDepth(20);
    this.updateNameLabelPosition();
  }

  updateNameLabelPosition() {
    if (this.nameLabel && this.sprite) {
      this.nameLabel.setPosition(
        this.sprite.x,
        this.sprite.y - this.sprite.height/2 - 10
      );
    }
  }
}

export default Character; 