from PyQt6.QtWidgets import QListWidgetItem, QTableWidgetItem

from models import Video

# def build_youtube_video_item(video: Video) -> QListWidgetItem | None:

def build_youtube_video_items(video: Video) -> list[QTableWidgetItem]:
    items = []
    for value in [
        video.title,
        video.uploader,
        video.duration_formatted,
        video.view_count_formatted,
        video.upload_date_formatted
    ]:
        i = QTableWidgetItem(str(value))
        items.append(i)
    return items