import asyncio
import discord
from discord.ext import commands


class EmojiSuggestor(commands.Cog):
    """Sets up emoji suggestor channel in Modmail discord."""

    async def delete(self, message, warning):
        if warning:
            await message.channel.send(warning, delete_after=5)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 654622737159159829:
            if message.author.bot:
                await asyncio.sleep(5)
                await self.delete(message, warning=None)
            elif len(message.attachments):
                if len(message.attachments) > 1:
                    await self.delete(message, warning=f'{message.author.mention}, send 1 emoji at a time.')
                elif not (message.attachments[0].filename.endswith('.png') or message.attachments[0].filename.endswith('.gif')):
                    await self.delete(message, warning=f'{message.author.mention}, only png or gif attachments are allowed.')
                else:
                    await message.add_reaction(discord.utils.get(message.guild.emojis, name='check'))
                    await asyncio.sleep(0.1)
                    await message.add_reaction(discord.utils.get(message.guild.emojis, name='xmark'))
            else:
                await self.delete(message, warning=f'{message.author.mention}, only images + captions are allowed. If you wish to add a caption, edit your original message.')


def setup(bot):
    bot.add_cog(EmojiSuggestor())
