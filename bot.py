from discord.ext import commands
from os import environ

client = commands.Bot(command_prefix='.')


@client.event
async def on_ready():
    """Функция пишет о подключении бота у серверу дискорда"""
    print('BOT connected')


@client.command(pass_context=True)
async def hello(ctx):
    """Приветствие пользователя в дискорде при вводе команды .hello"""
    await ctx.send('Hello!')


client.run(environ.get('TOKEN'))
