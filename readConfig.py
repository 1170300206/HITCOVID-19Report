import configparser
import os

class ConfigReader(object):
    def __init__(self):
        self.parser = configparser.ConfigParser()
        self.parser.read(os.path.join(os.path.dirname(__file__), "config.txt"))

    def get(self, section, item):
        return self.parser[section][item]

if __name__ == "__main__":
    reader = ConfigReader()
    print(reader.get('DEFAULT', 'usr') == '1170300206')
