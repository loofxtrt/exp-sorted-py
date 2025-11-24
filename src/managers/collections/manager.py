from pathlib import Path
import json
import shutil

from send2trash import send2trash
import pathvalidate

from . import utils
from ... import logger
from ...utils import generic, json_io
from ...managers import settings

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

def insert_entry_generic(
    collection: Path,
    media_type: str,
    url: str
    ):
    data = {
        'type': media_type,
        'url': url
    }
    handle_entry_insertion(collection=collection, entry_data=data)

def insert_entry_service(
    collection: Path,
    media_type: str,
    resolvable_id: str,
    service_name: str
    ):
    data = {
        'type': media_type,
        'service-metadata': {
            'resolvable-id': resolvable_id,
            'service-name': service_name 
        }
    }
    handle_entry_insertion(collection=collection, entry_data=data)

def handle_entry_insertion(
    collection: Path,
    entry_data: dict,
    presence_verification: bool = True
    ):
    """
    adiciona uma nova entrada dentro da collection informada

    args:
        collection:
            caminho do arquivo da collection onde inserir
        
        entry_data:
            dados a serem escritos como uma nova entry

        presence_verification:
            verifica se a entrada já existe pra evitar duplicação
    """

    collection_data = read_file(collection)
    if not collection_data:
        logger.error(f'a collection {collection} não tem dados válidos')
        return
    
    if presence_verification:
        url = entry_data.get('url')
        service_metadata = entry_data.get('service-metadata')

        entries = collection_data.get('entries', [])
        if url is not None:
            for e in entries:
                if e.get('url') == url:
                    logger.info(f'{url} já está presente em {collection}')
                    return
        elif service_metadata is not None:
            service_name = service_metadata.get('service-name')
            resolvable_id = service_metadata.get('resolvable-id')
            
            for e in entries:
                s_md = e.get('service-metadata')
                n = s_md.get('service-name')
                ri = s_md.get('resolvable-id')

                if ri == resolvable_id and n == service_name:
                    logger.info(f'o id {resolvable_id} pertencente ao serviço {service_name} já está presente em  {collection}')
                    return 

    entry_data['id'] = generic.generate_random_id()
    entry_data['inserted-at'] = generic.get_iso_datetime()

    collection_data['entries'].append(entry_data)
    write_file(collection, collection_data)

    logger.success(f'entrada {entry_data} adicionada em {collection}')

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
    
            logger.success(f'entrada {entry_id} removida de {collection}')
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

def read_file(file: Path) -> dict | None:
    """
    lê um arquivo de collection e retorna os dados como dicionário,
    se o caminho for inválido retorna um dicionário vazio

    args:
        file:
            caminho do arquivo json que deve ser lido
    """

    if not file.is_file():
        logger.error('o caminho a ser lido deve ser um arquivo')
        return

    return json_io.read_json(file)

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

    json_io.write_json(file=file, data=data)

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

# TESTES
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
    from ...services import youtube#, reddit

    ytdl = youtube.instance_ytdl()

    url = 'https://www.youtube.com/watch?v=erb4n8PW2qw'

    remove_entry(this_coll, 'QGtnv_pc')

    videos.insert_youtube_video(
        collection=this_coll,
        url=url,
        ytdl=ytdl
    )