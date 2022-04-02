from discord.ext import commands
from os import environ
from sys import argv

from config import Config


config = Config(argv[1]).config
client = commands.Bot(command_prefix=config['prefix'])


@client.event
async def on_ready():
    """Функция пишет о подключении бота у серверу дискорда"""
    print('BOT connected')


@client.command(pass_context=True)
async def hello(ctx):
    """Приветствие пользователя в дискорде при вводе команды .hello"""
    await ctx.send(config['greeting'])


client.run(config['TOKEN'])
