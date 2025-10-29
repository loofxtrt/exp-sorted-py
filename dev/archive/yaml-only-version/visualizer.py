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
        box=box.ROUNDED, # remove a espessura grossa
        border_style='dim' # bordas mais fracas
    )

def truncate_text(text: str, max_characters: int):
    if len(text) > max_characters:
        # se o texto passado for realmente maior do que o permitido,
        # corta os caracteres do índice 0 até o limite e adiciona um sinalizador no final (ex: ...)
        # é a mesma coisa que [0:max_chars], mas com o 0 omitido
        text = text[:max_characters - 3] + '...'

    return text

def make_video_row(
        target_table: Table,
        url: str,
        ytdlp_options: dict,
        include_description: bool = False,
        truncate_title: bool = True,
        truncate_desc: bool = True,
        title_max: int = 120,
        desc_max: int = 100
    ):
    """
    @param target_table:
        a tabela em que o novo row vai ser inserido

    @param url:
        url do vídeo que deve ter suas informações exibidas
    
    @param ytdlp_options:
        opções da api do yt-dlp

    @param include_description:
        se a descrição deve ou não ser incluída na visualização
        caso seja true, pode ficar com informações demais na tabela, por isso é false por padrão
    
    @param truncate_title:
        define se o título vai ou não ser truncado caso seja muito grande
    
    @param truncate_desc:
        define se a descrição vai ou não ser truncada caso seja muito grande
    
    @param title_max:
        quantos caracteres o título pode ter antes de ser truncado
    
    @param desc_max:
        quantos caracteres a descrição pode ter antes de ser truncada
    """

    # obter as informações do vídeo usando as opções previamente definidas
    # o download do vídeo em si é ignorado
    with YoutubeDL(ytdlp_options) as ytdl:
        info = ytdl.extract_info(url, download=False)

    title = info.get('title')
    upload_date = info.get('upload_date')
    uploader = info.get('uploader')
    view_count = str(info.get('view_count'))

    # formatar o título
    if truncate_title:
        title = truncate_text(title, title_max)

    # formatar a descrição
    if include_description:
        # se optar por mostrar a descrição, juntar o título e ela (truncada, por padrão) em uma única célula
        # [dim] faz a desc ficar com a cor mais fraca
        description = info.get('description')
        if truncate_desc:
            description = truncate_text(description, desc_max)

        # unir os dois
        title = f'{title}\n[dim]{description}[/dim]'

    # formatar a data de upload
    # ela originalmente vem como 20251024
    # isso converte ela pra um objeto de datetime, depois de volta pra string reformatada
    upload_date = datetime.strptime(upload_date, '%Y%m%d').strftime('%Y-%m-%d')

    # adicionar as informações finais a tabela em um novo row
    target_table.add_row(
        title,
        uploader,
        view_count,
        upload_date
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
        #if f.suffix not in ('.yml', '.yaml'):
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

def view_playlist(playlist_file: Path, description_flag: bool = False):
    """
    visualiza em detalhes uma playlist individual, exibindo quais vídos estão nela

    @param description_flag:
        se a descrição deve ou não ser incluída na visuazaliação
    """

    data = yaml_read_playlist(playlist_file)

    # tabela com um título equivalente ao nome do arquivo, mas sem extensão
    table = make_table(playlist_file.stem)

    table.add_column('Title')
    table.add_column('Uploader')
    table.add_column('Views')
    table.add_column('Upload date')

    # definir as opções do ytdl
    ytdl_opts = {
        'quiet': True,
        'skip_download': True
    }

    for url in data['urls']:
        # pra cada url presente no arquivo, criar um row na tabela com essas informações
        make_video_row(table, url, ytdl_opts, include_description=description_flag)

    console = Console()
    console.print(table)