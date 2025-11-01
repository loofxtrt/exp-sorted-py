import settings
import helpers
import pathvalidate
from yt_dlp import YoutubeDL
from pathlib import Path
from loguru import logger

def is_entry_present(playlist_data: dict, video_id: str):
    # se existir um dicionário na lista de entries
    # que contenha uma url idêntica a target passada pra função, é true
    if any(entry['id'] == video_id for entry in playlist_data['entries']):
        return True
    
    return False

def create_playlist(playlist_title: str, output_dir: Path, playlist_description: str | None = None, assume_default: bool = False):
    # obter a data iso já formatada e um id aleatório novo pra playlist
    current_date = helpers.get_iso_datetime()
    playlist_id = helpers.generate_random_id()

    # construir o caminho final do arquivo    
    final_path = Path(output_dir, playlist_title + '.json')

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

def delete_playlist(playlist_file: Path, assume_default = False):
    if not helpers.is_playlist_valid(playlist_file):
        logger.info('a playlist à ser deletada é inválida')
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

        create_playlist(playlist_title=playlist_file.stem, output_dir=playlist_file.parent)

    # ler os dados atuais da playlist
    data = helpers.json_read_playlist(playlist_file)

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

def move_video(origin_playlist: Path, destination_playlist: Path, video_id: str):
    dest_title = helpers.get_playlist_title(destination_playlist)
    origin_title = helpers.get_playlist_title(origin_playlist)

    # entra na playlist de origem
    # e pra cada entrada, checa se o id é igual ao do vídeo alvo de movimento
    origin_data = helpers.json_read_playlist(origin_playlist)

    for entry in origin_data.get('entries'):
        # se encontrar o vídeo na playlist de origem, remove ele de lá
        # e adiciona esse mesmo vídeo na playlist de destino
        if entry.get('id') == video_id:
            # se o vídeo que está tentando ser movido já existe na playlist de destino, não continua
            if helpers.is_entry_present(destination_playlist, video_id):
                logger.info(f'o mesmo vídeo ({video_id}) já existe na playlist de destino {dest_title}')
                return

            # se ainda não existir no destino, continua o movimento
            helpers.remove_video(origin_playlist, video_id)
            helpers.insert_video(destination_playlist, video_id)

            logger.success(f'vídeo movido de {origin_title} para {dest_title}')
        
            return
    else:
        # se não encontrar o vídeo na playlist de origem
        logger.info(f'o vídeo ({video_id}) não existe na playlist de origem {origin_title}')
        return

def import_playlist(output_dir: Path, yt_playlist_url: str, new_title: str = None, ytdlp_options: dict = settings.YTDLP_OPTIONS):
    logger.info(f'iniciando a importação de uma playlist do youtube: {yt_playlist_url}')

    # tentar obter os dados da playlist
    # é importante que ela seja pública ou não-listada pra isso funcionar
    info = None

    try:
        ytdl = YoutubeDL(ytdlp_options)
        info = ytdl.extract_info(yt_playlist_url, download=False)

        logger.success('dados extraídos da playlist')
    except Exception as err:
        logger.error(f'erro ao importar a playlist: {err}')

    if not info:
        return
    
    # definir/verificar o título que a playlist vai ter
    # se o usuário não passar explicitamente um título novo pra ela,
    # ela tenta usar o título que tava no youtube
    if new_title:
        if not pathvalidate.validate_filename(new_title):
            logger.error('o novo título contém caracteres inválidos para a criação de um arquivo')
            return
    else:
        logger.info('o título da playlist será herdado do youtube')
        new_title = info['title']

        # conferir se o título obtido não tem nenhum caractere inválido
        # se tiver, sanitiza ele antes antes de aplicar
        try:
            pathvalidate.validate_filename(new_title)
            logger.success(f'título validado: {new_title}')
        except pathvalidate.ValidationError:
            logger.error(f'iniciando sanitização. título com caracteres inválidos: {new_title}')
            
            try:
                new_title = pathvalidate.sanitize_filename(new_title)
                logger.success(f'título sanitizado: {new_title}')
            except:
                logger.error(f'a sanitização do título {new_title} falhou. tente definir explicitamente um novo título para a playlist importada')
    
    # cria a playlist e reconstrói como é o novo caminho dela
    create_playlist(playlist_title=new_title, output_dir=output_dir)
    final_path = output_dir / (new_title + '.json')

    # passar todas as urls da playlist do youtube pra playlist local
    # identificando todas as urls de vídeos do campo 'entries' da playlist (vinda do yt-dlp) e obtendo os ids
    logger.success('playlist criada. iniciando a importação dos vídeos dela')
    urls = [entry['webpage_url'] for entry in info['entries'] if entry]

    for u in urls:
        video_id = helpers.extract_youtube_video_id(u)
        insert_video(playlist_file=final_path, video_id=video_id)