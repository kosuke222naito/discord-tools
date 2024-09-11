import discord
import os
import random
import asyncio
from dotenv import load_dotenv

load_dotenv()

ALLOWED_EXTENSIONS = {".png", ".jpeg", ".jpg", ".gif"}

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID_STR = os.getenv("GUILD_ID")
EMOJI_DIRECTORY = os.getenv("EMOJI_DIRECTORY")

# 環境変数のバリデーション
if not DISCORD_TOKEN:
    raise ValueError("Discord token not found. Please set DISCORD_TOKEN in your .env.")

if not GUILD_ID_STR:
    raise ValueError("Guild ID not found. Please set GUILD_ID in your .env.")

try:
    GUILD_ID = int(GUILD_ID_STR)
except ValueError:
    raise ValueError("Invalid Guild ID. GUILD_ID must be an int.")

if not EMOJI_DIRECTORY:
    raise ValueError(
        "Emoji directory not found. Please set EMOJI_DIRECTORY in your .env."
    )

client = discord.Client(intents=discord.Intents.default())


async def register_emoji(guild, filename):
    file_path = os.path.join(EMOJI_DIRECTORY, filename)
    emoji_name = os.path.splitext(filename)[0]

    with open(file_path, "rb") as image:
        image_data = image.read()
        try:
            new_emoji = await guild.create_custom_emoji(
                name=emoji_name, image=image_data
            )
            print(f"Created emoji: {new_emoji.name}")
        except discord.HTTPException as e:
            print(f"Failed to create emoji {emoji_name}: {e}")


def get_emoji_filename_list(emoji_directory) -> list[str]:
    """
    登録できるファイル形式の画像のファイル名のみのリストを取得
    """
    return [
        filename
        for filename in os.listdir(emoji_directory)
        if os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS
    ]


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    guild = client.get_guild(GUILD_ID)

    if not guild:
        print(
            f"Guild with ID {GUILD_ID} not found! Make sure the bot is a member of the guild."
        )
        await client.close()
        return

    filename_list = get_emoji_filename_list(EMOJI_DIRECTORY)

    for filename in filename_list:
        await register_emoji(guild, filename)

        # API レート制限回避のためにランダムな秒数待機
        delay = random.uniform(1, 2)
        await asyncio.sleep(delay)

    await client.close()


client.run(DISCORD_TOKEN)
