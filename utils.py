# import the pygame module as pg so that we can use it within our code
import pygame as pg
# import everything from settings so we can use that in our code
from settings import *
# import the floor function from pythons built-in math module
from math import floor

#create the Map class so we can load the map from a text file
class Map:
    def __init__(self, filename):
        # create an empty list to store the rows of the map
        self.data = []
        # open the map file and add each line of the file to the data list
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        # find the width and height of the map in tiles
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        # find the width and height of the map in pixels
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE
        print("map instantiated")

# create the Spritesheet class so we can get images from the sprite sheet
class Spritesheet:
    def __init__(self, filename):
        # load the sprite sheet image
        self.spritesheet = pg.image.load(filename).convert_alpha()
    def get_image(self, x, y, width, height):
        # create a surface for the image we want to get
        image = pg.Surface((width, height), pg.SRCALPHA)
        # copy the selected part of the sprite sheet onto the surface
        image.blit(self.spritesheet, (0,0), (x, y, width, height))
        # scale the image to the width and height we want
        new_image = pg.transform.scale(image, (width, height))
        image = new_image
        return image

# creates the Timer class so we can keep track of how much time has passed
class Timer:
    def __init__(self):
        # save the time when the timer is created
        self.event_time = floor((pg.time.get_ticks())/1000)
    def get_delta(self):
        # returns difference in time in seconds from time of instantiation to now
        return floor((pg.time.get_ticks())/1000) - self.event_time