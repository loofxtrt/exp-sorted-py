from urllib.parse import urlparse, parse_qs

from yt_dlp import YoutubeDL

from .. import logger
from ..managers import settings

def instance_ytdl(options: dict | None = None):
    """
    se o ytdl for ser usado duas vezes numa mesma função, a instância retornada
    por essa função pode ser atribuída a uma variável pra evitar a recriação da api
    """

    if options is None:
        options = settings.get('ytdl-options')

    ytdl = YoutubeDL(options)
    return ytdl

def build_youtube_url(video_id: str):
    """
    reconstrói uma url do youtube a partir do id de um vídeo
    é majoritariamente usada quando um vídeo precisa ser passado pro yt-dlp
    """

    return f'https://www.youtube.com/watch?v={video_id}'

def unstable_extract_video_id(url: str) -> str | None:
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url # adiciona esquema se faltar

    query = urlparse(url)
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        return parse_qs(query.query).get('v', [None])[0]
    elif query.hostname == 'youtu.be':
        return query.path.lstrip('/')

def handle_video_id_extraction(url: str, ytdl: YoutubeDL):
    """
    extrai o id de um vídeo por uma url do youtube
    o yt-dlp já tem um método pra obter o id, mas esse método é mais rápido
    ele é menos confiável que o yt-dlp, então se ele quebrar, ele usa a api como fallback

    IMPORTANTE: se os dados completos de um vídeo já foram extraídos,
    não tem necessidade de extrair o id separadamente
    """

    # tenta extrair por regex, que é mais rápido, mas menos robusto
    _id = unstable_extract_video_id(url)

    # se não conseguir o id só pelo regex, tenta com o yt-dlp
    if not _id:
        logger.warning('erro ao extrair id com regex. tentando novamente com a api do yt-dlp')
        video_data = extract_video_info(url, ytdl)
        _id = video_data.get('id')
    
    if not _id:
        logger.error(f'nenhum método de extração de id funcionou com a url: {url}')
    return _id

def extract_video_info(url: str, ytdl: YoutubeDL) -> dict | None :
    """
    usa a api do yt-dlp pra extrair dinamicamente os dados de um vídeo
    por fazer uso da api, deve ser evitada na maioria dos casos
    
    essa função geralmente é chamada pela consultora de vídeos já cacheados,
    quando ela tenta buscar um vídeo no cache e ele ainda não existe, ela chama
    
    args:
        url:
            url do vídeo a ser consultado

        ytdl:
            instância já criada da api do yt-dlp. isso evita que múltiplas instâncias precisem ser criadas
    """
    
    try:
        info = ytdl.extract_info(url, download=False)
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
    #description = info.get('description')
    
    # estruturar os dados obtidos em um objeto json
    video_data = {
        'id': video_id,
        'title': title,
        'upload_date': upload_date,
        'uploader': uploader,
        'view_count': view_count,
        'duration': duration,
        #'description': description,
        'thumbnail': thumbnail,
    }

    return video_data