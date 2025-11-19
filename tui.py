import cache
import helpers
import manager
import pyperclip
import shutil
import platform
import settings
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Input, Label, Footer, DirectoryTree
from textual.containers import Horizontal, Vertical
from rich.text import Text

def insert_video_row(video_data: dict, video_id: str, table: DataTable):
    """
    extrai e formata as informações de vídeo passadas pra função  
    e no fim dela, adiciona um row na tabela alvo
    """

    title = video_data.get('title')
    upload_date = video_data.get('upload_date')
    uploader = video_data.get('uploader')
    view_count = video_data.get('view_count')
    duration = video_data.get('duration', 0) # valor em segundos. o 0 é um fallback caso esse campo não esteja presente

    # formtações
    upload_date = helpers.format_upload_date(upload_date)
    view_count = helpers.format_view_count(view_count)
    duration = helpers.format_duration(duration)

    # adicionar o row a tabela
    # não precisa de return pq a instância já é passada como argumento
    # a key é a key_row, usada pra identificar esse row, nesse caso, o id do vídeo
    table.add_row(' ', title, uploader, duration, view_count, upload_date, key=video_id)

def build_input(label_contents: str, placeholder_contents: str | None = None):
        """
        wrapper que retorna um container que contém um label + um input  
        o input field é retornado separadamente para que ele pode ser definido como variável global da classe
          
        o uso dessa função deve ser:  
        nome_container, self.nome_input = build_input(...)  
          
        dessa forma, pode ser aplicado como:  
        yield nome_container  
          
        e o nome_input agora é uma variável global acessível com self.nome_input
        """

        # adicionar dois pontos no final do label
        if not label_contents.strip().endswith(':'):
            label_contents += ':'

        # criar o label
        input_label = Label(label_contents).add_class('input-label')
        input_field = Input()
        
        # adicionar o placeholder no input caso tenha sido passado pra função
        if placeholder_contents:
            input_field.placeholder = placeholder_contents

        # adicionar os widgets finais ao container horizontal
        # isso é o equivalente de with Horziontal(): yield Widget()
        # mas em vez de só criar os widgets dentro, insere eles com _add_child()
        container = Horizontal().add_class('input-container')
        container._add_child(input_label)
        container._add_child(input_field)

        return container, input_field

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
        ('s', 'set', 'Current as destination'),
        ('p', 'pick', 'Toggle picking'),
        ('i', 'insert', 'Insert video'),
        ('u', 'url', 'Copy selected URL'),
        ('c', 'clear', 'Clear inputs')
    ]
    CSS_PATH = "style.tcss"

    def __init__(self, playlist_file: Path, video_cache_file: Path, ytdl_options: dict, master_directory: Path, **kwargs):
        """
        @param playlist_file:  
            primeira playlist a ser carregada  
            quando mudanças ocorrem, como carregar outra playlist, a variável self.playlist_file deve ser atualizada  
            ela é o método de obter qual é playlist atualmente sendo vista  
          
        @param video_cache_file:  
            arquivo contendo o cache dos vídeos  
          
        @param ytdl_options:  
            opções pra api do ytdl  
          
        @param master_directory:  
            diretório que vai ser exibido como raíz da file tree  
            não afeta diretamente o funcionamento da visualização da playlist
        """

        super().__init__(**kwargs) # herdar o comportamento da classe padrão

        self.playlist_file = playlist_file
        self.video_cache_file = video_cache_file
        self.master_directory = master_directory
        self.ytdl_options = ytdl_options

        self.selected_row_keys = [] # lista de rows selecionados da tabela
        self.picking_state = False # indica se o usuário está ou não em estado de seleção de um destino

    def set_title(self):
        """
        define o título que aparece no header, geralmente contendo o caminho da playlist atual
        """

        # relativo ao master directory (no caso, relativo ao pai dele pra ele poder aparecer)
        # ex: master/creators/playlist-atual.json
        try:
            self.title = str(self.playlist_file.relative_to(self.master_directory.parent))
        except ValueError:
            # fallback caso a playlist não esteja em nenhum lugar do master directory
            self.title = self.playlist_file

    def get_video_title(self, video_id) -> str | None:
        # obtém o título do vídeo
        # útil pra notificações ou logging. o id puro não é intuitivo pra leitura humana
        data = cache.get_cached_video_info(video_id=video_id, cache_file=self.video_cache_file)
        title = data.get('title', None)

        return title

    def load_playlist_table(self, table: DataTable, playlist_file: Path):
        # adiciona na tabela os rows dos vídeos da playlist
        # obtendo as informações dos vídeos pelos ids presentes nas entries da playlist

        # limpar a tabela antes de carregar
        table.clear(True)

        # adicionar as colunas
        table.add_column( # pra verificar o estado de seleção dos rows
            ' ',
            key='selection-status',
        )

        table.add_columns( # colunas gerais
            'Title',
            'Uploader',
            'Duration',
            'View count',
            'Upload date'
        )

        # adicionar os vídeos, lendo a playlist e obtendo os dados pelo cache
        data = helpers.json_read_playlist(playlist_file)

        for e in data.get('entries'):
            video_id = e.get('id')
            info = cache.get_cached_video_info(video_id=video_id, cache_file=self.video_cache_file)

            insert_video_row(
                video_data=info,
                video_id=video_id, # pra seleção posterior dos rows
                table=table
            )

    def compose(self) -> ComposeResult:
        # cria e adiciona os widgets iniciais ao app
        
        self.header = Header()
        self.header.icon = ''
        yield self.header

        with Horizontal():
            # abrir a file tree no diretório principal
            self.file_tree = DirectoryTree(str(self.master_directory))
            self.file_tree.ICON_FILE = ''
            self.file_tree.ICON_NODE = '󰉋 ' #󰉖 nf-md-x
            self.file_tree.ICON_NODE_EXPANDED = '󰝰 ' #󰷏
            yield self.file_tree

            # conteúdo principal
            with Vertical():
                # inputs
                with Vertical():
                    # url de um novo vídeo a ser adicionado a playlist
                    insert_container, self.video_input = build_input(
                        label_contents='Insert video',
                        placeholder_contents='https://www.youtube.com/watch?v=erb4n8PW2qw'
                    )
                    yield insert_container

                    # destino pra onde os vídeos devem ir ao clicar em 'move'
                    destination_container, self.destination_input = build_input(
                        label_contents='Moving destination',
                        placeholder_contents='~/playlists/destination.json'
                    )
                    yield destination_container
                
                # tabela da playlist
                self.table = DataTable(cursor_type='row')
                self.table.focus() # foca na tabela quando entra na tela, e não nos inputs
                yield self.table

        self.footer = Footer()
        self.footer.show_command_palette = False
        yield self.footer

    def on_mount(self):
        # depois do app inicializar, quando estiver seguro fazer alterações
        self.load_playlist_table(table=self.table, playlist_file=self.playlist_file)

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

        if not helpers.is_playlist_valid(selected_file):
            self.notify(message='Not a valid playlist', severity='warning')
            return

        # tomar a seleção como moving destination caso o estado de picking esteja ativo
        if self.picking_state:
            self.destination_input.value = str(selected_file)
            return

        # selecionar normalmente caso nenhum estado especial esteja ativo
        self.playlist_file = selected_file
        self.selected_row_keys = []
        self.load_playlist_table(table=self.table, playlist_file=selected_file)

    def on_key(self, event):
        # limpar os quaisquer erros/avisos/sucessos visuais ao clicar em qualquer tecla
        self.destination_input.remove_class('input-warning')
        self.destination_input.remove_class('input-error')

        if event.key == 'm':
            """
            mover os vídeos selecionados pro endereço definido ao pressionar a tecla
            """

            destination = Path(self.destination_input.value)

            # se a playlist de destino for a mesma que a playlist atual
            if destination == self.playlist_file:
                self.notify(message='Destination is the same as the current playlist', severity='information')
                return

            # se a playlist de destino for válida
            if not helpers.is_playlist_valid(destination, superficial_validation=True):
                self.destination_input.add_class('input-error')
                self.notify(message='Destination playlist is not valid', severity='error')
                return

            # se a quantidade de vídeos selecionados seja válida, maior que 0
            if not len(self.selected_row_keys) > 0:
                self.destination_input.add_class('input-warning')
                self.notify(message='No videos selected', severity='warning')
                return

            # mover cada vídeo pra playlist de destino
            # a variável de contagem serve pra logging/notificações
            # o título do vídeo só é obtido em caso de erro pra evitar i/o
            moved_count = 0
            
            for row_key in self.selected_row_keys:
                # moção real do vídeo
                video_id = row_key.value # o id tá dentro da row_key, ele não é a row_key em si

                try:
                    manager.move_video(
                        origin_playlist=self.playlist_file,
                        destination_playlist=destination,
                        video_id=video_id,
                        ensure_destination=True
                    )

                    self.selected_row_keys.remove(row_key) # remove da lista de selecionados
                    self.table.remove_row(row_key) # remove da tabela visual

                    moved_count += 1
                except manager.InvalidPlaylist as err:
                    # essa chamada não falha por falta da playlist de destino (a flag de criação foi passada como true)
                    # então o problema só pode ser com a playlist de origem
                    self.notify(message=f'Something is wrong with the origin playlist: {err}', severity='error')
                except manager.EntryAlreadyExists:
                    title = self.get_video_title(video_id)
                    self.notify(message=f'Destination playlist already contains {title} ({video_id})', severity='information')
                except manager.EntryNotFound:
                    title = self.get_video_title(video_id)
                    self.notify(message=f'Could not find {title} ({video_id}) in the origin playlist', severity='error')

            if moved_count > 0:
                # usar plural se for mais de um vídeo e singular se for só um
                handle_plural = 'video' if moved_count == 1 else 'videos'

                self.notify(message=f'Sucessfully moved {moved_count} {handle_plural}')

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
                title = self.get_video_title(video_id)
                self.notify(message=f'Removed {title}', severity='information')

                # remoção real do vídeo
                manager.remove_video(
                    playlist_file=self.playlist_file,
                    video_id=video_id
                )
        
        if event.key == 's':
            """
            define a playlist atual como o destino de movimento dos vídeos  
            usada pra não precisar digitar o endereço do destino manualmente
            """

            self.destination_input.value = str(self.playlist_file)
            self.notify(message='Moving destination updated', severity='information')
        
        if event.key == 'i':
            """
            adiciona um novo vídeo à playlist
            """

            video_url = self.video_input.value
            if video_url.strip() == '':
                self.notify(message='No video URL provided', severity='warning')
                return

            video_id = helpers.extract_youtube_video_id(video_url, self.ytdl_options)
            if not video_id:
                self.notify(message=f'Could not extract video ID from {video_url}', severity='error')
                return

            # obtém os dados do vídeo
            # feito aqui mesmo pq é mais barato do que recarregar a tabela inteira
            # assim, o row individual pode ser adicionado em tempo de execução
            # e as notificações também podem usar o título do vídeo sem custos adicionais
            video_data = cache.get_cached_video_info(video_id, self.video_cache_file)
            if not video_data:
                self.notify(message='Something went wrong while extracting the video data', severity='error')
                return
            
            title = video_data.get('title', None)
            
            # inserir o vídeo na playlist atual
            # e também atualizar na tabela
            try:
                manager.insert_video(
                    playlist_file=self.playlist_file,
                    video_id=video_id,
                    ensure_playlist=True
                )


                insert_video_row(
                    video_data=video_data,
                    video_id=video_id,
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
            self.destination_input.value = ''
        
        if event.key == 'u':
            """
            copia a url do primeiro vídeo selecionado da lista pra área de transferência do sistema
            """

            # primeiro verifica se o sistema possui suporte à clipboard
            # obtém o nome do sistema e verifica o software que ele usa pra esse tipo de ação
            # no linux pode variar, mas no windows e macos geralmente são sempre os mesmos
            system = platform.system().lower()

            if system == 'linux':
                if (shutil.which('xclip') is not None or
                    shutil.which('xsel') is not None or
                    shutil.which('wl-copy') is not None):
                    pass
                else:
                    self.notify(
                        message=f"""Could not find clipboard support on system {system}. Expected xclip, xsel or wl-copy\n
                        If you're using Wayland, install wl-clipboard. If you're using X11, install xclip or xsel""",
                        severity='error'
                    )
                    return
            elif system == 'windows':
                if shutil.which('clip') is None:
                    self.notify(
                        message=f'Could not find clipboard support on system {system}. Expected clip',
                        severity='error'
                    )
                    return
            elif system == 'darwin': # macos
                if shutil.which('pbcopy') is None:
                    self.notify(
                        message=f'Could not find clipboard support on system {system}. Expected pbcopy',
                        severity='error'
                    )
                    return
            else:
                self.notify(message='Unknown operational system', severity='error')
                return

            if not len(self.selected_row_keys) > 0:
                self.notify(message='No videos selected', severity='warning')
                return

            video_id = self.selected_row_keys[0].value
            if not video_id:
                self.notify(message='Could not identify the first video of the selected list', severity='error')
                return

            video_url = helpers.build_youtube_url(video_id)
            if not video_url:
                self.notify(message=f'Could not build URL from the ID {video_id}')
                return
            
            try:
                pyperclip.copy(video_url)
                self.notify(message=f'URL copied {video_url}', severity='information')
            except Exception as err:
                self.notify(message=f'Something went wrong while copying the URL: {err}', severity='error')
        
        if event.key == 'p':
            """
            toggle do estado de picking  
            não possui lógica interna porque a file tree é a responsável por isso
            """

            self.picking_state = not self.picking_state

            if self.picking_state:
                self.title = 'Picking mode activated'
                self.header.add_class('picking-mode-indicator') # tem alterações no css especificas pra essa classe
            else:
                self.set_title() # reseta o título pro normal
                self.header.remove_class('picking-mode-indicator')

def main(playlist_file: Path, master_directory: Path, video_cache_file: Path, ytdl_options: dict):
    if not helpers.is_playlist_valid(playlist_file):
        return

    if not master_directory.is_dir():
        return

    app = PlaylistView(
        playlist_file=playlist_file,
        master_directory=master_directory,
        video_cache_file=video_cache_file,
        ytdl_options=ytdl_options
    )
    app.run()