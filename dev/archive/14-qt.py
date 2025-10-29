# VERSÃO ANTES DA BARRA LATERAL DAS PLAYLISTS

import helpers
import cache
import requests
from pathlib import Path
from loguru import logger
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

def build_video_widget(video_id: str, uploader: str, title: str, view_count: int, upload_date: str, thumbnail_url: str, duration: int, description: str = None) -> QWidget:
    thumb_width = int(1280 / 7)
    thumb_height = int(thumb_width * 9 / 16) # mantém a proporção/aspect ratio 16:9

    # label e pixmap (imagem) da thumbnail do vídeo
    # primeiro faz um request pra baixar temporariamente a imagem da thumbnail
    # se o códio de resposta for 200, significa que o download foi bem sucedido
    # se não conseguir baixar, usa uma imagem de fallback no lugar
    try:
        response = requests.get(thumbnail_url)
        response.raise_for_status() # lançar um erro caso o código de resposta não seja 200

        pixmap_thumbnail = QPixmap()
        pixmap_thumbnail.loadFromData(response.content)
    except requests.exceptions.RequestException as err:
        logger.error(f'erro ao tentar baixar uma thumbnail, usando fallback: {err}')
        pixmap_thumbnail = QPixmap('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/placeholders/thumbnail.jpg')
    
    pixmap_thumbnail = pixmap_thumbnail.scaled(thumb_width, thumb_height) # redimensionar a thumbnail
    label_thumbnail = QLabel()
    label_thumbnail.setPixmap(pixmap_thumbnail)

    # labels de informações textuais e metadados sobre o vídeo
    label_uploader_name = QLabel(uploader)
    label_title = QLabel(title)
    label_description = QLabel(description)
    label_views_uploaddate_duration = QLabel(f'{view_count} views • {upload_date} • {duration}')

    # configurações adicionais desses labels
    label_title.setStyleSheet('font-weight: bold')
    label_description.setProperty('class', 'faint')
    label_uploader_name.setProperty('class', 'faint')
    label_views_uploaddate_duration.setProperty('class', 'faint')

    # criação da vbox e organização desses elementos
    # a vbox por si só não é um widget, então ela precisa de um container pra se comportar como um
    vbox_info = QVBoxLayout()
    vbox_info.addWidget(label_title)
    vbox_info.addWidget(label_views_uploaddate_duration)
    vbox_info.addWidget(label_uploader_name)
    if description is not None: vbox_info.addWidget(label_description) # desc só é adicionada se for passada pra func
    container_info = QWidget()
    container_info.setLayout(vbox_info)

    # cria o layout interno que uma representação de um vídeo tem
    # hbox é usado pra que a thumbnail fique de um lado e os metadados do outro
    hbox_video_entry = QHBoxLayout()
    hbox_video_entry.addWidget(label_thumbnail)
    hbox_video_entry.addWidget(container_info)
    
    # como a entrada de vídeo é um layout e não um widget, ela precisa de um container
    # pra poder ser adicionada em outro layout
    container_video_entry = QWidget()
    container_video_entry.setLayout(hbox_video_entry)

    return container_video_entry

def set_stylesheet(app: QApplication):
    app.setStyleSheet("""
    * {
        color: white
    }

    .faint {
        color: #aaaaaa
    }
    
    QMainWindow {
        background-color: #0f0f0f;
    }
    """)

def main(playlist_file: Path):
    app = QApplication([])

    # vbox que é responsável por ordenar verticalmente todas as entradas de vídeo como em uma lista
    vbox_main = QVBoxLayout()

    # nessa vbox, adicionar as entradas de vídeos
    data = helpers.json_read_playlist(playlist_file)
    for video in data.get('entries'):
        video_id = video.get('id')
        video_data = cache.get_video_info(video_id)

        title = video_data.get('title')
        #description = helpers.truncate_text(video_data.get('description'), 80)
        uploader = video_data.get('uploader')
        view_count = video_data.get('view_count')
        upload_date = video_data.get('upload_date')
        thumbnail = video_data.get('thumbnail')
        duration = video_data.get('duration')

        # formatar os metadados numéricos
        upload_date = helpers.format_upload_date(upload_date)
        duration = helpers.format_duration(seconds=duration)
        view_count = helpers.format_view_count(view_count)

        container_video_entry = build_video_widget(
            video_id=video_id,
            title=title,
            #description=description,
            view_count=view_count,
            uploader=uploader,
            upload_date=upload_date,
            thumbnail_url=thumbnail,
            duration=duration
        )
        
        vbox_main.addWidget(container_video_entry)

    # criar um widget central, responsável por ser o parent da vbox principal anteriormente criada
    central_widget = QWidget()
    central_widget.setLayout(vbox_main)

    # criar, exibir a janela e definir o widget central
    main_window = QMainWindow()
    main_window.setCentralWidget(central_widget)
    main_window.show()

    # aplicar o estilo visual no app
    set_stylesheet(app)

    # começar o app
    app.exec()

main(Path('./tests/vq.json'))