import pygame
from support import import_folder

class Player(pygame.sprite.Sprite):

	def __init__(self, position, size):
		super().__init__()

		# Player image and animation
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.7
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(topleft = position)

		# Player movement
		self.direction = pygame.math.Vector2(0, 0)
		self.speed = 8
		self.gravity = 0.8
		self.jump_speed = -16

		# Player status. Used for animations and tile collision
		self.status = 'idle'
		self.facing_right = True
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False

		# Player's ability to move left/right. This is disabled when player
		# reaches the level boundaries
		self.can_move_left = True
		self.can_move_right = True


	# Import folder for storing images for animation
	def import_character_assets(self):
		character_path = './graphics/player/'
		self.animations = {'idle': [], 'run': []}
		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)


	# Animate player
	def animate(self):
		animation = self.animations[self.status]

		# Loop over frame index
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]
		if self.facing_right:
			self.image = image
		else:
			flipped_image = pygame.transform.flip(image, True, False)
			self.image = flipped_image

		# Set rectangle. Used for more accurate collision detection
		if self.on_ground and self.on_right:
			self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
		elif self.on_ground and self.on_left:
			self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
		elif self.on_ground:
			self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
		elif self.on_ceiling and self.on_right:
			self.rect = self.image.get_rect(topright = self.rect.topright)
		elif self.on_ceiling and self.on_left:
			self.rect = self.image.get_rect(topleft = self.rect.topleft)
		elif self.on_ceiling:
			self.rect = self.image.get_rect(midtop = self.rect.midtop)


	# Set keyboard input
	def get_input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_RIGHT]:
			self.facing_right = True
			self.can_move_left = True
			if self.can_move_right:
				self.direction.x = 1
			else:
				self.direction.x = 0
			
		elif keys[pygame.K_LEFT]:
			self.facing_right = False
			self.can_move_right = True
			if self.can_move_left:
				self.direction.x = -1
			else:
				self.direction.x = 0
		else:
			self.direction.x = 0

		if keys[pygame.K_SPACE] and self.on_ground:
			self.jump()


	# Set character status. Used for determining correct animation
	def get_status(self):
		if self.direction.x != 0:
			self.status = 'run'
		else:
			self.status = 'idle'


	def apply_gravity(self):
		self.direction.y += self.gravity
		self.rect.y += self.direction.y


	def jump(self):
		self.direction.y = self.jump_speed


	def update(self):
		self.get_input()
		self.get_status()
		self.animate()