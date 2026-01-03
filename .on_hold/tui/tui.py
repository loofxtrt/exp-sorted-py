from pathlib import Path
import shutil
import platform

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Input, Label, Footer, DirectoryTree
from textual.containers import Horizontal, Vertical
from rich.text import Text
from yt_dlp import YoutubeDL
import pyperclip

from ..managers import cache, settings
from ..managers.collections import manager as collection_manager, utils as collection_utils
from ..managers.collections.types import videos
from ..utils import json_io, formatting, clipboard
from ..services import youtube
from . import structure, controller

def get_video_title(video_id: str) -> str | None:
    # obtém o título do vídeo
    # útil pra notificações ou logging. o id puro não é intuitivo pra leitura humana
    data = cache.get_cached_entry_data(resolvable_id=video_id, cache_file=self.video_cache_file)
    title = data.get('title', None)

    return title

def toggle_picking_state(app: App, state: bool):
    """
    toggle do estado de picking  
    """

    app.picking_state = state

    if app.picking_state:
        app.notify('Picking mode enabled', severity='information')
    else:
        app.notify('Picking mode disabled', severity='information')

def update_header(app: App):
    structure.header.update(
        collection_file=app.playlist_file,
        collection_data=app.playlist_data,
        label_title=app.header_title,
        label_entry_count=app.header_video_count,
        label_type=app.header_type
    )

# from textual.widgets.tree import TreeNode
# class IconizedDirectoryTree(DirectoryTree):
#     def render_label(self, node: TreeNode, base_style, guide_style) -> Text:
#         path = node.data
#         
#         if not path.is_dir():
#             return
#         collection = collection_utils.read_file(path)
#         if not collection:
#             return
#         if collection.get('type') == 'posts':
#             icon = "󰯗 "
#         
#         return Text(icon + name, style=base_style)

