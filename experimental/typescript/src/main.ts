const API_ADDRESS = 'http://127.0.0.1:5000';
const playlistId = 'DtVRqDNU';

interface playlistEntry {
    id: string;
    insertedAt: string;
}

async function loadPlaylist(playlistId: string) {
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
    let videoIds: string[] = [];
    entries.forEach((entry: playlistEntry) => {
        let id = entry.id;
        videoIds.push(id);
    });
    
    // atualizar o html com os dados
    updateHtml(title, lastModifiedAt, createdAt, videoIds, path);
}

async function updateHtml(playlistTitle: string, lastModifiedAt: string, createdAt: string, videoIds: string[], playlistPath: string) {
    // atualizar o caminho sendo exibido
    const pathElement = document.querySelector('#playlist-path') as HTMLInputElement | null;
    if (pathElement) { pathElement.value = playlistPath; }

    // atualizar os valores gerais da playlist
    const titleElement = document.querySelector('#playlist-title');
    if (titleElement) { titleElement.textContent = playlistTitle; }

    const modifiedElement = document.querySelector('#playlist-last-modified-at');
    if (modifiedElement) { modifiedElement.textContent = lastModifiedAt; }

    const createdElement = document.querySelector('#playlist-created-at');
    if ( createdElement ) { createdElement.textContent = createdAt; }

    // criar um elemento de vídeo pra cada id passado pra essa func
    // e adicionar o elemento criado a lista de vídeos visual da playlist
    const videoList = document.querySelector('#video-list');
    if (!videoList) {
        return;
    }

    for (const id of videoIds) { // não dá pra usar foreach por causa do await
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

        videoList.appendChild(videoItem);
    };
}

loadPlaylist(playlistId);