# Imports das bibliotecas
from googleapiclient.discovery import build
import pandas as pd
import re
import os

key = os.getenv("YOUTUBE_KEY")
link = '' # Conectar com o a parte de envio de url

# Função comentarios Youtube
def api_youtube(link, access_token):
  url = link
  api_key = access_token
  
  def extrair_id_url(url):
    # Tenta extrair ID de vídeo padrão (v=...)
    match = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    if match:
      return match.group(1)
    
    # Tenta extrair ID de Shorts (/shorts/...)
    match = re.search(r"/shorts/([a-zA-Z0-9_-]{11})", url)
    if match:
      return match.group(1)
    return None
  
  video_id = extrair_id_url(url)
  youtube = build('youtube', 'v3', developerKey = api_key)

  def extrair_comentarios(video_id, youtube_client):
    comentarios = []
    token_pagina = None

    while True:
      response = youtube_client.commentThreads().list(
          part = 'snippet',
          videoId = video_id,
          maxResults = 100,
          pageToken = token_pagina,
          textFormat = 'plainText'
        ).execute()

      for item in response['items']:
        comentario = item['snippet']['topLevelComment']['snippet']
        comentarios.append({
          'author': comentario['authorDisplayName'],
          'text': comentario['textDisplay'],
          'published_at': comentario['publishedAt'],
          'like_count' : comentario['likeCount']
        })

      token_pagina = response.get('nextPageToken')
      if not token_pagina:
        break

    return pd.DataFrame(comentarios)
    
  def verificar_video(video_id, youtube_client):
    response = youtube_client.videos().list(
      part = 'snippet',
      id = video_id
    ).execute()
    return len(response["items"]) > 0
  
  if verificar_video(video_id, youtube):
    df_origem = extrair_comentarios(video_id, youtube)
    return pd.DataFrame(df_origem)
  else:
    print("Video não encontrado ou ID invalido")

df = api_youtube(link, key)

def df_comentarios():
  return df[['text']]