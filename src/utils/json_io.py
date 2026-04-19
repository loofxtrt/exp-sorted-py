from pathlib import Path
import json

from .. import logger

def read_json(file: Path) -> dict:
    """
    lê um arquivo json e retorna seu conteúdo como dicionário
    se o arquivo não existir ou estiver vazio/inválido, retorna um dict vazio

    args:
        file:
            caminho do arquivo json a ser lido

    returns:
        dicionário com o conteúdo do json ou {} em caso de falha
    """

    if not file.is_file():
        return {}

    try:
        with file.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        logger.info(f'{file} provavelmente estava vazio. um objeto vazio foi criado')
        return {}
    except Exception as err:
        logger.error(f'{file} erro ao ler o arquivo. um objeto vazio foi criado')
        return {}

def write_json(file: Path, data: dict):
    """
    escreve um dicionário em um arquivo json
    sobrescreve o conteúdo do arquivo caso ele já exista

    args:
        file:
            caminho do arquivo onde os dados serão salvos

        data:
            dicionário que pra ser serializado em json
    """

    try:
        with file.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as err:
        logger.error(f'{file} erro ao escrever o arquivo')