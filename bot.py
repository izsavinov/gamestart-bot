from discord.ext import commands
from os import environ
from sys import argv

from config import Config


config = Config(argv[1]).config
client = commands.Bot(command_prefix=config['prefix'])


@client.event
async def on_ready():
    """Сообщение о подключении бота."""
    print('BOT connected')


@client.command(pass_context=True)
async def hello(ctx):
    """Приветствие пользователя по команде в Discord."""
    await ctx.send(config['greeting'])


client.run(config['TOKEN'])
