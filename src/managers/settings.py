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