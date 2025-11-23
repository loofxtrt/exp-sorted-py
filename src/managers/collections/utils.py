from pathlib import Path

from .manager import read_file

def get_file_from_id(collection_id: str, base_directory: Path) -> None | Path:
    if not base_directory.is_dir():
        return
    
    for coll in base_directory.rglob('*.json'):
        try:
            data = read_file(coll)
        except Exception:
            continue
        
        if data.get('id') == collection_id:
            return coll
    
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

def is_entry_present(data: dict, target_id: str):
    """
    verifica se há pelo menos uma ocorrência do target_id dentro dos dicionários presentes em entries
    esses dicionários sempre têm o campo 'id', o que faz eles serem verificáveis
    """

    entries = data.get('entries', [])

    # any -> pelo menos uma ocorrência
    # for e in entries -> verificar todos os dicionários
    if any(e.get('id') == target_id for e in entries):
        return True
    
    return False