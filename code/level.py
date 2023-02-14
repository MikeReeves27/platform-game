import pygame
from tiles import Tile, StaticTile
from settings import tile_size, screen_width
from player import Player
from support import import_csv_layout
from enemy import Enemy, AnimatedEnemy
from enemy_data import enemy_list

class Level:

	def __init__(self, level_data, surface):

		# Level setup
		self.display_surface = surface
		self.level_data = level_data

		# World shift variables. Used for determining if player reaches
		# end of the screen
		self.world_length = 0
		self.world_shift = 0
		self.total_world_shift = 0
		
		# Player and portal setup
		player_layout = import_csv_layout(level_data['player'])
		self.player = pygame.sprite.GroupSingle()
		self.portal = pygame.sprite.GroupSingle()
		self.player_setup(player_layout)
		self.current_x = None

		# Terrain setup
		terrain_layout = import_csv_layout(level_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

		# Fill setup. Used for filling screen with tiles that look solid but
		# are only used for fill, so that needless collision calls aren't used
		fill_layout = import_csv_layout(level_data['fill'])
		self.fill_sprites = self.create_tile_group(fill_layout, 'fill')

		# Items setup (eg, corn)
		item_layout = import_csv_layout(level_data['items'])
		self.item_sprites = self.create_tile_group(item_layout, 'items')

		# Enemy setup
		enemy_layout = import_csv_layout(level_data['enemies'])
		self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

		# Constraints. Used for setting enemy movement to a specific path
		constraint_layout = import_csv_layout(level_data['constraints'])
		self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraint')

	
	def create_tile_group(self, layout, type):
		sprite_group = pygame.sprite.Group()
		self.world_length = len(layout[0] * tile_size)

		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):

				# If tile value is -1, it's an empty tile (eg, sky)
				if val != '-1':
					x = col_index * tile_size
					y = row_index * tile_size

					# If tile is terrain or item, create a static tile.
					if type == 'terrain' or type == 'items':
						image = pygame.image.load(f'../graphics/{type}/{val}.png').convert_alpha()
						image = pygame.transform.scale(image, (tile_size, tile_size))
						sprite = StaticTile(tile_size, x, y, image)

					# If tile is fill, create static tile using the image specified in level_data
					elif type == 'fill':
						image = pygame.image.load(self.level_data['fill_image']).convert_alpha()
						image = pygame.transform.scale(image, (tile_size, tile_size))
						sprite = StaticTile(tile_size, x, y, image)

					# If tile is enemy, create an enemy tile
					elif type == 'enemies':

						# If enemy data value is 0, load static sprite
						if enemy_list[int(val)][0] == 0:
							image = pygame.image.load(f'../graphics/{type}/{val}.png').convert_alpha()
							image = pygame.transform.scale(image, (tile_size, tile_size))
							sprite = Enemy(tile_size, x, y, enemy_list[int(val)][1], enemy_list[int(val)][2], image)

						# If enemy data value is 1, load animated sprite
						elif enemy_list[int(val)][0] == 1:
							sprite = AnimatedEnemy(tile_size, x, y, enemy_list[int(val)][1], enemy_list[int(val)][2], None, int(val))

					# If tile is constraint, create a blank, imageless tile
					elif type == 'constraint':
						sprite = Tile(tile_size, x, y)

					sprite_group.add(sprite)
		
		return sprite_group


	def player_setup(self, layout):
		for row_index, row in enumerate(layout):
			for col_index, val in enumerate(row):
				x = col_index * tile_size
				y = row_index * tile_size

				# If tile value is 0, it's the player starting point
				if val == '0':
					sprite = Player((x, y), self.display_surface)
					self.player.add(sprite)

				# If tile value is 1, it's the level finish point (the portal)
				elif val == '1':
					portal_image = pygame.image.load('../graphics/world/portal.png').convert_alpha()
					sprite = StaticTile(tile_size, x, y, portal_image)
					self.portal.add(sprite)


	# If enemy collides with constraint tile, enemy reverses direction
	def enemy_collision_reverse(self):
		for enemy in self.enemy_sprites.sprites():
			if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
				enemy.reverse_direction()


	# Used to scroll player and the surrounding world
	def scroll_x(self):
		player = self.player.sprite
		direction_x = player.direction.x

		# If left side of player reaches left side of level, turn off player
		# left movement. Allow 8 pixel buffer (this is because player is
		# updated before this function and can therefore slightly go off-screen)
		if player.rect.x <= self.total_world_shift + 8:
			player.can_move_left = False

		# If right side of player reaches right side of level, turn off player
		# right movement
		elif player.rect.right >= screen_width - 8:
			player.can_move_right = False

		# Shift screen right:
		# If center of player reaches center of screen, and player is facing left, and the world 
		# shift is not at zero (meaning the screen is not at its leftmost point), begin shifting 
		# world and keep player in center of screen
		elif player.rect.centerx < screen_width / 2 and direction_x < 0 and self.total_world_shift != 0:
			self.world_shift = 8
			player.speed = 0
			
		# Shift screen left:
		# Same as above function, but this instead checks that the length of the world minus the 
		# width of the screen is less than the total shift (meaning the screen is not at its
		# rightmost point)
		elif player.rect.centerx > screen_width - (screen_width / 2) and direction_x > 0 and abs(self.total_world_shift) < self.world_length - screen_width:
			self.world_shift = -8
			player.speed = 0

		# Else, player must therefore be idle
		else:
			self.world_shift = 0
			player.speed = 8

		self.total_world_shift += self.world_shift


	# Check for horizontal collision between player and solid tiles
	def horizontal_movement_collision(self):
		player = self.player.sprite
		player.rect.x += player.direction.x * player.speed

		for sprite in self.terrain_sprites.sprites():
			if sprite.rect.colliderect(player.rect):
				if player.direction.x < 0: 
					player.rect.left = sprite.rect.right
					player.on_left = True
					self.current_x = player.rect.left
				elif player.direction.x > 0:
					player.rect.right = sprite.rect.left
					player.on_right = True
					self.current_x = player.rect.right

		if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
			player.on_left = False
		if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
			player.on_right = False


	# Check for vertical collision between player and solid tiles
	def vertical_movement_collision(self):
		player = self.player.sprite
		player.apply_gravity()

		for sprite in self.terrain_sprites.sprites():
			if sprite.rect.colliderect(player.rect):
				if player.direction.y > 0:
					player.rect.bottom = sprite.rect.top
					player.direction.y = 0
					player.on_ground = True
				elif player.direction.y < 0:
					player.rect.top = sprite.rect.bottom
					player.direction.y = 0
					player.on_ceiling = True

		if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
			player.on_ground = False
		if player.on_ceiling and player.direction.y > 0.1:
			player.on_ceiling = False


	# Check for collision between player and items such as corn
	def item_collision(self):
		player = self.player.sprite
		for sprite in self.item_sprites.sprites():
			if sprite.rect.colliderect(player.rect):
				sprite.kill()


	# Check for collision between player and enemies
	def enemy_collision(self):
		player = self.player.sprite
		for sprite in self.enemy_sprites.sprites():
			if sprite.rect.colliderect(player.rect):
				#player.kill()
				print('game over')


	# Check for collision between player and portal
	def portal_collision(self):
		player = self.player.sprite
		if self.portal.sprite.rect.colliderect(player.rect):
			print('victory')


	# Main level function for looping through all sprite and tile updates,
	# as well as drawing all images to screen
	def run(self):
		
		# Draw terrtain and file tiles
		self.terrain_sprites.update(self.world_shift)
		self.terrain_sprites.draw(self.display_surface)
		self.fill_sprites.update(self.world_shift)
		self.fill_sprites.draw(self.display_surface)

		# Draw item tiles and check for collision
		self.item_sprites.update(self.world_shift)
		self.item_sprites.draw(self.display_surface)
		self.item_collision()

		# Draw portal tile and check for collision
		self.portal.update(self.world_shift)
		self.portal.draw(self.display_surface)
		self.portal_collision()

		# Update/draw player, scroll screen, check for tile collision
		self.player.update()
		self.scroll_x()
		self.horizontal_movement_collision()
		self.vertical_movement_collision()
		self.player.draw(self.display_surface)
		
		# Update/draw enemies and check for constraint collision
		self.enemy_sprites.update(self.world_shift)
		self.constraint_sprites.update(self.world_shift)
		self.enemy_collision_reverse()
		self.enemy_sprites.draw(self.display_surface)
		self.enemy_collision()