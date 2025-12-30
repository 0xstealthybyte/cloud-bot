import discord
from discord.ext import commands
import json
import os
intents = discord.Intents.default()
intents.guild_messages = True
bot = commands.Bot(command_prefix="$", intents=intents)
STORAGE_CHANNEL_ID = "channel-id-here"
BACKUP_FILE = "file_data_backup.json"
if os.path.exists(BACKUP_FILE):
    with open(BACKUP_FILE, "r") as f:
        stored_data = json.load(f)
else:
    stored_data = {}
def save_backup():
    with open(BACKUP_FILE, "w") as f:
        json.dump(stored_data, f, indent=4)
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"Message from {message.author}: {message.content}")
    await bot.process_commands(message)
@bot.command()
async def save(ctx, tag: str, *, description: str = ""):

    if not ctx.message.attachments:
        await ctx.send("Please attach a file to save!")
        return
    file = ctx.message.attachments[0]
    channel = bot.get_channel(STORAGE_CHANNEL_ID)
    message = await channel.send(f"**Tag:** {tag}\n**Description:** {description}", file=await file.to_file())
    stored_data[tag] = {
        "description": description,
        "discord_message_id": message.id,
        "filename": file.filename,
    }
    save_backup()
    await ctx.send(f"file saved with tag `{tag}`!")
@bot.command()
async def retrieve(ctx, tag: str):
    if tag not in stored_data:
        await ctx.send(f"No file found with tagg `{tag}`.")
        return
    data = stored_data[tag]
    channel = bot.get_channel(STORAGE_CHANNEL_ID)
    message = await channel.fetch_message(data["discord_message_id"])
    await ctx.send(f"**Description:** {data['description']}")
    if message.attachments:
        await ctx.send(message.attachments[0].url)
@bot.command()
async def list_files(ctx):
    if not stored_data:
        await ctx.send("No files stored yet.")
        return
    file_list = "\n".join([f"**{tag}**: {data['description']}" for tag, data in stored_data.items()])
    await ctx.send(f"**Stored Files:**\n{file_list}")
@bot.command()
async def delete(ctx, tag: str):
    if tag not in stored_data:
        await ctx.send(f"No file found with tag `{tag}`.")
        return
    stored_data.pop(tag)
    save_backup()
    await ctx.send(f"File with tag `{tag}` has been deleted.")
@bot.command()
async def backup(ctx):
    save_backup()
    await ctx.send("Data has been backed up to the local file.")
@bot.command()
async def restore(ctx):
    global stored_data
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r") as f:
            stored_data = json.load(f)
        await ctx.send("Data has been restored from the backup.")
    else:
        await ctx.send("No backup file found.")
import os
@bot.command()
async def save_large(ctx, tag: str, *, description: str = ""):
    if not ctx.message.attachments:
        await ctx.send("Please attach a file to save!")
        return
    file = ctx.message.attachments[0]
    file_data = await file.read()
    chunk_size = 8 * 1024 * 1024  
    chunks = [file_data[i:i + chunk_size] for i in range(0, len(file_data), chunk_size)]
    stored_data[tag] = {"description": description, "chunks": [], "filename": file.filename}
    for i, chunk in enumerate(chunks):
        chunk_message = await ctx.send(
            f"**Tag:** {tag} (Chunk {i + 1}/{len(chunks)})", 
            file=discord.File(fp=chunk, filename=f"{file.filename}.part{i + 1}")
        )
        stored_data[tag]["chunks"].append(chunk_message.id)
    save_backup()
    await ctx.send(f"File saved with tag `{tag}`!")

@bot.command()
async def helpme(ctx):
    commands = [
        "!save <tag> <description>: Save a file with a tag and optional description.",
        "!retrieve <tag>: Retrieve a file by its tag.",
        "!list_files: List all saved files with their tags and descriptions.",
        "!delete <tag>: Delete a saved file by its tag.",
        "!backup: Back up all stored data to a local JSON file.",
        "!restore: Restore data from the local backup file.",
    ]
    help_text = "**Command Usage Guide:**\n" + "\n".join(commands)
    await ctx.send(help_text)

bot.run('Bot token here')
