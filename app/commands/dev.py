import discord
from discord import app_commands
from app.utils import is_dev
import app.db.init as init

# command used for shutting down bot's connection to mongo until i find a better way
@app_commands.command(name="shutdown")
@is_dev()
async def shutdown(interaction: discord.Interaction):
    # check if current user is dev

    # disconnect
    if interaction.user.id == 204427877955928064:
        init.disconnect_db()
        await interaction.response.send_message("successful shutdown")

    else:
        await interaction.response.send_message("not authorized")

__commands__ = [shutdown]

