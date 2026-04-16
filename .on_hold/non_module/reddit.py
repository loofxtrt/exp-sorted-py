import requests
import time

from .. import logger
from ..managers import settings
from ..utils import json_io

def jsonify_reddit_url(url: str, include_about: bool = False) -> str:    
    # remover a barra do final da url se ela estiver presente
    if url.endswith('/'):
        url = url.rstrip('/')

    # incluir o /about no final da url
    # isso geralmente é útil pra obter informações mais específicas sobre subreddits
    if include_about:
        if url.endswith('.json'):
            url = url.rstrip('.json')

        url += '/about'

    # adicionar a extensão no final da url, que dá acesso aos dados
    # do conteúdo que ela comporta
    if not url.endswith('.json'):
        url += '.json'
    
    return url

def prefix_subreddit(subreddit_name: str) -> str:
    """
    adiciona r/ na frente do nome de um subreddit. o nome passado pra essa função
    deve ser o nome real do subreddit, não o nome de display
    """

    if not subreddit_name.startswith('r/'):
        subreddit_name = f'r/{subreddit_name}'
    
    return subreddit_name

def get_post_info(url: str, retries: int = 3):
    url = jsonify_reddit_url(url)

    for attempt in range(retries):
        # fazer a requisição pro json do post e converter os dados pra json
        response = requests.get(url).json()

        # as vezes, em vez de responder um array (o esperado), vem um outro tipo
        # isso pode acontcer por erros tipo too many requests ou forbidden
        # antes de tentar de novo, espera alguns segundos pra api não sobrecarregar
        if isinstance(response, list):
            break

        logger.warning('erro inesperado ao acessar o post. tentando novamente')
        time.sleep(3)

        return get_post_info(url)
    else:
        logger.error('não foi possível obter as informações do post')
        return
    
    # os dados que interessam ficam na estrutura: index -> data -> children -> index -> data
    data = response[0]['data']['children'][0]['data']

    # organizar os dados num formato melhor pra uso
    data = {
        'id': data.get('id'),
        'subreddit': data.get('subreddit'),
        'author': data.get('author'),
        'title': data.get('title'),
        'selftext': data.get('selftext'),
        'archived': data.get('archived'),
        'score': data.get('score'),
        'thumbnail': data.get('thumbnail'),
        'post-flair': {
            'text': data.get('link_flair_text'),
            'background-color': data.get('link_flair_background_color')
        },
        'author-flair': {
            'text': data.get('author_flair_text'),
            'background-color': data.get('author_flair_background_color')
        },
        'created-utc': data.get('created_utc')
    }

    return data

def get_subreddit_info(url: str):
    url = jsonify_reddit_url(url, include_about=True)

    response = requests.get(url)
    response = response.json()

    data = response.get('data')

    data = {
        'title': data.get('title'),
        'display-name': data.get('display_name'),
        'description': data.get('description'),
        'created-utc': data.get('created_utc'),
        'subscribers': data.get('subscribers')
    }

    return data

# tem flair no post mas não no usuário
#get_post_info('https://www.reddit.com/r/unixporn/comments/1p0z2ki/just_be_consistent_brutal_hyprland/')

# tem flair no post e no usuário
#get_post_info('https://www.reddit.com/r/Clamworks/comments/1p0kcrr/clamtube/')











# settings._load()
# cache_reddit_posts = settings.get_cache_file('reddit', 'posts')

# data = get_post_info('https://www.reddit.com/r/Clamworks/comments/1p0kcrr/clamtube/')
# post_id = data.pop('id')

# cache = json_io.json_read_cache(cache_reddit_posts)
# already = cache.get(post_id)

# if not already:
#     cache[post_id] = data
#     json_io.json_write_cache(cache, cache_reddit_posts)
# else:
#     logger.info(f'pulando salvamento de dados. o post já está no cache')