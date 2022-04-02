import json
from os import environ


class Config:
    def __init__(self, filename):
        """Формирование словаря с конфигурацией из файла и переменных среды."""
        with open(filename) as f:
            self.config = json.load(f)
        self.config = environ | self.config

    def dump(self, filename):
        """Выгрузка конфигурации в .json-файл."""
        with open(filename, 'w+') as f:
            json.dump(self.config, f)
