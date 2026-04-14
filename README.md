# The Archivist 

A modular, multi-universe Discord bot designed for writers, game developers, and tabletop players to manage their world-building directly within Discord. 

Instead of digging through scattered notes, The Archivist allows you to organize your lore by server channel or category. You can query character bios, magic systems, and pantheons without breaking your creative flow.

## Key Features
* **Multi-Universe Support:** Reads from different JSON data sources depending on the Discord channel. Keep your ARPG game lore separated from your dark fantasy novel drafts.
* **Instant Lore Retrieval:** Use simple commands to pull up beautifully formatted embed cards for characters, locations, and factions.
* **Dynamic Prompt Generation:** Generates random writing or design prompts tailored to the specific universe of the current channel.
* **Scalable Data Structure:** Easily expandable dictionary format, ready to be scaled into a full SQLite or PostgreSQL database.

## Usage Examples

The bot adapts its responses based on the channel context. 

**In `#project-verglas` (Game Dev Channel):**
> **User:** `!god Aurelius`
> **The Archivist:** *Retrieves the alignment, domains, and history of the Living God Aurelius.*
>
> **User:** `!magic loom of ages`
> **The Archivist:** *Details the foundational magical fabric of Verglas, explaining how it weaves reality without mechanical corruption.*

**In `#book-drafting` (Novel Channel):**
> **User:** `!bio Rieka`
> **The Archivist:** *Pulls up Rieka's profile: "Title: Wolfblood. A human raised by orcs, navigating the complex dynamics of his upbringing. Son of Solveig Debán."*
> 
> **User:** `!location Leofricburh`
> **The Archivist:** *Displays the history of the village, notable NPCs like Blaine the Blacksmith, and current regional conflicts.*

## Tech Stack
* **Language:** Python 3.8+
* **Library:** `discord.py`
* **Data Storage:** Local JSON (Current) -> SQLite (Planned)

## ⚙️ Installation & Setup
1. Clone the repository: 
   `git clone https://github.com/YourUsername/The-Archivist-DiscordBot.git`
2. Install the required dependencies:
   `pip install -r requirements.txt`
3. Create a `.env` file in the root directory and add your Discord Bot Token:
   `DISCORD_TOKEN=your_token_here`
4. Run the bot:
   `python bot.py`

## Roadmap
- [ ] Transition from in-memory dictionaries to dynamic JSON file handling.
- [ ] Add `!add-lore` command to update the database directly from Discord.
- [ ] Build an interactive relationship mapping command (e.g., showing faction alliances).
- [ ] Implement user permissions (restricting edit commands to admins/writers).

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
