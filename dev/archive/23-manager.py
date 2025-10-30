# ESSA VERSÃO NÃO USAVA REMOVE VIDEO NO MOVE VIDEO, ELA REPETIA A LÓGICA

import settings
import helpers
from helpers import json_read_playlist, json_write_playlist, get_iso_datetime, generate_random_id, extract_youtube_video_id, build_youtube_url

from yt_dlp import YoutubeDL
from pathlib import Path
from loguru import logger

def is_entry_present(playlist_file: Path, video_id: str):
    data = json_read_playlist(playlist_file)

    # se existir um dicionário na lista de entries
    # que contenha uma url idêntica a target passada pra função, é true
    if any(entry['id'] == video_id for entry in data['entries']):
        return True
    
    return False

def write_playlist(playlist_title: str, output_dir: Path, assume_default: bool = False):
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
    
    # se a playlist já existir
    if final_path.exists() and final_path.is_file():
        answer = helpers.confirm(
            prompt=f'o arquivo {final_path.name} já existe. prosseguir sobreescreverá ele, continuar?',
            assume_default=assume_default,
            default=False    
        )

        if not answer:
            return

    # escrever os dados da playlist em um arquivo que a representa
    json_write_playlist(final_path, data)
    
    logger.success(f'arquivo criado em {str(final_path)}')

def delete_playlist(playlist_file: Path, assume_default = False):
    if not playlist_file.exists():
        logger.info('a playlist não existe')
        return
    
    answer = helpers.confirm(
        prompt=f'deletar {playlist_file.stem}?',
        assume_default=assume_default,
        default=False
    )
    if not answer:
        return

    playlist_file.unlink()
    logger.success('playlist deletada')

def insert_video(playlist_file: Path, video_id: str, assume_default = False):
    if not video_id: return

    # criar a playlist primeiro caso ela ainda não exista
    if not playlist_file.exists():
        answer = helpers.confirm(
            prompt='essa playlist ainda não existe, criar ela agora?',
            assume_default=assume_default,
            default=True
        )
        if not answer:
            return

        write_playlist(playlist_file.stem, playlist_file.parent)

    # ler os dados atuais da playlist
    data = json_read_playlist(playlist_file)

    # verificação pra evitar duplicação acidental de urls
    existing = is_entry_present(playlist_file, video_id)
    if existing:
        logger.info('o vídeo já está presente na playlist')
        return

    # obter a data em que o vídeo foi inserido
    # é útil pra opções de ordenação por data de inserção
    current_date = get_iso_datetime()
    
    # montar o objeto que representa uma entrada de vídeo
    video = {            
        'id': video_id,
        'inserted-at': current_date
    }

    # adicionar o vídeo solicitado ao array de dicts e reescrever esses dados novos no mesmo arquivo
    data['entries'].append(video)
    json_write_playlist(playlist_file, data)
    
    logger.success(f'{video_id} adicionado na playlist {playlist_file.stem}')

def remove_video(playlist_file: Path, video_id: str):
    if not video_id: return

    data = json_read_playlist(playlist_file)

    for entry in data['entries']:
        # se o id alvo de remoção estiver presente em um desses campos,
        # remove o índice do dicionário a qual ele pertence e atualiza os dados
        if entry['id'] == video_id:
            removed = data.get('entries').remove(video_id)
            json_write_playlist(playlist_file, data)

            logger.success(f'{video_id} removido da playlist {playlist_file.stem}')
            break
    else:
        # se o for inteiro rodar sem nenhum break, o vídeo não foi encontrado
        logger.info(f'{video_id} não está presente na playlist {playlist_file.stem}')

def move_video(origin_playlist: Path, destination_playlist: Path, video_id: str):
    origin_data = helpers.json_read_playlist(origin_playlist)

    dest_title = helpers.get_playlist_title(destination_playlist)
    origin_title = helpers.get_playlist_title(origin_playlist)

    # se o vídeo que está tentando ser movido não existe na playlist de origem
    if is_entry_present(destination_playlist, video_id):
        logger.info(f'o mesmo vídeo ({video_id}) já existe na playlist de destino {dest_title}')
        return

    # se existir, entra na playlist de origem
    # e pra cada entrada, checa se o id é igual ao do vídeo alvo de movimento
    for entry in origin_data.get('entries'):
        # se encontrar o vídeo na playlist de origem
        if entry.get('id') == video_id:
            removed = origin_data.get('entries').remove(entry)
            insert_video(destination_playlist, video_id)

            logger.success(f'vídeo movido de {origin_title}')
        break
    else:
        logger.info(f'o vídeo ({video_id}) não existe na playlist de origem {origin_title}')
        return

    helpers.json_write_playlist(origin_playlist, origin_data)

def import_playlist(output_dir: Path, yt_playlist_url: str, new_title: str = None, ytdlp_options: dict = settings.YTDLP_OPTIONS):
    # tentar obter os dados da playlist
    info = None
    try:
        with YoutubeDL(ytdlp_options) as ytdl:
            info = ytdl.extract_info(yt_playlist_url, download=False)
    except Exception as err:
        logger.error(f'erro ao importar a playlist do youtube {yt_playlist_url}: {err}')

    if not info:
        return

    # construir o caminho do novo arquivo e criar a playlist
    try:
        # usar o título extraído da playlist se um novo título não tiver sido especificado
        if not new_title:
            new_title = info['title']
    
        # e garantir que o título não contenha caracteres conflitantes
        new_title = helpers.clear_risky_characters(new_title)

        final_path = output_dir / (new_title + '.json')
        write_playlist(new_title, output_dir)
    except OSError:
        # usar um id aleatório como fallback
        new_title = helpers.generate_random_id()
        
        final_path = output_dir / (new_title + '.json')
        write_playlist(new_title, output_dir)

    # passar todas as urls da playlist do youtube pra playlist local
    # identificando todas as urls de vídeos do campo 'entries' da playlist e obtendo os ids
    urls = [entry['webpage_url'] for entry in info['entries'] if entry]

    for u in urls:
        video_id = helpers.extract_youtube_video_id(u)
        insert_video(playlist_file=final_path, video_id=video_id)