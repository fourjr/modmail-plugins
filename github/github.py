import re


class Github:
    """Checks for issue mentions in the message and responds to them.
    Made for the Modmail server."""
    async def on_message(self, message):
        match = re.match(r'modmail#(\d+)', message.content)
        if match:
            issue_num = match.group(1)
            await message.channel.send(f'https://github.com/kyb3r/modmail/issues/{issue_num}')


def setup(bot):
    bot.add_cog(Github())
