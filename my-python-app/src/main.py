import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")


intents = discord.Intents.default()
intents.message_content = True  # Necessário para comandos funcionarem
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

async def play_next(ctx):
    if queue:
        item = queue.pop(0)
        await play_song(ctx, item['url'])
    else:
        await ctx.send("Fila de músicas vazia.")

async def play_song(ctx, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': 'temp_song.%(ext)s',
    }
    filename = None
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'Música')
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.webm') and not filename.endswith('.m4a') and not filename.endswith('.opus') and not filename.endswith('.mp3'):
            filename += '.webm'

    ffmpeg_options = {
        'options': '-vn'
    }
    source = discord.FFmpegPCMAudio(filename, **ffmpeg_options)
    ctx.voice_client.stop()
    ctx.voice_client.play(
        source,
        after=lambda e: (
            os.remove(filename) if os.path.exists(filename) else None,
            asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )
    )
    await ctx.send(f"Tocando: {title}")

    # Mostra as próximas 20 músicas da fila
    if queue:
        fila = queue[:20]
        mensagem = "\n".join(f"{i+1}. {item['title']}" for i, item in enumerate(fila))
        if len(queue) > 20:
            mensagem += f"\n...e mais {len(queue) - 20} músicas na fila."
        await ctx.send("Próximas músicas na fila:\n" + mensagem)
    else:
        await ctx.send("Nenhuma música na fila além da que está tocando.")

@bot.command()
async def play(ctx, url):
    if ctx.author.voice is None:
        await ctx.send("Você precisa estar em um canal de voz!")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)

    # Se for playlist, adiciona todas as músicas na fila
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:  # É uma playlist
            for entry in info['entries']:
                if entry and 'id' in entry:
                    queue.append({'title': entry.get('title', 'Sem título'), 'url': f"https://www.youtube.com/watch?v={entry['id']}"})
            await ctx.send(f"{len(info['entries'])} músicas adicionadas à fila!")
        else:
            queue.append({'title': info.get('title', 'Sem título'), 'url': url})
            await ctx.send("Música adicionada à fila!")

    # Se não estiver tocando nada, começa a tocar
    if not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Desconectado do canal de voz.")

@bot.command()
async def queue_(ctx):
    if queue:
        fila = queue[:20]  # Próximas 20 músicas (sem a atual)
        mensagem = "\n".join(f"{i+1}. {item['title']}" for i, item in enumerate(fila))
        if len(queue) > 20:
            mensagem += f"\n...e mais {len(queue) - 20} músicas na fila."
        await ctx.send("Próximas músicas na fila:\n" + mensagem)
    else:
        await ctx.send("Fila vazia.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Música pulada!")

@bot.command()
async def clear(ctx):
    queue.clear()
    await ctx.send("Fila de músicas limpa!")

@bot.command()
async def shuffle(ctx):
    if queue:
        random.shuffle(queue)
        await ctx.send("Fila embaralhada!")
    else:
        await ctx.send("Fila vazia, nada para embaralhar.")

# Substitua 'SEU_TOKEN_AQUI' pelo token do seu bot
bot.run(TOKEN)