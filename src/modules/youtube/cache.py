from pathlib import Path

from ...managers.models import Vault
from ...utils.generic import ensure_directory
from ...utils import json_io
from ... import logger
from .api import download_thumbnail_bytes
from .models import Video


def _get_cache_root(vault: Vault):
    """
    retorna o diretório de cache desse módulo

    args:
        vault:
            instância do vault onde esse módulo está
    """

    path = vault.modules_dir / 'youtube' / 'cache'
    ensure_directory(path)
    return path

def _get_videos_file(vault: Vault):
    """
    retorna o arquivo json onde os vídeos ficam salvos no cache
    """

    return _get_cache_root(vault) / 'videos.json'

def _get_thumbnail_path(video_id: str, vault: Vault):
    """
    retorna o caminho onde a thumbnail de um vídeo pertence
    pode ser usada tanto na fase de download quanto na de busca

    args:
        video_id:
            id do vídeo no youtube

        vault:
            instância do vault onde o arquivo vai ser armazenado
    """

    path = _get_cache_root(vault) / 'thumbnails'
    ensure_directory(path)

    return path / f'{video_id}.jpg'

def write_video_to_cache(data: dict, vault: Vault):
    """
    salva ou atualiza um vídeo no cache local
    se o vídeo já existir, ele é sobrescrito com os dados novos

    args:
        data:
            dados do vídeo vindos da api

        vault:
            instância do vault onde o cache vai ser salvo
    """

    data = Video.normalize_ytdl_data(data)
    video_id = data.get('id')
    if not video_id:
        logger.error('id resolvível não encontrado')
        return
    
    file = _get_videos_file(vault)
    existing_data = json_io.read_json(file)
    
    existing_data[video_id] = data
    json_io.write_json(file, existing_data)

def get_video_from_cache(video_id: str, vault: Vault) -> dict | None:
    """
    busca um vídeo que possivelmente já existe no cache local

    args:
        video_id:
            id do vídeo que vai ser procurado

        vault:
            instância do vault onde o cache está salvo

    returns:
        dados do vídeo ou None se não existir
    """

    file = _get_videos_file(vault)
    data = json_io.read_json(file)

    return data.get(video_id)

def download_thumbnail_to_cache(video_data: dict, vault: Vault):
    """
    baixa a thumbnail de um vídeo no cache local
    se o download dos bytes falhar, nada é salvo no disco

    vai sempre tentar obter uma thumbnail com resolução menor
    antes de ir pra maior como fallback

    se não existir uma maior dentro da lista 'thumbnails',
    usa a thumbnail principal como segundo fallback

    É ESPERADO QUE ESSA LISTA JÁ TENHA SIDO NORMALIZADA PELO MODULO
    E QUE NÃO SEJA A LISTA BRUTA QUE O YT-DLP RETORNA
    
    a principal e a maior normalmente já são as mesmas,
    mas é seguro confiar na 'thumbnail' como fonte da verdade

    args:
        video_data:
            dados do vídeo contendo o id dele e a url da thumbnail

        vault:
            instância do vault onde o arquivo vai ser salvo
    """
    
    thumbnail_url = None
    
    thumbnails = video_data.get('thumbnails')
    for t in thumbnails:
        if t.get('resolution_name') == 'mqdefault':
            logger.info('thumbnail mq encontrada')
            thumbnail_url = t.get('url')
        elif t.get('resolution_name') == 'maxresdefault':
            logger.info('thumbnail maxres encontrada')
            thumbnail_url = t.get('url')

    if thumbnail_url is None:
        logger.info('usando thumbnail padrão')
        thumbnail_url = video_data.get('thumbnail')

    content = download_thumbnail_bytes(thumbnail_url)
    if content:
        dest = _get_thumbnail_path(video_data.get('id'), vault)
        with dest.open('wb') as f:
            f.write(content)