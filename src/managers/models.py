from dataclasses import dataclass
from pathlib import Path

from ..utils.generic import ensure_directory, normalize_json_file
from ..utils import json_io
from .cache import VaultCache


class Vault:
    """
    representa um vault de trabalho e gerencia sua estrutura interna

    esta classe cria e organiza o diretório base do vault, incluindo o diretório oculto
    de contexto (.sorted), além de expor caminhos úteis como modules e cache

    args:
        root:
            diretório raiz do vault que será inicializado e garantido no sistema
    """

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
        """
        retorna o diretório de módulos do vault
        cria o diretório caso ainda não exista
        """

        path = self.context / 'modules'
        ensure_directory(path)

        return path
    
    # TODO: separar um cache pra cada plugin pra n precisar de um dir extra de cache
    @property
    def cache_dir(self):
        """
        retorna o diretório de cache do vault
        cria o diretório caso ainda não exista
        """

        path = self.context / 'cache'
        ensure_directory(path)
        
        return path
    
    @property
    def cache_file(self):
        """
        retorna o arquivo de cache principal do vault
        """
        
        return self.context / normalize_json_file('cache')


@dataclass
class Entry:
    """
    representa uma entrada individual dentro de uma collection
    """

    id: str
    created_at: str
    module: str
    type: str
    reference: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            created_at=data.get('created_at'),
            module=data.get('module'),
            type=data.get('type'),
            reference=data.get('reference')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'module': self.module,
            'type': self.type,
            'reference': self.reference
        }


@dataclass
class Collection:
    """
    representa uma collection carregada de um arquivo
    essa estrutura agrupa entries e metadados associados
    """

    id: str
    version: str
    created_at: str
    entries: list[Entry]
    file: Path

    @property
    def name(self):
        """
        retorna o nome da collection
        isso é sempre o nome do arquivo sem a extensão
        """
        
        return self.file.stem

    @property
    def entry_count(self):
        """
        retorna a quantidade de entradas na collection
        """

        return len(self.entries)

    @classmethod
    def from_dict(cls, data: dict, file: Path):
        """
        cria uma collection a partir de um dicionário

        args:
            data:
                dicionário contendo os dados da collection e suas entries
        """
        
        entries = []
        for v in data.get('entries', {}).values():
            entries.append(Entry.from_dict(v))

        return cls(
            id=data.get('id'),
            version=data.get('version'),
            created_at=data.get('created_at'),
            entries=entries,
            file=file
        )

    def to_dict(self):
        entries = []
        for e in self.entries:
            entries.append(e.to_dict())

        return {
            'id': self.id,
            'version': self.version,
            'created_at': self.created_at,
            'entries': entries
        }
    
    @classmethod
    def from_file(cls, file: Path):
        """
        carrega uma collection a partir de um arquivo
        esse arquivo deve ser um json (com extensão .json ou .scol)

        args:
            file:
                caminho do arquivo de collection
        """
        
        # TODO: validação mais rigorosa com base na chave type
        data = json_io.read_json(file)
        return cls.from_dict(data, file)
    
    def write_entry(self, entry: Entry):
        # atualiza a memória primeiro
        self.entries.append(entry)
        
        # TODO: talvez mover a conversão pra dict pra fora da func
        # pra evitar repetições em loops for/múltiplas adições
        data = self.to_dict()
        
        data[entry.id] = entry.to_dict()
        json_io.write_json(self.file, data)



class Module:
    """
    representa um plugin dentro de um vault

    um module é uma extensão isolada do sistema, usada pra adicionar
    funcionalidades específicas (tipo integrações, renderizações, processamento de dados etc)
    sem precisar mexer no core da aplicação

    cada module vive dentro do seu próprio diretório no vault, onde pode guardar arquivos,
    cache, configs e um manifesto com dados persistentes

    a ideia é permitir que funcionalidades sejam plugáveis, removíveis e independentes,
    sem quebrar o resto do sistema

    args:
        id:
            nome único do plugin dentro do vault (ex: "youtube", "notes", etc)

        vault:
            instância do Vault onde esse plugin está rodando
    """

    def __init__(self, id: str, vault: Vault):
        """
        inicializa o plugin e garante que a estrutura dele existe no disco

        cada module cria uma pasta própria dentro de vault.modules_dir pra armazenar
        dados, cache e arquivos internos
        """

        self.id = id
        self.vault = vault

        self.root = self.vault.modules_dir / id
        ensure_directory(self.root)
        
        self.manifest_file = self.root / normalize_json_file('manifest')
        self.manifest_data = self.load_manifest()
    
    def load_manifest(self):
        """
        carrega o manifesto do plugin

        o manifesto é basicamente um json com infos persistentes do module,
        tipo versão, configs e outros dados que precisam sobreviver entre execuções

        returns:
            dicionário com os dados do manifesto, ou vazio se ainda não existir
        """

        if not self.manifest_file.is_file():
            return {}
    
        return json_io.read_json(self.manifest_file)