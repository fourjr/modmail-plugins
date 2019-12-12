import asyncio
import discord
from discord.ext import commands


class EmojiSuggestor(commands.Cog):
    """Sets up emoji suggestor channel in Modmail discord."""

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 654622737159159829:
            if message.author.bot:
                await asyncio.sleep(5)
                await message.delete()
            elif len(message.attachments):
                if len(message.attachments) > 1:
                    await message.channel.send(f'{message.author.mention}, send 1 emoji at a time.', delete_after=5)
                    await message.delete()
                elif not message.attachments[0].filename.endswith('.png'):
                    await message.channel.send(f'{message.author.mention}, only png attachments are allowed.', delete_after=5)
                    await message.delete()
                else:
                    await message.add_reaction(discord.utils.get(message.guild.emojis, name='check'))
                    await asyncio.sleep(0.1)
                    await message.add_reaction(discord.utils.get(message.guild.emojis, name='xmark'))
            else:
                await message.channel.send(f'{message.author.mention}, only images + captions are allowed. If you wish to add a caption, edit your original message.', delete_after=5)
                await message.delete()


def setup(bot):
    bot.add_cog(EmojiSuggestor())
