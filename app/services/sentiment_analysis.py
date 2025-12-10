from .comments import df_comentarios
from collections import Counter
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import tiktoken
import string
import os
import re

load_dotenv()
cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = 'gpt-4o-mini'
codificador = tiktoken.encoding_for_model(modelo)

def analisar_sentimentos(video_link: str, api_key: str):
    df_texto = df_comentarios(video_link, api_key)
    if df_texto is None:
        return None

    prompt_sistema = prompt_sistema = """
Analise os sentimentos contidos em cada frase e identifique se o comentario é positivo, negativo ou neutro e apresente a principal palavra que motivou a classificação final, tendo que ser somente uma palavra apresentada.
Para a analise de sentimento de comentarios em redes sociais, é necessario identificar os seguintes pontos para retornar qual será o sentimento do texto, e os pontos são:
- Saber identificar girias;
- Saber identificar emojis;
- Saber interpretar contexto da mensagem;

Os itens citados acima, são de EXTREMA importancia para a classificação final, pois as girias, os emojis e a interpretação do contexto da mensagem, podem sim modificar os resultados.

Exemplos de casos:
1. wtfff como isso pode ser real?? 😱 (Caso de emoji + giria)
2. Se fosse essa versão da dublagem ficaria bem melhor (Caso de Interpretação)
3. n acredito nisso 😡 (Caso de emoki + giria)

O formato de saída deve ser:

1.Positivo: Adorei
2.Negativo: Odiei
3.Neutro: Normal
"""

    comentarios_texto = "\n".join([f"{i+1}. {linha}" for i, linha in enumerate(df_texto['text'])])

    lista_mensagens = [
        {'role': 'system', 'content': prompt_sistema},
        {'role': 'user', 'content': comentarios_texto}
    ]

    resposta = cliente.chat.completions.create(
        messages=lista_mensagens,
        model=modelo
    )

    texto_resposta = resposta.choices[0].message.content

    linhas = texto_resposta.strip().split("\n")
    dados = []
    for linha in linhas:
        match = re.match(r"\d+\.\s*(Positivo|Negativo|Neutro)\s*:\s*(.+)", linha, re.IGNORECASE)
        if match:
            sentimento = match.group(1).capitalize()
            explicacao = match.group(2).strip()
            dados.append({
                "sentimento": sentimento,
                "comentario": df_texto.iloc[len(dados)]['text'],
                "explicacao": explicacao
            })

    df_resultado = pd.DataFrame(dados)

    comentarios_pos = df_resultado[df_resultado['sentimento'].str.lower() == 'positivo']['comentario'].tolist()
    comentarios_neg = df_resultado[df_resultado['sentimento'].str.lower() == 'negativo']['comentario'].tolist()
    comentarios_neu = df_resultado[df_resultado['sentimento'].str.lower() == 'neutro']['comentario'].tolist()

    qtd_pos = len(comentarios_pos)
    qtd_neg = len(comentarios_neg)
    qtd_neu = len(comentarios_neu)

    palavras_pos = df_resultado[df_resultado['sentimento'].str.lower() == 'positivo']['explicacao'].tolist()
    palavras_neg = df_resultado[df_resultado['sentimento'].str.lower() == 'negativo']['explicacao'].tolist()
    palavras_neu = df_resultado[df_resultado['sentimento'].str.lower() == 'neutro']['explicacao'].tolist()

    top_pos = [palavra for palavra, _ in Counter(palavras_pos).most_common(5)]
    top_neg = [palavra for palavra, _ in Counter(palavras_neg).most_common(5)]
    top_neu = [palavra for palavra, _ in Counter(palavras_neu).most_common(5)]

    return qtd_pos, qtd_neg, qtd_neu, top_pos, top_neg, top_neu
