from utils import generic

def create_article_list():
    data = {
        'id': generic.generate_random_id(),
        'type': 'article-list',
        'created-at': generic.get_iso_datetime(),
        'entries': []
    }