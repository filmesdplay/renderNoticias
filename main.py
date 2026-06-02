from flask import Flask, request, jsonify
import os, tempfile, json, textwrap

app = Flask(__name__)

@app.get('/')
def health():
    return jsonify(status='ok')

@app.post('/gerar-short')
def gerar_short():
    data = request.get_json(force=True, silent=False)
    titulo = data.get('titulo', '')
    texto = data.get('texto', '')
    id_noticia = data.get('id', '')

    roteiro = gerar_roteiro(titulo, texto)
    return jsonify(
        status='ok',
        id=id_noticia,
        titulo=titulo,
        roteiro=roteiro,
        tts='pendente',
        video='pendente'
    )

def gerar_roteiro(titulo, texto):
    trecho = texto.strip().replace('\n', ' ')
    if len(trecho) > 700:
        trecho = trecho[:700].rsplit(' ', 1)[0]
    return {
        'abertura': f'Hoje na Agência Brasil: {titulo}.',
        'narracao': trecho,
        'fechamento': 'Acompanhe os principais destaques do dia.',
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '10000')))
