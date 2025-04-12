import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='ping', help='Replies with Pong!')
async def ping(ctx):
    await ctx.send('Pong!')

bot.run('YOUR_BOT_TOKEN')  # Replace with your bot token
