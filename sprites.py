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
        self.image.set_colorkey(BLACK)
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
        # reset v to zero
        # listen for events
        # change velocity based on which key is pressed
        # self.vel = vec(0,0)
        self.dir = "none"
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = -PLAYER_SPEED
            # self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x = PLAYER_SPEED
            # self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.acc.y = -PLAYER_SPEED
            # self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.acc.y = PLAYER_SPEED
            # self.vel.y = PLAYER_SPEED
        # check to see if player is moving diagonally
        # if self.vel.x != 0 and self.vel.y != 0:
        #     self.vel *= 0.7071

    def jump(self):
        pass

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
        self.acc = vec(0,2)
        # check which keys are being pressed
        self.get_keys()
        self.animate()
        self.acc.x += self.vel.x * PLAYER_FRIC
        self.acc.y += self.vel.y * PLAYER_FRIC
        self.vel += self.acc
        self.rect.center = self.pos
        self.pos += self.vel + 0.5 * self.acc
        # check to see if the player has collided with a coin
        hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        if hits:
            for i in range(25):
                p = Particle(self.game, hits[0].pos.x, hits[0].pos.y)
            # add one coin to the player's coin count
            self.coins += 1
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
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE/8, TILESIZE/8))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.vel = vec(randint(-180,180),randint(-180,180))
        self.pos = vec(x,y)
        self.speed = 0.5
        self.countdown = Timer()
        self.countdown.event_time = floor(pg.time.get_ticks()/1000)
        print("particle initialized...")

    def update(self):
        self.pos += self.vel * self.speed * self.game.dt
        # use the countdown to eliminate particles after 2 seconds
        if self.countdown.get_delta() > 2:
            self.kill()
            print("im dead")

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

class Coin(Sprite):
    def __init__(self, game, x, y):
        # add the coin to the all sprites and all coins groups
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        # create the coin as a yellow circle
        self.image = pg.Surface((TILESIZE, TILESIZE))
        pg.draw.circle(self.image, (YELLOW), (16, 16), 16)
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        # set the coin's position based on its tile on the map
        self.pos = vec(x*TILESIZE, y*TILESIZE)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        print("coin initialized")
    def update(self):
        pass

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
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
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
                    self.image.set_colorkey(BLACK)
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom
            # check to see if the mob is moving to the right
            elif self.dir == "right":
                pass
    
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