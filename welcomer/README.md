# Installation
Run this command in Modmail: `plugin add welcomer`

# Permission needed to function
`MANAGE_GUILD` (used to view invites)

# Variables
| Name     | Description |
| -------- | ------------------------------------------------------------------------------------------------------ |
| `member` | [Member](https://discordpy.readthedocs.io/en/rewrite/api.html#discord.Member) that joined the server.  |
| `guild`  | [Guild](https://discordpy.readthedocs.io/en/rewrite/api.html#discord.Guild) that the member joined.    |
| `bot`    | [ClientUser](https://discordpy.readthedocs.io/en/rewrite/api.html#discord.ClientUser) of the bot.      |
| `invite` | [Invite](https://discordpy.readthedocs.io/en/rewrite/api.html#discord.Invite) used to join the server. |

Example: `Welcome {member.mention} to {guild.name}! He used {invite.code} to join the server (invite created by {invite.inviter.name})`

# Embeds
For embeds, you'd have to send the JSON representation of the embed.    
1. You can use [this tool](https://leovoel.github.io/embed-visualizer/) to generate JSON representations.
2. Copy the JSON from the left and paste it into [hastebin](https://hasteb.in/). Save it (`Ctrl` + `S` or the save button on the right)
3. Copy the URL and paste it into Discord
4. Your final command would then be `welcomer #general https://hasteb.in/theurl`.

##### If you want to use your own text saver thing instead of hastebin, send the raw URL.
For example: https://hasteb.in/raw/about.md
