from dataclasses import dataclass

from . import utils


@dataclass
class Video:
    id: str
    title: str
    description: str
    uploader: str
    view_count: int
    duration: int
    upload_date: str

    @property
    def view_count_formatted(self):
        return utils.format_view_count(self.view_count)

    @property
    def duration_formatted(self):
        return utils.format_duration(self.duration)
    
    @property
    def upload_date_formatted(self):
        return utils.format_upload_date(self.upload_date)
    
    @staticmethod
    def normalize_ytdl_data(data: dict):
        return {
            'id': data.get('id'),
            'title': data.get('title'),
            'description': data.get('description'),
            'uploader': data.get('uploader'),
            'view-count': data.get('view_count'),
            'duration': data.get('duration'),
            'upload-date': data.get('upload_date')
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description'),
            uploader=data.get('uploader'),
            view_count=data.get('view_count'),
            duration=data.get('duration'),
            upload_date=data.get('upload_date')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'uploader': self.uploader,
            'view-count': self.view_count,
            'duration': self.duration,
            'upload-date': self.upload_date
        }