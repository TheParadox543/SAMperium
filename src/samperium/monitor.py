from re import match, search, findall

from nextcord import Guild, Member, Message, Role
from nextcord.ext.commands import Cog, Bot
from nextcord.utils import get

COUNTING_ID = 510016054391734273
COUNTABLE = 1119485526009974805
NUMSELLI_COUNTABLE = 1119488910632943656
CRAZY_COUNTABLE = 1119488960587112448


async def give_count_permission(
    saves: int, role: Role, counter: Member, guild: Guild, message: Message
):
    """Giving permission to count in respective bots"""
    if saves >= 1:
        if role in counter.roles:
            reaction = get(
                guild.emojis,
                name="foxheartattack",
            )
            if reaction is not None:
                await message.add_reaction(reaction)
        else:
            await counter.add_roles(
                role,
                reason="Has enough saves",
            )
            await message.channel.send(
                f"{counter.mention} can now count in <#{1017139366100992042}>"
            )
    else:
        if role in counter.roles:
            await counter.remove_roles(
                role,
                reason="Doesn't have enough saves",
            )
            await message.channel.send("Not enough saves")
        else:
            reaction = get(guild.emojis, name="nekogasp")
            if reaction is not None:
                await message.add_reaction(reaction)


def counting_check(m: Message):
    return m.author.id == COUNTING_ID


class Monitor(Cog):
    """Monitor the different bots and give permissions"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message):
        """Deal with messages"""
        if not isinstance(message.author, Member):
            return
        if not isinstance(message.guild, Guild):
            return

        # * c!vote
        if message.content.startswith("c!vote"):
            msg = await self.bot.wait_for("message", check=counting_check)
            if not isinstance(msg, Message):
                return
            if len(msg.embeds) != 1:
                return

            embed_content = msg.embeds[0].to_dict()
            if "description" not in embed_content:
                return
            embed_description = embed_content["description"]
            saves_str = findall("\d+", embed_description)  # type: ignore
            if len(saves_str) < 1:
                return
            saves = int(saves_str[0])
            countable = message.guild.get_role(COUNTABLE)
            if countable is None:
                return
            await give_count_permission(
                saves,
                countable,
                message.author,
                message.guild,
                msg,
            )

        # * c!user
        elif message.content.startswith("c!user"):
            msg = await self.bot.wait_for("message", check=counting_check)
            if not isinstance(msg, Message):
                return
            if len(msg.embeds) != 1:
                return

            embed_content = msg.embeds[0].to_dict()
            if "fields" not in embed_content:
                return
            embed_field = embed_content["fields"][0]
            field_value = embed_field["value"]
            saves_str = field_value.split("Saves: ")[1]
            saves = int(findall("\d", saves_str)[0])
            countable = message.guild.get_role(COUNTABLE)
            if countable is None:
                return
            await give_count_permission(
                saves,
                countable,
                message.author,
                message.guild,
                msg,
            )
            # await msg.channel.send(f"{saves}")


def setup(bot: Bot):
    bot.add_cog(Monitor(bot))
