import click
import manager
import visualizer
import helpers
import cache
import settings as stg
from pathlib import Path

#testing_folder = Path('./tests')
settings = stg.Settings()

@click.command()
@click.argument('title')
@click.option('--description', '-d')
@click.option('--assume-default', '-y', is_flag=True)
def create(title, description, assume_default):
    manager.create_playlist(
        playlist_title=title,
        playlist_description=description,
        output_dir=testing_folder,
        assume_default=assume_default
    )

@click.command()
@click.argument('playlist')
@click.option('--deep-validation', '-dv', is_flag=True)
def delete(playlist, deep_validation):
    manager.delete_playlist(
        playlist_file=Path(playlist),
        superficial_validation=deep_validation
    )

@click.command()
@click.argument('playlist')
@click.argument('urls', nargs=-1)
def insert(urls, playlist):
    for u in urls:
        video_id = helpers.extract_youtube_video_id(u)

        manager.insert_video(
            video_id=video_id,
            playlist_file=Path(playlist)
        )

@click.command()
@click.argument('playlist')
@click.argument('urls', nargs=-1)
def remove(urls, playlist):
    for u in urls:
        video_id = helpers.extract_youtube_video_id(u)

        manager.remove_video(
            video_id=video_id,
            playlist_file=Path(playlist)
        )

@click.command(name='import')
@click.argument('url')
@click.option('--new-title', '-nt')
def import_pl(url, new_title):
    manager.import_playlist(
        new_title=new_title,
        output_dir=testing_folder,
        yt_playlist_url=url,
        ytdl_options=settings.ytdl_options
    )

@click.command()
@click.argument('directory')
def view_dir(directory):
    visualizer.view_directory(
        directory=Path(directory)
    )

@click.command()
@click.argument('playlist')
@click.option('--show-desc', '-sd', is_flag=True)
def view_pl(playlist, show_desc):
    visualizer.view_playlist(
        playlist_file=Path(playlist),
        show_description=show_desc
    )

@click.command()
@click.argument('origin-playlist')
@click.argument('destination-playlist')
@click.argument('url')
def move(origin_playlist, destination_playlist, url):
    manager.move_video(
        origin_playlist=Path(origin_playlist),
        destination_playlist=Path(destination_playlist),
        video_id=helpers.extract_youtube_video_id(url)
    )

@click.command()
@click.argument('playlists-directory')
@click.option('--include-all', '-ia')
def update_cache(playlists_directory, include_all):
    cache.update_full_cache(
        playlists_directory=Path(playlists_directory),
        skip_already_cached=not include_all,
        cache_file=settings.video_cache_file,
        ytdl_options=settings.ytdl_options
    )

@click.command()
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