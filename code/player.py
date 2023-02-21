import pygame
from support import import_folder
from settings import tile_size, screen_ratio

class Player(pygame.sprite.Sprite):

	def __init__(self, position, size):
		super().__init__()

		# Player image and animation
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.7
		self.image = self.animations['idle'][self.frame_index]
		self.size = size
		self.image = pygame.transform.scale(self.image, (self.size, self.size))	
		self.rect = self.image.get_rect(topleft = position)

		# Player movement
		self.direction = pygame.math.Vector2(0, 0)
		self.max_speed = int(screen_ratio * 8)
		self.current_speed = self.max_speed
		self.gravity = screen_ratio * 0.8
		self.jump_speed = screen_ratio * -18

		# Player status. Used for animations and tile collision
		self.status = 'idle'
		self.facing_right = True
		self.on_ground = False
		self.on_platform = False

		# Player's ability to move left/right. This is disabled when player
		# reaches the level boundaries
		self.can_move_left = True
		self.can_move_right = True

		# When player collides with enemy, game over is activated
		self.game_over = False


	# Import folder for storing images for animation
	def import_character_assets(self):
		character_path = '../graphics/player/'
		self.animations = {'idle': [], 'run': []}
		for animation in self.animations.keys():
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)


	# Animate player
	def animate(self):

		if self.game_over == False:
			animation = self.animations[self.status]

			# Loop over frame index
			self.frame_index += self.animation_speed
			if self.frame_index >= len(animation):
				self.frame_index = 0

			image = animation[int(self.frame_index)]
			image = pygame.transform.scale(image, (self.size, self.size))
			if self.facing_right:
				self.image = image
			else:
				flipped_image = pygame.transform.flip(image, True, False)
				self.image = flipped_image

		else:
			self.image = pygame.image.load('../graphics/player/dead.png').convert_alpha()
			self.image = pygame.transform.scale(self.image, (self.size, self.size))


	# Set keyboard input
	def get_input(self):
		keys = pygame.key.get_pressed()

		if keys[pygame.K_RIGHT] and self.game_over == False:
			if self.game_over == False:
				self.facing_right = True
				self.can_move_left = True
				if self.can_move_right:
					self.direction.x = 1
				else:
					self.direction.x = 0
			
		elif keys[pygame.K_LEFT] and self.game_over == False:
			if self.game_over == False:
				self.facing_right = False
				self.can_move_right = True
				if self.can_move_left:
					self.direction.x = -1
				else:
					self.direction.x = 0
		else:
			self.direction.x = 0

		if keys[pygame.K_SPACE] and self.on_ground == True and self.game_over == False:
			self.on_ground = False
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