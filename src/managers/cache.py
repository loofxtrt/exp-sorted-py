from pathlib import Path

from ..utils.generic import ensure_directory, normalize_json_file
from ..utils import json_io
from .. import logger

class VaultCache:
    """
    gerencia o cache de um vault específico baseado em um contexto de diretório

    esta classe é responsável por carregar e manter em memória um arquivo de cache
    associado a um contexto (path do vault), permitindo leitura simples do estado salvo

    args:
        context:
            diretório base do vault onde o cache será armazenado e carregado
    """
    
    def __init__(self, context: Path):
        self.context = context
        self.cache_file = self.context / normalize_json_file('cache')
        self.data = self.load()

    def load(self):
        """
        carrega o conteúdo do arquivo de cache do vault

        returns:
            dicionário com os dados armazenados no cache json
        """
        
        return json_io.read_json(self.cache_file)

class GlobalCache:
    """
    gerencia o cache de um vault específico baseado em um contexto de diretório

    esta classe é responsável por carregar e manter em memória um arquivo de cache
    associado a um contexto (path do vault), permitindo leitura simples do estado salvo

    args:
        context:
            diretório base do vault onde o cache será armazenado e carregado
    """

    def __init__(self):
        self.cache_file = self.get_cache_dir() / normalize_json_file('global-cache')
        self.data = self.load()

    def load(self):
        """
        carrega o conteúdo do arquivo de cache do vault

        returns:
            dicionário com os dados armazenados no cache json
        """
        
        return json_io.read_json(self.cache_file)

    @staticmethod
    def get_cache_dir() -> Path:
        """
        retorna o diretório padrão de cache global e cria ele caso não exista
        """

        cache_dir = Path.home() / '.cache' / 'sorted'
        ensure_directory(cache_dir)
    
        return cache_dir

    @property
    def last_accessed_vault(self) -> Path | None:
        """
        retorna o último vault acessado salvo no cache global
        verifica se o caminho existe e se é um diretório válido antes de retornar
        """

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
        """
        salva o último vault acessado no cache global

        args:
            root:
                caminho do diretório do vault que será armazenado como último acesso
        """
        
        if not root.is_dir():
            logger.error(f'{root} não é um diretório')
            return
        
        self.data['last_accessed_vault'] = str(root.resolve())
        json_io.write_json(self.cache_file, self.data)