import shutil
import platform

import pyperclip

def has_clipboard_support() -> bool:
    """
    verifica se o sistema possui suporte à clipboard

    obtém o nome do sistema e verifica o software que ele usa pra esse tipo de ação
    no linux pode variar dependendo se for wayland e x11,
    mas no windows e macos geralmente são sempre os mesmos
    """

    system = platform.system().lower()

    if system == 'linux':
        # xclip e xsel -> x11
        # wl-copy -> wayland
        if not (shutil.which('xclip') or shutil.which('xsel') or shutil.which('wl-copy')):
            return False
    elif system == 'windows':
        if shutil.which('clip') is None:
            return False
    elif system == 'darwin': # macos
        if shutil.which('pbcopy') is None:
            return False
    else:
        return False
    
    return True