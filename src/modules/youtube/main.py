from PyQt6.QtWidgets import QListWidgetItem, QTableWidgetItem, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from . import cache
from .models import Video
from .utils import build_youtube_url
from .api import extract_video_info, instance_ytdl
from ...utils.generic import ensure_directory, normalize_json_file
from ...managers.models import Entry, Vault, Module


class YouTubeModule(Module):
    def __init__(self, vault: Vault):
        super().__init__(id='youtube', vault=vault)

        self.ytdl = instance_ytdl()

    def get_video(self, video_id: str):
        cached = cache.get_video_from_cache(video_id, self.vault)
        if cached:
            return cached

        url = build_youtube_url(video_id)
        data = extract_video_info(url, self.ytdl)
        if not data:
            return
        
        data = Video.normalize_ytdl_data(data)

        cache.write_video_to_cache(data, self.vault)
        return data
    
    def get_thumbnail(self, video_data: dict):
        def search_cached_thumbnail(video_id: str):
            return cache._get_thumbnail_path(video_id, self.vault)
        
        video_id = video_data.get('id')
        
        thumb = search_cached_thumbnail(video_id)
        if thumb.is_file():
            return thumb

        cache.download_thumbnail_to_cache(video_data, self.vault)
        
        thumb = search_cached_thumbnail(video_id)
        if thumb.is_file():
            return thumb

    def build_entry_widget(self, entry: Entry):
        video_id = entry.reference

        data = self.get_video(video_id)
        if not data:
            return
        
        video = Video.from_dict(data)
        if not video:
            return

        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)

        thumb_label = QLabel()
        pixmap = QPixmap(str(self.get_thumbnail(data)))
        thumb_label.setPixmap(pixmap.scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(thumb_label)
        
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