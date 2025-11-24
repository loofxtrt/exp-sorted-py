from pathlib import Path
import json

from .. import logger
from ..utils import generic

SETTINGS_DIRECTORY = Path.home() / '.config' / 'sorted' # INALTERÁVEL
SETTINGS_FILE = SETTINGS_DIRECTORY / 'settings.json' # INALTERÁVEL

# IMPORTANTE
# nas configurações e em jsons no geral, se usa kebab-case, não snake_case
# isso só não se aplica a algumas configs do ytdl, que precisam usar underline em vez de hífen
DEFAULTS = {
    'cache-directory': str(SETTINGS_DIRECTORY / 'cache'),
    'ytdl-options': {
        'quiet': True,
        'skip_download': True,
    }
}

_data = None

def _load():
    """
    carrega as configurações existentes ou cria as padrões caso ainda não existam
    essa função geralmente é usada só uma vez e só em um lugar, no momento de inicialização do software
    """

    global _data

    if _data is None:
        if SETTINGS_FILE.exists() and SETTINGS_FILE.is_file():
            # se o arquivo já existir, só carregar as configurações dele
            with SETTINGS_FILE.open('r', encoding='utf-8') as f:
                _data = json.load(f)
        else:
            # se não existir, criar um com as configurações padrões
            _data = DEFAULTS

            with SETTINGS_FILE.open('w', encoding='utf-8') as f:
                json.dump(_data, f, indent=4, ensure_ascii=False)

def get_cache_file(service: str, section: str, ensure_creation: bool = True) -> Path | None:
    """
    args:
        service:
            ex: youtube
        
        section:
            ex: videos
    """
    
    c_dir = get('cache-directory')
    if not c_dir:
        logger.error(f'erro ao obter o diretório de cache: {c_dir}')
        return

    c_dir = Path(c_dir)

    file = c_dir / service / section
    file = generic.normalize_json_file(file)
    
    if not file.exists():
        if not ensure_creation:
            logger.error(f'a seção {section} é inválida para o cache de {service}')
            logger.error(f'o arquivo de cache não existe: {file}')
            return
        else:
            # criar o arquivo se assim especificado
            file.parent.mkdir(exist_ok=True, parents=True)
            file.touch()
            
            logger.success(f'arquivo de cache criado: {file}')

    return file

def get(key: str):
    global _data

    # carregar as configurações se isso ainda não foi feito
    if _data is None:
        _load()

    # obter o valor correspondente a chave passada pra essa função
    result = _data.get(key)

    if result is None:
        logger.error(f'erro ao carregar a configuração {key}, usando o valor default como fallback')
        result = DEFAULTS.get(key)

    return result