from pathlib import Path

from ..utils import json_io
from .. import logger

def insert_entry_on_cache(resolvable_id: str, entry_data: dict, cache_file: Path):
    data = json_io.read_json(cache_file)

    data[resolvable_id] = entry_data
    json_io.write_json(file=cache_file, data=data)

    logger.success(f'entrada escrita no cache: {resolvable_id}')

def get_cached_entry_data(resolvable_id: str, cache_file: Path) -> dict | None:
    data = json_io.read_json(cache_file)
    return data.get(resolvable_id)