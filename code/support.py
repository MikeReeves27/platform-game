from os import walk
from settings import tile_size
from csv import reader
import pygame


# Import a folder of images to be used for animations
def import_folder(path):
	surface_list = []

	for _, __, image_files in walk(path):
		#print(image_files)
		for image in image_files:
			full_path = path + '/' + image
			image_surface = pygame.image.load(full_path).convert_alpha()
			image_surface = pygame.transform.scale(image_surface, (tile_size, tile_size))
			surface_list.append(image_surface)

	return surface_list


# Import level .csv data and convert it to terrain map
def import_csv_layout(path):
	terrain_map = []
	with open(path) as map:
		level = reader(map, delimiter = ',')
		for row in level:
			terrain_map.append(list(row))
		return terrain_map
