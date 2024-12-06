import json

def loadConfig(config):
	file = ''
	if config == 'local_config':
		file = open('./conf/local_config.json', 'r')
	elif config == 'ignore_config':
		file = open('./conf/ignore_config.json', 'r')
	else:
		print('[Error] config: {} not found!'.format(config))
		return -1

	data = json.loads(file.read())
	file.close()
	return data