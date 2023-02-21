import pygame
from support import import_folder
from settings import screen_ratio

class Tile(pygame.sprite.Sprite):

	def __init__(self, width, height, x, y):
		super().__init__()
		self.image = pygame.Surface((width, height))
		self.rect = self.image.get_rect(topleft = (x, y))


	def update(self, x_shift):
		self.rect.x += x_shift


class StaticTile(Tile):
	
	def __init__(self, width, height, x, y, surface):
		super().__init__(width, height, x, y)
		self.image = surface


class MovingTile(Tile):
	
	def __init__(self, width, height, x, y, surface, direction):
		super().__init__(width, height, x, y)
		self.image = surface
		self.direction = direction
		self.speed = int(screen_ratio * 3)


	def move(self):
		if self.direction == 0:
			self.rect.x += self.speed
		elif self.direction == 1:
			self.rect.y += self.speed


	def reverse_direction(self):
		self.speed *= -1


	def update(self, shift):
		self.rect.x += shift
		self.move()


class AnimatedTile(Tile):

	def __init__(self, width, height, x, y, surface, path_index):
		super().__init__(width, height, x, y)
		self.path = '../graphics/' + str(path_index)
		self.frames = import_folder(self.path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]


	def animate(self):
		self.frame_index += 0.15
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]


	def update(self, shift):
		self.rect.x += shift
		self.animate()
