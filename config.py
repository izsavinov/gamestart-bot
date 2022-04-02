import json
from os import environ


class Config:
    def __init__(self, filename):
        with open(filename) as f:
            self.config = json.load(f)
        self.config = environ | self.config

    def get_config(self):
        return self.config

    def dump(self, filename):
        with open(filename, 'w+') as f:
            json.dump(self.config, f)
