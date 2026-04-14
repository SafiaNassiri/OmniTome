import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Load command files
async def load_cogs():
    await bot.load_extension("cogs.lore_commands")

import asyncio
asyncio.run(load_cogs())

bot.run(TOKEN)