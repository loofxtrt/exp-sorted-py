import yaml

from helpers import * # geradores de id, leitores etc.

from pathlib import Path
from loguru import logger

def write_playlist(playlist_title: str, output_dir: Path):
    # obter a data iso já formatada e um id aleatório novo pra playlist
    current_data = get_iso_datetime()
    playlist_id = generate_random_id()

    # construir o caminho final do arquivo    
    final_path = Path(output_dir, playlist_title + '.yaml')

    # estruturar os dados
    data = {
        #'title': playlist_title,
        'created-at': current_date,
        'id': playlist_id,
        'urls': []
    }
    logger.debug(f'dados a serem escritos em {str(final_path)}: {str(data)}')
    
    if not handle_existing_file(final_path):
        logger.info(f'criação da playlist {playlist_title} cancelada')
        return
    
    # escrever os dados da playlist em um arquivo que a representa
    yaml_write_playlist(final_path, data)
    
    logger.success(f'arquivo criado em {str(final_path)}')

def insert_video(playlist_file: Path, url: str):
    # ler os dados atuais da playlist
    data = yaml_read_playlist(playlist_file)

    # confirmação trivial pra evitar duplicação acidental de urls
    # não quebra nada, só fica com o mesmo vídeo duas vezes na mesma playlist
    existing = any(item.get('url') == url for item in data['urls'])
    if url in data['urls']:
        answer = input(f'{url} já está presente nessa playlist, adicionar mesmo assim? (Y/n) ').strip().lower()
        
        if answer == 'n':
            logger.info('inserção de vídeo cancelada')
            return

    current_date = get_iso_datetime()

    # adicionar a url solicitada ao array e reescrever esses dados novos no mesmo arquivo
    data['urls'].append(url)
    yaml_write_playlist(playlist_file, data)
    
    logger.success(f'{url} adicionada na playlist {playlist_file.stem}')

def remove_video(playlist_file: Path, url: str):
    data = yaml_read_playlist(playlist_file)
    
    if url in data['urls']:
        # remover o item da lista e atualizar os dados
        data['urls'].remove(url)
        yaml_write_playlist(playlist_file, data)
        
        logger.success(f'{url} removida da playlist {playlist_file.stem}')
    else:
        logger.info(f'{url} não está presente na playlist {playlist_file.stem}')