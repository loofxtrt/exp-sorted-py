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

def extract_youtube_video_info(url: str, ytdl_instance: YoutubeDL) -> dict | None :
    """
    usa a api do yt-dlp pra extrair dinamicamente os dados de um vídeo
    por fazer uso da api, deve ser evitada na maioria dos casos
    
    essa função geralmente é chamada pela consultora de vídeos já cacheados,
    quando ela tenta buscar um vídeo no cache e ele ainda não existe, ela chama
    
    args:
        url:
            url do vídeo a ser consultado

        ytdl_instance:
            instância já criada da api do yt-dlp. isso evita que múltiplas instâncias precisem ser criadas
    """
    
    try:
        info = ytdl_instance.extract_info(url, download=False)
    except Exception as err:
        logger.error(f'erro ao tentar extrair os dados do vídeo {url}: {err}')
        return None

    video_id = info.get('id') # dígitos que aparecem depois de watch?v= em urls de vídeos
    title = info.get('title')
    upload_date = info.get('upload_date') # yyyymmdd
    uploader = info.get('uploader')
    view_count = info.get('view_count')
    duration = info.get('duration', 0) # segundos. 0 é fallback se o campo não estiver presente
    thumbnail = info.get('thumbnail')
    description = info.get('description')
    
    # estruturar os dados obtidos em um objeto json
    video_data = {
        'id': video_id,
        'title': title,
        'upload_date': upload_date,
        'uploader': uploader,
        'view_count': view_count,
        'duration': duration,
        'description': description,
        'thumbnail': thumbnail,
    }

    return video_data