from pathlib import Path

from yt_dlp import YoutubeDL

from ... import cache, settings
from ...collections import manager, utils
from ...collections.utils import Entry, ServiceMetadata
from ....services import youtube
from .... import logger

_MEDIA_TYPE = 'videos'

def insert_youtube_video(
    collection: Path,
    url: str,
    ytdl: YoutubeDL,
    ) -> Entry:
    video_id = youtube.unstable_extract_video_id(url)
    if not video_id:
        return

    sm = ServiceMetadata(
        service_name='youtube',
        resolvable_id=video_id
    )
    video_data = cache.get_video(sm)
    
    return manager.insert_entry_service(
        collection=collection,
        media_type=_MEDIA_TYPE,
        resolvable_id=video_id,
        service_name='youtube'
    )

def __insert_youtube_video(
    collection: Path,
    url: str,
    ytdl: YoutubeDL,
    update_existing_cached: bool = False
    ):
    video_id = youtube.unstable_extract_video_id(url)

    # extrair o id do vídeo de forma rápida antes de tentar extrair os dados pelo ytdl
    # se esse id já estiver presente no cache, usa os dados atrelados a ele
    if video_id:
        sm = ServiceMetadata(
            service_name='youtube',
            resolvable_id=video_id
        )
        video_data = cache.get_video(sm)

    entry = manager.insert_entry_service(
        collection=collection,
        media_type=_MEDIA_TYPE,
        resolvable_id=video_id,
        service_name='youtube'
    )
    
    # se os dados forem inválidos, significa que ou o vídeo realmente não existe no cache,
    # ou que a primeira extração de id falhou, então é mais seguro tentar de novo usando o ytdl
    # isso é mais demorado, mas também já obtém os demais dados extras do vídeo de uma vez
    if video_data is None:
        video_data = youtube.extract_youtube_video_info(url, ytdl)
        video_id = video_data.pop('id')

        if not video_id:
            return
        
        # inserir ou atualizar os dados desse vídeo no cache
        #
        # se o vídeo NÃO ESTAVA presente no cache até essa inserção,
        # adiciona ele agora, aproveitando os dados já obtidos pelo ytdl
        #
        # se JÁ ESTAVA presente, atualiza os dados dele pros mais novos
        # sobreescrevendo os dados antigos, atualizando, por exemplos, a contagem de views
        # isso só é feito se for explicitamente solicitado
        video_cached = cache.get_cached_entry_data(resolvable_id=video_id, cache_file=cache_file)
        if update_existing_cached or not video_cached:
            cache.insert_entry_on_cache(
                resolvable_id=video_id,
                media_type=_MEDIA_TYPE,
                entry_data=video_data,
                cache_file=cache_file
            )

    inserted = manager.insert_entry_service(
        collection=collection,
        resolvable_id=video_id,
        service_name='youtube',
        return_generated_id=True
    )
    return inserted