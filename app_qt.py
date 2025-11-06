import helpers
import cache
import requests
import settings as stg
import logger
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from colorthief import ColorThief

class VideoWidget:
    def __init__(self, video_data: dict, fallback_thumbnail: str):
        self.video_data = video_data
        self.fallback_thumbnail = fallback_thumbnail

    def build_video_widget(self):
        widget_thumbnail = self.handle_thumbnail(thumbnail_url=self.video_data.get('thumbnail'))
        widget_info = self.handle_video_info(video_data=self.video_data)

        # cria o layout interno que uma representação de um vídeo tem
        # hbox é usado pra que a thumbnail fique de um lado e os metadados do outro
        hbox_video_entry = QHBoxLayout()
        hbox_video_entry.addWidget(widget_thumbnail)
        hbox_video_entry.addWidget(widget_info, alignment=Qt.AlignmentFlag.AlignLeft)
        hbox_video_entry.addStretch() # faz as infos ficarem coladas à esquerda com a thumbnail
        
        # como a entrada de vídeo é um layout e não um widget, ela precisa de um container
        # pra poder ser adicionada em outro layout
        container_video_entry = QWidget()
        container_video_entry.setLayout(hbox_video_entry)

        return container_video_entry

    def handle_thumbnail(self, thumbnail_url: str):
        # label e pixmap (imagem) da thumbnail do vídeo
        pixmap_thumbnail = thumbnail_as_pixmap(thumbnail_url, self.fallback_thumbnail)
        
        # redimensionar a thumbnail
        thumb_width = int(1280 / 7)
        pixmap_thumbnail = resize_pixmap_16_9(thumb_width, pixmap_thumbnail)

        # criar o qlabel e aplicar o pixmap
        label_thumbnail = QLabel()
        label_thumbnail.setPixmap(pixmap_thumbnail)

        return label_thumbnail
    
    def handle_video_info(self, video_data: dict):
        title = video_data.get('title')
        uploader = video_data.get('uploader')
        view_count = video_data.get('view_count')
        upload_date = video_data.get('upload_date')
        duration = video_data.get('duration')

        # formatar os metadados numéricos
        upload_date = helpers.format_upload_date(upload_date)
        duration = helpers.format_duration(seconds=duration)
        view_count = helpers.format_view_count(view_count)

        # labels de informações textuais e metadados sobre o vídeo
        label_uploader_name = QLabel(uploader)
        label_title = QLabel(title)
        label_views_uploaddate_duration = QLabel(f'{view_count} views • {upload_date} • {duration}')

        # configurações adicionais desses labels
        label_title.setStyleSheet('font-weight: bold')
        label_uploader_name.setProperty('class', 'faint')
        label_views_uploaddate_duration.setProperty('class', 'faint')

        # criação da vbox e organização desses elementos
        # a vbox por si só não é um widget, então ela precisa de um container pra se comportar como um
        vbox_info = QVBoxLayout()
        vbox_info.addWidget(label_title)
        vbox_info.addWidget(label_views_uploaddate_duration)
        vbox_info.addWidget(label_uploader_name)
        container_info = QWidget()
        container_info.setLayout(vbox_info)

        return container_info

def resize_pixmap_16_9(width: int, pixmap: QPixmap) -> QPixmap:
    """
    redimensiona um pixmap mantendo a proporção 16:9 (padrão de thumbnails do youtube)  
    se baseia na largura, fazendo a altura se ajustar a ela
    """
    height = int(width * 9 / 16) # mantém a proporção/aspect ratio 16:9
    pixmap = pixmap.scaled(width, height)
    
    return pixmap

def thumbnail_as_pixmap(thumbnail_url: str, fallback_thumbnail: str, skip_download: bool = True) -> QPixmap:
    """
    faz o download na memória da imagem fornecida a essa função  
    depois, a retorna como um pixmap que pode ser aplicado em labels pra exibir a imagem
    """
    pixmap_thumbnail = None

    if not skip_download:
        # primeiro faz um request pra baixar imagem da thumbnail na memória
        # se o códio de resposta for 200, significa que o download foi bem sucedido
        # se não conseguir baixar, usa uma imagem de fallback no lugar
        try:
            response = requests.get(thumbnail_url)
            response.raise_for_status() # lançar um erro caso o código de resposta não seja 200

            pixmap_thumbnail = QPixmap()
            pixmap_thumbnail.loadFromData(response.content)
        except requests.exceptions.RequestException as err:
            logger.error(f'erro ao tentar baixar uma thumbnail, usando fallback: {err}')

    # usar o fallback se o resto da função não conseguiu sobreescrever o none inicial
    if pixmap_thumbnail is None:
        pixmap_thumbnail = QPixmap(fallback_thumbnail)
    
    return pixmap_thumbnail

