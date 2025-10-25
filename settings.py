from pathlib import Path

YTDLP_OPTIONS = { 'quiet': True, 'skip_download': True }

# IMPORTANTE: deve sempre ter diferenciação dos .json de dados dos de playlists, se o cache é entendido como uma playlist
# ele pode ficar em outro diretório reservado pra dados do software
CACHE_FILE = Path('./tests/data/video_cache.json')