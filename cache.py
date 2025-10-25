import json
import helpers
import settings
from pathlib import Path
from yt_dlp import YoutubeDL
from loguru import logger

def get_video_info(video_id: str, cache_file: Path = settings.CACHE_FILE):
    """
    consulta o cache pra tentar obter os dados de um vídeo sem precisar chamar a api do yt-dlp
    se o vídeo já não tiver sido cacheado, a api então é chamada, e depois o cache é reconsultado
    """

    # ler o cache e tentar obter o dict do vídeo pelo seu id
    cache = helpers.json_read_cache(cache_file)
    video_data = cache.get(video_id)

    # se os dados do vídeo estiverem presentes no cache retorna eles,
    # mas se não estiverem, insere os dados no meio da execução
    if video_data:
        return video_data
    else:
        # solicitar a adição do novo vídeo ao cache
        video_url = helpers.build_youtube_url(video_id)
        write_video_cache(video_url, cache_file)

        # depois de atualizado, consultar o cache de novo
        updated_cache = helpers.json_read_cache(cache_file)
        video_data = updated_cache.get(video_id)
        
        return video_data

def write_video_cache(
    url: str, cache_file: Path = settings.CACHE_FILE,
    ytdlp_options: dict = settings.YTDLP_OPTIONS
    ):
    """
    escreve as informações de um vídeo no arquivo de cache
    assim, a api do yt-dlp não precisa ser chamada toda vez que for carregar uma playlist

    @param url:
        url do vídeo que deve ter suas informações exibidas
    
    @param ytdlp_options:
        opções da api do yt-dlp
    """

    # requisitar os dados do vídeo a api, e depois de obter, guardar em variáveis
    # o download do vídeo em si é ignorado
    with YoutubeDL(ytdlp_options) as ytdl:
        info = ytdl.extract_info(url, download=False)
    
    video_id = info.get('id') # dígitos que aparecem depois de watch?v= em urls de vídeos
    title = info.get('title')
    upload_date = info.get('upload_date') # yyyymmdd
    uploader = info.get('uploader')
    view_count = info.get('view_count')
    duration = info.get('duration', 0) # segundos. 0 é fallback se o campo não estiver presente
    description = info.get('description')
    
    # estruturar os dados obtidos em um objeto json
    video_data = {
        'title': title,
        'upload_date': upload_date,
        'uploader': uploader,
        'view_count': view_count,
        'duration': duration,
        'description': description,
    }

    # ler o cache atual e adicionar o objeto dos dados do vídeo a essa lista do cache
    current_cache = helpers.json_read_cache(cache_file)
    current_cache[video_id] = video_data

    with cache_file.open('w', encoding='utf-8') as f:
        json.dump(current_cache, f, indent=4, ensure_ascii=False)