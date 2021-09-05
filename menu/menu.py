import asyncio
import copy

import discord
from discord.ext import commands
from discord.ext.commands.view import StringView

from core import checks
from core.models import DummyMessage, PermissionLevel
from core.utils import normalize_alias


class Menu(commands.Cog):
    """Reaction-based menu for threads"""
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        """Sends out menu to user"""
        menu_config = await self.db.find_one({'_id': 'config'})
        if menu_config:
            message = DummyMessage(copy.copy(initial_message))
            message.author = self.bot.modmail_guild.me
            message.content = menu_config['content']
            msgs, _ = await thread.reply(message)
            main_recipient_msg = None

            for m in msgs:
                if m.channel.recipient == thread.recipient:
                    main_recipient_msg = m
                    break

            for r in menu_config['options']:
                await main_recipient_msg.add_reaction(r)
                await asyncio.sleep(0.3)

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r, u: r.message == main_recipient_msg and u == thread.recipient and str(r.emoji) in menu_config['options'], timeout=120)
            except asyncio.TimeoutError:
                message.content = 'No reaction received in menu... timing out'
                await thread.reply(message)
            else:
                alias = menu_config['options'][str(reaction.emoji)]

                ctxs = []
                if alias is not None:
                    ctxs = []
                    aliases = normalize_alias(alias)
                    for alias in aliases:
                        view = StringView(self.bot.prefix + alias)
                        ctx_ = commands.Context(prefix=self.bot.prefix, view=view, bot=self.bot, message=message)
                        ctx_.thread = thread
                        discord.utils.find(view.skip_string, await self.bot.get_prefix())
                        ctx_.invoked_with = view.get_word().lower()
                        ctx_.command = self.bot.all_commands.get(ctx_.invoked_with)
                        ctxs += [ctx_]

                for ctx in ctxs:
                    if ctx.command:
                        old_checks = copy.copy(ctx.command.checks)
                        ctx.command.checks = [checks.has_permissions(PermissionLevel.INVALID)]

                        await self.bot.invoke(ctx)

                        ctx.command.checks = old_checks
                        continue

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def configmenu(self, ctx):
        """Creates a new menu"""
        config = {}

        try:
            await ctx.send('What is the menu message?')
            m = await self.bot.wait_for('message', check=lambda x: ctx.message.channel == x.channel and ctx.message.author == x.author, timeout=300)
            config['content'] = m.content

            await ctx.send('How many options are available?')
            m = await self.bot.wait_for('message', check=lambda x: ctx.message.channel == x.channel and ctx.message.author == x.author and x.content.isdigit(), timeout=300)
            options_len = int(m.content)
            config['options'] = {}

            for _ in range(options_len):
                await ctx.send('What is the option emoji?')
                while True:
                    m = await self.bot.wait_for('message', check=lambda x: ctx.message.channel == x.channel and ctx.message.author == x.author, timeout=300)
                    try:
                        await m.add_reaction(m.content)
                    except discord.HTTPException:
                        await ctx.send('Invalid emoji. Send another.')
                    else:
                        emoji = m.content
                        break

                await ctx.send('What is the option command? (e.g. `reply Transferring && move 1238343847384`)')
                m = await self.bot.wait_for('message', check=lambda x: ctx.message.channel == x.channel and ctx.message.author == x.author, timeout=300)
                config['options'][emoji] = m.content
        except asyncio.TimeoutError:
            await ctx.send('Timeout. Re-run the command to create a menu.')
        else:
            await self.db.find_one_and_update({'_id': 'config'}, {'$set': config}, upsert=True)
            await ctx.send('Success')

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def clearmenu(self, ctx):
        """Removes an existing menu"""
        await self.db.find_one_and_delete({'_id': 'config'})
        await ctx.send('Success')


def setup(bot):
    bot.add_cog(Menu(bot))
