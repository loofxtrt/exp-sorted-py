from pathlib import Path

from ...collections import manager, utils
from ....services import reddit
from .... import logger

_MEDIA_TYPE = 'posts'

def insert_reddit_post(collection: Path, url: str):
    data = reddit.get_post_info(url)
    if not data:
        logger.error(f'erro ao obter os dados do post {url}')
        return
    
    post_id = data.get('id')

    manager.insert_entry(
        collection=collection,
        media_type=_MEDIA_TYPE,
        entry_id=post_id,
        entry_service='reddit'
    )
    