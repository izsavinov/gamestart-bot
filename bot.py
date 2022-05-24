from discord.ext import commands
import datetime
import asyncio
import database
from bot_classes import statsdata
from sys import argv
from config import Config
import requests
import psycopg2

config = Config(argv[1]).config
client = commands.Bot(command_prefix=config['prefix'])
url_base = config['url_base']


@client.event
async def on_ready():
    """Сообщение о подключении бота."""
    print('BOT connected')


@client.command(pass_context=True)
async def hello(ctx):
    """Приветствие пользователя по команде в Discord."""
    await ctx.send(config['greeting'])

@client.command(pass_context=True)
async def help(ctx):
    """Инструкция по пользованию ботом"""
    await ctx.send('1')
    await ctx.send('Добро пожаловать в GameStart!!! Здесь вы узнаете как пользоваться этим ботом. Для начала, вы должны быть зар'
                   'егистрированы в сервисе FaceIT. Чтобы вызывать'
                   'команды, вам необходимо прописать точку(".") и потом только вводить команду.\n'
                   'Список команд:\n1.register - команда для регистрации в бота. Необходимо'
                   'ввести эту команду, затем ник вашего аккаунта в FaceIT\n'
                   '2.reminder - команда, которая напоминает о предстоящих матчах. Для того, чтобы напоминалка'
                   'заработала, необходимо ввести команду reminder, а затем через пробел ввести время в формате d-H-M-S'
                   '(Например "21-17:03:30"). Эта команда напомнит вам о предстоящем матче за день, за 15 минут, и'
                   'в момент начала вашего матча.\n'
                   '3.get_match_stats - команда, которая позволяет узнать статистику вашего последнего матча.\n'
                   '4.total_FI_stats - команда, которая позовляет узнать вашу общую статистику ваших матчей, в которые'
                   'вы заходили через FaceIT.\n'
                   '5. delete_my_account - так как в одном сервере, один пользователь может регистрировать только один'
                   'аккаунт, то эта команда позволяет удалить текущий аккаунт, и зарегистрировать новый.')

@client.command(pass_context=True)
async def reminder(ctx, message: str):
    """Напоминалка о начале матча, на вход передается день, часы, минуты, секунды начала матча. Сообщение о начале
    матча приходит за 15 минут и в момент, на который была запланирована игра"""
    datepattern = '%d-%H:%M:%S'  # Строковый тип
    gamedata = message
    time_now = datetime.datetime.now()
    try:
        date = datetime.datetime.strptime(gamedata, datepattern)
    except:
        pass
    # Добавляем 3 часа из-за европейского времени
    deltadate = (date.day * 24 * 3600 + date.hour * 3600 + date.minute * 60 + date.second - 3 * 3600) - (
            time_now.day * 24 * 3600
            + time_now.hour * 3600 + time_now.minute * 60 + time_now.second)
    if(deltadate - 24 * 60 * 60 > 0):
        await asyncio.sleep(deltadate - 24 * 60 * 60 + 2)
        await ctx.send('Напоминаю, что ровно через день вы запланировали матч')
    if (deltadate - 15 * 60 > 0):
        await asyncio.sleep(deltadate - 15 * 60 + 2)
        await ctx.send('Приготовьтесь! Через 15 минут начинаем')
    if (deltadate > 0):
        await asyncio.sleep(deltadate)
        await ctx.send('Начинаем!!! Переходите по ссылке https://www.faceit.com/ru/dashboard')


@client.command(pass_context=True)
async def register(ctx, nickFI: str):
    """
        Пользователь предоставляет нам информацию о своем аккаунте FACEIT, а именно - никнейм
    """
    # Получим player_id
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(config['APIID'])
    }
    api_url = "{}/players".format(url_base)
    api_url += "?nickname={}".format(nickFI)
    res = requests.get(api_url, headers=headers)
    data = res.json()
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    if (conn):
        if (res.status_code == 200):
            player_id = data["player_id"]
            query = """ SELECT id_chanell_discord, player_id 
                        FROM playersid 
                        WHERE id_chanell_discord = %s AND ID_discord = %s;"""
            try:
                cursor.execute(query, (str(ctx.guild.id), str(ctx.author.id)))
            except psycopg2.Error as err:
                await ctx.send(err)
            found_users = cursor.fetchall()
            if (len(found_users) == 0):
                try:
                    cursor.execute(
                        """INSERT INTO playersid (ID_chanell_discord, ID_discord, player_id) VALUES (%s, %s, %s);""",
                        (str(ctx.guild.id), str(ctx.author.id), str(player_id)))
                except psycopg2.Error as err:
                    await ctx.send(err)
                conn.commit()
                await ctx.send('Успешно зарегистрированы!')
            else:
                await ctx.send(
                    'Вы уже регистрировались на этом канале! Можете удалить свой аккаунт командой .delete_my_account и поменять аккаунт')
        else:
            await ctx.send('Такого никнейма в FACEIT не найдено')
    else:
        await ctx.send('Неполадки с базой данных')


