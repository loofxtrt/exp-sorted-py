from pathlib import Path
import json

from .. import logger
from ..utils import generic
from ..utils.json_io import read_json, write_json

# IMPORTANTE
# nas configurações e em jsons no geral, se usa kebab-case, não snake_case
# isso só não se aplica a algumas configs do ytdl, que precisam usar underline em vez de hífen
DEFAULTS = {
    'ytdl-options': {
        'quiet': True,
        'skip_download': True,
    }
}

settings = None

class Vault:
    def __init__(self, vault: Path):
        """
        define e cria o diretório oculto do vault
        """

        self.vault = vault
        self.dot = self.vault / '.sorted'
        self.dot.mkdir(parents=True, exist_ok=True)
    
    @property
    def settings(self):
        """
        tenta ler o arquivo de configuração, e, se não existir,
        gera um novo usando as configurações padrões e retorna elas
        """

        path = self.dot / 'settings.json'
        data = read_json(path)
        
        if data:
            return data
        else:
            write_json(path, DEFAULTS)
            return DEFAULTS
    
    @property
    def cache_directory(self):
        path = self.dot / 'cache'
        path.mkdir(parents=True, exist_ok=True)
        
        return path

# def _load():
#     """
#     carrega as configurações existentes ou cria as padrões caso ainda não existam
#     essa função geralmente é usada só uma vez e só em um lugar, no momento de inicialização do software
#     """

#     global _data

#     if _data is None:
#         if SETTINGS_FILE.exists() and SETTINGS_FILE.is_file():
#             # se o arquivo já existir, só carregar as configurações dele
#             with SETTINGS_FILE.open('r', encoding='utf-8') as f:
#                 _data = json.load(f)
#         else:
#             # se não existir, criar um com as configurações padrões
#             _data = DEFAULTS

#             with SETTINGS_FILE.open('w', encoding='utf-8') as f:
#                 json.dump(_data, f, indent=4, ensure_ascii=False)

# def get(key: str):
#     global _data

#     # carregar as configurações se isso ainda não foi feito
#     if _data is None:
#         _load()

#     # obter o valor correspondente a chave passada pra essa função
#     result = _data.get(key)

#     if result is None:
#         logger.error(f'erro ao carregar a configuração {key}, usando o valor default como fallback')
#         result = DEFAULTS.get(key)

#     return result