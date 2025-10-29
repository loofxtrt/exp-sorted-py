# VERSÃO INICIAL

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QHBoxLayout, QGridLayout, QWidget

def build_video_widget() -> QWidget:
    # label da thumbnail do vídeo
    label_thumbnail = QLabel('thumbnail')

    # labels de informações textuais e metadados sobre o vídeo
    label_uploader = QLabel('Uploader')
    label_title = QLabel('Title')
    label_views = QLabel('Views')
    label_description = QLabel('Description')
    
    # criação da grid e organização desses elementos
    # grid info por si só não é um widget, então ele precisa de um container pra se comportar como um
    grid_info = QGridLayout()
    grid_info.addWidget(label_title, 0, 0)
    grid_info.addWidget(label_uploader, 1, 0)
    grid_info.addWidget(label_views, 1, 1)
    grid_info.addWidget(label_description, 2, 0)
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

def main():
    app = QApplication([])

    container_video_entry = build_video_widget()

    # vbox que é responsável por ordenar verticalmente todas as entradas de vídeo como em uma lista
    vbox_main = QVBoxLayout()
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

main()