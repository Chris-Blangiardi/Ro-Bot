import discord
from discord.ext import commands
import os


BOT_prefix = "#"
BOT_token = os.environ.get("RO_TOKEN")
intents = discord.Intents.default()

client = commands.Bot(command_prefix=BOT_prefix, intents=intents)

# searches for cog files and loads them
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# informs when bot is connected to discord - terminal only
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


# starts the bot
client.run(BOT_token)
