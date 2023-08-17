from datetime import datetime, timedelta
from decimal import ROUND_UP, Decimal, getcontext
from math import sqrt
from pprint import PrettyPrinter
from re import findall, match, search
from typing import cast

from nextcord import Embed, Guild, Member, Message, Role
from nextcord.ext.commands import Bot, Cog, Context, command, is_owner
from nextcord.utils import get

from database import get_data, save_data

COUNTING_BOT = 510016054391734273
NUMSELLI_BOT = 726560538145849374
CRAZY_BOT = 935408554997874798

COUNTABLE = 1017143547541078066
NUMSELLI_COUNTABLE = 1115578157727219712
CRAZY_COUNTABLE = 1115578109056516136

PRIME_CHANNEL_ID = 1020461234115579934

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


def prime(num: int):
    f = False
    for i in range(3, int(sqrt(num)) + 1, 2):
        if num % i == 0:
            f = True
    return f


def next_prime(num: int):
    f = True
    while f:
        if num % 2 == 1:
            num += 2
        else:
            num += 1
        f = prime(num)
    return num


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

        # * Message from users
        if len(message.content) > 1 and message.content == message.content[::-1]:
            rev_reaction = get(message.guild.emojis, name="alternating_peek")
            if rev_reaction is not None:
                await message.add_reaction(rev_reaction)

        # if message.channel.id == PRIME_CHANNEL_ID:
        #     try:
        #         number = int(message.content)
        #     except ValueError:
        #         return
        #   next_prime_number = next_prime(number)
        #   await message.channel.send(f"`Next: {next_prime_number}`")

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
            saves_str = findall(r"\d+", embed_description)
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

            numbers = findall(r"\d+", message.content)
            if len(numbers) == 1:
                user_id = int(numbers[0])
                user = message.guild.get_member(user_id)
            else:
                user = message.author

            embed_content = msg.embeds[0].to_dict()
            if user is None:
                await message.channel.send("Could not find the user")
                return
            if "fields" not in embed_content:
                return
            embed_field = embed_content["fields"][0]
            field_value = embed_field["value"]
            field_value = field_value.replace(",", "")
            number_list = findall(r"[0-9]+\.*[0-9]*", field_value)
            rate = float(number_list[0])
            correct = int(number_list[1])
            wrong = int(number_list[2])
            save_data(user, "counting", rate, correct, wrong, message.created_at)
            saves = int(number_list[5])
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
                saves = int(findall(r"\d", saves_str)[0])
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
                numbers = findall(r"\d+", embed_description)
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
            if "Stats for" not in embed_title:
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
            saves = int(findall(r"\d", saves_str)[0])
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

        # * Error from counting
        if (
            message.author.id == COUNTING_BOT
            and message.content is not None
            and len(message.embeds) == 0
            and "You have" in message.content
        ):
            content = message.content
            numbers = findall(r"\d+", content)
            user_id = int(numbers[0])
            user = message.guild.get_member(user_id)
            if user is None:
                await message.channel.send("Couldn't find who made the mistake")
                return
            countable = message.guild.get_role(COUNTABLE)
            if countable is None:
                return
            if "your saves" in content:
                saves = int(numbers[2])
            else:
                saves = 0
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
            and "has used a" in message.content
        ):
            content = message.content
            numbers = findall(r"\d+", content)
            user_id = int(numbers[0])
            user = message.guild.get_member(user_id)
            if user is None:
                await message.channel.send("Couldn't find who made the mistake")
                return
            countable = message.guild.get_role(CRAZY_COUNTABLE)
            if countable is None:
                return
            if "has used a save" in content:
                saves = int(numbers[1])
            elif "has used a channel save" in content:
                saves = 0
            else:
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
            await member.remove_roles(role, reason="Clearing roles from users")
            await ctx.send(f"{role} removed from {member.name}")

    @command(name="rankup", aliases=["ru"])
    async def rankup_cmd(self, ctx: Context, member: Member | None = None):
        """Shows the number of counts required to increase stats"""

        user = cast(Member, member or ctx.author)
        msg = ""

        user_data = get_data(user)
        if user_data is None:
            await ctx.send("Run counting commands first!")
            return

        og_post = user_data.get("counting")
        if (
            og_post is not None
            and og_post.get("time") + timedelta(minutes=30) > datetime.utcnow()
        ):
            correct = Decimal(og_post.get("correct", 0))
            wrong = Decimal(og_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct / total).quantize(Decimal("1.00000"))
            if rate >= Decimal("0.9998"):
                msg += "`counting`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                new_rate = rate + Decimal("0.000005")
                x = ((new_rate * total - correct) / (Decimal("1") - new_rate)).quantize(
                    Decimal("1"), ROUND_UP
                )
                new_cor = correct + x
                new_rate = (new_rate * 100).quantize(Decimal("10.000"), ROUND_UP)
                msg += f"`counting`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"

        classic_post = user_data.get("classic")
        if (
            classic_post is not None
            and classic_post.get("time") + timedelta(minutes=30) > datetime.utcnow()
        ):
            correct = Decimal(classic_post.get("correct", 0))
            wrong = Decimal(classic_post.get("wrong", 0))
            total = correct + wrong
            rate = (correct / total).quantize(Decimal("1.00000"))
            if rate >= Decimal("0.9998"):
                msg += "`classic`: The bot can't calculate the number of counts "
                msg += "you need to rank up\n"
            else:
                getcontext().prec = 8
                new_rate = rate + Decimal("0.000005")
                x = ((new_rate * total - correct) / (1 - new_rate)).quantize(
                    Decimal("1"), ROUND_UP
                )
                new_cor = correct + x
                new_rate = (new_rate * 100).quantize(Decimal("10.000"))
                msg += f"`classic`: Rank up to {new_rate}% at **{new_cor}**. "
                msg += f"You need ~**{x}** more numbers.\n"

        if msg == "":
            msg = "Run counting commands first!"

        title_msg = f"Rank up stats for {user.display_name}"
        embedVar = Embed(title=title_msg, description=msg)
        await ctx.send(embed=embedVar)


def setup(bot: Bot):
    bot.add_cog(Monitor(bot))
