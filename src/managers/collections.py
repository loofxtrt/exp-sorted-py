from utils import json_io
from pathlib import Path
import json

def read_file(file: Path) -> dict:
    with file.open('r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def get_type_from_file(file: Path) -> str:
    data = read_collection_file(file)
    _type = get_collection_type_from_data(data)
    return _type

def get_type_from_data(data: dict) -> str:
    _type = data.get('type')
    return _type

def get_file_from_id(collection_id: str, base_directory: Path) -> None | Path:
    if not base_directory.is_dir():
        return
    
    for coll in base_directory.rglob('*.json'):
        try:
            data = read_file(coll)
        except Exception:
            continue
        
        if data.get('id') == collection_id:
            return coll
    
    return None

def get_title(file: Path) -> str:
    return file.stem

def get_entry_count(data: Path) -> int:
    return len(data.get('entries', []))