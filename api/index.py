from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "Servidor Flask activo en Vercel"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "recibido": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
