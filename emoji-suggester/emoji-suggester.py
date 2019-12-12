import asyncio
import discord
from discord.ext import commands


class EmojiSuggestor(commands.Cog):
    """Sets up emoji suggestor channel in Modmail discord."""

    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 654622737159159829

    async def delete(self, message, warning):
        if warning:
            await message.channel.send(warning, delete_after=5)
        try:
            await message.delete()
        except discord.NotFound:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == self.channel_id:
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

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == self.channel_id:
            message = await self.bot.get_channel(payload.channel_id).get_message(payload.message_id)
            for r in message.reactions:
                if r.count > 1:
                    try:
                        await r.remove(self.bot.user)
                    except discord.NotFound:
                        pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id == self.channel_id:
            message = await self.bot.get_channel(payload.channel_id).get_message(payload.message_id)
            r_emojis = [r.emoji for r in message.reactions]

            for r in (discord.utils.get(message.guild.emojis, name='check'), discord.utils.get(message.guild.emojis, name='xmark')):
                if r not in r_emojis:
                    await message.add_reaction(r)


def setup(bot):
    bot.add_cog(EmojiSuggestor(bot))
