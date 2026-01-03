from pathlib import Path

from textual.app import App
from textual.widgets import DataTable

from ..managers.collections import manager
from .structure import table

def move_entries(
    app: App,
    src_collection: Path,
    dest_collection: Path,
    selected_row_keys: list,
    collection_table: DataTable
    ) -> bool:
    if dest_collection == src_collection:
        app.notify(message='Destination is the same as the current playlist', severity='information')
        return

    # se a quantidade de vídeos selecionados seja válida, maior que 0
    if not len(app.selected_row_keys) > 0:
        app.notify(message='No videos selected', severity='warning')
        return

    # mover cada entry pra collection de destino
    # a variável de contagem serve pra logging/notificações
    moved_count = 0
    
    for row_key in selected_row_keys:
        entry_id = row_key.value # o id tá dentro da row_key, ele não é a row_key em si

        try:
            status = manager.move_entry(
                src_collection=src_collection, dest_collection=dest_collection,
                entry_id=entry_id
            )
            if not status:
                app.notify('Something went wrong while moving entries', severity='error')
                return False
        except manager.InvalidCollectionData:
            app.notify('Some collection for the moving action is invalid', severity='error')
            return False
        except manager.EntryNotFound:
            app.notify('Entry being moved was not found', severity='error')
            return False
        except manager.MismatchedCollectionType:
            app.notify('Destination and source collection types do not match', severity='error')
            return False

        selected_row_keys.remove(row_key) # remove da lista de selecionados
        collection_table.remove_row(row_key) # remove da tabela visual

        moved_count += 1

    if moved_count > 0:
        # usar plural se for mais de um vídeo e singular se for só um
        handle_plural = 'video' if moved_count == 1 else 'videos'
        app.notify(message=f'Sucessfully moved {moved_count} {handle_plural}')
    
    return True