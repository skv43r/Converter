from configparser import ConfigParser
import os



class Config():

	config_path = "config.ini"
	configparser = ConfigParser(allow_no_value = True)
	configparser.add_section('Settings')

	@staticmethod
	def load():
		if not os.path.exists(Config.config_path):
			with open(Config.config_path,"a+") as f:
				f.close()
		Config.configparser.read(Config.config_path)

	@staticmethod
	def get(section, name):

		Config.configparser.read(Config.config_path)
		try:
			result = Config.configparser.get(section, name)
			return result
		except:
			return False

	@staticmethod
	def set(section, name, value):
		Config.configparser.read(Config.config_path)
		Config.configparser.set(section, name, value)
		with open(Config.config_path, "w") as file:
			Config.configparser.write(file)
  