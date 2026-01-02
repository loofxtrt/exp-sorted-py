from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit

from ..utils import formatting
from ..managers.collections import utils
from ..managers.collections.utils import Entry, ServiceMetadata, Video
from ..managers import cache, settings

# add
# remove
# move
# copy

def main():
    app = QApplication([])

    data = utils.read_file(Path('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei/eumerly.json'))
    entries = utils.get_entries(data)

    columns = [
        'Title',
        'Uploader',
        'Duration',
        'View count',
        'Upload date'
    ]

    table = QTableWidget()
    table.setRowCount(len(entries))
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels(columns)

    row = 0
    collection_type = data.get('type')
    for e in entries:
        cached = cache.get_cached_entry(collection_type=collection_type, entry=e)
        column = 0

        if not isinstance(cached, Video):
            continue
        for var in [
            cached.title,
            cached.uploader,
            formatting.format_duration(cached.duration),
            formatting.format_view_count(cached.view_count),
            formatting.format_upload_date(cached.upload_date)
        ]:
            item = QTableWidgetItem(str(var))
            table.setItem(row, column, item)
            
            column += 1
        
        row += 1

    main_window = QMainWindow()
    main_window.setCentralWidget(table)
    main_window.show()

    app.exec()

main()