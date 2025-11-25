from pathlib import Path

from textual.widgets import Label
from textual.containers import Vertical

from ...managers.collections import utils
from ...managers import cache

def build(
    collection_file: Path,
    collection_data: dict
    ) -> Vertical:
    header = Vertical().add_class('plain-container')
    
    title = utils.get_playlist_title(collection_file)
    entry_count = str(utils.get_entry_count(collection_data))

    for var in [title, entry_count]:
        label = Label(var)
        header._add_child(label)
    
    return header

def update(
    collection_file: Path,
    collection_data: dict,
    label_title: Label,
    label_entry_count: Label
    ):
    title = utils.get_title(collection_file)
    entry_count = str(utils.get_entry_count(collection_data))

    label_title.update(f'Collection title: {title}')
    label_entry_count.update(f'Entry count: {entry_count}')