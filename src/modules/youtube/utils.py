from datetime import datetime, timedelta

from numerize.numerize import numerize

def build_youtube_url(video_id: str):
    """
    reconstrói uma url do youtube a partir do id de um vídeo
    é majoritariamente usada quando um vídeo precisa ser passado pro yt-dlp
    """

    return f'https://www.youtube.com/watch?v={video_id}'

def format_upload_date(upload_date: str):
    # a data do yt-dlp originalmente vem como a string '20251026'
    # pra manipular ela, primeiro precisa converter a string pra um formato de datetime
    # ex: (2025, 10, 26, 0, 0)
    upload_date = datetime.strptime(upload_date, '%Y%m%d')

    # depois, reformata esse agora objeto de datetime, pra uma string de volta
    # b: mês por extenso abreviado
    # -d: número do dia sem um padding zero a esquerda
    # (https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)
    return datetime.strftime(upload_date, '%b %-d, %Y').capitalize()

def format_count(count: int):
    # transforma 1.243 em 1K
    return numerize(count, decimals=0)

def format_duration(seconds: int):
    duration = str(timedelta(seconds=seconds)) # hh:mm:ss
    
    # remover a primeira parte (hh:) se o vídeo tiver menos de 1 hora
    # isso é identificado quando a primeira parte é só '0'
    # a string é cortada e o que é retornado é apenas a parte relevante
    if duration[0] == '0':
        duration = duration[2:]

    return duration