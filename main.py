import manager
import visualizer

import argparse
from pathlib import Path

def set_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    create = subparsers.add_parser('create', help='cria uma nova playlist')
    create.add_argument('title', type=str, help='título da playlist')

    insert = subparsers.add_parser('insert', help='insere um vídeo numa playlist')
    insert.add_argument('file', type=str, help='caminho do arquivo yaml da playlist')
    insert.add_argument('url', type=str, help='url do vídeo a ser adicionado')

    remove = subparsers.add_parser('remove', help='remove um vídeo numa playlist')
    remove.add_argument('file', type=str, help='caminho do arquivo yaml da playlist')
    remove.add_argument('url', type=str, help='url do vídeo a ser removido')

    viewdir = subparsers.add_parser('viewdir', help='visualiza todas as playlists dentro de um diretório')
    viewdir.add_argument('dir', type=str, help='caminho do diretório a ser visualizado')

    return parser

def main():
    parser = set_parser()
    args = parser.parse_args()

    if args.command == 'create':
        manager.write_playlist(
            playlist_title=args.title,
            output_dir=Path('./tests')
        )
    elif args.command == 'insert':
        manager.insert_video(
            playlist_file=Path(args.file),
            url=args.url
        )
    elif args.command == 'remove':
        manager.remove_video(
            playlist_file=Path(args.file),
            url=args.url
        )
    elif args.command == 'viewdir':
        visualizer.view_directory(
            dir=Path(args.dir)
        )

main()