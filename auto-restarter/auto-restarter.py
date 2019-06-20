import requests
import os
import logging
from discord.ext import commands


logger = logging.getLogger("Modmail")
logger.setLevel(logging.INFO)


@commands.Cog()
class AutoRestarter:
    """This plugin automatically starts another Heroku application
    when the first app dies.

    * 2 accounts must be used
    * Only 1 app can exist on each account
    * Each app must be named "$(APP_NAME)-1", "$(APP_NAME)-2"
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        bot.loop.create_task(self.send_payload('login'))

    def cog_unload(self):
        self.bot.loop.create_task(self.send_payload('logout'))

    async def send_payload(self, mode):
        db_data = await self.db.find_one({'_id': 'autorestarter'})

        try:
            requests.get(f'https://{db_data["startup_url"]}/{mode}/{os.environ["HEROKU_APP_NAME"]}')
        except KeyError:
            logger.warning(f'<autorestarter> startup_url is not set or HEROKU_APP_NAME is not set in environment variables. Unable to send {mode} payload. Read https://github.com/fourjr/modmail-plugins/blob/master/auto-restarter/README.md', exc_info=True)
        else:
            logger.info(f'<autorestarter> Successfully sent {mode} payload')

    @commands.command()
    async def setuprestarter(self, ctx, *, url):
        """Setup the AutoRestarter cog
        Url parameter should be the URL of the webserver to ping.
        Host it off https://github.com/fourjr/heroku-startup

        [Read more](https://github.com/fourjr/modmail-plugins/blob/master/auto-restarter/README.md)
        """
        if not url.startswith('http') or url.count('/') > 3:
            # / can appear in at most: https://a.com/
            await ctx.send('Invalid url. Refer to https://github.com/fourjr/modmail-plugins/blob/master/auto-restarter/README.md')
        else:
            await self.db.find_one_and_update({'_id': 'autorestarter'}, {'$set': {'startup_url': url}})
            await ctx.send('Changes saved. Remeber to set `HEROKU_APP_NAME` in the environment variables. Read <https://github.com/fourjr/modmail-plugins/blob/master/auto-restarter/README.md>')


def setup(bot):
    bot.add_cog(AutoRestarter(bot))
