from pathlib import Path

from yt_dlp import YoutubeDL

from .playlists import playlist_utils
from . import settings
from .. import logger
from ..utils import json_io
from ..services import youtube

def is_video_cached(video_id: str, cache_file: Path) -> bool:
    """
    consulta o cache pra verificar A PRESENÇA de um vídeo  
    essa função NÃO obtém as informações daquele vídeo, só confirma se ele de fato existe ou não
    """
    
    # retornar true se o id existir no cache e false caso não exista
    cache = json_io.json_read_cache(cache_file)
    return video_id in cache

def get_cached_video_info(video_id: str, cache_file: Path):
    """
    consulta o cache pra tentar obter os dados de um vídeo sem precisar chamar a api do yt-dlp
    se o vídeo já não tiver sido cacheado, a api então é chamada, e depois o cache é reconsultado
    
    args:
        video_id:
            id do vídeo a ser consultado. também é o recurso usado pra reconstruir a url do vídeo
            em caso de necessidade de adiciona-lo ao cache em tempo de execução

        cache_file:
            o arquivo de cache onde o vídeo deve ser procurado, e onde ele será escrito se necessário
    """

    # ler o cache e tentar obter o dict do vídeo pelo seu id
    cache = json_io.json_read_cache(cache_file)
    video_data = cache.get(video_id)

    # se os dados do vídeo estiverem presentes no cache retorna eles,
    # mas se não estiverem, insere os dados no meio da execução
    if video_data:
        return video_data
    else:
        # solicitar a adição do novo vídeo ao cache
        video_url = youtube.build_youtube_url(video_id)
        write_video_cache(video_url, cache_file, settings.get('ytdl_options'))

        # depois de atualizado, consultar o cache de novo
        updated_cache = json_io.json_read_cache(cache_file)
        video_data = updated_cache.get(video_id)
        
        if video_data:
            return video_data
        else:
            logger.error(f'erro ao tentar obter as informações do vídeo com o id: {video_id}')

def insert_video_on_memory_cache(video_data: dict, cache_data: dict):
    """
    constrói a estrutura que um vídeo deve ter no cache
    isso NÃO ESCREVE nada no cache, apenas formata os dados do vídeo
    
    deve ser usado por funções que realmente escrevam algo
    não precisa de return porque o cache_data passado pra função já é o mesmo que o chamador vai usar

    args:
        video_data:
            dados do vídeo já parseados
    
        cache_data:
            dados do cache já parseados
    """

    if not video_data:
        logger.error(f'não foi possível adicionar o vídeo no cache da memória. os dados são inválidos: {video_data}')
        return

    # remover o id do vídeo dos dados e guarda-lo numa variável
    # o id do vídeo é usado como chave no cache, e não como elemento comum,
    # por isso precisa estar fora do dicionário, pra servir de parent pro resto dos dados
    video_id = video_data.pop('id')
    cache_data[video_id] = video_data

def write_video_cache(
    url: str,
    cache_file: Path,
    ytdl_options: dict
    ):
    """
    escreve um único vídeo no cache, criando uma instância da api em toda chamada
    a estrutura atual de uma entrada no cache é usar o id do vídeo como chave pro resto dos dados
    ou seja, o id não faz parte do objeto do vídeo, ele é o "pai" que o identifica

    args:
        url:
            vídeo a ser escrito no cache
      
        cache_file:
            arquivo do cache, onde as novas informações serão escritas

        ytdl_options:
            opções da api do yt-dlp
    """

    # obter os dados do vídeo e do cache atual
    ytdl = YoutubeDL(ytdl_options)
    video = youtube.extract_youtube_video_info(url, ytdl_instance=ytdl)
    
    cache = json_io.json_read_cache(cache_file)
    
    if not video or not cache:
        return

    # atualizar o cache
    insert_video_on_memory_cache(video_data=video, cache_data=cache)
    json_io.json_write_cache(data_to_write=cache, cache_file=cache_file)

def update_full_cache(
    playlists_directory: Path,
    ytdl_options: dict,
    cache_file: Path,
    skip_already_cached: bool = True,
    ):
    """
    atualiza o cache inteiro com base nos vídeos únicos que aparecem nas playlists
    isso significa adicionar ao cache todos os vídeos que ainda não estavam lá,
    e também remover os vídeos que não aparecem mais em nenhuma playlist
    
    é um processo lento comparado a uma única escrita, mas uma vez chamado,
    agiliza a visualização de todas as playlists

    args:
        playlists_directory:
            diretório base onde as playlists devem ser procuradas. tudo que for uma playlist
            e estiver dentro desse diretório e seus filhos, será consultado pra obter quais ids de vídeos únicos ela possui
    
        cache_file:
            arquivo do cache, onde as novas informações serão escritas
    
        ytdl_options:
            opções da api do yt-dlp

        skip_already_cached:
            define se os vídeos que já têm suas informações guardadas no cache devem ser obtidos de novo
            caso seja falso, vai atualizar as infos de vídeos já existentes
            por ter que fazer todas as requisições de novo, demora mais pra concluir  
    """

    all_videos_ids = []

    # verificar todas as playlists criadas, partindo do diretório passado pra função
    # essa primeira parte foca em obter os ids de todos os vídeos únicos em todas as playlists
    for pl in playlists_directory.rglob('*.json'):
        # verificar apenas se a playlist for válida
        data = json_io.json_read_playlist(pl)
        if not playlist_utils.is_playlist_valid(playlist_file=pl, playlist_data=data):
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
    
    # depois de obter todos os ids dos vídeos, extrair os dados deles e atualizar o cache
    old_cache = json_io.json_read_cache(cache_file)
    new_cache = {}
    ytdl = YoutubeDL(ytdl_options)
    
    for v_id in all_videos_ids:
        # por padrão, não atualizar vídeos que já estão no cache,
        # só copia a versão atual deles pro cache novo, evitando chamadas de api
        # isso faz essa ação demorar menos, mas pode deixar as views de alguns vídeos desatualizadas
        if skip_already_cached and v_id in old_cache:
            new_cache[v_id] = old_cache[v_id]

            logger.info(f'vídeo não atualizado por já estar presente no cache: {v_id}')
            continue
        
        # incluir vídeos que ainda não estavam no cache
        # se for explicitamente pedido, também atualiza os já existentes
        url = youtube.build_youtube_url(v_id)
        video = youtube.extract_youtube_video_info(url, ytdl_instance=ytdl)
        
        insert_video_on_memory_cache(video_data=video, cache_data=new_cache)
    
    # escrever o cache atualizado
    json_io.json_write_cache(
        data_to_write=new_cache,
        cache_file=cache_file
    )