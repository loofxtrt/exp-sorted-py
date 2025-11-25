from pathlib import Path

import click

from .tui import tui
from .services import youtube
from .managers import cache, settings

@click.command(help='Inicia a TUI para visualizar e editar uma playlist')
def tui_pl():
    tui.main(
        master_directory=Path('/mnt/seagate/authoral-software/sorted'),
        playlist_file=Path('./testei/chinelo.json'),
        video_cache_file=_video_cache_file,
        ytdl=_ytdl
    )

@click.group()
def cli():
    pass

# variáveis pra não precisar requisitando as informações em cada comando
_ytdl = None
_video_cache_file = None

# adição dos comandos ao app
cli.add_command(tui_pl)

if __name__ == '__main__':
    ytdl_options = settings.get('ytdl-options')
    _video_cache_file = settings.get_cache_file('youtube', 'videos')
    _ytdl = youtube.instance_ytdl(ytdl_options)

    cli()