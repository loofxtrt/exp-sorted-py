from pathlib import Path
from managers.playlists import playlist_utils
import json

def json_read_playlist(playlist_file: Path) -> dict | None:
    """
    lê e retorna os dados dentro de um arquivo que representa uma playlist
    """

    if not playlist_utils.is_playlist_valid(playlist_file, superficial_validation=True):
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
    
