import click
import manager
import visualizer
import helpers
import cache
import importation
import settings as stg
from pathlib import Path

settings = stg.Settings()

@click.command(help='Cria uma playlist nova')
@click.argument('title')
@click.argument('output-dir')
@click.option('--description', '-d')
@click.option('--assume-default', '-y', is_flag=True)
def create(title, output_dir, description, assume_default):
    manager.create_playlist(
        playlist_title=title,
        playlist_description=description,
        output_dir=output_dir,
        assume_default=assume_default
    )

@click.command(help='Deleta uma playlist inteira')
@click.argument('playlist')
@click.option('--assume-default', '-y', is_flag=True)
@click.option('--deep-validation', '-dv', is_flag=True)
def delete(playlist, assume_default, deep_validation):
    manager.delete_playlist(
        playlist_file=Path(playlist),
        assume_default=assume_default,
        superficial_validation=deep_validation
    )

@click.command(help='Adiciona vídeos à uma playlist')
@click.argument('playlist')
@click.argument('urls', nargs=-1)
@click.option('--assume-default', '-y', is_flag=True)
def insert(playlist, urls, assume_default):
    for u in urls:
        video_id = helpers.extract_youtube_video_id(url=u, ytdl_options=settings.ytdl_options)

        manager.insert_video(
            video_id=video_id,
            playlist_file=Path(playlist),
            assume_default=assume_default
        )

@click.command(help='Remove vídeos de uma playlist')
@click.argument('playlist')
@click.argument('urls', nargs=-1)
def remove(playlist, urls):
    for u in urls:
        video_id = helpers.extract_youtube_video_id(url=u, ytdl_options=settings.ytdl_options)

        manager.remove_video(
            video_id=video_id,
            playlist_file=Path(playlist)
        )

@click.command(name='import', help='Importa uma playlist do YouTube e a converte para uma playlist local')
@click.argument('url', type=str)
@click.argument('output-dir')
@click.option('--new-title', '-nt')
def import_pl(url, output_dir, new_title):
    importation.import_playlist(
        new_title=new_title,
        output_dir=Path(output_dir),
        yt_playlist_url=url,
        ytdl_options=settings.ytdl_options
    )

@click.command(help='Visualiza um diretório e lista todas as playlists válidas que ele contém')
@click.argument('directory')
def view_dir(directory):
    visualizer.view_directory(
        directory=Path(directory)
    )

@click.command(help='Visualiza uma playlist individual, incluindo todos os vídeos que ela contém')
@click.argument('playlist')
@click.option('--show-desc', '-sd', is_flag=True)
def view_pl(playlist, show_desc):
    visualizer.view_playlist(
        playlist_file=Path(playlist),
        show_description=show_desc
    )

@click.command(help='Move um vídeo de uma playlist para a outra')
@click.argument('origin-playlist')
@click.argument('destination-playlist')
@click.argument('url')
def move(origin_playlist, destination_playlist, url):
    manager.move_video(
        origin_playlist=Path(origin_playlist),
        destination_playlist=Path(destination_playlist),
        video_id=helpers.extract_youtube_video_id(url=url, ytdl_options=settings.ytdl_options)
    )

@click.command(help='Atualiza o cache de vídeos do software, removendo os vídeos órfãos e incluindo os novos')
@click.argument('playlists-directory')
@click.option('--include-all', '-ia', is_flag=True)
def update_cache(playlists_directory, include_all):
    cache.update_full_cache(
        playlists_directory=Path(playlists_directory),
        skip_already_cached=not include_all,
        cache_file=settings.video_cache_file,
        ytdl_options=settings.ytdl_options
    )

@click.command(help='Reseta todas as configurações do usuário de volta para as configurações padrão')
def reset_settings():
    settings.reset_or_set()

@click.group()
def cli():
    pass

cli.add_command(import_pl)
cli.add_command(create)
cli.add_command(insert)
cli.add_command(remove)
cli.add_command(delete)
cli.add_command(view_dir)
cli.add_command(view_pl)
cli.add_command(move)
cli.add_command(update_cache)
cli.add_command(reset_settings)

if __name__ == '__main__':
    settings.load()
    cli()