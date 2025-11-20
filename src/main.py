from pathlib import Path
from managers.playlists import playlist_manager
from modules import importation
from managers import cache
from managers import settings
from tui import tui
from services import youtube
import click

@click.command(help='Cria uma playlist nova')
@click.argument('title')
@click.argument('output-dir')
@click.option('--description', '-d', help='Incluir uma descrição na playlist')
@click.option('--assume-default', '-y', is_flag=True, help='Assumir que se uma playlist no mesmo caminho já existir, ela deve ser sobreescrita')
def create(title, output_dir, description, assume_default):
    playlist_manager.create_playlist(
        playlist_title=title,
        playlist_description=description,
        output_dir=output_dir,
        assume_default=assume_default
    )

@click.command(help='Deleta uma playlist inteira')
@click.argument('playlist')
@click.option('--assume-default', '-y', is_flag=True, help='Assumir que a playlist deve ser deletada sem confirmação')
@click.option('--deep-validation', '-dv', is_flag=True, help='Se presente, vai exigir que uma playlist seja 100% válida pra ser deletada com esse comando')
def delete(playlist, assume_default, deep_validation):
    playlist_manager.delete_playlist(
        playlist_file=Path(playlist),
        assume_default=assume_default,
        superficial_validation=deep_validation
    )

@click.command(help='Adiciona vídeos à uma playlist')
@click.argument('playlist')
@click.argument('urls', nargs=-1)
@click.option('--assume-default', '-y', is_flag=True, help='Assumir que a playlist deve ser criada se ela não existir ainda')
def insert(playlist, urls, assume_default):
    for u in urls:
        video_id = youtube.extract_youtube_video_id(url=u, ytdl_options=settings.ytdl_options)

        playlist_manager.insert_video(
            video_id=video_id,
            playlist_file=Path(playlist),
            assume_default=assume_default
        )

@click.command(help='Remove vídeos de uma playlist')
@click.argument('playlist')
@click.argument('urls', nargs=-1)
def remove(playlist, urls):
    for u in urls:
        video_id = youtube.extract_youtube_video_id(url=u, ytdl_options=settings.ytdl_options)

        playlist_manager.remove_video(
            video_id=video_id,
            playlist_file=Path(playlist)
        )

@click.command(name='import', help='Importa uma playlist do YouTube e a converte para uma playlist local')
@click.argument('url', type=str)
@click.argument('output-dir')
@click.option('--new-title', '-nt', help='Novo título a ser atribuído a playlist. Se não for passado, ela herda o título do YouTube')
def import_pl(url, output_dir, new_title):
    importation.import_playlist(
        new_title=new_title,
        output_dir=Path(output_dir),
        yt_playlist_url=url,
        ytdl_options=_ytdl_options
    )

@click.command(help='Move um vídeo de uma playlist para a outra')
@click.argument('origin-playlist')
@click.argument('destination-playlist')
@click.argument('url')
@click.option('--ensure-destination', '-e', is_flag=True, help='Assumir que se a playlist de destino não existir, ela deve ser criada')
def move(origin_playlist, destination_playlist, url, ensure_destination):
    playlist_manager.move_video(
        origin_playlist=Path(origin_playlist),
        destination_playlist=Path(destination_playlist),
        video_id=youtube.extract_youtube_video_id(url=url, ytdl_options=settings.get('ytdl_options')),
        ensure_destination=ensure_destination
    )

@click.command(help='Atualiza o cache de vídeos do software, removendo os vídeos órfãos e incluindo os novos')
@click.argument('playlists-directory')
@click.option('--include-all', '-ia', is_flag=True, help='Não ignora os vídeos que já estavam presentes no cache, os atualizando')
def update_cache(playlists_directory, include_all):
    cache.update_full_cache(
        playlists_directory=Path(playlists_directory),
        skip_already_cached=not include_all,
        cache_file=_cache_youtube_videos,
        ytdl_options=_ytdl_options
    )

@click.command(help='Reseta todas as configurações do usuário de volta para as configurações padrão')
def reset_settings():
    settings.reset_or_set()

@click.command(help='Inicia a TUI para visualizar e editar uma playlist')
@click.argument('playlist')
def tui_pl(playlist):
    tui.main(
        master_directory=Path('/mnt/seagate/authoral-software/sorted'),
        playlist_file=Path(playlist),
        video_cache_file=_cache_youtube_videos,
        ytdl_options=_ytdl_options
    )

@click.group()
def cli():
    pass

# variáveis pra não precisar requisitando as informações em cada comando
_cache_youtube_videos = None
_ytdl_options = None

# adição dos comandos ao app
cli.add_command(import_pl)
cli.add_command(create)
cli.add_command(insert)
cli.add_command(remove)
cli.add_command(delete)
cli.add_command(move)
cli.add_command(update_cache)
cli.add_command(reset_settings)
cli.add_command(tui_pl)

if __name__ == '__main__':
    settings._load()

    _cache_youtube_videos = settings.get_cache_file('youtube', 'videos')
    _ytdl_options = settings.get('ytdl_options')

    cli()