from datetime import datetime
from types import SimpleNamespace

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class Report(commands.Cog):
    """Report emoji sent to mods"""

    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)
        self._config = None

    async def get_config(self):
        if self._config is None:
            config = await self.db.find_one({'_id': 'config'})

            if config:
                self._config = SimpleNamespace(
                    emoji=config['emoji'],
                    channel=self.bot.get_channel(int(config['channel']))
                )

        return self._config

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Sends out menu to user"""
        config = await self.get_config()
        if config and str(payload.emoji) == config.emoji:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            author = self.bot.get_user(payload.user_id)
            await message.remove_reaction(payload.emoji, author)

            if message.author.bot or message.author == author:
                return

            ellipsis = '...' if len(message.content) > 200 else ''
            description = f'{message.content[:200]}{ellipsis}\n[Read More]({message.jump_url})'

            em = discord.Embed(title='New Report', description=description, color=discord.Colour.red(), timestamp=datetime.utcnow())
            em.set_author(name=str(message.author), icon_url=message.author.avatar_url)
            em.set_footer(text=f'Reported by {author}', icon_url=author.avatar_url)
            await config.channel.send(embed=em)
            await author.send(embed=em)

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def configreports(self, ctx, emoji: str, *, channel: discord.TextChannel):
        """Configure emoji and channel used for reporting"""
        self._config = SimpleNamespace(
            emoji=emoji, channel=channel
        )
        await self.db.find_one_and_update({'_id': 'config'}, {'$set': {'emoji': emoji, 'channel': str(channel.id)}}, upsert=True)
        await ctx.send('Configured')


def setup(bot):
    bot.add_cog(Report(bot))
