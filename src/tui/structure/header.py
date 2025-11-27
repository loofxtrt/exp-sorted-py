from pathlib import Path

from textual.widgets import Label
from textual.containers import Vertical

from ...managers.collections import utils
from ...managers import cache

def update(
    collection_file: Path,
    collection_data: dict,
    label_title: Label,
    label_type: Label,
    label_entry_count: Label
    ):
    title = utils.get_title(collection_file)
    entry_count = str(utils.get_entry_count(collection_data))

    label_title.update(f'Title: {title}')
    label_type.update(f'Type: {collection_data.get('type')}')
    label_entry_count.update(f'Entry count: {entry_count}')