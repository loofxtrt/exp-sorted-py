import yaml
import string
import random
from pathlib import Path
from datetime import date

def generate_random_id(id_length: int = 6):
    # obter uma string com todas as letras do alfabeto (upper e lower)
    # e todos os digitos numéricos (0-9)
    characters = string.ascii_letters + string.digits

    # criar um id, atribuindo um índice aleatório do grupo de caracteres
    # até que o comprimento total do id seja preenchido
    final_id: str = ''
    for i in range(id_length):
        final_id += random.choice(characters)

    return final_id

print(generate_random_id())

def write_playlist(playlist_title: str, output_dir: Path):
    # obter a data em yyyy-mm-dd
    current_date = date.today().isoformat()

    data = {
        'title': playlist_title,
        'created-at': current_date,
        'urls': []
    }
    
    # escrever os dados da playlist em um arquivo que a representa
    with output_dir.open('r', encoding='utf-8') as f:
        yaml
