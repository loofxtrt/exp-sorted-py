# ESSA VERSÃO NÃO USAVA O ID DO VÍDEO COMOC CHAVE NO JSON

import json
from pathlib import Path
from yt_dlp import YoutubeDL
from loguru import logger

def write_video_cache(
    url: str, cache_file: Path,
    ytdlp_options: dict = { 'quiet': True, 'skip_download': True } ):
    # requisitar os dados do vídeo a api
    # e depois de obter, guardar em variáveis
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
        "id": video_id,
        "title": title,
        "upload_date": upload_date,
        "uploader": uploader,
        "view_count": view_count,
        "duration": duration,
        "description": description
    }

    # ler o cache atual
    if not cache_file.exists() or cache_file.stat().st_size == 0:
        # se o arquivo ainda não existir ou estiver vazio, cria uma lista vazia como fallback
        # stat = propriedades do arquivo, st_size = tamanho em bytes. se for 0, tá vazio
        current_cache = []
    else:
        # caso o arquivo esteja em condições normais, só lê direto
        with cache_file.open('r', encoding='utf-8') as f:
            current_cache = json.load(f)
    
    # adicionar o objeto dos dados do vídeo a essa lista do cache
    current_cache.append(video_data)

    with cache_file.open('w', encoding='utf-8') as f:
        json.dump(current_cache, f, indent=4, ensure_ascii=False)

write_video_cache('https://www.youtube.com/watch?v=5PfE5m5vkMc', Path('./tests/video_cache.json'))