import manager
import settings as stg

def by_uploader(yt_playlist_url: str, uploader: str, output_dir: Path):
    """
    obtém os vídeos de uma playlist no youtube, identifica quais foram upados pela mesma pessoa  
    e então cria uma nova playlist local apenas com os vídeos upados por aquela pessoa
    """
    settings = stg.Settings()
    
    manager.import_playlist(
        output_dir=output_dir,
        yt_playlist_url=yt_playlist_url,
        new_title=uploader,
        ytdl_options=settings.ytdl_options
    )