import discord
from discord import app_commands
import db.permissions as permissions
from utils import is_server_owner

@app_commands.command(name="edit-perms", description="edit permissions to modify stats")
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

@app_commands.command(name="get-current-perms", description="shows current permission levels for each stat-modifying command")
async def getCurrentPerms(interaction: discord.Interaction):
    modPerm = permissions.get_perm(interaction.guild_id, "add-values")
    pollPerm = permissions.get_perm(interaction.guild_id, "start-polls")

    await interaction.response.send_message("Current permissions:\n Update values: " + modPerm + "\n Start/close polls: " + pollPerm)

__commands__ = [getCurrentPerms, editPerms]