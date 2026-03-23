from pathlib import Path

from ..services import youtube
from ..utils import json_io
from ..utils.generic import normalize_json_file
from .. import logger
from .collections.utils import Entry, ServiceMetadata, Video, is_collection_valid
from .settings import CACHE_DIRECTORY

PATHS = normalize_json_file(CACHE_DIRECTORY / 'paths')

def insert_on_cache(resolvable_id: str, data: dict, cache_file: Path):
    cache = json_io.read_json(cache_file)

    # previnir valores nulos de entrarem no cache
    if not cache or not data or not resolvable_id:
        return

    # escrever os dados no cache usando o resolvable id como chave
    cache[resolvable_id] = data
    json_io.write_json(file=cache_file, data=cache)

    logger.success(f'informação escrita no cache: {resolvable_id}')

def get_video(service_metadata: ServiceMetadata) -> Video | None:
    service_name = service_metadata.service_name
    resolvable_id = service_metadata.resolvable_id
    
    cache_file = normalize_json_file(CACHE_DIRECTORY / service_name / 'videos')
    cache_file.parent.mkdir(exist_ok=True, parents=True)

    cache_data = json_io.read_json(cache_file)
    entry_data = cache_data.get(resolvable_id)

    if service_name == 'youtube':
        # obter o vídeo já do cache ou inserir ele em tempo de exeução
        # caso ele não seja encontrado
        if entry_data:
            return youtube.video_from_dict(entry_data)
        else:
            ytdl = youtube.instance_ytdl()
        
            url = youtube.build_youtube_url(resolvable_id)
            info = youtube.extract_video_info(url, ytdl)
            
            insert_on_cache(
                resolvable_id=resolvable_id,
                data=info,
                cache_file=cache_file
            )
            return youtube.video_from_dict(info)
    
    return None

def get_paths() -> dict:
    return json_io.read_json(PATHS)

def get_last_root() -> Path:
    """
    retorna o último root usado (caso ele esteja presente no cache)
    se não estiver, retorna a home padrão do sistema como root
    
    ambos os caminhos são transformados em absolutos com .resolve()
    """

    data = get_paths()
    raw = data.get('last-root')
    
    if not raw:
        return Path.home().resolve()

    root = Path(raw)

    if not root.is_dir():
        return Path.home().resolve()

    return root.resolve()

def get_last_collection() -> Path | None:
    """
    retorna a última collection aberta
    """

    data = get_paths()
    raw = data.get('last-collection')

    # Path só deve ser chamado depois da verificação
    # porque ele pode ainda não existir no cache e quebrar    
    if not raw:
        return None
    
    collection = Path(raw)

    if not is_collection_valid(collection):
        return None

    return collection.resolve()

def write_last_root(root: Path):
    """
    grava no cache qual foi o último root acessado
    """

    data = get_paths()
    data['last-root'] = str(root.resolve())

    json_io.write_json(PATHS, data)

def write_last_collection(collection: Path):
    data = get_paths()
    data['last-collection'] = str(collection.resolve())

    json_io.write_json(PATHS, data)

# def get_cache_file(service: str, section: str, ensure_creation: bool = True) -> Path | None:
#     """
#     args:
#         service:
#             ex: youtube
        
#         section:
#             ex: videos
#     """

#     file = CACHE_DIRECTORY / service / section
#     file = generic.normalize_json_file(file)
    
#     if not file.exists():
#         if not ensure_creation:
#             logger.error(f'a seção {section} é inválida para o cache de {service}')
#             logger.error(f'o arquivo de cache não existe: {file}')
#             return
#         else:
#             # criar o arquivo se assim especificado
#             file.parent.mkdir(exist_ok=True, parents=True)
#             file.touch()
            
#             logger.success(f'arquivo de cache criado: {file}')

#     return file