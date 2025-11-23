from pathlib import Path
import json
import shutil

from send2trash import send2trash
import pathvalidate

from . import utils
from ... import logger
from ...utils import generic 

class CollectionAlreadyExists(Exception): pass

def create_collection(
    title: str,
    output_directory: Path,
    description: str | None = None,
    force_overwrite: bool = False,
    ensure_parents: bool = True,
    ):
    """
    cria um novo arquivo de collection no diretório especificado

    uma collection é um arquivo que contém metadados sobre ela mesma
    e que comporta uma lista de links para conteúdos diversos
    ela pode conter, por exemplo, urls pra vídeos do youtube
    
    ela NÃO armazena os metadados completos desses conteúdos,
    estes são pegos do cache. o que a collection deve guardar é:
    - id idêntico ao presente no cache pra identificação
    - serviço correspondente à mídia
    - metadados extras, como data de inserção

    explicações mais detalhadas estão presentes na função insert_entry

    args:
        title:
            nome do arquivo, usado como título da collection
        
        output_directory:
            diretório onde a collection será criada
            isso não deve incluir o nome do arquivo no final, apenas o diretório pai
        
        description:
            descrição opcional da collection. só é adicionada se for passada
        
        force_overwrite:
            se for verdadeiro, cria um arquivo independente de um idêntico já existir ou não
            se for falso, precisa usar try/except quando for usar essa função
        
        ensure_parents:
            se for verdadeiro, cria toda a estrutura de diretórios a partir do output_directory
            se for falso e o diretório não existir, dá erro
    """

    # garante que o título é válido pra ser o nome de um arquivo
    try:
        pathvalidate.validate_filename(title)
    except pathvalidate.ValidationError:
        logger.error('o título contém caracteres inválidos para a criação de um arquivo')
        return

    # validar e construir o path do arquivo final
    if not ensure_parents:
        if not output_directory.exists() or not output_directory.is_dir():
            logger.error('o caminho final deve ser um diretório')
            return
    else:
        # criar o diretório se ele não existir
        output_directory.mkdir(exist_ok=True, parents=True)

    file = output_directory / title
    file = generic.normalize_json_file(file)

    if not force_overwrite and file.exists():
        raise CollectionAlreadyExists(f'Could not create collection at {file}. Something already exists there')
    
    # estruturar os dados e escrever o arquivo
    # description só é adicionado se estiver presente
    data = {
        'id': generic.generate_random_id(),
        'created-at': generic.get_iso_datetime(),
        'entries': []
    }
    if description is not None:
        data['description'] = description

    write_file(file=file, data=data)
    logger.success(f'collection criada com sucesso: {file}')

def insert_entry(
    collection: Path,
    entry_id: str,
    entry_type: str | None = None,
    entry_service: str | None = None,
    presence_verification: bool = True
    ):
    """
    adiciona uma nova entrada dentro da collection informada

    args:
        collection:
            caminho do arquivo da collection onde inserir
        
        entry_id:
            id do CONTEÚDO da entry. isso não é um id aleatório
            é o id que é usado pra reconstruir a url da entrada depois
            ex: se uma entrada se referir ao vídeo 'youtube.com/watch?v=erb4n8PW2qw'
                ela deve ter o id como 'erb4n8PW2qw'
        
        entry_type:
            tipo da mídia inserida
            ex: video, post, profile, community etc.

        entry_service:
            serviço a qual a entrada pertence
            ex: reddit, youtube etc.

            se for nulo, se considera que é uma url genérica da web
        
        presence_verification:
            verifica se a entrada já existe pra evitar duplicação
    """

    data = read_file(collection)
    if presence_verification:
        if utils.is_entry_present(data, entry_id):
            logger.info('o item já está presente na collection de destino')
            return
    
    entry = {
        'id': entry_id,
        'inserted-at': generic.get_iso_datetime(),
    }
    if entry_type:
        entry['type'] = entry_type
    if entry_service:
        entry['service'] = entry_service

    data['entries'].append(entry)
    write_file(collection, data)
    logger.success(f'entrada {entry_id} adicionada em {collection}')

def remove_entry(
    collection: Path,
    entry_id: str
    ):
    """
    remove uma entrada específica de uma collection
    NÃO remove duplicatas, só a primeira ocorrência do id passado pra função

    args:
        collection:
            caminho da collection onde remover a entrada
    
        entry_id:
            id da entrada que deve ser removida
    """

    data = read_file(collection)
    entries = data.get('entries')
    
    for e in entries:
        if e.get('id') == entry_id:
            entries.remove(e)
            write_file(collection, data)
    
            logger.info(f'entrada {entry_id} removida de {collection}')
            return # não continua procurando depois da primeira ocorrência
        
    logger.info(f'entrada {entry_id} não encontrada em {collection}')

