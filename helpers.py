import yaml
import string
import random
from pathlib import Path
from loguru import logger

def generate_random_id(id_length: int = 8):
    # obter uma string com todas as letras do alfabeto (upper e lower)
    # e todos os digitos numéricos (0-9)
    characters = string.ascii_letters + string.digits

    # criar um id, atribuindo um índice aleatório do grupo de caracteres
    # até que o comprimento total do id seja preenchido
    final_id: str = ''
    for i in range(id_length):
        final_id += random.choice(characters)

    logger.debug('novo id gerado: ' + final_id)
    return final_id

def handle_existing_file(file_path: Path) -> bool:
    """
    resolvedor de conflitos em casos onde um arquivo já existe
    @param file_path: o caminh do arquivo que deve ser verificado pra ter certeza que já não existe outro igual
    """
    
    # se o arquivo já existir, perguntar pro usuário se ele deve ser sobreescrito mesmo assim
    # caso a resposta seja qualquer coisa diferente de 'sim', se assume que NÃO deve sobreescrever
    if file_path.exists():
        # resposta tratada sem espaços e sempre em lowercase
        answer = input(f'o arquivo {file_path.name} já existe. prosseguir sobreescreverá ele, continuar? (y/N) ').strip().lower()
        
        # confirma a remoção, caso contrário, false
        if answer == 'y':
            return True
        
        return False
    
    # se já não existir, não tem problema
    return True

def yaml_read_playlist(playlist_file: Path):
    with playlist_file.open('r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
        
        # se o arquivo estiver vazio, ele vira um dict, se não daria erro
        if data is None:
            data = {}
    
    return data

def yaml_write_playlist(playlist_file: Path, data_to_write: dict):
    with playlist_file.open('w', encoding='utf-8') as file:
        yaml.safe_dump(
            data_to_write,
            stream=file,
            allow_unicode=True,
            indent=4,
        )
