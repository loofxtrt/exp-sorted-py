import cache
import settings as stg
import helpers
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Input
from rich.text import Text

def insert_video_row(video_data: dict, table: DataTable):
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
    table.add_row(title, uploader, duration, view_count, upload_date)

PLAYLIST = Path('./tests/serieshim.json')

class PlaylistView(App):
    #ffc971 amarelo
    #763fc4 roxo
    #496fc0 azul
    #52c58d verde

    # blue mocha -> https://catppuccin.com/palette/

    # essas constantes já são aplicadas automaticamente pelo textual
    TITLE = helpers.get_playlist_title(PLAYLIST)
    CSS = """
    Screen {
        background: #181825;
    }

    DataTable {
        border: round #89b4fa 30%;
    }

    DataTable, DataTable * {
        background: transparent;
    }

    DataTable > .datatable--cursor {
        background: #89b4fa 10%;
        color: #89b4fa;
        text-style: none;
    }

    Header {
        background: #89b4fa 10%;
        color: #89b4fa;
    }

    Input {
        border: round #89b4fa 30%;
        background: transparent;
    }
    """

    def compose(self) -> ComposeResult:
        # cria e adiciona os widgets iniciais ao app
        self.header = Header()
        yield self.header

        self.video_input = Input()
        self.video_input.placeholder = 'https://www.youtube.com/watch?v=erb4n8PW2qw'
        yield self.video_input

        self.search_entry = Input()
        self.search_entry.placeholder = 'Search a video inside this playlist...'
        yield self.search_entry
        
        self.table = DataTable(cursor_type='row')
        yield self.table

    def on_mount(self):
        # depois do app inicializar, quando estiver seguro fazer alterações
        # adiciona na tabela os rows dos vídeos da playlist
        # obtendo as informações dos vídeos pelos ids presentes nas entries da playlist

        # colunas base
        self.table.add_columns(
            'Title',
            'Uploader',
            'Duration',
            'View count',
            'Upload date'
        )

        # adicionar os vídeos, lendo a playlist e obtendo os dados pelo cache
        data = helpers.json_read_playlist(PLAYLIST)
        settings = stg.Settings()

        for e in data.get('entries'):
            video_id = e.get('id')
            info = cache.get_cached_video_info(video_id=video_id, cache_file=settings.video_cache_file)
            insert_video_row(info, self.table)

PlaylistView().run()