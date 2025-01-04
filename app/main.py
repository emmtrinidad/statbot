import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import db
import re

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
        db.startup_db()
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
            db.add_poll_channel(guild.id, channel.id)
            db.add_perms(guild.id)

    db.add_user(guild.id, guild.members)

    await channel.send("All set up! This channel will be used to host polls to alter stats. Currently, only admins have access to all stat-modifying commands. If you want to edit stats, consider using `/edit-perms`")


# on guild leave, erase collection to asve space
@bot.event
async def on_guild_remove(guild):
    db.delete_after_kick(guild.id)


# on member join, add user to collection
@bot.event
async def on_member_join(member: discord.Member):
    db.add_user(member.guild.id, [member])
    print("new member joined, added to database")

# on member leave, remove user document
@bot.event
async def on_member_leave(member):
    db.remove_user(member.guild.id, member)
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

# checking if user is authorized to use a certain command
async def check_authorized(interaction: discord.Interaction, permission):
    authorized = db.get_perm(interaction.guild_id, permission)
    
    if authorized == "owner":
        return interaction.user.id == interaction.guild.owner_id

    elif authorized == "admin":
        return interaction.channel.permissions_for(interaction.user).administrator

    else:
        return True
            
@bot.tree.command(name="test")
async def test(interaction: discord.Interaction):
    blah = db.get_perm(interaction.guild_id, "add-values")
    print(blah)
    await interaction.response.send_message("a command goes here")

# add stat to user - will all be set to string for simplicity
@bot.tree.command(name="add-stat", description="add a stat to a certain or specific users.  needs admin privilege to do so.")
@app_commands.describe(member="ping all users you want to add the stat to, or instead type 'all' for all users")
@app_commands.describe(name="name of the stat")
@app_commands.describe(member="the member you want to add this stat to")
@app_commands.describe(value="what will you set the value of this stat to be?")
async def addStat(interaction: discord.Interaction, name: str, member: str, value: str):
    
    if await check_authorized(interaction, "add-values"):

        if member == "all":
            memberIds = [str(member.id) for member in interaction.guild.members if member.id != 1307154758397726830]
            print(memberIds)
            db.add_stat(interaction.guild_id, name, value, memberIds)
    
        else:
            user_ids = re.findall(r'<@(\d+)>', member)
            db.add_stat(interaction.guild_id, name, value, user_ids)
    
        await interaction.response.send_message("stats added!")
        
    else:
        await interaction.response.send_message("you are unauthorized to use this command! only " + db.get_perm(interaction.guild_id, "add-values") + " is allowed to use this.")

def is_server_owner():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == interaction.guild.owner_id  # guild owner id
    return discord.app_commands.check(predicate)


@bot.tree.command(name="edit-perms", description="edit permissions to modify stats")
@app_commands.choices(users =[
    app_commands.Choice(name="owner", value="owner"),
    app_commands.Choice(name="admin", value="admin"),
    app_commands.Choice(name="all", value="all")
])
@app_commands.choices(permission =[
    app_commands.Choice(name="modify-values", value = "modify-values"),
    app_commands.Choice(name="add-values", value="add-values"),
    app_commands.Choice(name="start-polls", value="start-polls"),
    app_commands.Choice(name="all-perms", value="all-perms")
])
@is_server_owner()
async def editPerms(interaction: discord.Interaction, permission: app_commands.Choice[str], users: app_commands.Choice[str]):
    #TODO: show permissions after editing, and create a function that shows current permissions
    # also todo: make it so that guild owner only has permissions to do this
    db.edit_perms(interaction.guild_id, permission.value, users.value)
    await interaction.response.send_message("permissions updated!")

# remove stat from a user, specific users, or all users
# same perms as add stat
@bot.tree.command(name="remove-stat")
@app_commands.describe(name="name of the stat")
async def removeStat(interaction: discord.Interaction, name: str, users: discord.Member = None):

    if await check_authorized(interaction, "add-values"):
        print(interaction.message)
        await interaction.response.send_message("dummy message")
        
    else:
        await interaction.response.send_message("you are unauthorized to use this command! only " + db.get_perm(interaction.guild_id, "add-values") + " is allowed to use this.")

    pass

# allow to create polls for members to decide whether or not stat should be altered
# maybe make it so that it's in a designated channel?
# define functions for different kinds of stats
@bot.tree.command(name="start-poll")
@app_commands.describe(title="poll title")
@app_commands.describe(users="user")
@app_commands.describe(stat="stat to be proposed to modify")
@app_commands.describe(daystoend="how many days until the poll ends?")
@app_commands.describe(hourstoend="how many hours on top of (or without) those days until the poll ends?")
@app_commands.rename(daystoend="days-to-poll-end")
@app_commands.rename(hourstoend="hours-to-poll-end")
async def startPoll(interaction: discord.Interaction, title: str, users: discord.Member, stat: str, daystoend: int = None, hourstoend: int = None):
    pass


#allow for user stat to be changed without poll - will require admin permission
@bot.tree.command(name="modify-stat")
@app_commands.describe(user="user to modify")
@app_commands.describe(stat="stat to modify") #keep like this for now - try to see if there's a way to instead get stats after getting user
@app_commands.describe(newval="new value to modify") # parse string into int if value is int, same thing with decimal
async def modifyStat(interaction: discord.Interaction, user: discord.Member, stat: str, newval: str):
    pass

def is_dev():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == 204427877955928064  # developer (me) id
    return discord.app_commands.check(predicate)


# command used for shutting down bot's connection to mongo until i find a better way
@bot.tree.command(name="shutdown")
@is_dev()
async def shutdown(interaction: discord.Interaction):
    # check if current user is dev

    # disconnect
    if interaction.user.id == 204427877955928064:
        db.disconnect_db()
        await interaction.response.send_message("successful shutdown")

    else:
        await interaction.response.send_message("not authorized")

    pass

bot.run(DISCORD_TOKEN)
