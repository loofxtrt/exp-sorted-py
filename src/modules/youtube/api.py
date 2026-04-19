import requests

from yt_dlp import YoutubeDL

from ... import logger


SETTINGS = {
    'quiet': True,
    'skip_download': True
}


def instance_ytdl(options: dict | None = None) -> YoutubeDL:
    """
    cria uma instância do youtube-dl

    se for usar o ytdl mais de uma vez na mesma função, dá pra guardar o retorno
    em uma variável pra não ficar recriando a api toda vez

    args:
        options:
            opções de configuração da api
            precisa seguir o formato definido pelo yt-dlp
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

def download_thumbnail_bytes(image_url: str) -> bytes | None:
    """
    baixa uma imagem de uma url e retorna os bytes dela

    essa função só baixa a imagem pra memória e não salva nada em disco
    se precisar salvar, tem que usar uma função auxiliar pra escrever os bytes em arquivo

    args:
        image_url:
            url da imagem que vai ser baixada

    returns:
        bytes da imagem ou None se a requisição falhar
    """
    
    response = requests.get(image_url)
    
    if response.status_code != 200:
        return None
    
    return response.content