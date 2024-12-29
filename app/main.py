import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID= os.getenv('APP_ID')
DISCORD_TOKEN= os.getenv('DISCORD_TOKEN')
PUBLIC_KEY= os.getenv('PUBLIC_KEY')

bot = commands.Bot(command_prefix='$', intents= discord.Intents.all())

@bot.event
async def on_ready():
    print("bot up")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    print(message)

# on guild join, create collection and get all users in the server to put as documents
# also get server owner to be given admin permissions
@bot.event
async def on_guild_join(guild):
    # mongo adds to collections that don't exist
    print(guild)
    # create channel for polls

# on guild leave, erase collection to asve space
@bot.event
async def on_guild_remove(guild):
    print(guild)


# on member join, add user to collection
@bot.event
async def on_member_join(member):
    print(member)

# on member leave, remove user document
@bot.event
async def on_member_leave(member):
    pass

# on poll end, check if in designated channel - need to create own polls for this
# create custom listener for this

# manage poll reaction for "yes"
@bot.event
async def on_reaction_add(reaction, user):
    pass

# manage poll reaction for "no"
@bot.event
async def on_reaction_remove(reaction, user):
    pass


@bot.tree.command(name="test")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("a command goes here")

# add stat to user - decide later: is it better to ONLY have stats as numbers or could they also use text stats?
# for all "direct" stat commands, require admin permission
@bot.tree.command(name="add-stat", description="add a stat to a certain or specific users")
@app_commands.describe(member="person you want to add the desired stat to")
@app_commands.describe(name="name of the stat")
@app_commands.describe(name="e.g. 'missed three-pointers'")
@app_commands.choices(type =[
    app_commands.Choice(name="blah", value="blah"),
    app_commands.Choice(name="doubleblah", value="heh")
])
async def addStat(interaction: discord.Interaction, name: str, member: discord.Member, type: app_commands.Choice[str]):
    pass

#remove stat
@bot.tree.command(name="remove-stat")
async def removeStat(interaction: discord.Interaction):
    pass

# allow to create polls for members to decide whether or not stat should be altered
# maybe make it so that it's in a designated channel?
# define functions for different kinds of stats
@bot.tree.command(name="start-poll")
async def startPoll(interaction: discord.Interaction):
    pass


#allow for user stat to be changed without poll - will require admin permission
@bot.tree.command(name="modify-stat")
async def modifyStat(interaction: discord.Interaction):
    pass


# command used for shutting down bot's connection to mongo until i find a better way
@bot.tree.command(name="shutdown")
async def shutdown(intereaction: discord.Interaction):
    # check if current user is dev
    pass

bot.run(DISCORD_TOKEN)

