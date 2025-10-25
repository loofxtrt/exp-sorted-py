import manager
import visualizer

import argparse
from pathlib import Path

def set_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    create = subparsers.add_parser('create', help='cria uma nova playlist')
    create.add_argument('title', type=str, help='título da playlist')

    insert = subparsers.add_parser('insert', help='insere vídeo(s) numa playlist')
    insert.add_argument('file', type=Path, help='caminho do arquivo da playlist')
    insert.add_argument('urls', nargs='+', type=str, help='urls a serem vídeo adicionadas')

    remove = subparsers.add_parser('remove', help='remove vídeo(s) numa playlist')
    remove.add_argument('file', type=Path, help='caminho do arquivo da playlist')
    remove.add_argument('urls', nargs='+', type=str, help='urls a serem removidas')

    delete = subparsers.add_parser('delete', help='deleta uma playlist inteira')
    delete.add_argument('file', type=Path, help='caminho do arquivo da playlist')

    viewdir = subparsers.add_parser('viewdir', help='visualiza todas as playlists dentro de um diretório')
    viewdir.add_argument('dir', type=Path, help='caminho do diretório a ser visualizado')

    viewpl = subparsers.add_parser('viewpl', help='visualiza os conteúdos de uma playlist individual')
    viewpl.add_argument('file', type=Path, help='caminho do arquivo da playlist a ser visualizada')
    viewpl.add_argument('--descflag', '-df', action='store_true', help='se presente, a descrição do vídeo também será incluída na visualização')

    return parser

def main():
    parser = set_parser()
    args = parser.parse_args()

    if args.command == 'create':
        manager.write_playlist(
            playlist_title=args.title,
            output_dir='./tests'
        )
    elif args.command == 'insert':
        manager.insert_video(
            playlist_file=args.file,
            urls=args.urls
        )
    elif args.command == 'remove':
        manager.remove_video(
            playlist_file=args.file,
            urls=args.urls
        )
    elif args.command == 'viewdir':
        visualizer.view_directory(
            dir=args.dir
        )
    elif args.command == 'viewpl':
        visualizer.view_playlist(
            playlist_file=args.file,
            description_flag=args.descflag
        )
    elif args.command == 'delete':
        manager.delete_playlist(
            playlist_file=args.file,
        )

main()