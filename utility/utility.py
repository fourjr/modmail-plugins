import discord
from discord.ext import commands


class UtilityExamples:
    """Provides basic utility commands"""
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.command()
    async def say(self, ctx, *, message: commands.clean_content):
        """Repeats after you"""
        await ctx.send(message)

    @commands.group()
    async def group(self, ctx):
        """Allows user to set their group"""
        if ctx.invoked_subcommand is None:
            cmd = self.bot.get_command('help')
            await ctx.invoke(cmd, command='group')

    @group.command(name='set')
    async def set_(self, ctx, group_name: str.title):
        """Sets their group"""
        valid_groups = ('Red', 'Green', 'Blue')
        if group_name not in valid_groups:
            await ctx.send('Invalid group. Pick one from: ' + ', '.join(valid_groups))
        else:
            await self.db.find_one_and_update(
                {'user_id': str(ctx.author.id)},
                {'$set': {'group': group_name}},
                upsert=True
            )
            await ctx.send(f'Welcome to {group_name}!')

    @group.command()
    async def get(self, ctx, member: discord.Member = None):
        """Gets a user's group"""
        member = member or ctx.author
        data = await self.db.find_one({'user_id': str(member.id)})
        if data:
            await ctx.send(f"{member.name} is in {data['group']}!")
        else:
            await ctx.send(f"{member.name} hasn't picked a group :(")

    @commands.has_permissions(kick_member=True)
    @group.command()
    async def reset(self, ctx, member: discord.Member):
        """Resets a user's group
        Only available for mods with kick_member permission"""
        await self.db.find_one_and_delete({'user_id': str(member.id)})
        await ctx.send('Member reset')


def setup(bot):
    bot.add_cog(UtilityExamples(bot))
