import re
import pandas as pd
from googleapiclient.discovery import build

def extrair_id_url(url) -> str:
    url = str(url)
    match = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    raise ValueError(f"URL inválida: {url}")


def verificar_video(video_id: str, youtube):
    """
    Verifica se o vídeo existe usando a API do YouTube.
    """
    return youtube.videos().list(
        part="snippet",
        id=video_id
    ).execute()

def api_youtube(url: str, api_key: str):
    """
    Conecta na API do YouTube e retorna os comentários de um vídeo.
    """
    video_id = extrair_id_url(url)
    youtube = build("youtube", "v3", developerKey=api_key)

    info = verificar_video(video_id, youtube)
    if not info["items"]:
        raise ValueError("Vídeo não encontrado.")

    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=50
    )
    response = request.execute()

    for item in response.get("items", []):
        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(text)

    return pd.DataFrame({"text": comments})

def df_comentarios(url: str, api_key: str):
    """
    Wrapper que retorna um DataFrame com os comentários do vídeo.
    """
    return api_youtube(url, api_key)