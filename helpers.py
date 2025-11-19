import json
import string
import random
import settings
import re
import logger
from pathlib import Path
from datetime import datetime
from datetime import timedelta
from numerize.numerize import numerize
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs

def confirm(prompt: str, default: bool = False, assume_default: bool = False):
    """
    exibe um prompt de sim ou não pro usuário  
      
    @param prompt:  
        texto a ser exibido  
      
    @param default:  
        valor padrão de resposta. é destacado com uppercase na exibição do prompt  
        se o usuário não responder nada, esse é o valor que vai ser usado  
      
    @param assume_default:  
        se for verdadeiro, faz o prompt ser completamente ignorado,  
        retornando uma resposta positiva sem confirmação
    """

    if assume_default:
        return True
    
    # construir e mostrar o input
    # a opção padrão é mostrada em uppercase, enquanto a não-padrão é lowercase
    display = '(Y/n)' if default == True else '(y/N)'
    answer = input(f'{prompt} {display} ').strip().lower()
    
    # retornar o valor padrão caso só aperte enter e não especifique nada
    if not answer:
        return default

    # se teve resposta, retornar se ela foi 'sim' ou o oposto
    return answer == 'y'

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
    # transforma 1.243 em 1K
    return numerize(view_count, decimals=0)

def format_duration(seconds: int):
    duration = str(timedelta(seconds=seconds)) # hh:mm:ss
    
    # remover a primeira parte (hh:) se o vídeo tiver menos de 1 hora
    # isso é identificado quando a primeira parte é só '0'
    # a string é cortada e o que é retornado é apenas a parte relevante
    if duration[0] == '0':
        duration = duration[2:]

    return duration

def build_youtube_url(video_id: str):
    """
    reconstrói uma url do youtube a partir do id de um vídeo  
    é majoritariamente usada quando um vídeo precisa ser passado pro yt-dlp
    """

    return f'https://www.youtube.com/watch?v={video_id}'

def extract_youtube_video_id(url: str, ytdl_options: dict):
    """
    extrai o id de um vídeo por uma url do youtube  
    o yt-dlp já tem um método pra obter o id, mas esse método é mais rápido  
    ele é menos confiável que o yt-dlp, então se ele quebrar, ele usa a api como fallback
    """

    # tenta extrair por regex, que é mais rápido, mas menos robusto
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url # adiciona esquema se faltar

    query = urlparse(url)
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        return parse_qs(query.query).get('v', [None])[0]
    elif query.hostname == 'youtu.be':
        return query.path.lstrip('/')

    # se não conseguir o id só pelo regex, tenta com o yt-dlp
    logger.warning('erro ao extrair id com regex. tentando novamente com a api do yt-dlp')

    try:
        ytdl = YoutubeDL(ytdl_options)
        info = ytdl.extract_info(url, download=False)

        return info.get('id', None)
    except:
        logger.error(f'erro ao extrair id com a api do yt-dlp')
    
    logger.critical(f'nenhum método de extração de id funcionou com a url: {url}')
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

def get_playlist_file_by_id(playlist_id: str, directory: Path):
    """
    a partir do diretório passado pra função, verifica todas as playlists válidas nele  
    e tenta achar uma que contém o mesmo id passado
    """

    # ler todos os arquivos até achar uma playlist com o mesmo id passado
    for f in directory.iterdir():
        data = json_read_playlist(f)

        if not is_playlist_valid(playlist_file=f, playlist_data=data):
            continue
    
        if data.get('id') == playlist_id:
            return f
    
    logger.error(f'erro ao obter o arquivo da playlist com o id: {playlist_id}')
    return None

def get_playlist_title(playlist_file: Path):
    # o título de uma playlist é o nome do arquivo sem a extensão
    if playlist_file.exists() and playlist_file.is_file():
        return playlist_file.stem

