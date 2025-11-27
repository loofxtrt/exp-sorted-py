from pathlib import Path

from ... import logger
from ...utils import json_io

def get_file_from_id(collection_id: str, base_directory: Path) -> None | Path:
    if not base_directory.is_dir():
        return
    
    for file in base_directory.rglob('*.json'):
        try:
            data = read_file(file)
        except Exception:
            continue
        
        if data.get('id') == collection_id:
            return file
    
    return None

def get_title(file: Path) -> str:
    # o título de uma collection é o nome do arquivo sem a extensão
    return file.stem

def get_entry_count(data: dict) -> int:
    """
    retorna o número de dicionários presentes na lista de entries
    como fallback, usa uma lista vazia
    """
    
    return len(data.get('entries', []))

def is_entry_present(
    entry_data: dict,
    collection_data: dict,
    type_strictive: bool = True
    ) -> bool:
    """
    quando presence_verification for verdadeiro,
    a verificação impede duplicatas com base em dois critérios possíveis:

    1. se a entrada ter a chave 'url'
        geralmente significa que ela não é atrelada a um serviço específico,
        sendo um registro genérico de qualquer página da web

    2. se não tiver 'url', mas tiver 'service-metadata`
        significa que a url é atrelada a um serviço específico
        verifica usando o 'service-name' e o 'resolvable-id'

        ex:
            a entrada pro vídeo youtube.com/watch?v=erb4n8PW2qw
            possui o resolvable-id 'erb4n8PW2qw'
            e pertence ao service-name 'youtube'
    
    args:
        type_strictive:
            define se essa função deve considerar apenas se os metadados são iguais
            e desconsiderar o tipo do conteúdo, ou também incluir ele na verificação
            
            isso, em uma situação hipotética não tão comum,
            pode previnir que um vídeo do youtube e uma playlist com o mesmo id
            não sejam tratados como idênticos, por causa da diferença dos tipos

            desativar isso faz a função retornar o valor mais cedo,
            mas com a possibilidade desse erro acontecer
    """

    media_type = entry_data.get('type')
    url = entry_data.get('url')
    service_metadata = entry_data.get('service-metadata')
    
    # após obter os dados da entrada atual, começa a verificar as existentes
    existing_entries = collection_data.get('entries', [])
    for existing in existing_entries:
        existing_type = existing.get('type')
        
        if url is not None:
            # se a entrada atual tiver uma url, compara com a existente
            if existing.get('url') == url:
                logger.debug('url igual encontrada')
                
                if not type_strictive:
                    return True
                
                if existing_type == media_type:
                    return True
        elif service_metadata is not None:
            # se a entrada atual tiver metadados de serviço, indicando que ela não é genérica
            # isso considera id e serviço, os dois têm que ser iguais

            # dados da entry existente pra comparar com os da atual
            #
            # a verificação se ela tem ou não metadados de serviço é feita aqui
            # porque isso já descarta a possibilidade dela ser igual a entry atual
            # fazendo a função poder ignorar ela mais cedo
            existing_metadata = existing.get('service-metadata')
            if not existing_metadata:
                continue
            existing_service = existing_metadata.get('service-name')
            existing_id = existing_metadata.get('resolvable-id')

            # dados da entry atual
            service_name = service_metadata.get('service-name')
            resolvable_id = service_metadata.get('resolvable-id')

            if existing_id == resolvable_id and existing_service == service_name:
                logger.debug('metadados de serviço iguais encontrados')
                
                if not type_strictive:
                    return True
                
                if existing_type == media_type:
                    return True

    return False

def get_entry_data_by_id(collection_data: dict, entry_id: str) -> dict | None:
    """
    obtém os dados de uma entrada pelo id dela

    args:
        collection_data:
            a collection onde a entrada deve ser procurada
        
        entry_id:
            o id da entrada que possui os dados a serem retornados
    """

    entries = collection_data.get('entries')
    for e in entries:
        if e.get('id') == entry_id:
            return e
    
    return None

def data_collection_type_matches(media_type: str, collection_data: dict) -> bool:
    return media_type == collection_data.get('type')

def file_collection_type_matches(media_type: str, collection_file: Path) -> bool:
    data = read_file(collection_file)
    return data_collection_type_matches(media_type, data)

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
