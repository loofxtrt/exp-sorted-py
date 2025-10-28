# python3 api.py + node javascript/test.js

import cache
from flask import Flask, jsonify

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)