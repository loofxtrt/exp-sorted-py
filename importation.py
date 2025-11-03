import manager
import helpers
import pathvalidate
from pathlib import Path
from yt_dlp import YoutubeDL
from loguru import logger

def extract_youtube_playlist_data(yt_playlist_url: str, ytdl_options: dict) -> dict:
    """
    usa a api do yt-dlp pra obter os dados de uma playlist
    """

    try:
        ytdl = YoutubeDL(ytdl_options)
        info = ytdl.extract_info(yt_playlist_url, download=False)

        logger.success('dados extraídos da playlist')
        return info
    except Exception as err:
        logger.error(f'erro ao importar a playlist: {err}')
        return None

def resolve_imported_playlist_title(yt_playlist_data: dict):
    """
    baseado no título original de uma playlist do youtube, se necessário,  
    sanitiza esse título pra que ele não tenha nenhum caractere inválido pra criação de um arquivo
    """
    
    title = yt_playlist_data.get('title', '')
    
    # conferir se o título obtido não tem nenhum caractere inválido
    # se tiver, sanitiza ele antes antes de retornar
    try:
        pathvalidate.validate_filename(title)

        logger.success(f'título validado: {title}')
        return title
    except pathvalidate.ValidationError:
        logger.error(f'iniciando sanitização. título com caracteres inválidos: {title}')
        
        try:
            title = pathvalidate.sanitize_filename(title)

            logger.success(f'título sanitizado: {title}')
            return title
        except:
            logger.error(f'a sanitização do título {title} falhou. tente definir explicitamente um novo título para a playlist importada')
            return None

def import_playlist(
    output_dir: Path,
    yt_playlist_url: str,
    ytdl_options: dict,
    new_title: str = None
    ):
    """
    importa uma playlist do youtube pra uma playlist local  
    pra funcionar, a playlist passada pra função deve ser pública ou não-listada  
      
    @param output_dir:  
        diretório onde a playlist vai ser criada ao ser importada  
      
    @param yt_playlist_url:  
        url da playlist do youtube  
      
    @param new_title:  
        opcional. novo título pra quando a playlist for importada  
        se não for passado, o título que estava no youtube vai ser usado no lugar  
      
    @param ytdl_option:  
        opções da api do yt-dlp
    """
    
    logger.info(f'iniciando a importação de uma playlist do youtube: {yt_playlist_url}')

    info = extract_youtube_playlist_data(yt_playlist_url, ytdl_options)
    if not info:
        return
    
    # se o usuário não passar explicitamente um título novo pra ela,
    # ela tenta usar o título que tava no youtube
    if not new_title:
        logger.info('o título da playlist será herdado do youtube')
        new_title = resolve_imported_playlist_title(info)
    
    # cria a playlist e reconstrói como é o novo caminho dela
    manager.create_playlist(playlist_title=new_title, output_dir=output_dir, assume_default=True)
    final_path = output_dir / (new_title + '.json')

    # passar todas as urls da playlist do youtube pra playlist local
    # identificando todas as urls de vídeos do campo 'entries' da playlist (vinda do yt-dlp) e obtendo os ids
    logger.success('playlist criada. iniciando a importação dos vídeos dela')
    urls = [entry['webpage_url'] for entry in info['entries'] if entry]

    for u in urls:
        video_id = helpers.extract_youtube_video_id(url=u, ytdl_options=ytdl_options)
        manager.insert_video(playlist_file=final_path, video_id=video_id, assume_default=True)