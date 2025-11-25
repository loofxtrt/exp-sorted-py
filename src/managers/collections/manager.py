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
class InvalidCollectionData(Exception): pass
class EntryNotFound(Exception): pass

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

    utils.write_file(file=file, data=data)
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
    
    inserted = handle_entry_insertion(collection=collection, entry_data=data)
    return inserted

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

    inserted = handle_entry_insertion(collection=collection, entry_data=data)
    return inserted

def handle_entry_insertion(
    collection: Path,
    entry_data: dict,
    presence_verification: bool = True,
    ) -> dict | None:
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

    collection_data = utils.read_file(collection)
    if not collection_data:
        logger.error(f'a collection {collection} não tem dados válidos')
        return
    if presence_verification:
        if utils.is_entry_present(entry_data, collection_data):
            logger.info(f'a entrada já está presente em {collection}')
            return

    entry_data['id'] = generic.generate_random_id()
    entry_data['inserted-at'] = generic.get_iso_datetime()

    collection_data['entries'].append(entry_data)
    utils.write_file(collection, collection_data)

    logger.success(f'entrada {entry_data} adicionada em {collection}')

    # retorna os dados que acabou de criar pra função que a chamou
    # pode ser usado em situações onde o chamador tem que saber o id da entry, por exemplo
    return entry_data

def remove_entry(collection: Path, entry_id: str):
    """
    remove uma entrada específica de uma collection

    args:
        collection:
            caminho da collection onde remover a entrada
    
        entry_id:
            id da entrada que deve ser removida

            pelo id ser o da entrada e não um resolvable_id,
            NÃO remove duplicatas baseadas nos metadados delas
    """

    data = utils.read_file(collection)
    entries = data.get('entries')
    
    # percorre todas as entradas da collection
    # até achar uma com o id igual ao sendo alvo de deleção,
    # assim removendo da lista e atualizando o arquivo
    for e in entries:
        if e.get('id') == entry_id:
            entries.remove(e)
            utils.write_file(collection, data)
    
            logger.success(f'entrada {entry_id} removida de {collection}')
            return # não continua procurando depois da primeira ocorrência
        
    logger.info(f'entrada {entry_id} não encontrada em {collection}')

def move_entry(
    src_collection: Path,
    dest_collection: Path,
    entry_id: str,
    presence_verification: bool = True
    ) -> bool:
    """
    transfere uma entrada entre duas collections
    retorna um bool pra indicar se a moção foi bem ou mal sucedida

    args:
        src_collection:
            collection onde a entrada está originalmente
    
        dest_collection:
            collection onde a entrada deve ser inserida
    
        entry_id:
            id da entrada a ser movida
    
        presence_verification:
            impede de mover se a entrada já existir no destino
    """

    if src_collection == dest_collection:
        logger.info('as collections de destino e origem são as mesmas')
        return False

    # obter os dados das collections
    data_src = utils.read_file(src_collection)
    data_dest = utils.read_file(dest_collection)
    if not data_src or not data_dest:
        raise InvalidCollectionData(f'One or both of the collections are invalid:\n{src_collection}\n{dest_collection}')

    # obter a entrada em específico pelo id dela
    entry = utils.get_entry_data_by_id(data_src, entry_id)
    if not entry:
        raise EntryNotFound(f'{entry_id} not found in {src_collection}')
    if presence_verification:
        if utils.is_entry_present(data_dest, entry):
            logger.info('o item já está presente na collection de destino')
            return False

    # mover a entrada de uma collection pra outra
    handle_entry_insertion(dest_collection, entry, presence_verification)
    remove_entry(src_collection, entry_id)
        
    logger.success(f'entrada {entry_id} movida de {src_collection} para {dest_collection}')
    return True 

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

    try:
        create_collection(
            title='chinelo',
            output_directory=Path('./testei')
        )
    except CollectionAlreadyExists:
        pass

    this_coll = Path('./testei/leros.json')
    chinelo_coll = Path('./testei/chinelo.json')
    
    from .types import videos
    from ...services import youtube#, reddit

    ytdl = youtube.instance_ytdl()

    url = 'https://www.youtube.com/watch?v=erb4n8PW2qw'

    #remove_entry(this_coll, 'QGtnv_pc')

    #videos.insert_youtube_video(
    #    collection=this_coll,
    #    url=url,
    #    ytdl=ytdl
    #)
    move_entry(
        src_collection=this_coll,
        dest_collection=chinelo_coll,
        entry_id='uxPQcuH3'
    )