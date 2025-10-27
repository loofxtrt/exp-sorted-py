import json
import string
import random
import settings
from pathlib import Path
from loguru import logger
from datetime import datetime
from datetime import timedelta
from numerize.numerize import numerize

from urllib.parse import urlparse, parse_qs

def format_upload_date(upload_date: str):
    # a data do yt-dlp originalmente vem como a string '20251026'
    # pra manipular ela, primeiro precisa converter a string pra um formato de datetime
    # ex: (2025, 10, 26, 0, 0)
    upload_date = datetime.strptime(upload_date, '%Y%m%d')

    # depois, reformata esse agora objeto de datetime, pra uma string de volta
    # b: mês por extenso abreviado
    # -d: número do dia sem um padding zero a esquerda
    # (https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)
    return datetime.strftime(upload_date, '%b %-d, %Y').capitalize()

def format_view_count(view_count: int):
    return numerize(view_count, decimals=0)

def format_duration(seconds: int):
    duration = str(timedelta(seconds=seconds)) # hh:mm:ss
    
    # remover a primeira parte (hh:) se o vídeo tiver menos de 1 hora
    # portanto, essa parte não é necessária
    if duration[0] == '0':
        duration = duration[2:]

    return duration

def build_youtube_url(video_id: str):
    """reconstrói uma url do youtube a partir do id de um vídeo"""

    return f'https://www.youtube.com/watch?v={video_id}'

def extract_youtube_video_id(url: str):
    """extrai o id de um vídeo por uma url do youtube"""

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url # adiciona esquema se faltar

    query = urlparse(url)
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        return parse_qs(query.query).get('v', [None])[0]
    elif query.hostname == 'youtu.be':
        return query.path.lstrip('/')
    return None

def truncate_text(text: str, max_characters: int):
    if len(text) > max_characters:
        # se o texto passado for realmente maior do que o permitido,
        # corta os caracteres do índice 0 até o limite e adiciona um sinalizador no final (ex: ...)
        # é a mesma coisa que [0:max_chars], mas com o 0 omitido
        text = text[:max_characters - 3] + '...'

    return text

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
    """lê e retorna os dados dentro de um arquivo que representa uma playlist"""

    with playlist_file.open('r', encoding='utf-8') as f:
        data = json.load(f)

        # se não achar nenhum dado, o arquivo tá vazio
        if data is None:
            logger.error(f'o arquivo {playlist_file} está vazio ou corrompido')

    return data

def json_write_playlist(playlist_file: Path, data_to_write: dict):
    """escreve dados estruturados como um dicionário em um arquivo que representa uma playlist"""

    data_to_write['last-modified-at'] = get_iso_datetime()

    with playlist_file.open('w', encoding='utf-8') as f:
        json.dump(data_to_write, f, indent=4)

def json_read_cache(cache_file: Path = settings.CACHE_FILE):
    """lê o arquivo de cache atual e retorna o seu conteúdo"""
    
    if not cache_file.exists() or cache_file.stat().st_size == 0:
        # se o arquivo ainda não existir ou estiver vazio, cria um objeto vazio como fallback
        # stat = propriedades do arquivo, st_size = tamanho em bytes. se for 0, tá vazio
        current_cache = {}
    else:
        # caso o arquivo esteja em condições normais, só lê direto
        with cache_file.open('r', encoding='utf-8') as f:
            current_cache = json.load(f)

    return current_cache