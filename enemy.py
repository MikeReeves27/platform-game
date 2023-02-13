import pygame
from tiles import Tile

class Enemy(Tile):

	def __init__(self, size, x, y, surface):
		super().__init__(size, x, y)
		self.image = surface
		self.speed = 3


	def move(self):
		self.rect.x += self.speed


	# Reverse enemy image
	def reverse(self):
		self.speed *= -1
		self.image = pygame.transform.flip(self.image, True, False)


	def update(self, shift):
		self.rect.x += shift
		self.move()

# class AnimatedEnemy(Enemy):
# 	def __init__(self, size, x, y):
# 		super().__init__(size, x, y, '/graphics/enemies/')

# 	def update(self, shift):
# 		self.rect.x += shift
# 		self.animate()
# 		self.move()
# 		self.reverse_image()
