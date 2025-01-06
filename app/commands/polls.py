import discord
from discord import app_commands
from datetime import datetime, timedelta
import app.db.stats as stats
import re
import asyncio

class Poll:
    def __init__ (self, serverId, affectedMembers, affectedStat, newValue, description, expiry, removeFlag):
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
            return "passed"
        
        elif self.yesResponses == self.noResponses:
            return "tied"
        
        else:
            return "failed"
        
    def isDone(self):
        return datetime.now() >= self.expiry

#put try-catch here later
#maybe put a check for if the stat exists?
@app_commands.command(name="create-poll", description="create a poll for your server - note that there can only be one poll for server!")
async def createPoll(interaction: discord.Interaction, affected_stat: str, new_stat_value: str, users: str, expiry: int, description: str):
    userIds = re.findall(r'<@(?!1307154758397726830)(\d+)>', users)

    newPoll = Poll(interaction.guild_id, userIds, affected_stat, new_stat_value, description, datetime.now() + timedelta(minutes=1))
    print(newPoll)
    
    poll_checker_cog = interaction.client.get_cog('PollChecker')
    if poll_checker_cog:
        poll_checker_cog.addPoll(newPoll, interaction.guild_id)
        print("poll added")
    else:
        print("PollChecker cog not found.")


__commands__ = [createPoll]