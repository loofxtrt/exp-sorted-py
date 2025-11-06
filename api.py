# python3 api.py
# dps abre o html no navegador
# http://127.0.0.1:5000

import cache
import helpers
import settings as stg
from flask import Flask, jsonify
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app)

def get_playlist_file(playlist_id: str):
    # não faz parte da api, é só um wrapper
    return helpers.get_playlist_file_by_id(
        playlist_id=playlist_id,
        directory=Path('./tests')
    )

@app.route('/video/<video_id>', methods=['GET'])
def get_video(video_id: str):
    data = cache.get_cached_video_info(
        video_id=video_id,
        cache_file=stg.Settings().video_cache_file
    )

    response = {
        'url': helpers.build_youtube_url(video_id),
        'title': data.get('title'),
        'uploader': data.get('uploader'),
        'view_count': data.get('view_count'),
        'upload_date': data.get('upload_date'),
        'duration': data.get('duration'),
        'thumbnail': data.get('thumbnail'),
        'description': data.get('description')
    }

    return jsonify(response)

@app.route('/playlist/data/<playlist_id>', methods=['GET'])
def get_playlist_data(playlist_id: str):
    file = get_playlist_file(playlist_id)
    data = helpers.json_read_playlist(file)

    response = {
        'full_path': str(file.resolve()), # inclui o path inteiro
        'title': helpers.get_playlist_title(file), # também incluir o título da playlist na resposta
        'entries': data.get('entries'),
        'created_at': data.get('created-at'),
        'last_modified_at': data.get('last-modified-at'),
        'id': data.get('id')
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)