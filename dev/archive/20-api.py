# ESSA VERSÃO SEPARAVA O TÍTULO DOS OUTROS DADOS

# python3 api.py + node test.js

import cache
import helpers
from flask import Flask, jsonify
from pathlib import Path

app = Flask(__name__)

def get_playlist_file(playlist_id: str):
    return helpers.get_playlist_file_by_id(
        playlist_id=playlist_id,
        directory=Path('./tests')
    )

@app.route('/video/<video_id>', methods=['GET'])
def get_video(video_id: str):
    data = cache.get_video_info(video_id)

    response = {
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

    # também incluir o título da playlist na resposta
    data['title'] = helpers.get_playlist_title(file)

    return data

@app.route('/playlist/title/<playlist_id>', methods=['GET'])
def get_playlist_title(playlist_id: str):
    file = get_playlist_file(playlist_id)
    data = {'title': helpers.get_playlist_title(file)} # transforma em json mesmo sendo só uma string, pra ser parseavel
    
    return data

if __name__ == '__main__':
    app.run(debug=True)