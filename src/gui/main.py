from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QTableWidget, QTableWidgetItem, QAbstractItemView,
    QPushButton, QLineEdit, QLabel, QFileDialog,
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeView
)
from PyQt6.QtGui import QFileSystemModel, QFont, QIcon
from PyQt6.QtCore import Qt

from ..utils import formatting
from ..managers.collections import utils, manager
from ..managers.collections.types import videos
from ..managers.collections.utils import Entry, ServiceMetadata, Video
from ..managers import cache, settings
from ..services import youtube

# - [x] insert
# - [x] remove
# - [x] move
# - [ ] copy
# - [ ] ytdl é criado múltiplas vezes pra uma mesma operação
# - [ ] informações no header não atualizam

def get_selected_ids(table: QTableWidget) -> list[str]:
    # obter todos os índices selecionados
    selection = table.selectionModel()
    indexes = selection.selectedRows()

    ids = []
    for i in indexes:
        row = i.row() # int correspondente ao número do row
        item = table.item(row, 0) # 0 sempre é a coluna com o id oculto

        if not item:
            continue

        # obter o id oculto de cada entry
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        ids.append(entry_id)

    return ids

class MainWindow(QMainWindow):
    def __init__(self, collection_file: Path):
        super().__init__()

        # dados e api
        self.collection_file = collection_file
        self.collection_data = utils.read_file(collection_file)
        self.ytdl = youtube.instance_ytdl()

        # inputs
        self.button_insert = QPushButton('Insert')
        self.button_remove = QPushButton('Remove')
        self.button_move = QPushButton('Move')
        self.button_copy = QPushButton('Copy')

        self.button_remove.clicked.connect(self.action_remove)
        self.button_insert.clicked.connect(self.action_insert)
        self.button_move.clicked.connect(self.action_move)

        self.input_insert = QLineEdit()
        #self.input_root = QLineEdit()
        #self.input_root.textChanged.connect(self.action_change_root)
        
        # contents
        self.header = QHBoxLayout()
        self.header.addLayout(self.compose_info_panel())
        self.header.addLayout(self.compose_control_panel())

        self.table = self.compose_videos_table()
        self.load_table_contents() # carregar o conteúdo pela primeira vez

        # file tree
        self.root = '/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei'
        self.button_root = QPushButton('Pick root')
        self.button_root.clicked.connect(self.action_pick_root)
        
        self.model = None # tem que ser self pq é importante pra operações com a file tree
        self.file_tree = self.compose_file_tree()
        self.file_tree.clicked.connect(self.action_change_collection)

        # definir o widget central
        central = QWidget()
        self.setCentralWidget(central)

        # definir como os contents vão ser exibidos
        # na ordem vertical, primeiro o control panel, depois a table etc.
        widget_contents = QWidget()
        contents = QVBoxLayout(widget_contents)

        contents.addLayout(self.header)
        contents.addWidget(self.table)

        widget_sidebar = QWidget()
        widget_sidebar.setMaximumWidth(350) # é definido no widget inteiro, não só na file tree
        sidebar = QVBoxLayout(widget_sidebar)

        #sidebar.addWidget(self.input_root)
        sidebar.addWidget(self.button_root)
        sidebar.addWidget(self.file_tree)

        # layout, definir o que vai estar na horizontal
        # ex: sidebar, file tree, contents etc.
        layout = QHBoxLayout(central)
        layout.addWidget(widget_sidebar)
        layout.addWidget(widget_contents)

    def compose_info_panel(self) -> QVBoxLayout:
        # labels com dados sobre a collection
        label_title       = QLabel(utils.get_title(self.collection_file))
        label_entry_count = QLabel(str(utils.get_entry_count(self.collection_data)))
        label_type        = QLabel(self.collection_data.get('type').capitalize())

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
    
    def compose_control_panel(self) -> QVBoxLayout:
        # input de texto + botão pra inserir novas entradas
        vbox_control_panel = QVBoxLayout()

        hbox_insert = QHBoxLayout()
        hbox_insert.addWidget(self.input_insert)
        hbox_insert.addWidget(self.button_insert)

        vbox_control_panel.addLayout(hbox_insert)

        # row de ações que podem ser tomadas pra cada entrada
        hbox_actions = QHBoxLayout()

        for b in [self.button_remove, self.button_move, self.button_copy]:
            hbox_actions.addWidget(b)
        
        vbox_control_panel.addLayout(hbox_actions)
        
        return vbox_control_panel

    def compose_videos_table(self) -> QTableWidget:
        columns = [
            'Title',
            'Uploader',
            'Duration',
            'View count',
            'Upload date'
        ]

        table = QTableWidget()

        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns) # mostrar nomes nas colunas em vez de índices

        table.setColumnWidth(0, 600)

        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # selecionar por row
        table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # múltiplas seleções

        return table

    def compose_file_tree(self) -> QTreeWidget:
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root)

        #tree = QTreeWidget()
        tree = QTreeView()
        tree.setModel(self.model)

        tree.setRootIndex(self.model.index(self.root))

        tree.setHeaderHidden(True)
        # tree.setMaximumWidth(250)
        tree.hideColumn(1)
        tree.hideColumn(2)
        tree.hideColumn(3)

        return tree

    def load_table_contents(self):
        # antes de obter as entradas, atualiza os dados locais da classe
        # isso deve ser feito pra ela sempre ser 1:1 com a collection do file system
        # sem isso, mesmo com clearcontents, a tebela ficaria desatualizada
        self.collection_data = utils.read_file(self.collection_file)
        entries = utils.get_entries(self.collection_data)

        self.table.clearContents() # limpar a tabela antes de atualizar
        self.table.clearSelection() # desselecionar tudo ao atualizar
        self.table.setRowCount(len(entries)) # setar o número certo de rows

        row = 0
        collection_type = self.collection_data.get('type')
        for e in entries:
            cached = cache.get_video(e.service_metadata)
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
                
                # adicionar um id oculto correspondente à entrada na coluna 0
                # esse id NÃO é o id resolvivel do serviço
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, e.id)
                
                self.table.setItem(row, column, item)        
                column += 1
            
            row += 1

    def action_remove(self):
        ids = get_selected_ids(self.table)
        for i in ids:
            manager.remove_entry(self.collection_file, i)
        
        self.load_table_contents()
    
    def action_move(self):
        # promptar o caminho novo pra entrada
        dest, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select entry destination',
            filter='json (*.json)'
        )
        dest = Path(dest)

        # se o destino for do mesmo tipo que a collection atual, é uma moção válida
        if utils.file_collection_type_matches('videos', dest):
            ids = get_selected_ids(self.table)
            for i in ids:
                manager.move_entry(
                    src_collection=self.collection_file,
                    dest_collection=dest,
                    entry_id=i
                )
            
            self.load_table_contents()

    def action_insert(self):
        # obtém o conteúdo do input de texto e adiciona na collection
        value = self.input_insert.text()
        videos.insert_youtube_video(
            collection=self.collection_file,
            ytdl=self.ytdl,
            url=value
        )

        self.load_table_contents()
    
    def action_change_collection(self, index):
        # obtém o caminho de um arquivo clicado na file tree
        # e se for uma collection válida, atualiza a visualização pra ela
        model = self.file_tree.model()

        dest = model.filePath(index)
        dest = Path(dest)
        if utils.file_collection_type_matches('videos', dest):
            self.collection_file = dest
            self.load_table_contents()
    
    # def action_change_root(self):
    #     dest = self.input_root.text()
    #     if not Path(dest).is_dir():
    #         return
    #     self.root = dest
    #     self.model.setRootPath(self.root)
    #     self.file_tree.setRootIndex(self.model.index(self.root))

    def action_pick_root(self):
        root = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Pick root'
        )
        if Path(root).is_dir():
            self.root = root
            self.model.setRootPath(root)
            self.file_tree.setRootIndex(self.model.index(root))
        

def main():
    app = QApplication([])

    file = Path('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei/eumerlyteste.json')

    main_window = MainWindow(file)
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