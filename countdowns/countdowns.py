import asyncio
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from core import checks
from core.time import UserFriendlyTime
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class Countdowns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        self.bot.loop.create_task(self.setup_countdowns())

    async def setup_countdowns(self):
        countdowns = await self.db.find().to_list(None)
        for i in countdowns:
            if i['_id'] != 'config':
                self.bot.loop.create_task(self.trigger_countdown(i))

    async def category(self, ctx):
        config = await self.db.find_one({'_id': 'config'})
        category = False
        if config:
            category = self.bot.get_channel(int(config.get('category', 0)))

        if not category:
            category = await ctx.guild.create_category(name='Countdowns', overwrites={
                ctx.guild.default_role: discord.PermissionOverwrite(connect=False)
            })

            await self.db.find_one_and_update({'_id': 'config'}, {'$set': {'category': str(category.id)}}, upsert=True)
        
        return category

    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.group(invoke_without_command=True)
    async def countdown(self, ctx):
        await ctx.send_help(ctx.command)

    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @countdown.command(usage='<name> <time>')
    async def create(self, ctx, *, time: UserFriendlyTime):
        """Starts a countdown"""
        if await self.db.find_one({'name': time.arg}):
            await ctx.send('Countdown already created')
            return

        if time.dt <= datetime.utcnow():
            raise commands.BadArgument('Invalid time provided')
        if not time.arg:
            raise commands.BadArgument('Invalid name provided')

        try:
            category = await self.category(ctx)
            channel = await ctx.guild.create_voice_channel(name=time.arg, category=category)
        except discord.Forbidden:
            await ctx.send('Bot has insufficient permissions to manage voice channels and category. Allow the bot to "Manage Channels"')
            return

        data = {'name': time.arg, 'date': time.dt.isoformat(), 'channel_id': str(channel.id)}
        await self.db.insert_one(data)
        self.bot.loop.create_task(self.trigger_countdown(data))

        await ctx.send('Countdown created! View the voice channels in the "Countdowns" category.')

    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @countdown.command()
    async def update(self, ctx, *, name):
        """Updates a countdown"""
        data = await self.db.find_one({'name': name})
        if not data:
            await ctx.send('Unable to find countdown')
            return

        channel = self.bot.get_channel(int(data['channel_id']))
        if not channel:
            await ctx.send('Unable to find channel, removing countdown')
            await self.db.find_one_and_delete(data)
            return

        try:
            await self.update(data['name'], datetime.fromisoformat(data['date']), channel)
        except discord.Forbidden:
            await ctx.send('Bot has insufficient permissions to manage voice channels. Allow the bot to "Manage Channels"')
            return
        await ctx.send('Updated')

    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @countdown.command()
    async def delete(self, ctx, *, name):
        """Delete a countdown"""
        data = await self.db.find_one({'name': name})
        if not data:
            await ctx.send('Unable to find countdown')
            return

        channel = self.bot.get_channel(int(data['channel_id']))
        if channel:
            await channel.delete()

        await self.db.find_one_and_delete({'name': name})
        await ctx.send('Deleted')

    async def trigger_countdown(self, data):
        # data: Dict[name, date, channel_id]
        channel = self.bot.get_channel(int(data['channel_id']))
        if not channel:
            logger.warning('No channel found for %s, removing countdown', data['name'])
            await self.db.find_one_and_delete(data)
            return

        while True:
            try:
                if not await self.update(data['name'], datetime.fromisoformat(data['date']), channel):
                    return
            except discord.Forbidden:
                logger.error('Bot has insufficient permissions to manage voice channels. Allow the bot to "Manage Channels"')
                return

    async def update(self, name, date, channel):
        seconds = round((date - datetime.utcnow()).total_seconds())
        if seconds < 0:
            await channel.edit(name=name)
            logger.info('Countdown %s has ended, removing countdown', name)
            await self.db.find_one_and_delete({'name': name, 'date': date.isoformat(), 'channel_id': str(channel.id)})
            return False

        # months, days, hours, minute, second
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        months, days = divmod(days, 30)

        if months > 1:
            if days > 15:
                months += 1
            await channel.edit(name=f"{name}: {months} months")
            await asyncio.sleep(timedelta(months=1).total_seconds())

        elif days > 1:
            days += months * 30 + minutes / 60 / 24 + seconds / 60 / 60 / 24
            days = round(days)

            await channel.edit(name=f"{name}: {days} days")
            await asyncio.sleep(timedelta(days=1).total_seconds())

        elif hours > 1:
            hours += months * 30 + days * 24 + minutes / 60 + seconds / 60 / 60
            hours = round(hours)

            await channel.edit(name=f"{name}: {hours} hours")
            await asyncio.sleep(timedelta(hours=1).total_seconds())

        elif minutes > 1:
            minutes += months * 30 + days * 24 + hours * 60 + seconds / 60
            minutes = round(minutes)

            await channel.edit(name=f"{name}: {minutes} minutes")
            await asyncio.sleep(60)

        elif seconds:
            seconds += months * 30 + days * 24 + hours * 60 + minutes * 60
            seconds = round(seconds)

            await channel.edit(name=f"{name}: A few seconds")
            await asyncio.sleep(seconds)

        else:
            await channel.edit(name=f"{name}")
            logger.info('Countdown %s has ended, removing countdown', name)
            return False
        
        logger.info('Updated countdown %s', name)
        return True

def setup(bot):
    bot.add_cog(Countdowns(bot))
