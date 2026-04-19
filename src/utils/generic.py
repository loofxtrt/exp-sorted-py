from pathlib import Path
from datetime import datetime
import random
import string

from .. import logger


def ensure_directory(directory: Path):
    """
    garante que um diretório exista no sistema de arquivos

    se o diretório não existir, ele é criado junto com todos os pais necessários

    args:
        directory:
            caminho do diretório que deve ser verificado/criado
    """
    
    directory.mkdir(exist_ok=True, parents=True)

def truncate_text(text: str, max_characters: int):
    """
    corta um texto caso ele ultrapasse um limite de caracteres

    args:
        text:
            texto original que pode ou não ser reduzido

        max_characters:
            limite máximo de caracteres permitido
    """

    if len(text) > max_characters:
        # se o texto passado for realmente maior do que o permitido,
        # corta os caracteres do índice 0 até o limite e adiciona um sinalizador no final (ex: ...)
        # é a mesma coisa que [0:max_chars], mas com o 0 omitido
        text = text[:max_characters - 3] + '...'

    return text

def get_iso_datetime():
    """
    retorna a data e hora atual baseada no formato iso 8601
    """
    
    # yyyy-mm-ddThh:mm:ss. o timespec é pra não incluir microsegundos
    return datetime.now().isoformat(timespec='seconds')

def generate_random_id(id_length: int = 16):
    """
    gera um id usando todas as letras, numeros e alguns caracteres especiais

    args:
        id_length:
            tamanho total do id gerado
    """

    # obter uma string com todas as letras do alfabeto (upper e lower)
    # todos os digitos numéricos (0-9)
    # underscore (_) e hífen (-)
    characters = string.ascii_letters + string.digits + '-' + '_'

    # criar um id, atribuindo um índice aleatório do grupo de caracteres
    # até que o comprimento total do id seja preenchido
    final_id: str = ''
    for i in range(id_length):
        final_id += random.choice(characters)

    logger.debug('novo id gerado: ' + final_id)
    return final_id

def normalize_json_file(path: Path | str):
    """
    garante que um nome de arquivo termine com extensão .json

    se o caminho já tiver extensão json, nada é alterado
    se não tiver, a extensão é adicionada automaticamente

    args:
        path:
            caminho original que pode ser string ou Path
    """

    # adicionar a extensão no caminho
    normalized = str(path)
    if not normalized.endswith('.json'):
        normalized += '.json'
    
    # transformar o valor normalizado de volta em path
    # caso esse tenha sido o formato passado pra essa função inicialmente
    # ela deve apenas normalizar, não mudar o tipo
    if isinstance(path, Path):
        normalized = Path(normalized)

    return normalized