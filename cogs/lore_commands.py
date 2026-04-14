import discord
from discord.ext import commands
from utils.data_loader import load_data

class LoreCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_universe_data(self, ctx):
        channel_name = ctx.channel.name
        return load_data(channel_name)

    @commands.command()
    async def bio(self, ctx, *, name: str):
        data = self.get_universe_data(ctx)

        if not data:
            await ctx.send("No lore data found for this channel.")
            return

        character = data.get("characters", {}).get(name.lower())

        if not character:
            await ctx.send("Character not found.")
            return

        embed = discord.Embed(
            title=name.title(),
            description=character["description"],
            color=discord.Color.blue()
        )

        embed.add_field(name="Title", value=character["title"], inline=False)
        embed.add_field(name="Parent", value=character["parent"], inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def location(self, ctx, *, name: str):
        data = self.get_universe_data(ctx)

        if not data:
            await ctx.send("No lore data found.")
            return

        location = data.get("locations", {}).get(name.lower())

        if not location:
            await ctx.send("Location not found.")
            return

        embed = discord.Embed(
            title=name.title(),
            description=location["description"],
            color=discord.Color.green()
        )

        npcs = ", ".join(location.get("notable_npcs", []))
        embed.add_field(name="Notable NPCs", value=npcs or "None", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LoreCommands(bot))