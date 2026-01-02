from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QTableWidget, QTableWidgetItem, QAbstractItemView,
    QPushButton, QLineEdit, QLabel,
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeView
)
from PyQt6.QtGui import QFileSystemModel, QFont, QIcon
from PyQt6.QtCore import Qt

from ..utils import formatting
from ..managers.collections import utils
from ..managers.collections.utils import Entry, ServiceMetadata, Video
from ..managers import cache, settings

# insert
# remove
# move
# copy

def compose_videos_table(collection_data: dict) -> QTableWidget:
    entries = utils.get_entries(collection_data)
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

    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # selecionar por row
    table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # múltiplas seleções

    row = 0
    collection_type = collection_data.get('type')
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
            
            # adicionar um id oculto na coluna do título correspondente à entrada
            if var == cached.title:
                item.setData(Qt.ItemDataRole.UserRole, e.id)
            
            table.setItem(row, column, item)
            
            column += 1
        
        row += 1

    return table

def compose_info_header(collection_data: dict, collection_file: Path) -> QVBoxLayout:
    # labels com dados sobre a collection
    label_title = QLabel(utils.get_title(collection_file))
    label_entry_count = QLabel(str(utils.get_entry_count(collection_data)))
    label_type = QLabel(collection_data.get('type').capitalize())

    font = QFont()
    font.setPointSize(16)
    font.setBold(True)
    label_title.setFont(font)

    # título fica em cima
    vbox_info = QVBoxLayout()
    vbox_info.addWidget(label_title)
    
    # demais informações ficam em baixo
    hbox_sub_info = QHBoxLayout()
    vbox_info.addLayout(hbox_sub_info)
    
    hbox_sub_info.addWidget(label_entry_count)
    hbox_sub_info.addWidget(label_type)

    return vbox_info

def compose_control_panel() -> QVBoxLayout:
    # input de texto + botão pra inserir novas entradas
    vbox_control_panel = QVBoxLayout()

    hbox_insert = QHBoxLayout()
    input_insert = QLineEdit()
    button_insert = QPushButton('Insert')
    hbox_insert.addWidget(input_insert)
    hbox_insert.addWidget(button_insert)

    vbox_control_panel.addLayout(hbox_insert)

    # row de ações que podem ser tomadas pra cada entrada
    hbox_actions = QHBoxLayout()
    
    button_remove = QPushButton('Remove')
    button_move = QPushButton('Move')
    button_copy = QPushButton('Copy')

    for b in [button_remove, button_move, button_copy]:
        hbox_actions.addWidget(b)
        b.setDisabled(True) # desabilitar todos

    # button_remove.setIcon(QIcon.fromTheme('edit-delete'))
    # button_copy.setIcon(QIcon.fromTheme('edit-copy'))
    # button_move.setIcon(QIcon.fromTheme('folder-move'))
    # button_insert.setIcon(QIcon.fromTheme('add'))
    
    vbox_control_panel.addLayout(hbox_actions)
    
    return vbox_control_panel

def main():
    app = QApplication([])

    file = Path('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei/eumerly.json')

    data = utils.read_file(file)
    table = compose_videos_table(data)

    central = QWidget()
    layout = QHBoxLayout(central)

    # contents
    c_widget = QWidget()
    contents = QVBoxLayout(c_widget)

    hbox_header = QHBoxLayout()

    vbox_info = compose_info_header(data, file)
    hbox_header.addLayout(vbox_info)

    vbox_control_panel = compose_control_panel()
    hbox_header.addLayout(vbox_control_panel)

    # layout
    layout.addWidget(c_widget)

    contents.addLayout(hbox_header)
    contents.addWidget(table)

    main_window = QMainWindow()
    main_window.setCentralWidget(central)
    main_window.show()

    app.exec()

main()









# sidebar
# s_widget = QWidget()
# sidebar = QVBoxLayout(s_widget)

# model = QFileSystemModel()
# model.setRootPath('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei')

# #tree = QTreeWidget()
# tree = QTreeView()
# tree.setModel(model)

# tree.setRootIndex(model.index('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei'))

# tree.setHeaderHidden(True)
# tree.setColumnWidth(0, 100)
# tree.hideColumn(1)
# tree.hideColumn(2)
# tree.hideColumn(3)

# sidebar.addWidget(tree)

# layout.addWidget(s_widget)











# hbox_search = QHBoxLayout()
# input_search = QLineEdit()
# button_search = QPushButton('Search')
# hbox_search.addWidget(input_search)
# hbox_search.addWidget(button_search)
# contents.addLayout(hbox_search)