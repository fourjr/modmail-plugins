
import discord
from discord.ext import commands

from core import checks
from core.checks import PermissionLevel


class ClaimThread(commands.Cog):
    """Allows supporters to claim thread by sendning claim in the thread channel"""
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)
        check_reply.fail_msg = 'This thread has been claimed by another user.'
        self.bot.get_command('reply').add_check(check_reply)

    @commands.Cog.listener()
    async def on_message(self, m):
        if m.content == 'claim':
            thread = await self.bot.threads.find(channel=m.channel)
            if thread:
                t = await self.db.find_one({'thread_id': str(thread.channel.id)})
                if t is None:
                    await self.db.insert_one({'thread_id': str(thread.channel.id), 'claimers': [str(m.author.id)]})
                    await m.channel.send('Claimed')
                else:
                    await m.channel.send('Thread is already claimed')

    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @checks.thread_only()
    @commands.command()
    async def add(self, ctx, *, member: discord.Member):
        """Adds another user to the thread claimers"""
        thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
        if thread and str(ctx.author.id) in thread['claimers']:
            await self.db.find_one_and_update({'thread_id': str(ctx.thread.channel.id)}, {'$addToSet': {'claimers': str(member.id)}})
            await ctx.send('Added to claimers')

    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @checks.thread_only()
    @commands.command()
    async def remove(self, ctx, *, member: discord.Member):
        """Removes a user from the thread claimers"""
        thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
        if thread and str(ctx.author.id) in thread['claimers']:
            await self.db.find_one_and_update({'thread_id': str(ctx.thread.channel.id)}, {'$pull': {'claimers': str(member.id)}})
            await ctx.send('Removed from claimers')

    @checks.has_permissions(PermissionLevel.SUPPORTER)
    @checks.thread_only()
    @commands.command()
    async def transfer(self, ctx, *, member: discord.Member):
        """Removes all users from claimers and gives another member all control over thread"""
        thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
        if thread and str(ctx.author.id) in thread['claimers']:
            await self.db.find_one_and_update({'thread_id': str(ctx.thread.channel.id)}, {'$set': {'claimers': [str(member.id)]}})
            await ctx.send('Added to claimers')

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @checks.thread_only()
    @commands.command()
    async def overrideadd(self, ctx, *, member: discord.Member):
        """Allow mods to bypass claim thread check in add"""
        thread = await self.db.find_one({'thread_id': str(ctx.thread.channel.id)})
        if thread:
            await self.db.find_one_and_update({'thread_id': str(ctx.thread.channel.id)}, {'$addToSet': {'claimers': str(member.id)}})
            await ctx.send('Added to claimers')

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @checks.thread_only()
    @commands.command()
    async def overridereply(self, ctx, *, msg: str=""):
        """Allow mods to bypass claim thread check in reply"""
        await ctx.invoke(self.bot.get_command('reply'), msg=msg)


async def check_reply(ctx):
    thread = await ctx.bot.get_cog('ClaimThread').db.find_one({'thread_id': str(ctx.thread.channel.id)})
    if thread:
        return str(ctx.author.id) in thread['claimers']
    return True


def setup(bot):
    bot.add_cog(ClaimThread(bot))