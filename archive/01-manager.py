# ESSA VERSÃO INCLUE O TÍTULO DUPLICADO DENTRO DO ARQUIVO YAML E NÃO USA SÓ O NOME DO ARQUIVO NO SISTEMA

import yaml
import string
import random
from pathlib import Path
from datetime import date
from loguru import logger

def generate_random_id(id_length: int = 6):
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

def write_playlist(playlist_title: str, output_dir: Path):
    current_date = date.today().isoformat() # obter a data em yyyy-mm-dd
    playlist_id = generate_random_id()

    # construir o caminho final do arquivo    
    final_path = Path(output_dir, str(playlist_id) + '.yaml')

    # estruturar os dados
    data = {
        'title': playlist_title,
        'created-at': current_date,
        'id': playlist_id,
        'urls': []
    }
    logger.debug(f'dados a serem escritos em {str(final_path)}: {str(data)}')
    
    # escrever os dados da playlist em um arquivo que a representa
    with final_path.open('w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True)
    
    logger.success(f'arquivo criado em {str(final_path)}')