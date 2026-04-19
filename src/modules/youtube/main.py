from PyQt6.QtWidgets import QListWidgetItem, QTableWidgetItem, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from .models import Video
from .api import extract_video_info, instance_ytdl
from .resolver import build_youtube_url, resolve_get_video
from ...managers.models import Entry, Vault


class Module:
    def __init__(self, vault: Vault):
        self.vault = vault
        self.ytdl = instance_ytdl()


def build_video_entry(entry: Entry):
    ytdl = instance_ytdl()
    
    video_info = resolve_get_video()
    if not video_info:
        return
    
    video = Video.from_dict(video_info)
    if not video:
        return

    layout = QHBoxLayout()
    widget = QWidget()
    widget.setLayout(layout)
    
    labels = [
        QLabel(video.title),
        QLabel(video.uploader),
        QLabel(video.view_count_formatted),
        QLabel(video.upload_date_formatted)
    ]
    for l in labels:
        layout.addWidget(l)

    item = QListWidgetItem()
    item.setData(Qt.ItemDataRole.UserRole, entry.id)

    # definir altura mínima pra não ficar invisível
    widget.setMinimumHeight(40)
    item.setSizeHint(widget.sizeHint())
    
    print('carregado')
    
    return item, widget