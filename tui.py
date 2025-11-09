import cache
import helpers
import manager
import settings as stg
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Input, Label, Footer
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

PLAYLIST = Path('./tests/serieshim.json')

class PlaylistView(App):
    #ffc971 amarelo
    #763fc4 roxo
    #496fc0 azul
    #52c58d verde

    # blue, red, yellow mocha -> https://catppuccin.com/palette/

    # essas constantes já são aplicadas automaticamente pelo textual
    TITLE = helpers.get_playlist_title(PLAYLIST)
    BINDINGS = [
        ('^q', 'quit', 'Quit'),
        ('m', 'move', 'Move selected'),
        ('d', 'delete', 'Delete selected')
    ]
    CSS = """
    Screen {
        background: #181825;
    }

    DataTable {
        border: round #89b4fa 30%;
        height: 1fr;
    }

    DataTable, DataTable * {
        background: transparent;
    }

    DataTable > .datatable--cursor {
        /* rows selecionados */
        background: #89b4fa 10%;
        color: #89b4fa;
        text-style: none;
    }

    Header, Footer {
        background: #89b4fa 10%;
        color: #89b4fa;
    }

    Input {
        background: #89b4fa 10%;
        border: none;
        /*padding: 0 1;*/
        padding: 0;
        height: 1; /* altura mínima */
    }

    Input:focus {
        background: #89b4fa 30%;
    }

    .input-warning {
        background: #f9e2af 10%;
    }

    .input-warning:focus {
        background: #f9e2af 30%;
    }

    .input-error {
        background: #f38ba8 10%;
    }

    .input-error:focus {
        background: #f38ba8 30%;
    }

    .text-warning {
        color: #f9e2af;
    }

    .text-error {
        color: #f38ba8;
    }

    .text-success {
        color: #a6e3a1;
    }

    .input-label {
        /*background: #89b4fa;
        color: #181825;*/

        background: #89b4fa 10%;
        color: #89b4fa;
        /*color: white;*/

        /*text-align: center;*/
        text-style: bold;

        padding: 0 1;
        /*width: 24;*/
    }

    .input-container {
        /*margin-bottom: 1;*/
        height: 1; /* faz os inputs não ficarem afastados quando um em cima do outro */
    }
    """

    def build_input(self, label_contents: str, placeholder_contents: str | None = None):
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

    def compose(self) -> ComposeResult:
        # cria e adiciona os widgets iniciais ao app
        self.header = Header()
        self.header.icon = ''
        yield self.header

        with Vertical(): # conteúdo principal
            self.status_label = Label() # status, erros, avisos etc.
            yield self.status_label

            with Vertical(): # inputs
                # # url de um novo vídeo a ser adicionado a playlist
                # insert_container, self.video_input = self.build_input(
                #     label_contents='Insert video',
                #     placeholder_contents='https://www.youtube.com/watch?v=erb4n8PW2qw'
                # )
                # yield insert_container

                # destino pra onde os vídeos devem ir ao clicar em 'move'
                destination_container, self.destination_input = self.build_input(
                    label_contents='Moving destination',
                    placeholder_contents='~/playlists/destination.json'
                )
                yield destination_container

                # self.search_entry = Input()
                # self.search_entry.placeholder = 'Search a video inside this playlist...'
                # yield self.search_entry
            
            self.table = DataTable(cursor_type='row')
            self.table.focus() # foca na tabela quando entra na tela, e não nos inputs
            yield self.table

        self.footer = Footer()
        self.footer.show_command_palette = False
        yield self.footer

    def on_mount(self):
        # depois do app inicializar, quando estiver seguro fazer alterações
        # adiciona na tabela os rows dos vídeos da playlist
        # obtendo as informações dos vídeos pelos ids presentes nas entries da playlist

        # adicionar as colunas
        self.table.add_column( # pra verificar o estado de seleção dos rows
            ' ',
            key='selection-status',
        )

        self.table.add_columns( # colunas gerais
            'Title',
            'Uploader',
            'Duration',
            'View count',
            'Upload date'
        )

        # adicionar os vídeos, lendo a playlist e obtendo os dados pelo cache
        data = helpers.json_read_playlist(PLAYLIST)

        for e in data.get('entries'):
            video_id = e.get('id')
            info = cache.get_cached_video_info(video_id=video_id, cache_file=SETTINGS.video_cache_file)

            insert_video_row(
                video_data=info,
                video_id=video_id, # pra seleção posterior dos rows
                table=self.table
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

        if row_key in SELECTED_ROW_KEYS:
            SELECTED_ROW_KEYS.remove(row_key)
            toggle_selection(False)
        else:
            SELECTED_ROW_KEYS.append(row_key)
            toggle_selection(True)
    
    def on_key(self, event):
        # limpar os quaisquer erros/avisos/sucessos visuais ao clicar em qualquer tecla
        self.destination_input.remove_class('input-warning')
        self.destination_input.remove_class('input-error')
        
        self.status_label.update('') # não usa display = 'none' pra não alterar as posições
        self.status_label.remove_class('text-warning')
        self.status_label.remove_class('text-error')
        self.status_label.remove_class('text-success')

        if event.key == 'm':
            # mover os vídeos pro endereço ao pressionar a tecla, apenas se as condições forem favoráveis
            # se não forem, o input reage com alterações no estilo e o texto de status é exibido
            
            # se a playlist de destino for válida
            destination = Path(self.destination_input.value)
            if not helpers.is_playlist_valid(destination, superficial_validation=True):
                self.destination_input.add_class('input-error')
                
                self.status_label.add_class('text-error')
                self.status_label.update('Destination playlist is not valid')
                return

            # se a quantidade de vídeos selecionados seja válida, maior que 0
            if not len(SELECTED_ROW_KEYS) > 0:
                self.destination_input.add_class('input-warning')
                
                self.status_label.add_class('text-warning')
                self.status_label.update('No videos selected')
                return

            # mover cada vídeo pra playlist de destino
            for row_key in SELECTED_ROW_KEYS:
                self.table.remove_row(row_key) # remove da tabela visual
                video_id = row_key.value # o id tá dentro da row_key, ele não é a row_key em si

                # moção real do vídeo
                manager.move_video(
                    origin_playlist=PLAYLIST,
                    destination_playlist=destination,
                    video_id=video_id
                    )
        
        if event.key == 'd':
            for row_key in SELECTED_ROW_KEYS:
                # remover da tabela e obter o id do vídeo
                self.table.remove_row(row_key)
                video_id = row_key.value

                # obter o título pra mandar no status
                video_data = cache.get_cached_video_info(video_id=video_id, cache_file=SETTINGS.video_cache_file)
                video_title = video_data.get('title', None)
                self.status_label.update(f'Removed {video_title}')
                self.status_label.add_class('text-success')

                # remoção real do vídeo
                manager.remove_video(
                    playlist_file=PLAYLIST,
                    video_id=video_id
                )

SETTINGS = stg.Settings()
SELECTED_ROW_KEYS = []
PlaylistView().run()