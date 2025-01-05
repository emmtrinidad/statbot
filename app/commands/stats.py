import discord
from discord import app_commands
import app.db.stats as stats
import re
import app.utils as utils

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
@app_commands.command(name="update-stat", description="add/update a stat to a certain or specific users.")
@app_commands.describe(member="ping all users you want to add the stat to, or instead type 'all' for all users")
@app_commands.describe(name="name of the stat")
@app_commands.describe(member="the member you want to add this stat to")
@app_commands.describe(value="what will you set the value of this stat to be?")
async def updateStat(interaction: discord.Interaction, name: str, member: str, value: str):
    
    if await utils.check_authorized(interaction, "add-values"):

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
@app_commands.command(name="remove-stat")
@app_commands.describe(name="name of the stat")
async def removeStat(interaction: discord.Interaction, name: str, users: str):

    if await utils.check_authorized(interaction, "add-values"):
        userIds = re.findall(r'<@(?!1307154758397726830)(\d+)>', users)
        stats.add_stat(interaction.guild_id, name, "", userIds, removeFlag=True)
        result = stats.get_stats(interaction.guild_id, userIds)

        response = showStatsString(result)

        response  = "stat removed from the following users!\ncurrent stats for the affected users: \n" + response

        await interaction.response.send_message(response)
        
    else:
        await interaction.response.send_message("you are unauthorized to use this command! only " + db.get_perm(interaction.guild_id, "add-values") + " is allowed to use this.")

@app_commands.command(name="get-current-stats")
async def getCurrentStats(interaction:discord.Interaction, users: str):
    userIds = re.findall(r'<@(?!1307154758397726830)(\d+)>', users)
    result = stats.get_stats(interaction.guild_id, userIds)

    output = showStatsString(result)

    await interaction.response.send_message(output)


__commands__ = [getCurrentStats, removeStat, updateStat]
