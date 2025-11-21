from utils import generic

def create_post_collection():
    data = {
        'id': generic.generate_random_id(),
        'type': 'posts',
        'created-at': generic.get_iso_datetime(),
        'entries': []
    }