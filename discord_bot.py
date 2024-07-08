import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from slash_commands import MCGame


load_dotenv()

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# For release
tree.add_command(
    MCGame(),
    guilds=[
        discord.Object(id=os.getenv("UKCES_GUILD_ID")),
        discord.Object(id=os.getenv("TEST_GUILD_ID")),
    ],
)
# For testing
# tree.add_command(MCGame(), guilds=[discord.Object(id=os.getenv("TEST_GUILD_ID"))])


@client.event
async def on_ready():
    # For release
    await tree.sync(guild=discord.Object(id=os.getenv("UKCES_GUILD_ID")))
    # For testing and release
    await tree.sync(guild=discord.Object(id=os.getenv("TEST_GUILD_ID")))
    print(f"We have logged in as {client.user}")


@tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingAnyRole):
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )
    else:
        if interaction.response.is_done():
            await interaction.channel.send(f"An error occurred: {error}")
        else:
            await interaction.response.send_message(f"An error occurred: {error}")


client.run(os.getenv("BOT_TOKEN"))
