const API_ADDRESS = 'http://127.0.0.1:5000';
const playlistId = 'xKFHDg6h';

async function loadPlaylist(playlistId) {
    // requisitar os dados da playlist pra api
    const response = await fetch(`${API_ADDRESS}/playlist/data/${playlistId}`);
    const data = await response.json();
    
    // obter separadamente os dados retornados
    const title = data.title;
    const entries = data.entries;
    
    // adicionar os ids de cada entrada de vídeo num array
    let videoIds = [];
    entries.forEach(entry => {
        let id = entry.id;
        videoIds.push(id);
    });
    
    // atualizar o html com os dados
    updateHtml(title, videoIds);
}

function updateHtml(playlistTitle, videoIds) {
    // mudar o conteúdo do título pro título da playlist
    const titleElement = document.querySelector('#playlist-title');
    titleElement.textContent = playlistTitle;

    // criar um elemento de vídeo pra cada id passado pra essa func
    // e adicionar o elemento criado a lista de vídeos visual da playlist
    const videoList = document.querySelector('#video-list');
    
    videoIds.forEach(id => {
        const videoItem = document.createElement('div')
        videoItem.classList.add('video-item');
        videoItem.innerHTML = `
        <img src="../placeholders/sddefault.jpg" alt="video thumbnail" class="video-thumbnail">
        
        <div class="video-info">
            <p class="title">Entregando ÁGUA e TOMANDO SUSTO 💧 Water Delivery</p>
            
            <div class="sub-info faint">
                <div>
                    <span class="view-count">50K views</span>
                    <span>•</span>
                    <span class="upload-date">Dec 30, 2024</span>
                </div>

                <p class="uploader">Felps LIVE</p>
            </div>
        </div>
        `;

        videoList.appendChild(videoItem);
    });
}

loadPlaylist(playlistId);