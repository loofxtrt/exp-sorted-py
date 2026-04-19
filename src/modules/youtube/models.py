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
    like_count: int
    comment_count: int
    thumbnail: str

    @property
    def view_count_formatted(self):
        return utils.format_count(self.view_count or 0)

    @property
    def duration_formatted(self):
        return utils.format_duration(self.duration or 0)
    
    @property
    def upload_date_formatted(self):
        return utils.format_upload_date(self.upload_date or 0)

    @property
    def like_count_formatted(self):
        return utils.format_count(self.like_count or 0)
        
    @property
    def comment_count_formatted(self):
        return utils.format_count(self.comment_count or 0)
    
    @staticmethod
    def normalize_ytdl_data(data: dict):
        return {
            'id': data.get('id'),
            'title': data.get('title'),
            'description': data.get('description'),
            'uploader': data.get('uploader'),
            'view_count': data.get('view_count'),
            'duration': data.get('duration'),
            'upload_date': data.get('upload_date'),
            'like_count': data.get('like_count'),
            'comment_count': data.get('comment_count'),
            'thumbnail': data.get('thumbnail')
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
            upload_date=data.get('upload_date'),
            like_count=data.get('like_count'),
            comment_count=data.get('comment_count'),
            thumbnail=data.get('thumbnail')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'uploader': self.uploader,
            'view_count': self.view_count,
            'duration': self.duration,
            'upload_date': self.upload_date,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'thumbnail': self.thumbnail
        }