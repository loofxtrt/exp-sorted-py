import cache
import helpers

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box # pra controlar a espessura das bordas das tabelas
from pathlib import Path
from loguru import logger
#from yt_dlp import YoutubeDL
from datetime import datetime, timedelta

# largura de todos os painéis do rich (sejam eles tabelas, paineis comuns etc.)
STANDARD_PANEL_WIDTH: int = 120

def make_table(title: str = None, width: int = STANDARD_PANEL_WIDTH):
    """
    cria uma tabela com o rich
    poderia ser feito só chamando o Table manualmente,
    mas unificando em uma função, o estilo das tabelas fica mais consistente
    """

    table = Table(
        box=box.ROUNDED, # remove a espessura grossa
        border_style='dim', # bordas mais fracas
    )

    # configurações posteriores
    # por ex, se width, mesmo vazio, fosse passado logo na criação, o comportamento de tamanho automático se perderia
    if width is not None:
        table.width = width
    
    if title is not None:
        table.title = title
    
    return table

def make_video_row(
        target_table: Table,
        video_id: str,
        include_description: bool = False,
        truncate_title: bool = True,
        truncate_desc: bool = True,
        title_max: int = 120,
        desc_max: int = 100
    ):
    """
    @param target_table:
        a tabela em que o novo row vai ser inserido

    @param video_id:
        id do vídeo que deve ter suas informações exibidas
    
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

    data = cache.get_video_info(video_id)
    if not data: return

    title = data.get('title')
    upload_date = data.get('upload_date')
    uploader = data.get('uploader')
    view_count = data.get('view_count')
    duration = data.get('duration', 0) # valor em segundos. o 0 é um fallback caso esse campo não esteja presente

    # formatar o título
    if truncate_title:
        title = helpers.truncate_text(title, title_max)

    # formatar a descrição
    if include_description:
        # se optar por mostrar a descrição, juntar o título e ela (truncada, por padrão) em uma única célula
        # [dim] faz a desc ficar com a cor mais fraca
        description = info.get('description')
        if truncate_desc:
            description = helpers.truncate_text(description, desc_max)

        # unir os dois
        title = f'{title}\n[dim]{description}[/dim]'

    # formatar os metadados numéricos
    upload_date = helpers.format_upload_date(upload_date)
    duration = helpers.format_duration(seconds=duration)
    view_count = helpers.format_view_count(view_count)

    # adicionar as informações finais a tabela em um novo row
    target_table.add_row(
        title,
        uploader,
        duration,
        view_count,
        upload_date
    )

def view_directory(directory: Path):
    """visualiza um diretório que contém múltiplas playlists"""
    
    if not directory.is_dir():
        logger.error('o caminho não é um diretório')
        return

    # criação da tabela
    table = make_table()
    
    table.add_column('Title')
    table.add_column('Video count')
    table.add_column('Creation date')
    table.add_column('ID')

    # verificar cada arquivo dentro do diretório e inserir os dados dele na tabela
    for f in directory.iterdir():
        if not f.is_file() or not f.suffix == '.json':
            continue
        
        # obter os dados da playlist e extrai-los
        data = helpers.json_read_playlist(f)
        title = f.stem
        video_count = str(len(data['entries']))
        creation_date = data['created-at']
        playlist_id = data['id']

        # adicionar um row na tabela contendo esses dados
        table.add_row(title, video_count, creation_date, playlist_id)

    console = Console()
    console.print(table)

def view_playlist(playlist_file: Path, show_description: bool = False):
    """
    visualiza em detalhes uma playlist individual, exibindo quais vídos estão nela

    @param show_description:
        se a descrição deve ou não ser incluída na visuazaliação
    """

    data = helpers.json_read_playlist(playlist_file)

    # tabela de todos os vídeos da playlists
    table = make_table()

    table.add_column('Title')
    table.add_column('Uploader')
    table.add_column('Duration')
    table.add_column('Views')
    table.add_column('Upload date')

    for video in data.get('entries'):
        # pra cada video presente no arquivo, criar um row na tabela com essas informações
        #video_id = helpers.extract_youtube_video_id(video.get('url'))
        video_id = video.get('id')
        make_video_row(table, video_id, include_description=show_description)

    # painel com informações extras da playlist sendo visualizada
    # contém lógica pra usar plural ou singular de 'vídeos' caso tenha menos ou mais de um
    video_count = len(data['entries'])
    contains = str(video_count) + ' ' + ('videos' if video_count > 1 else 'video')
    
    panel = Panel(
        f'Title: {playlist_file.stem}\nContains: {contains}',
        box=box.ROUNDED,
        border_style='dim',
        width=STANDARD_PANEL_WIDTH
    )

    # imprimir o resultado final
    console = Console()
    console.print(panel)
    console.print(table)