import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import re

from db import init, permissions, stats

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


# on guild leave, erase collection to asve space
@bot.event
async def on_guild_remove(guild):
    init.delete_after_kick(guild.id)


# on member join, add user to collection
@bot.event
async def on_member_join(member: discord.Member):
    init.add_user(member.guild.id, [member])
    print("new member joined, added to database")

# on member leave, remove user document
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

# checking if user is authorized to use a certain command
async def check_authorized(interaction: discord.Interaction, permission):
    authorized = permissions.get_perm(interaction.guild_id, permission)
    
    if authorized == "owner":
        return interaction.user.id == interaction.guild.owner_id

    elif authorized == "admin":
        return interaction.channel.permissions_for(interaction.user).administrator

    else:
        return True
            
@bot.tree.command(name="test")
async def test(interaction: discord.Interaction):
    blah = permissions.get_perm(interaction.guild_id, "add-values")
    print(blah)
    await interaction.response.send_message("a command goes here")

def showStatsString(result):
    
    output = ""
    for user in result['users']:
        output += f"<@{user['user_id']}>'s stats:\n "

        stats = user['stats'].items()

        if stats:
            for statName, statValue in stats:
                output += f" - **{statName}**: {statValue}\n"

        else:
            output += " - **No stats added yet, add some!**\n"
        
        output += "\n"

    return output


# add stat to user - will all be set to string for simplicity
@bot.tree.command(name="update-stat", description="add/update a stat to a certain or specific users.")
@app_commands.describe(member="ping all users you want to add the stat to, or instead type 'all' for all users")
@app_commands.describe(name="name of the stat")
@app_commands.describe(member="the member you want to add this stat to")
@app_commands.describe(value="what will you set the value of this stat to be?")
async def updateStat(interaction: discord.Interaction, name: str, member: str, value: str):
    
    if await check_authorized(interaction, "add-values"):

        if member == "all":
            memberIds = [str(member.id) for member in interaction.guild.members if member.id != 1307154758397726830]
            print(memberIds)
            stats.add_stat(interaction.guild_id, name, value, memberIds)
    
        else:
            user_ids = re.findall(r'<@(\d+)>', member)
            stats.add_stat(interaction.guild_id, name, value, user_ids)
    
        await interaction.response.send_message("stats added!")
        
    else:
        await interaction.response.send_message("you are unauthorized to use this command! only " + db.get_perm(interaction.guild_id, "add-values") + " is allowed to use this.")

# remove stat from a user, specific users, or all users
# same perms as add stat
@bot.tree.command(name="remove-stat")
@app_commands.describe(name="name of the stat")
async def removeStat(interaction: discord.Interaction, name: str, users: str):

    if await check_authorized(interaction, "add-values"):
        userIds = re.findall(r'<@(?!1307154758397726830)(\d+)>', users)
        stats.add_stat(interaction.guild_id, name, "", userIds, removeFlag=True)
        result = stats.get_stats(interaction.guild_id, userIds)

        response = showStatsString(result)

        response  = "stat removed from the following users!\ncurrent stats for the affected users: \n" + response

        await interaction.response.send_message(response)
        
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
    app_commands.Choice(name="update-values", value="add-values"),
    app_commands.Choice(name="start-polls", value="start-polls"),
    app_commands.Choice(name="all-perms", value="all-perms")
])
@is_server_owner()
async def editPerms(interaction: discord.Interaction, permission: app_commands.Choice[str], users: app_commands.Choice[str]):
    #todo: make it so that guild owner only has permissions to do this
    permissions.edit_perms(interaction.guild_id, permission.value, users.value)

    modPerm = permissions.get_perm(interaction.guild_id, "add-values")
    pollPerm = permissions.get_perm(interaction.guild_id, "start-polls")

    await interaction.response.send_message("permissions updated!\n New permissions:\n Update values: " + modPerm + "\n Start/close polls: " + pollPerm)

@bot.tree.command(name="get-current-perms", description="shows current permission levels for each stat-modifying command")
async def getCurrentPerms(interaction: discord.Interaction):
    modPerm = permissions.get_perm(interaction.guild_id, "add-values")
    pollPerm = permissions.get_perm(interaction.guild_id, "start-polls")

    await interaction.response.send_message("Current permissions:\n Update values: " + modPerm + "\n Start/close polls: " + pollPerm)

@bot.tree.command(name="get-current-stats")
async def getCurrentStats(interaction:discord.Interaction, users: str):
    userIds = re.findall(r'<@(?!1307154758397726830)(\d+)>', users)
    result = stats.get_stats(interaction.guild_id, userIds)

    output = showStatsString(result)

    await interaction.response.send_message(output)

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
        init.disconnect_db()
        await interaction.response.send_message("successful shutdown")

    else:
        await interaction.response.send_message("not authorized")

    pass

bot.run(DISCORD_TOKEN)
