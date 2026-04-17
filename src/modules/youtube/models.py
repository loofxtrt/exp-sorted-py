from dataclasses import dataclass

import formatting


@dataclass
class Video:
    title: str
    description: str
    uploader: str
    view_count: int
    duration: int
    upload_date: str

    def __post_init__(self):
        self.view_count = formatting.format_view_count(self.view_count)
        self.duration = formatting.format_duration(self.duration)
        self.upload_date = formatting.format_upload_date(self.upload_date)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data.get('title'),
            description=data.get('description'),
            uploader=data.get('uploader'),
            view_count=data.get('view_count'),
            duration=data.get('duration'),
            upload_date=data.get('upload_date')
        )
    
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'uploader': self.uploader,
            'view-count': self.view_count,
            'duration': self.duration,
            'upload-date': self.upload_date
        }