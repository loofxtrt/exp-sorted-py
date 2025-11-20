from pathlib import Path
import logger
import random
import string

def truncate_text(text: str, max_characters: int):
    if len(text) > max_characters:
        # se o texto passado for realmente maior do que o permitido,
        # corta os caracteres do índice 0 até o limite e adiciona um sinalizador no final (ex: ...)
        # é a mesma coisa que [0:max_chars], mas com o 0 omitido
        text = text[:max_characters - 3] + '...'

    return text

def get_iso_datetime():
    # yyyy-mm-ddThh:mm:ss. o timespec é pra não incluir microsegundos
    return datetime.now().isoformat(timespec='seconds')

def generate_random_id(id_length: int = 8):
    """
    gera um id usando todas as letras, numeros e alguns caracteres especiais
    """

    # obter uma string com todas as letras do alfabeto (upper e lower)
    # todos os digitos numéricos (0-9)
    # underscore (_) e hífen (-)
    characters = string.ascii_letters + string.digits + '-' + '_'

    # criar um id, atribuindo um índice aleatório do grupo de caracteres
    # até que o comprimento total do id seja preenchido
    final_id: str = ''
    for i in range(id_length):
        final_id += random.choice(characters)

    logger.debug('novo id gerado: ' + final_id)
    return final_id

def normalize_json_file(path: Path | str):
    # adicionar a extensão no caminho
    normalized = str(path)
    if not normalized.endswith('.json'):
        normalized += '.json'
    
    # transformar o valor normalizado de volta em path
    # caso esse tenha sido o formato passado pra essa função inicialmente
    # ela deve apenas normalizar, não mudar o tipo
    if isinstance(path, Path):
        normalized = Path(normalized)

    return normalized

def confirm(prompt: str, default: bool = False, assume_default: bool = False):
    """
    exibe um prompt de sim ou não pro usuário

    args:
        prompt:
            texto a ser exibido
    
        default:
            valor padrão de resposta. é destacado com uppercase na exibição do prompt
            se o usuário não responder nada, esse é o valor que vai ser usado

        assume_default:
            se for verdadeiro, faz o prompt ser completamente ignorado,
            retornando uma resposta positiva sem confirmação
    """

    if assume_default:
        return True
    
    # construir e mostrar o input
    # a opção padrão é mostrada em uppercase, enquanto a não-padrão é lowercase
    display = '(Y/n)' if default == True else '(y/N)'
    answer = input(f'{prompt} {display} ').strip().lower()
    
    # retornar o valor padrão caso só aperte enter e não especifique nada
    if not answer:
        return default

    # se teve resposta, retornar se ela foi 'sim' ou o oposto
    return answer == 'y'