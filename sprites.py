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

#check to see if the hit rect of one sprite collides with another sprite
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    # check for x collision
    if dir == 'x':
        # checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
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
                # reposition the player sprite to the top of the wall
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            # check to see if we're below the wall
            if hits[0].rect.centery < sprite.hit_rect.centery:
                # reposition the player sprite to the bottom of the wall
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

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
        self.hit_rect = PLAYER_HIT_RECT
        # set the starting velocity and position of the player
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.pos = vec(x*TILESIZE,y*TILESIZE)
        # set up the variables used for player animation
        self.last_update = 0
        self.current_frame = 0
        self.dir = "none"
        # keep track of how many coins the player collects
        self.coins = 0
        self.jumping = False
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
        # move the player up/down by changing acceleration
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.acc.y = -PLAYER_ACC
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.acc.y = PLAYER_ACC
        # check to see if player is trying to jump
        if keys[pg.K_SPACE]:
            self.jump()
        # reduce player's velocity when moving diagonally
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def jump(self):
        # move the player's rect down slightly to check for a wall below
        self.rect.y += 2
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        # move the rect back to its og position
        self.rect.y -= 2
        # jump if the player is standing on a wall + not already jumping
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

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
        # animate the player and check if the player has landed
        self.animate()
        self.is_jumping()
        # reset acceleration and apply gravity
        self.acc = vec(0,PLAYER_GRAV)
        # check which keys are being pressed
        self.get_keys()
        # apply friction to slow the player's movement
        self.acc.x += self.vel.x * PLAYER_FRIC
        self.acc.y += self.vel.y * PLAYER_FRIC
        # update the player's velocity based on acceleration
        self.vel += self.acc
        # stop very small velocities so the player doesn't keep drifting
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if abs(self.vel.y) < 0.1:
            self.vel.y = 0
        # update the player's position based on velocity and acceleration
        self.rect.center = self.pos
        self.pos += self.vel + 0.5 * self.acc
        # check to see if the player has collided with a coin
        hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        if hits:
            # create particles at the coin's position
            for i in range(25):
                p = Particle(self.game, hits[0].pos.x, hits[0].pos.y)
            # add one coin to the player's coin count
            self.coins += 1
            self.game.pickup_snd.play()
            self.game.score += 1
        # check for collisions in the x direction
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        # check for collisions in the y direction
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')
        # make the sprite's rect match its hit rect
        self.rect.center = self.hit_rect.center


class Wall(Sprite):
    def __init__(self, game, x, y):
        # add the wall to the all sprites and all walls groups
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        # create a tile sized surface for the wall
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(SKY_BLUE)
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
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        # set a random velocity + starting pos for the particle
        self.vel = vec(randint(-180,180),randint(-180,180))
        self.pos = vec(x,y)
        self.speed = 0.5
        # create a timer to keep track of how long the particle exists
        self.countdown = Timer()
        self.countdown.event_time = floor(pg.time.get_ticks()/1000)
        print("particle initialized...")

    def update(self):
        # update the particle's pos based on its velocity
        self.pos += self.vel * self.speed * self.game.dt
        # use the countdown to eliminate particles after 2 seconds
        if self.countdown.get_delta() > 2:
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
        # create a seoarate hit rect for collisions
        self.hit_rect = MOB_HIT_RECT
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