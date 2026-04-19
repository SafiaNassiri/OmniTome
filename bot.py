import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} | Slash commands synced")

async def main():
    async with bot:
        await bot.load_extension("cogs.lore_commands")
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())