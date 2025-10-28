import click
import manager
from pathlib import Path

testing_folder = Path('./tests')

@click.command()
@click.argument('url')
def import_pl(url: str):
    manager.import_playlist('imported', testing_folder, url)

@click.group
def cli():
    pass

cli.add_command(import_pl)

if __name__ == '__main__':
    cli()