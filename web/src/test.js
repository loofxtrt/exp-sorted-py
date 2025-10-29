const videoId = '3onlW9wKxVc';
const playlistId = 'xKFHDg6h';

const API_ADDRESS = 'http://127.0.0.1:5000';

fetch(`${API_ADDRESS}/video/${videoId}`)
    .then(response => response.json())
    .then(data => {
        console.log(data.title)
    });

fetch(`${API_ADDRESS}/playlist/title/${playlistId}`)
    .then(response => response.json())
    .then(data => {
        console.log(data.title)
    });
