from pathlib import Path

from ..services import youtube
from ..utils import json_io
from ..utils.generic import normalize_json_file
from .. import logger
from .collections.utils import Entry, ServiceMetadata, Video
from .settings import CACHE_DIRECTORY

def insert_entry_on_cache(resolvable_id: str, entry_data: dict, cache_file: Path):
    data = json_io.read_json(cache_file)

    data[resolvable_id] = entry_data
    json_io.write_json(file=cache_file, data=data)

    logger.success(f'entrada escrita no cache: {resolvable_id}')

def get_video(service_metadata: ServiceMetadata) -> Video | None:
    service_name = sm.service_name
    resolvable_id = sm.resolvable_id
    
    cache_file = normalize_json_file(CACHE_DIRECTORY / service_name / 'videos')
    cache_file.parent.mkdir(exist_ok=True, parents=True)

    cache_data = json_io.read_json(cache_file)
    entry_data = cache_data.get(resolvable_id)

    if service_name == 'youtube':
        if entry_data:
            return youtube.video_from_dict(entry_data)
        else:
            ytdl = youtube.instance_ytdl()
        
            url = youtube.build_youtube_url(resolvable_id)
            info = youtube.extract_video_info(url, ytdl)
            
            insert_entry_on_cache(
                resolvable_id=resolvable_id,
                entry_data=info,
                cache_file=cache_file
            )
            return youtube.video_from_dict(info)
    
    return None
            
def get_cached_entry(collection_type: str, entry: Entry):
    sm = entry.service_metadata
    service_name = sm.service_name
    resolvable_id = sm.resolvable_id
    
    cache_file = CACHE_DIRECTORY / service_name / collection_type
    cache_file = normalize_json_file(cache_file)
    cache_file.parent.mkdir(exist_ok=True, parents=True)

    cache_data = json_io.read_json(cache_file)
    entry_data = cache_data.get(resolvable_id)

    cached = None

    if entry_data:
        # if collection_type == 'videos':
        cached = youtube.video_from_dict(entry_data)
    else:
        ytdl = youtube.instance_ytdl()
    
        url = youtube.build_youtube_url(resolvable_id)
        info = youtube.extract_video_info(url, ytdl)
        
        insert_entry_on_cache(
            resolvable_id=resolvable_id,
            entry_data=info,
            cache_file=cache_file
        )
        return youtube.video_from_dict(info)

    return cached



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