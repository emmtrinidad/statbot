import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
from db import init, permissions

load_dotenv()

APP_ID= os.getenv('APP_ID')
DISCORD_TOKEN= os.getenv('DISCORD_TOKEN')
PUBLIC_KEY= os.getenv('PUBLIC_KEY')

bot = commands.Bot(command_prefix='$', intents= discord.Intents.all())

@bot.event
async def on_ready():
    print("bot up", flush=True)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands", flush=True)
        await bot.load_extension('cogs.PollChecker')
        print("works?", flush=True)
        init.startup_db()
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    pass

# on guild join, create collection and get all users in the server to put as documents
# also get server owner to be given admin permissions
@bot.event
async def on_guild_join(guild):

    # create channel for polls if doesn't exist
    if not any(channel.name == "statbot-polls" for channel in guild.channels):
        await guild.create_text_channel("statbot-polls")

    for channel in guild.channels:
        if (channel.name == "statbot-polls"):
            # add poll channel as document in db for later reference, add permissions
            init.add_poll_channel(guild.id, channel.id)
            permissions.add_perms(guild.id)

    init.add_user(guild.id, guild.members)

    await channel.send("All set up! This channel will be used to host polls to alter stats. Currently, only admins have access to all stat-modifying commands. If you want to edit stats, consider using `/edit-perms`")

# on guild leave, erase document to asve space
@bot.event
async def on_guild_remove(guild):
    init.delete_after_kick(guild.id)

# on member join, add user to server document
@bot.event
async def on_member_join(member: discord.Member):
    init.add_user(member.guild.id, [member])
    print("new member joined, added to database")

# on member leave, remove user from document
@bot.event
async def on_member_remove(member):
    init.remove_user(member.guild.id, str(member.id))
    print("member left, removing")


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

# dynamically load all commands
def load_commands():
    import importlib
    from pathlib import Path

    # only get from db and commands folders - cog is already added upon initializing
    directories = [("db", "db"), ("commands", "commands")]

    # check every file in db, commands folders for all .py files that aren't init, and add expored commands to command tree
    for folderName, modulePrefix in directories:
        dir = Path(__file__).parent / folderName
        for file in dir.glob("*.py"):
            # skip init
            if file.name == "__init__.py":
                continue

            module_name = f"{modulePrefix}.{file.stem}"
            module = importlib.import_module(module_name)

            if hasattr(module, "__commands__"):
                for cmd in module.__commands__:
                    bot.tree.add_command(cmd)

load_commands()

bot.run(DISCORD_TOKEN)
