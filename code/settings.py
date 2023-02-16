import pygame, sys

# Pygame setup
pygame.init()

# Set number of vertical tiles in game
vertical_tile_number = 14

# Retrieve window height from system
window_height = pygame.display.Info().current_h

# Set tile size to match window height. Allow a buffer of 2 tiles for window
tile_size = int(window_height / (vertical_tile_number + 2))
screen_height = tile_size * vertical_tile_number

# Set screen width to be double the height
screen_width = screen_height * 2

# Set screen ratio. This will used to scale all elements in game depending on
# the size of user's screen
screen_ratio = tile_size / 64
