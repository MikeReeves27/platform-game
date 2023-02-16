import pygame
from tiles import Tile, StaticTile, MovingTile, AnimatedTile
from settings import tile_size, screen_width, screen_height
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

		# Terrain setup
		terrain_layout = import_csv_layout(level_data['terrain'])
		self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

		# Terrain setup
		platform_layout = import_csv_layout(level_data['platforms'])
		self.platform_sprites = self.create_tile_group(platform_layout, 'platforms')

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

		# Corn count. This tracks the number of corn collected and the total number
		# available. The font will be used to display the score on the screen
		self.corn_count = 0
		self.corn_total = len(self.item_sprites.sprites())
		self.font = pygame.font.SysFont('Consolas', int(tile_size / 2))

	
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

					# If tile is platform, create a moving tile.
					elif type == 'platforms':
						image = pygame.image.load(f'../graphics/{type}/{val}.png').convert_alpha()
						image = pygame.transform.scale(image, (tile_size, tile_size))
						sprite = MovingTile(tile_size, x, y, image, int(val) % 2)

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
					
					# Make player slightly smaller than tile size. This is to prevent
					# random collision glitches. These occur when player enters a narrow
					# tunnel and can't jump
					print(y)
					sprite = Player((x, y), tile_size - int(tile_size / 6))
					self.player.add(sprite)
					#print(self.player.rect.y)

				# If tile value is 1, it's the level finish point (the portal)
				elif val == '1':
					sprite = AnimatedTile(tile_size, x, y, None, 'portal/')
					self.portal.add(sprite)


	# If enemy collides with constraint tile, enemy reverses direction
	def enemy_collision_reverse(self):
		for enemy in self.enemy_sprites.sprites():
			if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
				enemy.reverse_direction()


	# If moving platform collides with constraint tile, platform reverses direction
	def platform_collision_reverse(self):
		for platform in self.platform_sprites.sprites():
			if pygame.sprite.spritecollide(platform, self.constraint_sprites, False):
				platform.reverse_direction()


	# Used to scroll player and the surrounding world
	def scroll_x(self):
		player = self.player.sprite

		# If left side of player reaches left side of level, turn off player
		# left movement. Allow pixel buffer (this is because player is
		# updated before this function and can therefore slightly go off-screen)
		if player.rect.x <= self.total_world_shift + player.max_speed:
			player.can_move_left = False

		# If right side of player reaches right side of level, turn off player
		# right movement
		elif player.rect.right >= screen_width - player.max_speed:
			player.can_move_right = False

		# Shift screen left:
		# If center of player reaches center of screen, and player is facing left, and the world 
		# shift is not at zero (meaning the screen is not at its leftmost point), begin shifting 
		# world and keep player in center of screen
		elif player.rect.centerx < screen_width / 2 and player.direction.x < 0 and self.total_world_shift != 0:
			self.world_shift = player.max_speed
			player.current_speed = 0
			
		# Shift screen right:
		# Same as above function, but this instead checks that the length of the world minus the 
		# width of the screen is less than the total shift (meaning the screen is not at its
		# rightmost point)
		elif player.rect.centerx > screen_width - (screen_width / 2) and player.direction.x > 0 and abs(self.total_world_shift) < self.world_length - screen_width:
			self.world_shift = -player.max_speed
			player.current_speed = 0

		# Else, player must therefore be idle
		else:
			self.world_shift = 0
			player.current_speed = player.max_speed

		self.total_world_shift += self.world_shift


	# Check for horizontal collision between player and solid tiles
	def horizontal_movement_collision(self):
		player = self.player.sprite
		player.rect.x += player.direction.x * player.current_speed

		for sprite in self.terrain_sprites.sprites():

			# Draw black rectangle around each terrain tile
			pygame.draw.rect(self.display_surface, (0, 0, 0), sprite, 1)

			if sprite.rect.colliderect(player.rect):

				# Set player's left/right side to match that of the
				# the tile they've just collided with
				if player.direction.x < 0:
					player.rect.left = sprite.rect.right
					if player.direction.y > 0:
						player.on_ground = False

				elif player.direction.x > 0:
					player.rect.right = sprite.rect.left
					if player.direction.y > 0:
						player.on_ground = False


	# Check for vertical collision between player and solid tiles
	def vertical_movement_collision(self):
		player = self.player.sprite
		player.apply_gravity()

		for sprite in self.terrain_sprites.sprites():

			if sprite.rect.colliderect(player.rect):

				# If player lands on tile, set player's y movement to 0
				# Set on_ground to True so that they can jump again
				if player.direction.y > 0:
					player.rect.bottom = sprite.rect.top
					player.direction.y = 0
					player.on_ground = True

				# If player hits tile from underneath, set player's
				# y movement to 0
				elif player.direction.y < 0:
					player.rect.top = sprite.rect.bottom
					player.direction.y = 0

	# Check for collision between player and moving platforms
	def platform_collision(self):
		player = self.player.sprite

		for sprite in self.platform_sprites.sprites():

			# Draw black rectangle around each terrain tile
			pygame.draw.rect(self.display_surface, (0, 0, 0), sprite, 1)

			if sprite.rect.colliderect(player.rect):
				
				# In each collision (left, right, top, bottom), allow
				# a 1/3 tile-buffer to account for the moving tile. This
				# is because the tiles move faster than the update()
				# functions are called, causing player to sometimes
				# warp through tile
				if abs(player.rect.left - sprite.rect.right) < tile_size / 3:
					player.rect.left = sprite.rect.right

				elif abs(player.rect.right - sprite.rect.left) < tile_size / 3:
					player.rect.right = sprite.rect.left

				# Add 2 to player's y direction so that they bounce off
				# tile after colliding with it from underneath
				elif abs(player.rect.top - sprite.rect.bottom) < tile_size / 3:
					player.direction.y += 2
					player.rect.top = sprite.rect.bottom

				# When player lands on moving platform
				elif abs(player.rect.bottom - sprite.rect.top) < tile_size / 3:
					player.direction.y = 0
					player.on_ground = True

					# If platform is horizontally moving, match player's
					# rect.x position with tile's speed so that player
					# remains standing on it
					if sprite.direction == 0:
						player.rect.x += sprite.speed

					# If platform is vertically moving, allow 1 and 3 pixels
					# depending on its direction so that player remains
					# standing smoothly on it. Without that, player will shake
					elif sprite.direction == 1:

						if sprite.speed > 0:
							player.rect.bottom = sprite.rect.top + sprite.speed + 1
						
						elif sprite.speed < 0:
							player.rect.bottom = sprite.rect.top + sprite.speed + 3


	# Check for collision between player and items such as corn
	def item_collision(self):
		player = self.player.sprite
		for sprite in self.item_sprites.sprites():
			if sprite.rect.colliderect(player.rect):
				sprite.kill()
				self.corn_count += 1


	# Check for collision between player and enemies
	def enemy_collision(self):
		player = self.player.sprite

		# If player falls off screen, it's game over
		if player.rect.top > screen_height:
			player.game_over = True
			print('Game over')

		# If player collides with enemy, it's game over
		else:
			for sprite in self.enemy_sprites.sprites():
				if sprite.rect.colliderect(player.rect):
					player.game_over = True
					player.speed = 0


	# Check for collision between player and portal
	def portal_collision(self):
		player = self.player.sprite
		if self.portal.sprite.rect.colliderect(player.rect):
			print('victory')


	# Draw player's current score in top-left corner of screen
	def draw_inventory(self):
		image = pygame.image.load('../graphics/items/0.png').convert_alpha()
		image = pygame.transform.scale(image, (32, 32))
		self.display_surface.blit(image, (image.get_width() / 2, image.get_height() / 2))
		score = str(self.corn_count) + '/' + str(self.corn_total)
		score_display = self.font.render(score, True, (0, 0, 0))
		self.display_surface.blit(score_display, (tile_size + image.get_width() / 2, image.get_height() / 2))


	# Main level function for looping through all sprite and tile updates,
	# as well as drawing all images to screen
	def run(self):
		
		# Draw terrain and file tiles
		self.terrain_sprites.update(self.world_shift)
		self.terrain_sprites.draw(self.display_surface)
		self.platform_sprites.update(self.world_shift)
		self.platform_sprites.draw(self.display_surface)
		self.platform_collision_reverse()
		self.fill_sprites.update(self.world_shift)
		self.fill_sprites.draw(self.display_surface)

		# Draw black rectangle around each fill tile
		for sprite in self.fill_sprites.sprites():
			pygame.draw.rect(self.display_surface, (0, 0, 0), sprite, 1)

		# Draw item tiles and check for collision
		self.item_sprites.update(self.world_shift)
		self.item_sprites.draw(self.display_surface)
		self.item_collision()

		# Draw portal tile and check for collision. Only draw portal
		# once all corn is collected
		self.portal.update(self.world_shift)
		if self.corn_count == self.corn_total:
			self.portal.draw(self.display_surface)
			self.portal_collision()

		# Update/draw player, scroll screen, check for tile collision
		self.player.update()
		self.scroll_x()
		self.horizontal_movement_collision()
		self.vertical_movement_collision()
		self.platform_collision()
		self.player.draw(self.display_surface)

		# Update/draw enemies and check for constraint collision
		self.enemy_sprites.update(self.world_shift)
		self.constraint_sprites.update(self.world_shift)
		self.enemy_collision_reverse()
		self.enemy_sprites.draw(self.display_surface)
		self.enemy_collision()

		# Draw score on screen
		self.draw_inventory()