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
  }
  
  createAnimations() {
    const anims = this.scene.anims;
    const directions = ['left', 'right', 'front', 'back'];
    
    // Create animations for each direction if they don't already exist
    directions.forEach(direction => {
      const key = `${this.id}-${direction}-walk`;
      
      // Skip if animation already exists
      if (anims.exists(key)) return;
      
      anims.create({
        key: key,
        frames: anims.generateFrameNames(this.atlas, {
          prefix: `${this.id}-${direction}-walk-`,
          end: 8,
          zeroPad: 4,
        }),
        frameRate: 10,
        repeat: -1,
      });
    });
  }
  
  // Turn to face the player when nearby
  facePlayer(player) {
    const dx = player.x - this.sprite.x;
    const dy = player.y - this.sprite.y;
    
    // Determine which direction to face based on player position
    if (Math.abs(dx) > Math.abs(dy)) {
      // Player is more to the side than above/below
      if (dx < 0) {
        this.sprite.setTexture(this.atlas, `${this.id}-left`);
      } else {
        this.sprite.setTexture(this.atlas, `${this.id}-right`);
      }
    } else {
      // Player is more above/below than to the side
      if (dy < 0) {
        this.sprite.setTexture(this.atlas, `${this.id}-back`);
      } else {
        this.sprite.setTexture(this.atlas, `${this.id}-front`);
      }
    }
  }
  
  // Calculate distance to player
  distanceToPlayer(player) {
    return Phaser.Math.Distance.Between(
      player.x, player.y,
      this.sprite.x, this.sprite.y
    );
  }
  
  // Check if player is within interaction distance
  isPlayerNearby(player, distance = 55) {
    return this.distanceToPlayer(player) < distance;
  }
  
  update(player, isInDialogue) {
    // Stop any previous movement
    this.sprite.body.setVelocity(0);
    
    // If in dialogue, face the player
    if (isInDialogue && this.isPlayerNearby(player)) {
      this.facePlayer(player);
      this.sprite.anims.stop();
    }
  }

  // Get current position
  get position() {
    return {
      x: this.sprite.x,
      y: this.sprite.y
    };
  }
  
  // Get sprite for collision detection
  get body() {
    return this.sprite;
  }
}

export default Character; 