def build_playlist_list(playlist_data: dict, cache_file: Path, fallback_thumbnail: str):
    # vbox que é responsável por ordenar verticalmente todas as entradas de vídeo em um formato de lista
    # precisa de um container pra depois poder se adicionada a tela como widget em vez de layout puro
    pl_vbox = QVBoxLayout()
    pl_widget = QWidget()
    pl_widget.setLayout(pl_vbox)

    # nessa vbox, adicionar as entradas de vídeos
    for e in playlist_data.get('entries'):
        video_id = e.get('id')
        video_data = cache.get_cached_video_info(video_id, cache_file)

        video_widget = VideoWidget(video_data, fallback_thumbnail)
        pl_vbox.addWidget(video_widget.build_video_widget())
    
    return pl_widget

def build_sidebar(playlist_file: Path, fallback_thumbnail: str, cache_file: Path, playlist_data: dict | None = None):
    # barra lateral com informações da playlist sendo atualmente visualizada
    # segue a mesma lógica da vbox dos vídeo, por isso precisa de um container
    sidebar_vbox = QVBoxLayout()

    # se não tiver passado as infos da playlist já abertas, lê elas agora
    if playlist_data is None:
        helpers.json_read_playlist(playlist_file)
    
    # definir a thumbnail da playlist sendo a mesma que a thumbnail do primeiro vídeo da lista
    entries = playlist_data.get('entries')
    first_entry = cache.get_cached_video_info(cache_file=cache_file, video_id=entries[0].get('id'))
    first_thumbnail = first_entry.get('thumbnail')
    playlist_thumbnail = thumbnail_as_pixmap(first_thumbnail, fallback_thumbnail)

    playlist_thumbnail = resize_pixmap_16_9(int(1280 / 4), playlist_thumbnail)

    thumbnail_label = QLabel()
    thumbnail_label.setPixmap(playlist_thumbnail)
    sidebar_vbox.addWidget(thumbnail_label)

    # título da playlist
    title_label = QLabel(helpers.get_playlist_title(playlist_file))
    sidebar_vbox.addWidget(title_label)

    # data de criação e modificação
    modified_label = QLabel(f'Created at: {playlist_data.get('last-modified-at')}')
    sidebar_vbox.addWidget(modified_label)

    creation_label = QLabel(f'Last modified at: {playlist_data.get('created-at')}')
    sidebar_vbox.addWidget(creation_label)

    # quantidade de vídeos
    video_count = len(entries)
    handle_plural = 'video' if video_count == 1 else 'videos'
    video_count_label = QLabel(f'Contains {video_count} {handle_plural}')
    sidebar_vbox.addWidget(video_count_label)

    # criar o container
    sidebar_widget = QWidget()
    sidebar_widget.setFixedWidth(300)
    #sidebar_widget.setStyleSheet('background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #002036, stop: 1 #003a56); border-radius: 5px;')
    sidebar_widget.setStyleSheet('background-color: #242526; border-radius: 5px;')
    sidebar_widget.setLayout(sidebar_vbox)

    return sidebar_widget

#242526 <- sidebar
#1f2021 <- bg mais claro
#181919 <- bg mais escuro
# CRÉDITOS LOGO: KORA

def set_stylesheet(app: QApplication):
    app.setStyleSheet("""
    * {
        color: white;
    }

    .faint {
        color: #aaaaaa;
    }
    
    QMainWindow {
        background-color: #181919;
    }
    """)

def main(playlist_file: Path, cache_file: Path, fallback_thumbnail: str):
    app = QApplication([])

    # criar a sidebar e a lista de vídeos
    data = helpers.json_read_playlist(playlist_file)

    playlist_widget = build_playlist_list(
        playlist_data=data,
        cache_file=cache_file,
        fallback_thumbnail=fallback_thumbnail
    )
    sidebar_widget = build_sidebar(
        playlist_file=playlist_file,
        fallback_thumbnail=fallback_thumbnail,
        playlist_data=data,
        cache_file=cache_file
    )

    # somar os dois elementos principais (sidebar e lista de vídeos) num layout só
    main_hbox = QHBoxLayout()
    main_hbox.addWidget(sidebar_widget)
    main_hbox.addWidget(playlist_widget)

    # criar um widget central, responsável por ser o parent conteúdo principal
    central_widget = QWidget()
    central_widget.setLayout(main_hbox)

    # criar, exibir a janela e definir o widget central
    main_window = QMainWindow()
    main_window.setCentralWidget(central_widget)
    main_window.show()

    # aplicar o estilo visual no app
    set_stylesheet(app)

    # começar o app
    app.exec()

settings = stg.Settings()

main(
    playlist_file=Path('./tests/vq.json'),
    cache_file=settings.video_cache_file,
    fallback_thumbnail = '/mnt/seagate/workspace/coding/experimental/exp-sorted-py/placeholders/thumbnail.jpg'
)