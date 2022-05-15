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
    if (deltadate - 15 * 60 > 0):
        await asyncio.sleep(deltadate - 15 * 60 + 2)
        await ctx.send('15 минут')
    if (deltadate > 0):
        await asyncio.sleep(deltadate)
        await ctx.send('Start')


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
    await ctx.send('1')
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    await ctx.send('2')
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
            await ctx.send(found_users)
            await ctx.send('1')
            if (found_users == None):
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
async def statistica(ctx):
    """Выводит статистику"""
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    # Получим player_id всех игроков из выбранного канала в дискорде
    query = """SELECT player_id
               FROM playersid
               WHERE id_chanell_discord = %s;"""
    try:
        await ctx.send('/')
        cursor.execute(query, (str(ctx.guild.id),))
        await ctx.send('//')
    except psycopg2.Error as err:
        await ctx.send("Не удалось подключиться к базе данных")
    found_playersid = cursor.fetchall()

    # Получим player_id игрока, который вызвал команду .statistica
    query = """SELECT player_id
                   FROM playersid
                   WHERE id_chanell_discord = %s AND ID_discord = %s;"""
    try:
        await ctx.send('///')
        cursor.execute(query, (str(ctx.guild.id), str(ctx.author.id)))
        await ctx.send('////')
    except psycopg2.Error as err:
        await ctx.send("Не удалось подключиться к базе данных")
    found_playerid = cursor.fetchall()

    if (found_playersid):
        await ctx.send(str(found_playersid[0]))
        await ctx.send(found_playerid)
        statsdata_obj = statsdata(config['APIID'], config['url_base'])
        await ctx.send('//////')
        player_id = statsdata.player_details(statsdata_obj, found_playerid, found_playersid)
        await ctx.send('1')
        for i in range(0, len(player_id)):
            await ctx.send(player_id[i])
    else:
        await ctx.send('Вы не регистрировали свой аккаунт')
    cursor.close()
    conn.close()


@client.command(pass_context=True)
async def delete_database_entries(ctx):
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    cursor = conn.cursor()
    query = """DELETE FROM playersid;"""
    if (conn):
        try:
            await ctx.send('///')
            cursor.execute(query)
            conn.commit()
            await ctx.send("Записи успешно удалены")
        except psycopg2.Error as err:
            await ctx.send(err)
    else:
        await ctx.send("Не удалось подключиться к бд")

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
            await ctx.send('///')
            cursor.execute(query, (str(ctx.guild.id), str(ctx.author.id)))
            conn.commit()
            await ctx.send("Записи успешно удалены")
        except psycopg2.Error as err:
            await ctx.send(err)
    else:
        await ctx.send("Не удалось подключиться к бд")

    cursor.close()
    conn.close()


client.run(config['TOKEN'])
