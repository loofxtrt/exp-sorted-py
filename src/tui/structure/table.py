from pathlib import Path

from textual.widgets import DataTable, Label, Input
from textual.containers import Vertical, Horizontal

from ...utils import formatting
from ...managers import cache

def update_collection_table(
    table: DataTable,
    collection_data: dict,
    cache_file: Path
    ):
    # limpar a tabela antes de carregar
    table.clear(True)

    # adicionar as colunas
    table.add_column( # pra verificar o estado de seleção dos rows
        ' ',
        key='selection-status',
    )

    table.add_columns( # colunas gerais
        'Title',
        'Uploader',
        'Duration',
        'View count',
        'Upload date'
    )

    # adicionar as entradas, lendo a collection e obtendo os dados pelo cache
    for e in collection_data.get('entries'):
        #entry_id = e.get('id')
        service_metadata = e.get('service-metadata')
        entry_id = service_metadata.get('resolvable-id')
        data = cache.get_cached_entry_data(resolvable_id=entry_id, cache_file=cache_file)

        insert_entry_row(
            entry_data=data,
            entry_id=entry_id, # pra seleção posterior dos rows
            table=table
        )

def insert_entry_row(
    entry_data: dict,
    entry_id: str,
    table: DataTable
    ):
    title = entry_data.get('title')
    upload_date = entry_data.get('upload_date')
    uploader = entry_data.get('uploader')
    view_count = entry_data.get('view_count')
    duration = entry_data.get('duration', 0) # valor em segundos. o 0 é um fallback caso esse campo não esteja presente

    # formatações
    upload_date = formatting.format_upload_date(upload_date)
    view_count = formatting.format_view_count(view_count)
    duration = formatting.format_duration(duration)

    # adicionar o row a tabela
    # não precisa de return pq a instância já é passada como argumento
    # a key é a key_row, usada pra identificar esse row, nesse caso, o id do vídeo
    table.add_row(' ', title, uploader, duration, view_count, upload_date, key=entry_id)