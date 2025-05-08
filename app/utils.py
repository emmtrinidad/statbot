import discord
import db.permissions as permissions

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

# checking if user is authorized to use a certain command
async def check_authorized(interaction: discord.Interaction, permission):
    authorized = permissions.get_perm(interaction.guild_id, permission)
    
    if authorized == "owner":
        return interaction.user.id == interaction.guild.owner_id

    elif authorized == "admin":
        return interaction.channel.permissions_for(interaction.user).administrator

    else:
        return True
    
def is_server_owner():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == interaction.guild.owner_id  # guild owner id
    return discord.app_commands.check(predicate)

def is_dev():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == 204427877955928064  # developer (me) id
    return discord.app_commands.check(predicate)