def is_playlist_valid(playlist_file: Path, playlist_data: dict | None = None, superficial_validation: bool = False) -> bool:
    """
    verifica a validade de uma playlist ou seus dados  
    a verificação de dados é necessária porque o arquivo pode ser um json válido,  
    mas não ter a estrutura esperada de uma playlist
      
    @param playlist_file:  
        obrigatório. nem toda chamada da função requer reler o arquivo inteiro  
        mas toda chamada requer verificar a extensão/sufixo do arquivo  
      
    @param playlist_data:  
        opicional. se for passado, a playlist não precisa ser lida duas vezes desnecessariamente  
        quando uma função precisa saber se uma playlist é válida, mas ao mesmo tempo também já leu ela  
        pode só passar os dados já extraídos pra validação  
      
    @param superficial_validation:  
        opcional. se for verdadeiro, faz a checagem apenas baseada nas informações externas,  
        como a existência, sufixo ou tipo do arquivo. é menos preciso, mas mais rápido por não precisar de i/o
    """
    logger.info(f'iniciando verificação de:\narquivo: {playlist_file}\ndados: {playlist_data}')

    # múltiplos ifs em vez de um só pra mais clareza e diagnóstico
    if not playlist_file.exists():
        logger.warning(f'o arquivo não existe: {playlist_file}')
        return False
    elif not playlist_file.is_file():
        logger.warning(f'o caminho não representa um arquivo: {playlist_file}')
        return False
    elif not playlist_file.suffix == '.json':
        logger.warning(f'o arquivo não é tem a extensão .json: {playlist_file}')
        return False

    # parar logo aqui se for uma verifiação superficial
    if superficial_validation:
        return True
    
    # se o conteúdo já aberto não tiver sido passado pra função, lê em tempo de execução
    # se não encontrar nada, já é inválido
    if playlist_data is None:
        playlist_data = json_read_playlist(playlist_file)
        
        if not playlist_data:
            logger.warning(f'não foi possível ler o arquivo a ser validado: {playlist_data}')
            return False

    # se um desses campos não estiverem nos dados extraídos, é inválido
    required_fields = ['entries', 'id']
    
    for field in required_fields:
        if field not in playlist_data:
            return False

    # se as entries não forem uma lista, é inválido
    if not isinstance(playlist_data['entries'], list):
        return False

    # se nenhuma das ocorrências a cima acontecer, é válido
    return True

def generate_random_id(id_length: int = 8):
    """
    gera um id usando todas as letras, numeros e alguns caracteres especiais
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

def json_read_playlist(playlist_file: Path) -> dict | None:
    """
    lê e retorna os dados dentro de um arquivo que representa uma playlist
    """

    if not is_playlist_valid(playlist_file, superficial_validation=True):
        logger.warning(f'o caminho {playlist_file} não representa uma playlist válida')
        return None

    try:
        with playlist_file.open('r', encoding='utf-8') as f:
            data = json.load(f)

            # se não achar nenhum dado, o arquivo tá vazio
            if data is None:
                logger.info(f'o arquivo {playlist_file} está provavelmente vazio')
    except Exception as err:
        logger.error(f'erro ao tentar ler a playlist {playlist_file} mesmo que ela aparente ser válida: {err}')
        return None

    return data

def json_write_playlist(playlist_file: Path, data_to_write: dict):
    """
    escreve dados estruturados pra representar uma playlist  
    não guarda url de vídeos, apenas o id deles  
    toda vez que é chamada, atualiza a data de modificação da playlist
    """

    data_to_write['last-modified-at'] = get_iso_datetime()

    with playlist_file.open('w', encoding='utf-8') as f:
        json.dump(data_to_write, f, indent=4, ensure_ascii=False)

def json_read_cache(cache_file: Path):
    """
    lê o arquivo de cache atual e retorna o seu conteúdo
    """
    
    if not cache_file.exists() or cache_file.stat().st_size == 0:
        # se o arquivo ainda não existir ou estiver vazio, cria um objeto vazio como fallback
        # stat = propriedades do arquivo, st_size = tamanho em bytes. se for 0, tá vazio
        current_cache = {}
    else:
        # caso o arquivo esteja em condições normais, só lê direto
        with cache_file.open('r', encoding='utf-8') as f:
            current_cache = json.load(f)

    return current_cache

def json_write_cache(data_to_write: dict, cache_file: Path):
    """
    escreve informações de vídeos no cache  
    serve pra salvar dados já obtidos e evitar chamadas extras pra api do yt-dlp  
    """

    with cache_file.open('w', encoding='utf-8') as f:
        json.dump(data_to_write, f, indent=4, ensure_ascii=False)
    
def normalize_json_file(path: Path | str):
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