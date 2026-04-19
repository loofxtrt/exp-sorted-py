from PyQt6.QtWidgets import QListWidgetItem, QTableWidgetItem, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from . import cache
from .models import Video
from .api import extract_video_info, instance_ytdl
# from .resolver import build_youtube_url, resolve_get_video
from .utils import build_youtube_url
from ...managers.models import Entry, Vault


class Module:
    def __init__(self, vault: Vault):
        self.vault = vault
        self.ytdl = instance_ytdl()

    def get_video(self, video_id: str):
        cached = cache.get_data_from_cache(video_id, self.vault)
        if cached:
            return cached

        url = build_youtube_url(video_id)
        data = extract_video_info(url, self.ytdl)
        if not data:
            return
        
        data = Video.normalize_ytdl_data(data)

        cache.write_data_to_cache(data, self.vault)
        return data

    def build_entry_widget(self, entry: Entry):
        data = self.get_video(video_id=entry.reference)
        if not data:
            return
        
        video = Video.from_dict(data)
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