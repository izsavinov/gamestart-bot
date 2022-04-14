import requests
from config import Config
from sys import argv

config = Config(argv[1]).config

class statsdata:
    """Данные полученные с помощью API FACEIT"""

    def __init__(self, api_id, url_base):
        """В этой функции заполняем парметры headers для cURL и инициализируем base_url и api_token
        """

        self.api_token = api_id
        self.base_url = url_base

        self.headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.api_token)
        }

    def player_details(self, nickname=None):
        """В эту функцию передаем параметры nickname от аккаунта в FACEIT и game_player_id от аккаунта в CS:GO.
           Функция возвращает статистику последнего матча.
        """
        # Получим player_id
        api_url = "{}/players".format(self.base_url)
        if nickname != None:
            api_url += "?nickname={}".format(nickname)
        res = requests.get(api_url, headers=self.headers)
        data = res.json()
        if res.status_code == 200:
            player_id = data["player_id"]
        else:
            return None

        # Получим последний match_id
        api_url = "{}/players/{}/history".format(self.base_url, player_id)
        api_url += "?game={}&offset={}&limit={}".format(config["game"], 0, 1)
        response = requests.get(api_url, headers=self.headers)
        data = response.json()
        if response.status_code == 200:
            match_id = data["items"][0]["match_id"]
        else:
            return None
        # Получим статистику матча
        api_url = "{}/matches/{}/stats".format(self.base_url, match_id)
        response = requests.get(api_url, headers=self.headers)
        data = response.json()
        teams = data["rounds"][0]["teams"]
        counter = -1
        stata = []
        if response.status_code == 200:
            for team_index in range(0, 2):
                for gamer_index in range(0, 5):
                    nick = teams[team_index]["players"][gamer_index]["nickname"]  # никнейм с фэйсит
                    if nick == nickname:
                        gamer_index_for_stats = teams[team_index]["players"][gamer_index]
                        counter += 1
                        kills = gamer_index_for_stats["player_stats"]["Kills"]
                        assists = gamer_index_for_stats["player_stats"]["Assists"]
                        deaths = gamer_index_for_stats["player_stats"]["Deaths"]
                        K_R_Ratio = gamer_index_for_stats["player_stats"]["K/R Ratio"]
                        MVPs = gamer_index_for_stats["player_stats"]['MVPs']
                        headshots = gamer_index_for_stats["player_stats"]['Headshots']
                        K_D_Ratio = gamer_index_for_stats["player_stats"]["K/D Ratio"]

                        stata.append('Kills:' + kills)
                        stata.append('Assists: ' + assists)
                        stata.append('Death: ' + deaths)
                        stata.append('K/R Ratio: ' + K_R_Ratio)
                        stata.append('K/D Ratio: ' + K_D_Ratio)
                        stata.append('MVPs: ' + MVPs)
                        stata.append('Headshots: ' + headshots)
                if counter > -1:
                    break
        else:
            return None
        return stata
