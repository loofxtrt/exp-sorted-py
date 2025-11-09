import settings
import helpers
import pathvalidate
import logger
from yt_dlp import YoutubeDL
from pathlib import Path

class PlaylistError(Exception): pass
class VideoError(Exception): pass

def is_entry_present(playlist_data: dict, video_id: str):
    # se existir um dicionário na lista de entries
    # que contenha uma url idêntica a target passada pra função, é true
    if any(entry.get('id') == video_id for entry in playlist_data['entries']):
        return True
    
    return False

def create_playlist(
    playlist_title: str,
    output_dir: Path,
    playlist_description: str | None = None,
    assume_default: bool = False
    ):
    # garante que o título é válido pra ser o nome de um arquivo
    try:
        pathvalidate.validate_filename(playlist_title)
    except pathvalidate.ValidationError:
        logger.error('o título contém caracteres inválidos para a criação de um arquivo')
        return

    # obter a data iso já formatada e um id aleatório novo pra playlist
    current_date = helpers.get_iso_datetime()
    playlist_id = helpers.generate_random_id()

    # construir o caminho final do arquivo
    # garantindo a não-redundância de extensões e a presença da estrutura de diretórios
    if not playlist_title.lower().endswith('.json'):
        playlist_title + '.json'
    else:
        logger.info('o título pra nova playlist já possui a extensão .json')

    output_dir.mkdir(exist_ok=True, parents=True)
    final_path = Path(output_dir, playlist_title)

    # estruturar os dados
    data = {
        'created-at': current_date,
        'id': playlist_id,
        'entries': []
    }
    if playlist_description:
        # adicionar a descrição caso ela tenha sido passada
        # se não foi, o campo não vai estar presente no arquivo
        data['description'] = playlist_description
    
    logger.debug(f'dados a serem escritos em {str(final_path)}: {str(data)}')
    
    # se a playlist já existir
    if final_path.exists() and final_path.is_file():
        answer = helpers.confirm(
            prompt=f'o arquivo {final_path} já existe. prosseguir sobreescreverá ele, continuar?',
            assume_default=assume_default,
            default=False    
        )

        if not answer:
            return

    # escrever os dados da playlist em um arquivo que a representará
    helpers.json_write_playlist(final_path, data)
    logger.success(f'arquivo criado em {str(final_path)}')

def delete_playlist(
    playlist_file: Path,
    assume_default = False,
    superficial_validation: bool = False
    ):
    """
    deleta uma playlist inteira  
      
    @param assume_default:  
        se for verdadeiro, não pede uma confirmação antes de apagar uma playlist  
      
    @param superficial_validation:  
        se verdadeiro, garante que apenas arquivos que sejam estritamente playlists válidas sejam deletados  
        é falso por padrão porque se um arquivo de playlist tiver uma formatação quebrada, ele pode ser mais difícil de deletar
    """

    if not helpers.is_playlist_valid(playlist_file=playlist_file, superficial_validation=superficial_validation):
        logger.info('a playlist à ser deletada é inválida. verifique se o arquivo realmente representa uma ou o remova manualmente')
        return
    
    answer = helpers.confirm(
        prompt=f'deletar {helpers.get_playlist_title(playlist_file)}?',
        assume_default=assume_default,
        default=False
    )
    if not answer:
        return

    # unlink é o equivalente a deletar
    playlist_file.unlink()
    logger.success('playlist deletada')

