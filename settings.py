import json
import logger
import helpers
from pathlib import Path

SETTINGS_DIRECTORY = Path.home() / '.config' / 'sorted' # INALTERÁVEL
SETTINGS_FILE = SETTINGS_DIRECTORY / 'settings.json' # INALTERÁVEL

DEFAULTS = {
    'cache-directory': str(SETTINGS_DIRECTORY / 'cache'),
    'ytdl_options': {
        'quiet': True,
        'skip_download': True,
    }
}

_data = None

def _load():
    global _data

    if _data is None:
        if SETTINGS_FILE.exists() and SETTINGS_FILE.is_file():
            with SETTINGS_FILE.open('r') as f:
                _data = json.load(f)
        else:
            _data = DEFAULTS

def get_cache_file(service: str, section: str):
    c_dir = get('cache-directory')
    c_dir = Path(c_dir)

    file = c_dir / service / section
    file = helpers.normalize_json_file(file)
    
    if not file.exists():
        logger.error(f'a seção {section} é inválida para o cache de {service}')
        logger.error(f'o arquivo de cache não existe: {file}')
        return

    return file

def get(key: str):
    result = _data.get(key)

    if result is None:
        logger.error(f'erro ao carregar a configuração {key}, usando o valor default como fallback')
        result = DEFAULTS.get(key)

    return result