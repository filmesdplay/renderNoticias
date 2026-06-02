from flask import Flask, request, jsonify
from pathlib import Path
import os, tempfile, textwrap, json

app = Flask(__name__)

@app.get('/')
def health():
    return jsonify(status='ok')

@app.post('/gerar-short')
def gerar_short():
    data = request.get_json(force=True, silent=False)
    titulo = data.get('titulo', '')
    texto = data.get('texto', '')
    id_noticia = str(data.get('id', ''))

    roteiro = gerar_roteiro(titulo, texto)
    arquivo = salvar_roteiro_txt(id_noticia, titulo, roteiro)

    return jsonify(
        status='ok',
        id=id_noticia,
        titulo=titulo,
        roteiro=roteiro,
        tts='pendente',
        video='pendente',
        artifact=arquivo
    )

def gerar_roteiro(titulo, texto):
    trecho = ' '.join(texto.strip().split())
    if len(trecho) > 700:
        trecho = trecho[:700].rsplit(' ', 1)[0]

    return {
        'abertura': f'Hoje na Agência Brasil: {titulo}.',
        'narracao': trecho,
        'fechamento': 'Acompanhe os principais destaques do dia.',
    }

def salvar_roteiro_txt(id_noticia, titulo, roteiro):
    out = Path('/tmp') / f'roteiro_{id_noticia}.txt'
    texto = []
    texto.append(f'TITULO: {titulo}')
    texto.append('')
    texto.append('ABERTURA:')
    texto.append(roteiro['abertura'])
    texto.append('')
    texto.append('NARRACAO:')
    texto.append(roteiro['narracao'])
    texto.append('')
    texto.append('FECHAMENTO:')
    texto.append(roteiro['fechamento'])
    out.write_text('\n'.join(texto), encoding='utf-8')
    return str(out)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '10000')))
