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
    ytdl: YoutubeDL,
    update_existing_cached: bool = False
    ):
    cache_file = settings.get_cache_file('youtube', _MEDIA_TYPE)

    # extrair o id do vídeo de forma rápida antes de tentar extrair os dados pelo ytdl
    # se esse id já estiver presente no cache, usa os dados atrelados a ele
    video_id = youtube.unstable_extract_video_id(url)
    if video_id:
        video_data = cache.get_cached_entry_data(resolvable_id=video_id, cache_file=cache_file)
    
    # se os dados forem inválidos, significa que ou o vídeo realmente não existe no cache,
    # ou que a primeira extração de id falhou, então é mais seguro tentar de novo usando o ytdl
    # isso é mais demorado, mas também já obtém os demais dados extras do vídeo de uma vez
    if video_data is None:
        video_data = youtube.extract_youtube_video_info(url, ytdl)
        video_id = video_data.pop('id')
        
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
                entry_data=video_data,
                cache_file=cache_file
            )

    manager.insert_entry_service(
        collection=collection,
        resolvable_id=video_id,
        media_type=_MEDIA_TYPE,
        service_name='youtube'
    )