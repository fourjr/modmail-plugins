import asyncio
import discord
from discord.ext import commands


class EmojiSuggestor(commands.Cog):
    """Sets up emoji suggestor channel in Modmail discord."""

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 654622737159159829:
            if len(message.attachments):
                await message.add_reaction(discord.utils.get(message.guild.emojis, name='check'))
                await asyncio.sleep(0.1)
                await message.add_reaction(discord.utils.get(message.guild.emojis, name='xmark'))
            else:
                await message.delete()
                await message.guild.get_channel(515085600047628288).send(f'{message.author.mention}, do not send messages in {message.channel.mention}')


def setup(bot):
    bot.add_cog(EmojiSuggestor())
