# ESSA VERSÃO NÃO ACEITAVA MÚLTIPLOS LINKS NA INSERÇÃO E REMOÇÃO

from helpers import * # geradores de id, leitores etc.

from pathlib import Path
from loguru import logger

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

def insert_video(playlist_file: Path, url: str):
    # ler os dados atuais da playlist
    data = json_read_playlist(playlist_file)

    # confirmação trivial pra evitar duplicação acidental de urls
    # não quebra nada, só fica com o mesmo vídeo duas vezes na mesma playlist
    # se existir um dicionário na lista de entries que contenha uma chave url
    # com o mesmo valor da passada pra função, o input é triggado
    existing = any(item.get('url') == url for item in data['entries'])

    if url in data['entries']:
        answer = input(f'{url} já está presente nessa playlist, adicionar mesmo assim? (Y/n) ').strip().lower()
        
        if answer == 'n':
            logger.info('inserção de vídeo cancelada')
            return

    # obter a data em que o vídeo foi inserido
    # é útil pra opções de ordenação por data de inserção
    current_date = get_iso_datetime()
    
    # montar o objeto que representa uma entrada de vídeo
    video = {
        'url': url,
        'inserted-at': current_date
    }

    # adicionar a url solicitada ao array e reescrever esses dados novos no mesmo arquivo
    data['entries'].append(video)
    json_write_playlist(playlist_file, data)
    
    logger.success(f'{url} adicionada na playlist {playlist_file.stem}')

def remove_video(playlist_file: Path, url: str):
    data = json_read_playlist(playlist_file)
    
    if url in data['entries']:
        # remover o item da lista e atualizar os dados
        data['entries'].remove(url)
        json_write_playlist(playlist_file, data)
        
        logger.success(f'{url} removida da playlist {playlist_file.stem}')
    else:
        logger.info(f'{url} não está presente na playlist {playlist_file.stem}')