class PlaylistView(App):
    # cores da logo
    #ffc971 amarelo
    #763fc4 roxo
    #496fc0 azul
    #52c58d verde

    # essas constantes já são aplicadas automaticamente pelo textual
    BINDINGS = [
        ('^q', 'quit', 'Quit'),
        ('m', 'move', 'Move selected'),
        ('d', 'delete', 'Delete selected'),
        ('i', 'insert', 'Insert entry'),
        ('u', 'url', 'Copy selected URL'),
        ('c', 'clear', 'Clear inputs')
    ]
    CSS_PATH = "style.tcss"

    def __init__(self, playlist_file: Path, video_cache_file: Path, master_directory: Path, ytdl: YoutubeDL, **kwargs):
        super().__init__(**kwargs) # herdar o comportamento da classe padrão

        self.playlist_file = playlist_file
        self.video_cache_file = video_cache_file
        self.master_directory = master_directory
        self.ytdl = ytdl

        # lê aqui e declara como self pra não precisar ler múltiplas vezes
        self.playlist_data = collection_utils.read_file(playlist_file)

        self.selected_row_keys = [] # lista de rows selecionados da tabela
        self.picking_state = False # indica se o usuário está ou não em estado de seleção de um destino

    def compose(self) -> ComposeResult:
        # cria e adiciona os widgets iniciais ao app
        
        self.header = Vertical().add_class('plain-container')
        with self.header:
            self.header_title = Label()
            self.header_type = Label()
            self.header_video_count = Label()

            yield Label('󰪶 Viewing a collection')
            yield self.header_title
            yield self.header_type
            yield self.header_video_count
        
        update_header(self)

        with Horizontal():
            # abrir a file tree no diretório principal
            self.file_tree = DirectoryTree(str(self.master_directory))
            self.file_tree.ICON_FILE = '󰪶 ' # nf-md
            self.file_tree.ICON_NODE = '󰉖 '
            self.file_tree.ICON_NODE_EXPANDED = '󰷏 '
            yield self.file_tree

            # conteúdo principal
            with Vertical():
                # inputs
                with Vertical().add_class('plain-container'):
                    # url de um novo vídeo a ser adicionado a playlist
                    insert_container, self.video_input = structure.input.build(
                        label_contents='󰃃 Insert entry',
                        placeholder_contents='https://www.youtube.com/watch?v=erb4n8PW2qw'
                    )
                    yield insert_container
                    #󰍉 Search entry
                    #󰒿 Sort entries by
                    #󰧧 Delete collection
                    #󱇨 Edit collection
                    #󱀱 Move collection
                
                # tabela da playlist
                self.table = DataTable(cursor_type='row')
                self.table.focus() # foca na tabela quando entra na tela, e não nos inputs
                yield self.table

        self.footer = Footer()
        self.footer.show_command_palette = False
        yield self.footer

    def on_mount(self):
        # depois do app inicializar, quando estiver seguro fazer alterações
        structure.table.update_collection_table(
            table=self.table,
            collection_data=self.playlist_data,
            cache_file=self.video_cache_file
        )

    # detectar eventos de seleção (por padrão, enter) em rows
    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        # obtém a row_key, um dado oculto relacionado do row alvo do evento, e usa ela pra obter os dados desse mesmo row
        # nesse contexto, a row_key CONTÉM sempre o id do vídeo que o row representa (ela não é o id em si)
        row_key = event.row_key
        row_data = self.table.get_row(row_key)

        # depois, verifica se essa row_key já tá na lista de ids selecionados
        # se estiver, remove ela da lista. se não estiver, adiciona ela na lista
        def toggle_selection(value: bool):
            # o x aparece pra indicar que o row está selecionado
            value = ' ' if value == False else 'x'
            
            self.table.update_cell(
                row_key=row_key,
                column_key='selection-status',
                value=value
            )

        if row_key in self.selected_row_keys:
            self.selected_row_keys.remove(row_key)
            toggle_selection(False)
        else:
            self.selected_row_keys.append(row_key)
            toggle_selection(True)
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        """
        ao selecionar um arquivo que seja uma playlist válida na file tree,  
        esse arquivo passa a ser a playlist atual, recarregando a tabela pra visualização dele  
        também zera as variáveis relacionadas a playlist anterior, como os selecionados
        """

        selected_file = event.path
        playlist_data = collection_utils.read_file(selected_file)

        # se estiver no estado de moção de entradas, a próxima collection a ser focada na file tree
        # vira o destino daquela moção. após a moção, o status e dados são limpos,
        # a menos que a moção falhe, aí os dados (tipo o destino e lista de selecionados) continuam
        if self.picking_state:
            source = self.playlist_file
            destination = selected_file

            status = controller.move_entries(
                app=self,
                src_collection=source,
                dest_collection=destination,
                selected_row_keys=self.selected_row_keys,
                collection_table=self.table
            )
            if not status:
                return
            
            toggle_picking_state(self, False)
            destination = None
            return

        # selecionar normalmente caso nenhum estado especial esteja ativo
        # atualizar a tabela, o header, e zerar os dados
        self.playlist_file = selected_file
        self.playlist_data = playlist_data
        self.selected_row_keys = []

        structure.table.update_collection_table(
            table=self.table,
            collection_data=self.playlist_data,
            cache_file=self.video_cache_file
        )

        update_header(self)

    def on_key(self, event):
        if event.key == 'm':
            """
            mover os vídeos selecionados pro endereço definido ao pressionar a tecla
            """
            if not self.picking_state:
                toggle_picking_state(self, True)

        if event.key == 'd':
            """
            deleta os vídeos selecionados da playlist atual
            """

            for row_key in self.selected_row_keys:
                # remover da tabela e obter o id do vídeo
                self.selected_row_keys.remove(row_key)
                self.table.remove_row(row_key)
                video_id = row_key.value

                # obter o título pra notificar
                title = get_video_title(video_id)
                self.notify(message=f'Removed {title}', severity='information')

                # remoção real do vídeo
                collection_manager.remove_entry(
                    collection=self.playlist_file,
                    entry_id=video_id
                )
        
        if event.key == 'i':
            """
            adiciona um novo vídeo à playlist
            """

            video_url = self.video_input.value
            if video_url.strip() == '':
                self.notify(message='No URL provided', severity='warning')
                return

            video_id = youtube.handle_video_id_extraction(video_url, self.ytdl_options)
            if not video_id:
                self.notify(message=f'Could not extract video ID from {video_url}', severity='error')
                return

            # obtém os dados do vídeo
            # feito aqui mesmo pq é mais barato do que recarregar a tabela inteira
            # assim, o row individual pode ser adicionado em tempo de execução
            # e as notificações também podem usar o título do vídeo sem custos adicionais
            video_data = cache.get_cached_entry_data(video_id, self.video_cache_file)
            if not video_data:
                self.notify(message='Something went wrong while extracting the video data', severity='error')
                return
            
            title = video_data.get('title', None)
            
            # inserir o vídeo na playlist atual
            # e também atualizar na tabela
            try:
                inserted = videos.insert_youtube_video(
                    collection=self.playlist_file,
                    ytdl=self.ytdl
                )

                entry_id = inserted.get('id')
                table.insert_entry_row(
                    entry_data=video_data,
                    entry_id=entry_id,
                    table=self.table
                )

                self.notify(message=f'Inserted {title}')
            except manager.InvalidPlaylist as err:
                self.notify(message=f'Something is wrong with the destination playlist: {err}', severity='error')
            except manager.EntryAlreadyExists:
                self.notify(message=f'{title} ({video_id}) already exists in the destination playlist', severity='information')

        if event.key == 'c':
            """
            limpa os principais campos de input
            """

            self.video_input.value = ''
        
        if event.key == 'u':
            """
            copia a url do primeiro vídeo selecionado da lista pra área de transferência do sistema
            """
            if not clipboard.has_clipboard_support():
                self.notify(message='No clipboard support found', severity='error')

            if not len(self.selected_row_keys) > 0:
                self.notify(message='No videos selected', severity='warning')
                return

            video_id = self.selected_row_keys[0].value
            if not video_id:
                self.notify(message='Could not identify the first video of the selected list', severity='error')
                return

            video_url = youtube.build_youtube_url(video_id)
            if not video_url:
                self.notify(message=f'Could not build URL from the ID {video_id}')
                return
            
            try:
                pyperclip.copy(video_url)
                self.notify(message=f'URL copied {video_url}', severity='information')
            except Exception as err:
                self.notify(message=f'Something went wrong while copying the URL: {err}', severity='error')

def main(playlist_file: Path, master_directory: Path, video_cache_file: Path, ytdl: dict):
    if not master_directory.is_dir():
        return

    app = PlaylistView(
        playlist_file=playlist_file,
        master_directory=master_directory,
        video_cache_file=video_cache_file,
        ytdl=ytdl
    )
    app.run()