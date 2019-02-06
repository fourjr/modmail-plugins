import json

import discord
from discord.ext import commands


class Welcomer:
    def __init__(self, bot):
        self.bot = bot
        # self.db = bot.plugin_db.get_partition(self)
        self.invite_cache = {}
        bot.loop.create_task(self.populate_invite_cache())

    async def populate_invite_cache(self):
        await self.bot.wait_until_ready()
        for g in self.bot.guilds:
            self.invite_cache[g.id] = {i for i in await g.invites()}

    async def get_used_invite(self, guild):
        """Checks which invite is used in join via the following strategies:
        1. Check if invite doesn't exist anymore
        2. Check invite uses
        """
        update_invite_cache = {i for i in await guild.invites()}

        for i in self.invite_cache[guild.id]:
            if i in update_invite_cache:
                # pass check 1
                try:
                    new_invite = next(inv for inv in update_invite_cache if inv.id == inv.id)
                except StopIteration:
                    continue
                else:
                    if new_invite.uses > i.uses:
                        return new_invite

    def apply_vars(self, member, message, invite):
        if invite is None:
            return message.format(
                member=member,
                guild=member.guild,
                bot=self.bot.user
            )
        else:
            return message.format(
                member=member,
                guild=member.guild,
                bot=self.bot.user,
                invite=invite
            )

    def apply_vars_dict(self, member, message, invite):
        for k, v in message.items():
            if isinstance(v, dict):
                message[k] = self.apply_vars_dict(member, v, invite)
            else:
                message[k] = self.apply_vars(member, v, invite)
        return message

    def format_message(self, member, message, invite):
        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            # message is not embed
            message = self.apply_vars(member, message, invite)
            message = {'content': message}
        else:
            # message is embed
            message = self.apply_vars_dict(member, message, invite)

            if any(i in message for i in ('embed', 'content')):
                message['embed'] = discord.Embed.from_data(message['embed'])
            else:
                message = None
        return message

    @commands.command()
    async def welcomer(self, ctx, channel: discord.TextChannel, *, message):
        """Sets up welcome command. Check [here](readme.md) for
        complex usage.
        Example usage: `welcomer #general Hello {member.name}
        """
        if message.startswith('http://'):
            # message is a URL
            if message.startswith('https://hasteb.in/'):
                message = 'https://hasteb.in/raw/' + message.split('/')[-1]

            async with self.bot.session.get(message) as resp:
                message = await resp.text()

        message = self.format_message(ctx.author, message, None)
        if message:
            await channel.send(**message)
            await self.db.find_one_and_update(
                {'_id': 'config'},
                {'$set': {'welcomer': {'channel': str(channel.id), 'message': message}}},
                upsert=True
            )
            await ctx.send(f'Message sent to {channel.mention} for testing.\nNote: invites cannot be rendered in test message')
        else:
            await ctx.send('Invalid welcome message syntax.')

    async def on_member_join(self, member):
        invite = await self.get_used_invite(member.guild)
        config = (await self.db.find_one({'_id': 'config'}))['welcomer']
        if config:
            channel = member.guild.get_channel(int(config['channel']))
            if channel:
                message = self.format_message(member, config['message'], invite)
                if message:
                    await channel.send(**message)
                else:
                    await channel.send('Invalid welcome message')
            else:
                print(f'Channel {channel.id} not found')


def setup(bot):
    bot.add_cog(Welcomer(bot))
