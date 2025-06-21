# Discord Music Bot YouTube

Um bot de música para Discord feito em Python, que toca músicas do YouTube, suporta playlists, fila, comandos de pular, limpar e embaralhar músicas.

## Funcionalidades

- Toca músicas do YouTube em canais de voz
- Suporte a playlists do YouTube
- Fila de músicas (queue)
- Comando para pular música (!skip)
- Comando para limpar a fila (!clear)
- Comando para embaralhar a fila (!shuffle)
- Mostra as próximas 20 músicas da fila (!queue_)
- Baixa a música, toca e apaga o arquivo após tocar

## Requisitos

- Python 3.8+
- FFmpeg instalado (`sudo apt install ffmpeg`)
- Token de bot do Discord

## Instalação

1. Clone o repositório:
    ```bash
    git clone <url-do-repositorio>
    cd disc_bot_yt/my-python-app
    ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. No arquivo `src/main.py`, substitua `"SEU_TOKEN_AQUI"` pelo token do seu bot do Discord.

## Uso

Execute o bot:
```bash
python src/main.py
```

No Discord, use os comandos:

- `!play <url>` — Adiciona uma música ou playlist à fila
- `!queue_` — Mostra as próximas 20 músicas da fila
- `!skip` — Pula para a próxima música
- `!clear` — Limpa a fila de músicas
- `!shuffle` — Embaralha a ordem da fila
- `!stop` — Desconecta o bot do canal de voz

## Observações

- Ative o "Message Content Intent" no portal de desenvolvedores do Discord para o bot funcionar corretamente.
- O bot apaga automaticamente o arquivo de áudio após tocar.
- O comando `!play` aceita links de vídeos e playlists do YouTube.

---

Feito com ❤️ usando [discord.py](https://github.com/Rapptz/discord.py) e [yt-dlp](https://github.com/yt-dlp/yt-dlp).