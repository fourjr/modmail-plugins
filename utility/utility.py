from discord.ext import commands


class Utility:
    """Provides basic utility commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, message: commands.clean_content):
        """Repeats after you"""
        await ctx.send(message)

    # TODO: DB Examples


def setup(bot):
    bot.add_cog(Utility(bot))
