import json
import string
import random
from pathlib import Path
from loguru import logger
from datetime import datetime

def get_iso_datetime():
    # yyyy-mm-ddThh:mm:ss. o timespec é pra não incluir microsegundos
    return datetime.now().isoformat(timespec='seconds')

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
    @param file_path: o caminho do arquivo que deve ser verificado pra ter certeza que já não existe outro igual
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

def json_read_playlist(playlist_file: Path):
    """
    lê e retorna os dados dentro de um arquivo que representa uma playlist
    """
    with playlist_file.open('r', encoding='utf-8') as f:
        data = json.load(f)

        # se não achar nenhum dado, o arquivo tá vazio
        if data is None:
            logger.erro(f'o arquivo {playlist_file} está vazio ou corrompido')

    return data

def json_write_playlist(playlist_file: Path, data_to_write: dict):
    """
    escreve dados estruturados como um dicionário em um arquivo que representa uma playlist
    """

    data_to_write['last-modified-at'] = get_iso_datetime()

    with playlist_file.open('w', encoding='utf-8') as f:
        json.dump(data_to_write, f, indent=4)