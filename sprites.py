# import the pygame module so that we can use it within our code
import pygame as pg
# import everything from settings so we can use that in our code here
from settings import *
# from the submodule sprite in pygame, import the Sprite class
from pygame.sprite import Sprite
# import everything from utils so we can use that in our code here
from utils import *
# import path from os so we can use it in our code here
from os import path
# import randint from random so we can use it in our code here
from random import randint
# create a shortcut for pygame's vector class we can use it in our code here
vec = pg.math.Vector2

# check whether the first sprite's hit rect collides with secon'd sprites hit rect
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    # keep track of whether the sprite has landed on a wall
    landed = False
    # check for x collision
    if dir == 'x':
        # checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # check if the player is running into the side of a wall
            if isinstance(sprite, Player):
                if ((sprite.vel.x >0 and hits[0].rect.centerx > sprite.hit_rect.centerx)
                    or (sprite.vel.x < 0 and hits[0].rect.centerx < sprite.hit_rect.centerx)):
                    sprite.collide_with_stuff(hits[0])
            # check to see if we're to the left of the wall
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                # reposition the player sprite to the left side of the wall
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            # check to see if we're to the right of the wall
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                # reposition the player sprite to the right side of the wall
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    # check for y collision
    if dir == 'y':
        # checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # check to see if we're above the wall
            if hits[0].rect.centery > sprite.hit_rect.centery:
                # check to see if the sprite is landing
                if sprite.vel.y > 0:
                    landed = True
                    # crack the wall only if the player landed after jumping
                    if isinstance(sprite, Player) and sprite.jumping:
                        sprite.collide_with_stuff(hits[0])
                # reposition the player sprite to the top of the wall
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            # check to see if we're below the wall
            if hits[0].rect.centery < sprite.hit_rect.centery:
                # crack the wall if the player jumps into it from below
                if isinstance(sprite, Player) and sprite.vel.y < 0:
                    sprite.collide_with_stuff(hits[0])
                # reposition the player sprite to the bottom of the wall
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
    # return whether the sprite has landed on a wall
    return landed

