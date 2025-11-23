from pathlib import Path

from yt_dlp import YoutubeDL

from ...collections import manager, utils
from ....services import youtube
from .... import logger

_ENTRY_TYPE = 'video'

def insert_youtube_video(collection: Path, url: str, ytdl: YoutubeDL):
    video_id = youtube.extract_youtube_video_id(url, ytdl)
    manager.insert_entry(
        collection=collection,
        entry_id=video_id,
        entry_type=_ENTRY_TYPE,
        entry_service='youtube'
    )