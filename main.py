from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.get("/")
def health():
    return jsonify(status="ok")

@app.post("/gerar-short")
def gerar_short():
    data = request.get_json(force=True, silent=False)
    return jsonify(status="ok", recebido=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))