import requests

from yt_dlp import YoutubeDL

from ... import logger

SETTINGS = {
    'quiet': True,
    'skip_download': True
}

def instance_ytdl(options: dict | None = None) -> YoutubeDL:
    """
    se o ytdl for ser usado duas vezes numa mesma função, a instância retornada
    por essa função pode ser atribuída a uma variável pra evitar a recriação da api

    se isso já tiver sido chamado uma vez, a função retorna a instância já existente
    """
    
    return YoutubeDL(options)

def extract_video_info(url: str, ytdl: YoutubeDL) -> dict | None :
    """
    usa a api do yt-dlp pra extrair dinamicamente os dados de um vídeo
    por fazer uso da api, deve ser evitada se a info já existir no cache

    args:
        url:
            url do vídeo a ser consultado

        ytdl:
            instância já criada da api do yt-dlp. isso evita que múltiplas instâncias precisem ser criadas
    """
    
    try:
        return ytdl.extract_info(url, download=False)
    except Exception as err:
        logger.error(f'erro ao tentar extrair os dados do vídeo {url}: {err}')
        return None

def download_thumbnail(image_url: str):
    response = requests.get(image_url)
    return response