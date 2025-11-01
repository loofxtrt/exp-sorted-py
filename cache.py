import json
import helpers
import settings
from pathlib import Path
from yt_dlp import YoutubeDL
from loguru import logger

def is_video_cached(video_id: str, cache_file: Path = settings.CACHE_FILE) -> bool:
    """
    consulta o cache pra verificar A PRESENÇA de um vídeo  
    essa função NÃO obtém as informações daquele vídeo, só confirma se ele de fato existe ou não
    """
    
    # retornar true se o id existir no cache e false caso não exista
    cache = helpers.json_read_cache(cache_file)
    return video_id in cache

def get_cached_video_info(video_id: str, cache_file: Path = settings.CACHE_FILE):
    """
    consulta o cache pra tentar obter os dados de um vídeo sem precisar chamar a api do yt-dlp  
    se o vídeo já não tiver sido cacheado, a api então é chamada, e depois o cache é reconsultado  
      
    @param video_id:  
        id do vídeo a ser consultado. também é o recurso usado pra reconstruir a url do vídeo  
        em caso de necessidade de adiciona-lo ao cache em tempo de execução  
      
    @param cache_file:  
        o arquivo de cache onde o vídeo deve ser procurado, e onde ele será escrito se necessário
    """

    # ler o cache e tentar obter o dict do vídeo pelo seu id
    cache = helpers.json_read_cache(cache_file)
    video_data = cache.get(video_id)

    # se os dados do vídeo estiverem presentes no cache retorna eles,
    # mas se não estiverem, insere os dados no meio da execução
    if video_data:
        return video_data
    else:
        # solicitar a adição do novo vídeo ao cache
        video_url = helpers.build_youtube_url(video_id)
        write_single_video_cache(video_url, cache_file)

        # depois de atualizado, consultar o cache de novo
        updated_cache = helpers.json_read_cache(cache_file)
        video_data = updated_cache.get(video_id)
        
        if video_data:
            return video_data
        else:
            logger.error(f'erro ao tentar obter as informações do vídeo com o id: {video_id}')

def extract_video_info(url: str, ytdl_instance: YoutubeDL) -> dict | None :
    """
    usa a api do yt-dlp pra extrair dinamicamente os dados de um vídeo  
    por fazer uso da api, deve ser evitada na maioria dos casos  
      
    essa função geralmente é chamada pela consultora de vídeos já cacheados,  
    quando ela tenta buscar um vídeo no cache e ele ainda não existe, ela chama  
      
    @param url:  
        url do vídeo a ser consultado  
      
    @param ytdl_instance:  
        instância já criada da api do yt-dlp. isso evita que múltiplas instâncias precisem ser criadas
    """
    try:
        info = ytdl_instance.extract_info(url, download=False)
    except Exception as err:
        logger.error(f'erro ao tentar extrair os dados do vídeo {url}: {err}')
        return None

    video_id = info.get('id') # dígitos que aparecem depois de watch?v= em urls de vídeos
    title = info.get('title')
    upload_date = info.get('upload_date') # yyyymmdd
    uploader = info.get('uploader')
    view_count = info.get('view_count')
    duration = info.get('duration', 0) # segundos. 0 é fallback se o campo não estiver presente
    thumbnail = info.get('thumbnail')
    description = info.get('description')
    
    # estruturar os dados obtidos em um objeto json
    video_data = {
        'id': video_id,
        'title': title,
        'upload_date': upload_date,
        'uploader': uploader,
        'view_count': view_count,
        'duration': duration,
        'description': description,
        'thumbnail': thumbnail,
    }

    return video_data

def write_single_video_cache(
    url: str,
    cache_file: Path = settings.CACHE_FILE,
    ytdlp_options: dict = settings.YTDLP_OPTIONS
    ):
    """
    escreve um único vídeo no cache, criando uma instância da api em toda chamada  
    a estrutura atual de uma entrada no cache é usar o id do vídeo como chave pro resto dos dados  
    ou seja, o id não faz parte do objeto do vídeo, ele é o "pai" que o identifica  
      
    @param url:  
        vídeo a ser escrito no cache  
      
    @param cache_file:  
        arquivo do cache, onde as novas informações serão escritas  
    
    @param ytdlp_options:  
        opções da api do yt-dlp
    """
    ytdlp = YoutubeDL(ytdlp_options)
    data = extract_video_info(url, ytdl_instance=ytdlp)
    if not data:
        return

    # remover o id do vídeo do retorno da função de extração de dados
    # o id do vídeo é usado como chave no cache, e não como elemento comum,
    # por isso precisa estar fora do dicionário
    video_id = data.pop('id')

    # ler o cache atual e adicionar o objeto dos dados do vídeo a essa lista do cache
    # usando o id como a chave pro resto dos dados
    cache = helpers.json_read_cache(cache_file)
    cache[video_id] = data

    # atualizar o cache
    helpers.json_write_cache(data_to_write=cache, cache_file=cache_file)

def update_full_cache(
    playlists_directory: Path,
    ytdlp_options: dict = settings.YTDLP_OPTIONS,
    cache_file: Path = settings.CACHE_FILE
    ):
    """
    atualiza o cache inteiro com base nos vídeos únicos que aparecem nas playlists  
    isso significa adicionar ao cache todos os vídeos que ainda não estavam lá,  
    e também remover os vídeos que não aparecem mais em nenhuma playlist  
      
    é um processo lento comparado a uma única escrita, mas uma vez chamado,  
    agiliza a visualização de todas as playlists  
      
    @param playlists_directory:  
        diretório base onde as playlists devem ser procuradas. tudo que for uma playlist  
        e estiver dentro desse diretório e seus filhos, será consultado pra obter quais ids de vídeos únicos ela possui  
      
    @param cache_file:  
        arquivo do cache, onde as novas informações serão escritas  
    
    @param ytdlp_options:  
        opções da api do yt-dlp
    """
    all_videos_ids = []

    # verificar todas as playlists criadas, partindo do diretório passado pra função
    # essa primeira parte foca em obter os ids de todos os vídeos únicos em todas as playlists
    for pl in playlists_directory.iterdir():
        # verificar apenas se a playlist for válida
        data = helpers.json_read_playlist(pl)
        if not helpers.is_playlist_valid(playlist_file=pl, data=data):
            continue

        # entrar na lista de vídeos da playlist atual e obter o id dele
        # se ele já não estiver presente na lista de vídeos encontrados, adiciona ele
        for e in data.get('entries'):
            video_id = e.get('id')

            if not video_id in all_videos_ids:
                all_videos_ids.append(video_id)
    
    if not len(all_videos_ids) > 0:
        logger.info('nenhum vídeo encontrado em nenhuma playlist')
        return
    
    # depois de obter todos os ids dos vídeos, extrai os dados deles
    # e os estrutura como o acache final deve ser
    cache = {}    
    ytdlp = YoutubeDL(ytdlp_options)
    
    for v_id in all_videos_ids:
        url = helpers.build_youtube_url(v_id)
        info = extract_video_info(url, ytdl_instance=ytdlp)
        
        if not info:
            continue
        
        # a função que extrai informações dos vídeos retorna o id deles
        # como parte do dicionário, mas o cache usa o id como chave, não como elemento
        #
        # depois de usar o pop pra remover o id dos dados retornados,
        # usa ele como chave pro resto dos dados
        info.pop('id')
        cache[v_id] = info
    
    # escrever o cache atualizado
    helpers.json_write_cache(
        data_to_write=cache,
        cache_file=cache_file
    )