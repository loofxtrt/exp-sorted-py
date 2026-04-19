from pathlib import Path

from ..utils.generic import ensure_directory, normalize_json_file
from ..utils import json_io
from .. import logger

class VaultCache:
    def __init__(self, context: Path):
        self.context = context
        self.cache_file = self.context / normalize_json_file('cache')
        self.data = self.load()

    def load(self):
        return json_io.read_json(self.cache_file)

class GlobalCache:
    def __init__(self):
        self.cache_file = self.get_cache_dir() / normalize_json_file('global-cache')
        self.data = self.load()

    def load(self):
        return json_io.read_json(self.cache_file)

    @staticmethod
    def get_cache_dir() -> Path:
        cache_dir = Path.home() / '.cache' / 'sorted'
        ensure_directory(cache_dir)
    
        return cache_dir

    @property
    def last_accessed_vault(self) -> Path | None:
        raw_path = self.data.get('last_accessed_vault')
        vault = None

        if raw_path is not None:
            vault = Path(raw_path)
        else:
            return

        if not vault.is_dir():
            logger.error(f'{vault} existe, mas não é um diretório')
            return
        
        return vault
    
    def write_last_accessed_vault(self, root: Path):
        if not root.is_dir():
            logger.error(f'{root} não é um diretório')
            return
        
        self.data['last_accessed_vault'] = str(root.resolve())
        json_io.write_json(self.cache_file, self.data)