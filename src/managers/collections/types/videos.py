from pathlib import Path

from yt_dlp import YoutubeDL

from ... import cache, settings
from ...collections import manager, utils
from ....services import youtube
from .... import logger

_MEDIA_TYPE = 'videos'

def insert_youtube_video(
    collection: Path,
    url: str,
    ytdl: YoutubeDL
    ):
    cache_file = settings.get_cache_file('youtube', _MEDIA_TYPE)

    # extrair o id do vídeo de forma rápida antes de tentar extrair os dados pelo ytdl
    # se esse id já estiver presente no cache, usa os dados atrelados a ele
    # se não, extrai todos os dados do vídeo de forma mais demorada, incluindo o id de novo
    video_id = youtube.unstable_extract_video_id(url)
    if video_id:
        video_data = cache.get_cached_entry_data(resolvable_id=video_id, cache_file=cache_file)
    if video_data is None:
        video_data = youtube.extract_youtube_video_info(url, ytdl)
        video_id = video_data.pop('id')
        
        cache.insert_entry_on_cache(
            resolvable_id=video_id,
            entry_data=video_data,
            cache_file=cache_file
        )

    manager.insert_entry_service(
        collection=collection,
        resolvable_id=video_id,
        media_type=_MEDIA_TYPE,
        service_name='youtube'
    )