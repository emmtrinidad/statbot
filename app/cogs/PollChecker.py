import discord
from discord.ext import commands, tasks

class PollChecker(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.activePolls = {}
        self.checkPolls.start()

    def cog_unload(self):
        self.checkPolls.cancel()

    def addPoll(self, poll, serverId):
        self.activePolls[str(serverId)] = poll

    @tasks.loop(seconds=5.0)
    async def checkPolls(self):
        print("looping")
        expiredPolls = []

        # check every poll to see if expired
        for serverId, poll in self.activePolls.items():
            if poll.isDone():
                print("poll expired")
                expiredPolls.append(poll)

        #after, delete all expired polls
        for serverId in expiredPolls:
            del self.activePolls[serverId]

async def setup(bot):
    await bot.add_cog(PollChecker(bot))