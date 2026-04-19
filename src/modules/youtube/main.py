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
        """
        inicializa o módulo do youtube e prepara o downloader

        args:
            vault:
                instância do vault onde o cache e dados vão ficar salvos
        """

        super().__init__(id='youtube', vault=vault)

        self.ytdl = instance_ytdl()

    def get_video(self, video_id: str):
        """
        busca os dados de um vídeo
        tenta primeiro o cache local, se não tiver, baixa da api e salva no cache

        args:
            video_id:
                id do vídeo no youtube

        returns:
            dados do vídeo ou None se falhar
        """

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
        """
        busca a thumbnail de um vídeo
        tenta primeiro o cache local, se não tiver, baixa

        args:
            video_data:
                dados do vídeo contendo id e url da thumbnail

        returns:
            path da thumbnail ou None se falhar
        """
        
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
        """
        cria um widget de interface pra representar uma entry de vídeo

        esse método monta o layout com thumbnail + infos do vídeo
        e retorna tanto o item da lista quanto o widget visual

        args:
            entry:
                entrada do vault que aponta pra um vídeo do youtube

        returns:
            tupla (item, widget) usada na ui
        """
        
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