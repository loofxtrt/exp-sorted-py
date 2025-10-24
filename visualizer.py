from helpers import *

from rich.console import Console
from rich.table import Table
from rich import box # pra controlar a espessura das bordas das tabelas
from pathlib import Path
from loguru import logger

def view_directory(dir: Path):
    if not dir.is_dir():
        logger.error('o caminho não é um diretório')
        return

    # criação da tabela
    table = Table(
        title=dir.name,
        box=box.ROUNDED # remove a espessura grossa
    )
    
    table.add_column('Title')
    table.add_column('Video count')
    table.add_column('Creation date')
    table.add_column('ID')

    # verificar cada arquivo dentro do diretório e inserir os dados dele na tabela
    for f in dir.iterdir():
        if not f.is_file():
            continue
        
        # FIXME: isso tá ignorando todos os arquivos
        #if not f.suffix not in ('.yml', '.yaml'):
        #    # aqui se usa not in em vez de dois if not,
        #    # pq se o sufixo for yml, mas não yaml, vai dar falso e vice-versa
        #    # isso verifica se UM DOS DOIS é o sufixo 
        #    continue
        
        # obter os dados da playlist e extrai-los
        data = yaml_read_playlist(f)
        title = f.stem
        video_count = str(len(data['urls']))
        creation_date = data['created-at']
        playlist_id = data['id']

        # adicionar um row na tabela contendo esses dados
        table.add_row(title, video_count, creation_date, playlist_id)

    console = Console()
    console.print(table)