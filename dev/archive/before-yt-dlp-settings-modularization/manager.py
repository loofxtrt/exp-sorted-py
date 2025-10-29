from helpers import json_read_playlist, json_write_playlist, get_iso_datetime, generate_random_id, extract_youtube_video_id, handle_existing_file, build_youtube_url

from YoutubeDL import yt_dlp
from pathlib import Path
from loguru import logger

def is_entry_present(playlist_file: Path, video_id: str):
    data = json_read_playlist(playlist_file)

    # se existir um dicionário na lista de entries
    # que contenha uma url idêntica a target passada pra função, é true
    if any(entry['id'] == video_id for entry in data['entries']):
        return True
    
    return False

def write_playlist(playlist_title: str, output_dir: Path):
    # obter a data iso já formatada e um id aleatório novo pra playlist
    current_date = get_iso_datetime()
    playlist_id = generate_random_id()

    # construir o caminho final do arquivo    
    final_path = Path(output_dir, playlist_title + '.json')

    # estruturar os dados
    data = {
        #'title': playlist_title,
        'created-at': current_date,
        'id': playlist_id,
        'entries': []
    }
    logger.debug(f'dados a serem escritos em {str(final_path)}: {str(data)}')
    
    if not handle_existing_file(final_path):
        logger.info(f'criação da playlist {playlist_title} cancelada')
        return
    
    # escrever os dados da playlist em um arquivo que a representa
    json_write_playlist(final_path, data)
    
    logger.success(f'arquivo criado em {str(final_path)}')

def delete_playlist(playlist_file: Path):
    answer = input(f'deletar {playlist_file.stem}? (y/N) ').strip().lower()
    if answer == 'y':
        playlist_file.unlink()
        logger.success('playlist deletada')
        return
    
    logger.info("exclusão de playlist cancelada")

def insert_video(playlist_file: Path, urls: list[str]):
    """
    @param: urls
        lista de urls que devem ser inseridas na playlist
        mesmo que seja apenas um vídeo, ele ainda deve vir em lista, pra manter o suporte a vários
    """

    if not playlist_file.exists():
        answer = input('essa playlist ainda não existe, criar ela agora? (Y/n) ').strip().lower()
        
        if answer == 'y':
            write_playlist(playlist_file.stem, playlist_file.parent)
        else:
            return

    # ler os dados atuais da playlist
    data = json_read_playlist(playlist_file)

    for url in urls:
        video_id = extract_youtube_video_id(url)

        # confirmação trivial pra evitar duplicação acidental de urls
        # não quebra nada, só fica com o mesmo vídeo duas vezes na mesma playlist
        existing = is_entry_present(playlist_file, video_id)

        if existing:
            answer = input(f'{url} já está presente nessa playlist, adicionar mesmo assim? (Y/n) ').strip().lower()
            
            if answer == 'n':
                logger.info('inserção de vídeo cancelada')
                return

        # obter a data em que o vídeo foi inserido
        # é útil pra opções de ordenação por data de inserção
        current_date = get_iso_datetime()
        
        # montar o objeto que representa uma entrada de vídeo
        video = {            
            'id': video_id,
            #'url': build_youtube_url(video_id),
            'inserted-at': current_date
        }

        # adicionar a url solicitada ao array e reescrever esses dados novos no mesmo arquivo
        data['entries'].append(video)
        json_write_playlist(playlist_file, data)
        
        logger.success(f'{url} adicionada na playlist {playlist_file.stem}')

def remove_video(playlist_file: Path, urls: list[str]):
    data = json_read_playlist(playlist_file)

    for url in urls:
        # pra cada url alvo, faz uma verificação no campo de entradas de cada playlist
        video_id = extract_youtube_video_id(url)

        for i, entry in enumerate(data['entries']):
            # se a url alvo de remoção estiver presente em um desses campos,
            # remove o índice do dicionário a qual ela pertence e atualiza os dados
            # e depois quebra o loop pra parar na primeira ocorrência
            # se mais de um link for passado pra função, mesmo sendo dois iguais, vão ser duas ocorrências iguais removidas
            if entry['id'] == video_id:
                removed = data['entries'].pop(i)
                json_write_playlist(playlist_file, data)

                logger.success(f'{url} removida da playlist {playlist_file.stem}')
                break
        else:
            # o else só roda se o break não tiver rodado nenhuma vez
            logger.info(f'{url} não está presente na playlist {playlist_file.stem}')

def import_playlist(youtube_playlist_url: str):
    with YoutubeDL()