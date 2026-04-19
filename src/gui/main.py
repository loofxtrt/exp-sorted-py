from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow,
    QTableWidget, QTableWidgetItem, QAbstractItemView,
    QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QFileDialog, QInputDialog,
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeView
)
from PyQt6.QtGui import QFileSystemModel, QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize

from ..managers.models import Collection, Vault
from ..modules.youtube.main import YouTubeModule


class MainWindow(QMainWindow):
    def __init__(self, scol: Path, root: Path):
        super().__init__()

        # FIXME: TEMPORÁRIO
        self.youtube = YouTubeModule(vault=Vault(root))
        
        # dados e api
        self.scol = scol
        self.collection = Collection.from_file(self.scol)

        # inputs
        self.button_insert = QPushButton('Insert')
        self.button_remove = QPushButton('Remove')
        self.button_move = QPushButton('Move')
        self.button_copy = QPushButton('Copy')

        self.button_remove.clicked.connect(self.action_remove)
        self.button_insert.clicked.connect(self.action_insert)
        self.button_move.clicked.connect(self.action_move)

        self.input_insert = QLineEdit()
        
        # info
        self.label_title = QLabel()
        self.label_entry_count = QLabel()
        self.label_type = QLabel()

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.label_title.setFont(font)

        self.load_info_labels()

        # contents
        self.header = QHBoxLayout()
        self.header.addLayout(self.compose_info_panel())
        self.header.addLayout(self.compose_control_panel())

        self.qlist = self.compose_list_widget()
        self.load_list_contents() # carregar o conteúdo pela primeira vez

        # file tree
        self.root = str(root) # carregar o último root que foi usado
        self.button_root = QPushButton('Pick root')
        self.button_root.clicked.connect(self.action_pick_root)
        
        self.model = None # tem que ser self pq é importante pra operações com a file tree
        self.file_tree = self.compose_file_tree()
        self.file_tree.clicked.connect(self.action_change_collection)

        self.button_create = QPushButton('+')
        self.button_create.clicked.connect(self.action_create_collection)

        # definir o widget central
        central = QWidget()
        self.setCentralWidget(central)

        # definir como os contents vão ser exibidos
        # na ordem vertical, primeiro o control panel, depois a table etc.
        widget_contents = QWidget()
        contents = QVBoxLayout(widget_contents)

        contents.addLayout(self.header)
        contents.addWidget(self.qlist)

        widget_sidebar = QWidget()
        widget_sidebar.setMaximumWidth(350) # é definido no widget inteiro, não só na file tree
        sidebar = QVBoxLayout(widget_sidebar)

        sidebar.addWidget(self.button_root)
        sidebar.addWidget(self.file_tree)
        sidebar.addWidget(self.button_create)

        # layout, definir o que vai estar na horizontal
        # ex: sidebar, file tree, contents etc.
        layout = QHBoxLayout(central)
        layout.addWidget(widget_sidebar)
        layout.addWidget(widget_contents)

    def compose_info_panel(self) -> QVBoxLayout:
        # título fica em cima
        vbox_info = QVBoxLayout()
        vbox_info.addWidget(self.label_title)
        
        # demais informações ficam em baixo
        hbox_sub_info = QHBoxLayout()
        vbox_info.addLayout(hbox_sub_info)
        
        hbox_sub_info.addWidget(self.label_entry_count)
        hbox_sub_info.addWidget(self.label_type)

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

    def compose_list_widget(self) -> QListWidget:
        qlist = QListWidget()
        qlist.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        return qlist

    def compose_file_tree(self) -> QTreeWidget:
        self.model = QFileSystemModel()
        self.model.setRootPath(self.root)

        tree = QTreeView()
        tree.setModel(self.model)

        tree.setRootIndex(self.model.index(self.root))

        tree.setHeaderHidden(True)
        tree.hideColumn(1)
        tree.hideColumn(2)
        tree.hideColumn(3)

        return tree

    def load_list_contents(self):
        self.qlist.clear()
        
        entries = self.collection.entries
        for e in entries:
            # FIXME: TEMPORÁRIO
            if e.module == 'youtube' and e.type == 'video':
                # espera o result em vez de desenpacotar de uma vez
                # pra não quebrar com 'cannot unpack non-iterable NoneType object'
                result = self.youtube.build_entry_widget(e)
                if not result:
                    continue
                item, widget = result
            
                self.qlist.addItem(item)
                self.qlist.setItemWidget(item, widget)

                print('adicionado')

    def load_info_labels(self):
        # atualiza os dados exibidos sobre a collection
        self.label_title.setText(self.collection.name)
        self.label_entry_count.setText(str(self.collection.entry_count))

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

        if not dest:
            return

        dest = Path(dest)
        if not dest.is_file():
            return

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
        
        #if not dest or not is_collection_valid(dest):
        #    return

        self.scol = dest
        self.collection = Collection.from_file(self.scol)
        self.load_list_contents()
        #cache.write_last_collection(dest)

        self.load_info_labels()
    
    def action_change_root(self):
        dest = self.input_root.text()
        if not Path(dest).is_dir():
            return
        self.root = dest
        self.model.setRootPath(self.root)
        self.file_tree.setRootIndex(self.model.index(self.root))

    def action_pick_root(self):
        # define o novo root, o diretório usado pra visualizar
        # quais playlists ele contém
        root = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Pick root'
        )

        if Path(root).is_dir():
            self.root = root
            self.model.setRootPath(root)
            self.file_tree.setRootIndex(self.model.index(root))
        
        cache.write_last_root(Path(root))
    
    def action_create_collection(self):
        text, ok = QInputDialog.getText(
            self,
            'Collection title',
            'Set a title for this collection'
        )

        if ok and text:
            manager.create_collection(
                title=text,
                media_type='videos',
                output_directory=Path(self.root)
            )

def main():
    app = QApplication([])

    file = Path('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei/eumerlyteste.json')
    #file = None

    root = Path('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/testei')

    main_window = MainWindow(file, root)
    main_window.show()

    app.exec()

main()