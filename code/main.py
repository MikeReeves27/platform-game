import pygame, sys
from settings import *
from overworld import Overworld
from level import Level
from level_data import *

screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
clock = pygame.time.Clock()

# Set starting status to start overworld. Current level is none
status = 'start_overworld'
current_level = None
overworld = Overworld(screen, status)

# Create level object with default settings
level = Level(build_level(1), screen, status)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	# Check status in loop
	# 'Start overworld' creates the overworld object
	if status == 'start_overworld':
		overworld = Overworld(screen, status)
		status = 'overworld'

	# 'Overworld' runs the overworld loop
	elif status == 'overworld':
		screen.fill((0,0,0))
		overworld.run()

		# While in overworld, if the status changes, change it here too
		if overworld.status == 'start_level':
			status = 'start_level'
			current_level = build_level(overworld.level_counter + 1)

	# 'Start level' creates the desired level
	elif status == 'start_level':
		level = Level(current_level, screen, status)
		status = 'level'
	
	# 'Level' will run the level loop
	elif status == 'level':
		screen.fill(current_level['background'])
		level.run()

		# While in level, if the status changes, change it here too
		if level.status == 'start_overworld':
			status = 'start_overworld'

	pygame.display.update()
	clock.tick(60)