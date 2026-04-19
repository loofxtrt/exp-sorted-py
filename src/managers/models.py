from dataclasses import dataclass
from pathlib import Path

from ..utils.generic import ensure_directory, normalize_json_file
from ..utils import json_io
from .cache import VaultCache


class Vault:
    def __init__(self, root: Path):
        """
        define e cria o diretório oculto do vault

        root: /path/do/vault
        context: /path/do/vault/.sorted
        """

        self.root = root
        ensure_directory(self.root)

        self.context = self.root / '.sorted'
        ensure_directory(self.context)

        self.cache = VaultCache(self.context)
    
    @property
    def modules_dir(self):
        path = self.context / 'modules'
        ensure_directory(path)

        return path
    
    # TODO: separar um cache pra cada plugin pra n precisar de um dir extra de cache
    @property
    def cache_dir(self):
        path = self.context / 'cache'
        ensure_directory(path)
        
        return path
    
    @property
    def cache_file(self):
        return self.context / normalize_json_file('cache')


@dataclass
class Entry:
    id: str
    created_at: str
    module: str
    type: str
    reference: str


@dataclass
class Collection:
    id: str
    version: str
    created_at: str
    entries: list[Entry]
    # file: Path

    @property
    def name(self):
        return 'lorem ipsum'
        # return self.file.stem

    @property
    def entry_count(self):
        return len(self.entries)

    @classmethod
    def from_dict(cls, data: dict):
        entries = []
        for v in data.get('entries', {}).values():
            entries.append(
                Entry(
                    id=v.get('id'),
                    created_at=v.get('created_at'),
                    module=v.get('module'),
                    type=v.get('type'),
                    reference=v.get('reference')
                )
            )

        return cls(
                id=data.get('id'),
                version=v.get('version'),
                created_at=data.get('created_at'),
                entries=entries
            )
    
    @classmethod
    def from_file(cls, file: Path):
        data = json_io.read_json(file)
        return cls.from_dict(data)


class Module:
    def __init__(self, id: str, vault: Vault):
        self.id = id
        self.vault = vault

        self.root = self.vault.modules_dir / id
        ensure_directory(self.root)
        
        self.manifest_file = self.root / normalize_json_file('manifest')
        self.manifest_data = self.load_manifest()
    
    def load_manifest(self):
        if not self.manifest_file.is_file():
            return {}
    
        return json_io.read_json(self.manifest_file)