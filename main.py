import manager
import argparse
from pathlib import Path

def set_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    create = subparsers.add_parser('create', help='cria uma nova playlist')
    create.add_argument('title', type=str, help='título da playlist')

    return parser

def main():
    parser = set_parser()
    args = parser.parse_args()

    if args.command == 'create':
        manager.write_playlist(
            playlist_title=args.title,
            output_dir=Path('./tests')
        )

main()