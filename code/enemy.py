import pygame
from tiles import Tile, AnimatedTile
from support import import_folder
from settings import screen_ratio

class Enemy(Tile):

	def __init__(self, width, height, x, y, direction, speed, surface):
		super().__init__(width, height, x, y)
		self.direction = direction
		self.speed = int(screen_ratio * speed)
		self.image = surface


	# Move enemy. If direction is 0 (horizontal), move along x axis.
	# If direction is 1 (vertical), move along y axis
	def move(self):
		if self.direction == 0:
			self.rect.x += self.speed
		elif self.direction == 1:
			self.rect.y += self.speed


	# Reverse enemy direction when they collide with constraints.
	# If enemy direction is horizontal, flip image
	def reverse_direction(self):
		self.speed *= -1
		if self.direction == 0:
			self.image = pygame.transform.flip(self.image, True, False)


	def update(self, shift):
		self.rect.x += shift
		self.move()


class AnimatedEnemy(Enemy):

	def __init__(self, width, height, x, y, direction, speed, surface, path_index):
		super().__init__(width, height, x, y, direction, speed, surface)
		self.path = '../graphics/enemies/' + str(path_index)
		self.frames = import_folder(self.path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.width = width
		self.height = height


	def animate(self):

		self.frame_index += 0.15
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]
		self.image = pygame.transform.scale(self.image, (self.width, self.height))
		print(self.direction)
		if self.speed > 0:
			self.image = pygame.transform.flip(self.image, True, False)



	def update(self, shift):
		self.rect.x += shift
		self.animate()
		self.move()
