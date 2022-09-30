import re
from discord.ext import commands


class Github(commands.Cog):
    """Checks for issue mentions in the message and responds to them.
    Made for the Modmail server. An example of a niche feature."""

    @commands.Cog.listener()
    async def on_message(self, message):
        match = re.match(r'modmail#(\d+)', message.content)
        if match:
            issue_num = match.group(1)
            await message.channel.send(f'https://github.com/kyb3r/modmail/issues/{issue_num}')


async def setup(bot):
    await bot.add_cog(Github())
