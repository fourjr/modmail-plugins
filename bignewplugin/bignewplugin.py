from discord.ext import commands

class BigNewPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send('I believe I have successfully performed the inital expected outcome with 100% success rate. Thank you and goodbye.')


def setup(bot):
    bot.add_cog(BigNewPlugin(bot))