class Player(Sprite):
    def __init__(self, game, x, y):
        # initializes the sprite at an x and y with different attributes
        # add the player to the all sprites group
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        # load the sprite sheet and the player images
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        # create the image for the player sprite
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0, TILESIZE, TILESIZE)
        # create the regular rect and hit rect for the player
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT.copy()
        # set the starting velocity and position of the player
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        # make the player's hit rect match its starting position
        self.hit_rect.center = self.pos
        # set up the variables used for player animation
        self.last_update = 0
        self.current_frame = 0
        self.dir = "none"
        # keep track of how many coins the player collects
        self.coins = 0
        # set the jumping status detector to false
        self.jumping = False
        # keep track of whether the jump key is being held
        self.jump_key_held = False
        print("player initialized...")

    def get_keys(self):
        # reset the player's direction before check which keys are pressed
        self.dir = "none"
        # check to see which keys are being pressed
        keys = pg.key.get_pressed()
        # move the player left/right by chaning acceleration
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.dir = "left"
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.dir = "right"
            self.acc.x = PLAYER_ACC
        # check to see if a jump key is being pressed
        jump_pressed = keys[pg.K_SPACE] or keys[pg.K_UP] or keys[pg.K_w]
        # only jump when the key is first pressed to prevent continuous jumping from one press
        if jump_pressed and not self.jump_key_held:
            self.jump()
        # keep track of whether the jump key is still being held
        self.jump_key_held = jump_pressed
        # reduce horizontal acceleration in air to make jumps easier to control
        if self.jumping:
            self.acc.x *= 0.7071 

    def collide_with_stuff(self, wall):
        # change the wall's image if it has not already been hit
        if not wall.hit:
            wall.image = wall.hit_image
            wall.hit = True
            self.game.collide_snd.play()

    def jump(self):
        # check if player is standing on top of a wall
        for wall in self.game.all_walls:
            # check if player is horizontally above the wall
            if (self.hit_rect.right > wall.rect.left and
                self.hit_rect.left < wall.rect.right):
                # check if player's feet are touching wall's top
                distance = wall.rect.top - self.hit_rect.bottom
                if -1 <= distance <= 3 and not self.jumping:
                    # jump and play the sound
                    self.game.jump_sound.play()
                    self.jumping = True
                    #reduce sideways velocity when starting a jump
                    self.vel.x *= 0.7071
                    self.vel.y = -PLAYER_JUMP
                    break

    # not using is_jumping() bc it could mistakenly reset jump state from side collisions
    def is_jumping(self):
        # check to see if player is falling
        if self.vel.y > 0:
            # check to see if the player has collided with a wall
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            # reset the jumping variable if a collision is detected
            if hits:
                self.jumping = False

    def animate(self):
        # get the current time so we can control the speed of the animation
        now = pg.time.get_ticks()
        # change to the next animation frame every 350 milliseconds
        if now - self.last_update > 350:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            # save the bottom of the rect so the sprite stays in the same position
            bottom = self.rect.bottom
            self.image = self.idle_frames[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

    # load the different frames used for the player's animation
    def load_images(self):
        self.idle_frames = [self.spritesheet.get_image(0,0, TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE,0, TILESIZE, TILESIZE)
                            ]
        self.run_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
                            self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)
                            ]
        
    def update(self):
        # animate the player
        self.animate()
        # reset acceleration and apply gravity
        self.acc = vec(0,PLAYER_GRAV)
        # check which keys are being pressed
        self.get_keys()
        # apply stronger ground friction for quick stops and
        # weaker air friction to preserve momentum during jumps
        if self.jumping:
            self.acc.x += self.vel.x * -0.04
        else:
            self.acc.x += self.vel.x * PLAYER_FRIC
        # apply separate vertical friction so changing ground friction doesn't affect jump height
        self.acc.y += self.vel.y * -0.12
        # update the player's velocity based on acceleration
        self.vel += self.acc
        # limit horizontal speed without affecting vertical movement
        self.vel.x = max(-PLAYER_MAX_SPEED, min(self.vel.x, PLAYER_MAX_SPEED))
        # stop very small velocities so the player doesn't keep drifting
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0
        # update the player's position based on velocity and acceleration
        self.rect.center = self.pos
        self.pos += self.vel
        # check to see if the player has collided with a coin
        hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        if hits:
            # create particles at the coin's position
            for i in range(10):
                p = Particle(self.game, hits[0].rect.centerx, hits[0].rect.centery)
            # add one coin to the player's coin count
            self.coins += 1
            self.game.pickup_snd.play()
            self.game.score += 100
        # check for collisions in the x direction
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        # check for collisions in the y direction
        self.hit_rect.centery = self.pos.y
        # reset jumping if the player has landed on a wall
        if collide_with_walls(self, self.game.all_walls, 'y'):
            self.jumping = False
        # make the sprite's rect match its hit rect
        self.rect.center = self.hit_rect.center


class Wall(Sprite):
    def __init__(self, game, x, y):
        # add the wall to the all sprites and all walls groups
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        # load the normal and damaged wall images from the sprite sheet
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.image = self.spritesheet.get_image(192, 0, TILESIZE, TILESIZE)
        self.hit_image = self.spritesheet.get_image(224, 0, TILESIZE, TILESIZE)
        self.hit = False
        self.rect = self.image.get_rect()
        # set the wall's position based on its tile on the map
        self.vx, self.vy = 0,0
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        print("wall initialized...")

