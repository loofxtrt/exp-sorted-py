from dataclasses import dataclass

from . import utils


# TODO: em vez de uploader, deve ser o handler do canal


@dataclass
class Video:
    """
    representa um vídeo do youtube dentro do sistema

    essa classe serve como um modelo único pra padronizar os dados vindos da api
    e facilitar o uso deles no resto do código (cache, ui, etc)

    também inclui propriedades prontas pra formatar valores numéricos comuns
    """

    id: str
    title: str
    description: str
    uploader: str
    view_count: int
    duration: int
    upload_date: str
    like_count: int
    comment_count: int
    thumbnail: str
    thumbnails: list[dict]

    @property
    def view_count_formatted(self):
        return utils.format_count(self.view_count or 0)

    @property
    def duration_formatted(self):
        return utils.format_duration(self.duration or 0)
    
    @property
    def upload_date_formatted(self):
        return utils.format_upload_date(self.upload_date or 0)

    @property
    def like_count_formatted(self):
        return utils.format_count(self.like_count or 0)
        
    @property
    def comment_count_formatted(self):
        return utils.format_count(self.comment_count or 0)
    
    @staticmethod
    def normalize_ytdl_data(data: dict):
        """
        extrai e normaliza os dados crus vindos do youtube-dl

        o yt-dlp retorna muitos, então serve pra filtrar o que é
        realmente relevante nesse contexto 

        args:
            data:
                dados crus vindos do youtube-dl

        returns:
            dicionário normalizado no formato interno do sistema
        """

        # filtra as thumbnails mostrando só as relevantes
        # e que tenham mudança perceptível de tamanho/qualidade
        #
        # thumbnails que são só frames aleatórios do vídeo
        # ou que são só versões webp equivalentes a um png idêntico, não entram
        thumbnails = []
        for t in data.get('thumbnails'):
            url = t.get('url')
            resolution_name = None
            
            if '.webp' in url:
                continue

            if '/mqdefault' in url:
                resolution_name = 'mqdefault'
            # TODO: não mudar os dados da thumb, só adicionar get_thumbnail(res: mq)
            # maxres quase sempre é idêntico ao 'thumbnail' principal
            # elif '/maxresdefault' in url:
                # resolution_name = 'maxresdefault'
            # hq720 não tem diferença grande comparado ao maxres
            # na maioria das vezes, então por enquanto não precisa
            # elif '/hq720' in url:
            #     resolution_name = 'hq720'
            
            # se a thumbnail não teve a resolução identificada
            # com clareza, é melhor não inserir ela na lista final
            if resolution_name is None:
                continue
            
            thumbnails.append(
                {
                    'url': url,
                    'resolution_name': resolution_name
                }
            )

        return {
            'id': data.get('id'),
            'title': data.get('title'),
            'description': data.get('description'),
            'uploader': data.get('uploader'),
            'view_count': data.get('view_count'),
            'duration': data.get('duration'),
            'upload_date': data.get('upload_date'),
            'like_count': data.get('like_count'),
            'comment_count': data.get('comment_count'),
            'thumbnail': data.get('thumbnail'),
            'thumbnails': thumbnails
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        cria uma instância de Video a partir de um dicionário

        args:
            data:
                dicionário com os dados do vídeo

        returns:
            instância de Video
		"""

        return cls(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description'),
            uploader=data.get('uploader'),
            view_count=data.get('view_count'),
            duration=data.get('duration'),
            upload_date=data.get('upload_date'),
            like_count=data.get('like_count'),
            comment_count=data.get('comment_count'),
            thumbnail=data.get('thumbnail'),
            thumbnails=data.get('thumbnails')
        )
    
    def to_dict(self):
        """
        converte a instância de Video de volta pra um dicionário
        útil pra salvar no cache ou enviar pra outras partes do sistema
        """

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'uploader': self.uploader,
            'view_count': self.view_count,
            'duration': self.duration,
            'upload_date': self.upload_date,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'thumbnail': self.thumbnail,
            'thumbnails': self.thumbnails
        }