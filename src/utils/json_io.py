from pathlib import Path
import json

from .. import logger

def read_json(file: Path) -> dict:
    try:
        with file.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        logger.info(f'{file} provavelmente estava vazio. um novo objeto foi criado')
        return {}
    except Exception as err:
        return {}

def write_json(file: Path, data: dict):
    with file.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)