@client.command(pass_context=True)
async def table_contents(ctx):
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    query = " SELECT * FROM playersid;"
    cursor.execute(query)
    massive = cursor.fetchall()
    for i in range(len(massive)):
        await ctx.send(massive[i])
    cursor.close()
    conn.close()


@client.command(pass_context=True)
async def get_match_stats(ctx):
    """Выводит статистику"""
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    # Получим player_id всех игроков из выбранного канала в дискорде
    query = """SELECT player_id
               FROM playersid
               WHERE id_chanell_discord = %s;"""
    try:
        cursor.execute(query, (str(ctx.guild.id),))
    except psycopg2.Error as err:
        await ctx.send("Не удалось подключиться к базе данных")
    found_playersid = cursor.fetchall()

    # Получим player_id игрока, который вызвал команду .get_mathch_stats
    query = """SELECT player_id
                   FROM playersid
                   WHERE id_chanell_discord = %s AND ID_discord = %s;"""
    try:
        cursor.execute(query, (str(ctx.guild.id), str(ctx.author.id)))
    except psycopg2.Error as err:
        await ctx.send("Не удалось подключиться к базе данных")
    found_playerid = cursor.fetchall()

    if (len(found_playerid) != 0):
        massive_playersid = []
        for i in range(0, len(found_playersid)):
            massive_playersid.append(found_playersid[i][0])
        statsdata_obj = statsdata(config['APIID'], config['url_base'])
        player_id, nick_max_kd_ratio, max_kd_ratio, nick_max_kills, max_kills, nick_max_headshots, max_headshots, nick_max_mvps, max_mvps, nick_max_assists, max_assists\
            = statsdata.player_details_for_latest_match(statsdata_obj, found_playerid[0][0], massive_playersid)
        for i in range(0, len(player_id)):
            await ctx.send(player_id[i])
        await ctx.send('Итоги последнего матча:\n Самым эффективным игроком стал ' + nick_max_kd_ratio + ' с kd_ratio, равное ' + str(max_kd_ratio) +
                       '.\nБольше всех киллов сделал игрок ' + nick_max_kills + ', всего: ' + str(max_kills) + '.\nГлавной звездой стал ' +
                       nick_max_mvps + '. Всего у него MVP: ' + str(max_mvps) + '.\nЛучшим помощником оказался ' + nick_max_assists + ' всего ассистов у него: '
                       + str(max_assists) + '.\nИ наконец, больше всех в голову настрелял ' + nick_max_headshots + ', количество headshots равно ' + str(max_headshots))
    else:
        await ctx.send('Вы не регистрировали свой аккаунт')
    cursor.close()
    conn.close()

@client.command(pass_context=True)
async def total_FI_stats(ctx):
    """Получение общей статистики игрока за матчи, в которые он заходил через платформу FaceIT"""
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    query = """SELECT player_id
                       FROM playersid
                       WHERE id_chanell_discord = %s AND ID_discord = %s;"""
    try:
        cursor.execute(query, (str(ctx.guild.id), str(ctx.author.id)))
    except psycopg2.Error as err:
        await ctx.send("Не удалось подключиться к базе данных")
    found_playerid = cursor.fetchall()
    if (found_playerid):
        statsdata_obj = statsdata(config['APIID'], config['url_base'])
        player_id = statsdata.player_stats(statsdata_obj, found_playerid[0][0])
        await ctx.send(player_id)
    else:
        await ctx.send('Вы не регистрировали свой аккаунт')
    cursor.close()
    conn.close()


@client.event
async def on_guild_join(guild):
    """Приветствие пользователей при добавлении бота на сервер"""
    try:
        join_chanell = guild.system_chanell
        await join_chanell.send('На вашем сервере работает Gamestart! Чтобы изучить работу бота, введите команду .help')
    except Exception as e:
        await guild.text_chanells[0].send(
            'На вашем сервере работает Gamestart! Чтобы изучить работу бота, введите команду .help')


@client.command(pass_context=True)
async def delete_my_account(ctx):
    """
        Удаляет аккаунт пользователя из базы данных
    """
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    query = """DELETE FROM playersid
                WHERE id_chanell_discord = %s AND id_discord = %s;"""
    if (conn):
        try:
            cursor.execute(query, (str(ctx.guild.id), str(ctx.author.id)))
            conn.commit()
            await ctx.send("Ваш аккаунт удален!")
        except psycopg2.Error as err:
            await ctx.send(err)
    else:
        await ctx.send("Не удалось подключиться к бд")

    cursor.close()
    conn.close()



client.run(config['TOKEN'])