def move_entry(
    src_collection: Path,
    dest_collection: Path,
    entry_id: str,
    presence_verification: bool = True
    ):
    """
    transfere uma entrada entre duas collections

    args:
        src_collection:
            collection onde a entrada está originalmente
    
        dest_collection:
            collection onde a entrada deve ser inserida
    
        entry_id:
            id da entrada a ser movida
    
        presence_verification:
            impede de mover se a entrada já existe no destino
    """

    data_src = read_file(src_collection)
    data_dest = read_file(dest_collection)

    if not data_src or not data_dest:
        logger.error('alguns dados são inválidos')
        return

    if presence_verification:
        if utils.is_entry_present(data_dest, entry_id):
            logger.info('o item já está presente na collection de destino')
            return

    for e in data_src.get('entries'):
        _id = e.get('id') # definido aqui pra não precisar repetir dentro do if
        
        if _id == entry_id:
            # ao encontrar o item com o mesmo id do alvo de moção,
            # obter os outros dados que são necessários pra mover ele de uma collection pra outra
            _type = e.get('type')
            _service = e.get('service')

            # se esse for tá rodando, é pq ele passou pela verificação do início dessa func,
            # ou pq essa função foi explicitamente dita pra ignorar a verificação
            # nos dois cenários, verificar verificar de novo
            _verify = False

            insert_entry(
                collection=dest_collection, presence_verification=_verify,
                entry_id=_id, entry_type=_type, entry_service=_service
            )
            remove_entry(collection=src_collection, entry_id=_id)
            logger.info(f'entrada {entry_id} movida de {src_collection} para {dest_collection}')

    logger.info(f'entrada {entry_id} não encontrada em {src_collection}')

def read_file(file: Path) -> dict:
    """
    lê um arquivo de collection e retorna os dados como dicionário,
    se o caminho for inválido retorna um dicionário vazio

    args:
        file:
            caminho do arquivo json que deve ser lido
    """

    if not file.is_file():
        logger.error('o caminho a ser lido deve ser um arquivo')
        return {}

    with file.open('r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def write_file(file: Path, data: dict):
    """
    escreve o dicionário informado em um arquivo de collection
    pode ser tanto um arquivo inexistente quanto um existente
    
    geralmente não deve ser usado sozinho fora desse módulo
    porque os métodos que o utilizam já sabem como lidar de forma segura
    com dados de arquivos já existentes, como a insert_entry

    args:
        file:
            caminho do arquivo onde os dados serão gravados
    
        data:
            dados que serão escritos no arquivo
    """

    with file.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def delete_path_permanently(path: Path):
    """
    apaga permanentemente um arquivo ou diretório do disco 

    args:
        path:
            caminho a ser removido do disco
    """

    if not path.exists():
        logger.info(f'path não existe: {path}')
        return
    
    try:
        # usa pathlib pra deletar se for um arquivo
        # e shutil se for um diretório
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        
        logger.success(f'{path} deletado')
    except Exception as err:
        logger.error(f'erro ao deletar caminho: {err}')

def path_to_trash(path: Path, custom_trash: Path | None = None):
    """
    envia um caminho para a lixeira do sistema ou para
    uma lixeira personalizada especificada

    diferente do delete_path_permanently, os arquivos deletados
    usando esse método são recuperáveis

    args:
        path:
            arquivo ou diretório a ser movido para a lixeira
    
        custom_trash:
            diretório alternativo para a lixeira, se definido
    """

    if not path.exists():
        logger.info(f'path não existe: {path}')
        return

    if custom_trash is None:
        send2trash(str(path))
        logger.success(f'{path} movido pra lixeira')
    else:
        custom_trash.mkdir(parents=True, exist_ok=True)
        shutil.move(src=path, dst=custom_trash)

if __name__ == '__main__':
    try:
        create_collection(
            title='leros',
            output_directory=Path('./testei'),
            description='sarelos'
        )
    except CollectionAlreadyExists:
        pass

    this_coll = Path('./testei/leros.json')
    
    from .types import videos
    from ...services import youtube

    ytdl = youtube.instance_ytdl()

    url = 'https://www.youtube.com/watch?v=erb4n8PW2qw'
    _id = youtube.extract_youtube_video_id(url, ytdl)

    remove_entry(this_coll, _id)

    videos.insert_youtube_video(
        collection=this_coll,
        url=url,
        ytdl=ytdl
    )