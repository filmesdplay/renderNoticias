from flask import Flask, request, jsonify
from pathlib import Path
import os, re, subprocess, sys, tempfile

app = Flask(__name__)

@app.get('/')
def health():
    return jsonify(status='ok')

@app.post('/gerar-short')
def gerar_short():
    try:
        data = request.get_json(force=True, silent=False) or {}
        titulo = data.get('titulo', '')
        texto = data.get('texto', '')
        id_noticia = sanitizar_id(data.get('id', 'sem_id'))

        roteiro = gerar_roteiro(titulo, texto)
        roteiro_txt = salvar_roteiro_txt(id_noticia, titulo, roteiro)
        audio_mp3 = gerar_tts_edge(roteiro_txt, id_noticia)

        return jsonify(
            status='ok',
            id=id_noticia,
            titulo=titulo,
            roteiro=roteiro,
            tts='ok',
            audio=audio_mp3,
            video='pendente'
        )
    except subprocess.CalledProcessError as e:
        return jsonify(status='error', message=f'TTS failed with exit code {e.returncode}'), 500
    except Exception as e:
        app.logger.exception('Erro em /gerar-short')
        return jsonify(status='error', message=str(e)), 500

def sanitizar_id(valor):
    s = str(valor or 'sem_id')
    s = re.sub(r'[^0-9A-Za-z._-]+', '_', s)
    return s.strip('_') or 'sem_id'

def gerar_roteiro(titulo, texto):
    trecho = ' '.join((texto or '').strip().split())
    if len(trecho) > 900:
        trecho = trecho[:900].rsplit(' ', 1)[0]

    abertura = f'Hoje na Agência Brasil: {titulo}.'
    narracao = f'{abertura} {trecho}'
    fechamento = 'Acompanhe os principais destaques do dia.'

    return {
        'abertura': abertura,
        'narracao': narracao,
        'fechamento': fechamento,
    }

def salvar_roteiro_txt(id_noticia, titulo, roteiro):
    out = Path('/tmp') / f'roteiro_{id_noticia}.txt'
    texto = []
    texto.append(f'TITULO: {titulo}')
    texto.append('')
    texto.append('ABERTURA:')
    texto.append(roteiro.get('abertura', ''))
    texto.append('')
    texto.append('NARRACAO:')
    texto.append(roteiro.get('narracao', ''))
    texto.append('')
    texto.append('FECHAMENTO:')
    texto.append(roteiro.get('fechamento', ''))
    out.write_text('\n'.join(texto), encoding='utf-8')
    return str(out)

def gerar_tts_edge(roteiro_txt, id_noticia):
    texto = Path(roteiro_txt).read_text(encoding='utf-8')
    linhas = []
    captura = False
    for linha in texto.splitlines():
        if linha.strip() == 'NARRACAO:':
            captura = True
            continue
        if linha.strip() == 'FECHAMENTO:':
            break
        if captura and linha.strip():
            linhas.append(linha.strip())
    narracao = ' '.join(linhas)
    narracao = re.sub(r'\s+', ' ', narracao).strip()
    narracao = narracao[:1200]

    mp3 = Path('/tmp') / f'audio_{id_noticia}.mp3'
    txt = Path('/tmp') / f'tts_{id_noticia}.txt'
    txt.write_text(narracao, encoding='utf-8')

    cmd = [
        sys.executable, '-m', 'edge_tts',
        '--voice', 'pt-BR-AntonioNeural',
        '--rate', '+0%',
        '--text', narracao,
        '--write-media', str(mp3)
    ]
    subprocess.run(cmd, check=True)
    return str(mp3)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '10000')))
