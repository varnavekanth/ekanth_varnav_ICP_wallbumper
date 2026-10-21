# thie file was created by Varnav Ekanth
# code inspired by game dev Chris Bradfield who was inspired by Notch

# import the pygame module as pg so that we can use it within our code
import pygame as pg
# import path from os so we can use it in our code here
from os import path
# import everything from sprites so we can use that in our code here
from sprites import *
# import everything from settings so we can use that in our code here
from settings import *
# import everything from utils so we can use that in our code here
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

GOALS

RULES

FEEDBACK

FREEDOM
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
        # get the folder that the game is located in
        self.game_dir = path.dirname(__file__)
        # create paths to the image and audio folders
        self.img_dir = path.join(self.game_dir, 'images')
        self.snd_dir = path.join(self.game_dir, 'audio')
        # load the map from the map file
        self.map = Map(path.join(self.game_dir, map))

    def new(self):
        # set up a new game and load the level
        self.load_data('level1.txt')
        # create the different sprite groups used in the game
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_coins = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        # go through each tile in the map and create the correct sprite
        for row, tiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'M':
                    Mob(self, col, row)
                if tile == 'C':
                    Coin(self, col, row)
        # go through the map again and create the player
        for row, tiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):
                if tile == 'P':
                    self.player = Player(self, col, row)
    
    def run(self):
        # uses events that happen to influence how it's drawn
        self.playing = True
        while self.playing:
            # calculate the amount of time that passed since the last frame
            self.dt = self.clock.tick(FPS) / 1000
            # check events, update the game, and draw the new frame
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

    def draw_text(self, text, size, color, x, y):
        # find the arial font and create it at the given site
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        # turn the text into a surface that pygame can draw
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        # position the text and draw it onto the screen
        text_rect.midtop = (x,y)
        self.screen.blit(text_surface, text_rect)

    def update(self):
        # update every sprite in the all sprites group
        self.all_sprites.update()

    def draw(self):
        # draws the background and the sprites
        # this orde matters: the first things are on the bottom because they are the 'first' to be drawn
        # the last lines in this method are drawn on top
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(f"Frames per second:{1/self.dt}", 24, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text(f"Coins:{self.player.coins}", 24, WHITE, WIDTH/2, HEIGHT/7)
        pg.display.flip()

# create the game when this file is run directly
if __name__ == "__main__":
    g = Game()

while g.running:
    # keep starting and running the game while the game is running
    g.new()
    g.run()