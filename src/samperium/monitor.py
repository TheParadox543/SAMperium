from re import match, search, findall
from pprint import PrettyPrinter

from nextcord import Guild, Member, Message, Role
from nextcord.ext.commands import Cog, Bot, command, Context, is_owner
from nextcord.utils import get

COUNTING_BOT = 510016054391734273
NUMSELLI_BOT = 726560538145849374
CRAZY_BOT = 935408554997874798

COUNTABLE = 1017143547541078066
NUMSELLI_COUNTABLE = 1115578157727219712
CRAZY_COUNTABLE = 1115578109056516136

pp = PrettyPrinter(indent=4)


async def give_count_permission(
    saves: int,
    role: Role,
    counter: Member,
    guild: Guild,
    message: Message,
    bot: int,
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
                f"{counter.mention} can now count with <@{bot}>."
            )
    else:
        if role in counter.roles:
            await counter.remove_roles(
                role,
                reason="Doesn't have enough saves",
            )
            await message.channel.send(
                f"{counter.mention} doesn't have enough saves to count with <@{bot}>."
            )
        else:
            reaction = get(guild.emojis, name="nekogasp")
            if reaction is not None:
                await message.add_reaction(reaction)


def counting_check(m: Message):
    return m.author.id == COUNTING_BOT


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
                COUNTING_BOT,
            )

        # * c!user
        elif message.content.startswith("c!user"):
            msg = await self.bot.wait_for("message", check=counting_check)
            if not isinstance(msg, Message):
                return
            if len(msg.embeds) != 1:
                return

            embed_content = msg.embeds[0].to_dict()
            user_name = embed_content.get("title")
            if user_name is None:
                return
            await message.channel.send(user_name.split("#")[0])
            user = message.guild.get_member_named(user_name.split("#")[0])
            await message.channel.send(f"Counter is: {user}")
            if user is None:
                return
            if "fields" not in embed_content:
                return
            embed_field = embed_content["fields"][0]
            field_value = embed_field["value"]
            saves_str = field_value.split("Saves: ")[1]
            saves = int(findall("\d", saves_str)[0])  # type: ignore
            countable = message.guild.get_role(COUNTABLE)
            if countable is None:
                return
            await give_count_permission(
                saves,
                countable,
                user,
                message.guild,
                msg,
                COUNTING_BOT,
            )

        # * Numselli
        elif message.author.id == NUMSELLI_BOT and len(message.embeds) == 1:
            embed_content = message.embeds[0].to_dict()
            embed_title = embed_content.get("title")
            if embed_title is None:
                return

            # * Numselli user
            if embed_title.startswith("Stats"):
                user_name = embed_title.split("Stats for ")[1]
                if user_name is None:
                    return
                user = message.guild.get_member_named(user_name)
                if user is None:
                    return
                if "fields" not in embed_content:
                    return
                embed_field = embed_content["fields"][0]
                field_value = embed_field["value"]
                saves_str = field_value.split("Saves left: ")[1]
                saves = int(findall("\d", saves_str)[0])  # type: ignore
                countable = message.guild.get_role(NUMSELLI_COUNTABLE)
                if countable is None:
                    return
                await give_count_permission(
                    saves,
                    countable,
                    user,
                    message.guild,
                    message,
                    NUMSELLI_BOT,
                )

            # * Numselli error
            elif embed_title.startswith("Save Used"):
                embed_description = embed_content.get("description")
                if embed_description is None:
                    await message.channel.send("Could not read embed")
                    return
                numbers = findall("\d+", embed_description)  # type: ignore
                user_id = int(numbers[0])
                saves = int(numbers[1])
                user = message.guild.get_member(user_id)
                if user is None:
                    await message.channel.send("Could not identify the user")
                    return
                countable = message.guild.get_role(NUMSELLI_COUNTABLE)
                if countable is None:
                    return
                await give_count_permission(
                    saves,
                    countable,
                    user,
                    message.guild,
                    message,
                    NUMSELLI_BOT,
                )

        # * Crazy Counting user
        elif message.author.id == CRAZY_BOT and len(message.embeds) == 1:
            embed_content = message.embeds[0].to_dict()
            embed_title = embed_content.get("title")
            if embed_title is None:
                return
            user_name = embed_title.split("Stats for ")[1]
            if user_name is None:
                return
            user = message.guild.get_member_named(user_name.split("#")[0])
            if user is None:
                return
            if "fields" not in embed_content:
                return
            embed_field = embed_content["fields"][0]
            field_value = embed_field["value"]
            saves_str = field_value.split("Saves: ")[1]
            saves = int(findall("\d", saves_str)[0])  # type: ignore
            countable = message.guild.get_role(CRAZY_COUNTABLE)
            if countable is None:
                return
            await give_count_permission(
                saves,
                countable,
                user,
                message.guild,
                message,
                CRAZY_BOT,
            )
            # await message.channel.send(f"{field_value}")

        # * Error from counting
        if (
            message.author.id == COUNTING_BOT
            and message.content is not None
            and len(message.embeds) == 0
            and "You have" in message.content
        ):
            content = message.content
            numbers = findall("\d+", content)  # type: ignore
            user_id = int(numbers[0])
            saves = int(numbers[2])
            user = message.guild.get_member(user_id)
            if user is None:
                await message.channel.send("Couldn't find who made the mistake")
                return
            countable = message.guild.get_role(COUNTABLE)
            if countable is None:
                return
            await give_count_permission(
                saves,
                countable,
                user,
                message.guild,
                message,
                COUNTING_BOT,
            )

        # * Error from crazy counting
        if (
            message.author.id == CRAZY_BOT
            and message.content is not None
            and len(message.embeds) == 0
            and "has used a save" in message.content
        ):
            content = message.content
            numbers = findall("\d+", content)  # type: ignore
            user_id = int(numbers[0])
            saves = int(numbers[1])
            user = message.guild.get_member(user_id)
            if user is None:
                await message.channel.send("Couldn't find who made the mistake")
                return
            countable = message.guild.get_role(CRAZY_COUNTABLE)
            if countable is None:
                return
            await give_count_permission(
                saves,
                countable,
                user,
                message.guild,
                message,
                COUNTING_BOT,
            )

    @command(name="clear")
    @is_owner()
    async def remove_roles(self, ctx: Context, role: Role):
        """Remove all users from the role"""
        for member in role.members:
            # if member.name == "paradox543":
            await member.remove_roles(role, reason="Clearing roles from users")
            await ctx.send(f"{role} removed from {member.name}")


def setup(bot: Bot):
    bot.add_cog(Monitor(bot))
