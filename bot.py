from discord.ext import commands
import datetime
import asyncio
from bot_classes import statsdata
from sys import argv
from config import Config
import sqlite3
import requests

nickFI = ''

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
    deltadate = (date.day * 24 * 3600 + date.hour * 3600 + date.minute * 60 + date.second) - (time_now.day * 24 * 3600 \
                                                 + time_now.hour * 3600 + time_now.minute * 60 + time_now.second)
    if (deltadate - 15 * 60 > 0):
        await asyncio.sleep(deltadate - 15 * 60 + 2)
        await ctx.send('15 минут')
    else:
        await asyncio.sleep(deltadate)
        await ctx.send('Start')


@client.command(pass_context=True)
async def getnickfi(ctx, nickFI: str):
    """
        Пользователь предоставляет нам информацию о своем аккаунте FACEIT, а именно - никнейм
    """
    await ctx.send('{}'.format(nickFI))
    await ctx.send(ctx.author.id)
    await ctx.send(ctx.guild.id)
    # Получим player_id
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(config['APIID'])
    }
    api_url = "{}/players".format(url_base)
    api_url += "?nickname={}".format(nickFI)
    res = requests.get(api_url, headers=headers)
    data = res.json()

    if res.status_code == 200:
        player_id = data["player_id"]
        await ctx.send(player_id)
        with sqlite3.connect('PlayersID.db') as db:
            cursor = db.cursor()
            cursor.execute("INSERT INTO PlayersID VALUES(?,?,?,?)", ctx.author.id, nickFI, player_id, ctx.guild.id)
            db.commit()
            query = """ SELECT * FROM PlayersID """
            cursor.execute(query)
            for res in cursor:
                await ctx.send(res)
    else:
        await ctx.send('Такого никнейма в FACEIT не найдено')




@client.command(pass_context=True)
async def statistica(ctx):
    """Выводит статистику"""
    statsdata_obj = statsdata(config['APIID'], config['url_base'])
    player_id = statsdata.player_details(statsdata_obj, nickFI)
    for i in range(0, len(player_id)):
        await ctx.send(player_id[i])


client.run(config['TOKEN'])
