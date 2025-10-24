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

def write_playlist(playlist_title: str, output_dir: Path):
    current_date = date.today().isoformat() # obter a data em yyyy-mm-dd
    playlist_id = generate_random_id()

    # construir o caminho final do arquivo    
    final_path = Path(output_dir, playlist_title + '.yaml')

    # estruturar os dados
    data = {
        #'title': playlist_title,
        'created-at': current_date,
        'id': playlist_id,
        'urls': []
    }
    logger.debug(f'dados a serem escritos em {str(final_path)}: {str(data)}')
    
    if not handle_existing_file(final_path):
        logger.info(f'criação da playlist {playlist_title} cancelada')
        return
    
    # escrever os dados da playlist em um arquivo que a representa
    with final_path.open('w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True)
    
    logger.success(f'arquivo criado em {str(final_path)}')