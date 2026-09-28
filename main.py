# thie file was created by Varnav Ekanth
# code inspired by game dev Chris Bradfield who was inspired by Notch

# import the pygame module so that we can use it within our code
import pygame as pg

from os import path
# import everything from sprites so we can use that in our code here
from sprites import *
# import everything from settings so we can use that in our code here
from settings import *

from utils import *

'''
Data types: boolean, JSON, strings, integers, floats, etc

Input (events): keyboard, mouse, right click, voice, 
power button, eye tracking, camera, gyroscoping, electrostatic, 
location, volume, microphone

Process: cursor position, position of the player, score, 
enemy position, velocity, aim in FPS

Output: graphics (things are drawn), sound (jump, power up, walking), 
hapitcs
'''

# create the class Game
class Game:
    def __init__(self):
        # initializes the class with running and playing attributes
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        print("game initialized...")
        pg.display.set_caption(TITLE)
        self.running = True
        self.playing = True
        self.clock = pg.time.Clock()

    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')
        self.snd_dir = path.join(self.game_dir, 'audio')
        self.map = Map(path.join(self.game_dir, map))

    def new(self):
        # creates a new sprite in the sprite group at (0,0)
        self.load_data('level1.txt')
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()

        for row, tiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'M':
                    Mob(self, col, row)
        for row, tiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):
                if tile == 'P':
                    Player(self, col, row)
    
    def run(self):
        # uses events that happen to influence how it's drawn
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def events(self):
        # looks through all events, if the event is quit then it stops running
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        # draws the background and the sprites
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

if __name__ == "__main__":
    g = Game()

while g.running:
    # the commands we give it
    g.new()
    g.run()