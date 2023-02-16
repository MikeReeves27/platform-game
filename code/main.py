import pygame, sys
from settings import *
from level import Level
from level_data import level_0, level_1

# Pygame setup

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
clock = pygame.time.Clock()
level = Level(level_1, screen)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	screen.fill(level_1['background'])
	level.run()

	pygame.display.update()
	clock.tick(60)