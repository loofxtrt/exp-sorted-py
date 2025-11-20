from urllib.parse import urlparse, parse_qs
from yt_dlp import YoutubeDL
import logger

def build_youtube_url(video_id: str):
    """
    reconstrói uma url do youtube a partir do id de um vídeo
    é majoritariamente usada quando um vídeo precisa ser passado pro yt-dlp
    """

    return f'https://www.youtube.com/watch?v={video_id}'

def extract_youtube_video_id(url: str, ytdl_options: dict):
    """
    extrai o id de um vídeo por uma url do youtube
    o yt-dlp já tem um método pra obter o id, mas esse método é mais rápido
    ele é menos confiável que o yt-dlp, então se ele quebrar, ele usa a api como fallback
    """

    # tenta extrair por regex, que é mais rápido, mas menos robusto
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url # adiciona esquema se faltar

    query = urlparse(url)
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        return parse_qs(query.query).get('v', [None])[0]
    elif query.hostname == 'youtu.be':
        return query.path.lstrip('/')

    # se não conseguir o id só pelo regex, tenta com o yt-dlp
    logger.warning('erro ao extrair id com regex. tentando novamente com a api do yt-dlp')

    try:
        ytdl = YoutubeDL(ytdl_options)
        info = ytdl.extract_info(url, download=False)

        return info.get('id', None)
    except:
        logger.error(f'erro ao extrair id com a api do yt-dlp')
    
    logger.critical(f'nenhum método de extração de id funcionou com a url: {url}')
    return None