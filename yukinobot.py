import logging
import traceback

import discord
from discord.ext import commands

import oauth

format_attrs = (
    '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
)
format_directives = '%A %B %d - %I:%M%p'

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log',                                  
    encoding='utf-8',
    mode='w'
)
handler.setFormatter(logging.Formatter(
    format_attrs,                                            
    format_directives
))
logger.addHandler(handler)

command_prefix = commands.when_mentioned_or('$')
bot = commands.Bot(command_prefix=command_prefix)

yukinos_exts = [
    'cogs.admin',
    'cogs.weeb',
    'cogs.movie-tv',
    'cogs.unist'
]

# Events:

@bot.event
async def on_ready():
    """Sets the bot's status"""
    print(
        f'Logged in as: {bot.user}\nVersion:{discord.__version__}'
    )
    game = discord.Game('with lolis')
    await bot.change_presence(activity=game)

# @bot.event
# async def on_message(message):
    
#     await bot.process_commands(message)

@bot.event
async def on_member_remove(member):
    """ Sends a message when a member leaves the guild."""
    await member.channel.send(f'{member} has left the server.')

if __name__ == '__main__':
    for extension in yukinos_exts:
        try:
            bot.load_extension(extension)
        except(ValueError, discord.HTTPException):
            pass
        except Exception:
            logger.error(
                f'Failed to load extension: {extension}'
            )
            traceback.print_exc()

bot.run(oauth.bot_token)