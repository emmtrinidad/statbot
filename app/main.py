import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

APP_ID= os.getenv('APP_ID')
DISCORD_TOKEN= os.getenv('DISCORD_TOKEN')
PUBLIC_KEY= os.getenv('PUBLIC_KEY')

class MyBot(discord.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content} in {message.channel}')

intents = discord.Intents.default()
intents.message_content = True

client = MyBot(intents=intents)
client.run(DISCORD_TOKEN)

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def pooopy(ctx, arg):
    await ctx.send(arg)