def insert_video(playlist_file: Path, video_id: str, assume_default = False):
    # outra função pode acidentalmente passar um id nulo se a extração der errado
    if not video_id:
        logger.warning(f'vídeo não adicionado à playlist. o id é inválido: {video_id}')
        return
    
    # criar a playlist primeiro caso ela ainda não exista
    # se assume que o output dir e o título serão os mesmos do arquivo não-existente passado pra função
    if not playlist_file.exists():
        answer = helpers.confirm(
            prompt='essa playlist ainda não existe, criar ela agora?',
            assume_default=assume_default,
            default=True
        )
        if not answer:
            return

        # também garante que a estrutura de diretórios inteira passada exista
        playlist_file.parent.mkdir(exist_ok=True, parents=True)
        create_playlist(playlist_title=playlist_file.stem, output_dir=playlist_file.parent)

    # ler os dados atuais da playlist
    data = helpers.json_read_playlist(playlist_file)
    
    if not helpers.is_playlist_valid(playlist_file=playlist_file, playlist_data=data):
        return

    # verificação pra evitar duplicação acidental de vídeos
    existing = is_entry_present(data, video_id)
    if existing:
        logger.info('o vídeo já está presente na playlist')
        return

    # obter a data em que o vídeo foi inserido
    # é útil pra opções de ordenação por data de inserção
    current_date = helpers.get_iso_datetime()
    
    # montar o objeto que representa uma entrada de vídeo
    video = {            
        'id': video_id,
        'inserted-at': current_date
    }

    # adicionar o vídeo solicitado ao array de dicts e reescrever esses dados novos no mesmo arquivo
    data['entries'].append(video)
    helpers.json_write_playlist(playlist_file, data)
    
    logger.success(f'{video_id} adicionado na playlist {playlist_file.stem}')

def remove_video(playlist_file: Path, video_id: str):
    if not video_id: return

    data = helpers.json_read_playlist(playlist_file)
    entries = data.get('entries')

    for entry in entries:
        # se o id alvo de remoção estiver presente em um desses campos,
        # remove a entrada do dicionário a qual ele pertence e atualiza os dados
        if entry.get('id') == video_id:
            entries.remove(entry)
            helpers.json_write_playlist(playlist_file, data)

            logger.success(f'{video_id} removido da playlist {playlist_file.stem}')
        
            return
    else:
        # se o for inteiro rodar sem nenhum break, o vídeo não foi encontrado
        logger.info(f'{video_id} não está presente na playlist {playlist_file.stem}')

def move_video(origin_playlist: Path, destination_playlist: Path, video_id: str, assume_default: bool = False):
    """
    move um vídeo de uma playlist a outra, o removendo da origem e inserindo no destino
    """
    # obtém os dados das playlists, mas só a de origem é obrigatória
    # se a de destino não existir, pode ser criada em tempo de execução
    origin_data = helpers.json_read_playlist(origin_playlist)
    dest_data = helpers.json_read_playlist(destination_playlist)

    if not origin_data:
        logger.error(f'a playlist de origem não existe')
        return
    
    if not dest_data and not assume_default:
        answer = helpers.confirm('a playlist de destino ainda não existe, criar ela agora?', default=True)
        if answer:
            create_playlist(
                playlist_title=destination_playlist.name,
                output_dir=destination_playlist.parent
            )

            # reler o arquivo atualizado
            # sem isso, o código quebra por ainda ter os dados inválidos
            dest_data = helpers.json_read_playlist(destination_playlist)
        else:
            return

    # obter os títulos só pra logging
    dest_title = helpers.get_playlist_title(destination_playlist)
    origin_title = helpers.get_playlist_title(origin_playlist)

    # entra na playlist de origem
    # e pra cada entrada, checa se o id é igual ao do vídeo alvo de movimento
    for entry in origin_data.get('entries'):
        # se encontrar o vídeo na playlist de origem, remove ele de lá
        # e adiciona esse mesmo vídeo na playlist de destino
        if entry.get('id') == video_id:
            # se o vídeo que está tentando ser movido já existe na playlist de destino, não continua
            if is_entry_present(playlist_data=dest_data, video_id=video_id):
                logger.info(f'o mesmo vídeo ({video_id}) já existe na playlist de destino {dest_title}')
                return

            remove_video(origin_playlist, video_id)
            insert_video(destination_playlist, video_id)

            logger.success(f'vídeo movido de {origin_title} para {dest_title}')
        
            return
    else:
        # se não encontrar o vídeo na playlist de origem
        logger.info(f'o vídeo ({video_id}) não existe na playlist de origem {origin_title}')
        return