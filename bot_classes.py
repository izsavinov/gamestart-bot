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

    def player_details_for_latest_match(self, player_id=None, massive_playerid=None):
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
        list_nick = []
        max_kd_ratio, max_kills, max_headshots, max_mvps, max_assists = 0, 0, 0, 0, 0
        if response.status_code == 200:
            for team_index in range(0, 2):
                for gamer_index in range(0, 5):
                    playerid = teams[team_index]["players"][gamer_index]["player_id"]  # player_id с фэйсит
                    if playerid in massive_playerid:
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
                                     nickname + ":" + '\nKills: ' + kills + '\nAssists: ' + assists +
                                     '\nDeath: ' + deaths + '\nK/R Ratio: ' + K_R_Ratio +
                                     '\nK/D Ratio: ' + K_D_Ratio + '\nMVPs: ' + MVPs + '\nHeadshots: ' + headshots + '\n\n')
                        list_nick.append(nickname)
                        if(float(K_D_Ratio) > max_kd_ratio):
                            nick_max_kd_ratio = nickname
                            max_kd_ratio = float(K_D_Ratio)
                        if(int(kills) > max_kills):
                            nick_max_kills = nickname
                            max_kills = int(kills)
                        if(int(headshots) > max_headshots):
                            nick_max_headshots = nickname
                            max_headshots = int(headshots)
                        if(int(MVPs) > max_mvps):
                            nick_max_mvps = nickname
                            max_mvps = int(MVPs)
                        if(int(assists) > max_assists):
                            nick_max_assists = nickname
                            max_assists = int(assists)
                if counter > -1:
                    break
        else:
            return None
        return list_nick, stata, nick_max_kd_ratio, max_kd_ratio, nick_max_kills, max_kills, nick_max_headshots, max_headshots, nick_max_mvps, max_mvps, nick_max_assists, max_assists

    def player_stats(self, player_id=None):
        """
            Функция возвращает общую статистику в фйэсит
        """
        api_url = "{}/players/{}/stats/{}".format(
            self.base_url, player_id, 'csgo')

        response = requests.get(api_url, headers=self.headers)
        data = response.json()
        stats = data['lifetime']
        if response.status_code == 200:
            avg_headshots = stats['Average Headshots %']
            total_headshots = stats['Total Headshots %']
            win_rate = stats['Win Rate %']
            longest_win_streak = stats['Longest Win Streak']
            wins = stats['Wins']
            matches = stats['Matches']
            kd_ratio = stats['K/D Ratio']
            current_win_streak = stats['Current Win Streak']
            avg_kt_ratio = stats['Average K/D Ratio']
            text = "Общая статистика в матчах у вас следующие:" + '\nAverage Headshots %: ' + avg_headshots + '\nTotal Headshots %: ' + total_headshots \
                   + '\nWin Rate %: ' + win_rate + '\nLongest Win Streak: ' + longest_win_streak + '\nWins: ' + wins + '\nMatches: ' + matches + \
                   '\nK/D Ratio: ' + kd_ratio + '\nCurrent Win Streak: ' + current_win_streak + '\nAverage K/D Ratio: ' + avg_kt_ratio
            return text
        else:
            return None
