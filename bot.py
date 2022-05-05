from discord.ext import commands
import datetime
import asyncio
import database
from bot_classes import statsdata
from sys import argv
from config import Config
import requests
import psycopg2
from psycopg2 import OperationalError

connection = None
try:
    connection = psycopg2.connect(
        database="d6t05qho73cje8",
        user="wwizoojruedcgc",
        password="b3196f53147103f61242e5f3edac45c708d0458a63cde4089da48713407219a6",
        host="ec2-63-32-248-14.eu-west-1.compute.amazonaws.com",
        port=5432)
    print("Connection to PostgreSQL DB successful")
except OperationalError as e:
    print(f"The error '{e}' occurred")

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
    elif (deltadate > 0):
        await asyncio.sleep(deltadate)
        await ctx.send('Start')


@client.command(pass_context=True)
async def getnickfi(ctx, nickFI: str):
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
    await ctx.send('1')
    res = requests.get(api_url, headers=headers)
    data = res.json()
    conn = database.create_connection(config['db_name'], config['db_user'], config['db_password'], config['db_host'],
                                      config['db_port'])
    await ctx.send('2')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE PlayersID IF NOT EXISTS (ID_chanell_discord TEXT, ID_discord TEXT, player_id TEXT);")
    await ctx.send('3')
    if (conn):
        await ctx.send('подключен')
        if (res.status_code == 200):
            await ctx.send('код==200')
            player_id = data["player_id"]
            await ctx.send('.')
            try:
                cursor.execute("""INSERT INTO PlayersID (ID_chanell_discord, ID_discord, player_id) VALUES (%s, %s, %s);""", (ctx.guild.id, ctx.author.id, player_id))
            except psycopg2.Error as err:
                await ctx.send(err)
            conn.commit()
            await ctx.send('..')
            query = " SELECT * FROM PlayersID "
            cursor.execute(query)
            await ctx.send('...')
            massive = cursor.fetchall()
            for i in range(len(massive)):
                await ctx.send(massive[i])
            await ctx.send('!!!11')
            cursor.close()
            conn.close()
        else:
            await ctx.send('Такого никнейма в FACEIT не найдено')
    else:
        await ctx.send('Неполадки с базой данных')


@client.command(pass_context=True)
async def statistica(ctx):
    """Выводит статистику"""
    statsdata_obj = statsdata(config['APIID'], config['url_base'])
    player_id = statsdata.player_details(statsdata_obj)
    for i in range(0, len(player_id)):
        await ctx.send(player_id[i])


client.run(config['TOKEN'])
