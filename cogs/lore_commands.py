import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from utils.data_loader import load_data, save_data, get_file_path

EMBED_COLORS = {
    "character": discord.Color.from_rgb(138, 79, 179),
    "location": discord.Color.from_rgb(46, 139, 87),
    "faction": discord.Color.from_rgb(200, 80, 80),
    "item": discord.Color.from_rgb(200, 160, 40),
    "timeline": discord.Color.from_rgb(60, 160, 200),
    "success": discord.Color.from_rgb(100, 200, 150),
    "error": discord.Color.from_rgb(200, 70, 70),
    "help": discord.Color.from_rgb(90, 130, 200),
    "custom": discord.Color.from_rgb(200, 150, 50),
}

def error_embed(title, message, suggestion=None):
    embed = discord.Embed(title=f"❌ {title}", description=message, color=EMBED_COLORS["error"])
    if suggestion:
        embed.add_field(name="💡 Try this instead", value=f"`{suggestion}`", inline=False)
    embed.set_footer(text="Use /help for a full command list.")
    return embed

def is_admin():
    async def predicate(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(embed=error_embed(
                "Permission Denied",
                "Only administrators can use this command."
            ), ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

class LoreCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- HELP ---

    @app_commands.command(name="help", description="Show all available Archivist commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 The Archivist — Command Reference",
            description="All commands are channel-aware. Lore is scoped to the channel you're in.",
            color=EMBED_COLORS["help"]
        )
        embed.add_field(name="🧍 Characters", value="`/bio` `/addcharacter` `/deletecharacter` `/edit type:character`", inline=False)
        embed.add_field(name="🗺️ Locations", value="`/location` `/addlocation` `/deletelocation` `/edit type:location`", inline=False)
        embed.add_field(name="⚔️ Factions", value="`/faction` `/addfaction` `/deletefaction`", inline=False)
        embed.add_field(name="🗡️ Items", value="`/item` `/additem` `/deleteitem`", inline=False)
        embed.add_field(name="📅 Timeline", value="`/timeline` `/addevent` `/deleteevent`", inline=False)
        embed.add_field(name="⚙️ Custom Commands", value="`/addcommand` `/cmd` `/deletecommand`", inline=False)
        embed.add_field(name="🔍 Search & Tools", value="`/search` `/export` `/list`", inline=False)
        embed.set_footer(text="The Archivist • Your Lore Keeper")
        await interaction.response.send_message(embed=embed)

    # --- BIO ---

    @app_commands.command(name="bio", description="Look up a character's lore entry")
    @app_commands.describe(name="The character's name")
    async def bio(self, interaction: discord.Interaction, name: str):
        data = load_data(interaction.channel.name)
        if not data:
            await interaction.response.send_message(embed=error_embed("No lore found", "This channel has no lore file yet.", "/addcharacter"))
            return
        character = data.get("characters", {}).get(name.lower())
        if not character:
            close = [k for k in data.get("characters", {}) if name.lower() in k]
            suggestion = f"/bio name:{close[0].title()}" if close else "/list type:characters"
            await interaction.response.send_message(embed=error_embed("Character not found", f"No character named **{name.title()}** exists here.", suggestion))
            return
        embed = discord.Embed(title=f"🧍 {name.title()}", description=character["description"], color=EMBED_COLORS["character"])
        embed.add_field(name="Title", value=character["title"], inline=True)
        embed.add_field(name="Parent", value=character["parent"], inline=True)
        embed.set_footer(text=f"#{interaction.channel.name} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addcharacter", description="Add a character to this channel's lore")
    @app_commands.describe(name="Character's name", title="Their title or role", description="A short bio", parent="Their parent or origin")
    async def add_character(self, interaction: discord.Interaction, name: str, title: str, description: str, parent: str):
        channel = interaction.channel.name
        data = load_data(channel) or {"characters": {}, "locations": {}, "factions": {}, "items": {}, "timeline": [], "custom_commands": {}}
        data.setdefault("characters", {})[name.lower()] = {"title": title, "description": description, "parent": parent}
        save_data(channel, data)
        embed = discord.Embed(title=f"✅ Character Added: {name.title()}", color=EMBED_COLORS["character"])
        embed.add_field(name="Title", value=title, inline=True)
        embed.add_field(name="Parent", value=parent, inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        embed.set_footer(text=f"#{channel} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deletecharacter", description="Delete a character (Admin only)")
    @app_commands.describe(name="Character's name")
    @is_admin()
    async def delete_character(self, interaction: discord.Interaction, name: str):
        channel = interaction.channel.name
        data = load_data(channel)
        if not data or name.lower() not in data.get("characters", {}):
            await interaction.response.send_message(embed=error_embed("Not found", f"No character named **{name.title()}** exists here."))
            return
        del data["characters"][name.lower()]
        save_data(channel, data)
        await interaction.response.send_message(embed=discord.Embed(title=f"🗑️ Character Deleted: {name.title()}", color=EMBED_COLORS["error"]))

    # --- LOCATION ---

    @app_commands.command(name="location", description="Look up a location's lore entry")
    @app_commands.describe(name="The location's name")
    async def location(self, interaction: discord.Interaction, name: str):
        data = load_data(interaction.channel.name)
        if not data:
            await interaction.response.send_message(embed=error_embed("No lore found", "This channel has no lore file yet.", "/addlocation"))
            return
        location = data.get("locations", {}).get(name.lower())
        if not location:
            close = [k for k in data.get("locations", {}) if name.lower() in k]
            suggestion = f"/location name:{close[0].title()}" if close else "/list type:locations"
            await interaction.response.send_message(embed=error_embed("Location not found", f"No location named **{name.title()}** exists here.", suggestion))
            return
        embed = discord.Embed(title=f"🗺️ {name.title()}", description=location["description"], color=EMBED_COLORS["location"])
        npcs = ", ".join(location.get("notable_npcs", []))
        embed.add_field(name="Notable NPCs", value=npcs or "None", inline=False)
        embed.set_footer(text=f"#{interaction.channel.name} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addlocation", description="Add a location to this channel's lore")
    @app_commands.describe(name="Location name", description="A short description", npcs="Comma-separated notable NPCs (optional)")
    async def add_location(self, interaction: discord.Interaction, name: str, description: str, npcs: str = ""):
        channel = interaction.channel.name
        data = load_data(channel) or {"characters": {}, "locations": {}, "factions": {}, "items": {}, "timeline": [], "custom_commands": {}}
        npc_list = [n.strip() for n in npcs.split(",")] if npcs else []
        data.setdefault("locations", {})[name.lower()] = {"description": description, "notable_npcs": npc_list}
        save_data(channel, data)
        embed = discord.Embed(title=f"✅ Location Added: {name.title()}", color=EMBED_COLORS["location"])
        embed.add_field(name="Description", value=description, inline=False)
        embed.add_field(name="Notable NPCs", value=npcs or "None", inline=False)
        embed.set_footer(text=f"#{channel} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deletelocation", description="Delete a location (Admin only)")
    @app_commands.describe(name="Location name")
    @is_admin()
    async def delete_location(self, interaction: discord.Interaction, name: str):
        channel = interaction.channel.name
        data = load_data(channel)
        if not data or name.lower() not in data.get("locations", {}):
            await interaction.response.send_message(embed=error_embed("Not found", f"No location named **{name.title()}** exists here."))
            return
        del data["locations"][name.lower()]
        save_data(channel, data)
        await interaction.response.send_message(embed=discord.Embed(title=f"🗑️ Location Deleted: {name.title()}", color=EMBED_COLORS["error"]))

    # --- FACTION ---

    @app_commands.command(name="faction", description="Look up a faction's lore entry")
    @app_commands.describe(name="The faction's name")
    async def faction(self, interaction: discord.Interaction, name: str):
        data = load_data(interaction.channel.name)
        if not data:
            await interaction.response.send_message(embed=error_embed("No lore found", "This channel has no lore file yet.", "/addfaction"))
            return
        faction = data.get("factions", {}).get(name.lower())
        if not faction:
            await interaction.response.send_message(embed=error_embed("Faction not found", f"No faction named **{name.title()}** exists here.", "/list type:factions"))
            return
        embed = discord.Embed(title=f"⚔️ {name.title()}", description=faction["description"], color=EMBED_COLORS["faction"])
        embed.add_field(name="Alignment", value=faction.get("alignment", "Unknown"), inline=True)
        embed.add_field(name="Members", value=faction.get("members", "Unknown"), inline=True)
        embed.set_footer(text=f"#{interaction.channel.name} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addfaction", description="Add a faction to this channel's lore")
    @app_commands.describe(name="Faction name", description="A short description", alignment="Their moral alignment", members="Comma-separated key members")
    async def add_faction(self, interaction: discord.Interaction, name: str, description: str, alignment: str = "Unknown", members: str = ""):
        channel = interaction.channel.name
        data = load_data(channel) or {"characters": {}, "locations": {}, "factions": {}, "items": {}, "timeline": [], "custom_commands": {}}
        data.setdefault("factions", {})[name.lower()] = {"description": description, "alignment": alignment, "members": members}
        save_data(channel, data)
        embed = discord.Embed(title=f"✅ Faction Added: {name.title()}", color=EMBED_COLORS["faction"])
        embed.add_field(name="Alignment", value=alignment, inline=True)
        embed.add_field(name="Members", value=members or "None", inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        embed.set_footer(text=f"#{channel} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deletefaction", description="Delete a faction (Admin only)")
    @app_commands.describe(name="Faction name")
    @is_admin()
    async def delete_faction(self, interaction: discord.Interaction, name: str):
        channel = interaction.channel.name
        data = load_data(channel)
        if not data or name.lower() not in data.get("factions", {}):
            await interaction.response.send_message(embed=error_embed("Not found", f"No faction named **{name.title()}** exists here."))
            return
        del data["factions"][name.lower()]
        save_data(channel, data)
        await interaction.response.send_message(embed=discord.Embed(title=f"🗑️ Faction Deleted: {name.title()}", color=EMBED_COLORS["error"]))

    # --- ITEM ---

    @app_commands.command(name="item", description="Look up an item's lore entry")
    @app_commands.describe(name="The item's name")
    async def item(self, interaction: discord.Interaction, name: str):
        data = load_data(interaction.channel.name)
        if not data:
            await interaction.response.send_message(embed=error_embed("No lore found", "This channel has no lore file yet.", "/additem"))
            return
        item = data.get("items", {}).get(name.lower())
        if not item:
            await interaction.response.send_message(embed=error_embed("Item not found", f"No item named **{name.title()}** exists here.", "/list type:items"))
            return
        embed = discord.Embed(title=f"🗡️ {name.title()}", description=item["description"], color=EMBED_COLORS["item"])
        embed.add_field(name="Type", value=item.get("type", "Unknown"), inline=True)
        embed.add_field(name="Owner", value=item.get("owner", "Unknown"), inline=True)
        embed.set_footer(text=f"#{interaction.channel.name} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="additem", description="Add an item to this channel's lore")
    @app_commands.describe(name="Item name", description="A short description", type="Item type (weapon, artifact, etc.)", owner="Current owner (optional)")
    async def add_item(self, interaction: discord.Interaction, name: str, description: str, type: str = "Unknown", owner: str = "Unknown"):
        channel = interaction.channel.name
        data = load_data(channel) or {"characters": {}, "locations": {}, "factions": {}, "items": {}, "timeline": [], "custom_commands": {}}
        data.setdefault("items", {})[name.lower()] = {"description": description, "type": type, "owner": owner}
        save_data(channel, data)
        embed = discord.Embed(title=f"✅ Item Added: {name.title()}", color=EMBED_COLORS["item"])
        embed.add_field(name="Type", value=type, inline=True)
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        embed.set_footer(text=f"#{channel} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deleteitem", description="Delete an item (Admin only)")
    @app_commands.describe(name="Item name")
    @is_admin()
    async def delete_item(self, interaction: discord.Interaction, name: str):
        channel = interaction.channel.name
        data = load_data(channel)
        if not data or name.lower() not in data.get("items", {}):
            await interaction.response.send_message(embed=error_embed("Not found", f"No item named **{name.title()}** exists here."))
            return
        del data["items"][name.lower()]
        save_data(channel, data)
        await interaction.response.send_message(embed=discord.Embed(title=f"🗑️ Item Deleted: {name.title()}", color=EMBED_COLORS["error"]))

    # --- TIMELINE ---

    @app_commands.command(name="timeline", description="View this channel's timeline of events")
    async def timeline(self, interaction: discord.Interaction):
        data = load_data(interaction.channel.name)
        if not data or not data.get("timeline"):
            await interaction.response.send_message(embed=error_embed("No timeline yet", "No events have been added.", "/addevent"))
            return
        events = sorted(data["timeline"], key=lambda e: e.get("date", ""))
        lines = "\n".join([f"**{e['date']}** — {e['title']}: {e['description']}" for e in events])
        embed = discord.Embed(title=f"📅 Timeline — #{interaction.channel.name}", description=lines, color=EMBED_COLORS["timeline"])
        embed.set_footer(text="The Archivist • Your Lore Keeper")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addevent", description="Add an event to this channel's timeline")
    @app_commands.describe(date="When it happened (e.g. 'Year 402')", title="Short event title", description="What happened")
    async def add_event(self, interaction: discord.Interaction, date: str, title: str, description: str):
        channel = interaction.channel.name
        data = load_data(channel) or {"characters": {}, "locations": {}, "factions": {}, "items": {}, "timeline": [], "custom_commands": {}}
        data.setdefault("timeline", []).append({"date": date, "title": title, "description": description})
        save_data(channel, data)
        embed = discord.Embed(title=f"✅ Event Added: {title}", color=EMBED_COLORS["timeline"])
        embed.add_field(name="Date", value=date, inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        embed.set_footer(text=f"#{channel} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deleteevent", description="Delete a timeline event by title (Admin only)")
    @app_commands.describe(title="The event title to delete")
    @is_admin()
    async def delete_event(self, interaction: discord.Interaction, title: str):
        channel = interaction.channel.name
        data = load_data(channel)
        if not data:
            await interaction.response.send_message(embed=error_embed("Not found", "No lore data in this channel."))
            return
        original = data.get("timeline", [])
        data["timeline"] = [e for e in original if e["title"].lower() != title.lower()]
        if len(data["timeline"]) == len(original):
            await interaction.response.send_message(embed=error_embed("Not found", f"No event titled **{title}** exists."))
            return
        save_data(channel, data)
        await interaction.response.send_message(embed=discord.Embed(title=f"🗑️ Event Deleted: {title}", color=EMBED_COLORS["error"]))

    # --- EDIT ---

    @app_commands.command(name="edit", description="Edit a field on an existing lore entry")
    @app_commands.describe(type="Entry type", name="Entry name", field="Field to edit", value="New value")
    @app_commands.choices(type=[
        app_commands.Choice(name="Character", value="characters"),
        app_commands.Choice(name="Location", value="locations"),
        app_commands.Choice(name="Faction", value="factions"),
        app_commands.Choice(name="Item", value="items"),
    ])
    async def edit(self, interaction: discord.Interaction, type: str, name: str, field: str, value: str):
        channel = interaction.channel.name
        data = load_data(channel)
        if not data or name.lower() not in data.get(type, {}):
            await interaction.response.send_message(embed=error_embed("Not found", f"No {type[:-1]} named **{name.title()}** exists here."))
            return
        if field not in data[type][name.lower()]:
            await interaction.response.send_message(embed=error_embed("Invalid field", f"`{field}` is not a valid field for this entry type."))
            return
        data[type][name.lower()][field] = value
        save_data(channel, data)
        embed = discord.Embed(title=f"✏️ Updated: {name.title()}", color=EMBED_COLORS["success"])
        embed.add_field(name=field.title(), value=value, inline=False)
        embed.set_footer(text=f"#{channel} • The Archivist")
        await interaction.response.send_message(embed=embed)

    # --- SEARCH ---

    @app_commands.command(name="search", description="Search across all lore in this channel")
    @app_commands.describe(term="Keyword to search for")
    async def search(self, interaction: discord.Interaction, term: str):
        data = load_data(interaction.channel.name)
        if not data:
            await interaction.response.send_message(embed=error_embed("No lore found", "This channel has no lore file yet."))
            return
        results = []
        for cat in ["characters", "locations", "factions", "items"]:
            for key, val in data.get(cat, {}).items():
                if term.lower() in json.dumps(val).lower() or term.lower() in key:
                    results.append(f"**{cat[:-1].title()}** — {key.title()}")
        for event in data.get("timeline", []):
            if term.lower() in json.dumps(event).lower():
                results.append(f"**Event** — {event['title']}")
        if not results:
            await interaction.response.send_message(embed=error_embed("No results", f"Nothing matched `{term}` in this channel's lore."))
            return
        embed = discord.Embed(title=f"🔍 Search: '{term}'", description="\n".join(results), color=EMBED_COLORS["help"])
        embed.set_footer(text=f"#{interaction.channel.name} • The Archivist")
        await interaction.response.send_message(embed=embed)

    # --- LIST ---

    @app_commands.command(name="list", description="List all entries of a given type in this channel")
    @app_commands.describe(type="What to list")
    @app_commands.choices(type=[
        app_commands.Choice(name="Characters", value="characters"),
        app_commands.Choice(name="Locations", value="locations"),
        app_commands.Choice(name="Factions", value="factions"),
        app_commands.Choice(name="Items", value="items"),
        app_commands.Choice(name="Custom Commands", value="custom_commands"),
    ])
    async def list_entries(self, interaction: discord.Interaction, type: str):
        data = load_data(interaction.channel.name)
        if not data or not data.get(type):
            await interaction.response.send_message(embed=error_embed("Nothing here yet", f"No {type} found in this channel."))
            return
        lines = "\n".join([f"• **{k.title()}**" for k in data[type].keys()])
        embed = discord.Embed(title=f"📋 {type.replace('_', ' ').title()} in #{interaction.channel.name}", description=lines, color=EMBED_COLORS["help"])
        embed.set_footer(text="The Archivist • Your Lore Keeper")
        await interaction.response.send_message(embed=embed)

    # --- CUSTOM COMMANDS ---

    @app_commands.command(name="addcommand", description="Create a custom lore command for this channel")
    @app_commands.describe(name="Command name", response="What the bot should respond with")
    async def add_command(self, interaction: discord.Interaction, name: str, response: str):
        channel = interaction.channel.name
        data = load_data(channel) or {"characters": {}, "locations": {}, "factions": {}, "items": {}, "timeline": [], "custom_commands": {}}
        data.setdefault("custom_commands", {})[name.lower()] = response
        save_data(channel, data)
        embed = discord.Embed(title=f"✅ Custom Command Added: {name.lower()}", description=f"Use `/cmd name:{name.lower()}` to run it.", color=EMBED_COLORS["custom"])
        embed.set_footer(text=f"#{channel} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cmd", description="Run a custom lore command for this channel")
    @app_commands.describe(name="The custom command name")
    async def run_command(self, interaction: discord.Interaction, name: str):
        data = load_data(interaction.channel.name)
        if not data:
            await interaction.response.send_message(embed=error_embed("No lore found", "This channel has no data yet."))
            return
        response = data.get("custom_commands", {}).get(name.lower())
        if not response:
            await interaction.response.send_message(embed=error_embed("Command not found", f"No custom command named `{name}` in this channel.", "/list type:Custom Commands"))
            return
        embed = discord.Embed(title=f"📜 {name.title()}", description=response, color=EMBED_COLORS["custom"])
        embed.set_footer(text=f"#{interaction.channel.name} • The Archivist")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deletecommand", description="Delete a custom command (Admin only)")
    @app_commands.describe(name="Command name")
    @is_admin()
    async def delete_command(self, interaction: discord.Interaction, name: str):
        channel = interaction.channel.name
        data = load_data(channel)
        if not data or name.lower() not in data.get("custom_commands", {}):
            await interaction.response.send_message(embed=error_embed("Not found", f"No custom command named `{name}` exists here."))
            return
        del data["custom_commands"][name.lower()]
        save_data(channel, data)
        await interaction.response.send_message(embed=discord.Embed(title=f"🗑️ Command Deleted: {name.lower()}", color=EMBED_COLORS["error"]))

    # --- EXPORT ---

    @app_commands.command(name="export", description="Export this channel's full lore as a text file")
    async def export(self, interaction: discord.Interaction):
        data = load_data(interaction.channel.name)
        if not data:
            await interaction.response.send_message(embed=error_embed("No lore found", "This channel has no lore file yet."))
            return
        lines = [f"# Lore Export — #{interaction.channel.name}\n"]
        for cat in ["characters", "locations", "factions", "items"]:
            entries = data.get(cat, {})
            if entries:
                lines.append(f"\n## {cat.title()}")
                for name, val in entries.items():
                    lines.append(f"\n### {name.title()}")
                    for k, v in val.items():
                        lines.append(f"**{k.title()}:** {v}")
        if data.get("timeline"):
            lines.append("\n## Timeline")
            for e in sorted(data["timeline"], key=lambda x: x.get("date", "")):
                lines.append(f"\n**{e['date']}** — {e['title']}: {e['description']}")
        content = "\n".join(lines)
        file = discord.File(
            fp=__import__("io").BytesIO(content.encode()),
            filename=f"{interaction.channel.name}-lore.md"
        )
        await interaction.response.send_message(file=file)


async def setup(bot):
    await bot.add_cog(LoreCommands(bot))