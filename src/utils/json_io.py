from pathlib import Path
import json

from .. import logger

def read_json(file: Path) -> dict:
    if not file.is_file():
        return {}

    try:
        with file.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        logger.info(f'{file} provavelmente estava vazio. um objeto vazio foi criado')
        return {}
    except Exception as err:
        logger.error(f'{file} erro ao ler o arquivo. um objeto vazio foi criado')
        return {}

def write_json(file: Path, data: dict):
    try:
        with file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as err:
        logger.error(f'{file} erro ao escrever o arquivo')