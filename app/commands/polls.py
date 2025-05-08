import discord
from discord import app_commands
from datetime import datetime, timedelta
import db.stats as stats
import utils as utils
import db.permissions as permissions
import re

class Poll:
    def __init__ (self, serverId, affectedMembers, affectedStat, newValue, description, expiry, removeFlag=None):
        self.serverId = serverId
        self.yesResponses = 0
        self.noResponses = 0
        self.affectedMembers = affectedMembers
        self.affectedStat = affectedStat
        self.newValue = newValue
        self.description = description
        self.expiry = expiry
        self.removeFlag = removeFlag

    def voteYes(self):
        self.yesResponses += 1

    def voteNo(self):
        self.noResponses += 1

    def endPoll(self):

        if self.yesResponses > self.noResponses:
            stats.add_stat(self.serverId, self.affectedStat, self.newValue, self.users, self.removeFlag)
            return 1
                
        else:
            return 0
        
    def isDone(self):
        return datetime.now() >= self.expiry

#put try-catch here later
#maybe put a check for if the stat exists?
@app_commands.command(name="create-poll", description="create a poll for your server - note that there can only be one poll for server!")
async def createPoll(interaction: discord.Interaction, affected_stat: str, new_stat_value: str, users: str, expiry: int, description: str):

    if await utils.check_authorized(interaction, "add-values"):
        userIds = re.findall(r'<@(?!1307154758397726830)(\d+)>', users)

        newPoll = Poll(interaction.guild_id, userIds, affected_stat, new_stat_value, description, datetime.now() + timedelta(seconds=30))
        print(newPoll)
        
        poll_checker_cog = interaction.client.get_cog('PollChecker')
        if poll_checker_cog:
            check = poll_checker_cog.addPoll(newPoll, interaction.guild_id)
            print(check)

            if check:
                await interaction.response.send_message("works")

            else:
                await interaction.response.send_message("a poll is already running")
        else:
            print("something may have gone wrong")
            await interaction.response.send_message("not works")

    else:
        await interaction.response.send_message("you are unauthorized to use this command! only " + permissions.get_perm(interaction.guild_id, "start-polls") + " is allowed to use this.")


@app_commands.command(name="cancel-current-poll", description="cancels current running poll prematurely, no changes will be made")
async def cancelCurrentPoll(interaction: discord.Interaction):
    if await utils.check_authorized(interaction, "start-polls"):

        poll_checker_cog = interaction.client.get_cog('PollChecker')
        if poll_checker_cog:
            check = poll_checker_cog.cancelPoll(interaction.guild_id)

            if check:
                await interaction.response.send_message("poll successfully removed!")

            else:
                await interaction.response.send_message("there are currently no polls running")
        else:
            print("something may have gone wrong")
            await interaction.response.send_message("not works")


    else:
        await interaction.response.send_message("you are unauthorized to use this command! only " + permissions.get_perm(interaction.guild_id, "start-polls") + " is allowed to use this.")

@app_commands.command(name="end-current-poll", description="ends current running poll prematurely, but makes a decision based on the current votes")
async def endCurrentPoll(interaction:discord.Interaction):
    if await utils.check_authorized(interaction, "start-polls"):

        poll_checker_cog = interaction.client.get_cog('PollChecker')

        if poll_checker_cog:
            check = await poll_checker_cog.endPollEarly(interaction.guild_id)

            if not check:
                await interaction.response.send_message("no poll currently exists right now!")

            else:
                await interaction.response.send_message("poll ended!")


        else:
            print("something may have gone wrong")
            await interaction.response.send_message("not works")



    else:
        await interaction.response.send_message("you are unauthorized to use this command! only " + permissions.get_perm(interaction.guild_id, "start-polls") + " is allowed to use this.")



__commands__ = [createPoll, cancelCurrentPoll, endCurrentPoll]