class Particle(Sprite):
    def __init__(self, game, x, y):
        # add the particle to the all sprites and all particles groups
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        # create a small white square for the particle
        self.image = pg.Surface((TILESIZE//8, TILESIZE//8))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        # set a random velocity + starting pos for the particle
        self.vel = vec(randint(-180,180),randint(-180,180))
        self.pos = vec(x,y)
        self.speed = 0.75
        # create a timer to keep track of how long the particle exists
        self.countdown = Timer()
        self.countdown.event_time = pg.time.get_ticks()
        print("particle initialized...")

    def update(self):
        # update the particle's pos based on its velocity
        self.pos += self.vel * self.speed * self.game.dt
        # use the countdown to eliminate particles after 2 seconds
        if pg.time.get_ticks() - self.countdown.event_time > 250:
            self.kill()
            print("im dead")
        # make the particles rect match its new position
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

class Coin(Sprite):
    def __init__(self, game, x, y):
        # add the coin to the all sprites and all coins groups
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        # load the sprite sheet and the coin's animation frames
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        # use the first coin as the starting image
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        # set the coin's position based on its tile on the map
        self.pos = vec(x*TILESIZE, y*TILESIZE)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        # set up the variables used for coin animation
        self.last_update = 0
        self.current_frame = 0
        print("coin initialized")

    def load_images(self):
        # load the two frames used for the coin's animation
        self.idle_frames = [
            self.spritesheet.get_image(128, 0, TILESIZE, TILESIZE),
            self.spritesheet.get_image(160, 0, TILESIZE, TILESIZE)
        ]

    def animate(self):
        # get the current time so we can control the speed of the animation
        now = pg.time.get_ticks()
        # change to the next coin frame every 350 milliseconds
        if now - self.last_update > 350:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.image = self.idle_frames[self.current_frame]
            self.rect = self.image.get_rect()

    def update(self):
        # animate the coin and keep it in the same position
        self.animate()
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

class Mob(Sprite):
    def __init__(self, game, x, y):
        # add the mob to the all sprites and all mobs groups
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        # load the sprite sheet and mob images
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        # create the image and rect for the mob
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        # set the mob's speed, velocity, and starting position
        self.speed = 100
        self.vel = vec(0,0)
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        # position the mob based on its tile on the map
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        # set up the variables used for mob animation
        self.dir = "none"
        self.last_update = 0
        self.current_frame = 0
        # create a separate hit rect for collisions
        self.hit_rect = MOB_HIT_RECT.copy()
        print("mob initialized...")

    def load_images(self):
            # load the frames for the mob's idle animation
            self.idle_frames = [self.spritesheet.get_image(64,0,TILESIZE, TILESIZE),
                                self.spritesheet.get_image(96,0,TILESIZE, TILESIZE)
                                ]
            # load the frames for the mob's running animation
            self.run_frames = [self.spritesheet.get_image(0,0,TILESIZE, TILESIZE),
                                self.spritesheet.get_image(TILESIZE,0,TILESIZE, TILESIZE)
                                ]
                
    def animate(self):
            # use the time element to get now
            now = pg.time.get_ticks()
            # use the idle animation when the mob is not moving
            if self.dir == "none":
                if now - self.last_update > 350:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                    bottom = self.rect.bottom
                    self.image = self.idle_frames[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom
            # check to see if the mob is moving to the right
            elif self.dir == "right":
                if now - self.last_update > 350:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                    bottom = self.rect.bottom
                    self.image = self.idle_frames[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom
            # check to see if the mob is moving to the left
            elif self.dir == "left":
                if now - self.last_update > 350:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                    bottom = self.rect.bottom
                    self.image = self.idle_frames[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom

    # determine the mob's velocity based on the player's position
    def chase(self, obj):
        # move the mob left or right toward the object's x position
        if self.pos.x < obj.pos.x:
            self.vel.x = self.speed
            self.dir = "right"
        elif self.pos.x > obj.pos.x:
            self.vel.x = -self.speed
            self.dir = "left"
        else:
            self.vel.x = 0

        # move the mob up or down toward the object's y position
        if self.pos.y < obj.pos.y:
            self.vel.y = self.speed
        elif self.pos.y > obj.pos.y:
            self.vel.y = -self.speed
        else:
            self.vel.y = 0

    def update(self):
        # animate the mob
        self.animate()
        # chase the player if there is a plyer in the game
        if self.game.player:
            self.chase(self.game.player)
        # update the mob's position based on its velocity
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        # check for collisions in the x direction
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        # check for collisions in the y direction
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')
        # make the sprite's rect match with its hit rect
        self.rect.center = self.hit_rect.center