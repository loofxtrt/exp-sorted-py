# ESSA VERSÃO TINHA SUPORTE MÍNIMO AO AVATAR DO UPLOADER, MAS GERALMENTE SEMPRE VINHA COMO NULL

import helpers
import cache
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

def build_video_widget(uploader: str, title: str, view_count: int, upload_date: str, description: str = None) -> QWidget:
    thumb_width = int(1280 / 6)
    thumb_height = int(thumb_width * 9 / 16) # mantém a proporção/aspect ratio 16:9
    uploader_size = 24

    # label e pixmap (imagem) da thumbnail do vídeo
    pixmap_thumbnail = QPixmap('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/placeholders/thumbnail.jpg')
    pixmap_thumbnail = pixmap_thumbnail.scaled(thumb_width, thumb_height) # redimensionar a thumbnail
    label_thumbnail = QLabel()
    label_thumbnail.setPixmap(pixmap_thumbnail)

    # labels de informações textuais e metadados sobre o vídeo
    label_uploader_name = QLabel(uploader)
    label_title = QLabel(title)
    label_views = QLabel(f'{str(view_count)} views')
    label_upload_date = QLabel(upload_date)
    label_description = QLabel(description)
    
    # configurações adicionais desses labels
    label_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
    
    # pixmap (imagem) do uploader (canal que postou o vídeo)
    pixmap_uploader = QPixmap('/mnt/seagate/workspace/coding/experimental/exp-sorted-py/placeholders/profile-picture.jpg')
    pixmap_uploader = pixmap_uploader.scaled(uploader_size, uploader_size)
    label_uploader_picture = QLabel()
    label_uploader_picture.setPixmap(pixmap_uploader)

    # criação da grid e organização desses elementos
    # grid info por si só não é um widget, então ele precisa de um container pra se comportar como um
    # ordem de posicionamento: (linha, coluna)
    grid_info = QGridLayout()
    grid_info.addWidget(label_title, 0, 0)
    grid_info.addWidget(label_uploader_picture, 2, 0)
    grid_info.addWidget(label_uploader_name, 2, 1)
    grid_info.addWidget(label_views, 1, 0)
    grid_info.addWidget(label_upload_date, 1, 1)
    if description is not None: grid_info.addWidget(label_description, 3, 0) # desc só é adicionada se for passada pra func
    container_info = QWidget()
    container_info.setLayout(grid_info)

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
        description = video_data.get('description')
        uploader = video_data.get('uploader')
        view_count = video_data.get('view_count')
        upload_date = video_data.get('upload_date')

        container_video_entry = build_video_widget(
            title=title,
            #description=description,
            view_count=view_count,
            uploader=uploader,
            upload_date=upload_date
        )
        
        vbox_main.addWidget(container_video_entry)

    # criar um widget central, responsável por ser o parent da vbox principal anteriormente criada
    central_widget = QWidget()
    central_widget.setLayout(vbox_main)

    # criar, exibir a janela e definir o widget central
    main_window = QMainWindow()
    main_window.setCentralWidget(central_widget)
    main_window.show()

    # começar o app
    app.exec()

main(Path('./tests/vq.json'))