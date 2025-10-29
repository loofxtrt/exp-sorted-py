const videoId = '3onlW9wKxVc';

fetch(`http://127.0.0.1:5000/video/${videoId}`)
    .then(response => response.json())
    .then(data => {
        console.log(data.title)
    });