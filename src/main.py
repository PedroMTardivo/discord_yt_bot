import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random
import os
from dotenv import load_dotenv
from discord.ui import View, button, Button

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")


intents = discord.Intents.default()
intents.message_content = True  # Necessário para comandos funcionarem
bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
now_playing_message = None
queue_message = None

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
    global now_playing_message, queue_message

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'outtmpl': 'temp_song.%(ext)s',
    }
    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Música')
            filename = ydl.prepare_filename(info)
            if not filename.endswith('.webm') and not filename.endswith('.m4a') and not filename.endswith('.opus') and not filename.endswith('.mp3'):
                filename += '.webm'
    except Exception as e:
        await play_next(ctx)
        return

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
    embed_now = discord.Embed(
        title="Tocando agora",
        description=title,
        color=discord.Color.green()
    )
    view = PlayerControls(ctx)
    # Atualiza ou envia a mensagem de "Tocando agora"
    if now_playing_message and now_playing_message.channel == ctx.channel:
        try:
            await now_playing_message.edit(embed=embed_now, view=view)
        except Exception:
            now_playing_message = await ctx.send(embed=embed_now, view=view)
    else:
        now_playing_message = await ctx.send(embed=embed_now, view=view)

    # Monta embed da fila
    if queue:
        fila = queue[:5]
        embed_queue = discord.Embed(
            title="Próximas músicas na fila",
            color=discord.Color.blue()
        )
        for i, item in enumerate(fila, 1):
            embed_queue.add_field(name=f"{i}.", value=item['title'], inline=False)
        if len(queue) > 5:
            embed_queue.set_footer(text=f"...e mais {len(queue) - 5} músicas na fila.")
    else:
        embed_queue = discord.Embed(
            description="Nenhuma música na fila além da que está tocando.",
            color=discord.Color.orange()
        )

    # Atualiza ou envia a mensagem da fila
    if queue_message and queue_message.channel == ctx.channel:
        try:
            await queue_message.edit(embed=embed_queue)
        except Exception:
            queue_message = await ctx.send(embed=embed_queue)
    else:
        queue_message = await ctx.send(embed=embed_queue)

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
    global queue_message
    if queue:
        fila = queue[:5]
        embed = discord.Embed(
            title="Próximas músicas na fila",
            color=discord.Color.blue()
        )
        for i, item in enumerate(fila, 1):
            embed.add_field(name=f"{i}.", value=item['title'], inline=False)
        if len(queue) > 5:
            embed.set_footer(text=f"...e mais {len(queue) - 5} músicas na fila.")
    else:
        embed = discord.Embed(
            description="Fila vazia.",
            color=discord.Color.red()
        )

    # Edita ou envia a mensagem da fila
    if queue_message and queue_message.channel == ctx.channel:
        try:
            await queue_message.edit(embed=embed)
        except Exception:
            queue_message = await ctx.send(embed=embed)
    else:
        queue_message = await ctx.send(embed=embed)

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Música pulada!")

@bot.command()
async def clear(ctx):
    queue.clear()
    await ctx.send("Fila de músicas limpa!")

async def update_queue_embed(ctx):
    global queue_message
    if queue:
        fila = queue[:5]
        embed = discord.Embed(
            title="Próximas músicas na fila",
            color=discord.Color.blue()
        )
        for i, item in enumerate(fila, 1):
            embed.add_field(name=f"{i}.", value=item['title'], inline=False)
        if len(queue) > 5:
            embed.set_footer(text=f"...e mais {len(queue) - 5} músicas na fila.")
    else:
        embed = discord.Embed(
            description="Fila vazia.",
            color=discord.Color.red()
        )

    if queue_message and queue_message.channel == ctx.channel:
        try:
            await queue_message.edit(embed=embed)
        except Exception:
            queue_message = await ctx.send(embed=embed)
    else:
        queue_message = await ctx.send(embed=embed)

@bot.command()
async def shuffle(ctx):
    if queue:
        random.shuffle(queue)
        await ctx.send("Fila embaralhada!")
        await update_queue_embed(ctx)  # Atualiza o embed da fila
    else:
        await ctx.send("Fila vazia, nada para embaralhar.")

class PlayerControls(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @button(label="⏭️ Pular", style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.voice and interaction.user.voice.channel == self.ctx.voice_client.channel:
            self.ctx.voice_client.stop()
            await interaction.response.defer(ephemeral=True)  # Não mostra mensagem
        else:
            await interaction.response.send_message("Você precisa estar no mesmo canal de voz!", ephemeral=True)

    @button(label="⏸️ Pausar/Retomar", style=discord.ButtonStyle.secondary)
    async def pause_resume_button(self, interaction: discord.Interaction, button: Button):
        vc = self.ctx.voice_client
        if interaction.user.voice and interaction.user.voice.channel == vc.channel:
            if vc.is_playing():
                vc.pause()
                await interaction.response.defer(ephemeral=True)  # Não mostra mensagem
            elif vc.is_paused():
                vc.resume()
                await interaction.response.defer(ephemeral=True)  # Não mostra mensagem
            else:
                await interaction.response.send_message("Nada está tocando.", ephemeral=True)
        else:
            await interaction.response.send_message("Você precisa estar no mesmo canal de voz!", ephemeral=True)

    @button(label="🔀 Embaralhar", style=discord.ButtonStyle.success)
    async def shuffle_button(self, interaction: discord.Interaction, button: Button):
        if queue:
            random.shuffle(queue)
            await update_queue_embed(self.ctx)
            await interaction.response.defer(ephemeral=True)  # Não mostra mensagem
        else:
            await interaction.response.send_message("Fila vazia!", ephemeral=True)

# Substitua 'SEU_TOKEN_AQUI' pelo token do seu bot
bot.run(TOKEN)