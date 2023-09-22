from nextcord import Member, CategoryChannel, TextChannel
from nextcord.ext.commands import Bot, Cog

COUNTING_BOT = 510016054391734273
NUMSELLI_BOT = 726560538145849374
CRAZY_BOT = 935408554997874798
PARADOX_ID = 717240803789111345

COUNTING_CHANNEL = 1017139366100992042
CRAZY_CATEGORY = 1020098853690671114
NUMSELLI_CATEGORY = 1020098784358834237

DUCK_ROLE = 1017143547541078066
NUMSELLI_ROLE = 1115578157727219712
CRAZY_ROLE = 1115578109056516136

status = {"online", "offline"}

bot_channel_link = {
    COUNTING_BOT: COUNTING_CHANNEL,
    NUMSELLI_BOT: NUMSELLI_CATEGORY,
    CRAZY_BOT: CRAZY_CATEGORY,
}

bot_role = {
    COUNTING_BOT: DUCK_ROLE,
    NUMSELLI_BOT: NUMSELLI_ROLE,
    CRAZY_BOT: CRAZY_ROLE,
}


class Presence(Cog):
    """"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def lock_channel(self, bot_id: int):
        """Lock the channel if bot is offline"""
        channel = self.bot.get_channel(bot_channel_link[bot_id])
        if not isinstance(channel, TextChannel) and not isinstance(
            channel, CategoryChannel
        ):
            return
        role = channel.guild.get_role(bot_role[bot_id])
        if role is None:
            return
        permissions = channel.overwrites_for(role)
        permissions.send_messages = False
        await channel.set_permissions(role, overwrite=permissions)
        if isinstance(channel, TextChannel):
            await channel.send("Channel locked as bot is offline.")
        elif isinstance(channel, CategoryChannel):
            for item in channel.text_channels:
                await item.send("Channel locked as bot is offline.")

    async def unlock_channel(self, bot_id: int):
        """Unlock the channel if bot is offline"""
        channel = self.bot.get_channel(bot_channel_link[bot_id])
        if not isinstance(channel, TextChannel) and not isinstance(
            channel, CategoryChannel
        ):
            return
        role = channel.guild.get_role(bot_role[bot_id])
        if role is None:
            return
        permissions = channel.overwrites_for(role)
        permissions.send_messages = True
        await channel.set_permissions(role, overwrite=permissions)
        if isinstance(channel, TextChannel):
            await channel.send("Channel unlocked as bot is online.")
        elif isinstance(channel, CategoryChannel):
            for item in channel.text_channels:
                await item.send("Channel locked as bot is online.")

    @Cog.listener()
    async def on_presence_update(self, before: Member, after: Member):
        """Listen for when there is a change in presence"""
        if before.status != after.status and before.id in bot_channel_link:
            if before.status == "online" and after.status == "offline":
                await self.lock_channel(before.id)
            elif before.status == "offline" and after.status == "online":
                await self.unlock_channel(before.id)


def setup(bot: Bot):
    bot.add_cog(Presence(bot))
