import base64
import glob
import os
import tempfile
import typing
import zipfile

import aiohttp
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class EmoteManager(commands.Cog):
    """Manage custom emojis in your server"""

    def __init__(self, bot):
        self.bot = bot

    async def compress_image(self, url):
        auth = aiohttp.BasicAuth("api", os.environ["TINIFY_APIKEY"])
        async with self.bot.session.post(
            'https://api.tinify.com/shrink',
            auth=auth,
            json={"source": {"url": url}}
        ) as resp:
            if resp.status == 201:
                response_data = await resp.json()
                output_url = response_data['output']['url']
            else:
                raise commands.BadArgument('Unable to compress image, try to upload an image < 256kb')

        async with self.bot.session.get(output_url) as resp:
            return await resp.read()

    @commands.group(invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def emoji(self, ctx):
        """Manage custom emojis in your server"""
        await ctx.send_help(ctx.command)

    @emoji.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def add(self, ctx, name: str, *, link: typing.Union[discord.PartialEmoji, str] = None):
        """Add an emoji to the server

        If a link is provided, the emoji will be downloaded from that link.
        If a custom emoji is provided, the emoji will be downloaded there.
        If neither are provided, the bot will look at the image attachment.
        """
        if isinstance(link, discord.PartialEmoji):
            link = str(link.url)

        if link is None:
            if ctx.message.attachments:
                link = ctx.message.attachments[0].url
                filename = ctx.message.attachments[0].filename
                if (
                    not filename.endswith(".png")
                    and not filename.endswith(".jpg")
                    and not filename.endswith(".jpeg")
                    and not filename.endswith(".gif")
                ):
                    raise commands.BadArgument("Invalid attachment, please ensure it is an imagae.")

        if link is None:
            # if after trying to find attachment link is still None
            raise commands.BadArgument("A link or attachment image is needed")

        if not link.startswith("http"):
            raise commands.BadArgument("Please provide a valid link.")

        async with self.bot.session.get(link) as resp:
            data = await resp.read()

        kb = len(data) / 1000
        if kb > 256:
            data = await self.compress_image(link)

        kb = len(data) / 1000
        if kb > 256:
            # if still more than 256
            raise commands.BadArgument('Unable to compress image, try to upload an image < 256kb')

        await ctx.guild.create_custom_emoji(name=name, image=data)
        await ctx.send("Emoji added.")

    @emoji.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def delete(self, ctx, emoji: discord.Emoji):
        """Remove an emoji from the server"""
        await emoji.delete()
        await ctx.send("Emoji removed.")

    @emoji.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def rename(self, ctx, emoji: discord.Emoji, *, new_name: str):
        """Rename an emoji"""
        await emoji.edit(name=new_name)
        await ctx.send("Emoji renamed.")

    @emoji.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def display(self, ctx):
        """List all emojis in the server"""
        emojis = [str(e) for e in ctx.guild.emojis]
        await ctx.send(" ".join(emojis))

    @emoji.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def export(self, ctx):
        """Export all emojis to a zip file"""
        await ctx.send("Generating zip file...")
        async with ctx.typing():
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(f"{tmpdir}/emojis.zip", "w") as zipf:
                    for e in ctx.guild.emojis:
                        extension = "gif" if e.animated else "png"

                        with open(f"{tmpdir}/{e.name}.{extension}", "wb") as f:
                            await e.url.save(f)
                        zipf.write(f"{tmpdir}/{e.name}.{extension}", f"{e.name}.{extension}")

                await ctx.send(file=discord.File(f"{tmpdir}/emojis.zip"))

    @emoji.command(name="import")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def _import(self, ctx):
        """Import emojis from a zip file"""
        attachment = None
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            if not ctx.message.attachments[0].filename.endswith(".zip"):
                raise commands.BadArgument("Invalid attachment, please ensure it is a zip file.")

        if attachment is None:
            raise commands.BadArgument("Attach a zip file.")

        current_emojis = [e.name for e in ctx.guild.emojis]

        await ctx.send("Parsing zip file...")
        async with ctx.typing():
            with tempfile.TemporaryDirectory() as tmpdir:
                await attachment.save(f"{tmpdir}/emojis.zip")
                with zipfile.ZipFile(f"{tmpdir}/emojis.zip", "r") as zipf:
                    zipf.extractall(tmpdir)

                extensions = [".gif", ".png", ".jpeg", ".jpg"]
                for ex in extensions:
                    for fp in glob.iglob(f"{tmpdir}/*{ex}"):
                        fn = os.path.split(fp)[1]
                        name = fn.replace(ex, "")
                        if name in current_emojis:
                            continue

                        with open(fp, "rb") as f:
                            data = f.read()
                        await ctx.guild.create_custom_emoji(name=name, image=data)

            await ctx.send("Emojis added")


def setup(bot):
    bot.add_cog(EmoteManager(bot))
