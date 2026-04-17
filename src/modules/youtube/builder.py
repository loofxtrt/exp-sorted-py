from PyQt6.QtWidgets import QListWidgetItem, QTableWidgetItem, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from .models import Video

def build_video_entry(title: str, entry_id: str):
    layout = QHBoxLayout()
    widget = QWidget()
    widget.setLayout(layout)
    
    label_title = QLabel(title)
    layout.addWidget(label_title)

    item = QListWidgetItem()
    item.setData(Qt.ItemDataRole.UserRole, entry_id)

    # definir altura mínima pra não ficar invisível
    widget.setMinimumHeight(40)
    item.setSizeHint(widget.sizeHint())
    
    print('carregado')
    
    return item, widget
    
# def build_youtube_video_items(video: Video) -> list[QTableWidgetItem]:
#     items = []
#     for value in [
#         video.title,
#         video.uploader,
#         video.duration_formatted,
#         video.view_count_formatted,
#         video.upload_date_formatted
#     ]:
#         i = QTableWidgetItem(str(value))
#         items.append(i)
#     return items