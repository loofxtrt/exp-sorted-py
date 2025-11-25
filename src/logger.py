from rich.console import Console
from rich.text import Text
from rich.markup import escape
from rich.panel import Panel

def message_formatter(message, level: str = 'info', mode: str = 'panel', shorten: bool = True):
    lvl_colors = {
        'warning': 'yellow',
        'info': 'blue',
        'debug': 'green',
        'error': 'red',
        'critical': 'red',
        'success': 'green'
    }

    lvl_shorts = {
        'warning': 'warn',
        'info': 'info',
        'debug': 'dbug',
        'error': 'erro',
        'critical': 'crit',
        'success': 'okay'
    }

    # formatar o indicador de level
    # passa pra lowercase pra previnir erros
    level = level.lower()

    # usa o level passado pra essa função pra obter a cor do indicador dele
    color = lvl_colors.get(level, 'blue')
    
    # se especificado, também encurta o nome do level
    if shorten:
        level = lvl_shorts.get(level)
    
    # na hora de imprimir, sempre mostra o level em uppercase
    level = level.upper()

    # iniciar a formatação da mensagem
    # escape é usado pra que o rich não reconheça caracteres do texto como parte da formatação
    # str é usado pra garantir que qualquer coisa seja printável
    message = escape(str(message))
    formatted = Text()

    # se a mensagem tiver mais de uma linha, tratar essas linhas extras
    lines = message.splitlines()
    
    if len(lines) > 0:
        # adicionada separada pra não ter quebra de linha extra no começo
        formatted.append(lines[0])

        # verifica as demais linhas, começando do índice 1
        # pq o índice zero já foi adicionado como primeira linha
        for l in lines[1:]:
            formatted.append(f'\n{l}')

    # imprimir o logger formatado
    printable = None
    if mode == 'panel':
        # o modo painel usa o panel do rich
        panel = Panel(
            formatted,
            title=level,
            title_align='left',
            border_style=color
        )

        printable = panel
    else:
        # qualquer outro modo diferente do panel é considerado
        # como texto puro, então ele é formatado como um log convencional
        #
        # nesse modo, também deixa o indicador do level em negrito
        # além de adicionar uma separação entre o level e o texto
        handle_color = color + ' bold'
        level_display = Text(level, handle_color)
        
        text = Text()
        text.append(level_display)
        text.append(' | ')
        text.append(formatted)

        printable = text

    console = Console()
    console.print(printable)

def warning(message):
    message_formatter(message=message, level='warning')

def error(message):
    message_formatter(message=message, level='error')

def info(message):
    message_formatter(message=message, level='info')

def success(message):
    message_formatter(message=message, level='success')

def debug(message):
    message_formatter(message=message, level='debug')

def critical(message):
    message_formatter(message=message, level='critical')