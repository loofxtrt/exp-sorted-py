import helpers
from pathlib import Path

data = helpers.get_playlist_file_by_id(directory=Path('./tests'), playlist_id='xKFHDg6h')
print(data.stem)