from pathlib import Path

from ...utils.generic import Vault
from ...utils import json_io
from ... import logger


def _get_cache_file(vault: Vault):
    return vault.cache_dir / 'youtube.json'

def write_data_to_cache(data: dict, vault: Vault):
    video_id = data.get('id')
    if not video_id:
        logger.error('id resolvível não encontrado')
        return
    
    cache_file = _get_cache_file(vault)
    existing_cache = json_io.read_json(cache_file)
    
    existing_cache[video_id] = data
    json_io.write_json(file, data)

def get_data_from_cache(video_id: str, vault: Vault) -> dict | None:
    cache_file = _get_cache_file(vault)
    data = json_io.read_json(cache_file)

    found = data.get(video_id)
    return found