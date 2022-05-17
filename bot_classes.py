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

    def player_details(self, player_id=None, massive_playerid=None):
        """В эту функцию передаем параметры nickname от аккаунта в FACEIT и game_player_id от аккаунта в CS:GO.
           Функция возвращает статистику последнего матча.
        """
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
                    playerid = teams[team_index]["players"][gamer_index]["player_id"]  # player_id с фэйсит
                    j = 0  # счетчик для массива из базы данных
                    if playerid in massive_playerid[j]:
                        gamer_index_for_stats = teams[team_index]["players"][gamer_index]
                        counter += 1
                        kills = gamer_index_for_stats["player_stats"]["Kills"]
                        assists = gamer_index_for_stats["player_stats"]["Assists"]
                        deaths = gamer_index_for_stats["player_stats"]["Deaths"]
                        K_R_Ratio = gamer_index_for_stats["player_stats"]["K/R Ratio"]
                        MVPs = gamer_index_for_stats["player_stats"]['MVPs']
                        headshots = gamer_index_for_stats["player_stats"]['Headshots']
                        K_D_Ratio = gamer_index_for_stats["player_stats"]["K/D Ratio"]
                        nickname = teams[team_index]["players"][gamer_index]["nickname"]
                        stata.append(
                            nickname + ':\nKills:' + kills + '\nAssists: ' + assists + '\nDeath: ' + deaths + '\nK/R Ratio: ' + K_R_Ratio +
                            '\nK/D Ratio: ' + K_D_Ratio + '\nMVPs: ' + MVPs + '\nHeadshots: ' + headshots)
                        j += 1
                if counter > -1:
                    break
        else:
            return None
        return stata
