import os

from dotenv import load_dotenv
from nextcord import Game, Intents, Interaction
from nextcord.ext.commands import Bot, Context

load_dotenv()

intents = Intents.all()

bot = Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Notify when bot is ready"""
    await bot.change_presence(activity=Game("Testing"))
    print(f"We have logged in as {bot.user}")


@bot.slash_command()
async def ping(ctx: Interaction):
    await ctx.send("Pong")


@bot.command(name="ping")
async def pingable(ctx: Context):
    """"""
    await ctx.send("Pong")


@bot.slash_command(name="reload")
async def reload(ctx: Interaction, name: str):
    """"""
    bot.reload_extension(name)
    await ctx.send(f"{name} is reloaded")


@bot.command(name="reload")
async def reload_command(ctx: Context, name: str):
    bot.reload_extension(name)
    await ctx.send(f"{name} is reloaded")


bot.load_extensions(
    [
        "monitor",
    ]
)


bot.run(os.getenv("SAMPERIUM"))
