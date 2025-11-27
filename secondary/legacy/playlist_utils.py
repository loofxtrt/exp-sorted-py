from pathlib import Path

from ...utils import json_io, formatting
from ... import logger
from .. import cache

def get_playlist_file_by_id(playlist_id: str, directory: Path):
    """
    a partir do diretório passado pra função, verifica todas as playlists válidas nele  
    e tenta achar uma que contém o mesmo id passado
    """

    # ler todos os arquivos até achar uma playlist com o mesmo id passado
    for f in directory.iterdir():
        data = json_io.json_read_playlist(f)

        if not is_playlist_valid(playlist_file=f, playlist_data=data):
            continue
    
        if data.get('id') == playlist_id:
            return f
    
    logger.error(f'erro ao obter o arquivo da playlist com o id: {playlist_id}')
    return None

def get_playlist_title(playlist_file: Path):
    # o título de uma playlist é o nome do arquivo sem a extensão
    if playlist_file.exists() and playlist_file.is_file():
        return playlist_file.stem

def get_playlist_video_count(playlist_data: dict):
    return len(playlist_data.get('entries'))

def get_playlist_duration(playlist_data: dict, video_cache_file: Path):
    duration = 0
    for e in playlist_data.get('entries'):
        video = cache.get_cached_video_info(e.get('id'), video_cache_file)
        if not video:
            continue

        duration += video.get('duration')
    
    duration = formatting.format_duration(duration)
    return duration

def is_playlist_valid(playlist_file: Path, playlist_data: dict | None = None, superficial_validation: bool = False) -> bool:
    """
    verifica a validade de uma playlist ou seus dados
    a verificação de dados é necessária porque o arquivo pode ser um json válido,
    mas não ter a estrutura esperada de uma playlist

    args:
        playlist_file:
            obrigatório. nem toda chamada da função requer reler o arquivo inteiro
            mas toda chamada requer verificar a extensão/sufixo do arquivo
    
        playlist_data:
            opicional. se for passado, a playlist não precisa ser lida duas vezes desnecessariamente
            quando uma função precisa saber se uma playlist é válida, mas ao mesmo tempo também já leu ela
            pode só passar os dados já extraídos pra validação

        superficial_validation:
            opcional. se for verdadeiro, faz a checagem apenas baseada nas informações externas,
            como a existência, sufixo ou tipo do arquivo. é menos preciso, mas mais rápido por não precisar de i/o
    """
    logger.info(f'iniciando verificação de:\narquivo: {playlist_file}\ndados: {playlist_data}')

    # múltiplos ifs em vez de um só pra mais clareza e diagnóstico
    if not playlist_file.exists():
        logger.warning(f'o arquivo não existe: {playlist_file}')
        return False
    if not playlist_file.is_file():
        logger.warning(f'o caminho não representa um arquivo: {playlist_file}')
        return False
    if not playlist_file.suffix == '.json':
        logger.warning(f'o arquivo não é tem a extensão .json: {playlist_file}')
        return False

    # parar logo aqui se for uma verifiação superficial
    if superficial_validation:
        return True
    
    # se o conteúdo já aberto não tiver sido passado pra função, lê em tempo de execução
    # se não encontrar nada, já é inválido
    if playlist_data is None:
        playlist_data = json_io.json_read_playlist(playlist_file)
        
        if not playlist_data:
            logger.warning(f'não foi possível ler o arquivo a ser validado: {playlist_data}')
            return False

    # se um desses campos não estiverem nos dados extraídos, é inválido
    required_fields = ['entries', 'id']
    
    for field in required_fields:
        if field not in playlist_data:
            return False

    # se as entries não forem uma lista, é inválido
    if not isinstance(playlist_data['entries'], list):
        return False

    # se nenhuma das ocorrências a cima acontecer, é válido
    return True

def is_entry_present(playlist_data: dict, video_id: str):
    # se existir um dicionário na lista de entries
    # que contenha uma url idêntica a target passada pra função, é true
    if any(entry.get('id') == video_id for entry in playlist_data['entries']):
        return True
    
    return False