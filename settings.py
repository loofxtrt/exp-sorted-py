import json
from pathlib import Path

SETTINGS_DIRECTORY = Path.home() / '.config' / 'sorted' # INALTERÁVEL
SETTINGS_FILE = SETTINGS_DIRECTORY / 'settings.json' # INALTERÁVEL

class Settings:
    def __init__(self):
        # valores padrão (são sobreescritos pelo load)
        self.cache_directory = SETTINGS_DIRECTORY / 'cache'
        self.ytdl_options = {
            'quiet': True,
            'skip_download': True,
        }
    
    def load(self):
        try:
            # abrir o arquivo de configuração e sobreescrever as variáveis dessa classe
            # com os valores encontrados no arquivo. se não encontrar nenhum, só reseta pro padrão
            with SETTINGS_FILE.open('r', encoding='utf-8') as f:
                data = json.load(f)

                # tem que ter str(self.) pq logo dps é convertido de volta pra path
                get_cache = data.get('cache-directory', str(self.cache_directory))
                self.cache_directory = Path(get_cache)

                get_ytdl = data.get('ytdl-options', self.ytdl_options)
                self.ytdl_options = get_ytdl
        except FileNotFoundError:
            # criar um arquivo de configuração padrão se não conseguir abrir
            self.reset_or_set()

    def reset_or_set(self):
        # redefine explicitamente os valores padrão
        default_cache = SETTINGS_DIRECTORY / 'cache'
        default_ytdl = {
            'quiet': True,
            'skip_download': True,
        }

        # atualiza essa instância da classe com os valores padrão
        self.cache_directory = default_cache
        self.ytdl_options = default_ytdl

        # reseta o arquivo de configurações ao padrão
        # ou, se não existir, cria um arquivo de configuração novo
        write_settings(
            cache_directory=self.cache_directory,
            ytdl_options=self.ytdl_options
        )

    # todos os marcados com @property não precisam de () pra serem chamados
    # eles dependem de variáveis dinâmicas, que podem mudar,
    # por isso são definidos individualmente e não na __init__
    @property
    def video_cache_file(self):
        return self.cache_directory / 'videos.json'

def write_settings(cache_directory: Path, ytdl_options: dict):
    """escreve argumentos no arquivo de configuração"""
    # criar o dir de configurações caso ele não exista
    SETTINGS_DIRECTORY.mkdir(exist_ok=True, parents=True)

    settings = {
        'cache-directory': str(cache_directory),
        'ytdl-options': ytdl_options
    }

    with SETTINGS_FILE.open('w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)