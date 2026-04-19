from pathlib import Path

from ...managers.models import Vault
from ...utils.generic import ensure_directory
from ...utils import json_io
from ... import logger
from .api import download_thumbnail_bytes
from .models import Video


def _get_cache_root(vault: Vault):
    path = vault.modules_dir / 'youtube' / 'cache'
    ensure_directory(path)
    return path

def _get_videos_file(vault: Vault):
    return _get_cache_root(vault) / 'videos.json'

def _get_thumbnail_path(video_id: str, vault: Vault):
    path = _get_cache_root(vault) / 'thumbnails'
    ensure_directory(path)

    return path / f'{video_id}.png'

def write_video_to_cache(data: dict, vault: Vault):
    data = Video.normalize_ytdl_data(data)
    video_id = data.get('id')
    if not video_id:
        logger.error('id resolvível não encontrado')
        return
    
    file = _get_videos_file(vault)
    existing_data = json_io.read_json(file)
    
    existing_data[video_id] = data
    json_io.write_json(file, existing_data)

def get_video_from_cache(video_id: str, vault: Vault) -> dict | None:
    file = _get_videos_file(vault)
    data = json_io.read_json(file)

    return data.get(video_id)

def download_thumbnail_to_cache(video_data: dict, vault: Vault):
    content = download_thumbnail_bytes(video_data.get('thumbnail'))
    if content:
        dest = _get_thumbnail_path(video_data.get('id'), vault)
        with dest.open('wb') as f:
            f.write(content)