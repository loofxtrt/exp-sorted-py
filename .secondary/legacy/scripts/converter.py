"""
converte o formato:
{
    "created-at": "2025-11-02T22:37:50",
    "id": "WelGN9ij",
    "entries": [
        {
            "id": "8zZYyhEBgEY",
            "inserted-at": "2025-11-02T22:41:03"
        }
    ],
    "last-modified-at": "2025-11-16T12:38:06"
}

pra:
{
    "id": "WelGN9ij",
    "created-at": "2025-11-02T22:37:50",
    "type": "videos"
    "entries": [
        {
            "service-metadata": {
                "resolvable-id": "8zZYyhEBgEY",
                "service-name": "youtube",
            },
            "id": "123abc456",
            "inserted-at": "2025-11-02T22:41:03"
        }
    ],
    "last-modified-at": "2025-11-16T12:38:06"
}
"""

from pathlib import Path
import json
import string
import random

def generate_random_id(id_length: int = 8):
    # copiado das utils
    characters = string.ascii_letters + string.digits + '-' + '_'

    final_id: str = ''
    for i in range(id_length):
        final_id += random.choice(characters)

    return final_id

def convert(file: Path):
    with file.open('r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = []
    for e in data.get('entries'):
        entry_id = generate_random_id()
        resolvable_id = e.get('id')
        inserted_at = e.get('inserted-at')

        entry = {
            'service-metadata': {
                'resolvable-id': resolvable_id,
                'service-name': 'youtube'
            },
            'id': entry_id,
            'inserted-at': inserted_at
        }
        entries.append(entry)

    converted = {
        'id': data.get('id'),
        'type': 'videos',
        'entries': entries,
        'last-modified-at': data.get('last-modified-at')
    }

    directory = file.parent / 'converted'
    directory.mkdir(parents=True, exist_ok=True)

    final = directory / file.name
    with final.open('w', encoding='utf-8') as f:
        json.dump(converted, f, indent=4, ensure_ascii=False)
    
    print(str(final))

#for f in Path('/home/luan/Desktop/sorted-data/series').iterdir():
#    if f.is_file():
#        convert(f)

#convert(Path('/home/luan/Desktop/sorted-data/creators/eumerly.json'))
#convert(Path('/home/luan/Desktop/sorted-data/watch-later/creators/eumerly.json'))