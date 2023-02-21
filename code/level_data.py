
def build_level(value):

	level = {
		'terrain': f'../levels/{value}/level_{value}_terrain.csv',
		'platforms': f'../levels/{value}/level_{value}_platforms.csv',
		'fill': f'../levels/{value}/level_{value}_fill.csv',
		'player': f'../levels/{value}/level_{value}_player.csv',
		'items': f'../levels/{value}/level_{value}_items.csv',
		'enemies': f'../levels/{value}/level_{value}_enemies.csv',
		'constraints': f'../levels/{value}/level_{value}_constraints.csv',
	}

	# Levels 1-5: Hilly-verse. Background: Sky blue. Fill image: grass
	if value >= 1 and value <= 5:
		level.update({'background': (153, 217, 234), 'fill_image': '../graphics/terrain/1.png'})

	# Levels 6-10: Beachy. Background: Sky blue. Fill image: sand
	elif value >= 6 and value <= 10:
		level.update({'background': (153, 217, 234), 'fill_image': '../graphics/terrain/2.png'})

	return level