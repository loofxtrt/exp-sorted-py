# ESSA VERSÃO AINDA MANTINHA A DESCRIÇÃO COMENTADA

from helpers import *

from rich.console import Console
from rich.table import Table
from rich import box # pra controlar a espessura das bordas das tabelas
from pathlib import Path
from loguru import logger
from yt_dlp import YoutubeDL
from datetime import datetime

def make_table(title: str):
    """
    cria uma tabela com o rich
    poderia ser feito só chamando o Table manualmente,
    mas unificando em uma função, o estilo das tabelas fica mais consistente
    """

    return Table(
        title=title,
        box=box.ROUNDED # remove a espessura grossa
    )

def view_directory(dir: Path):
    if not dir.is_dir():
        logger.error('o caminho não é um diretório')
        return

    # criação da tabela
    table = make_table(dir.name)
    
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

def view_playlist(playlist_file: Path):
    data = yaml_read_playlist(playlist_file)

    # tabela com um título equivalente ao nome do arquivo, mas sem extensão
    table = make_table(playlist_file.stem)

    table.add_column('Title')
    table.add_column('Uploader')
    table.add_column('Views')
    table.add_column('Upload date')
    #table.add_column('Description')

    # definir as opções do ytdl
    ytdl_opts = {
        'quiet': True,
        'skip_download': True
    }

    for url in data['urls']:
        # pra cada urls presente no arquivo, obter as informações do vídeo
        # usando as opções previamente definidas
        # o download do vídeo em si é ignorado
        with YoutubeDL(ytdl_opts) as ytdl:
            info = ytdl.extract_info(url, download=False)

        # juntar o título e a descrição (truncada) em uma única célula
        # [dim] faz a desc ficar com a cor mais fraca
        title = info.get('title')
        description = info.get('description')[0:30]

        title_desc = f'[bold]{title}[/bold]\n[dim]{description}[/dim]'

        # formatar a data de upload
        # ela originalmente vem como 20251024
        # isso converte ela pra um objeto de datetime, depois de volta pra string reformatada
        upload_date = info.get('upload_date')
        upload_date = datetime.strptime(upload_date, '%Y%m%d').strftime('%Y-%m-%d')

        # criar um row na tabela com essas informações
        table.add_row(
            title_desc,
            info.get('uploader'),
            str(info.get('view_count')),
            upload_date
        )

    console = Console()
    console.print(table)