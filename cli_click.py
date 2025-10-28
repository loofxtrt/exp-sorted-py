import click
import manager
import visualizer
import helpers
from pathlib import Path

testing_folder = Path('./tests')

@click.command()
@click.argument('title')
def create(title):
    manager.write_playlist(
        title=title,
        output_dir=testing_folder
    )

@click.command()
@click.argument('playlist')
def delete(playlist):
    manager.delete_playlist(
        playlist_file=Path(playlist)
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
def import_pl(url):
    manager.import_playlist(
        new_title='imported',
        output_dir=testing_folder,
        url=url
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

@click.group()
def cli():
    pass

cli.add_command(import_pl)
cli.add_command(create)
cli.add_command(insert)
cli.add_command(remove)
cli.add_command(view_dir)
cli.add_command(view_pl)

if __name__ == '__main__':
    cli()