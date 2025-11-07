const API_ADDRESS = 'http://127.0.0.1:5000';
const playlistId = 'DtVRqDNU';

function selectVideo() {
    let selectedCount = 0
    
    const countElement = document.querySelector('#selected-videos-count');
    countElement.textContent = selectedCount.toString();

    const selections = document.querySelectorAll('.selected')
    selections.forEach(s => {

        selectedCount++
        countElement.textContent = selectedCount.toString();
    });
}

async function loadPlaylist(playlistId) {
    // requisitar os dados da playlist pra api
    const response = await fetch(`${API_ADDRESS}/playlist/data/${playlistId}`);
    const data = await response.json();

    // obter separadamente os dados retornados
    const path = data.full_path;
    const title = data.title;
    const entries = data.entries;
    const lastModifiedAt = data.last_modified_at;
    const createdAt = data.created_at;

    // adicionar os ids de cada entrada de vídeo num array
    let videoIds = [];
    entries.forEach(entry => {
        let id = entry.id;
        videoIds.push(id);
    });

    // funcionalidades dos botões
    const moveSelectedElement = document.querySelector('#move-selected-videos');
    moveSelectedElement.addEventListener('click', () => {
        
    });

    // atualizar o html com os dados
    updateHtml(title, lastModifiedAt, createdAt, videoIds, path);
}

async function updateHtml(playlistTitle, lastModifiedAt, createdAt, videoIds, playlistPath) {
    // atualizar o caminho sendo exibido
    const pathElement = document.querySelector('#playlist-path');
    pathElement.value = playlistPath;

    // atualizar a thumbnail da playlist pra usar a mesma do primeiro vídeo
    const firstVideo = await fetch(`${API_ADDRESS}/video/${videoIds[0]}`);
    const firstVideoData = await firstVideo.json().then(data => { // obter os dados e então
        // extrai a thumbnail dos dados obtidos e atualiza a img
        const thumbnail = data.thumbnail;

        const playlistThumbnailElement = document.querySelector('#playlist-thumbnail')
        playlistThumbnailElement.src = thumbnail;
    });

    // atualizar os valores gerais da playlist
    const titleElement = document.querySelector('#playlist-title');
    titleElement.textContent = playlistTitle;

    const modifiedElement = document.querySelector('#playlist-last-modified-at');
    modifiedElement.textContent = lastModifiedAt;

    const createdElement = document.querySelector('#playlist-created-at');
    createdElement.textContent = createdAt;

    // criar um elemento de vídeo pra cada id passado pra essa func
    // e adicionar o elemento criado a lista de vídeos visual da playlist
    const videoList = document.querySelector('#video-list');

    for (id of videoIds) { // não dá pra usar foreach por causa do await
        const response = await fetch(`${API_ADDRESS}/video/${id}`);
        const data = await response.json();

        const url = data.url;
        const title = data.title;
        const viewCount = data.view_count;
        const uploadDate = data.upload_date;
        const uploader = data.uploader;
        const thumbnail = data.thumbnail;

        const videoItem = document.createElement('div')
        videoItem.classList.add('video-item');
        videoItem.innerHTML = `
        <img src="${thumbnail}" alt="video thumbnail" class="video-thumbnail">

        <div class="video-info">
            <p class="title">
                <a href="${url}" target="_blank">${title}</a>
            </p>

            <div class="sub-info faint">
                <div>
                    <span class="view-count">${viewCount} views</span>
                    <span>•</span>
                    <span class="upload-date">${uploadDate}</span>
                </div>

                <p class="uploader">${uploader}</p>
            </div>
        </div>
        `;

        // adicionar uma propriedade oculta que guarda o id do vídeo
        // serve principalmente pra lógica de seleções
        videoItem.dataset.videoId = id;

        // adicionar um event listener em todo vídeo
        // pra que ao clicar sobre ele, se adicione ou remova a classe 'selected'
        videoItem.addEventListener('click', () => {
            videoItem.classList.toggle('selected');
            selectVideo();
        });

        // adicionar o vídeo à lista visual
        videoList.appendChild(videoItem);
    };
}

loadPlaylist(playlistId);
