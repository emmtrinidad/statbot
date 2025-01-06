import discord
from discord.ext import commands, tasks
import app.db.stats as stats
import app.utils as utils
import app.db.init as init

class PollChecker(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.activePolls = {}
        self.checkPolls.start()

    def cog_unload(self):
        self.checkPolls.cancel()

    def addPoll(self, poll, serverId):

        if str(serverId) not in self.activePolls:
            self.activePolls[str(serverId)] = poll
            return True

        else:
            return False
        
    # cancels/ends poll prematurely
    def cancelPoll(self, serverId, endFlag = None):
        # get poll to be cancelled/ended
        poll = self.activePolls.pop(str(serverId), None)
        
        if poll:
            # if poll is to be ENDED and not cancelled, return result
            if endFlag:
                return poll.endPoll()
            return True
        
        return False
    
    async def handlePollEnd(self, poll, serverId):
        result = poll.endPoll()

        if result == 1:

            stats.add_stat(serverId, poll.affectedStat, poll.newValue, poll.affectedMembers, None)
            newStats = stats.get_stats(serverId, poll.affectedMembers)

            output = f"Poll passed {poll.yesResponses} - {poll.noResponses}!\n New stats of affected users:\n"

            output += utils.showStatsString(newStats)

        else:
            output = f"Poll failed {poll.yesResponses} - {poll.noResponses}. No stats have been altered."

        pollChannelId = init.get_poll_channel(serverId)['settings']['poll-channel-id']
        channel = await self.bot.fetch_channel(pollChannelId)
        print(channel)
        await channel.send(output)

        
    async def endPollEarly(self, serverId):
        if str(serverId) in self.activePolls:
            await self.handlePollEnd(self.activePolls[str(serverId)], str(serverId))
            return True # signal poll exists and has been ended

        else:
            return False # signal no poll exists



    @tasks.loop(seconds=5.0)
    async def checkPolls(self):
        print(self.activePolls)
        expiredPolls = []

        # check every poll to see if expired
        for serverId, poll in self.activePolls.items():
            if poll.isDone():
                print("poll expired")
                expiredPolls.append(serverId)

        #after, delete all expired polls
        for serverId in expiredPolls:
            finishedPoll = self.activePolls[serverId]
            result = finishedPoll.endPoll()

            if result == 1:

                stats.add_stat(serverId, finishedPoll.affectedStat, finishedPoll.newValue, finishedPoll.affectedMembers, None)
                newStats = stats.get_stats(serverId, finishedPoll.affectedMembers)

                output = f"Poll passed {finishedPoll.yesResponses} - {finishedPoll.noResponses}!\n New stats of affected users:\n"

                output += utils.showStatsString(newStats)

            else:
                output = f"Poll failed {finishedPoll.yesResponses} - {finishedPoll.noResponses}. No stats have been altered."

            pollChannelId = init.get_poll_channel(serverId)['settings']['poll-channel-id']
            channel = await self.bot.fetch_channel(pollChannelId)
            print(channel)
            await channel.send(output)
            del self.activePolls[serverId]
            print("poll deleted")

async def setup(bot):
    await bot.add_cog(PollChecker(bot))