from urllib.parse import urlparse, parse_qs

from . import api


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
        video_data = api.extract_video_info(url, ytdl)
        _id = video_data.get('id')
    
    if not _id:
        logger.error(f'nenhum método de extração de id funcionou com a url: {url}')
    return _id