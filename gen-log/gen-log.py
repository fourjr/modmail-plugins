import io

import dateutil
import discord
from discord.ext import commands


class GenLog(commands.Cog):
    """Sets up a log txt file generator to be sent on thread close"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_thread_close(self, thread, closer, silent, delete_channel, message, scheduled):
        text = self.get_log_message(await self.bot.api.get_log(thread.channel.id))
        with io.StringIO() as f:
            f.write(text)
            f.seek(0)
            await self.bot.log_channel.send(file=discord.File(f, f"Modmail-Log-{thread.recipient}.txt"))

    def get_log_message(self, thread):
        # From the logviewer's plain text functionality: https://github.com/kyb3r/logviewer/blob/master/core/models.py#L65-L109
        messages = thread["messages"]
        thread_create_time = dateutil.parser.parse(thread["created_at"]).strftime("%d %b %Y - %H:%M UTC")
        out = f"Thread created at {thread_create_time}\n"

        if thread['creator']['id'] == thread['recipient']['id'] and thread['creator']['mod'] == thread['recipient']['mod']:
            out += f"[R] {thread['creator']['name']} "
            out += f"({thread['creator']['id']}) created a Modmail thread. \n"
        else:
            out += f"[M] {thread['creator']['name']} "
            out += f"created a thread with [R] "
            out += f"{thread['recipient']['name']} ({thread['recipient']['id']})\n"

        out += "────────────────────────────────────────────────\n"

        def get_visibility_label(message):
            msg_type = (message.get("type") or "").lower()

            if msg_type == "internal":
                return "[INTERNAL]"
            if msg_type == "note":
                return "[NOTE]"
            if msg_type in {"thread_message", "anonymous"}:
                return "[SENT]"
            return "[UNKNOWN]"

        if messages:
            for index, message in enumerate(messages):
                next_index = index + 1 if index + 1 < len(messages) else index
                curr, next_ = message["author"], messages[next_index]["author"]

                author = curr
                user_type = "M" if author["mod"] else "R"
                create_time = dateutil.parser.parse(message["timestamp"]).strftime("%d/%m %H:%M")

                visibility = get_visibility_label(message)

                base = f"{create_time} {visibility} {user_type} "
                base += f"{author['name']}: {message['content']}\n"

                for attachment in message["attachments"]:
                    base += f"Attachment [{attachment['filename']}]: {attachment['url']}\n"

                out += base

                if curr != next_:
                    out += "────────────────────────────────\n"

        if not thread["open"]:
            if messages:
                out += "────────────────────────────────────────────────\n"

            out += f"[M] {thread['closer']['name']} ({thread['closer']['id']}) "
            out += "closed the Modmail thread. \n"

            closed_time = dateutil.parser.parse(thread["closed_at"]).strftime("%d %b %Y - %H:%M UTC")
            out += f"Thread closed at {closed_time} \n"

        return out


async def setup(bot):
    await bot.add_cog(GenLog(bot))
